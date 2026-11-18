package ua.agrichain.work03;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;
import ua.agrichain.work03.api.dto.SubmitApplicationRequest;
import ua.agrichain.work03.persistence.ExternalEffect;
import ua.agrichain.work03.persistence.ExternalEffectRepository;
import ua.agrichain.work03.persistence.WorkflowRun;
import ua.agrichain.work03.persistence.WorkflowRunRepository;
import ua.agrichain.work03.persistence.WorkflowRun.Step;
import ua.agrichain.work03.service.CommandHashing;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class WorkflowFaultScenariosIT {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    ObjectMapper objectMapper;

    @Autowired
    WorkflowRunRepository workflowRunRepository;

    @Autowired
    ExternalEffectRepository externalEffectRepository;

    @Autowired
    CommandHashing commandHashing;

    @Test
    void resumeFromCalculateCheckpoint() throws Exception {
        var body = new SubmitApplicationRequest("tenant_b", "resume-1", "sprayer", 4, "south");
        var run = new WorkflowRun();
        run.setTenantId(body.tenantId());
        run.setIdempotencyKey(body.idempotencyKey());
        run.setCommandHash(commandHashing.hashEquipmentApplication(
                body.equipmentType(), body.requestedHours(), body.region()));
        run.setPolicyRule("STANDARD_12H");
        run.setEstimatedCost(380.0);
        run.setLastCompletedStep(Step.CALCULATE);
        workflowRunRepository.saveAndFlush(run);

        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isOk());

        assertThat(workflowRunRepository.findByTenantIdAndIdempotencyKey(body.tenantId(), body.idempotencyKey())
                        .orElseThrow()
                        .getStatus())
                .isEqualTo(WorkflowRun.Status.COMPLETED);
        assertThat(externalEffectRepository.count()).isEqualTo(1);
    }

    @Test
    void recoverWhenExternalEffectCommittedBeforeWorkflowCheckpoint() throws Exception {
        var body = new SubmitApplicationRequest("tenant_c", "crash-1", "tractor", 5, "east");
        String hash = commandHashing.hashEquipmentApplication(
                body.equipmentType(), body.requestedHours(), body.region());

        var effect = new ExternalEffect();
        effect.setTenantId(body.tenantId());
        effect.setIdempotencyKey(body.idempotencyKey());
        effect.setCommandHash(hash);
        effect.setPayload("precommitted");
        externalEffectRepository.saveAndFlush(effect);

        var run = new WorkflowRun();
        run.setTenantId(body.tenantId());
        run.setIdempotencyKey(body.idempotencyKey());
        run.setCommandHash(hash);
        run.setPolicyRule("STANDARD_12H");
        run.setEstimatedCost(475.0);
        run.setLastCompletedStep(Step.CALCULATE);
        workflowRunRepository.saveAndFlush(run);

        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isOk());

        assertThat(externalEffectRepository.count()).isEqualTo(1);
        assertThat(workflowRunRepository.findByTenantIdAndIdempotencyKey(body.tenantId(), body.idempotencyKey())
                        .orElseThrow()
                        .getExternalRecordId())
                .isNotNull();
    }

    @Test
    void newIdempotencyKeyWithSameCommandCreatesSecondEffect() throws Exception {
        var args = new SubmitApplicationRequest("tenant_d", "key-a", "sprayer", 3, "north");
        postApplication(args);
        var args2 = new SubmitApplicationRequest("tenant_d", "key-b", "sprayer", 3, "north");
        postApplication(args2);
        assertThat(externalEffectRepository.count()).isEqualTo(2);
    }

    @Test
    void invalidRequestDoesNotPersistWorkflow() throws Exception {
        long before = workflowRunRepository.count();
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(
                                """
                                {"tenantId":"","idempotencyKey":"x","equipmentType":"a",\
                                "requestedHours":0,"region":"north"}
                                """))
                .andExpect(status().isBadRequest());
        assertThat(workflowRunRepository.count()).isEqualTo(before);
    }

    private void postApplication(SubmitApplicationRequest body) throws Exception {
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isOk());
    }
}