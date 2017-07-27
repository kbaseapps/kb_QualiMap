import os
import time
import uuid
import subprocess

from pprint import pprint

from Workspace.WorkspaceClient import Workspace
from ReadsAlignmentUtils.ReadsAlignmentUtilsClient import ReadsAlignmentUtils
from SetAPI.SetAPIServiceClient import SetAPI
from KBaseReport.KBaseReportClient import KBaseReport
from DataFileUtil.DataFileUtilClient import DataFileUtil


class QualiMapRunner:

    QUALIMAP_PATH = '/kb/module/qualimap-bin/qualimap'

    def __init__(self, scratch_dir, callback_url, workspace_url, srv_wiz_url):
        self.scratch_dir = scratch_dir
        self.rau = ReadsAlignmentUtils(callback_url)
        self.kbr = KBaseReport(callback_url)
        self.dfu = DataFileUtil(callback_url)
        self.set_api = SetAPI(srv_wiz_url)
        self.ws = Workspace(workspace_url)
        self.valid_commands = ['bamqc', 'multi-bamqc']

    def run_app(self, params):
        self.validate_params(params)
        print('Validated Params = ')
        pprint(params)
        run_info = self.get_run_info(params)

        if run_info['mode'] == 'single':
            result = self.run_bamqc(params['input_ref'], run_info['input_info'])
        elif run_info['mode'] == 'multi':
            result = self.run_multi_sample_qc(params['input_ref'], run_info['input_info'])
        else:
            raise ValueError('Error in fetching the type to determine run settings.')

        if params['create_report']:
            result = self.create_report(result, params['output_workspace'])

        return result

    def create_report(self, result, output_workspace):
        qc_result_zip_info = result['qc_result_zip_info']
        report_info = self.kbr.create_extended_report({
            'message': '',
            'objects_created': [],
            'direct_html_link_index': 0,
            'html_links': [{'shock_id': qc_result_zip_info['shock_id'],
                            'name': qc_result_zip_info['index_html_file_name'],
                            'label': qc_result_zip_info['name']}],
            'report_object_name': 'qualimap_report' + str(uuid.uuid4()),
            'workspace_name': output_workspace
        })
        result['report_name'] = report_info['name']
        result['report_ref'] = report_info['ref']
        return result

    def run_bamqc(self, input_ref, input_info):
        # download the input and setup a working dir
        alignment_info = self.rau.download_alignment({'source_ref': input_ref})
        bam_file_path = self.find_my_bam_file(alignment_info['destination_dir'])
        workdir = os.path.join(self.scratch_dir, 'qualimap_' + str(int(time.time() * 10000)))

        options = ['-bam', bam_file_path, '-outdir', workdir, '-outformat', 'html']
        self.run_cli_command('bamqc', options)

        package_info = self.package_output_folder(
            workdir, 'QualiMap_report', 'HTML report directory for QualiMap BAM QC', 'qualimapReport.html')

        return {'qc_result_folder_path': workdir, 'qc_result_zip_info': package_info}

    def run_multi_sample_qc(self, input_ref, input_info):
        # download the input and setup a working dir
        reads_alignment_info = self.get_alignments_from_set(input_ref)
        suffix = 'qualimap_' + str(int(time.time() * 10000))
        workdir = os.path.join(self.scratch_dir, suffix)
        os.makedirs(workdir)

        input_file_path = self.create_multi_qualimap_cfg(reads_alignment_info, workdir)

        options = ['-d', input_file_path, '-r', '-outdir', workdir, '-outformat', 'html']
        self.run_cli_command('multi-bamqc', options)

        package_info = self.package_output_folder(workdir,
                                                  'QualiMap_report',
                                                  'HTML report directory for QualiMap Multi-sample BAM QC',
                                                  'multisampleBamQcReport.html')

        return {'qc_result_folder_path': workdir, 'qc_result_zip_info': package_info}

    def get_alignments_from_set(self, alignment_set_ref):
        set_data = self.set_api.get_reads_alignment_set_v1({'ref': alignment_set_ref, 'include_item_info': 1})
        items = set_data['data']['items']

        reads_alignment_data = []
        for alignment in items:
            alignment_info = self.rau.download_alignment({'source_ref': alignment['ref']})
            bam_file_path = self.find_my_bam_file(alignment_info['destination_dir'])
            label = None
            if 'label' in alignment:
                label = alignment['label']
            reads_alignment_data.append({
                    'bam_file_path': bam_file_path,
                    'ref': alignment['ref'],
                    'label': label,
                    'info': alignment['info']
                })
        return reads_alignment_data

    def create_multi_qualimap_cfg(self, reads_alignment_info, workdir):
        # Group by labels if there is at least one defined
        use_labels = False
        for alignment in reads_alignment_info:
            if alignment['label']:
                use_labels = True
                break

        # write the file
        input_file_path = os.path.join(workdir, 'multi_input.txt')
        input_file = open(input_file_path, 'w')
        name_lookup = {}
        for alignment in reads_alignment_info:
            name = alignment['info'][1]
            if name in name_lookup:
                name_lookup[name] += 1
                name = name + '_' + str(name_lookup[name])
            else:
                name_lookup[name] = 1

            input_file.write(name + '\t' + alignment['bam_file_path'])
            if use_labels:
                if alignment['label']:
                    input_file.write('\t' + alignment['label'])
                else:
                    input_file.write('\tunlabeled')
            input_file.write('\n')
        input_file.close()
        return input_file_path

    def get_run_info(self, params):
        info = self.get_obj_info(params['input_ref'])
        obj_type = self.get_type_from_obj_info(info)
        if obj_type in ['KBaseRNASeq.RNASeqAlignment']:
            return {'mode': 'single', 'input_info': info}
        if obj_type in ['KBaseRNASeq.RNASeqAlignmentSet', 'KBaseSets.ReadsAlignmentSet']:
            return {'mode': 'multi', 'input_info': info}
        raise ValueError('Object type of input_ref is not valid, was: ' + str(obj_type))

    def validate_params(self, params):
        if 'input_ref' not in params:
            raise ValueError('required parameter field "input_ref" was not set')

        create_report = False
        if 'create_report' in params:
            if int(params['create_report']) == 1:
                if 'output_workspace' not in params:
                    raise ValueError('If "create_report" was set, then "output_workspace" is required')
                if not params['output_workspace']:
                    raise ValueError('If "create_report" was set, then "output_workspace" is required')
                create_report = True
        params['create_report'] = create_report

    def run_cli_command(self, command, options, cwd=None):
        if command not in self.valid_commands:
            raise ValueError('Invalid QualiMap command: ' + str(command))
        command = [self.QUALIMAP_PATH, command] + options
        print('Running: ' + ' '.join(command))

        if not cwd:
            cwd = self.scratch_dir

        p = subprocess.Popen(command, cwd=cwd, shell=False)
        exitCode = p.wait()

        if (exitCode == 0):
            print('Success, exit code was: ' + str(exitCode))
        else:
            raise ValueError('Error running command: ' + ' '.join(command) + '\n' +
                             'Exit Code: ' + str(exitCode))

    def find_my_bam_file(self, dirpath):
        bam_path = None
        for f in os.listdir(dirpath):
            fullpath = os.path.join(dirpath, f)
            if os.path.isfile(fullpath) and f.lower().endswith('.bam'):
                if bam_path is not None:
                    raise ValueError('Error! Too many BAM files were downloaded for this alignment!')
                bam_path = fullpath
        if bam_path is None:
            raise ValueError('Error! No BAM files were downloaded for this alignment!')
        return bam_path

    def package_output_folder(self, folder_path, zip_file_name, zip_file_description, index_html_file):
        ''' Simple utility for packaging a folder and saving to shock '''
        output = self.dfu.file_to_shock({'file_path': folder_path,
                                         'make_handle': 0,
                                         'pack': 'zip'})
        return {'shock_id': output['shock_id'],
                'name': zip_file_name,
                'description': zip_file_description,
                'index_html_file_name': index_html_file}

    def get_type_from_obj_info(self, info):
        return info[2].split('-')[0]

    def get_obj_info(self, ref):
        return self.ws.get_object_info3({'objects': [{'ref': ref}]})['infos'][0]
