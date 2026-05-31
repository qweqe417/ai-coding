# AI Coding Plugin 使用指南

## 📦 安装插件

### 1. 添加 Marketplace

在 Claude Code 中运行：

```bash
/plugin marketplace add https://github.com/qweqe417/ai-coding.git  


/plugin update ai-coding@ai-coding-marketplace

/reload-plugins
```

### 2. 安装插件

```bash

/plugin install ai-coding@ai-coding-marketplace
```

### 3. 重新加载插件

```bash
/reload-plugins
```

### 4. 验证安装

安装成功后，你可以使用以下命令：

- `/ai-coding:init`
- `/ai-coding:testcase-generator`
- `/ai-coding:assertion-generator`
- `/ai-coding:integration-test`
- `/ai-coding:diff-analyzer`
- `/ai-coding:auto-fixer`
- `/ai-coding:report-generator`
- `/ai-coding:full-test-pipeline`

---

## 🚀 快速开始

### 第一步：初始化项目

在你的项目根目录运行：

```bash
/ai-coding:init
```

这个命令会：
- 自动检测项目类型（Java/Python/Go/Node.js/Vue/React）
- 创建 `.ai-coding/` 目录结构
- 生成 `config.yaml` 配置文件

**生成的目录结构：**
```
.ai-coding/
├── config.yaml          # 配置文件
├── specs/              # API 规范文档
├── testcases/          # 测试用例
├── plans/              # 数据收集计划
├── results/            # 测试结果
├── reports/            # 测试报告
└── logs/               # 执行日志
```

### 第二步：配置中间件连接

编辑 `.ai-coding/config.yaml`，配置你的中间件连接信息：

```yaml
project:
  name: "my-service"
  type: "microservice"
  language: "java"

service:
  url: "http://localhost:8080"
  startup_command: "mvn spring-boot:run"
  health_check: "/actuator/health"

middleware:
  mysql:
    host: "localhost"
    port: 3306
    user: "root"
    password: "password"
    database: "test_db"
  
  redis:
    host: "localhost"
    port: 6379
    db: 0
  
  mongodb:
    host: "localhost"
    port: 27017
    database: "test_db"
  
  kafka:
    bootstrap_servers: "localhost:9092"
    topics: ["test-topic"]
  
  rabbitmq:
    host: "localhost"
    port: 5672
    username: "guest"
    password: "guest"
  
  elasticsearch:
    hosts: ["http://localhost:9200"]

test:
  timeout: 30
  retry: 3
  parallel: false

logging:
  level: "INFO"
  output: "console"
```

### 第三步：准备 API 规范文档

将你的 API 规范文档放到 `.ai-coding/specs/` 目录：

```
.ai-coding/specs/
├── user-api.yaml       # OpenAPI/Swagger 格式
├── order-api.md        # Markdown 格式
└── payment-api.json    # JSON 格式
```

**支持的格式：**
- OpenAPI/Swagger (YAML/JSON)
- Markdown
- 纯文本

---

## 📝 完整工作流程

### 方案 1：完整自动化流程

使用 `/ai-coding:full-test-pipeline` 一键执行完整流程：

```bash
/ai-coding:full-test-pipeline
```

这个命令会自动执行：
1. 生成测试用例
2. 生成数据收集计划
3. 执行集成测试
4. 分析测试结果
5. 自动修复失败用例（可选）
6. 生成测试报告

**参数选项：**
```bash
# 启用自动修复
/ai-coding:full-test-pipeline --auto-fix

# 跳过测试用例生成（使用已有用例）
/ai-coding:full-test-pipeline --skip-generation

# 只生成报告（不执行测试）
/ai-coding:full-test-pipeline --report-only
```

### 方案 2：分步执行流程

#### 1. 生成测试用例

```bash
/ai-coding:testcase-generator
```

**功能：**
- 从 API 规范文档自动生成测试用例
- 支持正常场景和异常场景
- 生成 JSON 格式的测试用例文件

**输出：**
```
.ai-coding/testcases/
├── TC001_create_user.json
├── TC002_get_user.json
├── TC003_update_user.json
└── TC004_delete_user.json
```

