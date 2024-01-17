import os

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from vectordb_manager import VectordbManager

vectordb_manager = VectordbManager()

vectordb_manager.set_vector_db("test_db")

# 列印現有的 collection
name_list = vectordb_manager.get_collection_name_list()
for i, name in enumerate(name_list):
    print(f"collection {i+1} : {name}")

current_name = vectordb_manager.get_current_collection_name()
print("current collection : ", current_name)

# 添加資料 1
documents = ["第一筆", "第二筆", "第三筆", "第四筆"]
metadatas = [
    {"source": "pdf-1"},
    {"source": "pdf-2"},
    {"source": "pdf-2"},
    {"source": "pdf-4"},
]
texts = [
    Document(page_content=documents[i], metadata=metadatas[i])
    for i in range(len(documents))
]
vectordb_manager.add(texts)

# 添加資料 2
# file_path = "../Discord-Bot/storage/(20230217)課程_智慧工廠資訊系統.pdf"
file_path = "./docs/(20230217)課程_智慧工廠資訊系統.pdf"
file_name = os.path.basename(file_path)
loader = file_path.endswith(".pdf") and PyPDFLoader(file_path) or TextLoader(file_path)
splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
texts = loader.load_and_split(splitter)
# 修改 metadata
for text in texts:
    text.metadata["source"] = file_name
vectordb_manager.add(texts)

# 列印 collection 裡的 document 數量
count = vectordb_manager.count()
print(f"當前共有 {count} 筆資料")

# 刪除資料
vectordb_manager.delete(where={"source": "pdf-4"})
count = vectordb_manager.count()
print(f"刪除後剩下 {count} 筆資料")

# 查詢
n_results = 1
retrieved_data = vectordb_manager.query("首項目是誰?", n_results=n_results)
print(f"最相關的{n_results}筆 : {retrieved_data}")

# 指定範圍內的查詢
n_results = 1
where = {"source": "pdf-2"}
retrieved_data = vectordb_manager.query("首項目是誰?", n_results=n_results, where=where)
print(f"有範圍的最相關 {n_results} 筆 : {retrieved_data}")

# 獲取指定條件的資料
retrieved_data = vectordb_manager.get(where={"source": "pdf-1"})
print(f"指定條件取出 : {retrieved_data}")

# To cleanup, you can delete the collection(危)
vectordb_manager.vectordb.delete_collection()
vectordb_manager.vectordb.persist()
