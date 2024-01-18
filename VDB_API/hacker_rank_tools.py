from typing import List

from dotenv import load_dotenv
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI

from VDB_API.utils import file_processor
from VDB_API.vectordb_manager import VectordbManager

load_dotenv()  # 加載.env檔案


class HackerRankTools:
    def __init__(self):
        self.llm = OpenAI(temperature=0)
        self.template = "If the following documents are related to the question, please answer the question based on the documents:\n{context}\n\nQuestion: {question}\n\nAnswer: "
        self.prompt = PromptTemplate.from_template(self.template)
        self.vectordb_manager = VectordbManager()

    def set_llm_type(self, isOnline: bool):
        if isOnline:
            self.llm = OpenAI(temperature=0)
        else:
            print("set to offline model，待辦!")

    def add_documents_to_vdb(self, file_paths: List[str]):
        """
        Arg:
            file_paths: 文件路徑 list (需含檔名)
        """
        for file_path in file_paths:
            texts = file_processor.get_split_data(file_path)
            self.vectordb_manager.add(texts)

    # 刪除 _collection 裡的指定資料
    def delete(self, fileNameList) -> List[str]:
        """
        Arg:
            fileNameList: list of specified reference file names
        Returns:
            fileNameList: list of deleted file names
        """
        if len(fileNameList) == 1:
            where = {"source": fileNameList[0]}
        else:
            where = {"$or": [{"source": name} for name in fileNameList]}
        self.vectordb_manager.delete(where=where)
        print(f"刪除 {fileNameList} 相關資料")
        return fileNameList

    # 無任何參考資料，直接問答
    def chat(
        self, query, refFileNameList=None, refAll=False
    ) -> (str, List[str], List[dict]):
        """
        Args:
            query: user query
            refFileNameList: list of specified reference file names
            refAll: if True, ignore refFileNameList, use all reference files
        Returns:
            ans: model reply
            ref_contents: list of reference document paragraphs
            metadatas: list of reference document info
                pdf: {'source': 檔名, 'page': 頁碼}
                txt: {'source': 檔名}
        """
        if refAll:
            where = None
        elif refFileNameList is None:
            return self.llm(prompt=query), None, None
        elif len(refFileNameList) == 1:
            where = {"source": refFileNameList[0]}
        else:
            where = {"$or": [{"source": name} for name in refFileNameList]}

        # 從 vector database 取得指定文件
        contents, metadatas = self.vectordb_manager.query(
            query, n_results=3, where=where
        )
        templated_query = self.prompt.format(
            context="\n".join(contents), question=query
        )
        ans = self.llm(prompt=templated_query)

        return ans, contents, metadatas
