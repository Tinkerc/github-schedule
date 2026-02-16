# 技术行业动态跟踪系统设计文档

**Date:** 2026-02-16
**Author:** Claude Code
**Status:** Design Approved

## Overview

### Goal
构建一个技术行业动态跟踪系统，通过每日自动化收集多源数据（Hacker News、Product Hunt、技术博客），利用AI分析生成技术趋势简报，并通过企业微信推送。

### User Requirements
- 关注维度：**开源项目动态** + **技术趋势跟踪**
- 数据来源：Hacker News、Product Hunt、技术博客聚合（Dev.to、Medium等）
- 处理方式：保存原始数据 + AI分析生成简报
- 通知方式：企业微信推送
- 内容类型：新兴热门项目、技术趋势变化、AI相关动态、新工具发布

### Solution
采用**独立任务方案**（方案1），为每个数据源创建独立的Task类，通过统一的AI分析任务生成技术行业简报。

### Key Benefits
- ✅ 符合现有Task/Notifier架构
- ✅ 每个数据源独立，易于测试和调试
- ✅ 可以单独禁用某个数据源（修改PRIORITY）
- ✅ AI分析可综合所有数据源，发现跨平台趋势
- ✅ 易于扩展新数据源

---

## Architecture

### Directory Structure

```
github-schedule/
├── core/                       # 现有核心框架
│   ├── base.py                 # Task和Notifier基类
│   └── runner.py               # 任务发现和执行
├── tasks/
│   ├── ai_news.py             # PRIORITY=10 (现有)
│   ├── hackernews.py          # PRIORITY=15 (新增)
│   ├── producthunt.py         # PRIORITY=16 (新增)
│   ├── techblogs.py           # PRIORITY=17 (新增)
│   ├── github_trending.py     # PRIORITY=20 (现有)
│   ├── trending_ai.py         # PRIORITY=30 (现有)
│   ├── tech_insights.py       # PRIORITY=40 (新增，AI分析)
│   └── wecom_robot.py         # Notifier (现有，需扩展)
├── output/
│   ├── hackernews/            # YYYY-MM-DD.json
│   ├── producthunt/           # YYYY-MM-DD.json
│   ├── techblogs/             # YYYY-MM-DD.json
│   └── tech-insights/         # YYYY-MM-DD.md (AI生成简报)
└── script/                    # 旧系统，迁移后删除
```

### Execution Order

```
1. ai_news (10)                # 现有任务
2. hackernews (15)             # 新增
3. producthunt (16)            # 新增
4. techblogs (17)              # 新增
5. github_trending (20)        # 现有任务
6. trending_ai (30)            # 现有任务
7. tech_insights (40)          # 新增：AI分析
   ↓
WeComNotifier                   # 推送 ai_news + tech_insights
```

---

## Core Components

### 1. HackerNewsTask (tasks/hackernews.py)

**职责：** 每日获取Hacker News Top 30故事

**实现：**
```python
from core.base import Task
import requests
import json
from datetime import datetime

class HackerNewsTask(Task):
    TASK_ID = "hackernews"
    PRIORITY = 15

    def execute(self) -> bool:
        try:
            # 获取Top 30故事IDs
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(url, timeout=10)
            story_ids = response.json()[:30]

            stories = []
            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_resp = requests.get(story_url, timeout=10)
                story_data = story_resp.json()

                stories.append({
                    "title": story_data.get("title"),
                    "url": story_data.get("url"),
                    "points": story_data.get("score", 0),
                    "comments_count": story_data.get("descendants", 0),
                    "posted_at": datetime.fromtimestamp(story_data.get("time", 0)).isoformat(),
                    "source": "hackernews",
                    "hn_id": story_id
                })

            # 保存
            output_path = self.get_output_path(f"hackernews/{self.get_today()}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(stories, f, ensure_ascii=False, indent=2)

            print(f"[{self.TASK_ID}] ✓ 成功获取 {len(stories)} 条Hacker News")
            return True

        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ 错误: {str(e)}")
            return False
```

**输出格式：** `output/hackernews/YYYY-MM-DD.json`
```json
[
  {
    "title": "Show HN: I built...",
    "url": "https://...",
    "points": 245,
    "comments_count": 87,
    "posted_at": "2026-02-16T10:30:00Z",
    "source": "hackernews",
    "hn_id": 12345678
  }
]
```

---

### 2. ProductHuntTask (tasks/producthunt.py)

**职责：** 每日获取Product Hunt Top 20产品

