package ua.agrichain.docguard.retrieval;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "retrieval")
public record RetrievalProperties(String baseUrl) {}