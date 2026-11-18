package ua.agrichain.logistics;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "rag-api")
public record RagApiProperties(String baseUrl) {}