"""
    testing of HackerRankTools
"""

from VDB_API.hacker_rank_tools import HackerRankTools

tools = HackerRankTools()

# 設置到測試用的 vector database collection
tools.vectordb_manager.set_vector_db("test_db")

# 添加資料
file_paths = ["./VDB_API/docs/tt.txt", "./VDB_API/docs/tt.doc"]
ori_names = ["333.txt", "333.doc"]
tools.add_documents_to_vdb(file_paths, ori_names)

# 刪除指定文件資料
# tools.delete(["Retentive Network_A Successor to Transformer.pdf"])

# 設置線上/線下模型
tools.set_llm_type("gpt3")  # gpt3、gpt4、offline

# 設置自動執行二次搜尋
tools.set_secondary_search(True)  # default: True

# 準備所有可用文件名稱
searchableFileNameList = ["tt.doc", "tt.txt"]

# 快速問答(將搜索所有可用文件)
query = "請問小美的職業是甚麼?"
ans, _, _ = tools.chat(query, searchableFileNameList)
print("\n快速問答 : ")
print("Q : ", query)
print("A : ", ans)

# 有限定參考資料的問答
refFileNameList = ["tt.doc"]
ans, contents, metadatas = tools.chat(query, searchableFileNameList, refFileNameList)
print("\n\n有參考資料的問答 : ")
print("Q : ", query)
print("A : ", ans)
print("\n參考資料 : ")
print("contents : ", contents)
print("metadatas : ", metadatas)


# 設置不執行二次搜尋
tools.set_secondary_search(False)

# 有限定參考資料，但沒有二次搜索的問答
refFileNameList = ["tt.doc"]
ans, contents, metadatas = tools.chat(query, searchableFileNameList, refFileNameList)
print("\n\n有參考資料，但沒有二次搜索的問答 : ")
print("Q : ", query)
print("A : ", ans)
print("\n參考資料 : ")
print("contents : ", contents)
print("metadatas : ", metadatas)

# 刪除測試用的 vector database(小心使用)
tools.vectordb_manager.vectordb.delete_collection()
tools.vectordb_manager.vectordb.persist()
