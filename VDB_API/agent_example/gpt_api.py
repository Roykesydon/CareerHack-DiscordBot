from langchain_openai import ChatOpenAI
from prompt_generation import generate_planning_prompt
from api_executor import execute_api_call
from tool_config import TOOLS
from opencc import OpenCC

    
def run_query_with_tools(query, model, selected_tools):
    prompt = generate_planning_prompt(selected_tools, query) # 建立設定好的 prompt
    stop = ["Observation:", "Observation:\n"]
    response = model.invoke(prompt, temperature=0.1, stop=stop).content # 生成 response
    
    while "Final Answer:" not in response: # 若回應中出現 "Final Answer:" 則停止
        
        api_output = execute_api_call(selected_tools, response) # 透過 parser 解析 response 並執行對應的 api
        api_output = str(api_output) # 將 api 輸出轉為字串
        if "no tool founds" == api_output:
            break
        print("\033[32m" + response + "\033[0m" + "\033[34m" + ' ' + api_output + "\033[0m")
        print('-'*20)
        prompt = prompt + response + 'Observation: ' + api_output # 將 Api 輸出放到 observation 中，並更新 prompt
        response = model.invoke(prompt, temperature=0.1, stop=stop).content # 生成新的 response，直到出現 "Final Answer:"
    print("\033[32m" + response + "\033[0m" + "\033[34m" + ' ' + api_output + "\033[0m")
    print('-'*20)   
    final_answer_index = response.rfind('\nFinal Answer:')
    final_answer = response[final_answer_index + len('\nFinal Answer:'):].strip()
    return final_answer


if __name__ == '__main__':
    model = ChatOpenAI()
    query = "臺北面積大小和紐約面積大小，兩個數字相加是多少？請用繁體中文回答。"
    response = run_query_with_tools(query, model, TOOLS)
    print(response)
    
