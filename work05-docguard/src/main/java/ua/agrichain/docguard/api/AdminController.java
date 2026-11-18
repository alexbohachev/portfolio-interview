package ua.agrichain.docguard.api;

import java.util.Map;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import ua.agrichain.docguard.cache.QueryCache;

@RestController
public class AdminController {

    private final QueryCache cache;

    public AdminController(QueryCache cache) {
        this.cache = cache;
    }

    @PostMapping("/api/v1/admin/invalidate-cache")
    public Map<String, String> invalidate(
            @RequestHeader("X-Tenant-Id") String tenantId, @RequestHeader("X-Principal-Id") String principalId) {
        cache.invalidatePrincipal(tenantId, principalId);
        return Map.of("status", "ok", "tenantId", tenantId, "principalId", principalId);
    }
}