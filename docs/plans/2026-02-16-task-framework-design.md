# Task Framework Design Document

**Date:** 2026-02-16
**Author:** Claude Code
**Status:** Design Phase

## Overview

### Goal
Refactor the current numbered-script system into a robust task framework using base classes, providing clear separation of concerns, explicit dependencies, and independent testability.

### Current Problems
1. ❌ Numbered filenames (1., 2., 3., 4.) make reordering difficult
2. ❌ Implicit dependencies between scripts
3. ❌ Doesn't scale well for 20+ scripts
4. ❌ Hard to test scripts independently

### Solution
Task Framework with 2 base classes:
- **Task** - For data fetching/analysis jobs (ai_news, github_trending, trending_ai)
- **Notifier** - For notification modules (wecom_robot, future: email, slack)

### Key Benefits
✅ No more numbered filenames
✅ Explicit priority-based execution
✅ Independent task execution and testing
✅ Easy to add new tasks and notifiers
✅ Clear separation of concerns

---

## Architecture

### Directory Structure

```
github-schedule/
├── main.py              # Entry point (simplified)
├── core/
│   ├── __init__.py
│   ├── base.py          # Task and Notifier base classes
│   └── runner.py        # Task discovery and execution
├── tasks/               # All tasks (flat structure)
│   ├── __init__.py
│   ├── ai_news.py           # Inherits Task
│   ├── github_trending.py   # Inherits Task
│   ├── trending_ai.py       # Inherits Task
│   └── wecom_robot.py       # Inherits Notifier
├── utils/               # Keep existing
└── output/              # Keep existing
```

### Core Components

#### 1. core/base.py - Base Classes

**Task Base Class:**
```python
class Task(ABC):
    TASK_ID: str = ""          # Unique identifier (required)
    PRIORITY: int = 100        # Execution order (lower = earlier)

    @abstractmethod
    def execute(self) -> bool:
        """Execute task, return success/failure"""
        pass

    def get_output_path(self, filename: str) -> str:
        """Get output file path"""
        pass

    def get_today(self) -> str:
        """Get today's date YYYY-MM-DD"""
        pass
```

**Notifier Base Class:**
```python
class Notifier(ABC):
    NOTIFIER_ID: str = ""
    SUBSCRIBE_TO: List[str] = []  # List of task IDs to subscribe

    @abstractmethod
    def send(self, task_results: Dict[str, Any]) -> bool:
        """
        Send notification
        task_results: {'ai_news': True, 'github_trending': False, ...}
        """
        pass
```

#### 2. core/runner.py - Execution Engine

**Responsibilities:**
- Discover all Task and Notifier classes in `tasks/`
- Execute tasks by PRIORITY order
- Collect execution results
- Execute notifiers with task results

```python
class TaskRunner:
    def discover(self):
        """Scan tasks/ directory, load all Task and Notifier subclasses"""
        pass

    def run_tasks(self) -> Dict[str, bool]:
        """Execute all tasks sorted by PRIORITY"""
        pass

    def run_notifiers(self, task_results: Dict[str, bool]):
        """Execute all notifiers"""
        pass
```

### Task Examples

#### ai_news.py
```python
class AINewsTask(Task):
    TASK_ID = "ai_news"
    PRIORITY = 10

    def execute(self) -> bool:
        # Fetch from https://ai-bot.cn/daily-ai-news/
        # Save to output/ai-news/YYYY-MM-DD.json
        return True  # or False on failure
```

#### github_trending.py
```python
class GitHubTrendingTask(Task):
    TASK_ID = "github_trending"
    PRIORITY = 20

    def execute(self) -> bool:
        # Scrape GitHub trending for python, javascript, go, java
        # Save to output/YYYY/YYYY-MM-DD.md
        return True
```

#### trending_ai.py
```python
class TrendingAITask(Task):
    TASK_ID = "trending_ai"
    PRIORITY = 30

    def execute(self) -> bool:
        # Read output/YYYY/YYYY-MM-DD.md
        # Call ZhipuAI API for analysis
        # Save to output/YYYY/YYYY-MM-DD-analysis.md
        return True
```

