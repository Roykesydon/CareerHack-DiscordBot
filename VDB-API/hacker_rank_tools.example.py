"""
    testing of HackerRankTools
"""

from hacker_rank_tools import HackerRankTools


tools = HackerRankTools()

# 設置到測試用的 vector database
tools.vectordb_manager.set_vector_db("test_db")

# 添加資料
file_paths = ["./docs/112,訴,1085,20240110,1.pdf", "./docs/tt.txt"]
tools.add_documents_to_vdb(file_paths)

# 設置線上/線下模型
tools.set_llm_type(isOnline=True)

# 純問答
query = "這個案件涉及甚麼法條?"
ans, _, _ = tools.chat(query)
print("純問答 : ")
print("Q : ", query)
print("A : ", ans)

# 有參考資料的問答
query = "這個案件涉及甚麼法條?"
refFileNameList = ["112,訴,1085,20240110,1.pdf"]
ans, contents, metadatas = tools.chat(query, refFileNameList)
print("\n\n有參考資料的問答 : ")
print("Q : ", query)
print("A : ", ans)
print("\n參考資料 : ")
print("contents : ", contents)
print("metadatas : ", metadatas)


# 刪除測試用的 vector database(小心使用)
tools.vectordb_manager.vectordb.delete_collection()
tools.vectordb_manager.vectordb.persist()
