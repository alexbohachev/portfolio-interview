package ua.agrichain.work03.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import ua.agrichain.work03.api.dto.ApplicationResponse;
import ua.agrichain.work03.api.dto.SubmitApplicationRequest;
import ua.agrichain.work03.persistence.WorkflowRun;
import ua.agrichain.work03.persistence.WorkflowRunRepository;
import ua.agrichain.work03.persistence.WorkflowRun.Step;
import ua.agrichain.work03.persistence.OutboxMessage;
import ua.agrichain.work03.service.tools.CalculatorTool;
import ua.agrichain.work03.service.tools.RuleSearchTool;

@Service
public class WorkflowService {

    private final WorkflowRunRepository workflowRunRepository;
    private final CommandHashing commandHashing;
    private final RuleSearchTool ruleSearchTool;
    private final CalculatorTool calculatorTool;
    private final OutboxService outboxService;
    private final WorkflowRecovery workflowRecovery;

    public WorkflowService(
            WorkflowRunRepository workflowRunRepository,
            CommandHashing commandHashing,
            RuleSearchTool ruleSearchTool,
            CalculatorTool calculatorTool,
            OutboxService outboxService,
            WorkflowRecovery workflowRecovery) {
        this.workflowRunRepository = workflowRunRepository;
        this.commandHashing = commandHashing;
        this.ruleSearchTool = ruleSearchTool;
        this.calculatorTool = calculatorTool;
        this.outboxService = outboxService;
        this.workflowRecovery = workflowRecovery;
    }

    @Transactional
    public ApplicationResponse handle(SubmitApplicationRequest request) {
        String hash = commandHashing.hashEquipmentApplication(
                request.equipmentType(), request.requestedHours(), request.region());

        var existing = workflowRunRepository.findByTenantIdAndIdempotencyKey(
                request.tenantId(), request.idempotencyKey());
        if (existing.isPresent()) {
            WorkflowRun run = existing.get();
            if (!run.getCommandHash().equals(hash)) {
                throw new IdempotencyConflictException("idempotency_key reused with different command");
            }
            if (run.getStatus() == WorkflowRun.Status.COMPLETED) {
                return toResponse(run, true);
            }
            return executeFromCheckpoint(run, request, hash, true);
        }

        WorkflowRun run = new WorkflowRun();
        run.setTenantId(request.tenantId());
        run.setIdempotencyKey(request.idempotencyKey());
        run.setCommandHash(hash);
        run = workflowRunRepository.save(run);
        return executeFromCheckpoint(run, request, hash, false);
    }

    private ApplicationResponse executeFromCheckpoint(
            WorkflowRun run, SubmitApplicationRequest request, String hash, boolean replayed) {
        if (run.getLastCompletedStep().ordinal() < Step.RULES.ordinal()) {
            String rule = ruleSearchTool.findPolicyRule(request.equipmentType(), request.region());
            run.setPolicyRule(rule);
            run.setLastCompletedStep(Step.RULES);
            workflowRunRepository.saveAndFlush(run);
        }
        if (run.getLastCompletedStep().ordinal() < Step.CALCULATE.ordinal()) {
            double cost = calculatorTool.estimateCost(run.getPolicyRule(), request.requestedHours());
            run.setEstimatedCost(cost);
            run.setLastCompletedStep(Step.CALCULATE);
            workflowRunRepository.saveAndFlush(run);
        }
        if (run.getLastCompletedStep().ordinal() < Step.EXTERNAL.ordinal()) {
            String recordId = workflowRecovery
                    .findCommittedExternalRecord(run)
                    .orElseGet(() -> {
                        String payload = "equipment=%s;hours=%d;cost=%.2f"
                                .formatted(request.equipmentType(), request.requestedHours(), run.getEstimatedCost());
                        OutboxMessage outbox = outboxService.getOrCreatePending(
                                run.getId(),
                                request.tenantId(),
                                request.idempotencyKey(),
                                hash,
                                payload);
                        return outboxService.publish(outbox);
                    });
            run.setExternalRecordId(recordId);
            run.setLastCompletedStep(Step.EXTERNAL);
            run.setStatus(WorkflowRun.Status.COMPLETED);
            workflowRunRepository.saveAndFlush(run);
        }
        return toResponse(run, replayed);
    }

    private ApplicationResponse toResponse(WorkflowRun run, boolean replayed) {
        return new ApplicationResponse(
                run.getId(),
                run.getStatus().name(),
                run.getPolicyRule(),
                run.getEstimatedCost(),
                run.getExternalRecordId(),
                replayed);
    }
}