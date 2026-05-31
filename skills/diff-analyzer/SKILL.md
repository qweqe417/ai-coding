---
name: diff-analyzer
description: "分析测试失败原因并分类问题"
---

# diff-analyzer - 差异分析器

使用 AI 分析测试失败的根本原因。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

- 对比预期结果和实际结果
- 识别差异根本原因
- 分类问题类型（真实 Bug、时序问题、环境问题、断言问题）
- 生成修复建议

## 前置条件

- [ ] 集成测试已执行
- [ ] 存在测试失败的用例

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

python "$PLUGIN_PATH/skills/diff-analyzer/run.py" "$1"
```

## 参数说明

- `test_case_id`（可选）：指定要分析的测试用例 ID

## 输出结果

生成 `.ai-coding/analysis/root-cause-analysis-{test_case_id}.yaml`

## 执行完成后

用中文向用户展示：

```
✅ 差异分析完成！

📊 分析结果：
- 真实 Bug: X 个
- 时序问题: X 个
- 环境问题: X 个
- 断言问题: X 个

📁 分析文件：
.ai-coding/analysis/

📝 后续步骤：
1. 查看根因分析报告
2. 对于真实 Bug，运行 /ai-coding:auto-fixer 自动修复
3. 对于其他问题，根据建议手动调整

需要我帮你自动修复 Bug 吗？
```

## 问题分类

**真实 Bug：**
- 代码逻辑错误
- 业务规则实现错误

**时序问题：**
- 异步操作未完成
- 消息队列延迟

**环境问题：**
- 中间件配置不一致
- 测试数据污染

**断言问题：**
- 预期值设置错误
- 验证规则不合理