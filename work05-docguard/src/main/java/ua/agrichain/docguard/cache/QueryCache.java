package ua.agrichain.docguard.cache;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;

@Component
public class QueryCache {

    private final Map<String, Map<String, Object>> store = new ConcurrentHashMap<>();

    public String key(String tenant, String principal, String query, String aclRevision) {
        return tenant + "|" + principal + "|" + aclRevision + "|" + query.trim().toLowerCase();
    }

    public Map<String, Object> get(String key) {
        return store.get(key);
    }

    public void put(String key, Map<String, Object> value) {
        store.put(key, value);
    }

    public void invalidatePrincipal(String tenant, String principal) {
        String prefix = tenant + "|" + principal + "|";
        store.keySet().removeIf(k -> k.startsWith(prefix));
    }
}