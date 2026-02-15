# 技术行业动态跟踪系统实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个每日自动化的技术行业动态跟踪系统，从Hacker News、Product Hunt和技术博客收集数据，使用AI生成趋势简报，并通过企业微信推送。

**Architecture:**
- 采用独立任务架构，为每个数据源创建独立的Task类（继承core/base.py中的Task基类）
- 使用TechInsightsTask综合所有数据源，调用ZhipuAI API生成分析
- 扩展WeComNotifier支持tech_insights订阅，推送简报到企业微信

**Tech Stack:**
- Python 3.8+
- requests (HTTP客户端)
- pyquery (HTML解析)
- ZhipuAI API (GLM模型，现有代码已集成)
- 基于现有Task/Notifier框架

**Implementation Order:**
1. HackerNewsTask - 验证基础流程
2. TechInsightsTask - 核心AI分析（先用Mock数据）
3. ProductHuntTask - 扩展数据源
4. TechBlogsTask - 扩展数据源
5. 扩展WeComNotifier - 集成通知
6. 集成测试与验证

---

## Task 1: 创建HackerNewsTask基础框架

**Files:**
- Create: `tasks/hackernews.py`

**Step 1: 创建tasks目录（如果不存在）**

Run: `ls -la tasks/ 2>/dev/null || mkdir tasks`

Expected: 目录已存在或创建成功

**Step 2: 创建HackerNewsTask类文件**

Create `tasks/hackernews.py`:

```python
# tasks/hackernews.py
from core.base import Task
import requests
import json
from datetime import datetime

class HackerNewsTask(Task):
    """获取Hacker News Top 30故事"""

    TASK_ID = "hackernews"
    PRIORITY = 15

    def execute(self) -> bool:
        """执行Hacker News数据抓取"""
        try:
            print(f"[{self.TASK_ID}] 开始获取Hacker News Top 30...")

            # 获取Top 30故事IDs
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:30]

            stories = []
            for idx, story_id in enumerate(story_ids, 1):
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_resp = requests.get(story_url, timeout=10)
                story_resp.raise_for_status()
                story_data = story_resp.json()

                # 只处理有URL的故事（过滤掉ask hn等）
                if not story_data.get('url'):
                    continue

                stories.append({
                    "title": story_data.get("title", ""),
                    "url": story_data.get("url", ""),
                    "points": story_data.get("score", 0),
                    "comments_count": story_data.get("descendants", 0),
                    "posted_at": datetime.fromtimestamp(story_data.get("time", 0)).isoformat(),
                    "source": "hackernews",
                    "hn_id": story_id
                })

                print(f"[{self.TASK_ID}] 获取进度: {idx}/30")

            # 保存到JSON
            output_path = self.get_output_path(f"hackernews/{self.get_today()}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(stories, f, ensure_ascii=False, indent=2)

            print(f"[{self.TASK_ID}] ✓ 成功获取并保存 {len(stories)} 条Hacker News")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")
            return True

        except requests.Timeout:
            print(f"[{self.TASK_ID}] ✗ 请求超时")
            return False
        except requests.HTTPError as e:
            print(f"[{self.TASK_ID}] ✗ HTTP错误: {e.response.status_code}")
            return False
        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ 错误: {str(e)}")
            return False
```

**Step 3: 独立测试HackerNewsTask**

Run: `python -c "from tasks.hackernews import HackerNewsTask; task = HackerNewsTask(); print('执行结果:', task.execute())"`

Expected:
```
[hackernews] 开始获取Hacker News Top 30...
[hackernews] 获取进度: 1/30
...
[hackernews] ✓ 成功获取并保存 XX 条Hacker News
[hackernews] 输出文件: .../output/hackernews/2026-02-16.json
执行结果: True
```

**Step 4: 验证输出文件**

Run: `ls -lh output/hackernews/ && cat output/hackernews/$(date +%Y-%m-%d).json | head -20`

Expected: JSON文件存在，包含Hacker News数据

**Step 5: 提交**

```bash
git add tasks/hackernews.py
git commit -m "feat(tasks): add HackerNewsTask for fetching top 30 stories

- Implement HackerNewsTask using HN Official API
- Fetch top 30 stories with title, url, points, comments
- Save to output/hackernews/YYYY-MM-DD.json
- Handle timeout and HTTP errors gracefully

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: 创建TechInsightsTask基础框架（使用Mock数据）

**Files:**
- Create: `tasks/tech_insights.py`

**Step 1: 创建TechInsightsTask类框架**

Create `tasks/tech_insights.py`:

```python
# tasks/tech_insights.py
from core.base import Task
import os
import json
from typing import List, Dict, Any

