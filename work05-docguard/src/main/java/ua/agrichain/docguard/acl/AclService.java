package ua.agrichain.docguard.acl;

import jakarta.annotation.PostConstruct;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.yaml.snakeyaml.Yaml;

@Service
public class AclService {

    private final AclProperties props;
    private Map<String, List<String>> principals = Map.of();

    public AclService(AclProperties props) {
        this.props = props;
    }

    @PostConstruct
    void load() throws Exception {
        String path = props.file();
        InputStream in;
        if (path.startsWith("classpath:")) {
            String resource = path.substring("classpath:".length());
            if (!resource.startsWith("/")) {
                resource = "/" + resource;
            }
            in = getClass().getResourceAsStream(resource);
        } else {
            in = Files.newInputStream(Path.of(path));
        }
        Map<String, Object> raw = new Yaml().load(in);
        @SuppressWarnings("unchecked")
        Map<String, List<String>> p = (Map<String, List<String>>) raw.getOrDefault("principals", Map.of());
        principals = p;
    }

    public List<String> allowedDocs(String tenantId, String principalId) {
        String key = tenantId + ":" + principalId;
        return principals.getOrDefault(key, Collections.emptyList());
    }
}