# GitHub Trending AI 每日分析 - 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标：** 创建独立的 GitHub Trending 分析脚本，每日自动获取前 25 个热门项目，使用 GLM-4.7 模型生成详细分析报告

**架构：** 三层架构 - 数据获取层（爬虫）→ AI 分析层（GLM-4.7 API）→ 报告生成层（Markdown）。使用独立 GitHub Actions workflow 每日自动执行

**技术栈：** Python 3.8, requests, pyquery, GLM-4.7 API

---

## Task 1: 创建 Prompt 模块

**文件：**
- 创建: `script/prompts/trending_prompts.py`

**步骤 1: 创建 prompt 模块基础结构**

创建文件 `script/prompts/trending_prompts.py`：

```python
# coding:utf-8
"""GitHub Trending AI 分析的 Prompt 模板"""

def get_batch_analysis_prompt(projects):
    """
    生成批量分析项目详情的 prompt

    Args:
        projects: list[dict], 项目列表，每个项目包含 name, description, url, stars, language, stars_today

    Returns:
        str: AI 分析的 prompt
    """
    projects_text = ""
    for i, p in enumerate(projects, 1):
        projects_text += f"""
{i}. {p.get('name', 'Unknown')}
   描述: {p.get('description', '暂无描述')}
   语言: {p.get('language', '未知')}
   星标: {p.get('stars', 'N/A')} (今日 +{p.get('stars_today', 'N/A')})
   链接: {p.get('url', '')}
"""

    prompt = f"""你是一个技术分析师，擅长分析开源项目的技术价值和实用价值。

请分析以下 {len(projects)} 个 GitHub Trending 项目，对每个项目提供详细分析。

项目列表：
{projects_text}

请严格按照以下 JSON 格式返回分析结果：
{{
    "projects": [
        {{
            "name": "项目名称",
            "core_functionality": "核心功能（1-2句话）",
            "use_cases": "适用场景（3-4个要点，用换行符分隔）",
            "tech_stack": "技术栈（关键依赖/框架）",
            "tech_highlights": "技术亮点（2-3个要点，用换行符分隔）",
            "learning_value": "学习价值（1-2句话）"
        }}
    ]
}}

注意：
1. 必须返回有效的 JSON 格式，不要包含其他文字
2. core_functionality 简洁明了，说明项目做什么
3. use_cases 要具体，说明在什么场景下使用
4. tech_stack 列出关键技术和框架
5. tech_highlights 突出技术创新点
6. learning_value 说明开发者能学到什么
"""

    return prompt


def get_trend_summary_prompt(analyses):
    """
    生成趋势概览和热门领域分析的 prompt

    Args:
        analyses: dict, 包含所有项目的分析结果

    Returns:
        str: AI 分析的 prompt
    """
    projects_info = ""
    for p in analyses.get('projects', []):
        projects_info += f"""
- {p.get('name', 'Unknown')}: {p.get('core_functionality', '')}
  技术栈: {p.get('tech_stack', '未知')}
  技术亮点: {p.get('tech_highlights', '')}
"""

    prompt = f"""你是一个技术趋势分析师，擅长发现技术发展动向。

基于以下 {len(analyses.get('projects', []))} 个项目的分析结果，生成趋势概览和热门领域分析。

项目分析：
{projects_info}

请严格按照以下 JSON 格式返回：
{{
    "trend_overview": "今日趋势概览（3-5句话，描述整体技术趋势特点、创新方向、热门话题等）",
    "hot_domains": [
        {{
            "domain": "领域名称（如 AI/LLM、Web3、DevOps 等）",
            "reason": "热门原因（2-3句话）",
            "projects": ["相关项目名称1", "相关项目名称2"]
        }}
    ]
}}

注意：
1. 必须返回有效的 JSON 格式
2. trend_overview 要宏观描述整体趋势
3. hot_domains 提取 3-5 个热门领域
4. 每个领域要说明为什么热门，并列出相关项目
"""

    return prompt
```

**步骤 2: 提交基础结构**

```bash
git add script/prompts/trending_prompts.py
git commit -m "feat: add trending analysis prompt module"
```

