
package us.kbase.kbqualimap;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: RunBamQCResult</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report_ref",
    "report_name",
    "qc_result_folder_path",
    "qc_result_zip_info"
})
public class RunBamQCResult {

    @JsonProperty("report_ref")
    private String reportRef;
    @JsonProperty("report_name")
    private String reportName;
    @JsonProperty("qc_result_folder_path")
    private String qcResultFolderPath;
    /**
     * <p>Original spec-file type: BamQZResultZipFileInfo</p>
     * 
     * 
     */
    @JsonProperty("qc_result_zip_info")
    private BamQZResultZipFileInfo qcResultZipInfo;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("report_ref")
    public String getReportRef() {
        return reportRef;
    }

    @JsonProperty("report_ref")
    public void setReportRef(String reportRef) {
        this.reportRef = reportRef;
    }

    public RunBamQCResult withReportRef(String reportRef) {
        this.reportRef = reportRef;
        return this;
    }

    @JsonProperty("report_name")
    public String getReportName() {
        return reportName;
    }

    @JsonProperty("report_name")
    public void setReportName(String reportName) {
        this.reportName = reportName;
    }

    public RunBamQCResult withReportName(String reportName) {
        this.reportName = reportName;
        return this;
    }

    @JsonProperty("qc_result_folder_path")
    public String getQcResultFolderPath() {
        return qcResultFolderPath;
    }

    @JsonProperty("qc_result_folder_path")
    public void setQcResultFolderPath(String qcResultFolderPath) {
        this.qcResultFolderPath = qcResultFolderPath;
    }

    public RunBamQCResult withQcResultFolderPath(String qcResultFolderPath) {
        this.qcResultFolderPath = qcResultFolderPath;
        return this;
    }

    /**
     * <p>Original spec-file type: BamQZResultZipFileInfo</p>
     * 
     * 
     */
    @JsonProperty("qc_result_zip_info")
    public BamQZResultZipFileInfo getQcResultZipInfo() {
        return qcResultZipInfo;
    }

    /**
     * <p>Original spec-file type: BamQZResultZipFileInfo</p>
     * 
     * 
     */
    @JsonProperty("qc_result_zip_info")
    public void setQcResultZipInfo(BamQZResultZipFileInfo qcResultZipInfo) {
        this.qcResultZipInfo = qcResultZipInfo;
    }

    public RunBamQCResult withQcResultZipInfo(BamQZResultZipFileInfo qcResultZipInfo) {
        this.qcResultZipInfo = qcResultZipInfo;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((("RunBamQCResult"+" [reportRef=")+ reportRef)+", reportName=")+ reportName)+", qcResultFolderPath=")+ qcResultFolderPath)+", qcResultZipInfo=")+ qcResultZipInfo)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
