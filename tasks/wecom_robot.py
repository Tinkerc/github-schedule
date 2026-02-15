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
