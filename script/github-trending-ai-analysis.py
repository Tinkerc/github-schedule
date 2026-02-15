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


if __name__ == '__main__':
    job()
