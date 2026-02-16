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
