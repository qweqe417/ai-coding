# AI Coding 插件化设计方案

**日期**: 2026-05-30  
**版本**: 1.0.0  
**状态**: 已批准

## 概述

将 AI Coding 集成测试框架改造为 Claude Code Skills 插件，实现全局安装和跨项目使用。

## 目标

1. **保持现有代码不变** - 所有 Python 实现（adapters、engines、models）保持原样
2. **全局安装** - 用户安装一次，任何项目都能使用
3. **简单调用** - 通过 `/ai-coding:xxx` 命令调用
4. **灵活执行** - 支持单独执行任意 Skill 或完整流程

## 核心架构

### 工作原理

```
用户输入: /ai-coding:init
    ↓
Claude Code 加载 skills/init/SKILL.md
    ↓
Claude 读取执行指令
    ↓
Claude 通过 Bash 工具执行: python ~/.claude/plugins/.../skills/init/run.py
    ↓
Python 脚本执行实际逻辑
    ↓
输出结果返回给用户
```

### 插件结构

```
ai-coding/
├── .claude-plugin/
│   ├── plugin.json              # 插件元数据
│   └── marketplace.json         # 市场信息（可选）
├── package.json                 # NPM 格式元数据
├── skills/                      # 8 个 Skills
│   ├── init/
│   │   ├── SKILL.md            # 修改：添加 frontmatter + 执行指令
│   │   └── run.py              # 保持不变
│   ├── testcase-generator/
│   ├── assertion-generator/
│   ├── integration-test/
│   ├── diff-analyzer/
│   ├── auto-fixer/
│   ├── report-generator/
│   └── full-test-pipeline/
├── ai-coding/                   # Python 实现（保持不变）
│   ├── __init__.py
│   ├── adapters/
│   ├── engines/
│   ├── models/
│   ├── shared/
│   └── tests/
├── requirements.txt             # Python 依赖
├── docs/
├── examples/
├── README.md
└── LICENSE
```

## 详细设计

### 1. 插件配置文件

#### `.claude-plugin/plugin.json`

```json
{
  "name": "ai-coding",
  "description": "AI-powered integration testing framework with middleware validation",
  "version": "1.0.0",
  "author": {
    "name": "AI Coding Team",
    "email": "contact@ai-coding.dev"
  },
  "homepage": "https://github.com/ai-coding-team/ai-coding",
  "repository": "https://github.com/ai-coding-team/ai-coding",
  "license": "MIT",
  "keywords": [
    "testing",
    "integration-test",
    "middleware",
    "mysql",
    "redis",
    "mongodb",
    "kafka",
    "elasticsearch",
    "rabbitmq"
  ]
}
```

#### `package.json`（根目录）

```json
{
  "name": "ai-coding",
  "version": "1.0.0",
  "type": "module",
  "description": "AI-powered integration testing framework"
}
```

#### `.claude-plugin/marketplace.json`（可选）

```json
{
  "name": "ai-coding-marketplace",
  "description": "AI Coding integration testing framework marketplace",
  "owner": {
    "name": "AI Coding Team",
    "email": "contact@ai-coding.dev"
  },
  "plugins": [
    {
      "name": "ai-coding",
      "description": "AI-powered integration testing framework with middleware validation",
      "version": "1.0.0",
      "source": "./",
      "author": {
        "name": "AI Coding Team",
        "email": "contact@ai-coding.dev"
      }
    }
  ]
}
```

### 2. SKILL.md 标准结构

每个 Skill 的 SKILL.md 需要添加 frontmatter 和执行指令：

```markdown
---
name: skill-name
description: "简短描述（一句话）"
---

# Skill 标题

详细说明这个 skill 做什么。

## Prerequisites（可选）

前置条件检查：
- [ ] `.ai-coding/config.yaml` exists (run `/ai-coding:init` first)
- [ ] Test cases exist (run `/ai-coding:testcase-generator` first)

## What This Does

1. 功能点 1
2. 功能点 2
3. 功能点 3

## How To Execute

**IMPORTANT:** You MUST execute the Python script using the Bash tool.

```bash
# Find plugin installation path
PLUGIN_PATH=$(find ~/.claude/plugins/cache -name "ai-coding" -type d | grep -E "ai-coding/[0-9]" | head -1)

# Check dependencies (first time only)
python -c "import yaml, requests, pymysql" 2>/dev/null || {
    echo "⚠️  Installing dependencies..."
    pip install -r "$PLUGIN_PATH/requirements.txt"
}

