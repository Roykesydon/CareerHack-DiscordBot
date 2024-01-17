import chromadb
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

from config import CONFIG


class LangchainManager:
    _emb_fn = SentenceTransformerEmbeddings(
        model_name=CONFIG["HuggingFace"]["model_name"]
    )
    _chroma_client = chromadb.PersistentClient(
        path=CONFIG["db_path"]
    )  # Load the Database from disk (就算 langchain_db 是空的也可以)

    def __init__(self):
        self.vectordb = Chroma(
            client=LangchainManager._chroma_client,
            embedding_function=LangchainManager._emb_fn,
            persist_directory=CONFIG["db_path"],
            collection_name=CONFIG["collections"]["basic"],
        )

    # 切換 collection，若不存在則自動創建
    def set_vector_db(self, collection_name: str):
        self.vectordb = Chroma(
            client=LangchainManager._chroma_client,
            embedding_function=LangchainManager._emb_fn,
            persist_directory=CONFIG["db_path"],
            collection_name=collection_name,
        )
        print("set collection to", collection_name)

    # 回傳所有的 collection name
    def get_collection_name_list(self) -> list[str]:
        collection_list = LangchainManager._chroma_client.list_collections()
        name_list = [collection.name for collection in collection_list]
        return name_list

    # 回傳所有 collection 的名稱
    def get_current_collection_name(self) -> str:
        return self.vectordb._collection.name

    # 儲存切割後的資料
    def add(self, texts: list[Document]) -> list[str]:
        print("adding data...")
        ids = self.vectordb.add_documents(texts)
        self.vectordb.persist()  # ensure the embeddings are written to disk
        return ids

    # 獲取指定條件的資料
    def get(self, where: dict[str]) -> list[str]:
        """Args example:
        where: {"source": "pdf-1"}
        """
        retrieved_data = self.vectordb._collection.get(where=where)
        retrieved_text = (
            retrieved_data["documents"][0]
            if len(retrieved_data["documents"]) > 0
            else []
        )
        return retrieved_text

    # 回傳與問題相關的資料
    def query(self, query, n_results=1, where=None) -> dict[str]:
        """Args example:
        where: {"source": "pdf-1"}
        """
        docs = self.vectordb.similarity_search(query, k=n_results, filter=where)
        content_list = [docs[i].page_content for i in range(len(docs))]
        return content_list

    # 刪除 _collection 裡的資料
    def delete(self, where: dict[str]):
        """Args example:
        where: {"source": "pdf-1"}
        """
        self.vectordb._collection.delete(where=where)

    # 列印當前 collection 裡的 document 數量
    def count(self) -> int:
        return self.vectordb._collection.count()
