# AI Coding 示例

本目录包含AI Coding集成测试框架的完整示例。

## 文件说明

- `run_integration_test.py` - 完整的集成测试脚本
- `config.yaml` - 示例配置文件
- `testcases.json` - 示例测试用例
- `data-collection-plan-TC001.yaml` - 示例数据采集计划

## 快速开始

### 1. 准备环境

```bash
# 安装依赖
cd ..
pip install -r requirements.txt
```

### 2. 准备测试项目

假设你有一个Spring Boot项目，提供用户管理API：

```
your-project/
├── src/
│   └── main/
│       └── java/
│           └── com/example/
│               ├── UserController.java
│               └── UserService.java
├── pom.xml
└── application.yml
```

### 3. 初始化配置

```bash
cd your-project

# 方式1：使用示例配置
cp /path/to/ai-coding/examples/config.yaml .ai-coding/config.yaml

# 方式2：自动生成配置
python /path/to/ai-coding/examples/run_integration_test.py
```

### 4. 准备测试用例

```bash
# 复制示例测试用例
mkdir -p .ai-coding/testcases
cp /path/to/ai-coding/examples/testcases.json .ai-coding/testcases/

# 复制示例数据采集计划
mkdir -p .ai-coding/plans
cp /path/to/ai-coding/examples/data-collection-plan-TC001.yaml .ai-coding/plans/
```

### 5. 配置中间件

编辑 `.ai-coding/config.yaml`，配置MySQL和Redis连接信息：

```yaml
middleware:
  mysql:
    enabled: true
    host: localhost
    port: 3306
    user: root
    password: your_password
    database: your_db

  redis:
    enabled: true
    host: localhost
    port: 6379
    db: 0
```

### 6. 运行测试

```bash
cd your-project
python /path/to/ai-coding/examples/run_integration_test.py
```

## 预期输出

```
================================================================================
AI Coding - 集成测试框架示例
================================================================================

[1/7] 初始化配置...
✅ 初始化完成: /path/to/your-project/.ai-coding/config.yaml
   项目类型: backend - java - springboot
   构建工具: maven

[2/7] 初始化日志...

[3/7] 加载测试用例...
   加载了 4 个测试用例

[4/7] 创建服务适配器...
   服务类型: java

[5/7] 准备中间件配置...
   ✓ mysql
   ✓ redis

[6/7] 执行集成测试...
--------------------------------------------------------------------------------
============================================================
Starting backend integration test
============================================================
Starting service...
Connected to MySQL: localhost:3306/test_db
Connected to Redis: localhost:6379/0
Service is ready (attempt 5/30)

============================================================
Executing test case: TC001 - 创建用户
============================================================
Calling API: POST /api/users
Response: 200
Starting data collection for test case: TC001
Executing step 1: 验证MySQL中用户记录
Executing step 2: 验证Redis缓存
Data collection completed for test case: TC001
Comparison completed: PASS (6/6 passed)
✅ Test case TC001 PASSED

... (其他测试用例)

Stopping service...

============================================================
Test Summary
============================================================
Total: 4
Passed: 4
Failed: 0
Pass Rate: 100.00%
Duration: 25.43s
============================================================

[7/7] 生成测试报告...
   ✓ JSON报告: .ai-coding/reports/test-report.json
   ✓ Markdown报告: .ai-coding/reports/test-report.md
   ✓ HTML报告: .ai-coding/reports/test-report.html

================================================================================
测试完成
================================================================================
总用例数: 4
通过数: 4 ✅
失败数: 0 ❌
通过率: 100.00%
执行时间: 25.43s
================================================================================

✅ 测试通过！
```

## 查看报告

### HTML报告

在浏览器中打开：

```bash
open .ai-coding/reports/test-report.html
```

### Markdown报告

```bash
cat .ai-coding/reports/test-report.md
```

### JSON报告

```bash
cat .ai-coding/reports/test-report.json | jq
```

## 自定义测试用例

### 1. 编写测试用例

编辑 `.ai-coding/testcases/testcases.json`：

```json
{
  "testcases": [
    {
      "id": "TC005",
      "name": "你的测试用例",
      "test_type": "backend",
      "api": {
        "method": "POST",
        "url": "/api/your-endpoint",
        "body": {
          "key": "value"
        }
      },
      "expected_http": {
        "status_code": 200
      }
    }
  ]
}
```

### 2. 编写数据采集计划

创建 `.ai-coding/plans/data-collection-plan-TC005.yaml`：

```yaml
test_case_id: TC005
api: POST /api/your-endpoint

collection_steps:
  - step: 1
    name: 验证数据库
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM your_table WHERE id = {response.data.id}"
    validations:
      - field: step_1.data.field_name
        rule: equals
        value: expected_value

expected_result:
  step_1:
    data:
      field_name: expected_value
```

### 3. 运行测试

```bash
python /path/to/ai-coding/examples/run_integration_test.py
```

## 故障排查

### 服务启动失败

检查：
- 端口是否被占用
- 配置文件是否正确
- 依赖是否安装

### 中间件连接失败

检查：
- 中间件是否启动
- 连接信息是否正确
- 网络是否可达

### 测试用例失败

查看：
- `.ai-coding/results/diff-{test_case_id}.yaml` - 差异报告
- `.ai-coding/logs/integration-test.log` - 详细日志

## 下一步

- 查看 [完整文档](../docs/USAGE.md)
- 查看 [快速开始](../docs/QUICKSTART.md)
- 使用AI Skills自动生成测试用例和数据采集计划
