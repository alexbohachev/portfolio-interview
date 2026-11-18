package ua.agrichain.work03.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.stereotype.Component;

@Component
public class CommandHashing {

    private final ObjectMapper mapper;

    public CommandHashing(ObjectMapper mapper) {
        this.mapper = mapper.copy().configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true);
    }

    public String hashEquipmentApplication(String equipmentType, int requestedHours, String region) {
        Map<String, Object> canonical = new LinkedHashMap<>();
        canonical.put("operation", "EQUIPMENT_APPLICATION");
        canonical.put("equipmentType", equipmentType);
        canonical.put("requestedHours", requestedHours);
        canonical.put("region", region);
        try {
            byte[] json = mapper.writeValueAsBytes(canonical);
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(digest.digest(json));
        } catch (JsonProcessingException | NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }
}