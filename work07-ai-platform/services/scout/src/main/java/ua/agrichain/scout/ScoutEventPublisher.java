package ua.agrichain.scout;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class ScoutEventPublisher {

    private final KafkaTemplate<String, Map<String, Object>> kafka;
    private final String topic;

    public ScoutEventPublisher(
            KafkaTemplate<String, Map<String, Object>> kafka,
            @Value("${work07.kafka.topic-scout-report}") String topic) {
        this.kafka = kafka;
        this.topic = topic;
    }

    public void publishObservation(String observationId, String fieldId, String note) {
        String docId = "scout_" + observationId;
        Map<String, Object> payload = new HashMap<>();
        payload.put("event_id", UUID.randomUUID().toString());
        payload.put("schema_version", 1);
        payload.put("correlation_id", observationId);
        payload.put("doc_id", docId);
        payload.put("title", "Спостереження агронома " + fieldId);
        payload.put("body", note);
        payload.put("field_id", fieldId);
        kafka.send(topic, docId, payload);
    }
}