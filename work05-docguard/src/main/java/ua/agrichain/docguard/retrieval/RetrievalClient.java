package ua.agrichain.docguard.retrieval;

import java.util.List;
import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

@Component
public class RetrievalClient {

    private final RestClient rest;

    public RetrievalClient(RetrievalProperties props) {
        this.rest = RestClient.builder().baseUrl(props.baseUrl()).build();
    }

    public record SearchRequest(String query, List<String> allowedDocIds, int topK) {}

    @SuppressWarnings("unchecked")
    public Map<String, Object> search(String query, List<String> allowed, int topK) {
        try {
            Map<String, Object> body = rest.post()
                    .uri("/v1/search")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(new SearchRequest(query, allowed, topK))
                    .retrieve()
                    .body(Map.class);
            return body == null ? Map.of("hits", List.of()) : body;
        } catch (RestClientResponseException ex) {
            if (ex.getStatusCode().value() >= 500 || ex.getStatusCode().value() == 408) {
                return Map.of("hits", List.of(), "degraded", true, "mode", "python_unavailable");
            }
            throw ex;
        }
    }
}