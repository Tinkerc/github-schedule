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
    """优先从AI分析文件创建内容，如果不存在则使用原始trending数据"""
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        year = datetime.datetime.now().strftime('%Y')

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

def job():
    """发送两条独立的消息：AI News 和 GitHub Trending"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    year = datetime.datetime.now().strftime('%Y')
    webhook_url = os.environ.get('WECOM_WEBHOOK_URL')

    if not webhook_url:
        print("错误: 未设置环境变量 WECOM_WEBHOOK_URL")
        return

    # ========== 第一条消息：AI News ==========
    json_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'output',
        'ai-news',
        year,
        f'{today}.json'
    )

    if os.path.exists(json_file):
        print("\n" + "="*60)
        print("发送第一条消息: AI 快讯")
        print("="*60)

        news_content = create_content_from_json(json_file)
        if news_content:
            if send_wecom_message(webhook_url, news_content):
                print("✓ AI 快讯已成功发送到企业微信")
        else:
            print("✗ 创建 AI 快讯内容失败")
    else:
        print(f"未找到今日的新闻数据: {json_file}")

    # ========== 第二条消息：GitHub Trending ==========
    print("\n" + "="*60)
    print("发送第二条消息: GitHub Trending")
    print("="*60)

    trending_content = create_trending_content()
    if trending_content:
        # 检查内容是否已包含标题（AI分析结果自带标题）
        if not trending_content.startswith('#'):
            # 原始trending数据，需要添加标题
            full_trending_message = "# GitHub Trending 今日热榜\n\n" + trending_content
        else:
            # AI分析结果，已有标题，直接使用
            full_trending_message = trending_content

        if send_wecom_message(webhook_url, full_trending_message):
            print("✓ GitHub Trending 已成功发送到企业微信")
    else:
        print("✗ 未找到 GitHub Trending 数据")

    print("\n" + "="*60)
    print("消息发送完成")
    print("="*60)

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