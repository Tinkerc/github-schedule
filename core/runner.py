# core/runner.py
import os
import importlib.util
import sys
from typing import Dict, List, Type
from pathlib import Path

from core.base import Task, Notifier


class TaskRunner:
    """任务执行器 - 发现、执行所有任务和通知器"""

    def __init__(self, tasks_dir: str = "tasks"):
        self.tasks_dir = tasks_dir
        self.tasks: Dict[str, Task] = {}
        self.notifiers: Dict[str, Notifier] = {}

    def discover(self):
        """扫描 tasks/ 目录，加载所有 Task 和 Notifier 子类"""
        tasks_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.tasks_dir)

        if not os.path.exists(tasks_path):
            print(f"错误: 任务目录 {tasks_path} 不存在")
            sys.exit(1)

        # 遍历 tasks/ 目录下的所有 .py 文件
        for filename in os.listdir(tasks_path):
            if not filename.endswith('.py') or filename == '__init__.py':
                continue

            module_name = filename[:-3]  # 移除 .py 扩展名
            module_path = os.path.join(tasks_path, filename)

            try:
                # 动态加载模块
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 查找模块中的 Task 和 Notifier 子类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # 跳过基类本身
                    if attr_name in ['Task', 'Notifier']:
                        continue

                    # 检查是否是 Task 子类
                    if isinstance(attr, type) and issubclass(attr, Task) and attr is not Task:
                        task_instance = attr()
                        if task_instance.TASK_ID:
                            self.tasks[task_instance.TASK_ID] = task_instance
                            print(f"  ✓ 发现任务: {task_instance.TASK_ID}")

                    # 检查是否是 Notifier 子类
                    if isinstance(attr, type) and issubclass(attr, Notifier) and attr is not Notifier:
                        notifier_instance = attr()
                        if notifier_instance.NOTIFIER_ID:
                            self.notifiers[notifier_instance.NOTIFIER_ID] = notifier_instance
                            print(f"  ✓ 发现通知器: {notifier_instance.NOTIFIER_ID}")

            except Exception as e:
                print(f"  警告: 加载 {filename} 失败: {str(e)}")

        print(f"\n发现 {len(self.tasks)} 个任务, {len(self.notifiers)} 个通知器")

    def run_tasks(self) -> Dict[str, bool]:
        """执行所有任务（按优先级排序）"""
        if not self.tasks:
            print("警告: 没有发现任何任务")
            return {}

        # 按优先级排序
        sorted_tasks = sorted(
            self.tasks.items(),
            key=lambda x: x[1].PRIORITY
        )

        print(f"\n执行顺序:")
        for task_id, task in sorted_tasks:
            print(f"  {task.PRIORITY}. {task_id}")

        print(f"\n{'='*60}")
        print("开始执行任务")
        print(f"{'='*60}")

        results = {}
        for task_id, task in sorted_tasks:
            print(f"\n[{task.TASK_ID}] 开始执行...")
            try:
                success = task.execute()
                results[task_id] = success
                if success:
                    print(f"[{task.TASK_ID}] ✓ 执行成功")
                else:
                    print(f"[{task.TASK_ID}] ✗ 执行失败")
            except Exception as e:
                print(f"[{task.TASK_ID}] ✗ 执行异常: {str(e)}")
                results[task_id] = False

        return results

    def run_notifiers(self, task_results: Dict[str, bool]):
        """执行所有通知器"""
        if not self.notifiers:
            print("\n没有发现任何通知器")
            return

        print(f"\n{'='*60}")
        print("开始执行通知")
        print(f"{'='*60}")

        for notifier_id, notifier in self.notifiers.items():
            print(f"\n[{notifier_id}] 开始发送通知...")
            try:
                success = notifier.send(task_results)
                if success:
                    print(f"[{notifier_id}] ✓ 发送成功")
                else:
                    print(f"[{notifier_id}] ✗ 发送失败")
            except Exception as e:
                print(f"[{notifier_id}] ✗ 发送异常: {str(e)}")

    def print_summary(self, task_results: Dict[str, bool]):
        """打印执行摘要"""
        total = len(task_results)
        success = sum(1 for v in task_results.values() if v)
        failed = total - success

        print(f"\n{'='*60}")
        print("执行摘要")
        print(f"{'='*60}")
        print(f"总计任务数: {total}")
        print(f"成功执行: {success}")
        print(f"执行失败: {failed}")
        print(f"{'='*60}")