# Execute the script
python "$PLUGIN_PATH/ai-coding/skills/SKILL_NAME/run.py" [args]
```

## Arguments（如果有参数）

- `test_case_id`: 测试用例 ID（可选/必需）
- `--force`: 强制执行标志

## Output

执行后的输出说明。

## After Execution

✅ Execution completed!

**Next steps:**
- Run `/ai-coding:next-skill` to continue
- Or check the results in `.ai-coding/results/`

## Error Handling

常见错误和解决方案：

**Error: Module not found**
```bash
pip install -r "$PLUGIN_PATH/requirements.txt"
```

**Error: Connection refused**
- Check middleware configuration in `.ai-coding/config.yaml`
- Ensure services are running
```

### 3. 8 个 Skills 改造清单

| Skill | 参数 | 前置条件 | 改造内容 |
|-------|------|----------|----------|
| `init` | 无 | 无 | 添加 frontmatter + 执行指令 |
| `testcase-generator` | 无 | config.yaml | 添加 frontmatter + 执行指令 |
| `assertion-generator` | `[test_case_id]` | testcases.json | 添加 frontmatter + 执行指令 |
| `integration-test` | `[test_case_ids]` | plans/*.yaml | 添加 frontmatter + 执行指令 |
| `diff-analyzer` | `test_case_id` | diff-*.yaml | 添加 frontmatter + 执行指令 |
| `auto-fixer` | `test_case_id` | root-cause-*.yaml | 添加 frontmatter + 执行指令 |
| `report-generator` | 无 | test-summary.json | 添加 frontmatter + 执行指令 |
| `full-test-pipeline` | 无 | config.yaml | 添加 frontmatter + 执行指令 |

### 4. 安装和分发

#### 安装方式

**方式 1：本地开发（测试用）**

```bash
# 创建符号链接
ln -s /path/to/your/ai-coding ~/.claude/plugins/local/ai-coding

# 或直接复制
cp -r /path/to/your/ai-coding ~/.claude/plugins/local/ai-coding
```

**方式 2：Git 仓库安装（推荐）**

```bash
# 在 Claude Code 中
/install https://github.com/ai-coding-team/ai-coding

# 或手动
cd ~/.claude/plugins/cache
git clone https://github.com/ai-coding-team/ai-coding
```

**方式 3：Marketplace（未来）**

提交到 Claude Code 官方插件市场。

#### 依赖安装

用户首次使用时需要安装 Python 依赖：

```bash
# 自动查找插件路径并安装
pip install -r $(find ~/.claude/plugins/cache -name "ai-coding" -type d | grep -E "ai-coding/[0-9]" | head -1)/requirements.txt

# 可选：安装 Playwright
playwright install
```

或者在每个 Skill 的执行指令中添加自动检查和安装。

### 5. 使用流程

#### 完整流程示例

```bash
# 1. 安装插件（一次性）
/install https://github.com/ai-coding-team/ai-coding

# 2. 安装依赖（一次性）
pip install -r ~/.claude/plugins/cache/ai-coding/*/requirements.txt

# 3. 在新项目中使用
cd /path/to/my-project

# 4. 初始化
/ai-coding:init

# 5. 生成测试用例
/ai-coding:testcase-generator

# 6. 生成断言计划
/ai-coding:assertion-generator

# 7. 执行测试
/ai-coding:integration-test

# 8. 分析失败（如果有）
/ai-coding:diff-analyzer TC001

# 9. 自动修复
/ai-coding:auto-fixer TC001

# 10. 生成报告
/ai-coding:report-generator
```

#### 单独执行示例

```bash
# 只生成测试用例
/ai-coding:testcase-generator

# 只执行特定测试
/ai-coding:integration-test TC001 TC002

# 只分析差异
/ai-coding:diff-analyzer TC001
```

#### 完整流程一键执行

```bash
# 执行完整测试流程
/ai-coding:full-test-pipeline
```

## 实施计划

### 阶段 1：添加配置文件（5 分钟）

1. 创建 `.claude-plugin/` 目录
2. 编写 `plugin.json`
3. 编写 `package.json`
4. 编写 `marketplace.json`（可选）

### 阶段 2：改造 SKILL.md（30 分钟）

按优先级改造 8 个 Skills：

1. ✅ `init` - 最常用，优先改造
2. ✅ `testcase-generator`
3. ✅ `assertion-generator`
4. ✅ `integration-test`
5. ✅ `diff-analyzer`
6. ✅ `auto-fixer`
7. ✅ `report-generator`
8. ✅ `full-test-pipeline`

### 阶段 3：本地测试（15 分钟）

1. 创建符号链接到 `~/.claude/plugins/local/`
2. 在测试项目中调用 `/ai-coding:init`
3. 验证 Python 脚本能正确执行
4. 测试参数传递
5. 测试错误处理

### 阶段 4：文档更新（10 分钟）

1. 更新 `README.md` - 添加安装说明
2. 更新 `docs/QUICKSTART.md` - 添加插件使用方式
3. 创建 `INSTALL.md` - 详细安装指南
4. 创建 `CHANGELOG.md` - 版本记录

### 阶段 5：发布（5 分钟）

1. 推送到 GitHub
2. 创建 Release
3. 编写 Release Notes

## 技术细节

### 插件路径查找

```bash
# 查找插件安装路径（支持版本号）
PLUGIN_PATH=$(find ~/.claude/plugins/cache -name "ai-coding" -type d | grep -E "ai-coding/[0-9]" | head -1)

