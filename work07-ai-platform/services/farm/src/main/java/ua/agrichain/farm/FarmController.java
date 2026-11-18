package ua.agrichain.farm;

import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class FarmController {

    @GetMapping("/api/v1/fields")
    public List<Map<String, String>> fields() {
        return List.of(
                Map.of("fieldId", "F-001", "crop", "wheat", "region", "north"),
                Map.of("fieldId", "F-002", "crop", "corn", "region", "south"));
    }
}