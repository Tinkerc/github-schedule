# coding:utf-8

import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq
import json

# git_helper import removed - unused



def create_content_from_json(json_file):
    try:
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

def create_trending_content():
    """从 GitHub trending markdown 文件创建内容"""
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        year = datetime.datetime.now().strftime('%Y')

        # GitHub trending 文件路径
        trending_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'output',
            'github-trending',
            year,
            f'{today}.md'
        )

        if not os.path.exists(trending_file):
            print(f"未找到 GitHub trending 数据: {trending_file}")
            return None

        with codecs.open(trending_file, 'r', 'utf-8') as f:
            content = f.read()

        # 只显示前 400 字符，避免消息过长
        if len(content) > 400:
            content = content[:400] + "\n\n... (更多内容请查看仓库)"

        return content
    except Exception as e:
        print(f"读取 GitHub trending 数据失败: {str(e)}")
        return None

def job():
    # 获取当天的日期
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # 构建JSON文件路径
    json_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'output',
        'ai-news',
        f'{today}.json'
    )

    # 检查文件是否存在
    if not os.path.exists(json_file):
        print(f"未找到今日的新闻数据: {json_file}")
        return

    # 创建消息内容 - AI News
    content = create_content_from_json(json_file)
    if not content:
        return

    # 添加 GitHub trending 内容
    trending_content = create_trending_content()
    if trending_content:
        content += "\n\n---\n\n" + "## GitHub Trending 今日热榜\n" + trending_content

    # 发送到企业微信
    webhook_url = os.environ.get('WECOM_WEBHOOK_URL')
    if not webhook_url:
        print("错误: 未设置环境变量 WECOM_WEBHOOK_URL")
        return
    if send_wecom_message(webhook_url, content):
        print("新闻和 Trending 已成功发送到企业微信")

def send_wecom_message(webhook_url, content):
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
def create_content():
    content = """# 项目日报通知
## 项目进展
- 已完成功能开发：<font color="info">80%</font>
- 测试覆盖率：<font color="warning">75%</font>
- 发现严重问题：<font color="warning">2</font> 个

### 详细信息
> 今日代码提交：12次
> 新增代码行数：+1200/-500

**重要提醒**
1. 项目例会时间：<font color="info">14:30</font>
2. 代码审查截止：<font color="warning">18:00</font>

[查看详细报告](https://example.com/report)

---
@所有人 请注意查收"""
    return content

if __name__ == '__main__':
    job()