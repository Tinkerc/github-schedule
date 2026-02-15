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
