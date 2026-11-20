package ua.agrichain.logistics;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/** Фіксує суть кейсу N+1: «після» = 1 виклик rag-api, «до» = по виклику на токен + 2. */
class EquipmentSearchServiceTest {

    private RagClient rag;
    private EquipmentSearchService service;

    @BeforeEach
    void setUp() {
        rag = mock(RagClient.class);
        service = new EquipmentSearchService(rag);
    }

    private static RagClient.SearchResponse hits(String... ids) {
        return new RagClient.SearchResponse(
                java.util.Arrays.stream(ids).map(id -> new RagClient.Hit(id, "s-" + id, 1.0)).toList());
    }

    @Test
    void searchFastMakesExactlyOneHybridCall() {
        when(rag.search("трактор John Deere", 5, "hybrid")).thenReturn(hits("a", "b"));

        List<RagClient.Hit> out = service.searchFast("трактор John Deere", 5);

        assertEquals(List.of("a", "b"), out.stream().map(RagClient.Hit::docId).toList());
        verify(rag, times(1)).search(anyString(), anyInt(), anyString());
        verifyNoMoreInteractions(rag);
    }

    @Test
    void searchSlowCallsRagOncePerTokenPlusBm25AndHybrid() {
        when(rag.search(anyString(), anyInt(), anyString())).thenReturn(hits());

        service.searchSlow("трактор John Deere", 5); // 3 токени

        verify(rag, times(3)).search(anyString(), eq(2), eq("hybrid"));
        verify(rag, times(1)).search("трактор John Deere", 5, "bm25");
        verify(rag, times(1)).search("трактор John Deere", 5, "hybrid");
        verify(rag, times(5)).search(anyString(), anyInt(), anyString());
    }

    @Test
    void searchSlowSkipsOneCharTokensAndDeduplicatesAndRespectsTopK() {
        when(rag.search(anyString(), anyInt(), anyString())).thenReturn(hits("a", "b", "c"));

        List<RagClient.Hit> out = service.searchSlow("a комбайн", 2);

        verify(rag, times(1)).search("комбайн", 2, "hybrid"); // токен "a" пропущено
        assertEquals(2, out.size());
        assertEquals(out.size(), out.stream().map(RagClient.Hit::docId).distinct().count());
        assertTrue(out.size() <= 2);
    }
}
