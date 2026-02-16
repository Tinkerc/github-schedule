# Optimize Trending AI Task - Design Document

**Date:** 2026-02-16
**Author:** Claude Code
**Status:** Approved

## Overview

Optimize `tasks/trending_ai.py` by migrating from ZhipuAI GLM-4 API to Volcengine Doubao API, incorporating proven improvements from `script/ai-analyze-trending.py` while maintaining the Task framework structure.

## Problem Statement

The current `trending_ai.py` task:
- Uses ZhipuAI GLM-4 API (BIGMODEL_API_KEY)
- Has basic error handling (generic exceptions)
- Fixed 60-second timeout
- Generic system prompt

Meanwhile, `script/ai-analyze-trending.py` has:
- Volcengine Doubao API integration (battle-tested)
- Enhanced error handling (401, 429, connection errors)
- 120-second timeout for better reliability
- More insightful system prompt
- Configurable model endpoint

## Solution: Enhanced Migration

Migrate `trending_ai.py` to Volcengine API while preserving Task framework integration and incorporating all improvements from the script version.

## Architecture

### Class Structure (Unchanged)
```python
class TrendingAITask(Task):
    TASK_ID = "trending_ai"
    PRIORITY = 30

    def execute(self) -> bool:
        # Main orchestration
```

### Configuration Changes

**Environment Variables:**
- **Remove:** `BIGMODEL_API_KEY`
- **Add:** `VOLCENGINE_API_KEY` (required)
- **Add:** `VOLCENGINE_MODEL` (optional, default: `ep-20250215154848-djsgr`)

**API Endpoint:**
- **From:** `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- **To:** `https://ark.cn-beijing.volces.com/api/v3/chat/completions`

### Method Changes

#### `_call_ai_analysis()` - Major Refactor

**Before (GLM-4):**
```python
api_key = os.environ.get('BIGMODEL_API_KEY')
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
model = "glm-4"
timeout = 60
# Generic error handling
```

**After (Volcengine):**
```python
api_key = os.environ.get('VOLCENGINE_API_KEY')
model = os.environ.get('VOLCENGINE_MODEL', 'ep-20250215154848-djsgr')
url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
timeout = 120
# Enhanced error handling:
#   - 401: Authentication failure
#   - 429: Rate limiting
#   - Connection errors
#   - Detailed error messages
```

#### `_read_trending_data()` - Unchanged
Continues to use `get_output_path()` via file path construction.

#### `_save_analysis()` - Unchanged
Continues to use `get_output_path()` for output file path.

## Key Improvements

### 1. Enhanced Error Handling

**Status Code Specific Handling:**
- `401`: "认证失败: API Key 无效或已过期"
- `429`: "请求频率超限，请稍后重试"
- Other HTTP errors: Display status code and response details

**Exception Specific Handling:**
- `requests.exceptions.Timeout`: "AI 请求超时"
- `requests.exceptions.ConnectionError`: "网络连接错误"
- Generic exceptions: "AI 分析过程出错"

### 2. Improved System Prompt

**Before:**
```
"你是一个技术专家，擅长分析开源项目和技术趋势。
请用中文回答，使用清晰的 markdown 格式。"
```

**After:**
```
"你是一位资深技术专家，长期关注开源生态与前沿工程实践。
请对以下 GitHub 项目列表中的每一个项目，用一句简洁、准确、有洞察力的话进行解读，
说明其核心价值、技术特点或潜在影响。"
```

### 3. Configurable Model

Supports custom model endpoints via environment variable:
```bash
export VOLCENGINE_MODEL=ep-20250215154848-djsgr  # Default
export VOLCENGINE_MODEL=custom-endpoint-id        # Custom
```

### 4. Increased Reliability

- Timeout: 60s → 120s
- Better error messages for debugging
- Graceful degradation on API failures

## Data Flow (Unchanged)

```
execute()
  ↓
_read_trending_data()
  → Reads: output/{year}/{date}.md
  → Returns: markdown content
  ↓
_call_ai_analysis()
  → API call to Volcengine
  → Returns: analysis text or None
  ↓
_save_analysis()
  → Writes: output/{year}/{date}-analysis.md
  → Returns: True/False
  ↓
execute() returns True/False
```

## File Path Management

All file paths continue to use Task base class methods:
- `self.get_today()` → `2026-02-16`
- `self.get_year()` → `2026`
- File paths constructed relative to `output/` directory

**Input:** `output/{year}/{date}.md`
**Output:** `output/{year}/{date}-analysis.md`

## Testing Strategy

1. **Primary:** GitHub Actions workflow (automatic)
2. **Manual:** `python -m tasks.trending_ai`
3. **Verification:** Monitor initial runs for error handling effectiveness

## Migration Steps

1. Update environment variable documentation (README.md)
2. Refactor `_call_ai_analysis()` method
3. Update system prompt
4. Test manually (optional, per user preference)
5. Commit changes
6. Monitor GitHub Actions run

## Dependencies

**Required:**
- `VOLCENGINE_API_KEY` environment variable set in GitHub Actions secrets

**Optional:**
- `VOLCENGINE_MODEL` environment variable (uses default if not set)

## Rollback Plan

If issues arise:
1. Revert commit to restore GLM-4 integration
2. Restore `BIGMODEL_API_KEY` in GitHub Actions secrets
3. No data loss (input/output files unaffected)

## Success Criteria

- ✅ Task executes without errors in GitHub Actions
- ✅ Analysis report generated successfully
- ✅ Enhanced error messages appear when API fails
- ✅ No breaking changes to other tasks or notifiers

## Future Considerations

- Add retry logic for 429 rate limit errors
- Consider caching analysis results to reduce API calls
- Add metrics/monitoring for API success rates
