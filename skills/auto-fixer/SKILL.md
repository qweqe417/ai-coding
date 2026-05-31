---
name: auto-fixer
description: "基于根因分析自动修复代码问题"
---

# auto-fixer - 自动修复器

根据根因分析自动修复代码问题。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

- 读取根因分析结果
- 生成修复方案
- 自动修改代码
- 验证修复效果

## 前置条件

- [ ] 差异分析已完成
- [ ] 存在可修复的问题

## 执行步骤

**重要：必须使用 Bash 工具执行 Python 脚本。**

```bash
PLUGIN_PATH=$(find ~/.claude/plugins/cache -path "*/ai-coding-marketplace/ai-coding/*" -name "skills" -type d | head -1 | xargs dirname)

if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

if [ -z "$PLUGIN_PATH" ]; then
    echo "❌ 错误: 找不到 ai-coding 插件"
    exit 1
fi

python "$PLUGIN_PATH/skills/auto-fixer/run.py" "$1"
```

## 参数说明

- `test_case_id`（可选）：指定要修复的测试用例 ID

## 输出结果

生成 `.ai-coding/fixes/fix-record-{test_case_id}.yaml`

## 执行完成后

用中文向用户展示：

```
✅ 自动修复完成！

📊 修复结果：
- 成功修复: X 个
- 需要人工介入: X 个
- 总计: X 个

📁 修复记录：
.ai-coding/fixes/

📝 后续步骤：
1. 查看修复记录
2. 重新运行 /ai-coding:integration-test 验证修复
3. 提交代码变更

需要我帮你重新运行测试吗？
```

## 修复策略

**高置信度（自动修复）：**
- 简单逻辑错误
- 明显的类型错误

**中置信度（建议修复）：**
- 业务逻辑调整
- 复杂的条件判断

**低置信度（人工介入）：**
- 架构级别问题
- 需要业务确认的问题