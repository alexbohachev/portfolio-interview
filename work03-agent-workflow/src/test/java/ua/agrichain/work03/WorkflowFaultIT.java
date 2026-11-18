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
import org.springframework.transaction.annotation.Transactional;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import ua.agrichain.work03.api.dto.SubmitApplicationRequest;
import ua.agrichain.work03.persistence.ExternalEffectRepository;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class WorkflowFaultIT {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    ObjectMapper objectMapper;

    @Autowired
    ExternalEffectRepository externalEffectRepository;

    @Test
    void duplicateIdempotencyKeyProducesSingleExternalEffect() throws Exception {
        var body = new SubmitApplicationRequest("tenant_a", "key-1", "sprayer", 6, "north");
        postOk(body);
        postOk(body);
        assertThat(externalEffectRepository.count()).isEqualTo(1);
    }

    @Test
    void sameKeyDifferentCommandReturnsConflict() throws Exception {
        postOk(new SubmitApplicationRequest("tenant_a", "key-2", "sprayer", 6, "north"));
        mockMvc.perform(
                        post("/api/v1/applications")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(
                                        new SubmitApplicationRequest("tenant_a", "key-2", "sprayer", 8, "north"))))
                .andExpect(status().isConflict());
    }

    private void postOk(SubmitApplicationRequest body) throws Exception {
        MvcResult result = mockMvc.perform(
                        post("/api/v1/applications")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isOk())
                .andReturn();
        assertThat(result.getResponse().getContentAsString()).contains("COMPLETED");
    }
}