# 如果找不到，尝试 local 目录
if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

# 如果还找不到，报错
if [ -z "$PLUGIN_PATH" ]; then
    echo "❌ Error: ai-coding plugin not found"
    exit 1
fi
```

### 参数传递

```bash
# 无参数
python "$PLUGIN_PATH/ai-coding/skills/init/run.py"

# 可选参数
python "$PLUGIN_PATH/ai-coding/skills/assertion-generator/run.py" "$1"

# 必需参数
if [ -z "$1" ]; then
    echo "❌ Error: test_case_id is required"
    echo "Usage: /ai-coding:diff-analyzer <test_case_id>"
    exit 1
fi
python "$PLUGIN_PATH/ai-coding/skills/diff-analyzer/run.py" "$1"

# 多个参数
python "$PLUGIN_PATH/ai-coding/skills/integration-test/run.py" "$@"
```

### 依赖检查

```bash
# 检查 Python 依赖
python -c "import yaml, requests, pymysql, redis, pymongo, pika, kafka, elasticsearch, jinja2, rich, playwright" 2>/dev/null || {
    echo "⚠️  Missing dependencies. Installing..."
    pip install -r "$PLUGIN_PATH/requirements.txt"
}

# 检查 Playwright（如果需要）
python -c "from playwright.sync_api import sync_playwright" 2>/dev/null || {
    echo "⚠️  Playwright not installed. Installing browsers..."
    playwright install
}
```

### 错误处理

```bash
# 执行 Python 脚本并捕获错误
if ! python "$PLUGIN_PATH/ai-coding/skills/init/run.py"; then
    echo ""
    echo "❌ Execution failed. Common solutions:"
    echo "1. Check if dependencies are installed: pip install -r requirements.txt"
    echo "2. Check if Python version >= 3.9: python --version"
    echo "3. Check the error message above for details"
    exit 1
fi
```

## 兼容性

### Claude Code

- ✅ 完全支持
- ✅ 通过 `/ai-coding:xxx` 调用
- ✅ 支持 Bash 工具执行 Python

### Cursor

- ✅ 支持（如果有 `.cursor-plugin/` 配置）
- ⚠️ 需要额外配置文件

### Codex

- ✅ 支持（如果有 `.codex/` 配置）
- ⚠️ 需要额外配置文件

### 其他 AI 编程工具

- ⚠️ 需要根据具体工具适配

## 优势

1. **最小改动** - 只添加配置文件，不改 Python 代码
2. **保持灵活** - Python 代码可以独立使用
3. **用户友好** - 简单的命令调用
4. **全局可用** - 安装一次，到处使用
5. **易于维护** - 配置和代码分离
6. **易于扩展** - 添加新 Skill 只需添加目录和 SKILL.md

## 限制

1. **需要 Python 环境** - 用户必须安装 Python 3.9+
2. **需要安装依赖** - 首次使用需要 `pip install`
3. **路径依赖** - 依赖插件安装路径查找
4. **平台限制** - 主要支持 Claude Code

## 未来扩展

1. **自动依赖管理** - 首次使用自动安装依赖
2. **多平台支持** - 添加 Cursor、Codex 配置
3. **MCP Server** - 提供 MCP 接口供其他工具调用
4. **Web UI** - 提供可视化配置和报告界面
5. **插件市场** - 发布到官方市场

## 风险和缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 插件路径查找失败 | 高 | 提供多种查找方式，清晰的错误提示 |
| Python 依赖缺失 | 中 | 自动检查和安装，详细的安装文档 |
| 参数传递错误 | 中 | 参数验证，清晰的使用说明 |
| 跨平台兼容性 | 低 | 优先支持 Claude Code，逐步扩展 |

## 成功标准

1. ✅ 用户可以通过 `/ai-coding:init` 调用
2. ✅ 所有 8 个 Skills 都能正常执行
3. ✅ 支持单独执行和完整流程
4. ✅ 参数传递正确
5. ✅ 错误提示清晰
6. ✅ 文档完整

## 总结

通过添加最少的配置文件（3 个）和修改 SKILL.md（8 个），将 AI Coding 改造为标准的 Claude Code Skills 插件，实现全局安装和跨项目使用，同时保持所有现有 Python 代码不变。

用户体验：
- 安装：`/install https://github.com/ai-coding-team/ai-coding`
- 使用：`/ai-coding:init`
- 简单、直观、强大