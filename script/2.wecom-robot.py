# coding:utf-8

import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq
import json



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
    
    # 创建消息内容
    content = create_content_from_json(json_file)
    if not content:
        return
    
    # 发送到企业微信
    webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2e9f5a61-9ec3-4049-b981-c9b01f56f410'
    if send_wecom_message(webhook_url, content):
        print("新闻已成功发送到企业微信")

def git_add_commit_push(date, filename):
    cmd_git_add = 'git add {filename}'.format(filename=filename)
    cmd_git_commit = 'git commit -m "{date}"'.format(date=date)
    cmd_git_push = 'git push -u origin master'

    os.system(cmd_git_add)
    os.system(cmd_git_commit)
    os.system(cmd_git_push)

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
        response = requests.post(webhook_url, headers=headers, json=data)
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