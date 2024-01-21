# vector database settings
HUGGINGFACE_MODEL_NAME = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
DB_PATH = "./chroma_db"
COLLECTION_NAME = "basic"

# file_processor.py setting
EN_CHUNK_SIZE = 1000
EN_CHUNK_OVERLAP = 400
ZH_CHUNK_SIZE = 400
ZH_CHUNK_OVERLAP = 200