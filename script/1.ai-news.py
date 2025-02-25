# coding:utf-8

import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq
import json

def fetch_ai_news():
    url = "https://ai-bot.cn/daily-ai-news/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # 创建输出目录
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'ai-news')
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存文件
        output_file = os.path.join(output_dir, f'{today}.html')
        with codecs.open(output_file, 'w', 'utf-8') as f:
            f.write(response.text)
        
        return output_file
    except Exception as e:
        print(f"Failed to fetch AI news: {str(e)}")
        return None

def parse_news_from_file(file_path):
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
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
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

def job():
    # 获取AI新闻并保存
    output_file = fetch_ai_news()
    if not output_file:
        return
    
    # 解析新闻内容
    news = parse_news_from_file(output_file)
    
    if news:
        print(f"Successfully parsed {len(news['items'])} news items")
        
        # 保存为JSON文件
        json_file = os.path.join(
            os.path.dirname(output_file),
            f"{news['date']}.json"
        )
        
        try:
            with codecs.open(json_file, 'w', 'utf-8') as f:
                json.dump(news, f, ensure_ascii=False, indent=2)
            print(f"News data saved to: {json_file}")
            
        except Exception as e:
            print(f"Failed to save JSON file: {str(e)}")

if __name__ == '__main__':
    job()