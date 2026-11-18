package ua.agrichain.docguard.acl;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "acl")
public record AclProperties(String file) {}