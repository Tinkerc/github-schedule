# GitHub Trending AI 每日分析 - 设计文档

**日期：** 2026-02-15
**方案：** 批量分析 + 两次 AI 调用（方案 A）

## 1. 概述

创建独立的 GitHub Trending 分析脚本，每日自动获取前 25 个热门项目，使用 GLM-4.7 模型生成详细分析报告，包括趋势概览、热门领域分析和每个项目的功能/技术评估。

## 2. 整体架构

系统由三个核心组件构成：

### 数据获取层（`GitHubTrendingScraper`类）
- 复用 `github-trending.py` 的爬虫逻辑
- 使用 requests + pyquery 爬取 GitHub Trending 页面
- 支持获取指定语言的 trending 项目
- 返回结构化的项目数据（名称、描述、星标数、语言等）

### AI 分析层（`GLMAnalyzer`类）
- 封装 GLM-4.7 API 调用
- 使用环境变量 `BIGMODEL_API_KEY` 进行认证
- 第一次调用的 prompt：批量分析 25 个项目，要求返回 JSON 格式的详细分析
- 第二次调用的 prompt：基于项目分析结果，生成趋势概览和热门领域总结
- 处理 API 错误、重试逻辑、上下文限制

### 报告生成层（`MarkdownReportGenerator`类）
- 组织数据结构：头部信息 → 趋势概览 → 热门领域分析 → 项目详情列表
- 格式化 markdown 输出
- 保存到 `output/github-trending-analysis/YYYY/YYYY-MM-DD.md`

**数据流向：** 爬虫 → AI 分析（2次）→ 报告生成 → 文件输出

## 3. 脚本结构与文件组织

### 文件列表

1. **`script/github-trending-ai-analysis.py`**（主脚本，~300行）
   - `job()` 函数作为入口点（符合项目规范）
   - 包含三个核心类：`GitHubTrendingScraper`、`GLMAnalyzer`、`MarkdownReportGenerator`
   - 配置常量：输出目录基础路径、日期格式、AI 模型配置

2. **`script/prompts/trending_prompts.py`**（Prompt 模块，~100行）
   - `get_batch_analysis_prompt(projects)` - 返回第一次调用的 prompt
   - `get_trend_summary_prompt(analyses)` - 返回第二次调用的 prompt
   - Prompt 模板使用中文（符合项目代码风格）

3. **`script/prompts/trending_examples.py`**（示例输出，可选）
   - 包含期望的 JSON 返回格式示例
   - 用于指导 AI 返回正确的数据结构

4. **`.github/workflows/github-trending-ai-analysis.yml`**
   - 独立 workflow，触发条件：cron schedule
   - 配置 secrets：`BIGMODEL_API_KEY`
   - 执行命令：`python script/github-trending-ai-analysis.py`

## 4. 数据结构与 AI Prompt 设计

### 项目数据结构（爬虫输出）

```python
{
    "name": "项目名称",
    "description": "GitHub 描述",
    "url": "项目链接",
    "stars": "星标数（如 12.5k）",
    "language": "主要语言",
    "stars_today": "今日增长星标数"
}
```

### 第一次 AI 调用（批量分析）

**输入：** 25 个项目的基本信息（JSON 格式）
**输出：** JSON 格式的详细分析

```python
{
    "projects": [
        {
            "name": "项目名称",
            "core_functionality": "核心功能（1-2句）",
            "use_cases": "适用场景（3-4点）",
            "tech_stack": "技术栈（关键依赖/框架）",
            "tech_highlights": "技术亮点（2-3点）",
            "learning_value": "学习价值（1-2句）"
        }
    ]
}
```

### 第二次 AI 调用（趋势分析）

**输入：** 所有项目的分析结果
**输出：** 趋势概览和热门领域分析

```python
{
    "trend_overview": "今日趋势概览（3-5句，描述整体特点）",
    "hot_domains": [
        {"domain": "领域名称", "reason": "热门原因", "projects": ["相关项目列表"]}
    ]
}
```

## 5. 错误处理与边缘情况

### 网络和爬虫错误

