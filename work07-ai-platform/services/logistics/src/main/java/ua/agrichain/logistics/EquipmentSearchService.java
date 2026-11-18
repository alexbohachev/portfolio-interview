package ua.agrichain.logistics;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class EquipmentSearchService {

    private final RagClient ragClient;

    public EquipmentSearchService(RagClient ragClient) {
        this.ragClient = ragClient;
    }

    /** Профіль «після»: один hybrid top-k. */
    public List<RagClient.Hit> searchFast(String question, int topK) {
        return ragClient.search(question, topK, "hybrid").hits();
    }

    /**
     * Профіль «до»: N+1 — послідовні виклики rag-api по кожному токену + bm25 + hybrid по всьому запиту
     * (свідомо повільний шлях для кейсу продуктивності).
     */
    public List<RagClient.Hit> searchSlow(String question, int topK) {
        Map<String, RagClient.Hit> merged = new LinkedHashMap<>();
        for (String token : question.split("\\s+")) {
            if (token.length() < 2) {
                continue;
            }
            for (RagClient.Hit h : ragClient.search(token, 2, "hybrid").hits()) {
                merged.putIfAbsent(h.docId(), h);
            }
        }
        for (RagClient.Hit h : ragClient.search(question, topK, "bm25").hits()) {
            merged.putIfAbsent(h.docId(), h);
        }
        for (RagClient.Hit h : ragClient.search(question, topK, "hybrid").hits()) {
            merged.putIfAbsent(h.docId(), h);
        }
        List<RagClient.Hit> out = new ArrayList<>(merged.values());
        return out.subList(0, Math.min(topK, out.size()));
    }
}