import json
from copy import deepcopy
from typing import Any, Dict, List, Tuple, Union

from dotenv import load_dotenv
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_openai import ChatOpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from VDB_API.agent.gpt_api import llm_agent
from VDB_API.agent.tool_config import TOOLS
from VDB_API.utils import file_processor
from VDB_API.utils.config import (CHAT_MODELS, CONTINUE_SEARCH_WORD, DEVICE,
                                  PROMPT_TEMPLATE)
from VDB_API.vectordb_manager import VectordbManager

load_dotenv()  # 加載.env檔案


class HackerRankTools:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model=CHAT_MODELS["gpt3"])
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
                    device=DEVICE,
                )
                self.llm = HuggingFacePipeline(pipeline=pipe)
            else:
                self.llm = ChatOpenAI(temperature=0, model=CHAT_MODELS[llm_type])
        else:
            print("Model type not found, keeping it unchanged.")

        self.chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
        print("set chat model to ", CHAT_MODELS[llm_type])

    def set_secondary_search(self, secondary_search: bool):
        self.secondary_search = secondary_search
        print("set secondary_search to ", secondary_search)

    def add_documents_to_vdb(self, file_paths: List[str], ori_file_names: List[str]):
        """
        Arg:
            file_paths: 文件路徑 list (需含檔名)
        """
        for i, file_path in enumerate(file_paths):
            texts = file_processor.get_split_data(file_path)

            for text in texts:
                text.page_content = ori_file_names[i] + "--" + text.page_content
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
    async def chat(
        self, query, all_accessible_files, specified_files=None, processing_message=None
    ) -> Tuple[str, Union[List[str], None], Union[List[dict], None]]:
        tools = deepcopy(TOOLS)
        tools[0]["tool_api"] = self._tool_wrapper(all_accessible_files, specified_files)
        ans, docs = await llm_agent(
            query, self.llm, tools, processing_message=processing_message
        )

        # 整理出需要的東西
        contents, metadatas = [], []
        for doc in docs:
            tmp_content = doc.page_content.split("--")
            tmp_content = "".join(tmp_content[1:])
            contents.append(tmp_content)
            metadatas.append(doc.metadata)
        return ans, contents, metadatas

    def _tool_wrapper(self, all_accessible_files, specified_files=None):
        def wrapper(query):
            query = json.loads(query)["query"]
            docs = []
            if specified_files is None:
                tmp_docs = self._search_vdb(query, all_accessible_files)
            else:
                tmp_docs = self._search_vdb(query, specified_files)
            docs = file_processor.add_unique_docs(docs, tmp_docs)
            ans = self._get_llm_reply(query, docs)

            # 二次搜索
            if (
                self.secondary_search
                and (specified_files != None)
                and (CONTINUE_SEARCH_WORD in ans)
            ):
                # 快速問答不應觸發到這裡
                print("\n有其他參考資料需要，進行二次搜索...")
                tmp_docs = self._search_vdb(query, all_accessible_files)
                docs = file_processor.add_unique_docs(docs, tmp_docs)
                ans = self._get_llm_reply(query, docs)

            return ans, docs

        return wrapper

    def _get_filter(self, file_list) -> Union[Dict[str, Any], None]:
        if len(file_list) == 1:
            return {"source": file_list[0]}
        elif len(file_list) > 1:
            return {"$or": [{"source": name} for name in file_list]}
        else:
            raise ValueError("file_list is empty")

    def _search_vdb(self, query, file_list):
        where = self._get_filter(file_list)
        docs = self.vectordb_manager.query(query, n_results=3, where=where)
        return docs

    def _get_llm_reply(self, query, docs):
        templated_query = PROMPT_TEMPLATE.format(query=query)
        # ans = self.chain.invoke(
        #     {"input_documents": docs, "question": templated_query},
        #     return_only_outputs=True,
        # )["output_text"]
        # ans = ans.split("\nSOURCES:")[0]
        contents = ""
        for doc in docs:
            contents += doc.page_content + "\n"
        ans = self.llm.invoke(f"[參考資料] {contents} \n" + templated_query).content

        return ans
