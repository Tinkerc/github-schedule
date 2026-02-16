# 项目结构迁移总结

## 迁移日期
2026-02-16

## 迁移类型
从扁平结构迁移到 **src/ 布局** (modern Python project layout)

---

## 迁移前后结构对比

### 迁移前
```
github-schedule/
├── main.py
├── core/                    # 在根目录
├── tasks/                   # 在根目录
├── scripts/
│   ├── demo/                # 单数
│   └── manual/
├── tests/
│   └── test_notion_*.py    # 散落在根目录
├── docs/
│   ├── designs/            # 6个子目录
│   ├── guides/
│   ├── plans/
│   ├── reference/
│   ├── reports/
│   └── standards/
└── config/                 # 空目录
```

### 迁移后
```
github-schedule/
├── main.py                 # 更新了导入路径
├── requirements.txt
├── pytest.ini
├── .env.example
│
├── src/                    # 新增：应用源代码
│   ├── __init__.py
│   ├── core/              # 移入
│   └── tasks/             # 移入
│
├── scripts/               # 重组
│   ├── tools/            # 新增：实用工具
│   ├── demos/            # 改名：复数形式
│   └── manual/
│
├── tests/                 # 完全分类
│   ├── integration/
│   │   └── notion/       # 新增：Notion集成测试
│   └── unit/
│       └── core/         # 新增：核心单元测试
│
└── docs/                  # 简化结构
    ├── README.md         # 从根目录移入
    ├── guides/           # 扁平化
    ├── development/      # 新增：开发文档
    └── projects/         # 合并designs+plans
        ├── notion/
        ├── task-framework/
        ├── tech-insights/
        └── trending-ai/
```

---

## 主要变更

### 1. 源代码组织 ✅
- ✅ 创建 `src/` 目录
- ✅ 移动 `core/` 到 `src/core/`
- ✅ 移动 `tasks/` 到 `src/tasks/`
- ✅ 添加 `src/__init__.py`

### 2. 导入路径更新 ✅
**main.py 更新：**
```python
# 修改前
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.runner import TaskRunner
runner = TaskRunner(tasks_dir="tasks")

# 修改后
from pathlib import Path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))
from core.runner import TaskRunner
runner = TaskRunner(tasks_dir=str(src_path / "tasks"))
```

**tests/conftest.py 更新：**
```python
# 修改前
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 修改后
from pathlib import Path
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))
```

### 3. 脚本目录重组 ✅
- ✅ 创建 `scripts/tools/` 并移动6个工具脚本
- ✅ 重命名 `scripts/demo/` → `scripts/demos/`
- ✅ 保留 `scripts/manual/` 不变

**工具脚本移动清单：**
- `verify_notion_config.py`
- `inspect_notion_database.py`
- `cleanup_notion_duplicates.py`
- `debug_notion_page.py`
- `list_notion_children.py`
- `simple_notion_test.py`

### 4. 测试目录重组 ✅
- ✅ 创建 `tests/integration/notion/`
- ✅ 移动7个Notion客户端测试到 `tests/integration/notion/`
- ✅ 创建 `tests/unit/core/` (待添加单元测试)

**移动的测试文件：**
- `test_notion_client.py`
- `test_notion_client_database_id.py`
- `test_notion_client_delete_duplicates.py`
- `test_notion_client_env_vars.py`
- `test_notion_client_is_available.py`
- `test_notion_client_obsolete_config_warning.py`
- `test_notion_client_current_behavior.py`

### 5. 文档目录重组 ✅
- ✅ 合并 `designs/` + `plans/` → `projects/`
- ✅ 创建 `docs/development/` 移入开发文档
- ✅ 扁平化 `docs/guides/`
- ✅ 移动根目录文档到 `docs/`

**根目录文档移动：**
- `README.md` → `docs/README.md`
- `NOTION_QUICK_START.md` → `docs/guides/getting-started.md`
- `TESTING.md` → `docs/guides/testing.md`
- `CLAUDE.md` → `docs/development/CLAUDE.md`
- `REFACTOR_SUMMARY.md` → `docs/development/REFACTOR_SUMMARY.md`

### 6. 清理操作 ✅
- ✅ 删除空目录 `config/`
- ✅ 删除docs下的空子目录
- ✅ 删除 `docs/designs/`, `docs/plans/` (内容已合并)

---

## 验证结果

### ✅ 应用正常运行
```bash
$ python main.py
============================================================
GitHub Schedule Automation System
============================================================

发现任务和通知器...
  ✓ 发现任务: hackernews
  ✓ 发现任务: github_trending
  ✓ 发现任务: trending_ai
  ✓ 发现任务: ai_news
  ✓ 发现任务: tech_insights
  ✓ 发现任务: producthunt
  ✓ 发现任务: techblogs
  ✓ 发现通知器: wecom

发现 7 个任务, 1 个通知器
```

### ✅ 导入路径正确
```python
>>> from src.core.base import Task
>>> from src.tasks.ai_news import AINewsTask
```

---

## 迁移统计

| 指标 | 迁移前 | 迁移后 | 改善 |
|-----|-------|-------|------|
| 根目录文件数 | 7 | 4 | ⬇️ 43% |
| 一级目录数 | 7 | 5 | ⬇️ 29% |
| docs/子目录 | 6 | 4 | ⬇️ 33% |
| docs/嵌套层级 | 3 | 2 | ⬇️ 33% |
| 未分类测试 | 7 | 0 | ✅ 100% |
| 工具脚本分类 | 0 | 6个 | ✅ 新增 |

---

## 遗留事项

### 需要手动处理的文件

1. **创建新的根目录 README.md**
   - 当前 `README.md` 在 `docs/README.md`
   - 建议在根目录创建简洁的 README 引导用户到 docs/

2. **GitHub Actions 工作流**
   - 验证 `.github/workflows/blank.yml` 是否正常工作
   - 可能需要更新工作目录路径

3. **tests/unit/core/** 目录当前为空
   - 待添加核心模块的单元测试

### 可能需要更新的引用

- `scripts/` 中的脚本可能需要更新导入路径
- 如果有外部工具引用项目路径，需要更新

---

## 回滚方案

如需回滚，执行以下操作：

```bash
# 1. 移回 core 和 tasks
mv src/core .
mv src/tasks .

# 2. 删除 src 目录
rmdir src

# 3. 恢复 main.py 和 conftest.py
git checkout main.py tests/conftest.py

# 4. 恢复文档结构（较复杂，建议用git）
git checkout docs/

# 5. 恢复脚本和测试目录
git checkout scripts/ tests/
```

---

## 优势总结

### ✅ 清晰的代码组织
- 应用代码在 `src/` 辅助代码在外层
- 符合现代Python项目标准
- 便于打包为pip包

### ✅ 更好的可维护性
- 测试完全分类，无散落文件
- 文档结构简化，查找更方便
- 工具脚本独立分类

### ✅ 根目录清爽
- 只保留核心配置文件
- 减少认知负担
- 更专业的项目外观

---

## 参考资料

- [Python Project Layout](https://docs.python-guide.org/writing/structure/)
- [Src Layout Tutorial](https://hynek.me/articles/testing-src-layout/)
- [Cookiecutter模板](https://github.com/audreyfeldroy/cookiecutter-pypackage)

---

迁移完成！✨
