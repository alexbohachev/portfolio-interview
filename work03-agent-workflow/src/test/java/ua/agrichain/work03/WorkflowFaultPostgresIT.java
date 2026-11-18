package ua.agrichain.work03;

import org.junit.jupiter.api.condition.EnabledIfSystemProperty;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/**
 * Повний PostgreSQL-прогін: {@code gradlew test -Dwork03.docker=true} (потрібен Docker).
 */
@Testcontainers
@SpringBootTest
@ActiveProfiles("default")
@EnabledIfSystemProperty(named = "work03.docker", matches = "true")
class WorkflowFaultPostgresIT extends WorkflowFaultIT {

    @Container
    static PostgreSQLContainer<?> postgres =
            new PostgreSQLContainer<>("postgres:16-alpine")
                    .withDatabaseName("work03")
                    .withUsername("work03")
                    .withPassword("work03");

    @DynamicPropertySource
    static void datasource(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}