#### wecom_robot.py
```python
class WeComNotifier(Notifier):
    NOTIFIER_ID = "wecom"
    SUBSCRIBE_TO = ["ai_news"]  # Only subscribe to ai_news

    def send(self, task_results: Dict[str, Any]) -> bool:
        # Check if ai_news succeeded
        if "ai_news" in task_results and task_results["ai_news"]:
            # Read output/ai-news/YYYY-MM-DD.json
            # Send to WeChat Work webhook
            return True
        return False
```

---

## Data Flow

```
1. main.py starts
   ↓
2. TaskRunner.discover()
   - Scan tasks/ directory
   - Load all Task and Notifier subclasses
   ↓
3. TaskRunner.run_tasks()
   - Sort tasks by PRIORITY
   - Execute: ai_news(10) → github_trending(20) → trending_ai(30)
   - Collect results: {"ai_news": True, "github_trending": True, "trending_ai": True}
   ↓
4. TaskRunner.run_notifiers(task_results)
   - For each Notifier:
     - WeComNotifier checks SUBSCRIBE_TO = ["ai_news"]
     - If ai_news succeeded, read output/ai-news/YYYY-MM-DD.json
     - Send to WeChat Work webhook
   ↓
5. Print statistics
   Total: 3 tasks, 1 notifier
   Success: 3
   Failed: 0
```

**Task Output Convention:**
- `ai_news`: → `output/ai-news/YYYY-MM-DD.json`
- `github_trending`: → `output/YYYY/YYYY-MM-DD.md`
- `trending_ai`: → `output/YYYY/YYYY-MM-DD-analysis.md`

---

## Error Handling

### Multi-Level Strategy

**1. Task Level:**
- Each task wraps logic in try-catch
- Failure returns False, doesn't affect other tasks
- Prints clear error message

**2. Notifier Level:**
- If subscribed task failed, skip notification
- Notification failure doesn't affect other notifiers

**3. Runner Level:**
- Track success/failure count
- Exit code: 0 = all success, 1 = some failures

### Example Error Handling

```python
def execute(self) -> bool:
    try:
        # Task logic
        return True
    except requests.Timeout:
        print(f"[{self.TASK_ID}] Request timeout")
        return False
    except Exception as e:
        print(f"[{self.TASK_ID}] Error: {e}")
        return False
```

---

## Testing Strategy

### Independent Task Testing

**Run single task directly:**
```bash
# Method 1: Direct module execution
python -m tasks.ai_news

# Method 2: Import and run
python -c "from tasks.ai_news import AINewsTask; AINewsTask().execute()"
```

**Mock Mode:**
- Environment variable: `MOCK_MODE=true`
- Tasks read from cached files instead of real HTTP requests
- Useful for development and testing

### Example Test Script

```python
# test_tasks.py
from tasks.ai_news import AINewsTask
from tasks.github_trending import GitHubTrendingTask

def test_ai_news():
    task = AINewsTask()
    result = task.execute()
    assert result == True
    # Check output file exists

def test_github_trending():
    task = GitHubTrendingTask()
    result = task.execute()
    assert result == True
```

---

## Migration Plan

### Phase 1: Create Framework
- [ ] Create `core/__init__.py`
- [ ] Create `core/base.py` with Task and Notifier base classes
- [ ] Create `core/runner.py` with TaskRunner
- [ ] Update `main.py` to use TaskRunner

### Phase 2: Migrate Tasks
- [ ] Refactor `script/1.ai-news.py` → `tasks/ai_news.py`
  - Create AINewsTask class
  - Move fetch and parse logic
  - Test independently
- [ ] Refactor `script/2.github-trending.py` → `tasks/github_trending.py`
  - Create GitHubTrendingTask class
  - Move scraping logic
  - Test independently
- [ ] Refactor `script/3.ai-analyze-trending.py` → `tasks/trending_ai.py`
  - Create TrendingAITask class
  - Move AI analysis logic
  - Test independently
