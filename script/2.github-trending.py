# coding:utf-8

import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq

# git_helper import removed - unused


def createMarkdown(date, filename):
    with open(filename, 'w') as f:
        f.write("## " + date + "\n")


def checkPathExist(path):
    if not os.path.exists(path):
        os.makedirs(path)


def scrape_trending(filename):
    """获取 GitHub Trending 总榜（15条）"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    url = 'https://github.com/trending'
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    d = pq(r.content)
    items = d('div.Box article.Box-row')

    # 只获取前15条
    items = items[:15]

    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n### 今日热榜 Top 15\n\n')
        for idx, item in enumerate(items, 1):
            i = pq(item)
            title = i(".lh-condensed a").text()
            description = i("p.col-9").text()
            url = i(".lh-condensed a").attr("href")
            url = "https://github.com" + url

            # 获取编程语言标签
            language_span = i("span[itemprop='programmingLanguage']")
            language = language_span.text() if language_span else "Unknown"

            # 获取星标数
            stars_link = i("a[href*='/stargazers']")
            stars = stars_link.text().strip() if stars_link else ""

            f.write(u"{idx}. **[{title}]({url})**\n".format(idx=idx, title=title, url=url))
            if description:
                f.write(u"   > {description}\n".format(description=description))
            f.write(u"   📦 {language} ⭐ {stars}\n\n".format(language=language, stars=stars))


def job():
    """主任务函数 - 获取 GitHub Trending 总榜"""
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    stryear = datetime.datetime.now().strftime('%Y')

    # 输出目录改为 output/github-trending/{YEAR}/
    output_dir = os.path.join('output', 'github-trending', stryear)
    checkPathExist(output_dir)
    filename = os.path.join(output_dir, f'{strdate}.md')

    # 创建文件标题
    createMarkdown(strdate, filename)

    # 获取总榜数据
    scrape_trending(filename)

    print(f"✓ GitHub trending data saved to: {filename}")


if __name__ == '__main__':
    job()