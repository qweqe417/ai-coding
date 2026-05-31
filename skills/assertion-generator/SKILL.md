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

**重要：你必须按顺序执行以下所有步骤，不能跳过！**

### 1. 加载测试用例

使用 Read 工具读取 `.ai-coding/testcases/testcases.json`

如果文件不存在，用中文提示：
```
❌ 错误: 测试用例文件不存在
请先运行 /ai-coding:testcase-generator 生成测试用例
```

### 2. 查找相关代码文件

对于每个测试用例，使用 Glob 工具查找相关代码文件：

```
常见的代码目录：
- src/main/java/**/*.java
- src/**/*.py
- app/**/*.js
- controllers/**/*.ts
- services/**/*.go
```

限制文件数量为 10 个以内。

### 3. 读取代码内容

使用 Read 工具读取找到的代码文件内容。

### 4. AI 分析代码

**这是核心步骤！** 你需要分析代码并生成数据采集计划。

分析要点：
1. 识别 API 会操作哪些中间件（MySQL/Redis/MongoDB/RabbitMQ/Kafka/Elasticsearch）
2. 识别每个中间件的具体操作（INSERT/UPDATE/DELETE/SET/PUBLISH 等）
3. 确定需要验证哪些字段
4. 确定字段的预期值

根据请求方法生成不同的验证逻辑：
- **GET 请求**：验证查询结果是否正确
- **POST 请求**：验证数据是否正确插入
- **PUT 请求**：验证数据是否正确更新
- **DELETE 请求**：验证数据是否正确删除

### 5. 生成 YAML 格式的数据采集计划

使用 Write 工具保存到 `.ai-coding/plans/data-collection-plan-{test_case_id}.yaml`

**YAML 格式：**

```yaml
test_case_id: TC001
api: POST /user/account/create

collection_steps:
  - step: 1
    name: 验证MySQL中的用户记录
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM account WHERE username = '{{request.username}}'"
    validations:
      - field: step_1.data.username
        rule: equals
        value: "{{request.username}}"
        reason: 用户名应该正确保存到数据库
      - field: step_1.data.status
        rule: equals
        value: "active"
        reason: 新用户状态应该为 active

expected_result:
  step_1:
    data:
      username: "{{request.username}}"
      status: "active"
```

### 6. 验证计划

读取刚生成的 YAML 文件，确保格式正确。

### 7. 显示中文摘要

**必须用中文**向用户展示：

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

## 注意事项

- 必须实际分析代码，不要生成占位符
- SQL 查询必须使用实际的表名和字段名
- 必须根据代码逻辑确定验证规则
- 所有与用户的交互必须使用中文