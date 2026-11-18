package ua.agrichain.scout;

import jakarta.validation.constraints.NotBlank;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ScoutController {

    public record ObservationRequest(@NotBlank String fieldId, @NotBlank String note) {}

    @PostMapping("/api/v1/observations")
    public Map<String, Object> create(@RequestBody ObservationRequest req) {
        return Map.of(
                "observationId", UUID.randomUUID().toString(),
                "fieldId", req.fieldId(),
                "note", req.note(),
                "createdAt", Instant.now().toString());
    }
}