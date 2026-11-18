package ua.agrichain.docguard.api;

import jakarta.validation.constraints.NotBlank;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;
import ua.agrichain.docguard.acl.AclService;
import ua.agrichain.docguard.audit.AuditEntry;
import ua.agrichain.docguard.audit.AuditRepository;
import ua.agrichain.docguard.cache.QueryCache;
import ua.agrichain.docguard.retrieval.RetrievalClient;

@RestController
public class QueryController {

    private final AclService acl;
    private final RetrievalClient retrieval;
    private final QueryCache cache;
    private final AuditRepository auditRepository;
    private final String aclRevision = "v1";

    public QueryController(
            AclService acl, RetrievalClient retrieval, QueryCache cache, AuditRepository auditRepository) {
        this.acl = acl;
        this.retrieval = retrieval;
        this.cache = cache;
        this.auditRepository = auditRepository;
    }

    public record QueryBody(@NotBlank String question) {}

    @PostMapping("/api/v1/query")
    public Map<String, Object> query(
            @RequestHeader("X-Tenant-Id") String tenantId,
            @RequestHeader("X-Principal-Id") String principalId,
            @RequestBody QueryBody body) {
        List<String> allowed = acl.allowedDocs(tenantId, principalId);
        if (allowed.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "no document access");
        }
        String cacheKey = cache.key(tenantId, principalId, body.question(), aclRevision);
        Map<String, Object> cached = cache.get(cacheKey);
        if (cached != null) {
            audit(tenantId, principalId, body.question(), cached, true);
            return cached;
        }
        Map<String, Object> result = retrieval.search(body.question(), allowed, 5);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> hits = (List<Map<String, Object>>) result.getOrDefault("hits", List.of());
        for (Map<String, Object> h : hits) {
            String docId = String.valueOf(h.get("doc_id"));
            if (!allowed.contains(docId)) {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "leak blocked: " + docId);
            }
        }
        Map<String, Object> response = Map.of(
                "tenantId", tenantId,
                "principalId", principalId,
                "question", body.question(),
                "hits", hits,
                "aclRevision", aclRevision,
                "degraded", result.getOrDefault("degraded", false));
        cache.put(cacheKey, response);
        audit(tenantId, principalId, body.question(), response, false);
        return response;
    }

    private void audit(String tenant, String principal, String q, Map<String, Object> res, boolean cacheHit) {
        @SuppressWarnings("unchecked")
        int n = ((List<?>) res.getOrDefault("hits", List.of())).size();
        AuditEntry e = new AuditEntry();
        e.setTenantId(tenant);
        e.setPrincipalId(principal);
        e.setQuery(q);
        e.setHitsReturned(n);
        e.setCacheHit(cacheHit);
        auditRepository.save(e);
    }
}