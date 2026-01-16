# config/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# ===== LLM =====
UPSTAGE_MODEL = "solar-1-mini-chat"  # 예시
TEMPERATURE = 0.0

# ===== Embedding (적재 시 사용한 것과 동일해야 함) =====
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ===== Qdrant =====
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "insurance_docs"

# ===== Retriever =====
TOP_K = 10
SCORE_THRESHOLD = 0.3



# ===== Path =====
RAW_DIR = Path(
    os.getenv(
        "RAW_INSURANCE_XML_DIR",
        "/Users/kim-yein/workspace/raw_insurance_xml"
    )
)


ALLOWED_INSURANCE_TYPES = {
    "상해보험",
    "손해보험",
    "연금보험",
    "자동차보험",
    "질병보험",
    "책임보험",
    "화재보험",
}