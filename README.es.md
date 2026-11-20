[Українська](README.md) | [English](README.en.md) | **Español**

# Monorepo de Sistemas de IA y Machine Learning Aplicado

[![CI: Clean-Clone Reproducibility](https://github.com/alexbohachev/portfolio-interview/actions/workflows/repro.yml/badge.svg)](https://github.com/alexbohachev/portfolio-interview/actions/workflows/repro.yml)
[![All GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI_Runs-blue)](https://github.com/alexbohachev/portfolio-interview/actions)
[![Demo Video (60s MP4)](https://img.shields.io/badge/Demo_Video-60s_MP4_Walkthrough-blueviolet)](https://github.com/alexbohachev/portfolio-interview/blob/main/assets/work07_demo_walkthrough.mp4)
[![Demo Script (5-7 min)](https://img.shields.io/badge/Demo_Script-5--7_min_Walkthrough-purple)](https://github.com/alexbohachev/portfolio-interview/blob/main/work07-ai-platform/DEMO_SCRIPT_5MIN.md)
[![Live Demo Runner](https://img.shields.io/badge/Live_Demo-scripts%2Flive__interview.ps1-orange)](scripts/live_interview.ps1)

Portafolio de ingeniería reproducible con **7 proyectos de referencia (+ 1 utilidad de recuperación offline)** que demuestra:
* **Plataformas de IA distribuidas (Java 21, Python 3.13, Docker, Kafka, OpenTelemetry):** caso de latencia N+1 reproducido y medido localmente (p95 231,5 ms → 46,9 ms), pasarela de seguridad zero-trust previa al LLM y recuperación con Transactional Outbox (30/30 escenarios de fallo superados).
* **Machine Learning aplicado y MLOps (PyTorch, LightGBM, FastAPI):** backtesting temporal sin fuga de datos sobre datos UCI, previsión de demanda multiserie con predicción conforme (LightGBM sobre series sintéticas; línea base Seasonal Naive elegida con datos reales de Capital Bikeshare por la navaja de Occam) y servicio de modelos en producción con monitorización de deriva de características.

> **Versión ucraniana:** [`README.md`](README.md) · **Versión inglesa:** [`README.en.md`](README.en.md) · **Guía de reproducción:** [`REPRO.md`](REPRO.md) · **Caso N+1:** [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) · **Guion de demo en vivo:** [`DEMO_SCRIPT_5MIN.md`](work07-ai-platform/DEMO_SCRIPT_5MIN.md) · **Guía standalone:** [`STANDALONE_PORTFOLIO.md`](STANDALONE_PORTFOLIO.md)

> *Nota: los READMEs de cada proyecto, los informes (`REPORT.md`) y los guiones de demo enlazados están disponibles en ucraniano e inglés. Las consultas de ejemplo en los datos están en ucraniano, tal como en el original.*

---

## Capacidades y límites operativos

Cada métrica siguiente está respaldada por suites de pruebas versionadas, arrays de mediciones en bruto versionados y pruebas automatizadas de matriz de fallos en CI:

| Dimensión | Evidencia en el monorepo | Capacidades e impacto medido | Límites operativos (alcance) |
|---|---|---|---|
| **Sistemas de IA y rendimiento** | **Work 07 (Plataforma de IA)** | Medición del antipatrón N+1 en microservicios (Java → API RAG en Python). **Latencia p95 reducida de 231,5 ms → 46,9 ms (aceleración de 4,94×; p50: 171,6 ms → 33,9 ms, 5,06×)** mediante recuperación híbrida RRF en el servidor; verificada con trazas OpenTelemetry/Jaeger y arrays de tiempos en bruto versionados. | Benchmark local con Docker Compose; no es un clúster Kubernetes geodistribuido. |
| **Seguridad de IA empresarial** | **Work 05 (DocGuard)** | Pasarela zero-trust previa al LLM (Java 21 + FastAPI). Intercepta las consultas antes de la BD vectorial o del LLM. **Aislamiento de inquilinos verificado en 8 escenarios adversarios automatizados**, registro de auditoría literal de las consultas y fallback degradado con circuit breaker. | Caché ACL en memoria con expulsión vía REST; no es un IdP empresarial externo (Ory/Keycloak). |
| **ML aplicado y backtesting** | **Work 01 (Bank Marketing)** | ML tabular empíricamente riguroso sobre datos reales de UCI. **Eliminación estricta de la fuga del objetivo** (se retiró `duration`, posterior a la llamada), división temporal cronológica bajo un fuerte covariate shift (5,8% → 39,3%), IC bootstrap al 95% que muestra que las redes neuronales no superan a las líneas base lineales calibradas. | Dataset tabular UCI; el temperature scaling por sí solo no elimina el shift sin adaptación de dominio. |
| **Previsión de demanda y riesgo** | **Work 08 (Demand Forecasting)** | Backtests rodantes de 4 temporadas ($H=14$) sobre dos benchmarks: (1) **Simulación agro sintética (20 series)**: LightGBM redujo el WAPE de 13,2% a 7,8% (-41%), la política Newsvendor recortó los costes simulados de inventario un 43% y CQR logró una cobertura observada $\ge 80{,}0\%$ (media 84,1%). (2) **Capital Bikeshare real (2011–2012)**: la línea base Seasonal Naive superó a LightGBM (35,4% vs 37,7% WAPE) y elegimos la línea base para producción. CQR elevó la cobertura empírica de 26,8% a 75,9%. | Modelo de previsión directa fijado al horizonte operativo $H=14$; la intercambiabilidad se cumple en series sintéticas pero se degrada ante la deriva por expansión física de la flota. |
| **Servicio de ML en producción y deriva** | **Work 04 (Risk Serving)** | Servicio de modelos de baja latencia con FastAPI. Umbral basado en la matriz de costes de negocio ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$), `/v1/predict` versionado y un endpoint demostrativo de deriva por z-score. | Datos sintéticos con etiqueta determinista (PR-AUC 1,0 indica una tarea trivial); las columnas `available_at` existen en el contrato de datos pero no se aplican en el código; la comprobación de deriva no tiene pruebas y no se ejecutó sobre lotes de streaming reales. |
| **Resiliencia distribuida** | **Work 03 (Agent Workflow)** | Orquestador determinista de 3 pasos con **Transactional Outbox y recuperación por checkpoint**. Superó **30/30 escenarios automatizados de inyección de fallos** sin efectos externos duplicados; devuelve HTTP 409 Conflict ante manipulación del payload. | Frontera transaccional de un solo nodo con Spring Boot y PostgreSQL; no se afirma consenso multinodo (Raft/Paxos). |
| **Ciencia de búsqueda y recuperación** | **Work 02 y 07 (RAG)** | Búsqueda híbrida RRF (Elasticsearch BM25 + kNN denso). **Prueba de estrés con 10 consultas de dominio difíciles**: 8 consultas con respuesta (Recall@5: BM25 0,125, Híbrido 0,25, Híbrido + Cross-Encoder 0,50; esta mejora NO se replicó: en el conjunto ampliado de 40 consultas los tres métodos obtienen Recall@5 = 0,05 y la mejora del re-ranker es 0,0, IC 95% [-0,075, 0,075]) + 2 consultas fuera de dominio rechazadas correctamente por la puerta de rechazo previa a la recuperación. | 200 documentos de dominio; el bi-encoder por sí solo requiere fine-tuning de dominio o re-ranking con cross-encoder para una discriminación fina. |
| **Ingeniería full stack** | **Suite del monorepo** | Java 21 (Spring Boot 3, RestClient), Python 3.13 (FastAPI, PyTorch/SentenceTransformers), Docker Compose, Kafka, Elasticsearch, Jaeger. | El CI multiplataforma verifica la suite offline (<30 s) y la suite de integración con Docker. |

---

## Casos de estudio principales

### 1. Work 07 — Plataforma de IA distribuida: antipatrón N+1 reproducido y optimización de latencia

```
[Cliente / App móvil]
       │
       ▼
[Logistics Service (Java 21)] ──(Trace: OpenTelemetry)──► [Jaeger UI :16687]
       │
       ├─► (searchSlow: N+1 llamadas por token) ──┐
       │                                          ▼
       └─► (searchFast: una sola llamada híbrida) ──► [RAG API (Python 3.13 / FastAPI)]
                                                           │
                                                           ▼
                                               [Elasticsearch 8.17 (BM25 + kNN / RRF)]
```

* **Arquitectura y contexto del benchmark:** Diseñado para medir y cuantificar un antipatrón habitual de RAG distribuido, en el que los servicios upstream descomponen las consultas del usuario en llamadas HTTP iterativas a nivel de token hacia servicios de búsqueda downstream. Implementamos esta línea base en `EquipmentSearchService.java` (`searchSlow`: viajes HTTP secuenciales por token) y la comparamos con la recuperación híbrida de una sola llamada en el servidor (`searchFast`: Reciprocal Rank Fusion en el servidor, en Elasticsearch 8.17) con Docker Compose local.
* **Corrección arquitectónica:** Se sustituyó la búsqueda iterativa por una única llamada híbrida por lotes (`searchFast()`) que solicita los top-K elementos mediante Reciprocal Rank Fusion (RRF) en el servidor de Elasticsearch.

#### Benchmark cuantitativo en ejecuciones independientes (25 muestras por perfil, Docker Compose local):

* **Ejecución 1 (línea base, 2026-11-18, Git SHA `6efad68`):**
  * perfil `slow` (N+1): p50 = **172,6 ms** | **p95 = 197,0 ms**
  * perfil `fast` (híbrido por lotes): p50 = **34,0 ms** | **p95 = 53,3 ms**
* **Ejecución 2 (verificación con clon limpio, 2026-11-19, Git SHA `45d550c`):**
  * perfil `slow` (N+1): p50 = **171,6 ms** | **p95 = 231,5 ms** | media = 179,2 ms
  * perfil `fast` (híbrido por lotes): p50 = **33,9 ms** | **p95 = 46,9 ms** | media = 37,9 ms
* **Mejora neta de rendimiento:** **aceleración de 5,06×–5,08× en p50, de 3,70× (Ejecución 1, método de percentil antiguo) y 4,94× (Ejecución 2) en p95** (~80% de reducción en p50 y p95 en la Ejecución 2).
  * *Nota metodológica:* los percentiles de la Ejecución 2 se recalculan con interpolación lineal (valor por defecto de numpy) a partir de las muestras en bruto versionadas (`work07-ai-platform/manifests/latency_raw_samples.json`). Las primeras cifras publicadas de p95 (195,7 / 46,7 ms) provenían de un percentil por índice truncado que devolvía la muestra 23 de 25 (aprox. p92) y quedan sustituidas. Con n=25 el p95 depende de las dos muestras más lentas, por lo que es orientativo; la Ejecución 1 se mantiene tal como se reportó originalmente (método antiguo, sin conservar las muestras en bruto).
* **Evidencia en bruto versionada:**
  * Arrays de tiempos en bruto (las 25 muestras por perfil): [`work07-ai-platform/manifests/latency_raw_samples.json`](work07-ai-platform/manifests/latency_raw_samples.json)
  * Métricas resumen: [`work07-ai-platform/manifests/latency_before_after.json`](work07-ai-platform/manifests/latency_before_after.json)

#### Prueba de estrés de recuperación difícil: re-ranking de 2.ª etapa con Cross-Encoder (mejora no replicada)

Las pruebas sintéticas estándar dan un trivial `Recall@5 = 1,0`. Para evaluar los límites reales de la recuperación, hicimos una prueba de estrés con **10 consultas de dominio difíciles** (`data/golden/hard_retrieval.json`, acotado a los 200 documentos compartidos con el Work 02): **8 consultas con respuesta** (evalúan Recall@5 y MRR@5 en paráfrasis y consultas multi-hop) más **2 consultas fuera de dominio sin respuesta** (evalúan la puerta de rechazo previa a la recuperación).

Para eliminar los errores de agrupación temática del bi-encoder, añadimos un **re-ranker Cross-Encoder de 2.ª etapa** (`cross-encoder/ms-marco-MiniLM-L-6-v2`) que puntúa los 25 pares candidatos híbridos principales $(q, d_i)$:

* **Ablación cuantitativa por etapas de recuperación (8 consultas con respuesta):**
  * **Línea base BM25:** Recall@5 = **0,1250** (1/8) | MRR@5 = **0,0625** | IC bootstrap 95%: `[0,000, 0,375]`
  * **1.ª etapa híbrida (RRF):** Recall@5 = **0,2500** (2/8) | MRR@5 = **0,0938** | IC bootstrap 95%: `[0,000, 0,625]`
  * **2.ª etapa Cross-Encoder:** Recall@5 = **0,5000** (4/8) | MRR@5 = **0,1771** | IC bootstrap 95%: `[0,125, 0,875]`
  * **Mejora neta del reranker sobre el híbrido:** $\Delta = +0{,}2500$ Recall@5 (2/8 → 4/8) | IC bootstrap 95%: `[0,000, 0,625]`. **Esto no se replicó en el conjunto ampliado de 40 consultas (`hard_retrieval_extended.json`, `manifests/hard_extended_eval_snapshot.json`): Recall@5 = 0,05 para BM25, Híbrido y Cross-Encoder por igual, mejora 0,0, IC 95% `[-0,075, 0,075]`; el resultado de 8 consultas debe leerse como ruido.** El bajo recall absoluto refleja limitaciones de la prueba, no una prueba de que el enfoque sea débil: los 20 documentos sintéticos por tema se diferencian solo por una palabra clave y un año, de modo que una paráfrasis no puede identificar un único objetivo, y ambos modelos (`all-MiniLM-L6-v2`, `ms-marco-MiniLM`) son solo en inglés mientras que las consultas están en ucraniano.
* **Puerta de rechazo:** no se mide en esta evaluación offline (la puerta se ejecuta en `rag-api` y requiere Docker); las cifras anteriores «2/2» y «10/10» provenían de un contador fijo en el código y se han retirado.
* **Los modelos multilingües cambian el panorama** (`paraphrase-multilingual-MiniLM-L12-v2` + `mmarco-mMiniLMv2`, `manifests/hard_extended_eval_snapshot_multilingual.json`): en las mismas 40 consultas el cross-encoder alcanza Recall@5 = 0,20 frente a 0,05 del Híbrido (mejora +0,15, IC 95% `[0,025, 0,275]`, excluye el cero), y el Hit@5 a nivel de tema sube de 0,575 (Híbrido) a 0,750, por lo que parte del problema eran los modelos solo en inglés. Salvedad: una única ejecución sobre un corpus sintético en el que los documentos de un tema son casi idénticos (elegir al azar dentro de un tema conocido da ~0,25 de Recall@5), así que los valores absolutos dicen poco sobre la calidad con datos reales. El Hit@5 a nivel de tema es reproducible con `scripts/topic_level_recall.py`.

| ID y pregunta de la consulta | Documento objetivo | BM25 Hit@5 | Híbrido (RRF) Hit@5 | Cross-Encoder Hit@5 | Diagnóstico y mecanismo |
|---|---|:---:|:---:|:---:|---|
| **`hard_001`** (paráfrasis sobre enfermedades del trigo)<br>«Які хвороби пшениці згадують буру іржа та фузаріоз?» | `agri_016_wheat_disease_15` | ❌ (fallo) | ❌ (fallo) | **✅ (Rango 3)** | **Victoria del Cross-Encoder:** el bi-encoder situó el documento agrupado en el rango 11; la atención cruzada entre la pregunta y el texto del párrafo subió el objetivo al top-3. |
| **`hard_004`** (dosis de siembra de girasol)<br>«Яка щільність посіву насіння для соняшнику?» | `agri_159_seed_rate_18` | ❌ (fallo) | ❌ (fallo) | **✅ (Rango 3)** | **Victoria del Cross-Encoder:** el bi-encoder denso asoció documentos de manejo integrado de plagas con vocabulario similar; el Cross-Encoder priorizó las métricas concretas de densidad de siembra. |
| **`hard_007`** (riesgos de enfermedades multi-hop)<br>«Порівняти ризики хвороб пшениці в різних сезонах» | `agri_015_wheat_disease_14` | ❌ (fallo) | ❌ (fallo) | **✅ (Rango 4)** | **Victoria del Cross-Encoder:** recuperó con éxito el objetivo multi-hop de riesgo entre temporadas. |
| **`hard_010`** (materia orgánica y humus)<br>«Органіка та сидерати для підвищення гумусу» | `agri_099_organic_matter_18` | ❌ (fallo) | **✅ (Rango 3)** | **✅ (Rango 2)** | **Victoria de Híbrido + CE:** generalización semántica entre abonos verdes y enriquecimiento orgánico del suelo. |
| **`hard_006`** (fórmula exacta)<br>«Дози азоту фосфору в NPK для поля» | `agri_062_npk_fertilizer_1` | ❌ (fallo) | ❌ (fallo) | ❌ (fallo) | **Caso difícil:** la coincidencia exacta de la fórmula requiere ampliar el diccionario de dominio. |
| **`hard_008`, `009`** (fuera de dominio)<br>«Чи вирощують рис на Марсі...» | *Ninguno (sin respuesta)* | n/a | n/a | n/a | La puerta de rechazo no se mide en la evaluación offline (se ejecuta en rag-api y requiere Docker). |

*Artefactos en bruto versionados: [`work07-ai-platform/manifests/eval_per_query.json`](work07-ai-platform/manifests/eval_per_query.json) y [`work07-ai-platform/manifests/hard_eval_snapshot.json`](work07-ai-platform/manifests/hard_eval_snapshot.json).*

* **Comandos de reproducción:**
  ```bash
  cd work07-ai-platform
  # Validación offline con Cross-Encoder (sin Docker, ~25 s):
  python scripts/eval_retrieval_offline.py
  # Validación en clúster Docker en vivo:
  docker compose up -d --build
  python scripts/benchmark_latency.py
  python scripts/eval_retrieval.py --golden-file data/golden/hard_retrieval.json --doc-id-prefix agri_
  ```
  *(Windows PowerShell: `.\make.ps1 build; .\make.ps1 up; py -3.13 scripts/benchmark_latency.py; .\make.ps1 eval-hard`)*

---

### 2. Work 05 — DocGuard: pasarela de seguridad zero-trust antes del LLM

```
[Petición del usuario (tenant_a, alice)]
       │
       ▼
[DocGuard Gateway (Java 21 / Spring)] ──► [Motor ACL (RBAC por principal e inquilino)]
       │ (Impone los doc_ids permitidos)
       ▼
[Servicio de recuperación (Python / FastAPI)] ──► [Base de conocimiento filtrada]
       │
       ▼ (Devuelve solo fragmentos autorizados)
[Audit Logger (consulta literal + captura de prompt injection)]
```

* **El problema:** Las arquitecturas RAG filtran con frecuencia datos empresariales privados cuando documentos de varios inquilinos comparten bases de datos vectoriales, o cuando los atacantes usan prompt injection para anular los prompts de sistema del LLM.
* **La arquitectura:** DocGuard intercepta las consultas **antes** de que lleguen a cualquier modelo o almacén vectorial.
  1. Resuelve la asignación ACL de inquilino y principal a una lista blanca de `doc_id` autorizados.
  2. Inyecta el filtro de seguridad directamente en el payload de recuperación (`allowedDocIds`).
  3. Valida los documentos devueltos en la salida de la pasarela para evitar fugas por canales laterales.
  4. **Circuit Breaker / modo degradado** automático: si la recuperación en Python falla o expira, la pasarela Java devuelve un fallback degradado estructurado (`degraded: true`) sin tumbar el microservicio.
  5. **Verificación automatizada:** aislamiento de inquilinos verificado en 8 escenarios adversarios automatizados en CI.
* **Pruebas de consultas de tipo inyección (`PromptInjectionIT`, 24 casos):** 11 consultas de tipo inyección (anulación del prompt de sistema, sondeo entre inquilinos, escape de delimitadores, DAN, escalada de rol, exfiltración por markdown, inyección indirecta, estilo SQL, borrado de instrucciones, manipulación de JSON, base64) se ejecutan cada una a través de la pasarela real y se verifican tres propiedades de control de acceso: (1) la lista blanca de documentos enviada a la recuperación coincide con la ACL del principal digan lo que digan las consultas; (2) si una recuperación engañada devuelve documentos de otro inquilino, la pasarela responde 403 y no filtra contenido; (3) la consulta se guarda literalmente en el registro de auditoría. Los campos JSON adicionales no pueden ampliar la ACL, y las consultas vacías o demasiado largas (>2000 caracteres) reciben 400 (la validación de peticiones se añadió durante esta auditoría; `@NotBlank` no se estaba aplicando). **Límites:** DocGuard es una capa de control de acceso, no un detector de inyecciones, y no impide que se manipule a un LLM mediante texto dentro de documentos permitidos; el servicio de recuperación está simulado en estas pruebas; las cabeceras de identidad (`X-Tenant-Id`, `X-Principal-Id`) no están autenticadas por este servicio, así que un cliente puede declarar cualquier principal. Una cifra anterior de «12/12 mitigados», procedente de un script con valores fijos, se retiró.
* **Comandos de reproducción:**
  ```bash
  cd work05-docguard
  python scripts/demo_offline.py
  # En vivo con Docker Compose:
  docker compose up -d --build
  bash scripts/reliability_demo.sh  # o PowerShell: .\scripts\reliability_demo.ps1
  ```

---

### 3. Work 01 y 04 — Línea de ML aplicado: backtesting temporal, prevención de fugas y MLOps

```
[Datos históricos en bruto]
       │
       ▼ (Solo orden cronológico — SIN fuga de datos futuros)
[División temporal (Train 5,8% -> Val 11,5% -> Test 39,3%)]
       │
       ├─► [Leakage Guard: elimina la característica posterior al evento 'duration']
       ├─► [Línea base: LogReg balanceada] ──► [Ajuste de macro-F1 en val] ──► [Evaluación en test]
       └─► [Candidato: MLP 5 semillas]     ──► [Temperature Scaling] ──► [IC bootstrap]
                                                                            │
                                                                            ▼
                                                       [Servicio MLOps con FastAPI (Work 04)]
                                                       * contrato event_time vs available_at
                                                       * Decisión con matriz de costes de negocio
                                                       * Monitorización de deriva por z-score
```

* **El problema (ML tabular del mundo real):** Las divisiones aleatorias ingenuas de train/test sobreestiman gravemente el rendimiento del modelo por sesgo de anticipación (lookahead) y fuga del objetivo. En el benchmark UCI Bank Marketing, los modelos ingenuos incorporan `duration` (duración de la llamada), que es imposible conocer antes de iniciar la llamada.
* **La solución de ML (Work 01):**
  * **Target Leakage Guard:** eliminación estricta de `duration` y de las señales derivadas.
  * **Backtesting temporal:** división cronológica que refleja un despliegue operativo real.
  * **Gestión del covariate shift:** la tasa positiva es 5,8% en train, 11,5% en validación y salta a 39,3% en test. Todos los umbrales (línea base=0,73, candidato=0,69) se ajustaron estrictamente en validación, evitando el sobreajuste al conjunto de test.
  * **Rigor estadístico:** desviación estándar de validación con 5 semillas (0,0045) e intervalo de confianza bootstrap al 95% sobre el delta en test (`[-0,0085, 0,0089]`), que documenta un resultado negativo honesto: las redes neuronales complejas no superan a las líneas base lineales calibradas en datos tabulares.
  * **Segmentos de error:** categorización automática en 5 arquetipos de error (`FN_borderline_high`, `FP_high_confidence`, etc.) sobre 20 filas documentadas.
* **Servicio en producción y MLOps (Work 04):**
  * **Contratos de datos temporales:** la distinción `event_time` vs `available_at` se impone en los esquemas JSON para garantizar que no se ingieran características del futuro.
  * **Matriz de costes de negocio:** el umbral de decisión se deriva de costes financieros ($C_{FN}$ vs $C_{FP}$ vs $C_{review}$) y no de una probabilidad arbitraria de 0,5.
  * **Servicio en producción:** endpoints FastAPI (`/v1/predict`, `/health`, `/v1/drift`) con alertas de deriva por z-score en vivo cuando las distribuciones de características se desvían.
* **Comandos de reproducción:**
  ```bash
  # Demo offline del Work 01
  cd work01-bank-marketing && python scripts/demo_offline.py
  # Demo de servicio y deriva del Work 04
  cd ../work04-ml-serving && python scripts/demo_offline.py
  ```

---

### 4. Work 03 — Agent Workflow: recuperación ante caídas y Transactional Outbox

* **El problema:** Las llamadas no deterministas a herramientas externas (efectos de API, comandos de maquinaria, despacho logístico) pueden ejecutarse dos veces si la aplicación se cae o se reinicia justo después de emitir un efecto secundario externo pero antes de que la transacción de base de datos confirme el estado actualizado del flujo.
* **La arquitectura:**
  * **Idempotency Guard:** `idempotency_key` + hash SHA-256 del payload identifican de forma única las intenciones. Una petición duplicada con el mismo payload devuelve el resultado en caché; un payload alterado provoca `409 Conflict`.
  * **Transactional Outbox:** las intenciones externas se almacenan en PostgreSQL dentro de la misma transacción ACID que el checkpoint del estado del flujo.
  * **Bucle de recuperación:** tras un reinicio por finalización abrupta del proceso, `WorkflowRecovery` inspecciona las entradas pendientes del outbox, verifica los efectos externos simulados y reanuda desde el checkpoint exacto sin volver a ejecutar efectos secundarios externos.
  * **Alcance y pruebas de matriz:** 30 escenarios de fallo automatizados sobre H2 en CI, más la misma suite re-ejecutada sobre un Testcontainer real de PostgreSQL 16 (`./gradlew test -Dwork03.docker=true`; este IT se omitía por defecto y fallaba por una incompatibilidad de driver hasta que se corrigió en esta auditoría) (`idempotency: 8`, `checkpoint_recovery: 4`, `validation_400: 7`, `outbox: 3`, `conflict_409: 4`, `domain: 4`). Probado dentro de una frontera transaccional de un solo nodo con Spring Boot + PostgreSQL (no se afirma consenso distribuido como Raft/Paxos).
* **Comandos de reproducción:**
  ```bash
  cd work03-agent-workflow
  python scripts/demo_offline.py

  # En vivo con PostgreSQL (Docker):
  docker compose up -d             # 1. Iniciar el contenedor de PostgreSQL (puerto 5433)
  ./gradlew bootRun                # 2. Arrancar el servicio Spring Boot (puerto 8083; o .\gradlew.bat bootRun)
  # En una 2.ª terminal:
  bash scripts/reliability_demo.sh # 3. Probar reintento idempotente y conflicto 409 (o .\scripts\reliability_demo.ps1)
  ```

---

### 5. Work 08 — Previsión de demanda: backtesting multiestacional y riesgo de inventario

#### Evaluación comparativa: benchmark sintético vs series empíricas reales

Para poner a prueba la robustez de la previsión tanto en dinámicas estacionales estacionarias como en series de sensores físicos no estacionarias, evaluamos pipelines idénticos de backtesting con ventana expansiva de 4 temporadas ($H=14$) sobre dos datasets:

| Métrica / Dimensión | Simulación agro sintética (20 series, 21.920 registros) | Capital Bikeshare real (2 series, 1.456 registros) |
|---|:---:|:---:|
| **WAPE Seasonal Naive ($y_{t-7}$)** | 13,20% | **35,42% (menor error)** |
| **WAPE media móvil de 4 semanas por día de la semana** | 11,78% | 34,02% |
| **WAPE puntual de LightGBM ($P_{50}$)** | **7,83% (-40,68% de error)** | 37,74% |
| **Coste de inventario simulado de la línea base** | 7.308,0 unidades | **33.576,2 unidades (menor coste)** |
| **Coste con stock de seguridad de LightGBM ($P_{83,3}$)** | **4.160,9 unidades (-43,06% de coste)** | 51.629,5 unidades |
| **Cobertura bruta del intervalo al 80% $[P_{10}, P_{90}]$** | 75,90% | 26,79% |
| **Cobertura conforme calibrada (CQR)** | **84,11%** (observada $\ge 80\%$ en las 4 ventanas) | **75,89%** (mejora de +49,10 p.p.) |
| **Decisión de producción** | **Desplegar LightGBM + calibración CQR** | **Desplegar la línea base estacional en producción** |

#### Selección de la línea base en producción: por qué elegimos la línea base simple con datos reales
> **Compromiso de ingeniería:** Al evaluar modelos candidatos de machine learning frente a líneas base del dominio con datos reales, los cambios estructurales de distribución suelen dominar la varianza del modelo. En el benchmark Capital Bikeshare 2011–2012 (donde la rápida expansión de flota y estaciones casi duplicó el volumen diario sin covariables de capacidad), nuestro backtest de 4 temporadas mostró que la **línea base Seasonal Naive, sin entrenamiento, superó a LightGBM** tanto en precisión de previsión (**35,42% vs 37,74% WAPE**) como en costes simulados de inventario (**33.576 vs 51.630 unidades**).
>
> **Decisión de producción:** Con base en estos resultados del backtest, elegimos la línea base estacional para Capital Bikeshare en producción. Desplegar un regresor GBDT complejo no está justificado cuando una heurística más simple ofrece menor error, cero sobrecarga de pipeline de entrenamiento y cero vulnerabilidad a la deriva del modelo.
>
> **Cobertura de intervalos de predicción y límites:** Con datos agro sintéticos, Split Conformal Quantile Regression (CQR) logró una **cobertura empírica observada $\ge 80{,}0\%$ en cuatro ventanas de test** (primavera: 80,4%, verano: 89,3%, otoño: 85,0%, invierno: 81,8%; media 84,11% vs 75,90% sin calibrar). Con datos reales de Bikeshare, CQR mejoró la cobertura de 26,79% a 75,89% (+49,10 p.p.), pero no alcanzó el objetivo nominal del 80% porque la rápida expansión física violó el supuesto de intercambiabilidad entre la ventana de calibración de 56 días y el horizonte de test.

* **Comandos de reproducción:**
  ```bash
  cd work08-demand-forecasting
  python scripts/demo_offline.py
  python scripts/eval_real_benchmark.py
  ```

---

## Matriz de reproducibilidad con clon limpio

Cada proyecto puede evaluarse de dos maneras:
1. **Modo offline (< 30 segundos):** evalúa modelos, manifiestos y escenarios simulados sin ejecutar daemons de Docker.
2. **Modo de clúster completo en vivo:** levanta el stack completo en Docker Compose y ejecuta peticiones HTTP reales contra los microservicios.

```bash
# 1. Clonar el repositorio
git clone https://github.com/alexbohachev/portfolio-interview.git
cd portfolio-interview

# 2. Ejecutar la validación offline de todos los proyectos
# Linux / macOS / Windows PowerShell:
python -m pytest work01-bank-marketing/tests work04-ml-serving/tests work08-demand-forecasting/tests
# O mediante el script smoke de PowerShell:
powershell -ExecutionPolicy Bypass -File scripts/portfolio_smoke.ps1

# 3. Ejecutar la validación en vivo con Docker de los Work 05 y 07
cd work07-ai-platform && docker compose up -d --build
cd ../work05-docguard && docker compose up -d --build
```

---

## Directorio de proyectos y resumen de arquitectura

### Proyectos de referencia principales (7 Works)

| # | Directorio del proyecto | Enfoque de dominio y arquitectura | Tecnologías clave | Verificación rápida |
|---|---|---|---|---|
| **08** | [`work08-demand-forecasting/`](work08-demand-forecasting/README.en.md) | Previsión de demanda multiserie, backtesting de 4 temporadas, riesgo de inventario Newsvendor | LightGBM, FastAPI, Conformal Prediction | `python scripts/demo_offline.py` · [`REPORT.md`](work08-demand-forecasting/REPORT.md) |
| **07** | [`work07-ai-platform/`](work07-ai-platform/README.en.md) | Benchmark N+1 en microservicios, búsqueda híbrida RRF, trazabilidad con OpenTelemetry/Jaeger | Java 21, Python, Kafka, Elasticsearch, Jaeger | `python scripts/demo_offline.py` · [`CASE_N1_PERF.md`](work07-ai-platform/CASE_N1_PERF.md) |
| **05** | [`work05-docguard/`](work05-docguard/README.en.md) | Seguridad multiinquilino, pasarela ACL previa al LLM, circuit breaker degradado | Java 21, FastAPI, Docker Compose | `python scripts/demo_offline.py` · [`REPORT.md`](work05-docguard/REPORT.md) |
| **01** | [`work01-bank-marketing/`](work01-bank-marketing/README.en.md) | Clasificación tabular con ML, eliminación de fuga del objetivo, optimización de costes | LightGBM, scikit-learn, Python 3.13 | `python scripts/demo_offline.py` · [`REPORT.md`](work01-bank-marketing/REPORT.md) |
| **04** | [`work04-ml-serving/`](work04-ml-serving/README.en.md) | Servicio de ML de baja latencia, contratos de datos por esquema, guardia de deriva de características | FastAPI, scikit-learn, Pydantic | `python scripts/demo_offline.py` · [`REPORT.md`](work04-ml-serving/REPORT.md) |
| **02** | [`work02-rag-citations/`](work02-rag-citations/README.en.md) | Recuperación híbrida RRF, verificación extractiva de citas, puerta de rechazo | SentenceTransformers, BM25, NumPy | `python scripts/demo_offline.py` · [`REPORT.md`](work02-rag-citations/REPORT.md) |
| **03** | [`work03-agent-workflow/`](work03-agent-workflow/README.en.md) | Orquestador idempotente, Transactional Outbox, recuperación ante caídas | Java 21, Spring Boot, PostgreSQL | `python scripts/demo_offline.py` · [`REPORT.md`](work03-agent-workflow/REPORT.md) |

### Utilidad de referencia auxiliar

| # | Directorio del proyecto | Enfoque y arquitectura | Tecnologías clave | Verificación |
|---|---|---|---|---|
| **06** | [`work06-bible-rag/`](work06-bible-rag/README.en.md) | Recuperación offline independiente de versículos con metadatos en SQLite | FAISS, SentenceTransformers, SQLite | `pytest tests/` · [`REPORT.md`](work06-bible-rag/REPORT.md) |
