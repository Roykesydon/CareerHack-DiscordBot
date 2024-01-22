# vector database settings
HUGGINGFACE_MODEL_NAME = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
DB_PATH = "./chroma_db"
COLLECTION_NAME = "basic"

# file_processor.py setting
LANG_SEARCH_SIZE = 2000
EN_CHUNK_SIZE = 1000
EN_CHUNK_OVERLAP = 400
ZH_CHUNK_SIZE = 400
ZH_CHUNK_OVERLAP = 200

# for hacker_rank_tools.py
CHAT_MODELS = {
    "gpt3": "gpt-3.5-turbo",
    "gpt4": "gpt-4-0613",
    "offline": "bigscience/bloomz-1b1",
}
CONTINUE_SEARCH_WORD = "繼續搜尋"
PROMPT_TEMPLATE = (
    """
{query} 若參考資料中有提到需要參考其他資料，請回答「%s」，並簡單說明可能需要參考的文件；否則直接用繁體中文回答即可。
"""
    % CONTINUE_SEARCH_WORD
)

# general
import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
