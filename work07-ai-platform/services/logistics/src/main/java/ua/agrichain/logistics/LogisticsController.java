package ua.agrichain.logistics;

import jakarta.validation.constraints.NotBlank;
import java.util.Map;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LogisticsController {

    private final RagClient ragClient;

    public LogisticsController(RagClient ragClient) {
        this.ragClient = ragClient;
    }

    public record EquipmentRequest(@NotBlank String fieldId, @NotBlank String question) {}

    @PostMapping("/api/v1/equipment-requests")
    public Map<String, Object> request(@RequestBody EquipmentRequest req) {
        var search = ragClient.search(req.question(), 3);
        return Map.of(
                "fieldId", req.fieldId(),
                "question", req.question(),
                "searchMode", "hybrid",
                "knowledgeHits", search.hits());
    }

    public record KnowledgeQuestion(@NotBlank String question) {}

    @PostMapping("/api/v1/knowledge/qa")
    public Map<String, Object> knowledgeQa(@RequestBody KnowledgeQuestion req) {
        return ragClient.qa(req.question(), 5);
    }
}