from typing import Tuple


def extract_latest_plugin_call(text: str) -> Tuple[str, str]:
    """
    從提供的文本中提取最近一次插件調用的名稱和參數。

    Args:
        text (str): 包含插件調用信息的文本。

    Returns:
        Tuple[str, str]: 返回一個元組，包含插件的名稱和參數。如果沒有有效的插件調用，則返回空字符串。
    """
    # 在文本中查找 'Action:', 'Action Input:', 和 'Observation:' 的最後出現位置
    action_index = text.rfind("\nAction:")
    action_input_index = text.rfind("\nAction Input:")
    observation_index = text.rfind("\nObservation:")

    # 確保 'Action' 和 'Action Input' 存在且順序正確
    if 0 <= action_index < action_input_index:
        # 如果 'Observation' 缺失，則在文本末尾補充
        if observation_index < action_input_index:
            text = text.rstrip() + "\nObservation:"
            observation_index = text.rfind("\nObservation:")

        # 從文本中提取插件名稱和參數
        plugin_name = text[action_index + len("\nAction:") : action_input_index].strip()
        plugin_args = text[
            action_input_index + len("\nAction Input:") : observation_index
        ].strip()
        return plugin_name, plugin_args

    # 如果沒有有效的插件調用，返回空字符串
    return "", ""


if __name__ == "__main__":
    # 模擬的文本，包含插件調用信息
    test_text = (
        "Question: What is the weather like today in Taiwan?\n"
        "Thought: I should use the weather API to find this information.\n"
        "Action: Search\n"
        'Action Input: query="weather in Taiwan today"\n'
        "Observation: The weather in Taiwan today is sunny.\n"
    )

    # 調用函數並打印結果
    plugin_name, plugin_args = extract_latest_plugin_call(test_text)
    print("Test Text:", test_text)
    print("Plugin Name:", plugin_name)
    print("Plugin Arguments:", plugin_args)
