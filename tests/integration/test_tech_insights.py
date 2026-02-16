# test_tech_insights.py
"""
技术行业动态完整流程集成测试
"""
import os
import sys
from datetime import datetime

def test_full_pipeline():
    """测试完整的数据收集和分析流程"""
    print("=" * 60)
    print("测试技术行业动态完整流程")
    print("=" * 60)

    # 导入任务
    from tasks.hackernews import HackerNewsTask
    from tasks.producthunt import ProductHuntTask
    from tasks.techblogs import TechBlogsTask
    from tasks.tech_insights import TechInsightsTask
    from tasks.wecom_robot import WeComNotifier

    today = datetime.now().strftime('%Y-%m-%d')

    # 1. 测试数据收集任务
    print("\n=== 第一阶段：数据收集 ===\n")
    data_tasks = [
        HackerNewsTask(),
        ProductHuntTask(),
        TechBlogsTask()
    ]

    for task in data_tasks:
        print(f"\n测试 {task.TASK_ID}...")
        result = task.execute()
        if result:
            print(f"✓ {task.TASK_ID} 成功")
        else:
            print(f"✗ {task.TASK_ID} 失败")
            sys.exit(1)

    # 2. 测试AI分析任务
    print(f"\n=== 第二阶段：AI分析 ===\n")
    print(f"测试 tech_insights...")
    insights_task = TechInsightsTask()
    result = insights_task.execute()
    if result:
        print(f"✓ tech_insights 成功")
    else:
        print(f"✗ tech_insights 失败")
        sys.exit(1)

    # 3. 验证输出文件
    print(f"\n=== 第三阶段：验证输出 ===\n")
    required_files = [
        f"output/hackernews/{today}.json",
        f"output/producthunt/{today}.json",
        f"output/techblogs/{today}.json",
        f"output/tech-insights/{today}.md"
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✓ 文件存在: {file_path} ({file_size} bytes)")
        else:
            print(f"✗ 文件不存在: {file_path}")
            sys.exit(1)

    # 4. 测试通知器（可选，需要设置WECHAT_WEBHOOK）
    print(f"\n=== 第四阶段：测试通知 ===\n")
    webhook = os.getenv("WECOM_WEBHOOK_URL")
    if webhook:
        print(f"测试 WeComNotifier...")
        notifier = WeComNotifier()
        results = {
            'ai_news': False,
            'tech_insights': True,
            'github_trending': False,
            'trending_ai': False
        }
        result = notifier.send(results)
        if result:
            print(f"✓ WeComNotifier 成功")
        else:
            print(f"✗ WeComNotifier 失败")
    else:
        print("⚠️ 未设置WECOM_WEBHOOK_URL环境变量，跳过通知测试")

    # 5. 总结
    print(f"\n{'=' * 60}")
    print("✓ 所有测试通过")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    test_full_pipeline()
