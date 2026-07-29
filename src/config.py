from pathlib import Path

#---PATHS---
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data/raw"
VECTOR_DB_DIR = PROJECT_ROOT / "vectordb"

# ---CHUNKING---
CHUNK_SIZE = 800 #Number of characters per chunk
CHUNK_OVERLAP = 120 #~15% overlap for context retention

#---EMBEDDING---
EMBEDDING_MODEL =  "sentence-transformers/all-MiniLM-L6-v2"

#---RETRIEVAL---
TOP_K = 12    #chunks to feed into LLM

#---COLLECTION---
COLLECTION_NAME = "telecom_specs"

DISTANCE_THRESHOLD = 1.05   # above this, treat as out-of-scope