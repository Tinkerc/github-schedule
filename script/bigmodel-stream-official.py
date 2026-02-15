import json
import requests
import os
from prompts.major_prompts import get_major_intro_prompt
import logging

logging.basicConfig(level=logging.INFO)

url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def get_response(major_info):
    prompt = get_major_intro_prompt(major_info)
    payload = {
        "model": "glm-4",  # 模型名称
        "messages": [
            {"role": "system", "content": "你是一个英语教练，不需要回复和说明，仅返回我要求内容"},
            #{"role": "user", "content": user_input},  # 使用用户输入作为内容
            {"role": "user", "content": prompt},
        ],
    }

    api_key = os.environ.get('BIGMODEL_API_KEY')
    if not api_key:
        logging.error("BIGMODEL_API_KEY is not set in environment variables.")
        return

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",  # 这里放你的 DMXAPI key
        "User-Agent": "DMXAPI/1.0.0 (https://www.dmxapi.com)",
        "Content-Type": "application/json",
    }
    logging.info(
        f"\n=== Sending intro request to ZhipuAI for {major_info['major_name']} (ID: {major_info['major_id']}) ==="
    )
    response = requests.post(url, headers=headers, json=payload)
    response_json = response.json()
    if 'choices' in response_json and len(response_json['choices']) > 0:
        content = response_json['choices'][0]['message']['content']
        print(content)
    else:
        print("No content found in response")

if __name__ == "__main__":
    get_response('计算机科学与技术')
    # while True:
    #     user_input = input("请输入您的问题或指令（输入'quit'退出）：")
    #     if user_input.lower() == "quit":
    #         print("退出应用程序。")
    #         break
    #     get_response(user_input)