- [ ] Refactor `script/4.wecom-robot.py` → `tasks/wecom_robot.py`
  - Create WeComNotifier class
  - Move notification logic
  - Test independently

### Phase 3: Validation
- [ ] Run full pipeline: `python main.py`
- [ ] Verify output files match current format
- [ ] Test WeChat Work notification
- [ ] Test error handling (kill network, etc.)

### Phase 4: Cleanup
- [ ] Remove old `script/` directory
- [ ] Update CLAUDE.md documentation
- [ ] Update GitHub Actions workflow if needed

---

## Future Extensibility

### Adding New Tasks

**Example: Add Hacker News scraping**

```python
# tasks/hackernews.py
from core.base import Task

class HackerNewsTask(Task):
    TASK_ID = "hackernews"
    PRIORITY = 15

    def execute(self) -> bool:
        # Fetch and save HN stories
        return True
```

### Adding New Notifiers

**Example: Add email notification**

```python
# tasks/email_notifier.py
from core.base import Notifier

class EmailNotifier(Notifier):
    NOTIFIER_ID = "email"
    SUBSCRIBE_TO = ["ai_news", "trending_ai"]  # Multiple subscriptions

    def send(self, task_results: Dict[str, Any]) -> bool:
        # Send email digest
        return True
```

### Advanced Features (Future)

- **Parallel execution**: Run independent tasks concurrently
- **Retries**: Automatic retry with exponential backoff
- **Rate limiting**: Built-in rate limiting for API calls
- **Task dependencies**: Explicit dependency graph
- **Scheduling**: Cron-like scheduling per task

---

## Design Decisions

### Q: Why only 2 base classes?
**A:** Simplicity. All current scripts are either data jobs (Task) or notifications (Notifier). No need for over-engineering.

### Q: Why flat tasks/ directory?
**A:** Current system only has 4 tasks. Flat structure is simpler. Can reorganize into subdirectories when we have 20+ tasks.

### Q: Why PRIORITY instead of dependency graph?
**A:** Current workflow is linear. Priority is simpler and sufficient. Can upgrade to DAG if needed in the future.

### Q: Why SUBSCRIBE_TO in Notifier?
**A:** Allows flexible notification composition. A notifier can subscribe to multiple tasks, and tasks can have multiple notifiers.

---

## Success Criteria

- [ ] All existing functionality works
- [ ] Tasks can run independently
- [ ] Easy to add new tasks without modifying existing code
- [ ] Clear error messages on failure
- [ ] Output format remains compatible
- [ ] WeChat Work notification works

---

## Open Questions

1. Should we add a `--dry-run` flag to main.py?
2. Should we add logging (use Python logging module)?
3. Should tasks be configurable via YAML/JSON?

**Decisions:** Defer to implementation phase based on needs.

---

## Appendix: File-by-File Migration

### script/1.ai-news.py → tasks/ai_news.py

**Changes:**
- Wrap in `class AINewsTask(Task)`
- `job()` → `execute(self)`
- Keep functions: `fetch_ai_news()`, `parse_news_from_file()`
- Use `self.get_output_path()` and `self.get_today()`

### script/2.github-trending.py → tasks/github_trending.py

**Changes:**
- Wrap in `class GitHubTrendingTask(Task)`
- `job()` → `execute(self)`
- Keep functions: `createMarkdown()`, `checkPathExist()`, `scrape()`

### script/3.ai-analyze-trending.py → tasks/trending_ai.py

**Changes:**
- Wrap in `class TrendingAITask(Task)`
- `job()` → `execute(self)`
- Keep functions: `get_trending_markdown_path()`, `read_trending_data()`, `call_ai_analysis()`

### script/4.wecom-robot.py → tasks/wecom_robot.py

**Changes:**
- Wrap in `class WeComNotifier(Notifier)`
- `job()` → `send(self, task_results)`
- Check `task_results["ai_news"]` before reading file
- Keep functions: `create_content_from_json()`, `send_wecom_message()`

---

**End of Design Document**
