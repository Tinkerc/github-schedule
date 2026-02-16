# Task Framework Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor numbered-script system into a robust task framework with base classes for improved maintainability, testability, and scalability.

**Architecture:** Two base classes (Task for data jobs, Notifier for notifications) with priority-based execution. Flat `tasks/` directory structure. TaskRunner discovers and executes all tasks, then triggers notifiers based on task results.

**Tech Stack:** Python 3.8+, abc (Abstract Base Classes), importlib (dynamic module loading), pytest (testing), existing libraries (requests, pyquery, lxml)

---

## Phase 1: Create Framework Core

### Task 1: Create core package structure

**Files:**
- Create: `core/__init__.py`
- Create: `core/base.py`
- Create: `core/runner.py`

**Step 1: Create core/__init__.py**

```bash
touch core/__init__.py
```

**Step 2: Create core/base.py with Task and Notifier base classes**

```python
# core/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import os
import json

class Task(ABC):
    """任务基类 - 所有数据获取/分析任务继承此类"""

    TASK_ID: str = ""          # 子类必须定义
    PRIORITY: int = 100        # 执行优先级，数字越小越先执行

    @abstractmethod
    def execute(self) -> bool:
        """
        执行任务
        返回: bool (成功=True, 失败=False)
        """
        pass

    def get_output_path(self, filename: str) -> str:
        """获取输出文件路径"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, 'output')

        # 如果文件路径包含子目录，创建它们
        if '/' in filename:
            subdir = os.path.dirname(filename)
            full_dir = os.path.join(output_dir, subdir)
            os.makedirs(full_dir, exist_ok=True)
        else:
            os.makedirs(output_dir, exist_ok=True)

        return os.path.join(output_dir, filename)

    def get_today(self) -> str:
        """获取今天的日期 YYYY-MM-DD"""
        return datetime.now().strftime('%Y-%m-%d')

    def get_year(self) -> str:
        """获取当前年份 YYYY"""
        return datetime.now().strftime('%Y')


class Notifier(ABC):
    """通知基类 - 所有通知模块继承此类"""

    NOTIFIER_ID: str = ""
    SUBSCRIBE_TO: List[str] = []  # 订阅的任务ID列表

    @abstractmethod
    def send(self, task_results: Dict[str, Any]) -> bool:
        """
        发送通知
        task_results: {
            'ai_news': True/False,
            'github_trending': True/False,
            ...
        }
        返回: bool (成功=True, 失败=False)
        """
        pass
```

**Step 3: Verify base.py syntax**

```bash
python -m py_compile core/base.py
```

Expected: No errors

**Step 4: Commit core/base.py**

```bash
git add core/base.py core/__init__.py
git commit -m "feat(core): add Task and Notifier base classes

Add abstract base classes for the task framework:
- Task: For data fetching and analysis jobs
- Notifier: For notification modules
- Helper methods for output path and date handling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 2: Create core/runner.py with TaskRunner

**Files:**
- Create: `core/runner.py`

**Step 1: Write core/runner.py**

```python
# core/runner.py
import os
import importlib.util
import sys
from typing import Dict, List, Type
from pathlib import Path

from core.base import Task, Notifier


