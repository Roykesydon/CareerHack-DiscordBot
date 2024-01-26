# tool_config.py
import json

from dotenv import load_dotenv
from langchain.chains import LLMMathChain
from langchain_community.utilities import ArxivAPIWrapper, SerpAPIWrapper
from langchain_openai import OpenAI

# 加載環境變數，用於設定如API金鑰等
load_dotenv()


def search_wrapper(tool):
    """
    包裝工具的API調用。

    Args:
        tool: 一個具有 run 方法的工具實例。
    Returns:
        包裝後的函數，接受一個包含查詢字符串的JSON字串，執行工具的查詢，並返回結果。
    """

    def wrapper(query):
        query = json.loads(query)["query"]
        return tool.run(query)

    return wrapper


def tool_wrapper(tool):
    def wrapper(query):
        query = json.loads(query)["query"]
        return tool.invoke(query)

    return wrapper


# 初始化各個API工具實例
search_api = SerpAPIWrapper()
arxiv_api = ArxivAPIWrapper()
open_ai = OpenAI(temperature=0)
llm_math_chain = LLMMathChain.from_llm(open_ai, verbose=False)


TOOLS = [
    {
        "name_for_human": "response",
        "name_for_model": "DCBA_LLM",
        "description_for_model": "unless there is a specific request for an online search or for performing mathematical calculations, please always opt for the LLMChain, which is activated to provide highly accurate responses, particularly for questions pertaining to TSMC",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "default response",
                "required": True,
            }
        ],
        "tool_api": tool_wrapper(open_ai),
    },
    # google search 工具
    {
        "name_for_human": "google search",
        "name_for_model": "Search",
        "description_for_model": "This browser tool is unstable and is used for current events inquiries, activated only when there is an explicit request to go online to search for the latest or specific information, ensuring the provision of accurate and timely responses.",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "search query of google",
                "required": True,
            }
        ],
        "tool_api": search_wrapper(search_api),
    },
    # Arxiv 文獻查詢工具
    {
        "name_for_human": "arxiv",
        "name_for_model": "Arxiv",
        "description_for_model": "a wrapper for Arxiv.org, is specifically for online inquiries in Physics, Mathematics, Computer Science, and other scientific fields using Arxiv.org articles. It becomes active only upon explicit online search requests for specific scientific information, offering expert, detailed responses.",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "the document id of arxiv to search",
                "required": True,
            }
        ],
        "tool_api": search_wrapper(arxiv_api),
    },
    # 數學計算工具
    {
        "name_for_human": "math",
        "name_for_model": "LLMMathChain",
        "description_for_model": "Useful for when you need to answer questions about calculating number.",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "calculating number",
                "required": True,
            }
        ],
        "tool_api": tool_wrapper(llm_math_chain),
    },
]
