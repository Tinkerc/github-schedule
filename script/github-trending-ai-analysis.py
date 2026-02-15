# coding:utf-8

import datetime
import os
import time
import codecs
import requests
import logging
import json
from pyquery import PyQuery as pq
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'prompts'))
from trending_prompts import get_batch_analysis_prompt, get_trend_summary_prompt

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


if __name__ == '__main__':
    # 测试 AI 分析
    scraper = GitHubTrendingScraper()
    projects = scraper.scrape_all_languages()[:5]  # 先测试 5 个

    analyzer = GLMAnalyzer()
    analyses = analyzer.analyze_projects(projects)
    print(f"分析结果: {json.dumps(analyses, ensure_ascii=False, indent=2)}")