---

## Task 2: 创建爬虫类

**文件：**
- 创建: `script/github-trending-ai-analysis.py`（创建文件，包含 GitHubTrendingScraper 类）

**步骤 1: 创建主脚本文件和爬虫类**

创建文件 `script/github-trending-ai-analysis.py`：

```python
# coding:utf-8

import datetime
import os
import time
import codecs
import requests
import logging
import json
from pyquery import PyQuery as pq

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class GitHubTrendingScraper:
    """GitHub Trending 爬虫"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }

    def scrape_trending(self, language=''):
        """
        爬取 GitHub Trending 项目

        Args:
            language: str, 编程语言（空字符串表示所有语言）

        Returns:
            list[dict]: 项目列表
        """
        url = f'https://github.com/trending/{language}' if language else 'https://github.com/trending'

        for attempt in range(3):
            try:
                logger.info(f"正在爬取 GitHub Trending: {url}")
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()

                doc = pq(response.content)
                items = doc('div.Box article.Box-row')

                projects = []
                for item in items:
                    i = pq(item)
                    title_elem = i(".lh-condensed a")
                    if not title_elem:
                        continue

                    title = title_elem.text()
                    url_path = title_elem.attr("href")
                    description = i("p.col-9").text().strip()

                    # 获取星标数
                    stars_elem = i("a[href*='/stargazers']")
                    stars_text = stars_elem.text().strip() if stars_elem else "0"

                    # 获取今日增长星标
                    today_stars_elem = i("span.d-inline-block")
                    today_stars_text = today_stars_elem.text().strip() if today_stars_elem else "0"

                    # 获取语言
                    language_elem = i("span[itemprop='programmingLanguage']")
                    language_text = language_elem.text().strip() if language_elem else "未知"

                    projects.append({
                        "name": title,
                        "description": description or "暂无描述",
                        "url": f"https://github.com{url_path}",
                        "stars": stars_text,
                        "language": language_text,
                        "stars_today": today_stars_text.replace("stars today", "").strip()
                    })

                logger.info(f"成功爬取 {len(projects)} 个项目")
                return projects

            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/3): {str(e)}")
                if attempt < 2:
                    time.sleep(30)
                else:
                    raise

        return []

    def scrape_all_languages(self):
        """
        爬取所有语言的 trending 项目（只爬取主页面）

        Returns:
            list[dict]: 项目列表（最多 25 个）
        """
        projects = self.scrape_trending('')
        return projects[:25]  # 限制 25 个
```

**步骤 2: 测试爬虫类**

运行以下测试代码：

```python
if __name__ == '__main__':
    scraper = GitHubTrendingScraper()
    projects = scraper.scrape_all_languages()
    print(f"爬取到 {len(projects)} 个项目")
    for p in projects[:3]:
        print(f"- {p['name']}: {p['description'][:50]}...")
```

运行：`python script/github-trending-ai-analysis.py`

预期输出：
```
[2026-02-15 XX:XX:XX] INFO: 正在爬取 GitHub Trending: https://github.com/trending
[2026-02-15 XX:XX:XX] INFO: 成功爬取 25 个项目
爬取到 25 个项目
- 项目1: 描述...
- 项目2: 描述...
- 项目3: 描述...
```

**步骤 3: 提交爬虫类**

```bash
git add script/github-trending-ai-analysis.py
git commit -m "feat: add GitHub Trending scraper class"
```

---

## Task 3: 创建 AI 分析类

**文件：**
- 修改: `script/github-trending-ai-analysis.py`（添加 GLMAnalyzer 类）

**步骤 1: 添加 AI 分析类**

在文件 `script/github-trending-ai-analysis.py` 中添加 GLMAnalyzer 类（添加到文件末尾，`if __name__` 之前）：

