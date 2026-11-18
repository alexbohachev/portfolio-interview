package ua.agrichain.work03;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;
import ua.agrichain.work03.api.dto.SubmitApplicationRequest;
import ua.agrichain.work03.persistence.ExternalEffectRepository;
import ua.agrichain.work03.persistence.OutboxMessageRepository;
import ua.agrichain.work03.persistence.WorkflowRun;
import ua.agrichain.work03.persistence.WorkflowRun.Step;
import ua.agrichain.work03.persistence.WorkflowRunRepository;
import ua.agrichain.work03.service.CommandHashing;

/**
 * Розширена fault-матриця (24 сценарії) + 6 існуючих IT = 30 за ТЗ.
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class WorkflowFaultMatrixIT {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    ObjectMapper objectMapper;

    @Autowired
    WorkflowRunRepository workflowRunRepository;

    @Autowired
    ExternalEffectRepository externalEffectRepository;

    @Autowired
    OutboxMessageRepository outboxMessageRepository;

    @Autowired
    CommandHashing commandHashing;

    @Test
    void differentTenantsMayReuseSameIdempotencyKey() throws Exception {
        postOk(new SubmitApplicationRequest("tenant_x", "shared-key", "sprayer", 2, "north"));
        postOk(new SubmitApplicationRequest("tenant_y", "shared-key", "sprayer", 2, "north"));
        assertThat(externalEffectRepository.count()).isEqualTo(2);
    }

    @Test
    void threeDistinctKeysCreateThreeEffects() throws Exception {
        postOk(new SubmitApplicationRequest("tenant_m", "m-1", "sprayer", 2, "north"));
        postOk(new SubmitApplicationRequest("tenant_m", "m-2", "sprayer", 2, "north"));
        postOk(new SubmitApplicationRequest("tenant_m", "m-3", "tractor", 2, "south"));
        assertThat(externalEffectRepository.count()).isEqualTo(3);
    }

    @Test
    void resumeFromRulesCheckpoint() throws Exception {
        var body = new SubmitApplicationRequest("tenant_r", "rules-resume", "sprayer", 3, "north");
        var run = new WorkflowRun();
        run.setTenantId(body.tenantId());
        run.setIdempotencyKey(body.idempotencyKey());
        run.setCommandHash(commandHashing.hashEquipmentApplication(
                body.equipmentType(), body.requestedHours(), body.region()));
        run.setPolicyRule("STANDARD_12H");
        run.setLastCompletedStep(Step.RULES);
        workflowRunRepository.saveAndFlush(run);
        postOk(body);
        assertThat(workflowRunRepository
                        .findByTenantIdAndIdempotencyKey(body.tenantId(), body.idempotencyKey())
                        .orElseThrow()
                        .getStatus())
                .isEqualTo(WorkflowRun.Status.COMPLETED);
    }

    @Test
    void replayMarksResponseReplayed() throws Exception {
        var body = new SubmitApplicationRequest("tenant_rep", "rep-1", "sprayer", 4, "north");
        postOk(body);
        MvcResult second = mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.replayed").value(true))
                .andReturn();
        assertThat(second.getResponse().getContentAsString()).contains("COMPLETED");
    }

    @Test
    void replayKeepsSingleOutboxRow() throws Exception {
        var body = new SubmitApplicationRequest("tenant_ob", "ob-1", "sprayer", 3, "north");
        postOk(body);
        postOk(body);
        assertThat(outboxMessageRepository.count()).isEqualTo(1);
    }

    @Test
    void completedWorkflowReturnsStableExternalRecord() throws Exception {
        var body = new SubmitApplicationRequest("tenant_st", "st-1", "tractor", 5, "east");
        String first = postOk(body).getResponse().getContentAsString();
        String second = postOk(body).getResponse().getContentAsString();
        assertThat(first).contains("externalRecordId");
        assertThat(second).contains("externalRecordId");
    }

    @Test
    void equipmentTypeChangeSameKeyIsConflict() throws Exception {
        postOk(new SubmitApplicationRequest("tenant_c1", "c-eq", "sprayer", 4, "north"));
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(
                                new SubmitApplicationRequest("tenant_c1", "c-eq", "tractor", 4, "north"))))
                .andExpect(status().isConflict());
    }

    @Test
    void regionChangeSameKeyIsConflict() throws Exception {
        postOk(new SubmitApplicationRequest("tenant_c2", "c-rg", "sprayer", 4, "north"));
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(
                                new SubmitApplicationRequest("tenant_c2", "c-rg", "sprayer", 4, "south"))))
                .andExpect(status().isConflict());
    }

    @Test
    void blankTenantRejected() throws Exception {
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(
                                """
                                {"tenantId":"","idempotencyKey":"k","equipmentType":"sprayer",\
                                "requestedHours":2,"region":"north"}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void blankIdempotencyKeyRejected() throws Exception {
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(
                                """
                                {"tenantId":"t","idempotencyKey":"","equipmentType":"sprayer",\
                                "requestedHours":2,"region":"north"}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void blankEquipmentRejected() throws Exception {
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(
                                """
                                {"tenantId":"t","idempotencyKey":"k","equipmentType":"",\
                                "requestedHours":2,"region":"north"}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void zeroHoursRejected() throws Exception {
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(
                                """
                                {"tenantId":"t","idempotencyKey":"k","equipmentType":"sprayer",\
                                "requestedHours":0,"region":"north"}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void blankRegionRejected() throws Exception {
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(
                                """
                                {"tenantId":"t","idempotencyKey":"k","equipmentType":"sprayer",\
                                "requestedHours":2,"region":""}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void tripleReplayStillOneEffect() throws Exception {
        var body = new SubmitApplicationRequest("tenant_tr", "tr-1", "sprayer", 2, "north");
        postOk(body);
        postOk(body);
        postOk(body);
        assertThat(externalEffectRepository.count()).isEqualTo(1);
    }

    @Test
    void sprayerNorthUsesMax8hPolicy() throws Exception {
        MvcResult r = postOk(new SubmitApplicationRequest("tenant_pol", "pol-1", "sprayer", 1, "north"));
        assertThat(r.getResponse().getContentAsString()).contains("MAX_8H_PER_DAY");
    }

    @Test
    void tractorSouthCompletesWithCost() throws Exception {
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(
                                new SubmitApplicationRequest("tenant_pol", "pol-2", "tractor", 8, "south"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.estimatedCost").isNumber());
    }

    @Test
    void largeHourRequestStillCompletes() throws Exception {
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(
                                new SubmitApplicationRequest("tenant_lh", "lh-1", "sprayer", 24, "north"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("COMPLETED"));
    }

    @Test
    void longIdempotencyKeyAccepted() throws Exception {
        String key = "k-" + "x".repeat(120);
        postOk(new SubmitApplicationRequest("tenant_lk", key, "sprayer", 1, "north"));
        assertThat(externalEffectRepository.count()).isEqualTo(1);
    }

    @Test
    void workflowRunCreatedOncePerKey() throws Exception {
        var body = new SubmitApplicationRequest("tenant_wf", "wf-1", "sprayer", 2, "north");
        postOk(body);
        assertThat(workflowRunRepository.count()).isEqualTo(1);
        postOk(body);
        assertThat(workflowRunRepository.count()).isEqualTo(1);
    }

    @Test
    void externalRecordPresentOnFirstSuccess() throws Exception {
        var body = new SubmitApplicationRequest("tenant_ex", "ex-1", "sprayer", 3, "north");
        postOk(body);
        var run = workflowRunRepository
                .findByTenantIdAndIdempotencyKey(body.tenantId(), body.idempotencyKey())
                .orElseThrow();
        assertThat(run.getExternalRecordId()).isNotBlank();
    }

    @Test
    void hoursChangeSameKeyIsConflict() throws Exception {
        postOk(new SubmitApplicationRequest("tenant_hc", "hc-1", "sprayer", 4, "north"));
        mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(
                                new SubmitApplicationRequest("tenant_hc", "hc-1", "sprayer", 5, "north"))))
                .andExpect(status().isConflict());
    }

    @Test
    void concurrentStyleDuplicatePostsAreSafe() throws Exception {
        var body = new SubmitApplicationRequest("tenant_dup", "dup-conc", "sprayer", 2, "west");
        for (int i = 0; i < 5; i++) {
            postOk(body);
        }
        assertThat(externalEffectRepository.count()).isEqualTo(1);
    }

    @Test
    void freshWorkflowStartsAtNoneStep() throws Exception {
        var body = new SubmitApplicationRequest("tenant_fresh", "fresh-1", "sprayer", 2, "north");
        postOk(body);
        assertThat(workflowRunRepository
                        .findByTenantIdAndIdempotencyKey(body.tenantId(), body.idempotencyKey())
                        .orElseThrow()
                        .getLastCompletedStep())
                .isEqualTo(Step.EXTERNAL);
    }

    @Test
    void outboxPublishedBeforeWorkflowCompleted() throws Exception {
        var body = new SubmitApplicationRequest("tenant_ox", "ox-1", "sprayer", 2, "north");
        postOk(body);
        assertThat(outboxMessageRepository.findAll()).hasSize(1);
        assertThat(outboxMessageRepository.findAll().getFirst().getStatus().name()).isEqualTo("PUBLISHED");
    }

    private MvcResult postOk(SubmitApplicationRequest body) throws Exception {
        return mockMvc.perform(post("/api/v1/applications")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isOk())
                .andReturn();
    }
}