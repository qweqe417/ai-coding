---
name: testcase-generator
description: "从 API 规范文档生成测试用例"
---

# testcase-generator - 测试用例生成器

使用 AI 从规范文档自动生成测试用例。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

- 解析 API 规范文档
- 生成正常流程测试用例
- 生成边界值测试用例
- 生成异常流程测试用例
- 生成幂等性测试用例

## 前置条件

- [ ] `.ai-coding/config.yaml` 已存在（先运行 `/ai-coding:init`）
- [ ] 规范文档存在于 `.ai-coding/specs/` 或 `docs/` 目录

## 执行步骤

**重要：你必须按顺序执行以下所有步骤，不能跳过！**

### 1. 查找规范文档

使用 Glob 工具在以下目录查找规范文档：
- `.ai-coding/specs/**/*.md`
- `.ai-coding/specs/**/*.yaml`
- `docs/**/*.md`
- `docs/**/*.yaml`

如果找到多个文档，用中文列出让用户选择。

如果没找到，用中文提示：
```
❌ 错误: 找不到规范文档
请在以下目录创建 API 规范文档：
- .ai-coding/specs/
- docs/
```

### 2. 读取规范文档

使用 Read 工具读取用户选择的规范文档。

### 3. AI 分析规范文档

**这是核心步骤！** 你需要分析规范文档并生成测试用例。

分析步骤：
1. **[1/6] 解析 API 定义**
   - 识别所有 API 端点
   - 提取 HTTP 方法、URL 路径
   - 提取请求参数、请求体结构

2. **[2/6] 识别输入参数**
   - 必需参数 vs 可选参数
   - 参数类型（string、number、boolean 等）
   - 参数约束（长度、范围、格式等）

3. **[3/6] 生成正常流程测试用例**
   - 使用有效的参数值
   - 覆盖主要业务场景
   - 每个 API 至少 1 个正常用例

4. **[4/6] 生成边界值测试用例**
   - 最小值/最大值
   - 空值/null 值
   - 特殊字符
   - 每个 API 至少 2 个边界用例

5. **[5/6] 生成异常流程测试用例**
   - 缺少必需参数
   - 无效参数类型
   - 无效参数格式
   - 业务规则违反
   - 每个 API 至少 3 个异常用例

6. **[6/6] 生成幂等性测试用例**（如适用）
   - 对于 POST/PUT/DELETE 请求
   - 验证重复请求的行为

### 4. 生成测试用例文件

使用 Write 工具保存到 `.ai-coding/testcases/testcases.yaml`

**YAML 格式：**

```yaml
testcases:
  - id: TC001
    name: 正常创建用户
    type: backend
    api:
      method: POST
      url: /user/account/create
      headers:
        Content-Type: application/json
      body:
        username: testuser001
        password: password123
        email: test@example.com
    expected_response:
      status: 200
      body:
        code: 200
        message: success

  - id: TC002
    name: 用户名最小长度（边界值）
    type: backend
    api:
      method: POST
      url: /user/account/create
      body:
        username: abc
        password: password123
        email: test@example.com
    expected_response:
      status: 200

  - id: TC003
    name: 缺少用户名（异常）
    type: backend
    api:
      method: POST
      url: /user/account/create
      body:
        password: password123
        email: test@example.com
    expected_response:
      status: 400
      body:
        code: 400
        message: 用户名不能为空
```

### 5. 转换为 JSON 格式

使用 Bash 工具将 YAML 转换为 JSON（某些工具需要 JSON 格式）：

```bash
python -c "import yaml, json; yaml_data = yaml.safe_load(open('.ai-coding/testcases/testcases.yaml')); json.dump(yaml_data, open('.ai-coding/testcases/testcases.json', 'w'), indent=2, ensure_ascii=False)"
```

### 6. 显示中文摘要

**必须用中文**向用户展示：

```
✅ 测试用例生成成功！

📊 生成统计：
- 正常流程用例: X 个
- 边界值用例: X 个
- 异常流程用例: X 个
- 幂等性用例: X 个
- 总计: X 个测试用例

📁 输出文件：
- .ai-coding/testcases/testcases.yaml
- .ai-coding/testcases/testcases.json

📝 后续步骤：
1. 查看生成的测试用例
2. 手动添加特殊场景用例（如需要）
3. 运行 /ai-coding:assertion-generator 生成数据采集计划

需要我帮你生成数据采集计划吗？
```

## 测试用例类型说明

**正常流程：**
- 有效的输入参数
- 预期成功响应
- 覆盖主要业务场景

**边界值：**
- 最小/最大值
- 空值/null 值
- 特殊字符
- 长度边界

**异常流程：**
- 缺少必需参数
- 无效参数类型
- 无效参数格式
- 业务规则违反

**幂等性：**
- 重复相同请求
- 验证结果一致性

## 注意事项

- 必须实际分析规范文档，不要生成占位符
- 测试用例 ID 必须唯一（TC001、TC002...）
- 测试数据必须真实合理
- 所有与用户的交互必须使用中文
