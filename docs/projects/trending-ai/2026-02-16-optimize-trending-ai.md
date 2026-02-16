# Optimize Trending AI Task - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate tasks/trending_ai.py from ZhipuAI GLM-4 API to Volcengine Doubao API with enhanced error handling.

**Architecture:** Refactor _call_ai_analysis() method to use Volcengine API endpoint, add comprehensive error handling for HTTP status codes (401, 429, connection errors), update environment variables, and improve system prompt while maintaining Task base class integration.

**Tech Stack:** Python 3.8+, requests library, Task framework (core/base.py), GitHub Actions CI/CD

---

## Task 1: Update Environment Variable Documentation

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md` (if it exists)

**Step 1: Update CLAUDE.md environment variables section**

Find the section that lists required environment variables and update it:

```markdown
Required environment variables:
  - `VOLCENGINE_API_KEY`: For AI analysis in trending_ai task
  - `VOLCENGINE_MODEL`: (optional) Volcengine model endpoint, defaults to 'ep-20250215154848-djsgr'
  - `WECOM_WEBHOOK_URL`: For WeChat Work notifications
```

Replace `BIGMODEL_API_KEY` with `VOLCENGINE_API_KEY` and add `VOLCENGINE_MODEL`.

**Step 2: Check if README.md exists and update it**

Run: `ls README.md`

If file exists:
```bash
# Read the file first to find the env var section
grep -n "BIGMODEL_API_KEY\|API_KEY" README.md
```

Then update any references to use `VOLCENGINE_API_KEY` instead.

**Step 3: Commit documentation changes**

```bash
git add CLAUDE.md README.md
git commit -m "docs: update API key references for Volcengine migration"
```

---

## Task 2: Refactor _call_ai_analysis() Method - Part 1: API Configuration

**Files:**
- Modify: `tasks/trending_ai.py:72-142`

**Step 1: Read current implementation to understand structure**

Read lines 72-142 of tasks/trending_ai.py to see current _call_ai_analysis method.

**Step 2: Update API endpoint and key retrieval**

Replace the method body starting from line 74:

```python
def _call_ai_analysis(self, trending_content):
    """调用 Volcengine (豆包) 大模型 API 进行分析"""
    api_key = os.environ.get('VOLCENGINE_API_KEY')
    if not api_key:
        print("警告: 未设置 VOLCENGINE_API_KEY 环境变量，跳过 AI 分析")
        print("提示: 如需启用 AI 分析，请设置环境变量: export VOLCENGINE_API_KEY=your_key")
        return None

    model = os.environ.get('VOLCENGINE_MODEL', 'ep-20250215154848-djsgr')
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
```

**Step 3: Update system prompt**

Replace the prompt construction section (around line 83):

```python
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
```

**Step 4: Update API payload**

Replace the payload dictionary (around line 97):

```python
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一位资深技术专家，长期关注开源生态与前沿工程实践。请对以下 GitHub 项目列表中的每一个项目，用一句简洁、准确、有洞察力的话进行解读，说明其核心价值、技术特点或潜在影响。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000
    }