```python
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prompts'))
from trending_prompts import get_batch_analysis_prompt, get_trend_summary_prompt


class GLMAnalyzer:
    """GLM-4.7 AI 分析器"""

    def __init__(self):
        self.api_key = os.environ.get('BIGMODEL_API_KEY')
        if not self.api_key:
            raise ValueError("环境变量 BIGMODEL_API_KEY 未设置")

        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _call_api(self, prompt):
        """
        调用 GLM-4.7 API

        Args:
            prompt: str, 用户 prompt

        Returns:
            dict: API 返回的 JSON 数据
        """
        payload = {
            "model": "glm-4.7",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的技术分析师，返回有效的 JSON 格式，不要包含其他文字。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 8000
        }

        for attempt in range(3):
            try:
                logger.info(f"正在调 GLM-4.7 API (尝试 {attempt + 1}/3)")
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()

                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    logger.info("API 调用成功")
                    return content
                else:
                    logger.error(f"API 返回格式错误: {result}")
                    raise ValueError("Invalid API response")

            except requests.exceptions.RequestException as e:
                logger.warning(f"API 请求失败 (尝试 {attempt + 1}/3): {str(e)}")
                if attempt < 2:
                    time.sleep(10)
                else:
                    raise

    def analyze_projects(self, projects):
        """
        批量分析项目

        Args:
            projects: list[dict], 项目列表

        Returns:
            dict: 分析结果
        """
        prompt = get_batch_analysis_prompt(projects)
        response = self._call_api(prompt)

        # 解析 JSON
        try:
            # 移除可能的 markdown 代码块标记
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            result = json.loads(response)
            if 'projects' not in result:
                raise ValueError("Response missing 'projects' field")

            logger.info(f"成功分析 {len(result['projects'])} 个项目")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {str(e)}")
            logger.error(f"原始响应: {response[:500]}")
            raise

    def generate_trend_summary(self, analyses):
        """
        生成趋势概览

        Args:
            analyses: dict, 项目分析结果

        Returns:
            dict: 趋势分析结果
        """
        prompt = get_trend_summary_prompt(analyses)
        response = self._call_api(prompt)

        # 解析 JSON
        try:
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            result = json.loads(response)
            if 'trend_overview' not in result:
                raise ValueError("Response missing 'trend_overview' field")

            logger.info("成功生成趋势概览")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {str(e)}")
            logger.error(f"原始响应: {response[:500]}")
            raise
```

**步骤 2: 测试 AI 分析类**

在 `if __name__ == '__main__':` 部分添加测试代码：

```python
if __name__ == '__main__':
    # 测试 AI 分析
    scraper = GitHubTrendingScraper()
    projects = scraper.scrape_all_languages()[:5]  # 先测试 5 个

    analyzer = GLMAnalyzer()
    analyses = analyzer.analyze_projects(projects)
    print(f"分析结果: {json.dumps(analyses, ensure_ascii=False, indent=2)}")
```

运行：`BIGMODEL_API_KEY=your_key python script/github-trending-ai-analysis.py`

预期输出：
```
[2026-02-15 XX:XX:XX] INFO: 正在调 GLM-4.7 API (尝试 1/3)
[2026-02-15 XX:XX:XX] INFO: API 调用成功
[2026-02-15 XX:XX:XX] INFO: 成功分析 5 个项目
分析结果: {
  "projects": [...]
}
```

**步骤 3: 提交 AI 分析类**

```bash
git add script/github-trending-ai-analysis.py
git commit -m "feat: add GLM-4.7 analyzer class"
```

---

## Task 4: 创建报告生成类

**文件：**
- 修改: `script/github-trending-ai-analysis.py`（添加 MarkdownReportGenerator 类）

**步骤 1: 添加报告生成类**

在文件 `script/github-trending-ai-analysis.py` 中添加 MarkdownReportGenerator 类（添加到 GLMAnalyzer 类之后）：

