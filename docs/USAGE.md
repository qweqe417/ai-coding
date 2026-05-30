# AI Coding 使用示例

本文档展示如何使用AI Coding框架进行集成测试。

## 1. 项目初始化

在你的项目根目录运行：

```bash
cd /path/to/your/project
python /path/to/ai-coding/scripts/init_project.py
```

这会自动：
- 检测项目类型
- 生成 `.ai-coding/config.yaml`
- 创建必要的目录结构

## 2. 配置示例

生成的 `.ai-coding/config.yaml` 示例：

```yaml
version: 1.0.0

project:
  name: my-project
  category: backend
  language: java
  framework: springboot
  build_tool: maven
  root: .

service:
  type: springboot
  start_command: mvn spring-boot:run
  health_check_url: http://localhost:8080/actuator/health
  base_url: http://localhost:8080
  startup_timeout: 60

middleware:
  mysql:
    enabled: true
    host: localhost
    port: 3306
    user: root
    password: password
    database: test_db
  
  redis:
    enabled: true
    host: localhost
    port: 6379
    db: 0

test:
  strategy: backend
  max_regression_rounds: 3
  auto_fix_enabled: true
  target_pass_rate: 0.95
```

## 3. 编写测试用例

在 `.ai-coding/testcases/testcases.json` 中定义测试用例：

```json
{
  "testcases": [
    {
      "id": "TC001",
      "name": "创建用户",
      "test_type": "backend",
      "description": "测试创建用户API",
      "api": {
        "method": "POST",
        "url": "/api/users",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "username": "testuser",
          "email": "test@example.com",
          "age": 25
        }
      },
      "expected_http": {
        "status_code": 200,
        "body": {
          "code": 0,
          "message": "success"
        }
      }
    }
  ]
}
```

## 4. 编写数据采集计划

在 `.ai-coding/plans/data-collection-plan-TC001.yaml` 中定义数据采集计划：

```yaml
test_case_id: TC001
api: POST /api/users

collection_steps:
  - step: 1
    name: 验证MySQL中用户记录
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM users WHERE username = 'testuser'"
    validations:
      - field: step_1.data.username
        rule: equals
        value: testuser
        reason: 用户名应该正确保存
      
      - field: step_1.data.email
        rule: equals
        value: test@example.com
        reason: 邮箱应该正确保存
      
      - field: step_1.data.age
        rule: equals
        value: 25
        reason: 年龄应该正确保存
  
  - step: 2
    name: 验证Redis缓存
    middleware: redis
    timing: after_api
    query:
      type: get
      key: "user:{response.data.id}"
    validations:
      - field: step_2.data.username
        rule: equals
        value: testuser
        reason: Redis缓存应该包含用户信息

expected_result:
  step_1:
    data:
      username: testuser
      email: test@example.com
      age: 25
  step_2:
    data:
      username: testuser
```

## 5. 运行测试

### 方式1：使用Python脚本

```python
from ai_coding.shared.config import ConfigManager
from ai_coding.shared.logger import get_logger
from ai_coding.models import TestCaseLoader
from ai_coding.engines.service import JavaServiceAdapter
from ai_coding.engines.executor import BackendTestExecutor

# 初始化
config_mgr = ConfigManager(".")
logger = get_logger(level="INFO", log_file=config_mgr.get("logging.file"))

# 加载测试用例
testcases_file = config_mgr.get_file_path("testcases")
testcases = TestCaseLoader.load_from_file(testcases_file)

# 创建服务适配器
service_config = config_mgr.get("service")
service_adapter = JavaServiceAdapter(service_config, ".", logger)

# 创建测试执行器
middleware_configs = {
    "mysql": config_mgr.get("middleware.mysql"),
    "redis": config_mgr.get("middleware.redis")
}
executor = BackendTestExecutor(
    service_adapter,
    middleware_configs,
    config_mgr.get("service.base_url"),
    logger
)

# 执行测试
plans_dir = config_mgr.get_directory("plans")
results_dir = config_mgr.get_directory("results")
summary = executor.run(testcases, plans_dir, results_dir)

print(f"Pass Rate: {summary.pass_rate:.2%}")
```

### 方式2：使用AI Skills（推荐）

```bash
# 在Claude Code中
/ai-coding:integration-test
```

## 6. 查看结果

测试完成后，结果保存在 `.ai-coding/results/` 目录：

- `actual-result-TC001.yaml` - 实际采集的数据
- `diff-TC001.yaml` - 差异报告
- `test-summary.json` - 测试汇总

## 7. 自动修复（如果测试失败）

如果测试失败，可以使用AI自动分析和修复：

```bash
# 在Claude Code中
/ai-coding:diff-analyzer
/ai-coding:auto-fixer
```

## 8. 生成报告

```bash
# 在Claude Code中
/ai-coding:report-generator
```

报告保存在 `.ai-coding/reports/` 目录：
- `test-report.md` - Markdown格式
- `test-report.html` - HTML格式
- `test-report.json` - JSON格式

## 完整流程

```bash
# 1. 初始化项目
/ai-coding:init

# 2. 生成测试用例（从Spec）
/ai-coding:testcase-generator

# 3. 生成数据采集计划（AI分析代码）
/ai-coding:assertion-generator

# 4. 执行测试
/ai-coding:integration-test

# 5. 如果失败，分析根因
/ai-coding:diff-analyzer

# 6. 自动修复
/ai-coding:auto-fixer

# 7. 生成报告
/ai-coding:report-generator

# 或者一键执行完整流程
/ai-coding:full-test-pipeline
```
