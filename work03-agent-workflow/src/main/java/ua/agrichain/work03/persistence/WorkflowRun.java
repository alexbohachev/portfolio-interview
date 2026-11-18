package ua.agrichain.work03.persistence;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(
        name = "workflow_runs",
        uniqueConstraints = @UniqueConstraint(columnNames = {"tenant_id", "idempotency_key"}))
public class WorkflowRun {

    public enum Status {
        RUNNING,
        COMPLETED,
        FAILED
    }

    public enum Step {
        NONE,
        RULES,
        CALCULATE,
        EXTERNAL
    }

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "tenant_id", nullable = false)
    private String tenantId;

    @Column(name = "idempotency_key", nullable = false)
    private String idempotencyKey;

    @Column(name = "command_hash", nullable = false)
    private String commandHash;

    @Enumerated(EnumType.STRING)
    private Status status = Status.RUNNING;

    @Enumerated(EnumType.STRING)
    private Step lastCompletedStep = Step.NONE;

    private String policyRule;
    private Double estimatedCost;
    private String externalRecordId;

    @Column(nullable = false)
    private Instant createdAt = Instant.now();

    public UUID getId() {
        return id;
    }

    public String getTenantId() {
        return tenantId;
    }

    public void setTenantId(String tenantId) {
        this.tenantId = tenantId;
    }

    public String getIdempotencyKey() {
        return idempotencyKey;
    }

    public void setIdempotencyKey(String idempotencyKey) {
        this.idempotencyKey = idempotencyKey;
    }

    public String getCommandHash() {
        return commandHash;
    }

    public void setCommandHash(String commandHash) {
        this.commandHash = commandHash;
    }

    public Status getStatus() {
        return status;
    }

    public void setStatus(Status status) {
        this.status = status;
    }

    public Step getLastCompletedStep() {
        return lastCompletedStep;
    }

    public void setLastCompletedStep(Step lastCompletedStep) {
        this.lastCompletedStep = lastCompletedStep;
    }

    public String getPolicyRule() {
        return policyRule;
    }

    public void setPolicyRule(String policyRule) {
        this.policyRule = policyRule;
    }

    public Double getEstimatedCost() {
        return estimatedCost;
    }

    public void setEstimatedCost(Double estimatedCost) {
        this.estimatedCost = estimatedCost;
    }

    public String getExternalRecordId() {
        return externalRecordId;
    }

    public void setExternalRecordId(String externalRecordId) {
        this.externalRecordId = externalRecordId;
    }
}