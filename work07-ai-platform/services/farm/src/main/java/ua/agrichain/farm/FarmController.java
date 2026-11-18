package ua.agrichain.farm;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class FarmController {

    private final DocumentEventPublisher publisher;

    public FarmController(DocumentEventPublisher publisher) {
        this.publisher = publisher;
    }

    public record DocumentRequest(
            @NotBlank String fieldId, @NotBlank String title, @NotBlank String body) {}

    @GetMapping("/api/v1/fields")
    public List<Map<String, String>> fields() {
        return List.of(
                Map.of("fieldId", "F-001", "crop", "wheat", "region", "north"),
                Map.of("fieldId", "F-002", "crop", "corn", "region", "south"));
    }

    @PostMapping("/api/v1/documents")
    public Map<String, Object> upload(@Valid @RequestBody DocumentRequest req) {
        String uploadId = UUID.randomUUID().toString();
        publisher.publish(uploadId, req.fieldId(), req.title(), req.body());
        return Map.of(
                "uploadId",
                uploadId,
                "fieldId",
                req.fieldId(),
                "title",
                req.title(),
                "createdAt",
                Instant.now().toString(),
                "kafkaTopic",
                "document.uploaded");
    }
}