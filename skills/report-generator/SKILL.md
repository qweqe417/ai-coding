---
name: report-generator
description: "生成测试报告（HTML、Markdown、JSON 格式）"
---

# report-generator - 测试报告生成器

生成全面的测试报告，包含图表和趋势分析。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

- 汇总测试结果
- 生成多格式报告（HTML、Markdown、JSON）
- 生成图表和统计
- 趋势分析

## 前置条件

- [ ] 集成测试已执行
- [ ] 存在测试结果

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

python "$PLUGIN_PATH/skills/report-generator/run.py"
```

## 输出结果

生成以下报告文件：
- `.ai-coding/reports/test-report.html`
- `.ai-coding/reports/test-report.md`
- `.ai-coding/reports/test-report.json`

## 执行完成后

用中文向用户展示：

```
✅ 测试报告生成成功！

📊 报告统计：
- 测试用例总数: X 个
- 通过率: X%
- 失败用例: X 个
- 执行时间: X 秒

📁 报告文件：
- HTML: .ai-coding/reports/test-report.html
- Markdown: .ai-coding/reports/test-report.md
- JSON: .ai-coding/reports/test-report.json

📝 后续步骤：
1. 在浏览器中打开 HTML 报告查看详情
2. 将报告分享给团队
3. 归档测试结果

需要我帮你打开 HTML 报告吗？
```

## 报告内容

**概览：**
- 测试统计
- 通过率趋势
- 执行时间分布

**详细结果：**
- 每个测试用例的执行结果
- 失败原因分析
- 中间件验证详情

**趋势分析：**
- 历史通过率
- 性能趋势
- 问题分类统计