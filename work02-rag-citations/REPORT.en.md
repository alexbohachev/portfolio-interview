[Українська](REPORT.md) | **English**

# Report — work 2: RAG with citations

## Task
Retrieval (BM25 vs hybrid RRF) + retrieval gate + answer with citations (extractive offline / LLM with a key).

## Corpus
- documents: 200, fingerprint `21de45e90e9664b3`
- test golden sha: `0993914458593c21`

## Retrieval (test)
| System | Recall@5 | n |
| baseline BM25 | 1.0000 | 40 |
| candidate hybrid | 1.0000 | 40 |

**Retrieval gate** (max RRF threshold on dev): `0.0313`

## QA (test, candidate + gate)
- Correct refusals: 10 / 10
- Citation precision (evidence overlap): 35 / 35
- Answer contains the gold fragment: 28 / 28

## Limitations
- Synthetic corpus of 200 docs; LLM disabled by default.
- The prompt does not replace the retrieval gate (refusal happens only in code, via the threshold).

## Next step
- `.\make.ps1 plan-corpus` → open corpus of 200–500 + manual golden; `.\make.ps1 eval-llm` (30 dev).

_Time: 6.93 s._