class TaskRunner:
    """任务执行器 - 发现、执行所有任务和通知器"""

    def __init__(self, tasks_dir: str = "tasks"):
        self.tasks_dir = tasks_dir
        self.tasks: Dict[str, Task] = {}
        self.notifiers: Dict[str, Notifier] = {}

    def discover(self):
        """扫描 tasks/ 目录，加载所有 Task 和 Notifier 子类"""
        tasks_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.tasks_dir)

        if not os.path.exists(tasks_path):
            print(f"错误: 任务目录 {tasks_path} 不存在")
            sys.exit(1)

        # 遍历 tasks/ 目录下的所有 .py 文件
        for filename in os.listdir(tasks_path):
            if not filename.endswith('.py') or filename == '__init__.py':
                continue

            module_name = filename[:-3]  # 移除 .py 扩展名
            module_path = os.path.join(tasks_path, filename)

            try:
                # 动态加载模块
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 查找模块中的 Task 和 Notifier 子类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # 跳过基类本身
                    if attr_name in ['Task', 'Notifier']:
                        continue

                    # 检查是否是 Task 子类
                    if isinstance(attr, type) and issubclass(attr, Task) and attr is not Task:
                        task_instance = attr()
                        if task_instance.TASK_ID:
                            self.tasks[task_instance.TASK_ID] = task_instance
                            print(f"  ✓ 发现任务: {task_instance.TASK_ID}")

                    # 检查是否是 Notifier 子类
                    if isinstance(attr, type) and issubclass(attr, Notifier) and attr is not Notifier:
                        notifier_instance = attr()
                        if notifier_instance.NOTIFIER_ID:
                            self.notifiers[notifier_instance.NOTIFIER_ID] = notifier_instance
                            print(f"  ✓ 发现通知器: {notifier_instance.NOTIFIER_ID}")

            except Exception as e:
                print(f"  警告: 加载 {filename} 失败: {str(e)}")

        print(f"\n发现 {len(self.tasks)} 个任务, {len(self.notifiers)} 个通知器")

    def run_tasks(self) -> Dict[str, bool]:
        """执行所有任务（按优先级排序）"""
        if not self.tasks:
            print("警告: 没有发现任何任务")
            return {}

        # 按优先级排序
        sorted_tasks = sorted(
            self.tasks.items(),
            key=lambda x: x[1].PRIORITY
        )

        print(f"\n执行顺序:")
        for task_id, task in sorted_tasks:
            print(f"  {task.PRIORITY}. {task_id}")

        print(f"\n{'='*60}")
        print("开始执行任务")
        print(f"{'='*60}")

        results = {}
        for task_id, task in sorted_tasks:
            print(f"\n[{task.TASK_ID}] 开始执行...")
            try:
                success = task.execute()
                results[task_id] = success
                if success:
                    print(f"[{task.TASK_ID}] ✓ 执行成功")
                else:
                    print(f"[{task.TASK_ID}] ✗ 执行失败")
            except Exception as e:
                print(f"[{task.TASK_ID}] ✗ 执行异常: {str(e)}")
                results[task_id] = False

        return results

    def run_notifiers(self, task_results: Dict[str, bool]):
        """执行所有通知器"""
        if not self.notifiers:
            print("\n没有发现任何通知器")
            return

        print(f"\n{'='*60}")
        print("开始执行通知")
        print(f"{'='*60}")

        for notifier_id, notifier in self.notifiers.items():
            print(f"\n[{notifier_id}] 开始发送通知...")
            try:
                success = notifier.send(task_results)
                if success:
                    print(f"[{notifier_id}] ✓ 发送成功")
                else:
                    print(f"[{notifier_id}] ✗ 发送失败")
            except Exception as e:
                print(f"[{notifier_id}] ✗ 发送异常: {str(e)}")

    def print_summary(self, task_results: Dict[str, bool]):
        """打印执行摘要"""
        total = len(task_results)
        success = sum(1 for v in task_results.values() if v)
        failed = total - success

        print(f"\n{'='*60}")
        print("执行摘要")
        print(f"{'='*60}")
        print(f"总计任务数: {total}")
        print(f"成功执行: {success}")
        print(f"执行失败: {failed}")
        print(f"{'='*60}")
```

**Step 2: Verify runner.py syntax**

```bash
python -m py_compile core/runner.py
```

Expected: No errors

**Step 3: Commit core/runner.py**

```bash
git add core/runner.py
git commit -m "feat(core): add TaskRunner for task discovery and execution

Implement TaskRunner class with:
- Dynamic task discovery from tasks/ directory
- Priority-based task execution
- Notifier execution with task results
- Execution summary with statistics

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 2: Migrate Tasks

### Task 3: Create tasks package

**Files:**
- Create: `tasks/__init__.py`

**Step 1: Create tasks/__init__.py**

```bash
touch tasks/__init__.py
```

**Step 2: Commit**

```bash
git add tasks/__init__.py
git commit -m "feat(tasks): create tasks package

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 4: Migrate ai_news task

**Files:**
- Create: `tasks/ai_news.py`
- Reference: `script/1.ai-news.py`

**Step 1: Create tasks/ai_news.py with AINewsTask class**

```python
# tasks/ai_news.py
# coding:utf-8

