package ua.agrichain.docguard;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import ua.agrichain.docguard.retrieval.RetrievalClient;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class SecurityMatrixIT {

    @Autowired
    MockMvc mockMvc;

    @MockBean
    RetrievalClient retrieval;

    @Test
    void returnsOnlyAllowedHits() throws Exception {
        when(retrieval.search(anyString(), eq(List.of("doc_a", "doc_b")), eq(5)))
                .thenReturn(Map.of("hits", List.of(Map.of("doc_id", "doc_a", "snippet", "x"))));
        mockMvc.perform(
                        post("/api/v1/query")
                                .header("X-Tenant-Id", "tenant_a")
                                .header("X-Principal-Id", "alice")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("{\"question\":\"бура іржа\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.hits[0].doc_id").value("doc_a"));
    }

    @Test
    void blocksDisallowedDocInResponse() throws Exception {
        when(retrieval.search(anyString(), anyList(), eq(5)))
                .thenReturn(Map.of("hits", List.of(Map.of("doc_id", "doc_leak", "snippet", "secret"))));
        mockMvc.perform(
                        post("/api/v1/query")
                                .header("X-Tenant-Id", "tenant_a")
                                .header("X-Principal-Id", "alice")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("{\"question\":\"test\"}"))
                .andExpect(status().isForbidden());
    }

    @Test
    void unknownPrincipalForbidden() throws Exception {
        mockMvc.perform(
                        post("/api/v1/query")
                                .header("X-Tenant-Id", "tenant_x")
                                .header("X-Principal-Id", "nobody")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("{\"question\":\"q\"}"))
                .andExpect(status().isForbidden());
    }

    @Test
    void degradedWhenPythonDown() throws Exception {
        when(retrieval.search(anyString(), anyList(), eq(5)))
                .thenReturn(Map.of("hits", List.of(), "degraded", true));
        mockMvc.perform(
                        post("/api/v1/query")
                                .header("X-Tenant-Id", "tenant_b")
                                .header("X-Principal-Id", "bob")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("{\"question\":\"q\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.degraded").value(true));
    }
}