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


if __name__ == '__main__':
    scraper = GitHubTrendingScraper()
    projects = scraper.scrape_all_languages()
    print(f"爬取到 {len(projects)} 个项目")
    for p in projects[:3]:
        print(f"- {p['name']}: {p['description'][:50]}...")