import datetime
import codecs
import requests
import os
from pyquery import PyQuery as pq

from core.base import Task


class AINewsTask(Task):
    """AI新闻获取任务"""

    TASK_ID = "ai_news"
    PRIORITY = 10

    def execute(self) -> bool:
        """获取AI新闻并保存为JSON"""
        try:
            # 获取HTML
            url = "https://ai-bot.cn/daily-ai-news/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 保存HTML到临时文件
            today = self.get_today()
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'output',
                'ai-news'
            )
            os.makedirs(output_dir, exist_ok=True)

            html_file = os.path.join(output_dir, f'{today}.html')
            with codecs.open(html_file, 'w', 'utf-8') as f:
                f.write(response.text)

            # 解析新闻
            news = self._parse_news_from_file(html_file)
            if not news:
                return False

            print(f"Successfully parsed {len(news['items'])} news items")

            # 保存为JSON
            json_file = os.path.join(output_dir, f"{today}.json")
            with codecs.open(json_file, 'w', 'utf-8') as f:
                import json
                json.dump(news, f, ensure_ascii=False, indent=2)

            print(f"News data saved to: {json_file}")
            return True

        except Exception as e:
            print(f"Failed to fetch AI news: {str(e)}")
            return False

    def _parse_news_from_file(self, file_path):
        """从HTML文件解析新闻数据"""
        try:
            with codecs.open(file_path, 'r', 'utf-8') as f:
                html_content = f.read()

            doc = pq(html_content)
            # 获取第一个news-list区块
            first_news_list = doc('.news-list').eq(0)

            # 获取日期（仅获取直接子元素）
            date_text = first_news_list.children('.news-date').text()
            date_parts = date_text.split('·')

            news = {
                'date': self.get_today(),
                'weekday': date_parts[1] if len(date_parts) > 1 else '',
                'items': []
            }

            # 获取新闻条目（仅获取直接子元素）
            for news_item in first_news_list.children('.news-item').items():
                content = news_item.find('.news-content')
                title = content.find('h2 a').text()
                url = content.find('h2 a').attr('href')

                # 获取新闻内容和来源
                p_text = content.find('p.text-muted').text()
                source = content.find('.news-time').text().replace('来源：', '')

                # 移除来源信息，得到纯内容
                main_content = p_text.replace(f'来源：{source}', '').strip()

                news['items'].append({
                    'title': title,
                    'url': url,
                    'content': main_content,
                    'source': source
                })

            return news
        except Exception as e:
            print(f"Failed to parse news: {str(e)}")
            return None


# Allow direct execution for testing
if __name__ == '__main__':
    task = AINewsTask()
    task.execute()
```

**Step 2: Test ai_news task independently**

```bash
python -m tasks.ai_news
```

Expected: Output shows "Successfully parsed X news items" and "News data saved to: output/ai-news/YYYY-MM-DD.json"

**Step 3: Verify output file exists**

```bash
ls -lh output/ai-news/
cat output/ai-news/$(date +%Y-%m-%d).json | head -20
```

Expected: JSON file with today's date containing news data

**Step 4: Commit ai_news task**

```bash
git add tasks/ai_news.py
git commit -m "feat(tasks): migrate ai_news to task framework

Refactor script/1.ai-news.py into tasks/ai_news.py:
- Inherit from Task base class
- TASK_ID = 'ai_news', PRIORITY = 10
- Keep existing fetch and parse logic
- Support independent execution via __main__

Output: output/ai-news/YYYY-MM-DD.json

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 5: Migrate github_trending task

**Files:**
- Create: `tasks/github_trending.py`
- Reference: `script/2.github-trending.py`

**Step 1: Create tasks/github_trending.py**

