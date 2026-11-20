[Українська](ADR.md) | **English**

# ADR (work05 draft)

1. **ACL in YAML until the MVP** — quick audit; later — DB + version in the cache key.
2. **doc_id check in Java** — even if Python makes a mistake, the gateway blocks the leak.
3. **Degraded mode without Python** — empty hits + a flag, not a 500 to the client.
