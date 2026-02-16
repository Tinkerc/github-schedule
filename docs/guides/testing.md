# Testing Guide

This document provides quick reference for testing the GitHub Schedule project.

## Quick Verification Tests

### Run Manual Tests
```bash
python test_manual.py
```

This runs a quick sanity check covering:
- Environment variable configuration
- Git helper module imports
- Script discovery and validation
- HTTP timeout configuration
- AI news script structure

### Run Comprehensive Tests
```bash
python test_verification.py
```

This runs detailed verification including:
- All manual test checks
- Requirements.txt validation
- GitHub Actions workflow configuration
- README documentation completeness

## Testing Individual Scripts

### Test AI News Fetching
```bash
# Method 1: Run as module
python -m tasks.ai_news

# Method 2: Direct execution
python tasks/ai_news.py
```

Output: `output/ai-news/YYYY-MM-DD.json`

### Test GitHub Trending
```bash
# Method 1: Run as module
python -m tasks.github_trending

# Method 2: Direct execution
python tasks/github_trending.py
```

Output: `output/github-trending/YYYY/YYYY-MM-DD.md`

### Test Trending AI Analysis
```bash
# Requires VOLCENGINE_API_KEY environment variable
export VOLCENGINE_API_KEY="your_api_key"

# Method 1: Run as module
python -m tasks.trending_ai

# Method 2: Direct execution
python tasks/trending_ai.py
```

Output: `output/github-trending/YYYY/YYYY-MM-DD-analysis.md`

### Test WeChat Notification
```bash
# Requires WECOM_WEBHOOK_URL environment variable
export WECOM_WEBHOOK_URL="your_webhook_url"
python -m tasks.wecom_robot
```

### Run All Tasks
```bash
python main.py
```

This executes all tasks using the TaskRunner in PRIORITY order.

## Environment Setup

### 1. Create `.env` file
```bash
cp .env.example .env
# Edit .env with your actual values
```

### 2. Required Environment Variables
```bash
# For WeChat notifications
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"

# For Trending AI analysis (Volcengine/豆包)
export VOLCENGINE_API_KEY="your_api_key"

# Optional: Specify Volcengine model endpoint (defaults to ep-20250215154848-djsgr)
export VOLCENGINE_MODEL="ep-20250215154848-djsgr"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Common Issues

### Issue: "WECOM_WEBHOOK_URL not set"
**Solution**: Set the environment variable or create a `.env` file

```bash
export WECOM_WEBHOOK_URL="your_webhook_url"
```

### Issue: "VOLCENGINE_API_KEY not set"
**Solution**: Set the environment variable for AI analysis

```bash
export VOLCENGINE_API_KEY="your_api_key"
```

### Issue: Task doesn't run
**Solution**: Check that the task has a valid `TASK_ID` and `execute()` method
```bash
grep "TASK_ID" tasks/your-task.py
grep "def execute" tasks/your-task.py
```

### Issue: Module import error
**Solution**: Ensure you're running from the project root directory
```bash
cd /path/to/github-schedule
python -m tasks.your_task
```

## CI/CD Testing

The project uses GitHub Actions for automated testing. The workflow runs daily at 00:00 UTC.

Required secrets:
- `WECOM_WEBHOOK_URL` - WeChat webhook URL
- `VOLCENGINE_API_KEY` - Volcengine API key for AI analysis
- `MAILUSERNAME` - Email username (optional)
- `MAILPASSWORD` - Email password (optional)

## Test Output

Expected output when running tests:
```
✓ PASS: Environment Variables
✓ PASS: Git Helper Module
✓ PASS: Script Loading
✓ PASS: HTTP Configuration
✓ PASS: AI News Script
Result: 5/5 tests passed
```

## Development Workflow

1. Make changes to tasks
2. Run individual tasks for testing: `python -m tasks.your_task`
3. Run `python main.py` to test the full workflow
4. Verify output files in `output/` directory
5. Commit and push changes