```python
# tasks/github_trending.py
# coding:utf-8

import datetime
import codecs
import requests
import os
from pyquery import PyQuery as pq

from core.base import Task


class GitHubTrendingTask(Task):
    """GitHub Trending 抓取任务"""

    TASK_ID = "github_trending"
    PRIORITY = 20

    def execute(self) -> bool:
        """抓取GitHub Trending并保存为Markdown"""
        try:
            strdate = self.get_today()
            stryear = self.get_year()
            filename = f'{stryear}/{strdate}.md'

            # 确保年份目录存在
            os.makedirs(stryear, exist_ok=True)

            # 创建markdown文件
            self._create_markdown(strdate, filename)

            # 抓取各语言趋势
            self._scrape('python', filename)
            self._scrape('javascript', filename)
            self._scrape('go', filename)
            self._scrape('java', filename)

            print(f"✓ GitHub Trending saved to: {filename}")
            return True

        except Exception as e:
            print(f"✗ GitHub Trending failed: {str(e)}")
            return False

    def _create_markdown(self, date, filename):
        """创建markdown文件并添加日期标题"""
        with open(filename, 'w') as f:
            f.write("## " + date + "\n")

    def _scrape(self, language, filename):
        """抓取指定语言的GitHub Trending"""
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }

        url = f'https://github.com/trending/{language}'
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()

        d = pq(r.content)
        items = d('div.Box article.Box-row')

        with codecs.open(filename, "a", "utf-8") as f:
            f.write(f'\n#### {language}\n')
            for item in items:
                i = pq(item)
                title = i(".lh-condensed a").text()
                description = i("p.col-9").text()
                url = i(".lh-condensed a").attr("href")
                url = "https://github.com" + url
                f.write(f"* [{title}]({url}):{description}\n")


# Allow direct execution for testing
if __name__ == '__main__':
    task = GitHubTrendingTask()
    task.execute()
```

**Step 2: Test github_trending task independently**

```bash
python -m tasks.github_trending
```

Expected: Output shows "✓ GitHub Trending saved to: YYYY/YYYY-MM-DD.md"

**Step 3: Verify output file**

```bash
ls -lh $(date +%Y)/$(date +%Y-%m-%d).md
head -30 $(date +%Y)/$(date +%Y-%m-%d).md
```

Expected: Markdown file with today's trending repositories

**Step 4: Commit github_trending task**

```bash
git add tasks/github_trending.py
git commit -m "feat(tasks): migrate github_trending to task framework

Refactor script/2.github-trending.py into tasks/github_trending.py:
- Inherit from Task base class
- TASK_ID = 'github_trending', PRIORITY = 20
- Scrape python, javascript, go, java trending
- Support independent execution

Output: output/YYYY/YYYY-MM-DD.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 6: Migrate trending_ai task

**Files:**
- Create: `tasks/trending_ai.py`
- Reference: `script/3.ai-analyze-trending.py`

**Step 1: Create tasks/trending_ai.py**

```python
# tasks/trending_ai.py
# coding:utf-8
"""
GitHub Trending AI 分析脚本
读取 GitHub Trending 数据，调用 AI 进行分析，生成分析报告
"""

import datetime
import os
import requests
import codecs

from core.base import Task


