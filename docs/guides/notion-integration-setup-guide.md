# Notion Integration Setup Guide - 诊断和修复

## 问题诊断

运行测试时遇到错误：
```
Could not find database with ID: 30943ad321af80d3a5e7d6c17ce3a93a
Make sure the relevant pages and databases are shared with your integration.
```

## 根本原因

**Integration 未被添加到 Notion 数据库中**。即使你有正确的 API Key，Integration 也需要显式添加到每个要访问的数据库中。

---

## 解决步骤

### 第 1 步：验证 Integration 配置

1. 访问：https://www.notion.so/my-integrations
2. 找到你的 Integration（比如 "GitHub Schedule Bot"）
3. 确认：
   - ✅ Integration 已创建
   - ✅ Internal Integration Token 已复制（这就是 `NOTION_API_KEY`）
   - ✅ 基本功能已启用

### 第 2 步：将 Integration 添加到数据库 ⚠️ **关键步骤**

这是大多数用户忽略的步骤！

#### 方法 A：通过数据库设置（推荐）

1. 打开你的 Notion 数据库（Published Markdown）
2. 点击右上角的 **`...`** (更多) 菜单
3. 向下滚动找到 **"Add connections"** 或 **"连接"**
4. 搜索你的 Integration 名称（例如 "GitHub Schedule Bot"）
5. 点击添加

#### 方法 B：通过页面设置

1. 打开数据库中的任意页面
2. 点击右上角的 **`...`** 菜单
3. 选择 **"Connections"** → **"Add connections"**
4. 选择你的 Integration

### 第 3 步：验证配置

运行验证脚本：

```bash
python scripts/verify_notion_config.py
```

预期输出：
```
✓ Step 1: Checking NOTION_API_KEY
  Status: ✓ Configured

✓ Step 2: Checking Database IDs
  Task: tech_insights
    Environment var (NOTION_DB_TECH_INSIGHTS): ✓ 30943ad321af80d3a5e7d6c17ce3a93a

✓ Step 3: Testing Client Availability
  Status: ✓ Ready to sync
```

### 第 4 步：测试连接

```bash
# 测试 data source 访问
python -c "
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client

client = Client(auth=os.getenv('NOTION_API_KEY'))
result = client.data_sources.retrieve(
    data_source_id=os.getenv('NOTION_DB_TECH_INSIGHTS')
)
print('✓ Success! Database name:', result.get('name'))
"
```

### 第 5 步：测试完整同步

```bash
# 干运行（无 API 调用）
python tests/manual_notion_test.py --task tech_insights --dry-run

# 真实 API 测试
python tests/manual_notion_test.py --task tech_insights --real
```

---

## 常见问题

### Q1: 我的数据库是 "Published Markdown" 类型，这有问题吗？

**A:** "Published Markdown" 是 Notion 的特殊数据源类型。需要使用 `data_sources` API 而不是 `databases` API。

当前代码使用的是 `databases` API，需要修改为支持 `data_sources`。

### Q2: 我需要重新创建 Integration 吗？

**A:** 不需要，只需要将现有的 Integration 添加到数据库中即可。

### Q3: 如何确认 Integration 已添加成功？

**A:** 在数据库页面右上角 `...` 菜单 → Connections 中，应该能看到你的 Integration 名称。

### Q4: GitHub Actions 中如何配置？

**A:** Integration 只需要在 Notion 中添加一次，然后在 GitHub Secrets 中配置相同的 API Key 和数据库 ID 即可。

---

## 当前代码问题

**问题：** `core/notion_client.py` 使用了 `databases.query()` 和 `databases` API，但你的数据库是 "Published Markdown" 类型，需要使用 `data_sources` API。

**需要修改的文件：**
- `core/notion_client.py:137` - `_find_and_delete_existing()` 方法
- `core/notion_client.py:168` - `_create_new_entry()` 方法

**解决方案：**
1. 添加代码自动检测数据库类型（普通数据库 vs Published Markdown）
2. 根据类型选择正确的 API（`databases` vs `data_sources`）
3. 更新属性映射（Published Markdown 使用不同的属性名称）

---

## 下一步

1. ✅ **立即执行：** 在 Notion 中将 Integration 添加到数据库
2. 🔧 **代码修复：** 更新 `notion_client.py` 支持 Published Markdown 数据源
3. ✅ **验证：** 运行测试脚本确认一切正常

---

## 快速命令参考

```bash
# 检查配置
python scripts/verify_notion_config.py

# 检查数据库结构
python scripts/inspect_notion_database.py tech_insights

# 测试同步（干运行）
python tests/manual_notion_test.py --task tech_insights --dry-run

# 测试同步（真实 API）
python tests/manual_notion_test.py --task tech_insights --real

# 运行完整自动化
python main.py
```

---

**状态：** 等待在 Notion 中添加 Integration 权限
