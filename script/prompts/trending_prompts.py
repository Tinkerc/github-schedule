# coding:utf-8
"""GitHub Trending AI 分析的 Prompt 模板"""


def get_batch_analysis_prompt(projects):
    """
    生成批量分析项目详情的 prompt

    Args:
        projects: list[dict], 项目列表，每个项目包含 name, description, url, stars, language, stars_today

    Returns:
        str: AI 分析的 prompt
    """
    projects_text = ""
    for i, p in enumerate(projects, 1):
        projects_text += f"""
{i}. {p.get('name', 'Unknown')}
   描述: {p.get('description', '暂无描述')}
   语言: {p.get('language', '未知')}
   星标: {p.get('stars', 'N/A')} (今日 +{p.get('stars_today', 'N/A')})
   链接: {p.get('url', '')}
"""

    prompt = f"""你是一个技术分析师，擅长分析开源项目的技术价值和实用价值。

请分析以下 {len(projects)} 个 GitHub Trending 项目，对每个项目提供详细分析。

项目列表：
{projects_text}

请严格按照以下 JSON 格式返回分析结果：
{{
    "projects": [
        {{
            "name": "项目名称",
            "core_functionality": "核心功能（1-2句话）",
            "use_cases": "适用场景（3-4个要点，用换行符分隔）",
            "tech_stack": "技术栈（关键依赖/框架）",
            "tech_highlights": "技术亮点（2-3个要点，用换行符分隔）",
            "learning_value": "学习价值（1-2句话）"
        }}
    ]
}}

注意：
1. 必须返回有效的 JSON 格式，不要包含其他文字
2. core_functionality 简洁明了，说明项目做什么
3. use_cases 要具体，说明在什么场景下使用
4. tech_stack 列出关键技术和框架
5. tech_highlights 突出技术创新点
6. learning_value 说明开发者能学到什么
"""

    return prompt


def get_trend_summary_prompt(analyses):
    """
    生成趋势概览和热门领域分析的 prompt

    Args:
        analyses: dict, 包含所有项目的分析结果

    Returns:
        str: AI 分析的 prompt
    """
    projects_info = ""
    for p in analyses.get('projects', []):
        projects_info += f"""
- {p.get('name', 'Unknown')}: {p.get('core_functionality', '')}
  技术栈: {p.get('tech_stack', '未知')}
  技术亮点: {p.get('tech_highlights', '')}
"""

    prompt = f"""你是一个技术趋势分析师，擅长发现技术发展动向。

基于以下 {len(analyses.get('projects', []))} 个项目的分析结果，生成趋势概览和热门领域分析。

项目分析：
{projects_info}

请严格按照以下 JSON 格式返回：
{{
    "trend_overview": "今日趋势概览（3-5句话，描述整体技术趋势特点、创新方向、热门话题等）",
    "hot_domains": [
        {{
            "domain": "领域名称（如 AI/LLM、Web3、DevOps 等）",
            "reason": "热门原因（2-3句话）",
            "projects": ["相关项目名称1", "相关项目名称2"]
        }}
    ]
}}

注意：
1. 必须返回有效的 JSON 格式
2. trend_overview 要宏观描述整体趋势
3. hot_domains 提取 3-5 个热门领域
4. 每个领域要说明为什么热门，并列出相关项目
"""

    return prompt
