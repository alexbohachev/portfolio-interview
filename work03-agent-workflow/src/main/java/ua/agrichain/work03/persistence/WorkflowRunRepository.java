package ua.agrichain.work03.persistence;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowRunRepository extends JpaRepository<WorkflowRun, UUID> {

    Optional<WorkflowRun> findByTenantIdAndIdempotencyKey(String tenantId, String idempotencyKey);
}