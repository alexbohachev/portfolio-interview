[**Українська**](README.md) | [English](README.en.md)

# Інженерне портфоліо — AI Systems & Applied Machine Learning

[![CI: Clean-Clone Reproducibility](https://github.com/alexbohachev/portfolio-interview/actions/workflows/repro.yml/badge.svg)](https://github.com/alexbohachev/portfolio-interview/actions/workflows/repro.yml)
[![All GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI_Runs-blue)](https://github.com/alexbohachev/portfolio-interview/actions)
[![Demo Video (60s MP4)](https://img.shields.io/badge/Demo_Video-60s_MP4_Walkthrough-blueviolet)](https://github.com/alexbohachev/portfolio-interview/blob/main/assets/work07_demo_walkthrough.mp4)
[![Demo Script (5-7 min)](https://img.shields.io/badge/Demo_Script-5--7_min_Walkthrough-purple)](https://github.com/alexbohachev/portfolio-interview/blob/main/work07-ai-platform/DEMO_SCRIPT_5MIN.md)
[![Live Demo Runner](https://img.shields.io/badge/Live_Demo-scripts%2Flive__interview.ps1-orange)](scripts/live_interview.ps1)

Відтворюване інженерне портфоліо з **7 еталонних проєктів (+ 1 допоміжна офлайн-утиліта)**:
* **Розподілені AI-платформи (Java 21, Python 3.13, Docker, Kafka, OpenTelemetry):** кейс N+1 латентності: відтворено та заміряно локально (p95 знизився зі 231.5 мс до 46.9 мс), Pre-LLM Zero-Trust шлюз безпеки та Transactional Outbox відновлення (30/30 пройдених тестів зі збоями).
* **Прикладне машинне навчання та MLOps (PyTorch, LightGBM, FastAPI):** часовий бектестинг на даних UCI без leakage, прогнозування попиту на багатьох рядах з конформним калібруванням (LightGBM на синтетиці; сезонний бейзлайн на реальних даних Bikeshare за принципом бритви Оккама) та сервінг на FastAPI з контролем дрейфу ознак.

> **Англомовний огляд:** [`README.en.md`](README.en.md) · **Інструкція відтворення:** [`REPRO.md`](REPRO.md) · **Розбір N+1 кейсу:** [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) · **Сценарій живого демо:** [`DEMO_SCRIPT_5MIN.md`](work07-ai-platform/DEMO_SCRIPT_5MIN.md) · **Автономний лонгрід:** [`STANDALONE_PORTFOLIO.md`](STANDALONE_PORTFOLIO.md)

---

## Можливості та операційні межі

Кожна метрика нижче підтверджена закомічними наборами тестів, закомічними масивами сирих вимірювань та автоматизованими тестами збоїв у CI:

| Напрям | Доказ у монорепозиторії | Можливості та виміряний ефект | Операційні межі (Scope) |
|---|---|---|---|
| **AI-системи та продуктивність** | **Work 07 (AI Platform)** | Виміряно антипатерн N+1 між мікросервісами (Java → Python RAG API). **p95 знижено з 231.5 мс → 46.9 мс (прискорення 4.94×; p50: 171.6 мс → 33.9 мс, 5.06×)** через серверний гібридний RRF-пошук; перевірено трейсами OpenTelemetry/Jaeger та закомічними масивами таймінгів. | Локальний бенчмарк у Docker Compose; не гео-розподілений кластер Kubernetes. |
| **Безпека корпоративного AI** | **Work 05 (DocGuard)** | Zero-trust Pre-LLM шлюз (Java 21 + FastAPI). Перехоплює запити до векторної БД чи LLM. **Підтверджена ізоляція тенантів на 8 автоматизованих атакових сценаріях**, дослівний аудит запитів і degraded circuit-breaker. | ACL-кеш у пам'яті з REST-інвалідацією; не зовнішній корпоративний IdP (Ory/Keycloak). |
| **Прикладний ML та бектестинг** | **Work 01 (Bank Marketing)** | Емпірично строгий табличний ML на реальних даних UCI. **Суворе усунення target leakage** (прибрано `duration`, відомий лише після дзвінка), хронологічний split за сильного covariate shift (5.8% → 39.3%), bootstrap 95% CI показує, що нейромережа не перевершує калібрований лінійний бейзлайн. | Табличний датасет UCI; temperature scaling сам по собі не усуває shift без domain adaptation. |
| **Прогнозування попиту та ризик** | **Work 08 (Demand Forecasting)** | Rolling-бектести на 4 сезонах ($H=14$) за двома бенчмарками: (1) **Синтетична агросимуляція (20 рядів)**: LightGBM знизив WAPE з 13.2% до 7.8% (-41%), політика Newsvendor скоротила змодельовані витрати на запаси на 43%, а CQR дав спостережуване покриття $\ge 80.0\%$ (середнє 84.1%). (2) **Реальні дані Capital Bikeshare (2011–2012)**: сезонний бейзлайн переміг LightGBM (35.4% проти 37.7% WAPE), і для продакшну обрано бейзлайн. CQR підняв емпіричне покриття з 26.8% до 75.9%. | Пряма модель прогнозу зафіксована на операційному горизонті $H=14$; exchangeability виконується на синтетичних рядах, але порушується за дрейфу фізичного розширення парку. |
| **Продакшн ML-сервінг і дрейф** | **Work 04 (Risk Serving)** | FastAPI-сервінг моделі. Поріг за матрицею бізнес-витрат ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$), версійований `/v1/predict` і демонстраційний ендпоінт дрейфу за z-score. | Синтетичні дані з детермінованою міткою (PR-AUC 1.0 = тривіальна задача); колонки `available_at` є в контракті даних, але кодом не застосовуються; перевірка дрейфу без тестів і без реальних потокових батчів. |
| **Розподілена стійкість** | **Work 03 (Agent Workflow)** | Детермінований 3-кроковий оркестратор з **Transactional Outbox та відновленням із checkpoint**. Витримав **30/30 автоматизованих сценаріїв збоїв** без дублювання зовнішніх ефектів; повертає HTTP 409 Conflict при підміні payload. | Транзакційна межа Spring Boot + PostgreSQL на одному вузлі; не претендує на багатовузловий консенсус (Raft/Paxos). |
| **Пошук і retrieval-наука** | **Work 02 і 07 (RAG Science)** | Гібридний RRF-пошук (Elasticsearch BM25 + dense kNN). **Стрес-тест на 10 складних доменних запитах**: 8 запитів із відповіддю (Recall@5: BM25 0.125, Hybrid 0.25, Hybrid + Cross-Encoder 0.50; цей приріст НЕ відтворився: на розширеному наборі з 40 запитів усі три методи мають Recall@5 = 0.05, приріст reranker-а 0.0, 95% CI [-0.075, 0.075]) + 2 запити поза доменом. | 200 доменних документів; сам bi-encoder потребує доменного fine-tuning або cross-encoder re-ranking для тонкої дискримінації. |
| **Full Stack Engineering** | **Монорепозиторій** | Java 21 (Spring Boot 3, RestClient), Python 3.13 (FastAPI, PyTorch/SentenceTransformers), Docker Compose, Kafka, Elasticsearch, Jaeger. | Мультиплатформений CI перевіряє офлайн-набір тестів (<30 с) та Docker-інтеграційний набір. |

---

## Ключові кейси

### 1. Work 07 — Розподілена AI-платформа: відтворений антипатерн N+1 та оптимізація латентності

```
[Клієнт / мобільний застосунок]
       │
       ▼
[Logistics Service (Java 21)] ──(Trace: OpenTelemetry)──► [Jaeger UI :16687]
       │
       ├─► (searchSlow: N+1 викликів на токен) ──┐
       │                                         ▼
       └─► (searchFast: один гібридний виклик) ──► [RAG API (Python 3.13 / FastAPI)]
                                                        │
                                                        ▼
                                            [Elasticsearch 8.17 (BM25 + kNN / RRF)]
```

* **Архітектура та контекст бенчмарку:** створено, щоб виміряти поширений антипатерн розподіленого RAG: клієнтський сервіс розбиває запит користувача на токени й робить послідовні HTTP-виклики до пошукового сервісу. Цей варіант реалізовано в `EquipmentSearchService.java` (`searchSlow`: послідовні виклики по токенах) і порівняно з одним серверним гібридним запитом (`searchFast`: Reciprocal Rank Fusion в Elasticsearch 8.17) у локальному Docker Compose.
* **Архітектурне виправлення:** ітеративний пошук замінено одним пакетним гібридним викликом (`searchFast()`), що запитує top-K через серверний RRF в Elasticsearch.

#### Кількісні виміри незалежних прогонів (25 вибірок на профіль, локальний Docker Compose):

* **Run 1 (Baseline, 2026-11-18, Git SHA `6efad68`):**
  * профіль `slow` (N+1): p50 = **172.6 мс** | **p95 = 197.0 мс**
  * профіль `fast` (пакетний hybrid): p50 = **34.0 мс** | **p95 = 53.3 мс**
* **Run 2 (перевірка з чистого клону, 2026-11-19, Git SHA `45d550c`):**
  * профіль `slow` (N+1): p50 = **171.6 мс** | **p95 = 231.5 мс** | mean = 179.2 мс
  * профіль `fast` (пакетний hybrid): p50 = **33.9 мс** | **p95 = 46.9 мс** | mean = 37.9 мс
* **Чистий приріст:** **прискорення 5.06×–5.08× на p50, 3.70× (Run 1, старий метод перцентиля) та 4.94× (Run 2) на p95** (~80% скорочення на p50 і p95 у Run 2).
  * *Примітка щодо методу:* перцентилі Run 2 перераховано лінійною інтерполяцією (стандарт numpy) із закомічених сирих вибірок (`work07-ai-platform/manifests/latency_raw_samples.json`). Перші опубліковані цифри p95 (195.7 / 46.7 мс) рахувалися floor-індексом (23-тє з 25 значень, близько p92) і замінені. З n=25 p95 визначають два найповільніші запити, тож це орієнтовна оцінка; Run 1 лишено як було зафіксовано (старий метод, сирих вибірок немає).
* **Закомічені сирі докази:**
  * масиви таймінгів (усі 25 вибірок на профіль): [`work07-ai-platform/manifests/latency_raw_samples.json`](work07-ai-platform/manifests/latency_raw_samples.json)
  * зведені метрики: [`work07-ai-platform/manifests/latency_before_after.json`](work07-ai-platform/manifests/latency_before_after.json)

#### Стрес-тест складного пошуку: 2-й етап Cross-Encoder Re-ranking (приріст не відтворився)

Стандартні синтетичні тести дають тривіальний `Recall@5 = 1.0`. Щоб оцінити реальні межі retrieval, проведено стрес-тест на **10 складних доменних запитах** (`data/golden/hard_retrieval.json` на 200 документах, спільних із Work 02): **8 запитів із відповіддю** (Recall@5 і MRR@5 на парафразах та multi-hop запитах) і **2 запити без відповіді поза доменом** (для pre-retrieval refusal gate).

Щоб усунути помилки тематичної кластеризації bi-encoder, додано **2-й етап Cross-Encoder re-ranker** (`cross-encoder/ms-marco-MiniLM-L-6-v2`), що оцінює пари $(q, d_i)$ для топ-25 гібридних кандидатів:

* **Кількісна абляція за етапами retrieval (8 запитів із відповіддю):**
  * **BM25 baseline:** Recall@5 = **0.1250** (1/8) | MRR@5 = **0.0625** | 95% bootstrap CI: `[0.000, 0.375]`
  * **1-й етап Hybrid (RRF):** Recall@5 = **0.2500** (2/8) | MRR@5 = **0.0938** | 95% bootstrap CI: `[0.000, 0.625]`
  * **2-й етап Cross-Encoder:** Recall@5 = **0.5000** (4/8) | MRR@5 = **0.1771** | 95% bootstrap CI: `[0.125, 0.875]`
  * **Чистий приріст reranker-а над Hybrid:** $\Delta = +0.2500$ Recall@5 (2/8 → 4/8) | 95% bootstrap CI: `[0.000, 0.625]`. **Це не відтворилося на розширеному наборі з 40 запитів (`hard_retrieval_extended.json`, `manifests/hard_extended_eval_snapshot.json`): Recall@5 = 0.05 для BM25, Hybrid і Cross-Encoder, приріст 0.0, 95% CI `[-0.075, 0.075]`; результат на 8 запитах слід читати як шум.** Низький абсолютний recall відображає обмеження тесту, а не доводить слабкість підходу: 20 синтетичних документів кожної теми відрізняються лише ключовим словом і роком, тож парафраз не може вказати єдину ціль, а обидві моделі (`all-MiniLM-L6-v2`, `ms-marco-MiniLM`) англомовні, тоді як запити українські.
* **Refusal gate:** в цій офлайн-оцінці не вимірюється (gate працює в `rag-api` і потребує Docker); попередні цифри «2/2» і «10/10» походили з жорстко закодованого лічильника і відкликані.
* **Мультимовні моделі змінюють картину** (`paraphrase-multilingual-MiniLM-L12-v2` + `mmarco-mMiniLMv2`, `manifests/hard_extended_eval_snapshot_multilingual.json`): на тих самих 40 запитах cross-encoder дає Recall@5 = 0.20 проти 0.05 у Hybrid (приріст +0.15, 95% CI `[0.025, 0.275]`, нуль не входить), а Hit@5 на рівні теми зростає з 0.575 (Hybrid) до 0.750, тож частина проблеми була в англомовних моделях. Застереження: один прогін на синтетичному корпусі, де документи теми майже ідентичні (випадковий вибір у межах відомої теми дає ~0.25 Recall@5), тому абсолютні значення мало кажуть про якість на реальних даних. Hit@5 на рівні теми відтворюється через `scripts/topic_level_recall.py`.

| Запит і питання | Цільовий документ | BM25 Hit@5 | Hybrid (RRF) Hit@5 | Cross-Encoder Hit@5 | Діагноз і механізм |
|---|---|:---:|:---:|:---:|---|
| **`hard_001`** (парафраз про хвороби пшениці)<br>«Які хвороби пшениці згадують буру іржа та фузаріоз?» | `agri_016_wheat_disease_15` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 3)** | **Перемога Cross-Encoder:** bi-encoder поставив документ на 11-те місце; cross-attention між питанням і текстом абзацу підняла ціль у топ-3. |
| **`hard_004`** (норма висіву соняшнику)<br>«Яка щільність посіву насіння для соняшнику?» | `agri_159_seed_rate_18` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 3)** | **Перемога Cross-Encoder:** dense bi-encoder зіставив документи IPM зі схожою лексикою; Cross-Encoder віддав пріоритет конкретним показникам щільності висіву. |
| **`hard_007`** (multi-hop ризики хвороб)<br>«Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14` | ❌ (Miss) | ❌ (Miss) | **✅ (Rank 4)** | **Перемога Cross-Encoder:** успішно відновив multi-hop ціль про ризики в різні сезони. |
| **`hard_010`** (органіка та гумус)<br>«Органіка та сидерати для підвищення гумусу» | `agri_099_organic_matter_18` | ❌ (Miss) | **✅ (Rank 3)** | **✅ (Rank 2)** | **Перемога Hybrid + CE:** семантичне узагальнення між сидератами та органічним збагаченням ґрунту. |
| **`hard_006`** (точна формула)<br>«Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | ❌ (Miss) | ❌ (Miss) | ❌ (Miss) | **Складний випадок:** точний збіг формули потребує розширення доменного словника. |
| **`hard_008`, `009`** (поза доменом)<br>«Чи вирощують рис на Марсі...» | *Немає (без відповіді)* | н/д | н/д | н/д | Refusal gate в офлайн-оцінці не вимірюється (працює в rag-api, потребує Docker). |

*Закомічені сирі артефакти: [`work07-ai-platform/manifests/eval_per_query.json`](work07-ai-platform/manifests/eval_per_query.json) і [`work07-ai-platform/manifests/hard_eval_snapshot.json`](work07-ai-platform/manifests/hard_eval_snapshot.json).*

* **Команди відтворення:**
  ```bash
  cd work07-ai-platform
  # Офлайн-валідація з Cross-Encoder (Docker не потрібен, ~25 с):
  python scripts/eval_retrieval_offline.py
  # Валідація на живому Docker-кластері:
  docker compose up -d --build
  python scripts/benchmark_latency.py
  python scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --doc-id-prefix agri_
  ```
  *(Windows PowerShell: `.\make.ps1 build; .\make.ps1 up; py -3.13 scripts/benchmark_latency.py; .\make.ps1 eval-hard`)*

---

### 2. Work 05 — DocGuard: Zero-Trust шлюз безпеки перед LLM

```
[Запит користувача (tenant_a, alice)]
       │
       ▼
[DocGuard Gateway (Java 21 / Spring)] ──► [ACL Engine (Principal & Tenant RBAC)]
       │ (Застосовує дозволені doc_ids)
       ▼
[Retrieval Service (Python / FastAPI)] ──► [Відфільтрована база знань]
       │
       ▼ (Повертає лише дозволені фрагменти)
[Audit Logger (дослівний запит + фіксація prompt injection)]
```

* **Проблема:** RAG-архітектури часто витікають приватні корпоративні дані, коли документи кількох тенантів ділять векторну БД, або коли зловмисники використовують prompt injection, щоб перевизначити системні промпти LLM.
* **Архітектура:** DocGuard перехоплює запити **до** будь-якої моделі чи векторного сховища.
  1. Перетворює відповідність tenant і principal на whitelist дозволених `doc_id`.
  2. Вкладає фільтр безпеки прямо в retrieval-запит (`allowedDocIds`).
  3. Перевіряє повернуті документи на виході шлюзу, щоб запобігти побічним витокам.
  4. Автоматичний **Circuit Breaker / Degraded Mode**: якщо Python-retrieval падає чи перевищує таймаут, Java-шлюз повертає структурований degraded-відгук (`degraded: true`), не зупиняючи мікросервіс.
  5. **Автоматизована перевірка:** ізоляція тенантів підтверджена на 8 автоматизованих атакових сценаріях у CI.
* **Тести запитів у стилі ін'єкцій (`PromptInjectionIT`, 24 кейси):** 11 запитів у стилі ін'єкцій (перевизначення системного промпту, міжтенантна розвідка, втеча з роздільників, DAN, ескалація ролі, markdown-ексфільтрація, непряма ін'єкція, SQL-стиль, стирання інструкцій, підміна JSON, base64) проганяються через реальний шлюз і перевіряються за трьома властивостями контролю доступу: (1) whitelist документів, надісланий у retrieval, дорівнює ACL принципала незалежно від запиту; (2) якщо ошуканий retrieval повертає документи іншого тенанта, шлюз відповідає 403 і не витікає вміст; (3) запит дослівно зберігається в audit-логу. Зайві JSON-поля не можуть розширити ACL, а порожні/завеликі (>2000 символів) запити отримують 400 (валідацію запитів додано під час цього аудиту; `@NotBlank` раніше не застосовувався). **Межі:** DocGuard є шаром контролю доступу, а не детектором ін'єкцій, і не зупиняє маніпуляцію LLM текстом усередині дозволених документів; retrieval-сервіс у цих тестах замокано; заголовки ідентичності (`X-Tenant-Id`, `X-Principal-Id`) цим сервісом не автентифікуються, тож клієнт може заявити будь-якого принципала. Попередню цифру «12/12 mitigated» з жорстко закодованого скрипта відкликано.
* **Команди відтворення:**
  ```bash
  cd work05-docguard
  python scripts/demo_offline.py
  # Живий запуск у Docker Compose:
  docker compose up -d --build
  bash scripts/reliability_demo.sh  # або PowerShell: .\scripts\reliability_demo.ps1
  ```

---

### 3. Work 01 і 04 — Applied ML: часовий бектестинг, захист від leakage та MLOps-сервінг

```
[Сирі історичні дані]
       │
       ▼ (Лише хронологічний порядок — БЕЗ витоку майбутніх даних)
[Temporal Split (Train 5.8% -> Val 11.5% -> Test 39.3%)]
       │
       ├─► [Leakage Guard: прибирає ознаку 'duration', відому лише після події]
       ├─► [Baseline: збалансована LogReg] ──► [Підбір порога за val macro-F1] ──► [Оцінка на test]
       └─► [Candidate: MLP, 5 seed]         ──► [Temperature Scaling] ──► [Bootstrap CI]
                                                                              │
                                                                              ▼
                                                         [FastAPI MLOps-сервінг (Work 04)]
                                                         * контракт event_time vs available_at
                                                         * рішення за матрицею бізнес-витрат
                                                         * моніторинг дрейфу ознак за z-score
```

* **Проблема (табличний ML на реальних даних):** наївні випадкові train/test split сильно завищують якість моделі через lookahead bias і target leakage. У бенчмарку UCI Bank Marketing наївні моделі використовують `duration` (тривалість дзвінка), яку неможливо знати до початку дзвінка.
* **ML-рішення (Work 01):**
  * **Target Leakage Guard:** суворе виключення `duration` та похідних сигналів.
  * **Часовий бектестинг:** хронологічний split, що відповідає реальному розгортанню.
  * **Керування covariate shift:** частка позитивних у train 5.8%, у validation 11.5%, а в test стрибає до 39.3%. Усі пороги (baseline=0.73, candidate=0.69) строго підібрано на validation, без переналаштування на test.
  * **Статистична строгість:** std на 5 seed на validation (0.0045) і 95% bootstrap CI різниці на test (`[-0.0085, 0.0089]`) документують чесний негативний результат: складні нейромережі не перевершують калібровані лінійні бейзлайни на табличних даних.
  * **Зрізи помилок:** автоматична категоризація на 5 архетипів помилок (`FN_borderline_high`, `FP_high_confidence` тощо) на 20 задокументованих рядках.
* **Продакшн-сервінг і MLOps (Work 04):**
  * **Часові контракти даних:** розрізнення `event_time` і `available_at` задекларовано в JSON-схемах, щоб не допускати ознак із майбутнього.
  * **Матриця бізнес-витрат:** поріг рішення виводиться з фінансових витрат ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$), а не з довільних 0.5.
  * **Продакшн-сервінг:** ендпоінти FastAPI (`/v1/predict`, `/health`, `/v1/drift`) з z-score алертами дрейфу, коли розподіл ознак відхиляється.
* **Команди відтворення:**
  ```bash
  # Офлайн-демо Work 01
  cd work01-bank-marketing && python scripts/demo_offline.py
  # Демо сервінгу та дрейфу Work 04
  cd ../work04-ml-serving && python scripts/demo_offline.py
  ```

---

### 4. Work 03 — Agent Workflow: відновлення після збоїв і Transactional Outbox

* **Проблема:** недетерміновані виклики зовнішніх інструментів (ефекти API, команди техніці, диспетчеризація логістики) можуть виконатися двічі, якщо застосунок падає чи перезапускається одразу після зовнішнього побічного ефекту, але до коміту транзакції з оновленим станом workflow.
* **Архітектура:**
  * **Idempotency Guard:** `idempotency_key` + SHA-256 хеш payload однозначно ідентифікують наміри. Дубль запиту з тим самим payload повертає кешований результат; змінений payload дає `409 Conflict`.
  * **Transactional Outbox:** зовнішні наміри зберігаються в PostgreSQL в одній ACID-транзакції з checkpoint стану workflow.
  * **Цикл відновлення:** після різкого завершення процесу `WorkflowRecovery` перевіряє записи outbox у статусі pending, звіряє ефекти зовнішнього stub і продовжує з точного checkpoint без повторного виконання зовнішніх побічних ефектів.
  * **Обсяг і матричні тести:** 30 автоматизованих сценаріїв збоїв на H2 у CI плюс той самий набір, повторно запущений на реальному PostgreSQL 16 Testcontainer (`./gradlew test -Dwork03.docker=true`; цей IT за замовчуванням пропускався і падав через невідповідність драйвера, доки не був виправлений під час цього аудиту) (`idempotency: 8`, `checkpoint_recovery: 4`, `validation_400: 7`, `outbox: 3`, `conflict_409: 4`, `domain: 4`). Перевірено в межах однієї транзакційної межі Spring Boot + PostgreSQL на одному вузлі (розподілений консенсус на кшталт Raft/Paxos не заявляється).
* **Команди відтворення:**
  ```bash
  cd work03-agent-workflow
  python scripts/demo_offline.py

  # Живий запуск із PostgreSQL (Docker):
  docker compose up -d             # 1. Запустити контейнер PostgreSQL (порт 5433)
  ./gradlew bootRun                # 2. Запустити Spring Boot (порт 8083; або .\gradlew.bat bootRun)
  # У 2-му терміналі:
  bash scripts/reliability_demo.sh # 3. Перевірити ідемпотентний повтор і 409 conflict (або .\scripts\reliability_demo.ps1)
  ```

---

### 5. Work 08 — Прогнозування попиту: багатосезонний бектестинг і ризик запасів

#### Порівняння синтетичного бенчмарку з реальним емпіричним рядом

Щоб перевірити стійкість прогнозування і на стаціонарній сезонній динаміці, і на нестаціонарних фізичних рядах датчиків, ідентичні 4-сезонні expanding-window бектести ($H=14$) виконано на двох датасетах:

| Метрика / вимір | Синтетична агросимуляція (20 рядів, 21,920 записів) | Реальний Capital Bikeshare (2 ряди, 1,456 записів) |
|---|:---:|:---:|
| **WAPE Seasonal Naive ($y_{t-7}$)** | 13.20% | **35.42% (менша похибка)** |
| **WAPE Historical 4-Week DOW MA** | 11.78% | 34.02% |
| **WAPE LightGBM Point ($P_{50}$)** | **7.83% (-40.68% похибки)** | 37.74% |
| **Змодельовані витрати на запаси, бейзлайн** | 7,308.0 од. | **33,576.2 од. (менші витрати)** |
| **Витрати LightGBM Safety Stock ($P_{83.3}$)** | **4,160.9 од. (-43.06% витрат)** | 51,629.5 од. |
| **Сире покриття 80% інтервалу $[P_{10}, P_{90}]$** | 75.90% | 26.79% |
| **Каліброване конформне покриття (CQR)** | **84.11%** (спостережено $\ge 80\%$ у всіх 4 вікнах) | **75.89%** (+49.10 в.п.) |
| **Рішення для продакшну** | **Розгорнути LightGBM + CQR-калібрування** | **Розгорнути сезонний бейзлайн у продакшні** |

#### Вибір продакшн-бейзлайну: чому на реальних даних обрано простий бейзлайн
> **Інженерний компроміс:** коли ML-моделі-кандидати порівнюють із доменними бейзлайнами на реальних даних, структурні зсуви розподілу часто домінують над дисперсією моделі. На бенчмарку Capital Bikeshare 2011–2012 (швидке розширення парку й станцій майже подвоїло денні обсяги без ковʼаріат потужності) наш 4-сезонний бектест показав, що сезонний бейзлайн без навчання **переміг LightGBM** і за точністю прогнозу (**35.42% проти 37.74% WAPE**), і за змодельованими витратами на запаси (**33,576 проти 51,630 од.**).
>
> **Вибір для продакшну:** за цими результатами для Capital Bikeshare обираємо сезонний бейзлайн. Розгортати складний GBDT-регресор невиправдано, коли простіша евристика дає меншу похибку, нульові витрати на пайплайн навчання і нульову вразливість до дрейфу моделі.
>
> **Покриття інтервалів прогнозу та межі:** на синтетичних агро-даних Split Conformal Quantile Regression (CQR) досягла **спостережуваного емпіричного покриття $\ge 80.0\%$ у чотирьох тестових вікнах** (весна: 80.4%, літо: 89.3%, осінь: 85.0%, зима: 81.8%; середнє 84.11% проти 75.90% некаліброваного). На реальних даних Bikeshare CQR підняла покриття з 26.79% до 75.89% (+49.10 в.п.), але не досягла номінальних 80%, бо швидке фізичне розширення порушило припущення exchangeability між 56-денним вікном калібрування і тестовим горизонтом.

* **Команди відтворення:**
  ```bash
  cd work08-demand-forecasting
  python scripts/demo_offline.py
  python scripts/eval_real_benchmark.py
  ```

---

## Матриця відтворюваності з чистого клону

Кожен проєкт можна оцінити двома способами:
1. **Офлайн-режим (< 30 секунд):** оцінює моделі, маніфести та моки без запуску Docker-демонів.
2. **Повний живий кластер:** піднімає весь стек у Docker Compose і виконує живі HTTP-запити до мікросервісів.

```bash
# 1. Клонувати репозиторій
git clone https://github.com/alexbohachev/portfolio-interview.git
cd portfolio-interview

# 2. Запустити офлайн-валідацію всіх проєктів
# Linux / macOS / Windows PowerShell:
python -m pytest work01-bank-marketing/tests work04-ml-serving/tests work08-demand-forecasting/tests
# Або через PowerShell smoke-скрипт:
powershell -ExecutionPolicy Bypass -File scripts/portfolio_smoke.ps1

# 3. Запустити живу Docker-валідацію для Work 05 і Work 07
cd work07-ai-platform && docker compose up -d --build
cd ../work05-docguard && docker compose up -d --build
```

---

## Каталог проєктів і підсумок архітектури

### Основні еталонні проєкти (7 робіт)

| № | Каталог | Предметна область та архітектура | Ключові технології | Швидка перевірка |
|---|---|---|---|---|
| **08** | [`work08-demand-forecasting/`](work08-demand-forecasting/) | Прогнозування попиту на багатьох рядах, 4-сезонний бектестинг, ризик запасів Newsvendor | LightGBM, FastAPI, Conformal Prediction | `python scripts/demo_offline.py` · [`REPORT.md`](work08-demand-forecasting/REPORT.md) |
| **07** | [`work07-ai-platform/`](work07-ai-platform/) | Бенчмарк N+1 між мікросервісами, гібридний RRF-пошук, трасування OpenTelemetry/Jaeger | Java 21, Python, Kafka, Elasticsearch, Jaeger | `python scripts/demo_offline.py` · [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) |
| **05** | [`work05-docguard/`](work05-docguard/) | Мультитенантна безпека, pre-LLM ACL-шлюз, degraded circuit breaker | Java 21, FastAPI, Docker Compose | `python scripts/demo_offline.py` · [`REPORT.md`](work05-docguard/REPORT.md) |
| **01** | [`work01-bank-marketing/`](work01-bank-marketing/) | Таблична ML-класифікація, усунення target leakage, оптимізація витрат | LightGBM, scikit-learn, Python 3.13 | `python scripts/demo_offline.py` · [`REPORT.md`](work01-bank-marketing/REPORT.md) |
| **04** | [`work04-ml-serving/`](work04-ml-serving/) | ML-сервінг з низькою латентністю, схеми контрактів даних, контроль дрейфу ознак | FastAPI, scikit-learn, Pydantic | `python scripts/demo_offline.py` · [`REPORT.md`](work04-ml-serving/REPORT.md) |
| **02** | [`work02-rag-citations/`](work02-rag-citations/) | Гібридний RRF-retrieval, екстрактивна верифікація цитат, refusal gate | SentenceTransformers, BM25, NumPy | `python scripts/demo_offline.py` · [`REPORT.md`](work02-rag-citations/REPORT.md) |
| **03** | [`work03-agent-workflow/`](work03-agent-workflow/) | Ідемпотентний оркестратор, Transactional Outbox, відновлення після збоїв | Java 21, Spring Boot, PostgreSQL | `python scripts/demo_offline.py` · [`REPORT.md`](work03-agent-workflow/REPORT.md) |

Деталі окремих проєктів та чесні межі результатів:
* **Work 02:** окремо від синтетичного корпусу (де запитання містять `doc_id`, тож Recall 1.0 і цитати 35/35 є пошуком за ID) оцінено на 123 реальних статтях uk.wikipedia (55 ручних питань): BM25 Recall@5 = 1.00 (питання лексично близькі до тексту), англомовний hybrid 0.64, мультимовний hybrid 0.80, + мультимовний cross-encoder 0.95. Деталі й обмеження: [`work02-rag-citations/README.md`](work02-rag-citations/README.md).
* **Work 04:** дані синтетичні з детермінованою міткою; `available_at` кодом не застосовується; дрейф лише демонстраційний.
* **Work 05:** це ACL-шар, а не детектор ін'єкцій; retrieval у тестах замокано; заголовки ідентичності не автентифікуються.

### Допоміжний референс

| № | Каталог | Фокус та архітектура | Ключові технології | Перевірка |
|---|---|---|---|---|
| **06** | [`work06-bible-rag/`](work06-bible-rag/) | Автономний офлайн-пошук віршів з метаданими в SQLite | FAISS, SentenceTransformers, SQLite | `pytest tests/` · [`REPORT.md`](work06-bible-rag/REPORT.md) |
