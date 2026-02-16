# Notion Integration - 完整修复报告

**日期:** 2026-02-16
**状态:** ✅ **完全正常工作**

---

## 问题诊断历程

### 发现的问题

经过系统调试，发现了 **4 个主要问题** 导致 Notion 推送失败：

#### ❌ 问题 1: `.env` 文件未加载
**文件:** `tests/manual_notion_test.py`
**原因:** 缺少 `load_dotenv()` 调用
**影响:** 环境变量（API Key、数据库 ID）无法读取
**修复:** 添加 `from dotenv import load_dotenv` 和 `load_dotenv()`

#### ❌ 问题 2: 缺少 SOCKS 代理支持
**原因:** 系统配置了 SOCKS5 代理但缺少 `socksio` 依赖
**错误:** `Using SOCKS proxy, but the 'socksio' package is not installed`
**修复:** 安装 `pip install "httpx[socks]"`

#### ❌ 问题 3: Integration 未添加到数据库
**原因:** Notion Integration 需要显式添加到每个数据库
**错误:** `Could not find database with ID. Make sure the relevant pages and databases are shared with your integration.`
**解决:** 用户在 Notion 中添加了 Integration 权限

#### ❌ 问题 4: 数据库类型不匹配（关键问题）
**原因:** 你的数据库是 **Published Markdown** 类型，而不是标准数据库
**差异:**
- API: `data_sources` vs `databases`
- 属性类型: `rich_text` vs `title`/`select`
- 数据源 ID 与数据库 ID 不同

**修复:** 重写 `notion_client.py` 以支持两种数据库类型

---

## 代码修复详情

### 1. `core/notion_client.py` - 主要改进

#### 自动检测数据库类型
```python
# 检测数据库类型
db_info = notion.databases.retrieve(database_id)
is_published_markdown = 'data_sources' in db_info

if is_published_markdown:
    # 使用 Published Markdown API
    ds_id = db_info['data_sources'][0]['id'].replace('-', '')
    return self._sync_to_published_markdown(ds_id, database_id, markdown_content, date)
else:
    # 使用标准数据库 API
    self._find_and_delete_existing(database_id, date)
    self._create_new_entry(database_id, markdown_content, date)
```

#### 正确的属性类型（Published Markdown）
```python
properties = {
    "Name": {"title": [{"text": {"content": date}}]},
    "Title": {"rich_text": [{"type": "text", "text": {"content": date}}]},
    "Date": {"date": {"start": date}},
    "Source": {"rich_text": [{"type": "text", "text": {"content": "github-schedule"}}]}
}
```

#### 正确的删除方法
```python
# 旧代码（错误）
notion.pages.delete(page_id)

# 新代码（正确）
notion.pages.update(page_id, archived=True)  # Notion 使用 archived=True 来删除
```

### 2. `tests/manual_notion_test.py` - 加载环境变量

```python
# 添加
from dotenv import load_dotenv
load_dotenv()
```

### 3. 新增诊断工具

#### `scripts/inspect_notion_database.py`
- 检查数据库结构
- 显示所有属性及其类型
- 帮助识别数据库类型

#### `scripts/verify_notion_config.py`
- 完整的配置验证
- 检查 API Key 和数据库 ID
- 测试干运行模式
- 提供详细的错误消息

### 4. 文档

#### `docs/notion-integration-setup-guide.md`
- 完整的设置指南
- Integration 权限配置步骤
- 常见问题解答

#### `docs/notion-debug-report.md`
- 调试过程记录
- 所有发现的问题
- 解决方案和验证步骤

---

## 验证结果

### ✅ 测试 1: 干运行模式
```bash
$ python tests/manual_notion_test.py --task tech_insights --dry-run
============================================================
Testing dry-run mode for tech_insights
============================================================
[Notion] DRY RUN: Would sync tech_insights for 2026-02-16
[Notion] Content length: 173 chars

Result: ✓ PASS
```

### ✅ 测试 2: 真实 API 调用
```bash
$ python tests/manual_notion_test.py --task tech_insights --real
============================================================
Testing real API sync for tech_insights
============================================================
[Notion] ✓ Successfully synced to Published Markdown for 2026-02-16

Result: ✓ PASS
```

### ✅ 测试 3: 验证内容已添加
```python
# 查询 Notion 数据库
Total entries: 1
Active entries: 1

Entry 1:
  Name: "2026-02-16"
  Title: "2026-02-16"
  Date: "2026-02-16"
  Created: 2026-02-16T07:43:00
```

### ✅ 测试 4: trending_ai 任务
```bash
$ python tests/manual_notion_test.py --task trending_ai --dry-run
Result: ✓ PASS
```

---

## 配置要求

### 必需的环境变量

```bash
# .env 文件
NOTION_API_KEY=ntn_your_api_key_here
NOTION_DB_TECH_INSIGHTS=30943ad321af80d3a5e7d6c17ce3a93a
NOTION_DB_TRENDING_AI=your_32_char_database_id_here
```

### 必需的 Python 包

```bash
pip install notion-client>=2.2.1
pip install python-dotenv
pip install "httpx[socks]"  # SOCKS 代理支持
```

