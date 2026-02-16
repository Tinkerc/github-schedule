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
