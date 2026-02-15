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
    SUBSCRIBE_TO = ["ai_news", "trending_ai", "tech_insights"]  # 订阅 ai_news, trending_ai 和 tech_insights 任务

    def send(self, task_results):
        """
        发送企业微信通知
        task_results: {'ai_news': True/False, 'trending_ai': True/False, ...}
        """
        webhook_url = os.environ.get('WECOM_WEBHOOK_URL')
        if not webhook_url:
            print("错误: 未设置环境变量 WECOM_WEBHOOK_URL")
            return False

        success_count = 0

        # ========== 第一条消息：AI News ==========
        if "ai_news" in task_results and task_results["ai_news"]:
            print("\n" + "="*60)
            print("发送第一条消息: AI 快讯")
            print("="*60)

            news_content = self._create_content_from_json()
            if news_content:
                if self._send_wecom_message(webhook_url, news_content):
                    print("✓ AI 快讯已成功发送到企业微信")
                    success_count += 1
            else:
                print("✗ 创建 AI 快讯内容失败")
        else:
            print("未发送 AI 快讯：任务未成功执行")

        # ========== 第二条消息：Tech Insights ==========
        if "tech_insights" in task_results and task_results["tech_insights"]:
            print("\n" + "="*60)
            print("发送第三条消息: 技术行业动态简报")
            print("="*60)

            insights_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'output',
                'tech-insights',
                f'{self._get_today()}.md'
            )

            if not os.path.exists(insights_path):
                print(f"⚠️ 技术简报文件不存在: {insights_path}")
            else:
                with codecs.open(insights_path, 'r', 'utf-8') as f:
                    content = f.read()

                # 企业微信markdown消息长度限制为2048字节
                # 如果内容过长，需要分段发送
                max_bytes = 1900  # 留一些余量
                current_bytes = len(content.encode('utf-8'))

                if current_bytes > max_bytes:
                    print(f"内容过长 ({current_bytes} 字节)，将分段发送")
                    if self._send_long_markdown(webhook_url, content, max_bytes):
                        print("✓ 技术行业动态简报已成功发送到企业微信（分段）")
                        success_count += 1
                    else:
                        print("✗ 发送技术简报失败")
                else:
                    full_message = "## 📊 技术行业动态简报\n\n" + content
                    if self._send_wecom_message(webhook_url, full_message):
                        print("✓ 技术行业动态简报已成功发送到企业微信")
                        success_count += 1
                    else:
                        print("✗ 发送技术简报失败")
        else:
            print("未发送技术简报：任务未成功执行")

        # ========== 第三条消息：GitHub Trending ==========
        print("\n" + "="*60)
        print("发送第二条消息: GitHub Trending")
        print("="*60)

        # 只要有 trending 数据就发送（不管 AI 分析是否成功）
        trending_content = self._create_trending_content()
        if trending_content:
            # 检查内容是否已包含标题（AI分析结果自带标题）
            if not trending_content.startswith('#'):
                # 原始trending数据，需要添加标题
                full_trending_message = "# GitHub Trending 今日热榜\n\n" + trending_content
            else:
                # AI分析结果，已有标题，直接使用
                full_trending_message = trending_content

            if self._send_wecom_message(webhook_url, full_trending_message):
                print("✓ GitHub Trending 已成功发送到企业微信")
                success_count += 1
        else:
            print("✗ 未找到 GitHub Trending 数据")

        print("\n" + "="*60)
        print("消息发送完成")
        print("="*60)

        return success_count > 0

    def _create_content_from_json(self):
        """从JSON文件创建AI新闻消息内容"""
        try:
            today = self._get_today()
            year = self._get_year()

            # 使用正确的路径结构：output/ai-news/{year}/{date}.json
            json_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'output',
                'ai-news',
                year,
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

    def _create_trending_content(self):
        """优先从AI分析文件创建GitHub Trending内容，如果不存在则使用原始trending数据"""
        try:
            today = self._get_today()
            year = self._get_year()

            # 优先尝试AI分析文件
            analysis_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'output',
                'github-trending',
                year,
                f'{today}-analysis.md'
            )

            # 回退到原始trending文件
            trending_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'output',
                'github-trending',
                year,
                f'{today}.md'
            )

            content = None
            source_type = ""

            # 优先使用AI分析结果
            if os.path.exists(analysis_file):
                print(f"✓ 找到AI分析文件: {analysis_file}")
                with codecs.open(analysis_file, 'r', 'utf-8') as f:
                    content = f.read()
                source_type = "AI分析"
            elif os.path.exists(trending_file):
                print(f"⚠ 未找到AI分析文件，使用原始trending数据: {trending_file}")
                with codecs.open(trending_file, 'r', 'utf-8') as f:
                    content = f.read()
                source_type = "原始数据"
            else:
                print(f"✗ 未找到任何数据文件")
                print(f"  - AI分析: {analysis_file}")
                print(f"  - 原始数据: {trending_file}")
                return None

            # 单独发送，可以使用全部 4096 字节（留一些缓冲）
            max_bytes = 3800  # 预留 296 字节给标题等
            current_bytes = len(content.encode('utf-8'))

            if current_bytes > max_bytes:
                # 截断到接近 max_bytes，但保留完整字符
                content_utf8 = content.encode('utf-8')
                content = content_utf8[:max_bytes].decode('utf-8', errors='ignore')
                content += "\n\n... (更多内容请查看仓库)"

            print(f"GitHub trending 内容 ({source_type}): {current_bytes} 字节 (限制: {max_bytes})")

            return content
        except Exception as e:
            print(f"读取 GitHub trending 数据失败: {str(e)}")
            return None

    def _send_long_markdown(self, webhook_url, content, max_bytes):
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
                if len('\n'.join(current_chunk).encode('utf-8')) > max_bytes:
                    if len(current_chunk) > 1:
                        chunks.append('\n'.join(current_chunk[:-1]))
                        current_chunk = [line]
                    else:
                        # 单行就超长，强制分割
                        chunks.append('\n'.join(current_chunk))
                        current_chunk = []

            # 添加最后一个chunk
            if current_chunk:
                chunks.append('\n'.join(current_chunk))

            # 发送每个chunk
            for idx, chunk in enumerate(chunks, 1):
                prefix = f"\n\n（第 {idx}/{len(chunks)} 部分）" if len(chunks) > 1 else ""
                message = "## 📊 技术行业动态简报" + prefix + "\n\n" + chunk
                if not self._send_wecom_message(webhook_url, message):
                    return False
                # 避免发送过快
                import time
                time.sleep(1)

            return True

        except Exception as e:
            print(f"✗ 分段发送失败: {str(e)}")
            return False

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
            return True
        except Exception as e:
            print(f"发送消息时发生错误: {str(e)}")
            return False

    def _get_today(self):
        """获取今天的日期 YYYY-MM-DD"""
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def _get_year(self):
        """获取当前年份 YYYY"""
        return datetime.datetime.now().strftime('%Y')


# Allow direct execution for testing
if __name__ == '__main__':
    notifier = WeComNotifier()
    # 模拟任务结果
    mock_results = {'ai_news': True, 'trending_ai': True}
    notifier.send(mock_results)
