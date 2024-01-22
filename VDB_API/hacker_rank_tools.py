from typing import Any, Dict, List, Tuple, Union

from dotenv import load_dotenv
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_openai import ChatOpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from VDB_API.utils import file_processor
from VDB_API.utils.config import (CHAT_MODELS, CONTINUE_SEARCH_WORD, DEVICE,
                                  PROMPT_TEMPLATE)
from VDB_API.vectordb_manager import VectordbManager

load_dotenv()  # 加載.env檔案


class HackerRankTools:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model_name=CHAT_MODELS["gpt3"])
        self.chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
        self.vectordb_manager = VectordbManager()
        self.secondary_search = True
        self.tokenizer = AutoTokenizer.from_pretrained(
            CHAT_MODELS["offline"], trust_remote_code=True
        )

    def set_llm_type(self, llm_type: str):
        if llm_type in CHAT_MODELS.keys():
            if llm_type == "offline":
                print("Your device: ", DEVICE)
                model = AutoModelForCausalLM.from_pretrained(
                    CHAT_MODELS["offline"]
                ).eval()
                pipe = pipeline(
                    "text-generation",
                    model=model.to(DEVICE),
                    tokenizer=self.tokenizer,
                    max_new_tokens=100,
                )
                self.llm = HuggingFacePipeline(pipeline=pipe)
            else:
                self.llm = ChatOpenAI(temperature=0, model_name=CHAT_MODELS[llm_type])
        else:
            print("Model type not found, keeping it unchanged.")

        self.chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
        print("set chat model to ", CHAT_MODELS[llm_type])

    def set_secondary_search(self, secondary_search: bool):
        self.secondary_search = secondary_search
        print("set secondary_search to ", secondary_search)

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

    # 模型問答
    def chat(
        self, query, specified_files=None, all_accessible_files=None, ref_all=False
    ) -> Tuple[str, Union[List[str], None], Union[List[dict], None]]:
        """
        Args:
            query: user query
            specified_files: list of specified reference file names
            all_accessible_files: list of all accessible file names
            ref_all: if True, ignore specified_files, use all_accessible_files
        Returns:
            ans: model reply
            contents: list of reference document paragraphs
            metadatas: list of reference document info
                pdf: {'source': 檔名, 'page': 頁碼}
                txt: {'source': 檔名}
        """
        if ref_all:
            where = self._get_filter(all_accessible_files)
        elif specified_files is None:
            if isinstance(self.llm, ChatOpenAI):
                response = self.llm.invoke(query + " 請用繁體中文回答").content
            else:
                print("是線下模型")
                response = self.llm.invoke(query)
            return response, None, None
        else:
            where = self._get_filter(specified_files)
        docs = self.vectordb_manager.query(query, n_results=3, where=where)

        contents, metadatas = [], []
        for doc in docs:
            contents.append(doc.page_content)
            metadatas.append(doc.metadata)

        templated_query = PROMPT_TEMPLATE.format(query=query)
        ans = self.chain.invoke(
            {"input_documents": docs, "question": templated_query},
            return_only_outputs=True,
        )["output_text"]
        ans = ans.split("\nSOURCES:")[0]

        # 二次搜索
        if (
            (not ref_all)
            and self.secondary_search
            and (all_accessible_files != None)
            and (CONTINUE_SEARCH_WORD in ans)
        ):
            print("\n有其他參考資料需要，進行二次搜索...")
            return self.chat(query, all_accessible_files, None, False)
        return ans, contents, metadatas

    def _get_filter(self, file_list) -> Union[Dict[str, Any], None]:
        if len(file_list) == 1:
            return {"source": file_list[0]}
        elif len(file_list) > 1:
            return {"$or": [{"source": name} for name in file_list]}
        else:
            raise ValueError("file_list is empty")