```python
class MarkdownReportGenerator:
    """Markdown 报告生成器"""

    def __init__(self, output_dir):
        """
        初始化报告生成器

        Args:
            output_dir: str, 输出基础目录
        """
        self.output_dir = output_dir

    def generate(self, date, projects, analyses, trend_summary):
        """
        生成 Markdown 报告

        Args:
            date: str, 日期 (YYYY-MM-DD)
            projects: list[dict], 原始项目数据
            analyses: dict, AI 分析结果
            trend_summary: dict, 趋势分析结果

        Returns:
            str: 报告文件路径
        """
        # 创建输出目录
        year = date.split('-')[0]
        output_path = os.path.join(self.output_dir, 'github-trending-ai-analysis', year)
        os.makedirs(output_path, exist_ok=True)

        filename = os.path.join(output_path, f'{date}.md')

        # 生成报告内容
        content = self._generate_content(date, projects, analyses, trend_summary)

        # 写入文件
        with codecs.open(filename, 'w', 'utf-8') as f:
            f.write(content)

        logger.info(f"报告已保存: {filename}")
        return filename

    def _generate_content(self, date, projects, analyses, trend_summary):
        """生成报告内容"""
        content = f"""# GitHub Trending 每日分析报告 - {date}

## 📈 今日趋势概览

{trend_summary.get('trend_overview', '')}

## 🔥 热门领域

"""

        # 热门领域
        for domain in trend_summary.get('hot_domains', []):
            content += f"""### {domain.get('domain', '未知领域')}

{domain.get('reason', '')}

**相关项目：** {', '.join(domain.get('projects', []))}

"""

        # 项目详情
        content += "\n## 📦 项目详情分析\n\n"

        # 创建项目名称到分析的映射
        analysis_map = {p['name']: p for p in analyses.get('projects', [])}

        for idx, project in enumerate(projects, 1):
            name = project['name']
            analysis = analysis_map.get(name, {})

            content += f"""### {idx}. [{name}]({project['url']})

**星标：** {project['stars']} (今日 +{project['stars_today']}) | **语言：** {project['language']}

**核心功能：** {analysis.get('core_functionality', '暂无')}

**适用场景：**
{self._format_list(analysis.get('use_cases', ''))}

**技术栈：** {analysis.get('tech_stack', '未知')}

**技术亮点：**
{self._format_list(analysis.get('tech_highlights', ''))}

**学习价值：** {analysis.get('learning_value', '暂无')}

---

"""

        return content

    def _format_list(self, text):
        """格式化列表文本"""
        if not text:
            return "- 暂无"
        lines = text.strip().split('\n')
        return '\n'.join(f"- {line.strip()}" for line in lines if line.strip())
```

**步骤 2: 测试报告生成类**

在 `if __name__ == '__main__':` 部分添加完整测试：

```python
if __name__ == '__main__':
    # 完整流程测试
    logger.info("开始 GitHub Trending AI 分析")

    # 1. 爬取数据
    scraper = GitHubTrendingScraper()
    projects = scraper.scrape_all_languages()[:5]  # 测试 5 个

    # 2. AI 分析
    analyzer = GLMAnalyzer()
    analyses = analyzer.analyze_projects(projects)

    # 3. 趋势总结
    trend_summary = analyzer.generate_trend_summary(analyses)

    # 4. 生成报告
    generator = MarkdownReportGenerator('output')
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    report_path = generator.generate(date, projects, analyses, trend_summary)

    logger.info(f"分析完成！报告路径: {report_path}")
```

运行：`BIGMODEL_API_KEY=your_key python script/github-trending-ai-analysis.py`

预期输出：
```
[2026-02-15 XX:XX:XX] INFO: 开始 GitHub Trending AI 分析
[2026-02-15 XX:XX:XX] INFO: 正在爬取 GitHub Trending: https://github.com/trending
[2026-02-15 XX:XX:XX] INFO: 成功爬取 5 个项目
[2026-02-15 XX:XX:XX] INFO: 正在调 GLM-4.7 API (尝试 1/3)
[2026-02-15 XX:XX:XX] INFO: API 调用成功
[2026-02-15 XX:XX:XX] INFO: 成功分析 5 个项目
[2026-02-15 XX:XX:XX] INFO: 正在调 GLM-4.7 API (尝试 1/3)
[2026-02-15 XX:XX:XX] INFO: API 调用成功
[2026-02-15 XX:XX:XX] INFO: 成功生成趋势概览
[2026-02-15 XX:XX:XX] INFO: 报告已保存: output/github-trending-ai-analysis/2026/2026-02-15.md
[2026-02-15 XX:XX:XX] INFO: 分析完成！报告路径: output/github-trending-ai-analysis/2026/2026-02-15.md
```

