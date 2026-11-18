package ua.agrichain.scout;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ScoutController {

    private final ScoutEventPublisher publisher;

    public ScoutController(ScoutEventPublisher publisher) {
        this.publisher = publisher;
    }

    public record ObservationRequest(@NotBlank String fieldId, @NotBlank String note) {}

    @PostMapping("/api/v1/observations")
    public Map<String, Object> create(@Valid @RequestBody ObservationRequest req) {
        String observationId = UUID.randomUUID().toString();
        publisher.publishObservation(observationId, req.fieldId(), req.note());
        return Map.of(
                "observationId", observationId,
                "fieldId", req.fieldId(),
                "note", req.note(),
                "createdAt", Instant.now().toString(),
                "kafkaTopic", "scout.report.created");
    }
}