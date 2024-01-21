import chromadb
import torch
from langchain.docstore.document import Document
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma

from VDB_API.utils.config import HUGGINGFACE_MODEL_NAME, DB_PATH, COLLECTION_NAME

class VectordbManager:
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("你的裝置是：", _device)
    _emb_fn = SentenceTransformerEmbeddings(
        model_name=HUGGINGFACE_MODEL_NAME, model_kwargs={"device": _device}
    )
    _chroma_client = chromadb.PersistentClient(
        path=DB_PATH
    )  # Load the Database from disk

    def __init__(self):
        self.vectordb = Chroma(
            client=VectordbManager._chroma_client,
            embedding_function=VectordbManager._emb_fn,
            persist_directory=DB_PATH,
            collection_name=COLLECTION_NAME,
            collection_metadata={"hnsw:space": "cosine"},  # l2 is the default
        )

    # 切換 collection，若不存在則自動創建
    def set_vector_db(self, collection_name):
        self.vectordb = Chroma(
            client=VectordbManager._chroma_client,
            embedding_function=VectordbManager._emb_fn,
            persist_directory=DB_PATH,
            collection_name=collection_name,
            collection_metadata={"hnsw:space": "cosine"},  # l2 is the default
        )
        print("set collection to", collection_name)

    # 回傳所有的 collection name
    def get_collection_name_list(self):
        collection_list = VectordbManager._chroma_client.list_collections()
        name_list = [collection.name for collection in collection_list]
        return name_list

    # 回傳當前使用 collection 的名稱
    def get_current_collection_name(self):
        return self.vectordb._collection.name

    # 儲存切割後的資料
    def add(self, texts):
        """
        Args:
            texts: split data from document.
                type: list[Document]
                *note: you can use file_processor.get_split_data(file_path) to get split data
        Returns:
            ids: id of each document in vector database
        """
        print("adding data...")
        ids = self.vectordb.add_documents(texts)
        self.vectordb.persist()  # ensure the embeddings are written to disk
        return ids

    # 獲取指定條件的 document (文件段落)、document information (文件資訊)
    def get(self, where):
        """
        Args example:
            where =
                (single condition)   {"source": "pdf-1"}
                (multiple condition) {"$or": [{"source": "pdf-1"}, {"source": "pdf-4"}]}
        Returns:
            contents: list of document's page_content. list[str]
            metadatas: list of document's infomation. list[dict[str]]
                [{
                    'source': 段落來源檔名(str),
                    'page': 段落所在頁碼(int) # 只有 pdf 才有
                    }, {}, ...
                ]
        """
        docs = self.vectordb._collection.get(where=where)
        if len(docs["documents"]) > 0:
            contents, metadatas = [], []
            for i, doc in enumerate(docs["documents"]):
                contents.append(doc)
                metadatas.append(docs["metadatas"][i])
            return contents, metadatas
        else:
            print("No data found")
            return [], []

    # 獲取 collection 中所有資料的來源檔名
    def get_all_source_name(self):
        all_data = self.vectordb._collection.get()
        source_name_list = [data["source"] for data in all_data["metadatas"]]
        source_name_list = list(set(source_name_list))  # Remove duplicates
        return source_name_list

    # 獲取與問題相關的 document (文件段落)、document information (文件資訊)
    def query(self, query, n_results=1, where=None):
        """
        Args example:
            where =
                (single condition)   {"source": "pdf-1"}
                (multiple condition) {"$or": [{"source": "pdf-1"}, {"source": "pdf-4"}]}
        Returns:
            docs: list of documents.
        """
        docs = self.vectordb.similarity_search(query, k=n_results, filter=where)
        return docs

    # 刪除 _collection 中指定條件的資料
    def delete(self, where):
        """
        Args example:
            where =
                (single condition)   {"source": "pdf-1"}
                (multiple condition) {"$or": [{"source": "pdf-1"}, {"source": "pdf-4"}]}
        """
        self.vectordb._collection.delete(where=where)

    # 回傳當前 collection 裡的 document 筆數
    def count(self):
        return self.vectordb._collection.count()
