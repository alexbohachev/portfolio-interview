package ua.agrichain.work03.service;

import java.util.Optional;
import org.springframework.stereotype.Component;
import ua.agrichain.work03.persistence.ExternalEffect;
import ua.agrichain.work03.persistence.ExternalEffectRepository;
import ua.agrichain.work03.persistence.WorkflowRun;

@Component
public class WorkflowRecovery {

    private final ExternalEffectRepository externalEffectRepository;

    public WorkflowRecovery(ExternalEffectRepository externalEffectRepository) {
        this.externalEffectRepository = externalEffectRepository;
    }

    /** Падіння після commit у зовнішній системі, до checkpoint workflow. */
    public Optional<String> findCommittedExternalRecord(WorkflowRun run) {
        return externalEffectRepository
                .findByTenantIdAndIdempotencyKey(run.getTenantId(), run.getIdempotencyKey())
                .map(ExternalEffect::getId)
                .map(Object::toString);
    }
}