---
name: assertion-generator
description: "通过分析代码生成数据采集计划"
---

# assertion-generator - 数据采集计划生成器

**核心功能** - AI 分析代码自动生成数据采集计划。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

这是框架的核心功能。使用 AI：
- 识别 API 数据流
- 跟踪跨中间件的数据流（MySQL、Redis、MongoDB、Kafka 等）
- 生成完整的数据采集计划
- 生成验证规则

## 前置条件

- [ ] `.ai-coding/config.yaml` 已存在（先运行 `/ai-coding:init`）
- [ ] 测试用例已存在于 `.ai-coding/testcases/`（先运行 `/ai-coding:testcase-generator`）
- [ ] 项目源代码可访问

## 执行步骤

**重要：必须使用 Bash 工具执行 Python 脚本。**

```bash
# 查找插件安装路径
PLUGIN_PATH=$(find ~/.claude/plugins/cache -path "*/ai-coding-marketplace/ai-coding/*" -name "skills" -type d | head -1 | xargs dirname)

# 如果 cache 中没找到，尝试 local
if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

# 如果还是没找到，报错
if [ -z "$PLUGIN_PATH" ]; then
    echo "❌ 错误: 找不到 ai-coding 插件"
    exit 1
fi

# 执行数据采集计划生成脚本
# 可选：指定 test_case_id
python "$PLUGIN_PATH/skills/assertion-generator/run.py" "$1"
```

## 参数说明

- `test_case_id`（可选）：指定要生成计划的测试用例 ID

## 输出结果

为每个测试用例生成 `.ai-coding/plans/data-collection-plan-{test_case_id}.yaml`

## 执行完成后

用中文向用户展示：

```
✅ 数据采集计划生成成功！

📊 生成统计：
- 已处理测试用例: X 个
- 生成的采集计划: X 个

📁 输出目录：
.ai-coding/plans/

📝 后续步骤：
1. 查看生成的数据采集计划
2. 根据实际数据库表结构调整 SQL 查询
3. 运行 /ai-coding:integration-test 执行集成测试

需要我帮你执行集成测试吗？
```

## 数据采集计划格式

```yaml
test_case_id: TC001
api: POST /api/users

collection_steps:
  - step: 1
    name: 验证数据库记录
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM users WHERE username = 'test'"
    validations:
      - field: step_1.data.username
        rule: equals
        value: test
        reason: 用户名应该正确保存到数据库

expected_result:
  step_1:
    data:
      username: test
```

## 错误处理

**错误：找不到测试用例文件**
- 先运行 `/ai-coding:testcase-generator` 生成测试用例

**错误：找不到源代码**
- 确保在项目根目录执行
- 检查项目结构是否正确

**错误：AI 分析失败**
- 检查代码是否可读
- 确保 API 实现清晰