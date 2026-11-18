package ua.agrichain.work03.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import ua.agrichain.work03.persistence.ExternalEffect;
import ua.agrichain.work03.persistence.ExternalEffectRepository;

@Service
public class ExternalStubService {

    private final ExternalEffectRepository repository;

    public ExternalStubService(ExternalEffectRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public String createRecord(String tenantId, String idempotencyKey, String commandHash, String payload) {
        return repository
                .findByTenantIdAndIdempotencyKey(tenantId, idempotencyKey)
                .map(e -> e.getId().toString())
                .orElseGet(() -> {
                    ExternalEffect effect = new ExternalEffect();
                    effect.setTenantId(tenantId);
                    effect.setIdempotencyKey(idempotencyKey);
                    effect.setCommandHash(commandHash);
                    effect.setPayload(payload);
                    return repository.save(effect).getId().toString();
                });
    }
}