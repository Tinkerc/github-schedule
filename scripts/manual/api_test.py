# coding:utf-8
"""
测试火山引擎（豆包）大模型 API 调用
用于诊断 GitHub Actions 中的问题
"""

import os
import sys
import requests

def test_api_connection():
    """测试火山引擎 API 连接"""
    print("=" * 60)
    print("火山引擎（豆包）大模型 API 连接测试")
    print("=" * 60)

    # 检查环境变量
    api_key = os.environ.get('VOLCENGINE_API_KEY')
    print(f"\n1. 环境变量检查:")
    print(f"   VOLCENGINE_API_KEY: {'✓ 已设置' if api_key else '✗ 未设置'}")

    if not api_key:
        print("\n错误: 未设置 VOLCENGINE_API_KEY 环境变量")
        print("请在 GitHub Actions Secrets 中添加 VOLCENGINE_API_KEY")
        return False

    # 检查 API key 格式
    print(f"\n2. API Key 格式检查:")
    print(f"   长度: {len(api_key)} 字符")

    model = os.environ.get('VOLCENGINE_MODEL', 'ep-20250215154848-djsgr')
    print(f"   模型: {model}")

    # 测试 API 调用
    print(f"\n3. API 调用测试:")

    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "请用一句话介绍你自己"
            }
        ],
        "max_tokens": 100
    }

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        print("   正在发送请求...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"   HTTP 状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                reply = result['choices'][0]['message']['content']
                print(f"   ✓ API 调用成功!")
                print(f"\n   AI 回复: {reply[:100]}...")
                return True
            else:
                print("   ✗ 响应格式异常")
                print(f"   响应内容: {result}")
                return False
        elif response.status_code == 401:
            print("   ✗ 认证失败: API Key 无效或已过期")
            return False
        elif response.status_code == 429:
            print("   ✗ 请求频率超限，请稍后重试")
            return False
        else:
            print(f"   ✗ API 调用失败")
            try:
                error_detail = response.json()
                print(f"   错误详情: {error_detail}")
            except:
                print(f"   响应内容: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print("   ✗ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("   ✗ 网络连接错误")
        return False
    except Exception as e:
        print(f"   ✗ 请求失败: {str(e)}")
        return False


if __name__ == '__main__':
    success = test_api_connection()
    sys.exit(0 if success else 1)
