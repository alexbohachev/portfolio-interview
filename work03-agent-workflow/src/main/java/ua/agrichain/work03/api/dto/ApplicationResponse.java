package ua.agrichain.work03.api.dto;

import java.util.UUID;

public record ApplicationResponse(
        UUID workflowId,
        String status,
        String policyRule,
        double estimatedCost,
        String externalRecordId,
        boolean replayed
) {}