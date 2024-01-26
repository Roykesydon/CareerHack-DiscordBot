from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

from VDB_API.agent.api_executor import execute_api_call
from VDB_API.agent.prompt_generation import generate_planning_prompt
from VDB_API.utils.config import CONTINUE_SEARCH_WORD
from VDB_API.utils.file_processor import add_unique_docs

# model = ChatOpenAI(temperature=0)


def llm_agent(query, model, selected_tools):
    docs = []
    prompt = generate_planning_prompt(selected_tools, query)  # 建立設定好的 prompt
    stop = ["Observation:", "Observation:\n"]
    if isinstance(model, HuggingFacePipeline):
        response = model.invoke(prompt, stop=stop)  # 生成 response
    else:
        response = model.invoke(prompt, stop=stop).content
    for i in range(3):
        if "Final Answer:" in response:  # 若回應中出現 "Final Answer:" 則停止
            break
        api_output, tmp_docs = execute_api_call(
            selected_tools,
            response,
        )  # 透過 parser 解析 response 並執行對應的 api
        docs = add_unique_docs(docs, tmp_docs)
        api_output = str(api_output)  # 將 api 輸出轉為字串
        print(
            "\033[32m"
            + response
            + "\033[0m"
            + "\033[34m"
            + "Observation: "
            + api_output
            + "\033[0m"
        )
        if "no tool founds" == api_output:
            break
        if CONTINUE_SEARCH_WORD in api_output:
            return "抱歉我無法解決您的問題，但您可以點擊以下參考按鈕，獲得更多資訊", docs

        print("-" * 20)
        prompt = (
            prompt + response + "Observation: " + api_output
        )  # 將 Api 輸出放到 observation 中，並更新 prompt

        if isinstance(model, HuggingFacePipeline):
            response = model.invoke(
                prompt, stop=stop
            )  # 生成新的 response，直到出現 "Final Answer:"
        else:
            response = model.invoke(prompt, stop=stop).content
    else:
        prompt = prompt + response + "Thought: I now know the final answer"
        response = model.invoke(prompt).content
    print("\033[32m" + response + "\033[0m")
    print("-" * 20)
    final_answer_index = response.rfind("Final Answer:")
    additional_length = len("Final Answer:") if final_answer_index != -1 else 0
    final_answer = response[final_answer_index + additional_length :].strip()
    return final_answer, docs


# query = "我現在162公分，請問我的身高和台積電員工身高平均相差多少？"
# query = '台積電一年有多少天的假期？請用繁體中文回答。'
# query = '台積電一年有多少天的假期？'
# query = '請根據網路訊息，請問台積電一年有多少天的假期？請用繁體中文回答。'
# query = '請問我一年有多少天的假期？'
# query = "請問員工一年有多少天的假期？請用繁體中文回答。"
# query = '請問台積電提供哪些產品和服務？'

# query = '請根據網路上的資料，告訴我台積電提供哪些產品和服務？'
# query = '台積電是什麼公司，他們主要從事什麼業務？'
# query = '請介紹台積電這間公司？請用繁體中文回答。'
# query = '請根據網路上的資料，介紹台積電這間公司，並以繁體中文回答。'
# query = '台積電是半導體製造業的領先者嗎？請用繁體中文回答'
# 他們有哪些先進製程技術？
# query = '請問最先進的製程在哪個廠區？請用繁體中文回答。'
