# coding:utf-8

import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.git_helper import git_add_commit_push


def createMarkdown(date, filename):
    with open(filename, 'w') as f:
        f.write("## " + date + "\n")


def checkPathExist(path):
    if not os.path.exists(path):
        os.makedirs(path)


def scrape(language, filename):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    url = 'https://github.com/trending/{language}'.format(language=language)
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    d = pq(r.content)
    items = d('div.Box article.Box-row')
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n#### {language}\n'.format(language=language))
        for item in items:
            i = pq(item)
            title = i(".lh-condensed a").text()
            description = i("p.col-9").text()
            url = i(".lh-condensed a").attr("href")
            url = "https://github.com" + url
            f.write(u"* [{title}]({url}):{description}\n".format(title=title, url=url, description=description))


def job():
    # 获取环境变量的值，如果不存在则返回默认值
    env_variable_value = os.environ.get('username', 'default_value')
    env_variable_value_password = os.environ.get('password', 'default_value')
    env_variable_value_appId = os.environ.get('appId', 'default_value')
    
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    stryear = datetime.datetime.now().strftime('%Y')
    filename = stryear + '/{date}.md'.format(date=strdate)
    checkPathExist(stryear)
    createMarkdown(strdate, filename)
    scrape('python', filename)
    #scrape('swift', filename)
    scrape('javascript', filename)
    scrape('go', filename)
    scrape('java', filename)


if __name__ == '__main__':
    job()