- GitHub Trending 页面访问失败 → 记录日志，等待 30s 重试，最多 3 次
- 某个项目信息不完整（无描述/无语言）→ 记录警告，使用占位符（"暂无描述"/"未知"）
- HTTP 429/503 → 指数退避重试（等待时间递增）

### AI API 错误

- API key 未配置 → 立即终止，提示设置 `BIGMODEL_API_KEY`
- API 返回格式错误（非 JSON）→ 记录原始响应，终止执行
- API 返回不完整（项目数量 < 25）→ 使用已返回数据，记录警告
- 上下文超限 → 降级方案：发送简化版项目信息（仅名称+描述+语言），重新分析
- API 调用超时/失败 → 重试 2 次，间隔 10s

### 文件系统错误

- 输出目录不存在 → 自动创建（`os.makedirs(parents=True)`）
- 文件写入失败 → 记录详细错误，终止执行

### 数据验证

- 验证 AI 返回的 JSON 是否包含必需字段（`projects`、`trend_overview`）
- 验证项目数量匹配（爬取 25 个，AI 返回也应 25 个）
- 验证日期格式正确性

## 6. 执行流程与日志

### 主流程（`job()` 函数）

1. 获取当前日期（`datetime.now().strftime('%Y-%m-%d')`）
2. 初始化 scraper，获取所有语言的 trending 项目
3. 调用 AI 第一次：批量分析项目，捕获重试逻辑
4. 调用 AI 第二次：生成趋势概览和热门领域
5. 生成 markdown 报告，保存到文件
6. 输出统计信息：成功分析项目数、执行时间、输出文件路径

### 日志输出（使用 `logging` 模块）

- `INFO` 级别：流程开始/完成、文件保存成功、API 调用成功
- `WARNING` 级别：项目信息不完整、AI 返回不完整、降级方案触发
- `ERROR` 级别：网络失败、API 错误、文件写入失败

## 7. GitHub Actions 配置

### Workflow 配置（`.github/workflows/github-trending-ai-analysis.yml`）

```yaml
name: GitHub Trending AI Analysis

on:
  schedule:
    - cron: "0 2 * * *"  # 每日 00:00 UTC
  workflow_dispatch:  # 支持手动触发

jobs:
  analyze:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python 3.8
      uses: actions/setup-python@v2
      with:
        python-version: 3.8

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run AI analysis
      env:
        BIGMODEL_API_KEY: ${{ secrets.BIGMODEL_API_KEY }}
      run: |
        python script/github-trending-ai-analysis.py

    - name: Commit and push
      run: |
        git config --global user.name "tinkerc"
        git config --global user.email "chenruoyun@126.com"
        git add -A
        git commit -m "feat: update trending AI analysis $(date '+%Y-%m-%d')"
        git push
```

## 8. Markdown 报告结构

```markdown
# GitHub Trending 每日分析报告 - YYYY-MM-DD

## 📈 今日趋势概览
[AI 生成的趋势概览]

## 🔥 热门领域
### 领域 1
**热门原因：** ...
**相关项目：** ...

### 领域 2
...

## 📦 项目详情分析

### 1. [项目名称](链接)
**核心功能：** ...
**适用场景：**
- 场景 1
- 场景 2
- 场景 3

**技术栈：** ...
**技术亮点：**
- 亮点 1
- 亮点 2

**学习价值：** ...

[重复 25 个项目]
```

## 9. 配置与依赖

### Python 依赖

已包含在 `requirements.txt` 中：
- `requests` - HTTP 请求
- `pyquery` - HTML 解析
- `lxml` - XML/HTML 处理
- `cssselect` - CSS 选择器

### 环境变量

- `BIGMODEL_API_KEY` - GLM-4.7 API 密钥（必需）

### 输出目录

- 默认：`output/github-trending-analysis/YYYY/YYYY-MM-DD.md`
- 可通过配置修改

## 10. 实施要点

1. 参考 `script/bigmodel-stream-official.py` 的 API 调用方式
2. 复用 `github-trending.py` 的爬虫逻辑
3. 确保所有错误处理都有日志记录
4. AI prompt 需要明确指定返回 JSON 格式
5. 测试时可以先限制项目数量（如 5 个）验证流程
