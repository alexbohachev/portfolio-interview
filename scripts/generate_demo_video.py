"""Генератор демонстраційного відео MP4 для Work 07 (N+1 Latency Fix & Distributed AI Platform).
Створює відео презентації з розбором архітектури, трейсами Jaeger та результатами бенчмарку.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "work07_demo_walkthrough.mp4"

WIDTH = 1280
HEIGHT = 720
FPS = 10

FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
FONT_HEADING = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 26)
FONT_CODE = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
FONT_CODE_BOLD = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 20)
FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)

# Кольори теми
BG_COLOR = (15, 20, 28)         # Темний синій/графітовий
PANEL_BG = (22, 30, 42)         # Контейнер картки
ACCENT_BLUE = (56, 189, 248)    # Cyan / Sky
ACCENT_GREEN = (74, 222, 128)   # Green
ACCENT_RED = (248, 113, 113)    # Coral Red
ACCENT_PURPLE = (192, 132, 252) # Purple
TEXT_MAIN = (241, 245, 249)     # White-ish
TEXT_MUTED = (148, 163, 184)    # Slate Gray
BORDER_COLOR = (45, 60, 80)     # Border


def draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str, step_tag: str):
    # Фонова панель заголовка
    draw.rectangle([(30, 25), (WIDTH - 30, 95)], fill=PANEL_BG, outline=BORDER_COLOR, width=1)
    # Тег кроку
    draw.rounded_rectangle([(45, 38), (170, 78)], radius=6, fill=(38, 55, 80))
    draw.text((60, 46), step_tag, fill=ACCENT_BLUE, font=FONT_CODE_BOLD)
    # Заголовок та підзаголовок
    draw.text((190, 36), title, fill=TEXT_MAIN, font=FONT_HEADING)
    draw.text((190, 66), subtitle, fill=TEXT_MUTED, font=FONT_SMALL)


def draw_footer(draw: ImageDraw.ImageDraw, current_sec: int, total_sec: int):
    # Нижня статус-панель
    draw.rectangle([(30, HEIGHT - 45), (WIDTH - 30, HEIGHT - 15)], fill=PANEL_BG, outline=BORDER_COLOR, width=1)
    draw.text((45, HEIGHT - 38), "Repository: github.com/alexbohachev/portfolio-interview", fill=TEXT_MUTED, font=FONT_SMALL)
    progress_text = f"{current_sec // 60}:{current_sec % 60:02d} / {total_sec // 60}:{total_sec % 60:02d} | Work 07 Walkthrough"
    draw.text((WIDTH - 350, HEIGHT - 38), progress_text, fill=ACCENT_BLUE, font=FONT_SMALL)


def scene_1_intro() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Головна картка
    draw.rounded_rectangle([(100, 100), (WIDTH - 100, HEIGHT - 100)], radius=12, fill=PANEL_BG, outline=ACCENT_BLUE, width=2)
    
    # Бейдж
    draw.rounded_rectangle([(140, 140), (450, 175)], radius=6, fill=(30, 58, 100))
    draw.text((155, 145), "SENIOR AI PLATFORM / BACKEND", fill=ACCENT_BLUE, font=FONT_CODE_BOLD)
    
    # Назва
    draw.text((140, 200), "Work 07: Distributed AI Platform", fill=TEXT_MAIN, font=FONT_TITLE)
    draw.text((140, 255), "Elimination of N+1 Latency Anti-Pattern via Batch Hybrid RRF Retrieval", fill=ACCENT_GREEN, font=FONT_HEADING)
    
    # Метрики плашки
    draw.rounded_rectangle([(140, 330), (600, 450)], radius=8, fill=(18, 25, 38), outline=BORDER_COLOR, width=1)
    draw.text((160, 350), "BEFORE OPTIMIZATION (N+1 calls):", fill=ACCENT_RED, font=FONT_HEADING)
    draw.text((160, 395), "Latency p95 = 231.5 ms  |  p50 = 171.6 ms", fill=TEXT_MAIN, font=FONT_CODE_BOLD)
    
    draw.rounded_rectangle([(640, 330), (1100, 450)], radius=8, fill=(18, 25, 38), outline=ACCENT_GREEN, width=1)
    draw.text((660, 350), "AFTER ARCHITECTURAL FIX (Batch RRF):", fill=ACCENT_GREEN, font=FONT_HEADING)
    draw.text((660, 395), "Latency p95 = 46.9 ms  |  p50 = 33.9 ms", fill=ACCENT_GREEN, font=FONT_CODE_BOLD)
    draw.text((660, 420), "Speedup: 4.94x at p95  (5.06x at p50)", fill=TEXT_MAIN, font=FONT_SMALL)
    
    # Доказова база
    draw.text((140, 490), "Committed Verification Evidence:", fill=TEXT_MUTED, font=FONT_CODE_BOLD)
    draw.text((140, 520), "- Distributed traces in Jaeger (http://localhost:16687)", fill=TEXT_MAIN, font=FONT_CODE)
    draw.text((140, 545), "- Committed raw latency sample arrays (25 iterations per profile)", fill=TEXT_MAIN, font=FONT_CODE)
    draw.text((140, 570), "- Clean-clone reproduction via: .\\scripts\\live_interview.ps1 work07", fill=ACCENT_BLUE, font=FONT_CODE)
    
    return img


def scene_2_architecture() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Step 1: Microservice Topology & The N+1 Problem", "How high-throughput microservices suffer from sequential token query amplification", "STEP 01 / 04")
    
    # Картка архітектури
    draw.rounded_rectangle([(50, 115), (WIDTH - 50, HEIGHT - 65)], radius=10, fill=PANEL_BG, outline=BORDER_COLOR, width=1)
    
    code_diagram = """
  [Client / Field Mobile App]
             │
             ▼ HTTP POST /api/v1/equipment-requests
  [Logistics Service (Java 21 / Spring Boot 3)]
             │
             ├──► (BEFORE: Naive N+1 Anti-Pattern)
             │    ├── HTTP /v1/knowledge/search?q=бура        (~28 ms) ──┐
             │    ├── HTTP /v1/knowledge/search?q=іржа        (~26 ms)   │  Sequential Waterfall:
             │    ├── HTTP /v1/knowledge/search?q=озимої      (~31 ms)   ├──► 6 Network Hops
             │    ├── HTTP /v1/knowledge/search?q=пшениці     (~29 ms)   │    Total p95: 231.5 ms
             │    └── HTTP /v1/knowledge/search?q=бура+іржа.. (~38 ms) ──┘
             │                                                           │
             │                                                           ▼
             └──► [Python 3.13 FastAPI RAG API] ────────► [Elasticsearch 8.17]
                                                        (BM25 + Dense kNN)
    """
    y = 135
    for line in code_diagram.strip("\n").split("\n"):
        color = ACCENT_RED if "BEFORE:" in line or "Sequential Waterfall" in line or "231.5 ms" in line else (
            ACCENT_BLUE if "Java 21" in line or "Python" in line or "Elasticsearch" in line else TEXT_MAIN
        )
        draw.text((80, y), line, fill=color, font=FONT_CODE)
        y += 24
        
    draw.rounded_rectangle([(80, 540), (WIDTH - 80, 630)], radius=6, fill=(28, 20, 20), outline=ACCENT_RED, width=1)
    draw.text((100, 555), "JAEGER DISTRIBUTED TRACE DIAGNOSIS (http://localhost:16687):", fill=ACCENT_RED, font=FONT_CODE_BOLD)
    draw.text((100, 585), "Trace waterfall showed 6 sequential spans to /v1/knowledge/search per single equipment request.", fill=TEXT_MAIN, font=FONT_CODE)
    draw.text((100, 605), "Network serialization + TCP handshake overhead dominated, creating artificial latency spike.", fill=TEXT_MUTED, font=FONT_CODE)
    
    return img


def scene_3_fix() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Step 2: Architectural Fix — Single-Call Batch Hybrid RRF", "Replacing token loop in Java with Elasticsearch Reciprocal Rank Fusion", "STEP 02 / 04")
    
    draw.rounded_rectangle([(50, 115), (WIDTH - 50, HEIGHT - 65)], radius=10, fill=PANEL_BG, outline=BORDER_COLOR, width=1)
    
    code_diff = """
  // Logistics Service: EquipmentSearchService.java
  
  (-) BEFORE (Iterative token loop):
      for (String token : queryTokens) {
          hits.addAll(ragClient.search(token, TopK=1)); // N+1 sequential HTTP calls!
      }
      
  (+) AFTER (Batch Hybrid Request with server-side RRF fusion):
      SearchResponse response = ragClient.searchFast(
          SearchRequest.builder()
              .query(fullNaturalQuery)
              .topK(3)
              .mode(SearchMode.HYBRID) // Combines BM25 + Dense kNN via RRF
              .build()
      ); // Single HTTP Call! Total roundtrip: ~34 ms (p50) / ~47 ms (p95)
    """
    y = 135
    for line in code_diff.strip("\n").split("\n"):
        color = ACCENT_RED if "(-)" in line or "N+1 sequential" in line else (
            ACCENT_GREEN if "(+)" in line or "Single HTTP Call" in line or "searchFast" in line else TEXT_MAIN
        )
        draw.text((80, y), line, fill=color, font=FONT_CODE)
        y += 24
        
    draw.rounded_rectangle([(80, 530), (WIDTH - 80, 630)], radius=6, fill=(18, 30, 24), outline=ACCENT_GREEN, width=1)
    draw.text((100, 545), "HYBRID SEARCH SCIENCE (Reciprocal Rank Fusion in Elasticsearch 8.17):", fill=ACCENT_GREEN, font=FONT_CODE_BOLD)
    draw.text((100, 575), "Score(d) = RRF(BM25, k=60) + RRF(Dense MiniLM, k=60)", fill=ACCENT_BLUE, font=FONT_CODE)
    draw.text((100, 600), "RRF merges lexical keyword precision with dense semantic generalization in a single query.", fill=TEXT_MAIN, font=FONT_CODE)
    
    return img


def scene_4_benchmark() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Step 3: Quantitative Verification & Benchmark Results", "Real measured timings across 25 independent requests per profile (Committed raw arrays)", "STEP 03 / 04")
    
    draw.rounded_rectangle([(50, 115), (WIDTH - 50, HEIGHT - 65)], radius=10, fill=PANEL_BG, outline=BORDER_COLOR, width=1)
    
    # Таблиця метрик
    draw.text((80, 135), "LATENCY BENCHMARK MATRIX (Java Logistics -> Python RAG API -> Elasticsearch):", fill=ACCENT_BLUE, font=FONT_CODE_BOLD)
    
    table_text = """
  ┌────────────────────────┬─────────────────────┬─────────────────────┬──────────────────┐
  │ Latency Percentile     │ Slow Profile (N+1)  │ Fast Profile (Batch)│ Relative Speedup │
  ├────────────────────────┼─────────────────────┼─────────────────────┼──────────────────┤
  │ p50 (Median)           │      171.6 ms       │       33.9 ms       │  5.06x Speedup   │
  │ p90                    │      193.7 ms       │       46.6 ms       │  4.15x Speedup   │
  │ p95                    │      231.5 ms       │       46.9 ms       │  4.94x Speedup   │
  │ Mean                   │      179.2 ms       │       37.9 ms       │  4.73x Speedup   │
  │ Std Dev                │       37.6 ms       │        7.0 ms       │  5.36x Lower Var │
  └────────────────────────┴─────────────────────┴─────────────────────┴──────────────────┘
    """
    y = 165
    for line in table_text.strip("\n").split("\n"):
        color = ACCENT_GREEN if "5.06x" in line or "4.94x" in line else TEXT_MAIN
        draw.text((80, y), line, fill=color, font=FONT_CODE)
        y += 24
        
    draw.rounded_rectangle([(80, 480), (WIDTH - 80, 630)], radius=6, fill=(18, 25, 38), outline=ACCENT_BLUE, width=1)
    draw.text((100, 495), "AUDITABLE COMMITTED EVIDENCE IN MONOREPO:", fill=ACCENT_BLUE, font=FONT_CODE_BOLD)
    draw.text((100, 525), "* Summary metrics: work07-ai-platform/manifests/latency_before_after.json", fill=TEXT_MAIN, font=FONT_CODE)
    draw.text((100, 550), "* Raw sample arrays: work07-ai-platform/manifests/latency_raw_samples.json (25 samples)", fill=TEXT_MAIN, font=FONT_CODE)
    draw.text((100, 575), "* Clean-clone reproduction script: py -3.13 scripts/benchmark_latency.py", fill=TEXT_MAIN, font=FONT_CODE)
    draw.text((100, 600), "* Compose smoke test in GitHub Actions (repro workflow, job: docker-compose)", fill=ACCENT_GREEN, font=FONT_CODE)
    
    return img


def scene_5_conclusion() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Step 4: What the Retrieval Data Supports", "Real Ukrainian corpus, bootstrap CIs, and what did not replicate", "STEP 04 / 04")
    
    draw.rounded_rectangle([(50, 115), (WIDTH - 50, HEIGHT - 65)], radius=10, fill=PANEL_BG, outline=BORDER_COLOR, width=1)
    
    retrieval_text = """
  1. RETRIEVAL ON A REAL UKRAINIAN CORPUS (123 articles, 55 questions, 95% CI):
     * English-only embedder: Recall@5 0.27  |  multilingual hybrid: 0.80
     * + multilingual cross-encoder: 0.95  |  BM25 alone: 1.00 (questions are lexically close)
     -> Conclusion: model language matters; a strong BM25 baseline can win. Measure, do not assume.

  2. WHAT DID NOT REPLICATE:
     * Re-ranker lift seen on 8 hard queries (0.25 to 0.50) vanished on 40 queries (CI includes 0).
     * Refusal gate is not measured in the offline evaluation (it runs in rag-api).

  3. PLATFORM RESULT:
     * p95 231.5 ms -> 46.9 ms (-80%), local Docker Compose, n=25 per profile.
     * Jaeger OpenTelemetry traces across Java and Python services.
     * Clean-clone reproduction via PowerShell and Docker Compose.
    """
    y = 135
    for line in retrieval_text.strip("\n").split("\n"):
        color = ACCENT_PURPLE if line.strip()[:2] in ("1.", "2.", "3.") else (
            ACCENT_GREEN if "Conclusion" in line or "-80%" in line else TEXT_MAIN
        )
        draw.text((80, y), line, fill=color, font=FONT_CODE)
        y += 24
        
    draw.rounded_rectangle([(80, 550), (WIDTH - 80, 630)], radius=6, fill=(25, 35, 50), outline=ACCENT_BLUE, width=1)
    draw.text((100, 565), "HOW TO RUN LIVE ON YOUR MACHINE:", fill=ACCENT_BLUE, font=FONT_CODE_BOLD)
    draw.text((100, 595), "git clone https://github.com/alexbohachev/portfolio-interview.git ; .\\scripts\\live_interview.ps1 work07", fill=ACCENT_GREEN, font=FONT_CODE)
    
    return img


def main():
    print("=== Generating Work 07 Video Walkthrough (assets/work07_demo_walkthrough.mp4) ===")
    
    # 5 сцен:
    # Сцена 1: Intro (0-8s, 80 кадрів)
    # Сцена 2: Architecture & N+1 (8-22s, 140 кадрів)
    # Сцена 3: Architectural Fix (22-34s, 120 кадрів)
    # Сцена 4: Quantitative Benchmark (34-48s, 140 кадрів)
    # Сцена 5: Domain Retrieval & Conclusion (48-60s, 120 кадрів)
    
    scenes = [
        (scene_1_intro, 8),
        (scene_2_architecture, 14),
        (scene_3_fix, 12),
        (scene_4_benchmark, 14),
        (scene_5_conclusion, 12),
    ]
    
    total_sec = sum(sec for _, sec in scenes)
    print(f"Total video duration: {total_sec} seconds at {FPS} FPS ({total_sec * FPS} frames)")
    
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "22",
        str(OUTPUT_PATH),
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    current_sec = 0
    frame_count = 0
    
    for scene_fn, duration in scenes:
        base_img = scene_fn()
        for s in range(duration):
            sec_mark = current_sec + s
            # Клонуємо та додаємо динамічний футер
            img = base_img.copy()
            draw = ImageDraw.Draw(img)
            draw_footer(draw, sec_mark, total_sec)
            
            raw_bytes = img.tobytes()
            for _ in range(FPS):
                proc.stdin.write(raw_bytes)
                frame_count += 1
        current_sec += duration
        
    proc.stdin.close()
    _, stderr = proc.communicate()
    
    if proc.returncode != 0:
        print("FFmpeg error:", stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(proc.returncode)
        
    size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"Successfully generated video: {OUTPUT_PATH} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
