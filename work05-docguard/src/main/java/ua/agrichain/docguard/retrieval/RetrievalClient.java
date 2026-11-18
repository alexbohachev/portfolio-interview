package ua.agrichain.docguard.retrieval;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

@Component
public class RetrievalClient {

    private final URI searchUri;
    private final ObjectMapper mapper;
    private final HttpClient http;

    public RetrievalClient(RetrievalProperties props, ObjectMapper mapper) {
        String base = props.baseUrl().replaceAll("/$", "");
        this.searchUri = URI.create(base + "/v1/search");
        this.mapper = mapper;
        this.http = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(Duration.ofSeconds(10))
                .build();
    }

    public Map<String, Object> search(String query, List<String> allowed, int topK) {
        Map<String, Object> payload = Map.of(
                "query", query,
                "allowedDocIds", allowed,
                "topK", topK);
        try {
            String json = mapper.writeValueAsString(payload);
            HttpRequest request = HttpRequest.newBuilder(searchUri)
                    .timeout(Duration.ofSeconds(30))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(json))
                    .build();
            HttpResponse<String> response = http.send(request, HttpResponse.BodyHandlers.ofString());
            int code = response.statusCode();
            if (code >= 500 || code == 408) {
                return degraded();
            }
            if (code >= 400) {
                throw new IllegalStateException("retrieval error " + code + ": " + response.body());
            }
            Map<String, Object> body = mapper.readValue(response.body(), new TypeReference<>() {});
            return body == null ? Map.of("hits", List.of()) : body;
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("retrieval request encode failed", ex);
        } catch (IOException | InterruptedException ex) {
            if (ex instanceof InterruptedException) {
                Thread.currentThread().interrupt();
            }
            return degraded();
        }
    }

    private static Map<String, Object> degraded() {
        return Map.of("hits", List.of(), "degraded", true, "mode", "python_unavailable");
    }
}