**实现要点：**
- 使用PyQuery或BeautifulSoup抓取
- 处理可能的JavaScript渲染（考虑使用selenium或直接API）
- 提取：name, description, url, votes_count, tags

**输出格式：** `output/producthunt/YYYY-MM-DD.json`
```json
[
  {
    "name": "AI Code Assistant",
    "description": "Write code faster with AI...",
    "url": "https://...",
    "votes_count": 1245,
    "comments_count": 89,
    "tags": ["Developer Tools", "AI"],
    "source": "producthunt"
  }
]
```

---

### 3. TechBlogsTask (tasks/techblogs.py)

**职责：** 获取热门技术博客文章

**支持平台：**
- Dev.to (有API: https://dev.to/api/articles?top=7)
- Medium (RSS或爬虫)
- HackerNoon (RSS)
- 可扩展更多平台

**输出格式：** `output/techblogs/YYYY-MM-DD.json`
```json
[
  {
    "title": "The Future of WebAssembly",
    "url": "https://blog.example.com/...",
    "author": "John Doe",
    "published_at": "2026-02-16",
    "source": "devto",
    "tags": ["WebAssembly", "Web"],
    "reading_time_minutes": 8
  }
]
```

---

### 4. TechInsightsTask (tasks/tech_insights.py)

**职责：** 综合所有数据源，生成AI技术趋势简报

**实现要点：**

```python
from core.base import Task
import os
import json
from typing import List, Dict, Any

class TechInsightsTask(Task):
    TASK_ID = "tech_insights"
    PRIORITY = 40

    def execute(self) -> bool:
        try:
            # 1. 读取所有数据源
            hn_data = self._read_json(f"hackernews/{self.get_today()}.json")
            ph_data = self._read_json(f"producthunt/{self.get_today()}.json")
            tb_data = self._read_json(f"techblogs/{self.get_today()}.json")

            # 检查数据可用性
            available_sources = [
                name for name, data in
                [("hackernews", hn_data), ("producthunt", ph_data), ("techblogs", tb_data)]
                if data is not None
            ]

            if not available_sources:
                print(f"[{self.TASK_ID}] ✗ 所有数据源均不可用")
                return False

            print(f"[{self.TASK_ID}] 可用数据源: {', '.join(available_sources)}")

            # 2. 构建AI提示词
            prompt = self._build_prompt(hn_data, ph_data, tb_data)

            # 3. 调用ZhipuAI API（复用trending_ai逻辑）
            insights = self._call_ai_analysis(prompt)

            # 4. 保存简报
            output_path = self.get_output_path(f"tech-insights/{self.get_today()}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)

            print(f"[{self.TASK_ID}] ✓ 技术简报生成成功")
            return True

        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ 错误: {str(e)}")
            return False

    def _read_json(self, filepath: str) -> List:
        """读取JSON文件，不存在返回None"""
        full_path = self.get_output_path(filepath)
        if not os.path.exists(full_path):
            print(f"[{self.TASK_ID}] ⚠️  文件不存在: {filepath}")
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
        formatted = []
        for item in data[:10]:
            formatted.append(f"- {item['title']} ({item['points']} points, {item['comments_count']} comments)")
        return '\n'.join(formatted) if formatted else "（无数据）"

    def _format_ph_data(self, data: List) -> str:
        formatted = []
        for item in data[:10]:
            formatted.append(f"- **{item['name']}**: {item['description']} ({item['votes_count']} votes)")
        return '\n'.join(formatted) if formatted else "（无数据）"

    def _format_tb_data(self, data: List) -> str:
        formatted = []
        for item in data[:10]:
            formatted.append(f"- **{item['title']}** by {item['author']} ({item['source']})")
        return '\n'.join(formatted) if formatted else "（无数据）"

    def _call_ai_analysis(self, prompt: str) -> str:
        """调用ZhipuAI API生成分析"""
        # 复用trending_ai中的API调用逻辑
        # 返回生成的markdown文本
        pass
```

**输出格式：** `output/tech-insights/YYYY-MM-DD.md`
```markdown
# 技术行业动态简报 - 2026-02-16

## 🔥 今日热门技术话题
- WebAssembly在各技术平台被广泛讨论...
- AI代码助手工具持续火热...

## 🚀 新兴热门项目
- **Project X** (⭐ 245 stars on HN)
  项目描述...

## 📊 技术趋势观察
- 基于Product Hunt数据，本周AI工具发布数量增长了30%...
- 技术博客中关于Rust的文章占比提升至15%...

## 🤖 AI前沿动态
- 今日Hacker News Top 30中，AI相关话题占40%...

## 🛠️ 新工具推荐
- Tool A: ...
- Tool B: ...

## 💡 技术洞察
- 基于所有数据，观察到一个有趣的趋势...
```

---

### 5. 扩展WeComNotifier (tasks/wecom_robot.py)

**修改：**
```python
class WeComNotifier(Notifier):
    NOTIFIER_ID = "wecom"
    SUBSCRIBE_TO = ["ai_news", "tech_insights"]  # 新增tech_insights

    def send(self, task_results: Dict[str, Any]) -> bool:
        success = True

        # 原有ai_news逻辑...

        # 新增：tech_insights通知
        if "tech_insights" in task_results and task_results["tech_insights"]:
            try:
                insights_path = f"output/tech-insights/{self.get_today()}.md"
                if not os.path.exists(insights_path):
                    print(f"[{self.NOTIFIER_ID}] ⚠️ 技术简报文件不存在")
                    success = False
                else:
                    with open(insights_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 长消息分段发送
                    if len(content) > 2000:
                        success &= self._send_long_message(content)
                    else:
                        success &= self._send_markdown(content)

            except Exception as e:
                print(f"[{self.NOTIFIER_ID}] ✗ 发送技术简报失败: {str(e)}")
                success = False

        return success

    def _send_long_message(self, content: str) -> bool:
        """分段发送长消息"""
        # 按段落分割，每段不超过2000字符
        # 发送多次
        pass
```

---

## Data Flow

```
1. main.py 启动
   ↓
2. TaskRunner.discover()
   - 发现 7 个任务 + 1 个通知器
   ↓
3. TaskRunner.run_tasks() (按PRIORITY顺序执行)
   ↓
   ai_news (10) → 成功
   ↓
   hackernews (15) → 成功
   - 保存: output/hackernews/2026-02-16.json
   ↓
   producthunt (16) → 成功
   - 保存: output/producthunt/2026-02-16.json
   ↓
   techblogs (17) → 成功
   - 保存: output/techblogs/2026-02-16.json
   ↓
   github_trending (20) → 成功
   ↓
   trending_ai (30) → 成功
   ↓
   tech_insights (40) → 成功
   - 读取: 3个JSON文件
   - 调用: ZhipuAI API分析
   - 保存: output/tech-insights/2026-02-16.md
   ↓
4. TaskRunner.run_notifiers()
   - WeComNotifier检查SUBSCRIBE_TO = ["ai_news", "tech_insights"]
   - 读取并推送简报
   ↓
5. 打印统计摘要
   总计任务数: 7
   成功执行: 7
   执行失败: 0
```

---

## Error Handling

### Multi-Level Strategy

**Level 1: Task内部错误处理**
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    # 处理数据...
    return True

except requests.Timeout:
    print(f"[{self.TASK_ID}] ⚠️ 请求超时")
    return False

except requests.HTTPError as e:
    print(f"[{self.TASK_ID}] ⚠️ HTTP错误: {e.response.status_code}")
    return False

except Exception as e:
    print(f"[{self.TASK_ID}] ⚠️ 未知错误: {str(e)}")
    return False
```

**Level 2: TechInsightsTask容错**
- 检查依赖数据是否存在
- 如果所有数据源缺失，跳过执行返回False
- 如果部分数据源可用，基于现有数据生成分析

**Level 3: Notifier容错**
- 文件不存在时打印警告
- 发送失败不影响其他通知
- 长消息自动分段

**Level 4: Runner级别**
- 单个任务失败不影响其他任务
- 统计成功/失败数量
- 最终返回适当的退出码

### Failure Scenarios

**场景1：单个数据源失败**
```
✗ hackernews: 网络超时
✓ producthunt: 成功
✓ techblogs: 成功
✓ tech_insights: 基于producthunt和techblogs生成分析
结果：部分功能可用
```

**场景2：AI分析失败**
```
✓ hackernews: 成功
✓ producthunt: 成功
✓ techblogs: 成功
✗ tech_insights: API调用失败
结果：数据已保存，可手动重试AI分析
```

**场景3：通知失败**
```
✓ 所有任务成功
✗ wecom: webhook发送失败
结果：数据已保存到GitHub，通知失败可接受
```

---

## Testing Strategy

### 1. 单个Task独立测试

```bash
# 测试HackerNewsTask
python -c "from tasks.hackernews import HackerNewsTask; task = HackerNewsTask(); print(task.execute())"

# 测试ProductHuntTask
python -c "from tasks.producthunt import ProductHuntTask; task = ProductHuntTask(); print(task.execute())"

# 测试TechInsightsTask（需先准备数据）
python -c "from tasks.tech_insights import TechInsightsTask; task = TechInsightsTask(); print(task.execute())"
```

### 2. Mock模式（开发调试）

```python
# tasks/hackernews.py
class HackerNewsTask(Task):
    def execute(self) -> bool:
        # 开发模式：使用缓存数据
        if os.getenv('MOCK_MODE') == 'true':
            print(f"[{self.TASK_ID}] 🧪 Mock模式：使用缓存数据")
            mock_data = self._load_mock_data()
            output_path = self.get_output_path(f"hackernews/{self.get_today()}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(mock_data, f, ensure_ascii=False, indent=2)
            return True

        # 生产模式：真实API请求
        # ... 原有逻辑
```

```bash
MOCK_MODE=true python main.py
```

### 3. 集成测试脚本

```python
# test_tech_insights.py
from tasks.hackernews import HackerNewsTask
from tasks.producthunt import ProductHuntTask
from tasks.techblogs import TechBlogsTask
from tasks.tech_insights import TechInsightsTask
import os
from datetime import datetime

def test_full_pipeline():
    """测试完整的数据收集和分析流程"""
    print("=== 测试技术行业动态完整流程 ===\n")

    # 1. 测试数据收集
    tasks = [
        HackerNewsTask(),
        ProductHuntTask(),
        TechBlogsTask()
    ]

    for task in tasks:
        print(f"\n测试 {task.TASK_ID}...")
        result = task.execute()
        assert result == True, f"{task.TASK_ID} 执行失败"
        print(f"✓ {task.TASK_ID} 成功")

    # 2. 测试AI分析
    print(f"\n测试 tech_insights...")
    insights_task = TechInsightsTask()
    result = insights_task.execute()
    assert result == True, "tech_insights 执行失败"
    print(f"✓ tech_insights 成功")

    # 3. 验证输出文件
    today = datetime.now().strftime('%Y-%m-%d')
    required_files = [
        f"output/hackernews/{today}.json",
        f"output/producthunt/{today}.json",
        f"output/techblogs/{today}.json",
        f"output/tech-insights/{today}.md"
    ]

    for file_path in required_files:
        assert os.path.exists(file_path), f"输出文件不存在: {file_path}"
        print(f"✓ 文件存在: {file_path}")

    print("\n=== 所有测试通过 ===")

if __name__ == "__main__":
    test_full_pipeline()
```

### 4. 完整流程测试

```bash
# 运行完整流程
python main.py

# 预期输出：
# 发现 7 个任务, 1 个通知器
# 执行顺序:
#   10. ai_news
#   15. hackernews          ← 新增
#   16. producthunt         ← 新增
#   17. techblogs           ← 新增
#   20. github_trending
#   30. trending_ai
#   40. tech_insights       ← 新增
#
# 执行摘要:
# 总计任务数: 7
# 成功执行: 7
# 执行失败: 0
```

---

## Implementation Plan

### Phase 1: 基础框架 - HackerNewsTask（优先级最高）

**目标：** 验证新数据源的完整流程

**任务清单：**
- [ ] 创建 `tasks/hackernews.py`
- [ ] 实现HackerNewsTask类（继承Task）
- [ ] 使用Hacker News Official API获取Top 30
- [ ] 保存到 `output/hackernews/YYYY-MM-DD.json`
- [ ] 单元测试：独立运行HackerNewsTask

**验收标准：**
- 能成功获取30条HN数据
- JSON格式正确，包含所有必需字段
- 输出文件路径正确

**时间估算：** 30-45分钟

---

### Phase 2: 扩展数据源 - ProductHuntTask & TechBlogsTask

**任务清单：**

**2.1 ProductHuntTask:**
- [ ] 创建 `tasks/producthunt.py`
- [ ] 研究Product Hunt网页结构
- [ ] 实现爬虫逻辑获取Top 20产品
- [ ] 保存到 `output/producthunt/YYYY-MM-DD.json`
- [ ] 独立测试

**2.2 TechBlogsTask:**
- [ ] 创建 `tasks/techblogs.py`
- [ ] 实现Dev.to热门文章抓取（有API）
- [ ] 实现Medium或其他平台抓取
- [ ] 保存到 `output/techblogs/YYYY-MM-DD.json`
- [ ] 独立测试

**验收标准：**
- 两个任务都能独立运行成功
- 数据格式统一（title, url, description等）
- 错误处理完善

**时间估算：** 1-1.5小时

---

### Phase 3: AI分析核心 - TechInsightsTask

**任务清单：**
- [ ] 创建 `tasks/tech_insights.py`
- [ ] 实现数据读取逻辑（从3个JSON文件）
- [ ] 实现Prompt构建函数（_build_prompt）
- [ ] 集成ZhipuAI API调用（复用trending_ai逻辑）
- [ ] 保存分析结果到 `output/tech-insights/YYYY-MM-DD.md`
- [ ] 处理数据源缺失的容错逻辑
- [ ] 端到端测试

**验收标准：**
- 能读取3个数据源并生成简报
- 简报包含所有必需章节
- 格式正确，适合企业微信推送
- 部分数据源缺失时仍能工作

**时间估算：** 45-60分钟

---

### Phase 4: 通知集成 - 扩展WeComNotifier

**任务清单：**
- [ ] 修改 `tasks/wecom_robot.py`
- [ ] 在SUBSCRIBE_TO中添加"tech_insights"
- [ ] 实现tech_insights的处理逻辑
- [ ] 实现长消息分段发送（简报可能超过2000字符）
- [ ] 添加消息格式化（Markdown优化）
- [ ] 测试企业微信推送

**验收标准：**
- WeComNotifier能读取tech_insights输出
- 消息格式正确，支持Markdown
- 长消息能正确分段发送
- 推送成功无错误

**时间估算：** 30分钟

---

### Phase 5: 集成测试与验证

**任务清单：**
- [ ] 创建测试脚本 `test_tech_insights.py`
- [ ] 运行完整流程：`python main.py`
- [ ] 验证所有输出文件生成正确
- [ ] 验证企业微信接收消息
- [ ] 测试错误场景（网络超时、数据缺失等）
- [ ] Mock模式测试

**验收标准：**
- 完整流程执行无错误
- 7个任务 + 1个通知器正常运行
- 输出文件完整且格式正确
- 企业微信成功接收简报

**时间估算：** 30-45分钟

---

### Phase 6: 文档与收尾

**任务清单：**
- [ ] 更新 `CLAUDE.md`（添加新任务说明）
- [ ] 更新 `README.md`（如有）
- [ ] 将设计文档保存到 `docs/plans/`
- [ ] Git提交（使用conventional commits）
- [ ] 清理临时文件

**验收标准：**
- 文档准确反映新架构
- 设计文档已提交
- Git提交信息规范

**时间估算：** 15分钟

---

**总时间估算：3-4小时**

**实施顺序建议（分阶段交付价值）：**
1. **Phase 1** - 快速验证流程，看到HN数据收集结果
2. **Phase 3** - 核心价值，让AI分析跑起来（先用Mock数据）
3. **Phase 2** - 补充真实数据源
4. **Phase 4, 5, 6** - 集成、测试、文档

---

## Future Extensibility

### 添加新数据源

**示例：添加Reddit抓取**

```python
# tasks/reddit.py
from core.base import Task

class RedditTask(Task):
    TASK_ID = "reddit"
    PRIORITY = 18

    def execute(self) -> bool:
        # 使用Reddit API抓取r/programming, r/MachineLearning
        # 保存到 output/reddit/YYYY-MM-DD.json
        return True
```

然后在TechInsightsTask中读取reddit数据并加入分析。

### 添加新的通知渠道

**示例：邮件通知**

```python
# tasks/email_notifier.py
from core.base import Notifier

class EmailNotifier(Notifier):
    NOTIFIER_ID = "email"
    SUBSCRIBE_TO = ["tech_insights"]

    def send(self, task_results: Dict[str, Any]) -> bool:
        # 发送邮件简报
        return True
```

---

## Success Criteria

- [x] 所有现有功能保持正常
- [x] 3个新数据源Task能独立运行
- [x] TechInsightsTask能综合数据源生成AI分析
- [x] WeComNotifier能成功推送技术简报
- [x] 错误处理健壮，部分失败不影响整体
- [x] 易于添加新数据源和通知方式
- [x] 输出格式统一且结构化
- [x] 有完整的测试覆盖

---

## Open Questions

1. **Q: Product Hunt是否需要处理JavaScript渲染？**
   A: 实施时验证，如需要可考虑使用selenium或寻找公开API

2. **Q: AI分析的token消耗如何控制？**
   A: 每个数据源只取前10条传递给AI，预计消耗可控

3. **Q: 企业微信消息长度限制如何处理？**
   A: 实现分段发送逻辑，每条不超过2000字符

4. **Q: 是否需要添加去重逻辑？**
   A: 初期不添加，如发现大量重复再考虑

---

**End of Design Document**
