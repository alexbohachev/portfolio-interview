package ua.agrichain.docguard;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class DocGuardApplication {
    public static void main(String[] args) {
        SpringApplication.run(DocGuardApplication.class, args);
    }
}