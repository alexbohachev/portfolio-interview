[**Українська**](ADR.md) | [English](ADR.en.md)

# ADR (чернетка work05)

1. **ACL у YAML до MVP** — швидкий аудит; далі — DB + версія в ключі кешу.
2. **Перевірка doc_id у Java** — навіть якщо Python помилиться, gateway блокує витік.
3. **Degraded без Python** — порожні hits + прапорець, не 500 клієнту.