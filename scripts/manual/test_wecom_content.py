# coding:utf-8
"""
测试 WeCom 推送内容长度
"""

import json

# 模拟 AI 新闻内容（4条）
ai_news_content = """
# GitHub Trending AI 分析报告

> 分析日期: 2026-02-15

---

# GitHub Trending 2026-02-15 分析报告

## 4. 推荐关注
| 适用人群                | 推荐项目                                  | 推荐理由                                                                 |
|-------------------------|-------------------------------------------|--------------------------------------------------------------------------|
| AI Agent 开发者         | openclaw/openclaw                         | 196k星的端侧AI助理标杆，可学习跨平台本地AI应用的架构设计                  |
| AI Agent 开发者         | ChromeDevTools/chrome-devtools-mcp        | 官方出品的Agent调试工具，是未来Agent开发的必备基础设施                    |
| 研发效率/DevOps 开发者  | github/gh-aw                              | GitHub官方的智能工作流框架，可学习如何把Agent能力和研发流程深度结合        |
| 量化/交易开发者         | nautechsystems/nautilus_trader            | 当前开源领域性能最强的量化交易框架之一，替代Python方案大幅提升策略效率    |
| AI基础设施开发者        | alibaba/zvec                              | 轻量进程内向量数据库，无需单独部署，适合嵌入端侧AI应用                    |
| IoT/智能家居开发者      | ruvnet/wifi-densepose                     | WiFi感知技术的落地方案，代表下一代无接触感知的核心发展方向                |
| 效率工具爱好者          | steipete/gogcli                           | 谷歌全家桶命令行工具，可在终端一站式操作Gmail、日历、云盘等服务            |

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

# Use only AI news content
full_content = ai_news_content

# 计算长度
print("=" * 60)
print("WeCom Bot 内容长度分析")
print("=" * 60)

print(f"\n1. AI 新闻部分:")
print(f"   字符数: {len(ai_news_content)}")
print(f"   字节数 (UTF-8): {len(ai_news_content.encode('utf-8'))}")

print(f"\n2. 完整内容 (仅AI新闻):")
print(f"   字符数: {len(full_content)}")
print(f"   字节数 (UTF-8): {len(full_content.encode('utf-8'))}")

print(f"\n3. 企业微信限制:")
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
    print("1. 缩短 AI 新闻内容")
    print("2. 简化每条信息的格式")
else:
    print("\n当前长度安全，可以正常发送")

# 显示部分内容预览
print("\n" + "=" * 60)
print("内容预览 (前500字符):")
print("=" * 60)
print(full_content[:500])
print("...")
