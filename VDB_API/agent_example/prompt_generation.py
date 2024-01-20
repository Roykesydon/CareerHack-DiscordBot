# prompt_generation.py
import json
from typing import List, Dict, Any

# 生成工具描述的模板
TOOL_DESCRIPTION = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""

# 生成互動提示的模板
REACT_PROMPT_TEMPLATE = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {query}"""


def generate_planning_prompt(tools: List[Dict[str, Any]], user_query: str) -> str:
    """
    生成計劃提示。

    Args:
        tools (List[Dict[str, Any]]): 工具配置列表。
        user_query (str): 用戶提出的問題。

    Returns:
        str: 生成的互動提示。
    """
    tool_descriptions = []
    tool_names = []
    for tool_info in tools:
        tool_descriptions.append(
            TOOL_DESCRIPTION.format(
                name_for_model=tool_info["name_for_model"],
                name_for_human=tool_info["name_for_human"],
                description_for_model=tool_info["description_for_model"],
                parameters=json.dumps(tool_info["parameters"], ensure_ascii=False),
            )
        )
        tool_names.append(tool_info["name_for_model"])
    combined_descriptions = "\n\n".join(tool_descriptions)
    combined_tool_names = ",".join(tool_names)
    prompt = REACT_PROMPT_TEMPLATE.format(
        tool_descs=combined_descriptions,
        tool_names=combined_tool_names,
        query=user_query,
    )
    return prompt


if __name__ == "__main__":
    from tool_config import *

    print(generate_planning_prompt(TOOLS, "臺北面積大小和紐約面積大小，兩個數字相加是多少？請用繁體中文回答。"))