**步骤 3: 验证报告内容**

查看生成的报告：`cat output/github-trending-ai-analysis/2026/2026-02-15.md`

验证报告包含：
- 标题和日期
- 趋势概览部分
- 热门领域部分
- 项目详情部分（5 个项目）

**步骤 4: 提交报告生成类**

```bash
git add script/github-trending-ai-analysis.py
git commit -m "feat: add markdown report generator class"
```

---

## Task 5: 实现主流程 job() 函数

**文件：**
- 修改: `script/github-trending-ai-analysis.py`（添加 job() 函数）

**步骤 1: 实现 job() 函数**

在文件中添加 job() 函数（添加到所有类定义之后，`if __name__` 之前）：

```python
def job():
    """主任务入口"""
    start_time = time.time()
    logger.info("="*60)
    logger.info("GitHub Trending AI 分析任务开始")
    logger.info("="*60)

    try:
        # 1. 获取当前日期
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        logger.info(f"目标日期: {date}")

        # 2. 爬取 GitHub Trending 数据
        logger.info("步骤 1/4: 爬取 GitHub Trending 数据")
        scraper = GitHubTrendingScraper()
        projects = scraper.scrape_all_languages()

        if len(projects) == 0:
            logger.error("未爬取到任何项目，任务终止")
            return

        logger.info(f"成功获取 {len(projects)} 个项目")

        # 3. AI 批量分析
        logger.info("步骤 2/4: AI 批量分析项目")
        analyzer = GLMAnalyzer()
        analyses = analyzer.analyze_projects(projects)

        if len(analyses.get('projects', [])) == 0:
            logger.error("AI 分析失败，任务终止")
            return

        # 4. 生成趋势概览
        logger.info("步骤 3/4: 生成趋势概览和热门领域")
        trend_summary = analyzer.generate_trend_summary(analyses)

        # 5. 生成报告
        logger.info("步骤 4/4: 生成 Markdown 报告")
        generator = MarkdownReportGenerator('output')
        report_path = generator.generate(date, projects, analyses, trend_summary)

        # 6. 输出统计信息
        elapsed = time.time() - start_time
        logger.info("="*60)
        logger.info("任务完成！")
        logger.info(f"执行时间: {elapsed:.2f} 秒")
        logger.info(f"分析项目数: {len(projects)}")
        logger.info(f"报告路径: {report_path}")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"任务执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
```

**步骤 2: 更新 main 块测试**

修改 `if __name__ == '__main__':` 部分：

```python
if __name__ == '__main__':
    job()
```

**步骤 3: 测试完整流程**

运行：`BIGMODEL_API_KEY=your_key python script/github-trending-ai-analysis.py`

预期输出：
```
============================================================
GitHub Trending AI 分析任务开始
============================================================
目标日期: 2026-02-15
步骤 1/4: 爬取 GitHub Trending 数据
正在爬取 GitHub Trending: https://github.com/trending
成功爬取 25 个项目
成功获取 25 个项目
步骤 2/4: AI 批量分析项目
正在调 GLM-4.7 API (尝试 1/3)
API 调用成功
成功分析 25 个项目
步骤 3/4: 生成趋势概览和热门领域
正在调 GLM-4.7 API (尝试 1/3)
API 调用成功
成功生成趋势概览
步骤 4/4: 生成 Markdown 报告
报告已保存: output/github-trending-ai-analysis/2026/2026-02-15.md
============================================================
任务完成！
执行时间: XX.XX 秒
分析项目数: 25
报告路径: output/github-trending-ai-analysis/2026/2026-02-15.md
============================================================
```

**步骤 4: 提交主流程**

```bash
git add script/github-trending-ai-analysis.py
git commit -m "feat: implement main job function"
```

---

## Task 6: 创建 GitHub Actions Workflow

**文件：**
- 创建: `.github/workflows/github-trending-ai-analysis.yml`

**步骤 1: 创建 workflow 配置**

