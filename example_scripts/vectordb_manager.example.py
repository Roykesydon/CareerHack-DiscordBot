"""
    testing of VectordbManager
"""
import os

from VDB_API.utils import file_processor
from VDB_API.vectordb_manager import VectordbManager

vectordb_manager = VectordbManager()
vectordb_manager.set_vector_db("test_db")

# 列印現有的 collection
name_list = vectordb_manager.get_collection_name_list()
for i, name in enumerate(name_list):
    print(f"collection {i+1} : {name}")

current_name = vectordb_manager.get_current_collection_name()
print("current collection : ", current_name)

# 添加資料 1 (dummy data)
# documents = ["第一筆", "第二筆", "第三筆", "第四筆"]
# metadatas = [
#     {"source": "pdf-1"},
#     {"source": "pdf-2"},
#     {"source": "pdf-2"},
#     {"source": "pdf-4"},
# ]
# texts = [
#     Document(page_content=documents[i], metadata=metadatas[i])
#     for i in range(len(documents))
# ]
# ids = vectordb_manager.add(texts)

# # 添加資料 2
file_path = "./docs/(20230217)課程_智慧工廠資訊系統.pdf"
file_name = os.path.basename(file_path)
texts = file_processor.get_split_data(file_path)
ids = vectordb_manager.add(texts)

# 列印出資料庫中資料的所有來源
print("所有來源檔案名 : ", vectordb_manager.get_all_source_name())

# 列印 collection 裡的 document 數量
count = vectordb_manager.count()
print(f"當前共有 {count} 筆資料")

# 刪除資料
# vectordb_manager.delete(where={"$or": [{"source": "pdf-1"}, {"source": "pdf-4"}]})
# count = vectordb_manager.count()
# print(f"刪除後剩下 {count} 筆資料")

# 查詢
n_results = 1
docs = vectordb_manager.query("首項目是誰?", n_results=n_results)
print(f"最相關的 {n_results} 筆 : {docs}")


# 指定範圍內的查詢
n_results = 1
where = {"source": "pdf-2"}
docs = vectordb_manager.query("首項目是誰?", n_results=n_results, where=where)
print(f"\n有範圍的最相關 {n_results} 筆 : {docs}")


# 獲取指定條件的資料
contents, metadatas = vectordb_manager.get(
    where={"$or": [{"source": "(20230217)課程_智慧工廠資訊系統.pdf"}, {"source": "pdf-4"}]}
)
print(f"\n指定條件取出內文 : {contents}")
print(f"內文資訊(metadata) : {metadatas}")

# To cleanup, you can delete the collection(危)
vectordb_manager.vectordb.delete_collection()
vectordb_manager.vectordb.persist()
