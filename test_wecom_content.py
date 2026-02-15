# coding:utf-8
"""
测试 WeCom 推送内容长度
"""

import json

# 模拟 AI 新闻内容（4条）
ai_news_content = """# AI快讯 (2026-02-16 周一)
## 今日要闻
### OpenAI 发布新模型 GPT-5
> 今天，OpenAI 正式发布了备受期待的 GPT-5 模型，该模型在推理能力、多模态理解和代码生成方面均有显著提升
来源：AIbot [查看详情](https://ai-bot.cn)

### Claude 4 推出企业版
> Anthropic 宣布推出 Claude 4 企业版，针对企业客户增加了更严格的安全控制和定制化能力
来源：AIbot [查看详情](https://ai-bot.cn)

### Google Gemini 2.0 开源
> Google 宣布将 Gemini 2.0 模型开源，研究社区可以免费使用和修改该模型
来源：AIbot [查看详情](https://ai-bot.cn)

### Meta 发布 Llama 4
> Meta 发布了 Llama 4 系列模型，包括 7B、13B、70B 三个版本，性能全面超越前代
来源：AIbot [查看详情](https://ai-bot.cn)

"""

# 模拟 GitHub Trending 内容（15条）
trending_content = """### 今日热榜 Top 15

1. **[microsoft/vscode](https://github.com/microsoft/vscode)**
   > Visual Studio Code
   📦 TypeScript ⭐ 159k stars

2. **[tensorflow/tensorflow](https://github.com/tensorflow/tensorflow)**
   > An Open Source Machine Learning Framework for Everyone
   📦 C++ ⭐ 185k stars

3. **[pytorch/pytorch](https://github.com/pytorch/pytorch)**
   > Tensors and Dynamic neural networks in Python with strong GPU acceleration
   📦 Python ⭐ 80k stars

4. **[vercel/next.js](https://github.com/vercel/next.js)**
   > The React Framework
   📦 JavaScript ⭐ 125k stars

5. **[microsoft/playwright](https://github.com/microsoft/playwright)**
   > Playwright is a framework for Web Testing and Automation
   📦 TypeScript ⭐ 65k stars

6. **[openai/gym](https://github.com/openai/gym)**
   > A toolkit for developing and comparing reinforcement learning algorithms
   📦 Python ⭐ 35k stars

7. **[langchain-ai/langchain](https://github.com/langchain-ai/langchain)**
   > ⚡ Building applications with LLMs through composability ⚡
   📦 Python ⭐ 95k stars

8. **[microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel)**
   > Integrate cutting-edge LLM technology quickly and easily into your apps
   📦 C# ⭐ 21k stars

9. **[dotnet/aspnetcore](https://github.com/dotnet/aspnetcore)**
   > ASP.NET Core is a cross-platform .NET framework for building modern cloud-based web applications
   📦 C# ⭐ 36k stars

10. **[golang/go](https://github.com/golang/go)**
    > The Go programming language
    📦 Go ⭐ 120k stars

11. **[facebook/react](https://github.com/facebook/react)**
    > The library for web and native user interfaces
    📦 JavaScript ⭐ 227k stars

12. **[vuejs/core](https://github.com/vuejs/core)**
    > Vue.js is a progressive, incrementally-adoptable JavaScript framework for building UI on the web
    📦 TypeScript ⭐ 47k stars

13. **[rust-lang/rust](https://github.com/rust-lang/rust)**
    > Empowering everyone to build reliable and efficient software
    📦 Rust ⭐ 95k stars

14. **[nodejs/node](https://github.com/nodejs/node)**
    > Node.js JavaScript runtime ✨ build for fun
    📦 JavaScript ⭐ 106k stars

15. **[apple/swift](https://github.com/apple/swift)**
    > Swift is a general-purpose programming language built using a modern approach to safety
    📦 Swift ⭐ 68k stars
"""

# 合并内容
full_content = ai_news_content + "\n\n---\n\n" + "## GitHub Trending 今日热榜\n" + trending_content

# 计算长度
print("=" * 60)
print("WeCom Bot 内容长度分析")
print("=" * 60)

print(f"\n1. AI 新闻部分:")
print(f"   字符数: {len(ai_news_content)}")
print(f"   字节数 (UTF-8): {len(ai_news_content.encode('utf-8'))}")

print(f"\n2. GitHub Trending 部分:")
print(f"   字符数: {len(trending_content)}")
print(f"   字节数 (UTF-8): {len(trending_content.encode('utf-8'))}")

print(f"\n3. 完整内容:")
print(f"   字符数: {len(full_content)}")
print(f"   字节数 (UTF-8): {len(full_content.encode('utf-8'))}")

print(f"\n4. 企业微信限制:")
print(f"   最大支持: 4096 字节")
print(f"   当前使用: {len(full_content.encode('utf-8'))} 字节")
print(f"   剩余空间: {4096 - len(full_content.encode('utf-8'))} 字节")

if len(full_content.encode('utf-8')) > 4096:
    print(f"\n   ⚠️  警告: 内容超长 {len(full_content.encode('utf-8')) - 4096} 字节")
else:
    print(f"\n   ✅ 内容长度在限制范围内")

print("\n" + "=" * 60)
print("建议:")
print("=" * 60)

if len(full_content.encode('utf-8')) > 4096:
    print("\n当前内容会超长，建议:")
    print("1. 减少 GitHub Trending 条数（15条 → 5-8条）")
    print("2. 简化每条信息的格式")
    print("3. 分成两条消息发送")
else:
    print("\n当前长度安全，但建议:")
    print("1. 保留一定缓冲空间")
    print("2. 监控实际使用情况")

# 显示部分内容预览
print("\n" + "=" * 60)
print("内容预览 (前500字符):")
print("=" * 60)
print(full_content[:500])
print("...")
