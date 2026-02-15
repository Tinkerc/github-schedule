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
