package ua.agrichain.logistics;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import java.util.List;
import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class RagClient {

    private final RestClient rest;

    public RagClient(RagApiProperties props) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5_000);
        factory.setReadTimeout(120_000);
        this.rest = RestClient.builder().baseUrl(props.baseUrl()).requestFactory(factory).build();
    }

    public record SearchRequest(String query, int topK, String mode) {
        public SearchRequest(String query, int topK) {
            this(query, topK, "hybrid");
        }
    }

    public record QaRequest(String query, int topK) {}

    public record Hit(String docId, String snippet, double score) {}

    public record SearchResponse(List<Hit> hits) {}

    public SearchResponse search(String query, int topK) {
        return search(query, topK, "hybrid");
    }

    @SuppressWarnings("unchecked")
    @CircuitBreaker(name = "ragApi", fallbackMethod = "searchFallback")
    public SearchResponse search(String query, int topK, String mode) {
        Map<String, Object> body = rest.post()
                .uri("/v1/knowledge/search")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new SearchRequest(query, topK, mode))
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

    @SuppressWarnings("unused")
    private SearchResponse searchFallback(String query, int topK, String mode, Throwable t) {
        return new SearchResponse(List.of());
    }

    @SuppressWarnings("unchecked")
    @CircuitBreaker(name = "ragApi", fallbackMethod = "qaFallback")
    public Map<String, Object> qa(String query, int topK) {
        Map<String, Object> body = rest.post()
                .uri("/v1/knowledge/qa")
                .contentType(MediaType.APPLICATION_JSON)
                .body(new QaRequest(query, topK))
                .retrieve()
                .body(Map.class);
        return body == null ? Map.of() : body;
    }

    @SuppressWarnings("unused")
    private Map<String, Object> qaFallback(String query, int topK, Throwable t) {
        return Map.of("refused", true, "answer", "", "mode", "circuit_open", "citations", List.of());
    }
}