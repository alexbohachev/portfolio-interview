package ua.agrichain.work03.persistence;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ExternalEffectRepository extends JpaRepository<ExternalEffect, String> {

    Optional<ExternalEffect> findByTenantIdAndIdempotencyKey(String tenantId, String idempotencyKey);
}