"""
Unit tests for core.base module
Tests Task and Notifier base classes
"""
import pytest
from datetime import datetime

from core.base import Task, Notifier


class MockTask(Task):
    """Mock task implementation for testing"""
    TASK_ID = "test_task"
    PRIORITY = 50

    def execute(self) -> bool:
        return True


class AnotherMockTask(Task):
    """Another mock task for testing priority ordering"""
    TASK_ID = "another_task"
    PRIORITY = 10

    def execute(self) -> bool:
        return True


class MockNotifier(Notifier):
    """Mock notifier implementation for testing"""
    NOTIFIER_ID = "test_notifier"
    SUBSCRIBE_TO = ["test_task", "another_task"]

    def send(self, task_results) -> bool:
        return all(task_results.values())


class TestTask:
    """Test Task base class"""

    def test_task_has_required_attributes(self):
        """Task should have TASK_ID and PRIORITY"""
        task = MockTask()
        assert task.TASK_ID == "test_task"
        assert task.PRIORITY == 50
        assert hasattr(task, 'execute')

    def test_get_output_path_creates_directories(self, tmp_path):
        """get_output_path should create nested directories"""
        task = MockTask()

        # Mock the project root to use temp directory
        import os
        original_dir = os.path.dirname
        os.path.dirname = lambda x: str(tmp_path)

        try:
            output_path = task.get_output_path('test/subdir/file.json')
            assert 'test/subdir/file.json' in output_path
        finally:
            os.path.dirname = original_dir

    def test_get_today_returns_correct_format(self):
        """get_today should return YYYY-MM-DD format"""
        task = MockTask()
        today = task.get_today()
        assert len(today) == 10  # YYYY-MM-DD
        assert today.count('-') == 2

        # Verify it's a valid date
        datetime.strptime(today, '%Y-%m-%d')

    def test_get_year_returns_correct_format(self):
        """get_year should return YYYY format"""
        task = MockTask()
        year = task.get_year()
        assert len(year) == 4  # YYYY
        assert year.isdigit()

    def test_execute_returns_bool(self):
        """execute method should return boolean"""
        task = MockTask()
        result = task.execute()
        assert isinstance(result, bool)
        assert result is True


class TestNotifier:
    """Test Notifier base class"""

    def test_notifier_has_required_attributes(self):
        """Notifier should have NOTIFIER_ID and SUBSCRIBE_TO"""
        notifier = MockNotifier()
        assert notifier.NOTIFIER_ID == "test_notifier"
        assert notifier.SUBSCRIBE_TO == ["test_task", "another_task"]
        assert hasattr(notifier, 'send')

    def test_send_returns_bool(self):
        """send method should return boolean"""
        notifier = MockNotifier()
        result = notifier.send({"test_task": True, "another_task": True})
        assert isinstance(result, bool)
        assert result is True

    def test_send_with_failed_task(self):
        """send should handle failed tasks"""
        notifier = MockNotifier()
        result = notifier.send({"test_task": True, "another_task": False})
        assert result is False  # all() returns False for any False value


class TestTaskPriorityOrdering:
    """Test task priority ordering"""

    def test_tasks_sortable_by_priority(self):
        """Tasks should be sortable by PRIORITY attribute"""
        task1 = MockTask()  # PRIORITY 50
        task2 = AnotherMockTask()  # PRIORITY 10

        tasks = [task1, task2]
        sorted_tasks = sorted(tasks, key=lambda t: t.PRIORITY)

        assert sorted_tasks[0].TASK_ID == "another_task"
        assert sorted_tasks[1].TASK_ID == "test_task"

    def test_priority_lower_executes_first(self):
        """Lower priority number should execute first"""
        assert AnotherMockTask.PRIORITY < MockTask.PRIORITY
