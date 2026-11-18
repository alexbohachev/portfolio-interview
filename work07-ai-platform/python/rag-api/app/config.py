import os

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX = os.getenv("ES_INDEX", "agri-knowledge")
CORPUS_DIR = os.getenv("CORPUS_DIR", "/corpus")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DIM = 384
RRF_K = int(os.getenv("RRF_K", "60"))
GATE_MIN_SCORE = float(os.getenv("GATE_MIN_SCORE", "0.02"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
REFUSAL = "Немає достатньо даних у корпусі для відповіді."