**测试用例格式：**
```json
{
  "id": "TC001",
  "name": "创建用户",
  "description": "测试创建用户接口",
  "api": {
    "method": "POST",
    "path": "/api/users",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "username": "testuser",
      "email": "test@example.com"
    }
  },
  "expected": {
    "status_code": 201,
    "response": {
      "id": "{{generated}}",
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

#### 2. 生成数据收集计划

```bash
/ai-coding:assertion-generator
```

**功能：**
- 分析代码和测试用例
- 追踪数据流经过的中间件
- 生成数据收集计划

**输出：**
```
.ai-coding/plans/
├── TC001_plan.json
├── TC002_plan.json
└── TC003_plan.json
```

**数据收集计划格式：**
```json
{
  "test_case_id": "TC001",
  "data_points": [
    {
      "middleware": "mysql",
      "type": "query",
      "table": "users",
      "operation": "INSERT",
      "fields": ["id", "username", "email", "created_at"]
    },
    {
      "middleware": "redis",
      "type": "cache",
      "key": "user:{{user_id}}",
      "operation": "SET"
    },
    {
      "middleware": "kafka",
      "type": "message",
      "topic": "user-events",
      "operation": "PRODUCE"
    }
  ]
}
```

#### 3. 执行集成测试

```bash
# 执行所有测试用例
/ai-coding:integration-test

# 执行指定测试用例
/ai-coding:integration-test TC001

# 执行多个测试用例
/ai-coding:integration-test TC001 TC002 TC003
```

**执行流程：**
1. 启动服务（如果未运行）
2. 执行 API 调用
3. 收集中间件数据
4. 验证响应和数据
5. 生成测试结果

**输出：**
```
.ai-coding/results/
├── TC001_result.json
├── TC002_result.json
└── execution_summary.json
```

#### 4. 分析测试失败

```bash
# 分析指定测试用例
/ai-coding:diff-analyzer TC001

# 分析所有失败用例
/ai-coding:diff-analyzer
```

**功能：**
- 对比预期和实际结果
- 识别根本原因
- 分类问题类型：
  - **Real Bug**: 真实的代码缺陷
  - **Timing Issue**: 时序问题
  - **Environment Issue**: 环境配置问题
  - **Assertion Issue**: 断言错误

**输出：**
```json
{
  "test_case_id": "TC001",
  "status": "failed",
  "root_cause": "Real Bug",
  "analysis": {
    "issue": "用户创建后未发送 Kafka 消息",
    "location": "UserService.java:45",
    "suggestion": "在 createUser 方法中添加 kafkaProducer.send() 调用"
  },
  "confidence": 0.95
}
```

#### 5. 自动修复问题

```bash
# 修复指定测试用例的问题
/ai-coding:auto-fixer TC001

# 修复所有失败用例
/ai-coding:auto-fixer
```

**修复策略：**
- **高置信度 (>0.9)**: 自动修复代码
- **中置信度 (0.7-0.9)**: 生成修复建议
- **低置信度 (<0.7)**: 标记为需要人工审查

**输出：**
- 修复后的代码文件
- 修复说明文档
- 重新执行测试验证

#### 6. 生成测试报告

```bash
/ai-coding:report-generator
```

**生成的报告：**
```
.ai-coding/reports/
├── test_report.html      # HTML 可视化报告
├── test_report.md        # Markdown 报告
└── test_report.json      # JSON 原始数据
```

**报告内容：**
- 测试执行摘要
- 通过率统计
- 失败用例详情
- 中间件数据验证结果
- 性能指标
- 趋势分析图表

---

## 🔧 高级用法

### 自定义测试用例

手动创建测试用例文件 `.ai-coding/testcases/TC_CUSTOM.json`：

```json
{
  "id": "TC_CUSTOM",
  "name": "自定义测试",
  "description": "测试复杂业务场景",
  "setup": {
    "sql": [
      "INSERT INTO users (id, username) VALUES (1, 'test')"
    ],
    "redis": {
      "user:1": "{\"username\": \"test\"}"
    }
  },
  "api": {
    "method": "POST",
    "path": "/api/orders",
    "body": {
      "user_id": 1,
      "product_id": 100,
      "quantity": 2
    }
  },
  "assertions": {
    "response": {
      "status_code": 201,
      "body.order_id": "{{exists}}"
    },
    "mysql": {
      "table": "orders",
      "where": "user_id = 1",
      "count": 1
    },
    "kafka": {
      "topic": "order-events",
      "message_count": 1,
      "message_contains": {
        "event_type": "ORDER_CREATED"
      }
    }
  },
  "teardown": {
    "sql": [
      "DELETE FROM orders WHERE user_id = 1",
      "DELETE FROM users WHERE id = 1"
    ]
  }
}
```

### 环境变量配置

在 `.ai-coding/config.yaml` 中使用环境变量：

```yaml
middleware:
  mysql:
    host: "${MYSQL_HOST:localhost}"
    port: ${MYSQL_PORT:3306}
    user: "${MYSQL_USER}"
    password: "${MYSQL_PASSWORD}"
