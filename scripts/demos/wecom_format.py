# coding:utf-8
"""
展示实际推送到 WeCom Bot 的完整格式
"""

# 实际推送格式示例
full_message = """# AI快讯 (2026-02-16 周一)
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


---

## GitHub Trending 今日热榜
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
    📦 Swift ⭐ 68k stars"""

print("=" * 80)
print("WeCom Bot 推送内容完整格式")
print("=" * 80)
print("\n")
print(full_message)
print("\n")

# 统计信息
content_bytes = len(full_message.encode('utf-8'))
print("=" * 80)
print("统计信息")
print("=" * 80)
print(f"总字符数: {len(full_message)}")
print(f"总字节数: {content_bytes}")
print(f"企业微信限制: 4096 字节")
print(f"使用率: {content_bytes / 4096 * 100:.1f}%")
print(f"剩余空间: {4096 - content_bytes} 字节")

if content_bytes <= 4096:
    print("\n✅ 内容长度在安全范围内")
else:
    print(f"\n⚠️  内容超长 {content_bytes - 4096} 字节")

print("\n" + "=" * 80)
print("格式说明")
print("=" * 80)
print("""
1. AI 快讯部分:
   - 标题: # AI快讯 (日期 星期)
   - 4条新闻，每条包含:
     * 标题 (### 标题)
     * 内容引用 (> 内容)
     * 来源和链接

2. GitHub Trending 部分:
   - 分隔线 (---)
   - 小标题 (## GitHub Trending 今日热榜)
   - 15条项目，每条包含:
     * 排名序号
     * 项目名称和链接 (**[名称](链接)**)
     * 项目描述 (> 描述)
     * 编程语言和星标数 (📦 语言 ⭐ 星标数)

3. 格式特点:
   - 使用 Markdown 格式
   - 使用 emoji 增强可读性
   - 链接可直接点击
   - 层级清晰，易于阅读
""")
