# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
from kb_QualiMap.QualiMapRunner import QualiMapRunner
#END_HEADER


class kb_QualiMap:
    '''
    Module Name:
    kb_QualiMap

    Module Description:

    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = "HEAD"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.scratch_dir = os.path.abspath(config['scratch'])
        self.workspace_url = config['workspace-url']
        self.srv_wiz_url = config['srv-wiz-url']
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        #END_CONSTRUCTOR
        pass


    def run_bamqc(self, ctx, params):
        """
        :param params: instance of type "RunBamQCParams" (Runs on either a
           ReadsAlignment or ReadsAlignmentSet. On a ReadsAlignment this will
           run BAM QC. On a set the mult-sample BAM QC is run. If the
           create_report flag is set, the result will be packaged as an HTML
           report. Either way you'll be provided with a qc_result_folder_path
           with an index.html file suitable for a report.) -> structure:
           parameter "input_ref" of String, parameter "create_report" of type
           "bool"
        :returns: instance of type "RunBamQCResult" -> structure: parameter
           "report_ref" of String, parameter "report_name" of String,
           parameter "qc_result_folder_path" of String, parameter
           "qc_result_zip_info" of type "BamQZResultZipFileInfo" ->
           structure: parameter "name" of String, parameter "shock_id" of
           String, parameter "index_html_file_name" of String, parameter
           "description" of String
        """
        # ctx is the context object
        # return variables are: result
        #BEGIN run_bamqc
        qmr = QualiMapRunner(self.scratch_dir, self.callback_url, self.workspace_url, self.srv_wiz_url)
        result = qmr.run_app(params)
        #END run_bamqc

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method run_bamqc return value ' +
                             'result is not type dict as required.')
        # return the results
        return [result]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
