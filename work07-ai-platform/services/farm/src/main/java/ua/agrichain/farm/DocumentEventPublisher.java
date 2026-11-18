package ua.agrichain.farm;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class DocumentEventPublisher {

    private final KafkaTemplate<String, Map<String, Object>> kafka;
    private final String topic;

    public DocumentEventPublisher(
            KafkaTemplate<String, Map<String, Object>> kafka,
            @Value("${work07.kafka.topic-document-uploaded}") String topic) {
        this.kafka = kafka;
        this.topic = topic;
    }

    public void publish(String uploadId, String fieldId, String title, String body) {
        String docId = "farm_" + uploadId;
        Map<String, Object> payload = new HashMap<>();
        payload.put("event_id", UUID.randomUUID().toString());
        payload.put("schema_version", 1);
        payload.put("correlation_id", uploadId);
        payload.put("doc_id", docId);
        payload.put("title", title);
        payload.put("body", body);
        payload.put("field_id", fieldId);
        kafka.send(topic, docId, payload);
    }
}