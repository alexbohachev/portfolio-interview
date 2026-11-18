package ua.agrichain.logistics;

import java.util.List;
import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class RagClient {

    private final RestClient rest;

    public RagClient(RagApiProperties props) {
        this.rest = RestClient.builder().baseUrl(props.baseUrl()).build();
    }

    public record SearchRequest(String query, int topK) {}

    public record Hit(String docId, String snippet, double score) {}

    public record SearchResponse(List<Hit> hits) {}

    @SuppressWarnings("unchecked")
    public SearchResponse search(String query, int topK) {
        Map<String, Object> body = rest.post()
                .uri("/v1/knowledge/search")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new SearchRequest(query, topK))
                .retrieve()
                .body(Map.class);
        if (body == null) {
            return new SearchResponse(List.of());
        }
        List<Map<String, Object>> raw = (List<Map<String, Object>>) body.getOrDefault("hits", List.of());
        List<Hit> hits = raw.stream()
                .map(h -> new Hit(
                        String.valueOf(h.get("doc_id")),
                        String.valueOf(h.get("snippet")),
                        ((Number) h.getOrDefault("score", 0)).doubleValue()))
                .toList();
        return new SearchResponse(hits);
    }
}