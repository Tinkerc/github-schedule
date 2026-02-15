# coding:utf-8
"""
测试分开发送两条消息的格式和长度
"""

# 第一条消息：AI News
message_1 = """# AI快讯 (2026-02-16 周一)
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

# 第二条消息：GitHub Trending
message_2 = """# GitHub Trending 今日热榜

### 今日热榜 Top 15

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

print("=" * 80)
print("分开发送两条消息 - 格式和长度分析")
print("=" * 80)

# 第一条消息统计
msg1_bytes = len(message_1.encode('utf-8'))
print("\n" + "="*80)
print("第一条消息: AI 快讯")
print("="*80)
print("\n内容:")
print(message_1)
print(f"\n字符数: {len(message_1)}")
print(f"字节数: {msg1_bytes}")
print(f"企业微信限制: 4096 字节")
print(f"使用率: {msg1_bytes / 4096 * 100:.1f}%")
print(f"剩余空间: {4096 - msg1_bytes} 字节")
if msg1_bytes <= 4096:
    print("✅ 长度安全")
else:
    print(f"⚠️  超长 {msg1_bytes - 4096} 字节")

# 第二条消息统计
msg2_bytes = len(message_2.encode('utf-8'))
print("\n" + "="*80)
print("第二条消息: GitHub Trending")
print("="*80)
print("\n内容:")
print(message_2)
print(f"\n字符数: {len(message_2)}")
print(f"字节数: {msg2_bytes}")
print(f"企业微信限制: 4096 字节")
print(f"使用率: {msg2_bytes / 4096 * 100:.1f}%")
print(f"剩余空间: {4096 - msg2_bytes} 字节")
if msg2_bytes <= 4096:
    print("✅ 长度安全")
else:
    print(f"⚠️  超长 {msg2_bytes - 4096} 字节")

# 总体统计
print("\n" + "="*80)
print("总体统计")
print("="*80)
print(f"两条消息总字节数: {msg1_bytes + msg2_bytes}")
print(f"平均使用率: {(msg1_bytes + msg2_bytes) / 2 / 4096 * 100:.1f}%")
print("\n优势:")
print("✅ 每条消息更简洁，易于阅读")
print("✅ 不会因为内容过多而被忽略")
print("✅ 可以独立转发或分享")
print("✅ 更好的阅读体验")
