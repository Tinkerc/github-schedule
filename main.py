# main.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path for imports
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from core.runner import TaskRunner

# 加载 .env 文件中的环境变量
load_dotenv()


def main():
    print("="*60)
    print("GitHub Schedule Automation System")
    print("="*60)

    

    # 创建任务执行器
    runner = TaskRunner(tasks_dir=str(src_path / "tasks"))

    # 发现所有任务和通知器
    print("\n发现任务和通知器...")
    runner.discover()

    # 执行所有任务
    task_results = runner.run_tasks()

    # 执行所有通知器
    runner.run_notifiers(task_results)

    # 打印摘要
    runner.print_summary(task_results)

    # 返回退出码
    total = len(task_results)
    failed = sum(1 for v in task_results.values() if not v)
    return 1 if failed > 0 else 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