```

### CI/CD 集成

在 CI/CD 流水线中使用：

```yaml
# .github/workflows/integration-test.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup services
        run: docker-compose up -d
      
      - name: Install Claude Code
        run: |
          curl -fsSL https://claude.ai/install.sh | sh
          claude plugin marketplace add qweqe417/ai-coding
          claude plugin install ai-coding@ai-coding-marketplace
      
      - name: Run integration tests
        run: |
          claude /ai-coding:full-test-pipeline --auto-fix
      
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: .ai-coding/reports/
```

---

## 📊 测试报告示例

### HTML 报告预览

报告包含以下部分：

1. **执行摘要**
   - 总用例数
   - 通过/失败/跳过数量
   - 通过率
   - 执行时间

2. **详细结果**
   - 每个测试用例的状态
   - API 请求/响应详情
   - 中间件数据验证结果
   - 失败原因分析

3. **数据验证**
   - MySQL 查询结果
   - Redis 缓存状态
   - Kafka 消息内容
   - MongoDB 文档数据

4. **性能指标**
   - API 响应时间
   - 数据库查询耗时
   - 端到端延迟

5. **趋势分析**
   - 历史通过率曲线
   - 性能趋势图
   - 失败用例分布

---

## 🐛 故障排查

### 问题 1: 插件命令找不到

**症状：**
```
Command not found: /ai-coding:init
```

**解决方案：**
```bash
# 1. 检查插件是否安装
/plugin list

# 2. 重新加载插件
/reload-plugins

# 3. 如果还不行，重新安装
/plugin uninstall ai-coding@ai-coding-marketplace
/plugin install ai-coding@ai-coding-marketplace
/reload-plugins
```

### 问题 2: Python 依赖缺失

**症状：**
```
ModuleNotFoundError: No module named 'yaml'
```

**解决方案：**
```bash
# 找到插件路径
PLUGIN_PATH=$(find ~/.claude/plugins/cache -name "ai-coding" -type d | grep -E "ai-coding/[0-9]" | head -1)

# 安装依赖
pip install -r "$PLUGIN_PATH/requirements.txt"
```

### 问题 3: 中间件连接失败

**症状：**
```
Error: Cannot connect to MySQL at localhost:3306
```

**解决方案：**
1. 检查中间件是否运行
2. 验证 `.ai-coding/config.yaml` 中的连接信息
3. 测试网络连接：
```bash
# MySQL
mysql -h localhost -P 3306 -u root -p

# Redis
redis-cli -h localhost -p 6379 ping

# MongoDB
mongosh --host localhost --port 27017
```

### 问题 4: 服务启动失败

**症状：**
```
Error: Service health check failed
```

**解决方案：**
1. 手动启动服务验证
2. 检查 `config.yaml` 中的 `startup_command`
3. 调整 `health_check` 端点
4. 增加超时时间：
```yaml
service:
  startup_timeout: 60  # 秒
  health_check_interval: 5
```

### 问题 5: 测试用例生成失败

**症状：**
```
Error: Cannot parse API specification
```

**解决方案：**
1. 验证规范文档格式
2. 确保文档在 `.ai-coding/specs/` 目录
3. 支持的格式：
   - OpenAPI 3.0 (YAML/JSON)
   - Swagger 2.0 (YAML/JSON)
   - Markdown (特定格式)

---

## 💡 最佳实践

### 1. 项目结构建议

```
your-project/
├── src/                    # 源代码
├── .ai-coding/            # AI Coding 配置
│   ├── config.yaml
│   ├── specs/             # API 规范
│   ├── testcases/         # 测试用例
│   └── reports/           # 测试报告
├── docker-compose.yml     # 中间件服务
└── README.md
```

### 2. 测试用例命名规范

```
TC001_create_user.json          # 功能_操作
TC002_get_user_by_id.json       # 功能_操作_条件
TC003_update_user_invalid.json  # 功能_操作_场景
```

### 3. 数据隔离

- 使用独立的测试数据库
- 每个测试用例使用唯一的测试数据
- 在 `teardown` 中清理测试数据

### 4. 持续集成

- 在 PR 中自动运行集成测试
- 失败时自动尝试修复
- 生成报告并通知团队

### 5. 性能监控

- 设置性能基线
- 监控 API 响应时间
- 追踪数据库查询性能

---

## 📚 更多资源

- [GitHub 仓库](https://github.com/qweqe417/ai-coding)
- [问题反馈](https://github.com/qweqe417/ai-coding/issues)
- [贡献指南](https://github.com/qweqe417/ai-coding/blob/master/CONTRIBUTING.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](https://github.com/qweqe417/ai-coding/blob/master/LICENSE)