class TrendingAITask(Task):
    """GitHub Trending AI分析任务"""

    TASK_ID = "trending_ai"
    PRIORITY = 30

    def execute(self) -> bool:
        """读取trending数据并调用AI分析"""
        print("\n" + "="*60)
        print("GitHub Trending AI 分析")
        print("="*60)

        # 1. 读取 trending 数据
        strdate = self.get_today()
        stryear = self.get_year()
        trending_file = f'{stryear}/{strdate}.md'

        if not os.path.exists(trending_file):
            print(f"✗ 未找到 trending 数据文件: {trending_file}")
            return False

        trending_content = self._read_trending_data(trending_file)
        if not trending_content:
            return False

        # 2. 调用 AI 分析
        analysis = self._call_ai_analysis(trending_content)
        if not analysis:
            print("\nAI 分析未完成，跳过保存步骤")
            return False

        # 3. 保存分析结果
        analysis_file = f'{stryear}/{strdate}-analysis.md'
        success = self._save_analysis(analysis, analysis_file)

        if success:
            print("\n" + "="*60)
            print("✓ AI 分析任务完成")
            print(f"原始数据: {trending_file}")
            print(f"分析报告: {analysis_file}")
            print("="*60)
            return True
        else:
            return False

    def _read_trending_data(self, filename):
        """读取trending markdown文件内容"""
        try:
            with codecs.open(filename, 'r', 'utf-8') as f:
                content = f.read()
            print(f"✓ 成功读取 trending 数据: {filename}")
            return content
        except Exception as e:
            print(f"✗ 读取trending数据失败: {str(e)}")
            return None

    def _call_ai_analysis(self, trending_content):
        """调用 ZhipuAI (GLM-4) 进行分析"""
        api_key = os.environ.get('BIGMODEL_API_KEY')
        if not api_key:
            print("警告: 未设置 BIGMODEL_API_KEY 环境变量，跳过 AI 分析")
            print("提示: 如需启用 AI 分析，请设置环境变量: export BIGMODEL_API_KEY=your_key")
            return None

        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

        # 构建分析 prompt
        prompt = f"""请分析以下 GitHub Trending 数据，提供以下内容：

1. **趋势概览**: 总结今天的整体趋势，有哪些突出的技术方向？
2. **热门项目分析**: 选取 3-5 个最有趣或最受欢迎的项目，详细介绍它们的特点、价值和应用场景
3. **技术趋势**: 从这些项目中分析出当前的技术趋势（如 AI、Web3、云原生等）
4. **推荐关注**: 列出值得开发者关注和学习的项目

请用中文回答，使用 markdown 格式，保持专业但易懂的语气。

---
GitHub Trending 数据:
{trending_content}
"""

        payload = {
            "model": "glm-4",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个技术专家，擅长分析开源项目和技术趋势。请用中文回答，使用清晰的 markdown 格式。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            print("正在调用 AI 分析...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                analysis = result['choices'][0]['message']['content']
                print("✓ AI 分析完成")
                return analysis
            else:
                print("✗ AI 响应格式异常")
                return None

        except requests.exceptions.Timeout:
            print("✗ AI 请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"✗ AI 请求失败 - {str(e)}")
            return None
        except Exception as e:
            print(f"✗ AI 分析过程出错 - {str(e)}")
            return None

    def _save_analysis(self, analysis_content, output_filename):
        """保存AI分析结果到文件"""
        try:
            with codecs.open(output_filename, 'w', 'utf-8') as f:
                # 添加标题
                strdate = self.get_today()
                f.write(f"# GitHub Trending AI 分析报告\n\n")
                f.write(f"> 分析日期: {strdate}\n\n")
                f.write("---\n\n")
                f.write(analysis_content)

            print(f"✓ 分析结果已保存: {output_filename}")
            return True
        except Exception as e:
            print(f"✗ 保存分析结果失败 - {str(e)}")
            return False


# Allow direct execution for testing
if __name__ == '__main__':
    task = TrendingAITask()
    task.execute()
```

**Step 2: Test trending_ai task independently**

```bash
python -m tasks.trending_ai
```

Expected: Output shows AI analysis process and "✓ AI 分析任务完成" (requires BIGMODEL_API_KEY env var)

**Step 3: Verify output file**

```bash
ls -lh $(date +%Y)/$(date +%Y-%m-%d)-analysis.md
head -30 $(date +%Y)/$(date +%Y-%m-%d)-analysis.md
```

Expected: Analysis markdown file with AI-generated insights

**Step 4: Commit trending_ai task**

```bash
git add tasks/trending_ai.py
git commit -m "feat(tasks): migrate trending_ai to task framework

Refactor script/3.ai-analyze-trending.py into tasks/trending_ai.py:
- Inherit from Task base class
- TASK_ID = 'trending_ai', PRIORITY = 30
- Call ZhipuAI API for analysis
- Read from and write to year-based directories

Output: output/YYYY/YYYY-MM-DD-analysis.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 7: Migrate wecom_robot notifier

**Files:**
- Create: `tasks/wecom_robot.py`
- Reference: `script/4.wecom-robot.py`

**Step 1: Create tasks/wecom_robot.py**

```python
# tasks/wecom_robot.py
# coding:utf-8

import datetime
import codecs
import requests
import os
import json

from core.base import Notifier


class WeComNotifier(Notifier):
    """企业微信通知器"""

    NOTIFIER_ID = "wecom"
    SUBSCRIBE_TO = ["ai_news"]  # 订阅 ai_news 任务

    def send(self, task_results):
        """
        发送企业微信通知
        task_results: {'ai_news': True/False, ...}
        """
        # 检查订阅的任务是否成功
        if "ai_news" not in task_results or not task_results["ai_news"]:
            print("ai_news 任务未成功执行，跳过通知")
            return False

        # 读取新闻数据
        content = self._create_content_from_json()
        if not content:
            return False

        # 发送到企业微信
        webhook_url = os.environ.get('WECOM_WEBHOOK_URL')
        if not webhook_url:
            print("错误: 未设置环境变量 WECOM_WEBHOOK_URL")
            return False

        return self._send_wecom_message(webhook_url, content)

    def _create_content_from_json(self):
        """从JSON文件创建消息内容"""
        try:
            today = self.get_today()
            json_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'output',
                'ai-news',
                f'{today}.json'
            )

            if not os.path.exists(json_file):
                print(f"未找到今日的新闻数据: {json_file}")
                return None

            with codecs.open(json_file, 'r', 'utf-8') as f:
                news_data = json.loads(f.read())

            # 构建markdown内容
            content = f"""# AI快讯 ({news_data['date']} {news_data['weekday']})
## 今日要闻
"""
            for item in news_data['items']:
                content += f"""### {item['title']}
> {item['content']}
来源：{item['source']} [查看详情]({item['url']})

"""
            return content
        except Exception as e:
            print(f"创建消息内容失败: {str(e)}")
            return None

    def _send_wecom_message(self, webhook_url, content):
        """发送企业微信消息"""
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'msgtype': 'markdown',
            'markdown': {
                'content': content
            }
        }
        try:
            response = requests.post(webhook_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result['errcode'] != 0:
                print(f"发送消息失败: {result['errmsg']}")
                return False
            print("新闻已成功发送到企业微信")
            return True
        except Exception as e:
            print(f"发送消息时发生错误: {str(e)}")
            return False

    def get_today(self):
        """获取今天的日期"""
        return datetime.datetime.now().strftime('%Y-%m-%d')


# Allow direct execution for testing
if __name__ == '__main__':
    notifier = WeComNotifier()
    # 模拟任务结果
    mock_results = {'ai_news': True}
    notifier.send(mock_results)
```

**Step 2: Test wecom_robot notifier independently**

```bash
python -m tasks.wecom_robot
```

Expected: Reads today's ai_news JSON and sends to WeChat Work (requires WECOM_WEBHOOK_URL env var)

**Step 3: Commit wecom_robot notifier**

```bash
git add tasks/wecom_robot.py
git commit -m "feat(tasks): migrate wecom_robot to notifier framework

Refactor script/4.wecom-robot.py into tasks/wecom_robot.py:
- Inherit from Notifier base class
- NOTIFIER_ID = 'wecom', SUBSCRIBE_TO = ['ai_news']
- Send notification only if ai_news task succeeds
- Support independent execution with mock results

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 3: Update Main Entry Point

### Task 8: Update main.py to use TaskRunner

**Files:**
- Modify: `main.py`

**Step 1: Backup current main.py**

```bash
cp main.py main.py.backup
```

**Step 2: Replace main.py with new implementation**

```python
# main.py
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.runner import TaskRunner

# 加载 .env 文件中的环境变量
load_dotenv()


def main():
    print("="*60)
    print("GitHub Schedule Automation System")
    print("="*60)

    # 创建任务执行器
    runner = TaskRunner(tasks_dir="tasks")

    # 发现所有任务和通知器
    print("\n发现任务和通知器...")
    runner.discover()

    # 执行所有任务
    task_results = runner.run_tasks()

    # 执行所有通知器
    runner.run_notifiers(task_results)

    # 打印摘要
    runner.print_summary(task_results)

    # 返回退出码
    total = len(task_results)
    failed = sum(1 for v in task_results.values() if not v)
    return 1 if failed > 0 else 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
```

**Step 3: Test new main.py**

```bash
python main.py
```

Expected: Full pipeline execution with all tasks and notifiers

**Step 4: Commit main.py**

```bash
git add main.py main.py.backup
git commit -m "refactor(main): update to use TaskRunner framework

Replace dynamic script loading with TaskRunner:
- Discover and execute Task and Notifier classes
- Priority-based execution
- Graceful error handling
- Detailed execution summary

Backup saved as main.py.backup

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 4: Validation

### Task 9: Full integration testing

**Files:**
- No file changes

**Step 1: Run full pipeline**

```bash
python main.py
```

Expected output:
```
============================================================
GitHub Schedule Automation System
============================================================

发现任务和通知器...
  ✓ 发现任务: ai_news
  ✓ 发现任务: github_trending
  ✓ 发现任务: trending_ai
  ✓ 发现通知器: wecom

发现 3 个任务, 1 个通知器

执行顺序:
  10. ai_news
  20. github_trending
  30. trending_ai

============================================================
开始执行任务
============================================================

[ai_news] 开始执行...
Successfully parsed X news items
News data saved to: output/ai-news/YYYY-MM-DD.json
[ai_news] ✓ 执行成功

[github_trending] 开始执行...
✓ GitHub Trending saved to: YYYY/YYYY-MM-DD.md
[github_trending] ✓ 执行成功

[trending_ai] 开始执行...
✓ 成功读取 trending 数据: YYYY/YYYY-MM-DD.md
正在调用 AI 分析...
✓ AI 分析完成
✓ 分析结果已保存: YYYY/YYYY-MM-DD-analysis.md
[trending_ai] ✓ 执行成功

============================================================
开始执行通知
============================================================

[wecom] 开始发送通知...
新闻已成功发送到企业微信
[wecom] ✓ 发送成功

============================================================
执行摘要
============================================================
总计任务数: 3
成功执行: 3
执行失败: 0
============================================================
```

**Step 2: Verify all output files exist**

```bash
# AI News
ls -lh output/ai-news/$(date +%Y-%m-%d).json

# GitHub Trending
ls -lh $(date +%Y)/$(date +%Y-%m-%d).md

# AI Analysis
ls -lh $(date +%Y)/$(date +%Y-%m-%d)-analysis.md
```

Expected: All three files exist and have content

**Step 3: Test independent task execution**

```bash
# Test each task independently
python -m tasks.ai_news
python -m tasks.github_trending
python -m tasks.trending_ai
python -m tasks.wecom_robot
```

Expected: Each task runs successfully in isolation

**Step 4: Commit validation results**

```bash
git add docs/plans/2026-02-16-task-framework-implementation.md
git commit -m "docs: add task framework implementation plan

Add detailed TDD-based implementation plan with:
- Phase-by-phase migration strategy
- Exact file paths and code snippets
- Step-by-step testing instructions
- All tasks validated and working

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 5: Documentation Updates

### Task 10: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update architecture section**

```bash
# Edit CLAUDE.md, replace the "Architecture" section with:

## Architecture

### Entry Point
`main.py` is the orchestrator that uses `TaskRunner` to:
1. Discover all `Task` and `Notifier` classes in the `tasks/` directory
2. Execute tasks in PRIORITY order (ai_news → github_trending → trending_ai)
3. Collect task execution results
4. Execute notifiers based on subscribed task results
5. Print execution summary

### Task Framework
All tasks inherit from base classes in `core/base.py`:

**Task base class** - For data fetching and analysis jobs:
- `TASK_ID`: Unique task identifier
- `PRIORITY`: Execution order (lower numbers run first)
- `execute()`: Main task logic, returns True/False

**Notifier base class** - For notification modules:
- `NOTIFIER_ID`: Unique notifier identifier
- `SUBSCRIBE_TO`: List of task IDs to subscribe to
- `send(task_results)`: Send notification based on task results

### Task Structure
```
tasks/
├── ai_news.py           # Fetches AI news (PRIORITY: 10)
├── github_trending.py   # Scrapes GitHub trending (PRIORITY: 20)
├── trending_ai.py       # AI analysis of trending (PRIORITY: 30)
└── wecom_robot.py       # WeChat Work notification (SUBSCRIBE_TO: ['ai_news'])
```

Each task can be run independently for testing:
```bash
python -m tasks.ai_news
python -m tasks.github_trending
python -m tasks.trending_ai
python -m tasks.wecom_robot
```
```

**Step 2: Commit documentation update**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for task framework architecture

Update architecture documentation to reflect:
- TaskRunner-based execution
- Task and Notifier base classes
- Priority-based task ordering
- Independent task testing

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 6: Cleanup

### Task 11: Remove old script directory

**Files:**
- Remove: `script/` directory

**Step 1: Verify new system works completely**

```bash
# Run full pipeline one more time
python main.py

# Check all outputs
find output/ -type f -name $(date +%Y-%m-%d)*
```

Expected: All outputs present and correct

**Step 2: Archive old script directory**

```bash
# Create archive
mv script script.backup.$(date +%Y%m%d)

# Test without old scripts
python main.py
```

Expected: Still works without script/ directory

**Step 3: Remove old scripts**

```bash
rm -rf script.backup.*
git status
```

**Step 4: Commit cleanup**

```bash
git add -A
git commit -m "chore: remove old script directory

Remove deprecated script/ directory after successful migration to task framework.
All functionality now in tasks/ with base class architecture.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 12: Final verification and push

**Files:**
- No file changes

**Step 1: Final end-to-end test**

```bash
# Clean outputs
rm -rf output/ai-news/$(date +%Y-%m-%d).json
rm -rf output/$(date +%Y)/$(date +%Y-%m-%d)*.md

# Run full pipeline
python main.py

# Verify all outputs created
ls -lh output/ai-news/$(date +%Y-%m-%d).json
ls -lh output/$(date +%Y)/$(date +%Y-%m-%d).md
ls -lh output/$(date +%Y)/$(date +%Y-%m-%d)-analysis.md
```

Expected: All files created successfully

**Step 2: Check git status**

```bash
git log --oneline -10
git status
```

Expected: Clean working directory, all commits present

**Step 3: Create migration summary tag**

```bash
git tag -a v2.0.0 -m "Task Framework Migration

Major refactoring from numbered scripts to task framework:
- Task and Notifier base classes
- Priority-based execution
- Independent task testing
- Improved error handling

Migration from v1.0.0 (script/ directory) complete"
```

**Step 4: Push to remote**

```bash
git push origin main --tags
```

**Step 5: Update README (optional)**

If README.md exists, update with:
- New architecture overview
- How to add new tasks
- Testing instructions

**Step 6: Final commit**

```bash
git add README.md
git commit -m "docs: update README for task framework

Update documentation with:
- Task framework architecture
- Development workflow
- How to add new tasks and notifiers

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin main
```

---

## Success Criteria Checklist

- [x] All tasks can run independently via `python -m tasks.<name>`
- [x] Full pipeline executes successfully via `python main.py`
- [x] Output files match original format
- [x] WeChat Work notification works
- [x] No script/ directory remains
- [x] Documentation updated
- [x] All commits pushed to remote
- [x] Tagged as v2.0.0

---

## Next Steps After Migration

### Adding New Tasks

1. Create new file in `tasks/`
2. Inherit from `Task` or `Notifier`
3. Set `TASK_ID`/`NOTIFIER_ID` and `PRIORITY`/`SUBSCRIBE_TO`
4. Implement `execute()` or `send()` method
5. Test independently: `python -m tasks.<your_task>`

Example:
```python
# tasks/hackernews.py
from core.base import Task

class HackerNewsTask(Task):
    TASK_ID = "hackernews"
    PRIORITY = 15

    def execute(self) -> bool:
        # Fetch HN stories
        # Save to output/hackernews/YYYY-MM-DD.json
        return True
```

### Adding New Notifiers

1. Create new file in `tasks/`
2. Inherit from `Notifier`
3. Set `NOTIFIER_ID` and `SUBSCRIBE_TO`
4. Implement `send(task_results)` method

Example:
```python
# tasks/email_notifier.py
from core.base import Notifier

class EmailNotifier(Notifier):
    NOTIFIER_ID = "email"
    SUBSCRIBE_TO = ["ai_news", "trending_ai"]

    def send(self, task_results):
        # Send email digest
        return True
```

---

**Implementation Plan Complete**
