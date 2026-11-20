[Українська](REPORT.md) | **English**

# Report — work 3: reliable agent workflow

## Task

Equipment request: **3 tools** (rules, calculator, external record), PostgreSQL checkpoint, idempotency_key + command_hash, **outbox** before the external effect.

## Baseline

Deterministic step order without an LLM planner.

## Architecture

```text
POST /applications → WorkflowRun (checkpoint) → Outbox PENDING → Stub (idempotent) → COMPLETED
                              ↑_________________recovery if effect exists________________|
```

## Fault scenarios (JUnit, `test` profile)

| # | Scenario | Expectation | Status |
|---|----------|------------|--------|
| 1 | Repeated idempotency_key | 1 `external_effects` | pass |
| 2 | Same key, different hash | HTTP 409 | pass |
| 3 | Restart from checkpoint CALCULATE | COMPLETED, 1 effect | pass |
| 4 | Effect already in DB, workflow not finished | 1 effect, checkpoint is completed | pass |
| 5 | New key, same arguments | 2 effects (allowed by the domain) | pass |
| 6 | Invalid input | 400, workflow is not created | pass |

**30 / 30** automated scenarios (`WorkflowFaultIT` + `WorkflowFaultScenariosIT` + `WorkflowFaultMatrixIT`).

## Metrics (MVP)

- Duplicated external effects in idempotency fault tests: **0 / n** (n=2 repeats)
- Successful completion in scenarios 1–5: **5 / 5**

## Limitations

- Outbox without a separate worker/queue (publishing is synchronous in the same transaction).
- LLM planner is not connected (candidate).

## Next step

- Spring AI candidate, human-in-the-loop, Testcontainers PostgreSQL in CI.

_Tag `work03-v1.0` — on main._