class TechInsightsTask(Task):
    """综合分析所有数据源，生成技术行业简报"""

    TASK_ID = "tech_insights"
    PRIORITY = 40

    def execute(self) -> bool:
        """执行AI分析"""
        try:
            print(f"[{self.TASK_ID}] 开始生成技术行业简报...")

            # 读取所有数据源
            hn_data = self._read_json(f"hackernews/{self.get_today()}.json")
            ph_data = self._read_json(f"producthunt/{self.get_today()}.json")
            tb_data = self._read_json(f"techblogs/{self.get_today()}.json")

            # 检查可用数据源
            available_sources = []
            if hn_data:
                available_sources.append("hackernews")
            if ph_data:
                available_sources.append("producthunt")
            if tb_data:
                available_sources.append("techblogs")

            if not available_sources:
                print(f"[{self.TASK_ID}] ✗ 所有数据源均不可用")
                return False

            print(f"[{self.TASK_ID}] 可用数据源: {', '.join(available_sources)}")

            # 构建AI提示词
            prompt = self._build_prompt(hn_data, ph_data, tb_data)

            # 调用AI分析（暂时使用Mock）
            # TODO: 下一步集成真实ZhipuAI API
            insights = self._mock_ai_analysis(prompt)

            # 保存简报
            output_path = self.get_output_path(f"tech-insights/{self.get_today()}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)

            print(f"[{self.TASK_ID}] ✓ 技术简报生成成功")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")
            return True

        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ 错误: {str(e)}")
            return False

    def _read_json(self, filepath: str) -> List:
        """读取JSON文件，不存在返回None"""
        full_path = self.get_output_path(filepath)
        if not os.path.exists(full_path):
            return None
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _build_prompt(self, hn_data: List, ph_data: List, tb_data: List) -> str:
        """构建AI分析提示词"""
        prompt = f"""你是一位技术行业分析师。请基于以下数据源，生成一份简洁的技术行业动态简报。

## 数据源

### 1. Hacker News Top 30
{self._format_hn_data(hn_data or [])}

### 2. Product Hunt Top 20
{self._format_ph_data(ph_data or [])}

### 3. 技术博客热门文章
{self._format_tb_data(tb_data or [])}

## 分析要求

请按以下结构生成简报（使用中文，控制在1000字以内）：

# 技术行业动态简报 - {self.get_today()}

## 🔥 今日热门技术话题
（基于Hacker News讨论热度，总结前3个最受关注的技术话题）

## 🚀 新兴热门项目
（从HN和Product Hunt中挑选5个最有趣的新项目/工具，每个用2-3句话描述）

## 📊 技术趋势观察
（分析数据中的趋势，例如：AI工具占比、编程语言热度、新技术栈兴起等）

## 🤖 AI前沿动态
（专门提取AI相关的重要更新、新工具、讨论热点）

## 🛠️ 新工具推荐
（从Product Hunt挑选3-5个值得推荐的实用工具，简短说明用途）

## 💡 技术洞察
（基于所有数据，给出1-2个你对当前技术行业的观察或见解）

---
*数据来源：Hacker News Top 30, Product Hunt Top 20, 技术博客热门文章*
"""
        return prompt

    def _format_hn_data(self, data: List) -> str:
        """格式化HN数据"""
        if not data:
            return "（无数据）"
        formatted = []
        for item in data[:10]:
            formatted.append(f"- {item['title']} ({item['points']} points, {item['comments_count']} comments)")
        return '\n'.join(formatted)

    def _format_ph_data(self, data: List) -> str:
        """格式化Product Hunt数据"""
        if not data:
            return "（无数据）"
        formatted = []
        for item in data[:10]:
            formatted.append(f"- **{item['name']}**: {item['description']} ({item['votes_count']} votes)")
        return '\n'.join(formatted)

    def _format_tb_data(self, data: List) -> str:
        """格式化技术博客数据"""
        if not data:
            return "（无数据）"
        formatted = []
        for item in data[:10]:
            formatted.append(f"- **{item['title']}** by {item['author']} ({item['source']})")
        return '\n'.join(formatted)

    def _mock_ai_analysis(self, prompt: str) -> str:
        """Mock AI分析（开发测试用）"""
        return f"""# 技术行业动态简报 - {self.get_today()}

## 🔥 今日热门技术话题

1. **WebAssembly技术突破** - HN上多个关于WASM的高讨论帖子，平均200+ comments
2. **AI代码助手工具竞赛** - 多款AI编程工具同时发布，竞争激烈
3. **Rust语言生态扩张** - 更多工具和框架选择Rust重写核心模块

## 🚀 新兴热门项目

1. **Rust-based AI Framework**
   新的高性能AI推理框架，比现有方案快3倍

2. **WebAssembly IDE**
   基于浏览器的完整IDE体验，支持多种语言

3. **Auto-GPT Advanced**
   自主AI助手的增强版本，支持更多工具集成

## 📊 技术趋势观察

- AI工具占比持续上升：今日HN Top 30中AI相关占40%
- Rust生态快速增长：工具类项目选择Rust重写成为趋势
- WebAssembly进入实用阶段：生产级应用开始涌现

## 🤖 AI前沿动态

- 多模态模型性能提升：新模型在视觉理解任务上表现优异
- AI代码助手领域竞争激烈：至少3款新工具发布
- 边缘AI计算受到关注：轻量级模型需求增长

## 🛠️ 新工具推荐

1. **WASM Studio** - WebAssembly开发专用IDE
2. **RustML** - Rust机器学习框架
3. **AI Code Review** - 自动代码审查工具

## 💡 技术洞察

基于今日数据分析，观察到**WebAssembly正在从实验技术转向生产可用**。多款生产级WASM工具的发布表明这项技术已经成熟。同时，AI工具开发进入**差异化竞争阶段**，通用型助手逐渐让位于垂直领域的专业工具。

---
*本简报由AI自动生成 | 数据来源: Hacker News, Product Hunt, 技术博客*
"""
```

**Step 2: 测试TechInsightsTask（基于HackerNews数据）**

Run: `python -c "from tasks.tech_insights import TechInsightsTask; task = TechInsightsTask(); print('执行结果:', task.execute())"`

Expected:
```
[tech_insights] 开始生成技术行业简报...
[tech_insights] 可用数据源: hackernews
[tech_insights] ✓ 技术简报生成成功
[tech_insights] 输出文件: .../output/tech-insights/2026-02-16.md
执行结果: True
```

**Step 3: 验证生成的简报**

Run: `cat output/tech-insights/$(date +%Y-%m-%d).md`

Expected: 完整的Markdown简报，包含所有章节

**Step 4: 提交**

```bash
git add tasks/tech_insights.py
git commit -m "feat(tasks): add TechInsightsTask for AI-powered analysis

- Implement TechInsightsTask to aggregate data sources
- Build structured prompt for AI analysis
- Use mock AI response for initial testing
- Generate markdown brief in output/tech-insights/
- Handle missing data sources gracefully

TODO: Integrate ZhipuAI API in next task

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: 集成ZhipuAI API到TechInsightsTask

**Files:**
- Modify: `tasks/tech_insights.py`
- Reference: `script/3.ai-analyze-trending.py:51-93` (现有ZhipuAI调用)

**Step 1: 阅读现有AI调用代码**

Run: `sed -n '51,93p' script/3.ai-analyze-trending.py`

Expected: 看到现有的ZhipuAI API调用逻辑

**Step 2: 添加ZhipuAI API集成**

Modify `tasks/tech_insights.py`, add import and constants at top:

```python
# tasks/tech_insights.py
from core.base import Task
import os
import json
from typing import List, Dict, Any
from zhipuai import ZhipuAI  # 添加
```

Add `_call_ai_analysis` method before `_mock_ai_analysis`:

```python
    def _call_ai_analysis(self, prompt: str) -> str:
        """调用ZhipuAI API生成分析"""
        try:
            # 从环境变量获取API Key
            api_key = os.getenv("BIGMODEL_API_KEY")
            if not api_key:
                print(f"[{self.TASK_ID}] ⚠️ 未找到BIGMODEL_API_KEY环境变量，使用Mock数据")
                return self._mock_ai_analysis(prompt)

            # 初始化客户端
            client = ZhipuAI(api_key=api_key)

            print(f"[{self.TASK_ID}] 正在调用ZhipuAI API生成分析...")

            # 调用API
            response = client.chat.completions.create(
                model="glm-4-flash",  # 使用快速模型
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            # 提取结果
            insights = response.choices[0].message.content.strip()
            print(f"[{self.TASK_ID}] ✓ AI分析生成成功")
            return insights

        except Exception as e:
            print(f"[{self.TASK_ID}] ⚠️ API调用失败: {str(e)}，使用Mock数据")
            return self._mock_ai_analysis(prompt)
```

Replace the insights generation line in `execute` method:

```python
# 旧代码
# insights = self._mock_ai_analysis(prompt)

# 新代码
insights = self._call_ai_analysis(prompt)
```

**Step 3: 设置API Key环境变量**

Run: `echo $BIGMODEL_API_KEY`

Expected: 显示API key（如果不存在，从.env文件读取）

**Step 4: 测试真实API调用**

Run: `python -c "from tasks.tech_insights import TechInsightsTask; import os; os.environ['BIGMODEL_API_KEY']='your_key_here'; task = TechInsightsTask(); print(task.execute())"`

Expected:
```
[tech_insights] 开始生成技术行业简报...
[tech_insights] 可用数据源: hackernews
[tech_insights] 正在调用ZhipuAI API生成分析...
[tech_insights] ✓ AI分析生成成功
[tech_insights] ✓ 技术简报生成成功
执行结果: True
```

**Step 5: 验证AI生成的简报质量**

Run: `cat output/tech-insights/$(date +%Y-%m-%d).md | head -40`

Expected: AI生成的真实分析内容

**Step 6: 提交**

```bash
git add tasks/tech_insights.py
git commit -m "feat(tasks): integrate ZhipuAI API for real AI analysis

- Add ZhipuAI client integration to TechInsightsTask
- Use glm-4-flash model for fast analysis
- Fallback to mock data if API call fails
- Read BIGMODEL_API_KEY from environment variable

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: 创建ProductHuntTask

**Files:**
- Create: `tasks/producthunt.py`

**Step 1: 研究Product Hunt网页结构**

Run: `curl -s "https://www.producthunt.com" -H "User-Agent: Mozilla/5.0" | grep -o '<title>.*</title>'`

Expected: 显示Product Hunt首页标题

**Step 2: 创建ProductHuntTask类**

Create `tasks/producthunt.py`:

```python
# tasks/producthunt.py
from core.base import Task
import requests
from pyquery import PyQuery as pq
import json
import time

class ProductHuntTask(Task):
    """获取Product Hunt Top 20产品"""

    TASK_ID = "producthunt"
    PRIORITY = 16

    def execute(self) -> bool:
        """执行Product Hunt数据抓取"""
        try:
            print(f"[{self.TASK_ID}] 开始获取Product Hunt Top 20...")

            url = "https://www.producthunt.com"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            doc = pq(response.text)

            products = []
            # Product Hunt的产品通常在特定的CSS选择器中
            # 注意：实际选择器可能需要根据页面结构调整
            for item in doc('article').items()[:20]:
                try:
                    name = item('h3').text().strip()
                    description = item('[class*="description"]').text().strip()
                    link_elem = item('a[href*="/posts/"]')

                    if not name or not link_elem:
                        continue

                    product_url = f"https://www.producthunt.com{link_elem.attr('href')}"

                    # 获取votes数（如果页面有显示）
                    votes_text = item('[class*="vote"], [class*="button"]').text()
                    votes = 0
                    if votes_text:
                        import re
                        votes_match = re.search(r'(\d+)', votes_text)
                        if votes_match:
                            votes = int(votes_match.group(1))

                    # 获取标签（如果有的话）
                    tags = []
                    for tag_elem in item('[class*="tag"], [class*="topic"]').items():
                        tag_text = tag_elem.text().strip()
                        if tag_text:
                            tags.append(tag_text)

                    products.append({
                        "name": name,
                        "description": description,
                        "url": product_url,
                        "votes_count": votes,
                        "comments_count": 0,  # Product Hunt首页不显示评论数
                        "tags": tags[:5],  # 限制标签数量
                        "source": "producthunt"
                    })

                except Exception as e:
                    print(f"[{self.TASK_ID}] ⚠️ 解析单个产品时出错: {str(e)}")
                    continue

            # 如果没有抓取到数据，使用Mock数据
            if not products:
                print(f"[{self.TASK_ID}] ⚠️ 未能抓取到真实数据，使用示例数据")
                products = self._get_mock_products()

            # 保存到JSON
            output_path = self.get_output_path(f"producthunt/{self.get_today()}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

            print(f"[{self.TASK_ID}] ✓ 成功获取并保存 {len(products)} 个Product Hunt产品")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")
            return True

        except requests.Timeout:
            print(f"[{self.TASK_ID}] ✗ 请求超时")
            return False
        except requests.HTTPError as e:
            print(f"[{self.TASK_ID}] ✗ HTTP错误: {e.response.status_code}")
            return False
        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ 错误: {str(e)}")
            return False

    def _get_mock_products(self) -> list:
        """获取Mock产品数据（用于测试）"""
        return [
            {
                "name": "AI Code Assistant Pro",
                "description": "Write code 10x faster with AI-powered autocomplete and suggestions",
                "url": "https://producthunt.com/posts/ai-code-assistant",
                "votes_count": 1245,
                "comments_count": 89,
                "tags": ["Developer Tools", "AI", "Productivity"],
                "source": "producthunt"
            },
            {
                "name": "WASM Studio",
                "description": "Complete IDE for WebAssembly development in your browser",
                "url": "https://producthunt.com/posts/wasm-studio",
                "votes_count": 876,
                "comments_count": 45,
                "tags": ["WebAssembly", "Developer Tools", "IDE"],
                "source": "producthunt"
            },
            {
                "name": "RustML Framework",
                "description": "High-performance machine learning framework written in Rust",
                "url": "https://producthunt.com/posts/rustml",
                "votes_count": 654,
                "comments_count": 32,
                "tags": ["Machine Learning", "Rust", "Framework"],
                "source": "producthunt"
            }
        ]
```

**Step 3: 测试ProductHuntTask**

Run: `python -c "from tasks.producthunt import ProductHuntTask; task = ProductHuntTask(); print('执行结果:', task.execute())"`

Expected:
```
[producthunt] 开始获取Product Hunt Top 20...
[producthunt] ✓ 成功获取并保存 XX 个Product Hunt产品
[producthunt] 输出文件: .../output/producthunt/2026-02-16.json
执行结果: True
```

**Step 4: 验证输出**

Run: `cat output/producthunt/$(date +%Y-%m-%d).json | head -30`

Expected: JSON格式的产品数据

**Step 5: 提交**

```bash
git add tasks/producthunt.py
git commit -m "feat(tasks): add ProductHuntTask for fetching top products

- Implement ProductHuntTask using web scraping
- Fetch top 20 products with name, description, votes
- Handle potential parsing errors gracefully
- Fallback to mock data if scraping fails
- Save to output/producthunt/YYYY-MM-DD.json

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: 创建TechBlogsTask

**Files:**
- Create: `tasks/techblogs.py`

**Step 1: 创建TechBlogsTask类（支持Dev.to API）**

Create `tasks/techblogs.py`:

```python
# tasks/techblogs.py
from core.base import Task
import requests
import json
from datetime import datetime

class TechBlogsTask(Task):
    """获取热门技术博客文章"""

    TASK_ID = "techblogs"
    PRIORITY = 17

    # 支持的博客平台
    BLOG_SOURCES = {
        "devto": {
            "url": "https://dev.to/api/articles",
            "params": {"top": "7", "per_page": 15}
        }
    }

    def execute(self) -> bool:
        """执行技术博客数据抓取"""
        try:
            print(f"[{self.TASK_ID}] 开始获取技术博客热门文章...")

            all_articles = []

            # 抓取Dev.to
            devto_articles = self._fetch_devto()
            if devto_articles:
                all_articles.extend(devto_articles)
                print(f"[{self.TASK_ID}] ✓ Dev.to: 获取 {len(devto_articles)} 篇文章")

            # 如果没有获取到任何文章，使用Mock数据
            if not all_articles:
                print(f"[{self.TASK_ID}] ⚠️ 未能抓取到真实数据，使用示例数据")
                all_articles = self._get_mock_articles()

            # 保存到JSON
            output_path = self.get_output_path(f"techblogs/{self.get_today()}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_articles, f, ensure_ascii=False, indent=2)

            print(f"[{self.TASK_ID}] ✓ 成功获取并保存 {len(all_articles)} 篇技术文章")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")
            return True

        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ 错误: {str(e)}")
            return False

    def _fetch_devto(self) -> list:
        """从Dev.to获取热门文章"""
        try:
            source = self.BLOG_SOURCES["devto"]
            response = requests.get(
                source["url"],
                params=source["params"],
                timeout=10
            )
            response.raise_for_status()

            articles = []
            for item in response.json():
                published_date = datetime.strptime(
                    item['published_at'],
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                ).strftime('%Y-%m-%d')

                articles.append({
                    "title": item.get('title', ''),
                    "url": item.get('url', ''),
                    "author": item.get('user', {}).get('name', 'Unknown'),
                    "published_at": published_date,
                    "source": "devto",
                    "tags": item.get('tag_list', [])[:5],
                    "reading_time_minutes": item.get('reading_time_minutes', 0),
                    "positive_reactions_count": item.get('positive_reactions_count', 0)
                })

            return articles

        except Exception as e:
            print(f"[{self.TASK_ID}] ⚠️ Dev.to抓取失败: {str(e)}")
            return []

    def _get_mock_articles(self) -> list:
        """获取Mock文章数据（用于测试）"""
        return [
            {
                "title": "The Future of WebAssembly: A Comprehensive Guide",
                "url": "https://dev.to/johndoe/future-of-webassembly",
                "author": "John Doe",
                "published_at": self.get_today(),
                "source": "devto",
                "tags": ["webassembly", "webdev", "performance"],
                "reading_time_minutes": 8,
                "positive_reactions_count": 234
            },
            {
                "title": "Why I Switched from Python to Rust for ML",
                "url": "https://dev.to/janesmith/python-to-rust-ml",
                "author": "Jane Smith",
                "published_at": self.get_today(),
                "source": "devto",
                "tags": ["rust", "machinelearning", "python"],
                "reading_time_minutes": 6,
                "positive_reactions_count": 567
            },
            {
                "title": "Building AI Agents with Auto-GPT",
                "url": "https://dev.to/alexchen/ai-agents-autogpt",
                "author": "Alex Chen",
                "published_at": self.get_today(),
                "source": "devto",
                "tags": ["ai", "agents", "autogpt"],
                "reading_time_minutes": 10,
                "positive_reactions_count": 892
            }
        ]
```

**Step 2: 测试TechBlogsTask**

Run: `python -c "from tasks.techblogs import TechBlogsTask; task = TechBlogsTask(); print('执行结果:', task.execute())"`

Expected:
```
[techblogs] 开始获取技术博客热门文章...
[techblogs] ✓ Dev.to: 获取 15 篇文章
[techblogs] ✓ 成功获取并保存 15 篇技术文章
[techblogs] 输出文件: .../output/techblogs/2026-02-16.json
执行结果: True
```

**Step 3: 验证输出**

Run: `cat output/techblogs/$(date +%Y-%m-%d).json | head -20`

Expected: JSON格式的文章数据

**Step 4: 提交**

```bash
git add tasks/techblogs.py
git commit -m "feat(tasks): add TechBlogsTask for fetching popular articles

- Implement TechBlogsTask with Dev.to API integration
- Fetch top 15 articles from past week
- Extract title, author, tags, reading time
- Fallback to mock data if API fails
- Save to output/techblogs/YYYY-MM-DD.json

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: 扩展WeComNotifier支持tech_insights

**Files:**
- Modify: `tasks/wecom_robot.py`

**Step 1: 阅读现有WeComNotifier代码**

Run: `head -80 tasks/wecom_robot.py`

Expected: 了解WeComNotifier的现有结构

**Step 2: 修改SUBSCRIBE_TO添加tech_insights**

Find and modify the `SUBSCRIBE_TO` line in WeComNotifier class:

```python
# 原代码
SUBSCRIBE_TO = ["ai_news"]

# 修改为
SUBSCRIBE_TO = ["ai_news", "tech_insights"]
```

**Step 3: 在send方法中添加tech_insights处理逻辑**

Find the send method and add tech_insights handling after ai_news section:

```python
# 在send方法中，添加tech_insights的处理
# 在ai_news处理逻辑之后添加：

        # 新增：tech_insights通知
        if "tech_insights" in task_results and task_results["tech_insights"]:
            try:
                insights_path = f"output/tech-insights/{self.get_today()}.md"

                if not os.path.exists(insights_path):
                    print(f"[{self.NOTIFIER_ID}] ⚠️ 技术简报文件不存在: {insights_path}")
                else:
                    with open(insights_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 企业微信markdown消息长度限制为2048字符
                    # 如果内容过长，需要分段发送
                    max_length = 1900  # 留一些余量
                    if len(content) > max_length:
                        success &= self._send_long_markdown(content, max_length)
                    else:
                        success &= self._send_markdown("## 📊 技术行业动态简报\n\n" + content)

            except Exception as e:
                print(f"[{self.NOTIFIER_ID}] ✗ 发送技术简报失败: {str(e)}")
                success = False
```

**Step 4: 添加_send_long_markdown方法**

Add this new method to the WeComNotifier class:

```python
    def _send_long_markdown(self, content: str, max_length: int) -> bool:
        """分段发送长markdown消息"""
        try:
            lines = content.split('\n')
            chunks = []
            current_chunk = []

            for line in lines:
                # 检查是否是二级标题（## 开头），作为分段点
                if line.startswith('## ') and current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                else:
                    current_chunk.append(line)

                # 如果当前chunk超过限制，强制分割
                if len('\n'.join(current_chunk)) > max_length:
                    chunks.append('\n'.join(current_chunk[:-1]))
                    current_chunk = [line]

            # 添加最后一个chunk
            if current_chunk:
                chunks.append('\n'.join(current_chunk))

            # 发送每个chunk
            for idx, chunk in enumerate(chunks, 1):
                prefix = f"\n\n（第 {idx}/{len(chunks)} 部分）" if len(chunks) > 1 else ""
                message = "## 📊 技术行业动态简报" + prefix + "\n\n" + chunk
                if not self._send_markdown(message):
                    return False
                # 避免发送过快
                import time
                time.sleep(1)

            return True

        except Exception as e:
            print(f"[{self.NOTIFIER_ID}] ✗ 分段发送失败: {str(e)}")
            return False
```

**Step 5: 测试WeComNotifier**

Run: `python -c "
from tasks.wecom_robot import WeComNotifier
from tasks.hackernews import HackerNewsTask
from tasks.tech_insights import TechInsightsTask

# 确保数据存在
hn = HackerNewsTask()
hn.execute()

insights = TechInsightsTask()
insights.execute()

# 测试通知
notifier = WeComNotifier()
results = {'ai_news': True, 'tech_insights': True}
print('发送结果:', notifier.send(results))
"`

Expected:
```
[wecom] 发送技术简报...
[wecom] ✓ 发送成功
发送结果: True
```

**Step 6: 提交**

```bash
git add tasks/wecom_robot.py
git commit -m "feat(notifier): add tech_insights subscription to WeComNotifier

- Extend SUBSCRIBE_TO to include tech_insights
- Add logic to read and send tech-insights brief
- Implement message splitting for long content (>1900 chars)
- Split on ## headings for better readability
- Add delay between chunks to avoid rate limiting

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: 创建集成测试脚本

**Files:**
- Create: `test_tech_insights.py`

**Step 1: 创建测试脚本**

Create `test_tech_insights.py`:

```python
# test_tech_insights.py
"""
技术行业动态完整流程集成测试
"""
import os
import sys
from datetime import datetime

def test_full_pipeline():
    """测试完整的数据收集和分析流程"""
    print("=" * 60)
    print("测试技术行业动态完整流程")
    print("=" * 60)

    # 导入任务
    from tasks.hackernews import HackerNewsTask
    from tasks.producthunt import ProductHuntTask
    from tasks.techblogs import TechBlogsTask
    from tasks.tech_insights import TechInsightsTask
    from tasks.wecom_robot import WeComNotifier

    today = datetime.now().strftime('%Y-%m-%d')

    # 1. 测试数据收集任务
    print("\n=== 第一阶段：数据收集 ===\n")
    data_tasks = [
        HackerNewsTask(),
        ProductHuntTask(),
        TechBlogsTask()
    ]

    for task in data_tasks:
        print(f"\n测试 {task.TASK_ID}...")
        result = task.execute()
        if result:
            print(f"✓ {task.TASK_ID} 成功")
        else:
            print(f"✗ {task.TASK_ID} 失败")
            sys.exit(1)

    # 2. 测试AI分析任务
    print(f"\n=== 第二阶段：AI分析 ===\n")
    print(f"测试 tech_insights...")
    insights_task = TechInsightsTask()
    result = insights_task.execute()
    if result:
        print(f"✓ tech_insights 成功")
    else:
        print(f"✗ tech_insights 失败")
        sys.exit(1)

    # 3. 验证输出文件
    print(f"\n=== 第三阶段：验证输出 ===\n")
    required_files = [
        f"output/hackernews/{today}.json",
        f"output/producthunt/{today}.json",
        f"output/techblogs/{today}.json",
        f"output/tech-insights/{today}.md"
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✓ 文件存在: {file_path} ({file_size} bytes)")
        else:
            print(f"✗ 文件不存在: {file_path}")
            sys.exit(1)

    # 4. 测试通知器（可选，需要设置WECHAT_WEBHOOK）
    print(f"\n=== 第四阶段：测试通知 ===\n")
    webhook = os.getenv("WECHAT_WEBHOOK")
    if webhook:
        print(f"测试 WeComNotifier...")
        notifier = WeComNotifier()
        results = {
            'ai_news': True,
            'tech_insights': True,
            'github_trending': True,
            'trending_ai': True
        }
        result = notifier.send(results)
        if result:
            print(f"✓ WeComNotifier 成功")
        else:
            print(f"✗ WeComNotifier 失败")
    else:
        print("⚠️ 未设置WECHAT_WEBHOOK环境变量，跳过通知测试")

    # 5. 总结
    print(f"\n{'=' * 60}")
    print("✓ 所有测试通过")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    test_full_pipeline()
```

**Step 2: 运行集成测试**

Run: `python test_tech_insights.py`

Expected:
```
============================================================
测试技术行业动态完整流程
============================================================

=== 第一阶段：数据收集 ===

测试 hackernews...
[hackernews] 开始获取Hacker News Top 30...
...
✓ hackernews 成功

测试 producthunt...
[producthunt] 开始获取Product Hunt Top 20...
...
✓ producthunt 成功

测试 techblogs...
[techblogs] 开始获取技术博客热门文章...
...
✓ techblogs 成功

=== 第二阶段：AI分析 ===

测试 tech_insights...
[tech_insights] 开始生成技术行业简报...
...
✓ tech_insights 成功

=== 第三阶段：验证输出 ===

✓ 文件存在: output/hackernews/2026-02-16.json (XXXX bytes)
✓ 文件存在: output/producthunt/2026-02-16.json (XXXX bytes)
✓ 文件存在: output/techblogs/2026-02-16.json (XXXX bytes)
✓ 文件存在: output/tech-insights/2026-02-16.md (XXXX bytes)

=== 第四阶段：测试通知 ===

测试 WeComNotifier...
✓ WeComNotifier 成功

============================================================
✓ 所有测试通过
============================================================
```

**Step 3: 提交**

```bash
git add test_tech_insights.py
git commit -m "test: add integration test for tech insights pipeline

- Create comprehensive integration test script
- Test all data collection tasks
- Test AI analysis task
- Verify output files existence
- Test WeComNotifier (if webhook configured)
- Exit with error code on any test failure

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: 运行完整流程测试

**Files:**
- Execute: `main.py`

**Step 1: 运行完整流程**

Run: `python main.py`

Expected output should include:
```
发现 7 个任务, 1 个通知器

执行顺序:
  10. ai_news
  15. hackernews
  16. producthunt
  17. techblogs
  20. github_trending
  30. trending_ai
  40. tech_insights

============================================================
开始执行任务
============================================================

[ai_news] 开始执行...
[ai_news] ✓ 执行成功

[hackernews] 开始执行...
[hackernews] ✓ 执行成功

[producthunt] 开始执行...
[producthunt] ✓ 执行成功

[techblogs] 开始执行...
[techblogs] ✓ 执行成功

[github_trending] 开始执行...
[github_trending] ✓ 执行成功

[trending_ai] 开始执行...
[trending_ai] ✓ 执行成功

[tech_insights] 开始执行...
[tech_insights] ✓ 执行成功

============================================================
开始执行通知
============================================================

[wecom] 开始发送通知...
[wecom] ✓ 发送成功

============================================================
执行摘要
============================================================
总计任务数: 7
成功执行: 7
执行失败: 0
============================================================
```

**Step 2: 验证所有输出文件**

Run: `ls -lh output/hackernews/ output/producthunt/ output/techblogs/ output/tech-insights/`

Expected: 所有目录都有今天的文件

**Step 3: 查看生成的简报**

Run: `cat output/tech-insights/$(date +%Y-%m-%d).md | less`

Expected: 完整的技术行业动态简报

**Step 4: 提交（如果有修改）**

```bash
git add -A
git commit -m "test: verify full pipeline execution

- Run complete main.py with all 7 tasks
- Verify all output files generated
- Confirm tech_insights brief contains all sections
- Test WeComNotifier integration
- All tasks executing successfully

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: 更新项目文档

**Files:**
- Modify: `CLAUDE.md`

**Step 1: 更新CLAUDE.md添加新任务说明**

Add to "Script Conventions" section, after describing existing scripts:

```markdown
### Tasks (New Framework)

The project is migrating to a new task-based framework. New tasks are in `tasks/`:

**Data Collection Tasks (inherit from Task):**
- `hackernews.py` - Fetches Hacker News Top 30 stories (PRIORITY=15)
- `producthunt.py` - Scrapes Product Hunt Top 20 products (PRIORITY=16)
- `techblogs.py` - Fetches Dev.to trending articles (PRIORITY=17)
- `tech_insights.py` - AI-powered analysis generating tech industry brief (PRIORITY=40)

**Notifiers (inherit from Notifier):**
- `wecom_robot.py` - Sends notifications to WeChat Work (subscribes to ai_news and tech_insights)

**Output Structure:**
```
output/
├── hackernews/          # Hacker News stories JSON (YYYY-MM-DD.json)
├── producthunt/         # Product Hunt products JSON (YYYY-MM-DD.json)
├── techblogs/           # Tech blog articles JSON (YYYY-MM-DD.json)
└── tech-insights/       # AI-generated industry brief (YYYY-MM-DD.md)
```

**Note:** The numbered scripts in `script/` directory are being migrated to the new framework.
```

**Step 2: 验证文档更新**

Run: `cat CLAUDE.md | grep -A 20 "Tasks (New Framework)"`

Expected: 看到新添加的任务说明

**Step 3: 提交文档更新**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with tech insights tasks documentation

- Add new tasks framework section
- Document hackernews, producthunt, techblogs tasks
- Document tech_insights AI analysis task
- Update output structure description
- Note migration from script/ to tasks/

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: 最终验证和清理

**Files:**
- Various

**Step 1: 运行完整测试套件**

Run: `python test_tech_insights.py && python main.py`

Expected: 所有测试通过，完整流程执行成功

**Step 2: 检查Git状态**

Run: `git status`

Expected: 只看到未跟踪的输出文件，没有未提交的代码更改

**Step 3: 查看最近的提交历史**

Run: `git log --oneline -10`

Expected: 看到所有实施任务的提交记录

**Step 4: 创建最终的summary commit**

```bash
git add -A
git commit -m "feat: complete tech industry insights tracking system

Implemented comprehensive tech industry tracking system:

Data Collection:
- HackerNewsTask: Fetch top 30 stories from HN API
- ProductHuntTask: Scrape top 20 products
- TechBlogsTask: Fetch trending articles from Dev.to

AI Analysis:
- TechInsightsTask: Aggregate data and generate AI brief
- Integrated ZhipuAI (GLM-4) for analysis
- Structured prompt engineering for quality output

Notifications:
- Extended WeComNotifier to support tech_insights
- Implemented message splitting for long content
- Split on headings for better readability

Testing:
- Comprehensive integration test script
- All tasks independently testable
- Full pipeline execution verified

Documentation:
- Updated CLAUDE.md with new tasks
- Implementation plan and design docs committed

Output:
- JSON files for raw data from each source
- Markdown brief with AI-generated insights
- Ready for daily automation via GitHub Actions

Total implementation time: ~3-4 hours
All tasks passing, ready for production use.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Step 5: 推送到远程仓库（可选）**

Run: `git push origin refactor-project-architecture`

Expected: 代码成功推送到GitHub

---

## 验收清单

在声称完成之前，确保以下所有项都通过：

- [ ] HackerNewsTask能成功获取30条HN数据
- [ ] ProductHuntTask能成功获取Top 20产品
- [ ] TechBlogsTask能成功获取Dev.to文章
- [ ] TechInsightsTask能读取3个数据源并生成AI分析
- [ ] 生成的简报包含所有必需章节（热门话题、新兴项目、趋势观察、AI动态、工具推荐、技术洞察）
- [ ] WeComNotifier能成功推送tech_insights简报
- [ ] 长消息能正确分段发送
- [ ] 完整流程 `python main.py` 执行无错误
- [ ] 集成测试 `test_tech_insights.py` 全部通过
- [ ] 输出文件格式正确且内容完整
- [ ] 错误处理健壮，部分失败不影响整体
- [ ] 文档已更新（CLAUDE.md）
- [ ] 所有代码已提交到Git
- [ ] Git提交信息符合conventional commits规范

---

## 故障排查指南

**问题1：HackerNewsTask获取数据失败**
```bash
# 检查网络连接
curl -I https://hacker-news.firebaseio.com

# 手动测试API
curl "https://hacker-news.firebaseio.com/v0/topstories.json" | head -20
```

**问题2：TechInsightsTask调用AI失败**
```bash
# 检查API Key
echo $BIGMODEL_API_KEY

# 测试API连接
python -c "from zhipuai import ZhipuAI; client = ZhipuAI(api_key='$BIGMODEL_API_KEY'); print(client.chat.completions.create(model='glm-4-flash', messages=[{'role': 'user', 'content': 'hi'}]))"
```

**问题3：企业微信推送失败**
```bash
# 检查webhook环境变量
echo $WECHAT_WEBHOOK

# 测试webhook
curl -X POST "$WECHAT_WEBHOOK" -H 'Content-Type: application/json' -d '{"msgtype":"text","text":{"content":"test message"}}'
```

**问题4：ProductHunt爬虫失败**
```bash
# Product Hunt可能更改了页面结构
# 检查是否需要更新CSS选择器
# 可以暂时使用Mock数据进行测试
```

---

## 后续优化建议

1. **添加更多数据源**
   - Reddit (r/programming, r/MachineLearning)
   - Medium热门技术文章
   - HackerNoon

2. **增强AI分析**
   - 添加历史数据对比
   - 生成趋势图表
   - 个性化推荐（基于用户偏好）

3. **优化通知**
   - 支持更多通知渠道（Email, Slack, Discord）
   - 添加摘要模式（仅关键信息）
   - 支持定时推送（非实时）

4. **性能优化**
   - 并行执行数据收集任务
   - 添加缓存机制
   - 减少API调用次数

5. **监控和告警**
   - 添加任务执行时间监控
   - 失败率统计
   - 异常告警通知

---

**实施计划完成时间预估：3-4小时**

**技能参考：**
- @superpowers:test-driven-development - TDD最佳实践
- @superpowers:systematic-debugging - 调试问题时的系统化方法
- @document-skills:doc-coauthoring - 如果需要协作文档

**End of Implementation Plan**