创建文件 `.github/workflows/github-trending-ai-analysis.yml`：

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
    - name: Checkout repository
      uses: actions/checkout@v2

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

    - name: Commit and push results
      run: |
        git config --global user.name "tinkerc"
        git config --global user.email "chenruoyun@126.com"
        git add -A
        git commit -m "feat: update trending AI analysis $(date '+%Y-%m-%d')" || echo "No changes to commit"
        git push
```

**步骤 2: 提交 workflow**

```bash
git add .github/workflows/github-trending-ai-analysis.yml
git commit -m "feat: add GitHub Actions workflow for trending AI analysis"
```

---

## Task 7: 验证和测试

**步骤 1: 本地完整测试**

运行完整流程（25 个项目）：

```bash
BIGMODEL_API_KEY=your_key python script/github-trending-ai-analysis.py
```

验证：
- 成功爬取 25 个项目
- AI 分析返回 25 个项目分析
- 趋势概览生成成功
- 报告文件包含所有内容
- 执行时间合理（< 5 分钟）

**步骤 2: 检查报告质量**

查看生成的报告：

```bash
cat output/github-trending-ai-analysis/2026/$(date +%Y-%m-%d).md | head -100
```

验证报告质量：
- 标题格式正确
- 趋势概览内容有意义
- 热门领域分类合理（3-5 个领域）
- 每个项目包含所有必需字段
- Markdown 格式正确

**步骤 3: 测试错误处理**

测试 API key 未设置：

```bash
unset BIGMODEL_API_KEY
python script/github-trending-ai-analysis.py
```

预期输出：
```
ValueError: 环境变量 BIGMODEL_API_KEY 未设置
```

**步骤 4: 提交最终版本**

```bash
git add script/github-trending-ai-analysis.py script/prompts/trending_prompts.py
git commit -m "chore: add error handling and final polish"
```

---

## Task 8: 更新项目文档

**文件：**
- 修改: `CLAUDE.md`

**步骤 1: 更新 CLAUDE.md**

在 `CLAUDE.md` 的 "Script Conventions" 部分添加：

```markdown
Scripts are executed in filename order:
- `1.ai-news.py` - Fetches AI news from https://ai-bot.cn/daily-ai-news/ and saves as JSON
- `2.wecom-robot.py` - Reads the news JSON and posts to WeChat Work webhook
- `github-trending.py` - Scrapes GitHub trending repositories for multiple languages
- `bigmodel-stream-official.py` - Makes API calls to ZhipuAI (GLM-4 model)
- `github-trending-ai-analysis.py` - Independent script for GitHub Trending AI analysis (uses GLM-4.7)
```

在 "Development Notes" 部分添加：

```markdown
- The `github-trending-ai-analysis.py` script runs independently via GitHub Actions workflow
- Output: `output/github-trending-ai-analysis/YYYY/YYYY-MM-DD.md`
- Requires `BIGMODEL_API_KEY` environment variable
```

**步骤 2: 提交文档更新**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with trending AI analysis info"
```

---

## Task 9: 推送到远程仓库

**步骤 1: 推送所有提交**

```bash
git push origin main
```

**步骤 2: 验证 GitHub Actions**

1. 访问 GitHub Actions 页面
2. 查看 workflow "GitHub Trending AI Analysis"
3. 确认 secrets 中配置了 `BIGMODEL_API_KEY`
4. 手动触发 workflow 测试（workflow_dispatch）

**步骤 3: 验证输出**

等待 workflow 完成后，检查仓库中的 `output/github-trending-ai-analysis/` 目录。

---

## 附录：配置 Secrets

### GitHub Actions Secrets 配置

在 GitHub 仓库设置中添加 Secret：
1. Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `BIGMODEL_API_KEY`
4. Value: 你的 GLM-4.7 API 密钥
5. 点击 Add secret

---

## 测试清单

- [ ] 本地运行成功（5 个项目测试）
- [ ] 本地运行成功（25 个项目完整流程）
- [ ] 报告内容完整且格式正确
- [ ] API key 未设置时正确报错
- [ ] 网络错误时正确重试
- [ ] GitHub Actions workflow 配置正确
- [ ] 手动触发 workflow 成功
- [ ] 文档更新完成