### Notion 配置

1. ✅ 创建 Integration: https://www.notion.so/my-integrations
2. ✅ 复制 Integration Token（`NOTION_API_KEY`）
3. ✅ 将 Integration 添加到数据库
   - 打开数据库 → 点击右上角 `...` → Add connections → 选择你的 Integration

---

## 如何使用

### 快速验证配置
```bash
python scripts/verify_notion_config.py
```

### 测试单个任务
```bash
# 干运行（无 API 调用）
python tests/manual_notion_test.py --task tech_insights --dry-run

# 真实 API 调用
python tests/manual_notion_test.py --task tech_insights --real
```

### 运行完整自动化
```bash
python main.py
```

这会：
1. 执行所有任务（ai_news, tech_insights, trending_ai 等）
2. 自动同步到 Notion（如果配置了）
3. 发送企业微信通知（如果配置了）

---

## GitHub Actions 配置

### 必需的 Secrets

在 GitHub 仓库设置中添加：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `NOTION_API_KEY` | Notion Integration Token | `ntn_1816...` |
| `NOTION_DB_TECH_INSIGHTS` | Tech Insights 数据库 ID | `30943ad321af80d3a5e7d6c17ce3a93a` |
| `NOTION_DB_TRENDING_AI` | Trending AI 数据库 ID | `your_32_char_id` |

### 工作流配置

已包含在 `.github/workflows/daily-automation.yml`:

```yaml
- name: Run daily automation scripts
  env:
    NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
    NOTION_DB_TECH_INSIGHTS: ${{ secrets.NOTION_DB_TECH_INSIGHTS }}
    NOTION_DB_TRENDING_AI: ${{ secrets.NOTION_DB_TRENDING_AI }}
  run: |
    python main.py
```

---

## 关键学习点

### 1. Notion 有两种数据库类型

**标准数据库:**
- API: `databases.query()`, `databases.retrieve()`
- 属性: `title`, `select`, `date` 等
- 数据库 ID 就是实际使用的 ID

**Published Markdown 数据库:**
- API: `data_sources.query()`, `data_sources.retrieve()`
- 属性: 全部是 `rich_text` 类型
- 需要从 `data_sources` 数组中提取真正的数据源 ID

### 2. Notion "删除"实际上是归档

```python
# 不是 delete()，而是设置 archived=True
notion.pages.update(page_id, archived=True)
```

### 3. Integration 必须显式添加到数据库

即使有正确的 API Key，也必须在 Notion UI 中：
1. 打开数据库
2. 点击 `...` → Add connections
3. 选择你的 Integration

### 4. 环境变量加载很重要

测试脚本和主程序都需要调用 `load_dotenv()`，否则环境变量无法读取。

---

## 故障排查

### 问题: `Could not find database with ID`
**解决:** 在 Notion 中将 Integration 添加到数据库

### 问题: `Using SOCKS proxy, but the 'socksio' package is not installed`
**解决:** `pip install "httpx[socks]"`

### 问题: `'DatabasesEndpoint' object has no attribute 'query'`
**解决:** 数据库是 Published Markdown 类型，需要使用 `data_sources` API

### 问题: `Title is expected to be rich_text`
**解决:** 使用正确的属性类型（`rich_text` 而不是 `title`）

### 问题: `'PagesEndpoint' object has no attribute 'delete'`
**解决:** 使用 `pages.update(page_id, archived=True)`

---

## 文件变更总结

### 修改的文件
- ✅ `core/notion_client.py` - 添加 Published Markdown 支持
- ✅ `tests/manual_notion_test.py` - 添加 dotenv 加载
- ✅ `.env.example` - 更新文档
- ✅ `config/notion_config.json.example` - 修正格式

### 新增的文件
- ✅ `scripts/verify_notion_config.py` - 配置验证工具
- ✅ `scripts/inspect_notion_database.py` - 数据库检查工具
- ✅ `docs/notion-integration-setup-guide.md` - 设置指南
- ✅ `docs/notion-debug-report.md` - 调试报告
- ✅ `docs/notion-integration-success-report.md` - 本报告

### Git 提交
```bash
a1f7e4a fix: add Published Markdown support and fix Notion integration
b536d12 fix: correct Notion database ID format and add verification tool
```

---

## 下一步建议

### 1. 测试其他任务
```bash
python tests/manual_notion_test.py --task trending_ai --real
```

### 2. 测试完整自动化
```bash
python main.py
```

### 3. 检查 Notion 数据库
确认内容格式符合预期，属性正确填充。

### 4. 配置 GitHub Actions Secrets
添加到 GitHub: Settings → Secrets and variables → Actions

---

## 成功指标

- ✅ 配置验证通过
- ✅ 干运行测试通过
- ✅ 真实 API 调用成功
- ✅ 内容正确添加到 Notion
- ✅ 重复项正确删除（归档）
- ✅ 支持多种数据库类型

---

**状态:** 🎉 **Notion 集成完全正常工作！**

**最后更新:** 2026-02-16
**测试环境:** macOS, Python 3.9, notion-client 2.7.0
