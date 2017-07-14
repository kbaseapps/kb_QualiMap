
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
 * <p>Original spec-file type: RunBamQCParams</p>
 * <pre>
 * Runs on either a ReadsAlignment or ReadsAlignmentSet. On a
 * ReadsAlignment this will run BAM QC. On a set the mult-sample
 * BAM QC is run. If the create_report flag is set, the result
 * will be packaged as an HTML report. Either way you'll be
 * provided with a qc_result_folder_path with an index.html file
 * suitable for a report.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "input_ref",
    "create_report"
})
public class RunBamQCParams {

    @JsonProperty("input_ref")
    private String inputRef;
    @JsonProperty("create_report")
    private Long createReport;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("input_ref")
    public String getInputRef() {
        return inputRef;
    }

    @JsonProperty("input_ref")
    public void setInputRef(String inputRef) {
        this.inputRef = inputRef;
    }

    public RunBamQCParams withInputRef(String inputRef) {
        this.inputRef = inputRef;
        return this;
    }

    @JsonProperty("create_report")
    public Long getCreateReport() {
        return createReport;
    }

    @JsonProperty("create_report")
    public void setCreateReport(Long createReport) {
        this.createReport = createReport;
    }

    public RunBamQCParams withCreateReport(Long createReport) {
        this.createReport = createReport;
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
        return ((((((("RunBamQCParams"+" [inputRef=")+ inputRef)+", createReport=")+ createReport)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
