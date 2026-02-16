# coding:utf-8
"""
测试新的输出目录结构
"""

import os
import datetime

def test_path_structure():
    """测试输出路径结构"""

    # 模拟日期
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    year = datetime.datetime.now().strftime('%Y')

    print("=" * 80)
    print("新的输出目录结构")
    print("=" * 80)

    print("\n1. AI 新闻输出路径:")
    print("   旧: output/ai-news/YYYY-MM-DD.json")
    print(f"   新: output/ai-news/{year}/{today}.json")
    print("   ✅ 按年份组织，便于管理")

    print("\n2. GitHub Trending 输出路径:")
    print(f"   新: output/github-trending/{year}/{today}.md")
    print("   ✅ 按年份组织（已实现）")

    print("\n3. AI 分析报告输出路径:")
    print(f"   新: output/github-trending/{year}/{today}-analysis.md")
    print("   ✅ 与 trending 在同一目录")

    print("\n" + "=" * 80)
    print("完整目录树:")
    print("=" * 80)
    print("""
output/
├── ai-news/                    # AI 新闻
│   ├── 2025/                   # 2025年
│   │   ├── 2025-12-31.json
│   │   └── ...
│   └── 2026/                   # 2026年
│       ├── 2026-01-01.json
│       ├── 2026-01-02.json
│       └── 2026-02-16.json
│
└── github-trending/            # GitHub Trending
    ├── 2025/                   # 2025年
    │   ├── 2025-12-31.md
    │   ├── 2025-12-31-analysis.md
    │   └── ...
    └── 2026/                   # 2026年
        ├── 2026-01-01.md
        ├── 2026-01-01-analysis.md
        ├── 2026-02-16.md
        └── 2026-02-16-analysis.md
    """)

    print("\n" + "=" * 80)
    print("优势:")
    print("=" * 80)
    print("""
✅ 按年份组织，结构清晰
✅ 便于归档和历史数据查询
✅ 避免单个目录文件过多
✅ 与 GitHub Trending 结构一致
✅ 易于备份和管理
    """)

if __name__ == '__main__':
    test_path_structure()
