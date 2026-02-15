# tasks/trending_ai.py
# coding:utf-8
"""
GitHub Trending AI 分析脚本
读取 GitHub Trending 数据，调用 AI 进行分析，生成分析报告
"""

import datetime
import os
import requests
import codecs

from core.base import Task


class TrendingAITask(Task):
    """GitHub Trending AI分析任务"""

    TASK_ID = "trending_ai"
    PRIORITY = 30

    def execute(self) -> bool:
        """读取trending数据并调用AI分析"""
        print("\n" + "="*60)
        print("GitHub Trending AI 分析")
        print("="*60)

        # 1. 读取 trending 数据
        strdate = self.get_today()
        stryear = self.get_year()
        trending_file = f'{stryear}/{strdate}.md'

        if not os.path.exists(trending_file):
            print(f"✗ 未找到 trending 数据文件: {trending_file}")
            return False

        trending_content = self._read_trending_data(trending_file)
        if not trending_content:
            return False

        # 2. 调用 AI 分析
        analysis = self._call_ai_analysis(trending_content)
        if not analysis:
            print("\nAI 分析未完成，跳过保存步骤")
            return False

        # 3. 保存分析结果
        analysis_file = f'{stryear}/{strdate}-analysis.md'
        success = self._save_analysis(analysis, analysis_file)

        if success:
            print("\n" + "="*60)
            print("✓ AI 分析任务完成")
            print(f"原始数据: {trending_file}")
            print(f"分析报告: {analysis_file}")
            print("="*60)
            return True
        else:
            return False

    def _read_trending_data(self, filename):
        """读取trending markdown文件内容"""
        try:
            with codecs.open(filename, 'r', 'utf-8') as f:
                content = f.read()
            print(f"✓ 成功读取 trending 数据: {filename}")
            return content
        except Exception as e:
            print(f"✗ 读取trending数据失败: {str(e)}")
            return None

    def _call_ai_analysis(self, trending_content):
        """调用 ZhipuAI (GLM-4) 进行分析"""
        api_key = os.environ.get('BIGMODEL_API_KEY')
        if not api_key:
            print("警告: 未设置 BIGMODEL_API_KEY 环境变量，跳过 AI 分析")
            print("提示: 如需启用 AI 分析，请设置环境变量: export BIGMODEL_API_KEY=your_key")
            return None

        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

        # 构建分析 prompt
        prompt = f"""请分析以下 GitHub Trending 数据，提供以下内容：

1. **趋势概览**: 总结今天的整体趋势，有哪些突出的技术方向？
2. **热门项目分析**: 选取 3-5 个最有趣或最受欢迎的项目，详细介绍它们的特点、价值和应用场景
3. **技术趋势**: 从这些项目中分析出当前的技术趋势（如 AI、Web3、云原生等）
4. **推荐关注**: 列出值得开发者关注和学习的项目

请用中文回答，使用 markdown 格式，保持专业但易懂的语气。

---
GitHub Trending 数据:
{trending_content}
"""

        payload = {
            "model": "glm-4",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个技术专家，擅长分析开源项目和技术趋势。请用中文回答，使用清晰的 markdown 格式。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            print("正在调用 AI 分析...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                analysis = result['choices'][0]['message']['content']
                print("✓ AI 分析完成")
                return analysis
            else:
                print("✗ AI 响应格式异常")
                return None

        except requests.exceptions.Timeout:
            print("✗ AI 请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"✗ AI 请求失败 - {str(e)}")
            return None
        except Exception as e:
            print(f"✗ AI 分析过程出错 - {str(e)}")
            return None

    def _save_analysis(self, analysis_content, output_filename):
        """保存AI分析结果到文件"""
        try:
            with codecs.open(output_filename, 'w', 'utf-8') as f:
                # 添加标题
                strdate = self.get_today()
                f.write(f"# GitHub Trending AI 分析报告\n\n")
                f.write(f"> 分析日期: {strdate}\n\n")
                f.write("---\n\n")
                f.write(analysis_content)

            print(f"✓ 分析结果已保存: {output_filename}")
            return True
        except Exception as e:
            print(f"✗ 保存分析结果失败 - {str(e)}")
            return False


# Allow direct execution for testing
if __name__ == '__main__':
    task = TrendingAITask()
    task.execute()
