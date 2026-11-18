package ua.agrichain.work03.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import ua.agrichain.work03.persistence.OutboxMessage;
import ua.agrichain.work03.persistence.OutboxMessageRepository;
import ua.agrichain.work03.persistence.OutboxMessage.Status;

@Service
public class OutboxService {

    private final OutboxMessageRepository outboxRepository;
    private final ExternalStubService externalStubService;

    public OutboxService(OutboxMessageRepository outboxRepository, ExternalStubService externalStubService) {
        this.outboxRepository = outboxRepository;
        this.externalStubService = externalStubService;
    }

    @Transactional
    public OutboxMessage getOrCreatePending(
            java.util.UUID workflowRunId,
            String tenantId,
            String idempotencyKey,
            String commandHash,
            String payload) {
        return outboxRepository
                .findByTenantIdAndIdempotencyKey(tenantId, idempotencyKey)
                .orElseGet(() -> {
                    OutboxMessage msg = new OutboxMessage();
                    msg.setWorkflowRunId(workflowRunId);
                    msg.setTenantId(tenantId);
                    msg.setIdempotencyKey(idempotencyKey);
                    msg.setCommandHash(commandHash);
                    msg.setPayload(payload);
                    msg.setStatus(Status.PENDING);
                    return outboxRepository.save(msg);
                });
    }

    /**
     * Доставка наміру в зовнішню систему. Stub ідемпотентний за (tenant, idempotency_key).
     */
    @Transactional
    public String publish(OutboxMessage message) {
        if (message.getStatus() == Status.PUBLISHED && message.getExternalRecordId() != null) {
            return message.getExternalRecordId();
        }
        String recordId = externalStubService.createRecord(
                message.getTenantId(),
                message.getIdempotencyKey(),
                message.getCommandHash(),
                message.getPayload());
        message.setExternalRecordId(recordId);
        message.setStatus(Status.PUBLISHED);
        outboxRepository.save(message);
        return recordId;
    }
}