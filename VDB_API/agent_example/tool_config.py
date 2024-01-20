# tool_config.py
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.utilities import ArxivAPIWrapper
from langchain_openai import OpenAI
from langchain.chains import LLMMathChain
from dotenv import load_dotenv
import json
from typing import Callable, Any, Dict, TypedDict, List


# 加載環境變數，用於設定如API金鑰等
load_dotenv()


def tool_wrapper_for_llm(tool: Any) -> Callable[[str], Any]:
    """
    包裝工具的API調用。

    Args:
        tool: 一個具有 run 方法的工具實例。

    Returns:
        包裝後的函數，接受一個包含查詢字符串的JSON字串，執行工具的查詢，並返回結果。
    """

    def wrapper(query: str) -> Any:
        query = json.loads(query)["query"]
        return tool.run(query)

    return wrapper


# 初始化各個API工具實例
search_api = SerpAPIWrapper()
arxiv_api = ArxivAPIWrapper()
open_ai = OpenAI(temperature=0.7)
llm_math_chain = LLMMathChain.from_llm(open_ai, verbose=False)


class ToolConfig(TypedDict):
    name_for_human: str
    name_for_model: str
    description_for_model: str
    parameters: List[Dict[str, Any]]
    tool_api: Callable[[str], Any]


TOOLS: List[ToolConfig] = [
    # google search 工具
    {
        "name_for_human": "google search",
        "name_for_model": "Search",
        "description_for_model": "useful for when you need to answer questions about current events.",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "search query of google",
                "required": True,
            }
        ],
        "tool_api": tool_wrapper_for_llm(search_api),
    },
    # Arxiv 文獻查詢工具
    {
        "name_for_human": "arxiv",
        "name_for_model": "Arxiv",
        "description_for_model": "A wrapper around Arxiv.org Useful for when you need to answer questions about Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering, and Economics from scientific articles on arxiv.org.",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "the document id of arxiv to search",
                "required": True,
            }
        ],
        "tool_api": tool_wrapper_for_llm(arxiv_api),
    },
    # 數學計算工具
    {
        "name_for_human": "math",
        "name_for_model": "LLMMathChain",
        "description_for_model": "useful for when you need to answer questions about calculating number.",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "calculating number",
                "required": True,
            }
        ],
        "tool_api": tool_wrapper_for_llm(llm_math_chain),
    },
]
