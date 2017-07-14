/* */
module kb_QualiMap {

    typedef int bool;

    /*
        Runs on either a ReadsAlignment or ReadsAlignmentSet. On a
        ReadsAlignment this will run BAM QC. On a set the mult-sample
        BAM QC is run. If the create_report flag is set, the result
        will be packaged as an HTML report. Either way you'll be
        provided with a qc_result_folder_path with an index.html file
        suitable for a report.
    */
    typedef structure {
        string input_ref;
        bool create_report;
        string output_workspace;
    } RunBamQCParams;

    typedef structure {
        string name;
        string shock_id;
        string index_html_file_name;
        string description;
    } BamQZResultZipFileInfo;

    typedef structure {
        string report_ref;
        string report_name;
        string qc_result_folder_path;
        BamQZResultZipFileInfo qc_result_zip_info;
    } RunBamQCResult;

    funcdef run_bamqc(RunBamQCParams params)
        returns (RunBamQCResult result) authentication required;
};
