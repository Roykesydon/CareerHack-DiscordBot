from VDB_API.agent.plugin_parser import extract_latest_plugin_call


def execute_api_call(tools, response):
    """
    根據解析出的插件名稱和參數執行相應的 API。

    Args:
        tools (list): 可用工具的列表，每個工具包含名稱和對應的 API 函數。
        response (str): 包含插件調用信息的文字。

    Returns:
        str: API 執行的輸出結果，如果沒有找到對應工具則返回錯誤訊息。
    """

    # 調用 extract_latest_plugin_call 函數，獲取插件名稱和參數
    use_toolname, action_input = extract_latest_plugin_call(response)

    # 如果沒有找到對應工具，返回錯誤訊息
    if use_toolname == "":
        return "no tool founds", []

    # 在 tools 列表中查找對應的工具
    used_tool_meta = list(filter(lambda x: x["name_for_model"] == use_toolname, tools))
    if len(used_tool_meta) == 0:
        return "no tool founds", []

    # 調用工具的 API 函數，獲取輸出結果
    if use_toolname == "DCBA_LLM":
        api_output, docs = used_tool_meta[0]["tool_api"](action_input)
        return api_output, docs
    else:
        api_output = used_tool_meta[0]["tool_api"](action_input)
        return api_output, []


if __name__ == "__main__":
    from tool_config import TOOLS

    # 模擬的文本，包含插件調用信息
    test_text = (
        "Question: What is the weather like today in Taiwan?\n"
        "Thought: I should use the weather API to find this information.\n"
        "Action: Search\n"
        'Action Input: query="weather in Taiwan today"\n'
        "Observation: The weather in Taiwan today is sunny.\n"
    )

    # 調用 execute_api_call 函數，獲取 API 執行結果
    api_output = execute_api_call(TOOLS, test_text)
    print("API Output:", api_output)
