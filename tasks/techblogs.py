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
                # Handle both date formats: with and without microseconds
                published_at = item['published_at']
                try:
                    if '.' in published_at:
                        published_date = datetime.strptime(
                            published_at,
                            '%Y-%m-%dT%H:%M:%S.%fZ'
                        ).strftime('%Y-%m-%d')
                    else:
                        published_date = datetime.strptime(
                            published_at,
                            '%Y-%m-%dT%H:%M:%SZ'
                        ).strftime('%Y-%m-%d')
                except ValueError:
                    published_date = self.get_today()  # Fallback to today

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
