package ua.agrichain.work03.persistence;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OutboxMessageRepository extends JpaRepository<OutboxMessage, UUID> {

    Optional<OutboxMessage> findByTenantIdAndIdempotencyKey(String tenantId, String idempotencyKey);

    Optional<OutboxMessage> findByWorkflowRunId(UUID workflowRunId);
}