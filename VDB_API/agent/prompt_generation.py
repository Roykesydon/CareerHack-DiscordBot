# prompt_generation.py
import json

from VDB_API.agent.prompt_templates import (REACT_PROMPT_TEMPLATE,
                                            TOOL_DESCRIPTION)

# from prompt_templates import (REACT_PROMPT_TEMPLATE, TOOL_DESCRIPTION)


def generate_planning_prompt(tools, user_query):
    """
    生成計劃提示。

    Args:
        tools (list): 工具配置列表。
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

    print(generate_planning_prompt(TOOLS, "台南今天天氣如何"))
