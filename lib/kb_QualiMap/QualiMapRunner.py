import os
import signal
import subprocess
import time
import traceback
import uuid
from pprint import pprint

from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsAlignmentUtilsClient import ReadsAlignmentUtils
from installed_clients.SetAPIServiceClient import SetAPI
from installed_clients.WorkspaceClient import Workspace


class QualiMapRunner:

    QUALIMAP_PATH = '/kb/module/qualimap-bin/qualimap'
    JAVA_MEM_DEFAULT_SIZE = '16G'
    LARGE_BAM_FILE_SIZE = 20 * 1024 * 1024 * 1024  # 20 GB
    TIMEOUT = 72 * 60 * 60  # 72 hours

    def _get_file_size(self, file_path):
        file_size = os.path.getsize(file_path)
        print('File size: {} -- {}'.format(file_size, file_path))
        return file_size

    def _large_file(self, file_path):

        filename, file_extension = os.path.splitext(file_path)
        multiplier = 0

        if file_extension == '.txt':
            total_file_size = 0
            with open(file_path, 'r') as f:
                for line in f:
                    bam_file_path = line.split('\t')[1]
                    total_file_size += self._get_file_size(bam_file_path)
            print('Total file size: {}'.format(total_file_size))
            multiplier = int(total_file_size) // int(self.LARGE_BAM_FILE_SIZE)
        else:
            multiplier = int(self._get_file_size(file_path)) // int(self.LARGE_BAM_FILE_SIZE)

        print('setting number of windows multiplier to: {}'.format(multiplier))

        return multiplier

    def _timeout_handler(self, signum, frame):
        print('Signal handler called with signal', signum)
        raise ValueError('QualiMap takes too long')

    def __init__(self, scratch_dir, callback_url, workspace_url, srv_wiz_url):
        self.scratch_dir = scratch_dir
        self.rau = ReadsAlignmentUtils(callback_url)
        self.kbr = KBaseReport(callback_url)
        self.dfu = DataFileUtil(callback_url)
        self.gfu = GenomeFileUtil(callback_url)
        self.set_api = SetAPI(srv_wiz_url)
        self.ws = Workspace(workspace_url)
        self.valid_commands = ['bamqc', 'multi-bamqc']

    def run_app(self, params):
        self.validate_params(params)
        print('Validated Params = ')
        pprint(params)
        run_info = self.get_run_info(params)

        if run_info.get('mode') not in ['single', 'multi']:
            raise ValueError('Error in fetching the type to determine run settings.')

        run_error = False
        try:
            signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(self.TIMEOUT)
            if run_info['mode'] == 'single':
                result = self.run_bamqc(params['input_ref'], run_info['input_info'])
            elif run_info['mode'] == 'multi':
                result = self.run_multi_sample_qc(params['input_ref'], run_info['input_info'])
            signal.alarm(0)
        except Exception:
            run_error = True

            workdir = os.path.join(self.scratch_dir, 'qualimap_' + str(int(time.time() * 10000)))
            os.makedirs(workdir)

            with open(os.path.join(workdir, 'qualimapReport.html'), 'w') as report:
                report.write('<html><body><p></p></body></html>')

            package_info = self.package_output_folder(
                                                    workdir, 'QualiMap_report',
                                                    'EMPTY HTML report directory for QualiMap BAM QC',
                                                    'qualimapReport.html')

            result = {'qc_result_folder_path': workdir,
                      'qc_result_zip_info': package_info,
                      'shock_id': None}
            error_msg = 'Running QualiMap returned an error:\n{}\n'.format(
                                                                    traceback.format_exc())
            error_msg += 'Generating simple report instead\n'
            print(error_msg)

        if params['create_report']:
            result = self.create_report(result, params['output_workspace'],
                                        run_error, params['input_ref'])

        return result

    def create_report(self, result, output_workspace, run_error=None, input_ref=None):

        if run_error:
            objects_created = []
            info = self.get_obj_info(input_ref)
            obj_type = self.get_type_from_obj_info(info)
            if obj_type in ['KBaseRNASeq.RNASeqAlignment']:
                objects_created.append({'ref': input_ref,
                                        'description': 'Alignment'})

            if obj_type in ['KBaseRNASeq.RNASeqAlignmentSet', 'KBaseSets.ReadsAlignmentSet']:
                objects_created.append({'ref': input_ref,
                                        'description': 'AlignmentSet'})
                reads_alignment_info = self.get_alignments_from_set(input_ref)
                for alignment in reads_alignment_info:
                    alignment_ref = alignment.get('ref')
                    objects_created.append({'ref': alignment_ref,
                                            'description': 'Alignment'})

            report_info = self.kbr.create_extended_report({
                    'message': ' ',
                    'objects_created': objects_created,
                    'report_object_name': 'qualimap_report' + str(uuid.uuid4()),
                    'workspace_name': output_workspace
                })
            result['report_name'] = report_info['name']
            result['report_ref'] = report_info['ref']
            return result

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

    def get_gtf_file(self, input_ref, set_op=False):

        print('Start fetching GFF file from genome')

        if set_op:
            set_data = self.set_api.get_reads_alignment_set_v1({'ref': input_ref,
                                                                'include_item_info': 1})
            input_ref = set_data['data']['items'][0]['ref']

        obj_data = self.dfu.get_objects(
            {"object_refs": [input_ref]})['data'][0]['data']

        genome_ref = obj_data.get('genome_id')

        if not genome_ref:
            raise ValueError('Alignment is not associated with a Genome object')

        result_directory = os.path.join(self.scratch_dir, str(uuid.uuid4()))
        os.makedirs(result_directory)

        genome_gtf_file = self.gfu.genome_to_gff({'genome_ref': genome_ref,
                                                  'is_gtf': True,
                                                  'target_dir': result_directory})['file_path']

        return genome_gtf_file

    def run_bamqc(self, input_ref, input_info):
        # download the input and setup a working dir
        alignment_info = self.rau.download_alignment({'source_ref': input_ref})
        bam_file_path = self.find_my_bam_file(alignment_info['destination_dir'])
        try:
            gtf_file = self.get_gtf_file(input_ref)
        except Exception:
            gtf_file = ''

        workdir = os.path.join(self.scratch_dir, 'qualimap_' + str(int(time.time() * 10000)))

        options = ['-bam', bam_file_path, '-c', '-outdir', workdir, '-outformat', 'html']

        if gtf_file:
            options += ['-gff', gtf_file]

        options.append('--java-mem-size={}'.format(self.JAVA_MEM_DEFAULT_SIZE))  # always use large mem
        multiplier = self._large_file(bam_file_path)
        if multiplier:
            window_size = multiplier * 400
            print(f'using larger window size: {window_size} and Java memory: '
                  f'{self.JAVA_MEM_DEFAULT_SIZE}')
            options.append('-nw {}'.format(window_size))  # increase size of windows

        self.run_cli_command('bamqc', options)

        package_info = self.package_output_folder(
            workdir, 'QualiMap_report', 'HTML report directory for QualiMap BAM QC', 'qualimapReport.html')

        return {'qc_result_folder_path': workdir, 'qc_result_zip_info': package_info}

    def run_multi_sample_qc(self, input_ref, input_info):
        # download the input and setup a working dir
        reads_alignment_info = self.get_alignments_from_set(input_ref)
        try:
            gtf_file = self.get_gtf_file(input_ref, set_op=True)
        except Exception:
            gtf_file = ''
        suffix = 'qualimap_' + str(int(time.time() * 10000))
        workdir = os.path.join(self.scratch_dir, suffix)
        os.makedirs(workdir)

        input_file_path = self.create_multi_qualimap_cfg(reads_alignment_info, workdir)

        options = ['-d', input_file_path, '-r', '-c', '-outdir', workdir, '-outformat', 'html']

        if gtf_file:
            options += ['-gff', gtf_file]

        multiplier = self._large_file(input_file_path)
        if multiplier:
            window_size = multiplier * 400
            print(f'using larger window size: {window_size} and Java memory: '
                  f'{self.JAVA_MEM_DEFAULT_SIZE}')
            options.append(f'-nw {window_size}')  # increase size of windows
            options.append(f'--java-mem-size={self.JAVA_MEM_DEFAULT_SIZE}')

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
                # remove spacing in label
                label = '_'.join(label.split(' '))
            reads_alignment_data.append({
                    'bam_file_path': bam_file_path,
                    'ref': alignment['ref'],
                    'label': label,
                    'info': alignment['info']
                })
        return reads_alignment_data

    def create_multi_qualimap_cfg(self, reads_alignment_info, workdir):
        # Group by labels if there is at least one defined
        print('reads_alignment_info: {}'.format(reads_alignment_info))
        use_labels = False
        for alignment in reads_alignment_info:
            if alignment['label']:
                use_labels = True
                break

        # write the file
        input_file_path = os.path.join(workdir, 'multi_input.txt')
        print('Start generating: {}'.format(input_file_path))
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

        with open(input_file_path, 'r') as f:
            print('Generated: {}'.format(input_file_path))
            print(f.read())

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

        if exitCode == 0:
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
        """ Simple utility for packaging a folder and saving to shock """
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
