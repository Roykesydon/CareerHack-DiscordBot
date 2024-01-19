from typing import List, Tuple, Union

from dotenv import load_dotenv
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain_openai import OpenAI

from VDB_API.utils import file_processor
from VDB_API.vectordb_manager import VectordbManager

load_dotenv()  # 加載.env檔案


class HackerRankTools:
    def __init__(self):
        self.llm = OpenAI(temperature=0)
        self.chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
        self.vectordb_manager = VectordbManager()

    def set_llm_type(self, isOnline: bool):
        if isOnline:
            self.llm = OpenAI(temperature=0)
            self.chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
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
    ) -> Tuple[str, Union[List[str], None], Union[List[dict], None]]:
        """
        Args:
            query: user query
            refFileNameList: list of specified reference file names
            refAll: if True, ignore refFileNameList, use all reference files
        Returns:
            ans: model reply
            contents: list of reference document paragraphs
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
        docs = self.vectordb_manager.query(query, n_results=3, where=where)

        contents, metadatas = [], []
        for doc in docs:
            contents.append(doc.page_content)
            metadatas.append(doc.metadata)

        ans = self.chain(
            {"input_documents": docs, "question": query}, return_only_outputs=True
        )["output_text"]
        ans = ans.split("\nSOURCES:")[0]

        return ans, contents, metadatas