```

Note: Remove `"temperature": 0.7` from payload (Volcengine doesn't use it).

**Step 5: Commit API configuration changes**

```bash
git add tasks/trending_ai.py
git commit -m "refactor(trending_ai): update API configuration for Volcengine"
```

---

## Task 3: Refactor _call_ai_analysis() Method - Part 2: Error Handling

**Files:**
- Modify: `tasks/trending_ai.py:119-142`

**Step 1: Update timeout value**

Change the requests.post call timeout parameter:

```python
response = requests.post(url, headers=headers, json=payload, timeout=120)
```

**Step 2: Replace error handling with enhanced version**

Replace the entire try-except block (lines 119-142) with:

```python
    try:
        print("正在调用 AI 分析...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                analysis = result['choices'][0]['message']['content']
                print("✓ AI 分析完成")
                return analysis
            else:
                print("✗ AI 响应格式异常")
                return None
        elif response.status_code == 401:
            print("✗ 认证失败: API Key 无效或已过期")
            return None
        elif response.status_code == 429:
            print("✗ 请求频率超限，请稍后重试")
            return None
        else:
            print(f"✗ API 调用失败 - HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"错误详情: {error_detail}")
            except:
                print(f"响应内容: {response.text[:500]}")
            return None

    except requests.exceptions.Timeout:
        print("✗ AI 请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print("✗ 网络连接错误")
        return None
    except Exception as e:
        print(f"✗ AI 分析过程出错 - {str(e)}")
        return None
```

**Step 3: Verify method signature is unchanged**

Ensure the method still has the same signature:
```python
def _call_ai_analysis(self, trending_content):
```

**Step 4: Commit error handling changes**

```bash
git add tasks/trending_ai.py
git commit -m "refactor(trending_ai): add enhanced error handling for Volcengine API"
```

---

## Task 4: Verify Task Integration

**Files:**
- Modify: `tasks/trending_ai.py` (verification only)

**Step 1: Verify Task class structure**

Ensure the Task class still properly inherits and has correct attributes:

```bash
# Check TASK_ID and PRIORITY are set
grep -A2 "class TrendingAITask" tasks/trending_ai.py
```

Expected output should show:
```python
class TrendingAITask(Task):
    """GitHub Trending AI分析任务"""

    TASK_ID = "trending_ai"
    PRIORITY = 30
```

**Step 2: Verify execute() method is unchanged**

Check that execute() method still uses get_output_path:

```bash
grep -A5 "def execute" tasks/trending_ai.py | head -20
```

Ensure it still calls:
- `_read_trending_data()`
- `_call_ai_analysis()`
- `_save_analysis()`

**Step 3: Verify file path methods are unchanged**

Check that _read_trending_data and _save_analysis don't use hardcoded paths:

```bash
grep "output/" tasks/trending_ai.py
```

Should NOT find any hardcoded `output/github-trending/` paths. The task should use `self.get_year()` and `self.get_today()` for path construction.

**Step 4: Syntax check**

Run Python syntax checker:

```bash
python -m py_compile tasks/trending_ai.py
```

Expected: No syntax errors (silent success)

**Step 5: Commit verification fix (if any changes needed)**

Only commit if you made corrections:

```bash
git add tasks/trending_ai.py
git commit -m "fix(trending_ai): correct task integration issues"
```

---

## Task 5: Manual Testing (Optional but Recommended)

**Files:**
- Test: `tasks/trending_ai.py`

**Step 1: Set up test environment**

Set required environment variables:

```bash
export VOLCENGINE_API_KEY="your-test-key"
export VOLCENGINE_MODEL="ep-20250215154848-djsgr"  # or your custom model
```

**Step 2: Ensure test data exists**

Check if trending data file exists for today:

```bash
# Today's date is 2026-02-16
ls -la output/2026/2026-02-16.md
```

If not exists, create a dummy test file:

```bash
mkdir -p output/2026
echo "# Test Trending Data

## Today's Trending

1. [test/repo](https://github.com/test/repo) - Test repository
" > output/2026/2026-02-16.md
```

**Step 3: Run the task in isolation**

```bash
python -m tasks.trending_ai
```

**Expected outcomes:**

If API key is valid:
- Should see "正在调用 AI 分析..."
- Should see "✓ AI 分析完成"
- Should see "✓ 分析结果已保存"
- Output file: `output/2026/2026-02-16-analysis.md`

If API key is invalid:
- Should see "✗ 认证失败: API Key 无效或已过期"

**Step 4: Verify output file**

If successful, check the generated analysis:

```bash
cat output/2026/2026-02-16-analysis.md
```

Should contain:
- Header with date
- AI-generated analysis content

**Step 5: Clean up test data (optional)**

```bash
# Remove test analysis file
rm output/2026/2026-02-16-analysis.md
```

Note: Don't commit test data or API keys.

---

## Task 6: Final Review and Cleanup

**Files:**
- Review: All modified files

**Step 1: Review all changes**

Show summary of all commits:

```bash
git log --oneline -6
```

**Step 2: Verify no API keys in code**

Check for accidentally committed credentials:

```bash
grep -r "API_KEY\|api_key" tasks/trending_ai.py | grep -v "environ.get"
```

Expected: Should only find `os.environ.get('VOLCENGINE_API_KEY')` and similar patterns.

**Step 3: Diff against original**

Show final diff:

```bash
git diff HEAD~5 tasks/trending_ai.py
```

Verify key changes:
- ✅ VOLCENGINE_API_KEY instead of BIGMODEL_API_KEY
- ✅ Volcengine API endpoint
- ✅ Enhanced error handling (401, 429, ConnectionError)
- ✅ Timeout changed to 120
- ✅ Updated system prompt
- ✅ Model configurable via env var

**Step 4: Run final syntax check**

```bash
python -m py_compile tasks/trending_ai.py && echo "✓ Syntax OK"
```

**Step 5: Check import statements**

Verify all imports are present:

```bash
head -15 tasks/trending_ai.py | grep import
```

Should include:
```python
import os
import requests
import codecs
from core.base import Task
```

**Step 6: Final commit (if any minor fixes needed)**

Only if you made corrections during review:

```bash
git add tasks/trending_ai.py
git commit -m "chore: final cleanup for trending_ai optimization"
```

---

## Task 7: Update GitHub Actions Configuration

**Files:**
- Modify: `.github/workflows/blank.yml` (if it references BIGMODEL_API_KEY)

**Step 1: Check workflow file**

Read the GitHub Actions workflow:

```bash
cat .github/workflows/blank.yml
```

**Step 2: Update secret references (if needed)**

If the workflow references BIGMODEL_API_KEY in secrets or env, update it:

Find and replace any reference to `BIGMODEL_API_KEY` with `VOLCENGINE_API_KEY`.

**Step 3: Commit workflow changes**

```bash
git add .github/workflows/blank.yml
git commit -m "ci: update API key secret reference for Volcengine"
```

---

## Task 8: Documentation Update - Migration Guide

**Files:**
- Create: `docs/MIGRATION_GUIDE.md` (if doesn't exist) or append to existing

**Step 1: Create migration guide**

```markdown
# API Migration Guide

## ZhipuAI → Volcengine Migration (2026-02-16)

The `trending_ai` task has been migrated from ZhipuAI GLM-4 to Volcengine Doubao API.

### Required Actions

If you're running this locally or in your own CI/CD:

1. **Update Environment Variables:**

   **Before:**
   ```bash
   export BIGMODEL_API_KEY="your-key"
   ```

   **After:**
   ```bash
   export VOLCENGINE_API_KEY="your-key"
   export VOLCENGINE_MODEL="ep-20250215154848-djsgr"  # Optional, has default
   ```

2. **Update GitHub Actions Secrets:**

   - Go to: Repository → Settings → Secrets and variables → Actions
   - Remove: `BIGMODEL_API_KEY` (if no longer needed)
   - Add: `VOLCENGINE_API_KEY`
   - Add: `VOLCENGINE_MODEL` (optional)

### Benefits

- ✅ Enhanced error handling (auth failures, rate limiting)
- ✅ Better system prompts for more insightful analysis
- ✅ Configurable model endpoints
- ✅ Improved reliability with longer timeouts

### Rollback

If needed, revert commit: `git revert <commit-hash>`
```

**Step 2: Commit migration guide**

```bash
git add docs/MIGRATION_GUIDE.md
git commit -m "docs: add API migration guide"
```

---

## Success Criteria Verification

After completing all tasks, verify:

- ✅ All commits pushed to branch
- ✅ No syntax errors in Python files
- ✅ Environment variable documentation updated
- ✅ Error handling covers 401, 429, timeout, connection errors
- ✅ Task maintains Task base class structure
- ✅ No hardcoded API keys in code
- ✅ GitHub Actions workflow updated (if needed)

Run final verification:

```bash
# Syntax check all Python files
python -m py_compile tasks/trending_ai.py

# Check for API key leaks
grep -r "sk-\|Bearer\|api.*key" tasks/ --include="*.py" | grep -v "environ\|print\|comment"

# Verify git history
git log --oneline -10
```

---

## Notes for Implementation

- This is a straightforward refactoring task
- No new dependencies required
- Task framework structure remains intact
- The script version (script/ai-analyze-trending.py) can be used as reference
- Focus on clean error messages that help debugging
- Maintain backward compatibility in file paths (uses get_output_path)
- Temperature parameter removed (Volcengine doesn't use it)
- Keep Chinese error messages for consistency with codebase
