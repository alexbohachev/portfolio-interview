package ua.agrichain.work03.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;

public record SubmitApplicationRequest(
        @NotBlank String tenantId,
        @NotBlank String idempotencyKey,
        @NotBlank String equipmentType,
        @Positive int requestedHours,
        @NotBlank String region
) {}