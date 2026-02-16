# core/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import os
import json

class Task(ABC):
    """任务基类 - 所有数据获取/分析任务继承此类"""

    TASK_ID: str = ""          # 子类必须定义
    PRIORITY: int = 100        # 执行优先级，数字越小越先执行

    @abstractmethod
    def execute(self) -> bool:
        """
        执行任务
        返回: bool (成功=True, 失败=False)
        """
        pass

    def get_output_path(self, filename: str) -> str:
        """获取输出文件路径"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, 'output')

        # 如果文件路径包含子目录，创建它们
        if '/' in filename:
            subdir = os.path.dirname(filename)
            full_dir = os.path.join(output_dir, subdir)
            os.makedirs(full_dir, exist_ok=True)
        else:
            os.makedirs(output_dir, exist_ok=True)

        return os.path.join(output_dir, filename)

    def get_today(self) -> str:
        """获取今天的日期 YYYY-MM-DD"""
        return datetime.now().strftime('%Y-%m-%d')

    def get_year(self) -> str:
        """获取当前年份 YYYY"""
        return datetime.now().strftime('%Y')


class Notifier(ABC):
    """通知基类 - 所有通知模块继承此类"""

    NOTIFIER_ID: str = ""
    SUBSCRIBE_TO: List[str] = []  # 订阅的任务ID列表

    @abstractmethod
    def send(self, task_results: Dict[str, Any]) -> bool:
        """
        发送通知
        task_results: {
            'ai_news': True/False,
            'github_trending': True/False,
            ...
        }
        返回: bool (成功=True, 失败=False)
        """
        pass
