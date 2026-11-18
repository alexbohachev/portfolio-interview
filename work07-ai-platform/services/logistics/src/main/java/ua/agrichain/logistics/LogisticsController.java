package ua.agrichain.logistics;

import jakarta.validation.constraints.NotBlank;
import java.util.Locale;
import java.util.Map;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LogisticsController {

    private final RagClient ragClient;
    private final EquipmentSearchService equipmentSearch;

    public LogisticsController(RagClient ragClient, EquipmentSearchService equipmentSearch) {
        this.ragClient = ragClient;
        this.equipmentSearch = equipmentSearch;
    }

    public record EquipmentRequest(@NotBlank String fieldId, @NotBlank String question) {}

    @PostMapping("/api/v1/equipment-requests")
    public Map<String, Object> request(
            @RequestBody EquipmentRequest req,
            @RequestHeader(value = "X-Search-Profile", defaultValue = "fast") String profile) {
        String p = profile.toLowerCase(Locale.ROOT);
        var hits = "slow".equals(p) ? equipmentSearch.searchSlow(req.question(), 3) : equipmentSearch.searchFast(req.question(), 3);
        return Map.of(
                "fieldId",
                req.fieldId(),
                "question",
                req.question(),
                "searchMode",
                "slow".equals(p) ? "slow-multi-call" : "hybrid",
                "searchProfile",
                p,
                "knowledgeHits",
                hits);
    }

    public record KnowledgeQuestion(@NotBlank String question) {}

    @PostMapping("/api/v1/knowledge/qa")
    public Map<String, Object> knowledgeQa(@RequestBody KnowledgeQuestion req) {
        return ragClient.qa(req.question(), 5);
    }
}