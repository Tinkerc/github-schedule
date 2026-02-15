# tasks/tech_insights.py
from core.base import Task
import os
import json
from typing import List, Dict, Any

class TechInsightsTask(Task):
    """综合分析所有数据源，生成技术行业简报"""

    TASK_ID = "tech_insights"
    PRIORITY = 40

    def execute(self) -> bool:
        """执行AI分析"""
        try:
            print(f"[{self.TASK_ID}] 开始生成技术行业简报...")

            # 读取所有数据源
            hn_data = self._read_json(f"hackernews/{self.get_today()}.json")
            ph_data = self._read_json(f"producthunt/{self.get_today()}.json")
            tb_data = self._read_json(f"techblogs/{self.get_today()}.json")

            # 检查可用数据源
            available_sources = []
            if hn_data:
                available_sources.append("hackernews")
            if ph_data:
                available_sources.append("producthunt")
            if tb_data:
                available_sources.append("techblogs")

            if not available_sources:
                print(f"[{self.TASK_ID}] ✗ 所有数据源均不可用")
                return False

            print(f"[{self.TASK_ID}] 可用数据源: {', '.join(available_sources)}")

            # 构建AI提示词
            prompt = self._build_prompt(hn_data, ph_data, tb_data)

            # 调用AI分析（暂时使用Mock）
            # TODO: 下一步集成真实ZhipuAI API
            insights = self._mock_ai_analysis(prompt)

            # 保存简报
            output_path = self.get_output_path(f"tech-insights/{self.get_today()}.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)

            print(f"[{self.TASK_ID}] ✓ 技术简报生成成功")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")
            return True

        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ 错误: {str(e)}")
            return False

    def _read_json(self, filepath: str) -> List:
        """读取JSON文件，不存在返回None"""
        full_path = self.get_output_path(filepath)
        if not os.path.exists(full_path):
            return None
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _build_prompt(self, hn_data: List, ph_data: List, tb_data: List) -> str:
        """构建AI分析提示词"""
        prompt = f"""你是一位技术行业分析师。请基于以下数据源，生成一份简洁的技术行业动态简报。

## 数据源

### 1. Hacker News Top 30
{self._format_hn_data(hn_data or [])}

### 2. Product Hunt Top 20
{self._format_ph_data(ph_data or [])}

### 3. 技术博客热门文章
{self._format_tb_data(tb_data or [])}

## 分析要求

请按以下结构生成简报（使用中文，控制在1000字以内）：

# 技术行业动态简报 - {self.get_today()}

## 🔥 今日热门技术话题
（基于Hacker News讨论热度，总结前3个最受关注的技术话题）

## 🚀 新兴热门项目
（从HN和Product Hunt中挑选5个最有趣的新项目/工具，每个用2-3句话描述）

## 📊 技术趋势观察
（分析数据中的趋势，例如：AI工具占比、编程语言热度、新技术栈兴起等）

## 🤖 AI前沿动态
（专门提取AI相关的重要更新、新工具、讨论热点）

## 🛠️ 新工具推荐
（从Product Hunt挑选3-5个值得推荐的实用工具，简短说明用途）

## 💡 技术洞察
（基于所有数据，给出1-2个你对当前技术行业的观察或见解）

---
*数据来源：Hacker News Top 30, Product Hunt Top 20, 技术博客热门文章*
"""
        return prompt

    def _format_hn_data(self, data: List) -> str:
        """格式化HN数据"""
        if not data:
            return "（无数据）"
        formatted = []
        for item in data[:10]:
            formatted.append(f"- {item['title']} ({item['points']} points, {item['comments_count']} comments)")
        return '\n'.join(formatted)

    def _format_ph_data(self, data: List) -> str:
        """格式化Product Hunt数据"""
        if not data:
            return "（无数据）"
        formatted = []
        for item in data[:10]:
            formatted.append(f"- **{item['name']}**: {item['description']} ({item['votes_count']} votes)")
        return '\n'.join(formatted)

    def _format_tb_data(self, data: List) -> str:
        """格式化技术博客数据"""
        if not data:
            return "（无数据）"
        formatted = []
        for item in data[:10]:
            formatted.append(f"- **{item['title']}** by {item['author']} ({item['source']})")
        return '\n'.join(formatted)

    def _mock_ai_analysis(self, prompt: str) -> str:
        """Mock AI分析（开发测试用）"""
        return f"""# 技术行业动态简报 - {self.get_today()}

## 🔥 今日热门技术话题

1. **WebAssembly技术突破** - HN上多个关于WASM的高讨论帖子，平均200+ comments
2. **AI代码助手工具竞赛** - 多款AI编程工具同时发布，竞争激烈
3. **Rust语言生态扩张** - 更多工具和框架选择Rust重写核心模块

## 🚀 新兴热门项目

1. **Rust-based AI Framework**
   新的高性能AI推理框架，比现有方案快3倍

2. **WebAssembly IDE**
   基于浏览器的完整IDE体验，支持多种语言

3. **Auto-GPT Advanced**
   自主AI助手的增强版本，支持更多工具集成

## 📊 技术趋势观察

- AI工具占比持续上升：今日HN Top 30中AI相关占40%
- Rust生态快速增长：工具类项目选择Rust重写成为趋势
- WebAssembly进入实用阶段：生产级应用开始涌现

## 🤖 AI前沿动态

- 多模态模型性能提升：新模型在视觉理解任务上表现优异
- AI代码助手领域竞争激烈：至少3款新工具发布
- 边缘AI计算受到关注：轻量级模型需求增长

## 🛠️ 新工具推荐

1. **WASM Studio** - WebAssembly开发专用IDE
2. **RustML** - Rust机器学习框架
3. **AI Code Review** - 自动代码审查工具

## 💡 技术洞察

基于今日数据分析，观察到**WebAssembly正在从实验技术转向生产可用**。多款生产级WASM工具的发布表明这项技术已经成熟。同时，AI工具开发进入**差异化竞争阶段**，通用型助手逐渐让位于垂直领域的专业工具。

---
*本简报由AI自动生成 | 数据来源: Hacker News, Product Hunt, 技术博客*
"""
