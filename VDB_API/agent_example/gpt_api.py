from api_executor import execute_api_call
from langchain_openai import ChatOpenAI
from opencc import OpenCC
from prompt_generation import generate_planning_prompt
from tool_config import TOOLS

model = ChatOpenAI(temperature=0.1)


def llm_agent(query, model, selected_tools):
    prompt = generate_planning_prompt(selected_tools, query)  # 建立設定好的 prompt
    stop = ["Observation:", "Observation:\n"]
    response = model.invoke(prompt, temperature=0.1, stop=stop).content  # 生成 response
    while "Final Answer:" not in response:  # 若回應中出現 "Final Answer:" 則停止
        api_output = execute_api_call(
            selected_tools, response
        )  # 透過 parser 解析 response 並執行對應的 api
        api_output = str(api_output)  # 將 api 輸出轉為字串
        if "no tool founds" == api_output:
            break
        print(
            "\033[32m"
            + response
            + "\033[0m"
            + "\033[34m"
            + "Observation: "
            + api_output
            + "\033[0m"
        )
        print("-" * 20)
        prompt = (
            prompt + response + "Observation: " + api_output
        )  # 將 Api 輸出放到 observation 中，並更新 prompt
        response = model.invoke(
            prompt, temperature=0.1, stop=stop
        ).content  # 生成新的 response，直到出現 "Final Answer:"
    print("\033[32m" + response + "\033[0m" + "\033[34m")
    print("-" * 20)
    final_answer_index = response.rfind("\nFinal Answer:")
    final_answer = response[final_answer_index + len("\nFinal Answer:") :].strip()
    return final_answer


if __name__ == "__main__":
    # query = "我現在162公分，請問我的身高和台積電員工身高平均相差多少？"
    # query = '台積電一年有多少天的假期？請用繁體中文回答。'
    # query = '台積電一年有多少天的假期？'
    # query = '請根據網路訊息，請問台積電一年有多少天的假期？請用繁體中文回答。'
    # query = '請問我一年有多少天的假期？'
    query = "請問員工一年有多少天的假期？請用繁體中文回答。"
    # query = '請問台積電提供哪些產品和服務？'

    # query = '請根據網路上的資料，告訴我台積電提供哪些產品和服務？'
    # query = '台積電是什麼公司，他們主要從事什麼業務？'
    # query = '請介紹台積電這間公司？請用繁體中文回答。'
    # query = '請根據網路上的資料，介紹台積電這間公司，並以繁體中文回答。'
    # query = '台積電是半導體製造業的領先者嗎？請用繁體中文回答'
    # 他們有哪些先進製程技術？
    # query = '請問最先進的製程在哪個廠區？請用繁體中文回答。'

    response = llm_agent(query, model, TOOLS)
    print(response)
