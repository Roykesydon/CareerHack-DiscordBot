"""
    testing of HackerRankTools
"""

from VDB_API.hacker_rank_tools import HackerRankTools

tools = HackerRankTools()

# 設置到測試用的 vector database collection
tools.vectordb_manager.set_vector_db("test_db")

# 添加資料
file_paths = ["./VDB_API/docs/tt.txt", "./VDB_API/docs/tt.doc"]
tools.add_documents_to_vdb(file_paths)

# 刪除指定文件資料
# tools.delete(["Retentive Network_A Successor to Transformer.pdf"])

# 設置線上/線下模型
# tools.set_llm_type(isOnline=True)
tools.set_llm_type("gpt3")  # gpt3、gpt4、offline

# 設置是否自動執行二次搜尋
tools.set_secondary_search(True)  # default: True

# 純問答
query = "請問小美的職業是甚麼?"
# ans, _, _ = tools.chat(query)
# print("\n純問答 : ")
# print("Q : ", query)
# print("A : ", ans)

# # 有參考資料的問答
refFileNameList = ["tt.doc"]
searchableFileNameList = ["tt.doc", "tt.txt"]
ans, contents, metadatas = tools.chat(query, refFileNameList, searchableFileNameList)
print("\n\n有參考資料的問答 : ")
print("Q : ", query)
print("A : ", ans)
print("\n參考資料 : ")
print("contents : ", contents)
print("metadatas : ", metadatas)

# 刪除測試用的 vector database(小心使用)
tools.vectordb_manager.vectordb.delete_collection()
tools.vectordb_manager.vectordb.persist()
