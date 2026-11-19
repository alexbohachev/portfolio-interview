package ua.agrichain.docguard;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
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

/** Контракт відповіді gateway (узгоджено з openapi/gateway.openapi.json). */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class GatewayResponseShapeIT {

    @Autowired
    MockMvc mockMvc;

    @MockBean
    RetrievalClient retrieval;

    @Test
    void healthOpenApiShape() throws Exception {
        mockMvc.perform(get("/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("ok"));
    }

    @Test
    void queryResponseHasContractFields() throws Exception {
        when(retrieval.search(anyString(), eq(List.of("doc_a", "doc_b")), eq(5)))
                .thenReturn(Map.of("hits", List.of(Map.of("doc_id", "doc_a", "snippet", "x"))));
        mockMvc.perform(
                        post("/api/v1/query")
                                .header("X-Tenant-Id", "tenant_a")
                                .header("X-Principal-Id", "alice")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("{\"question\":\"q\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.tenantId").value("tenant_a"))
                .andExpect(jsonPath("$.principalId").value("alice"))
                .andExpect(jsonPath("$.question").value("q"))
                .andExpect(jsonPath("$.hits[0].doc_id").value("doc_a"))
                .andExpect(jsonPath("$.aclRevision").exists());
    }
}