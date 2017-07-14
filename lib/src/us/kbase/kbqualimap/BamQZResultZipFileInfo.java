
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
 * <p>Original spec-file type: BamQZResultZipFileInfo</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "name",
    "shock_id",
    "index_html_file_name",
    "description"
})
public class BamQZResultZipFileInfo {

    @JsonProperty("name")
    private String name;
    @JsonProperty("shock_id")
    private String shockId;
    @JsonProperty("index_html_file_name")
    private String indexHtmlFileName;
    @JsonProperty("description")
    private String description;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("name")
    public String getName() {
        return name;
    }

    @JsonProperty("name")
    public void setName(String name) {
        this.name = name;
    }

    public BamQZResultZipFileInfo withName(String name) {
        this.name = name;
        return this;
    }

    @JsonProperty("shock_id")
    public String getShockId() {
        return shockId;
    }

    @JsonProperty("shock_id")
    public void setShockId(String shockId) {
        this.shockId = shockId;
    }

    public BamQZResultZipFileInfo withShockId(String shockId) {
        this.shockId = shockId;
        return this;
    }

    @JsonProperty("index_html_file_name")
    public String getIndexHtmlFileName() {
        return indexHtmlFileName;
    }

    @JsonProperty("index_html_file_name")
    public void setIndexHtmlFileName(String indexHtmlFileName) {
        this.indexHtmlFileName = indexHtmlFileName;
    }

    public BamQZResultZipFileInfo withIndexHtmlFileName(String indexHtmlFileName) {
        this.indexHtmlFileName = indexHtmlFileName;
        return this;
    }

    @JsonProperty("description")
    public String getDescription() {
        return description;
    }

    @JsonProperty("description")
    public void setDescription(String description) {
        this.description = description;
    }

    public BamQZResultZipFileInfo withDescription(String description) {
        this.description = description;
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
        return ((((((((((("BamQZResultZipFileInfo"+" [name=")+ name)+", shockId=")+ shockId)+", indexHtmlFileName=")+ indexHtmlFileName)+", description=")+ description)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
