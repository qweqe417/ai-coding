---
name: init
description: "初始化 AI Coding 集成测试框架"
---

# AI Coding - 项目初始化

为当前项目初始化 AI Coding 集成测试框架。

## 功能说明

- 自动检测项目类型（Java/Python/Go/Node.js/Vue/React）
- 生成 `.ai-coding/config.yaml` 配置文件
- 创建必要的目录结构
- 提供配置建议

## 执行步骤

**重要：你必须按顺序执行以下所有步骤，不能跳过！**

### 1. 检测项目类型

使用 Read 或 Bash 工具检查项目根目录中的文件：

- 如果存在 `pom.xml` → Java Maven 项目，启动命令：`mvn spring-boot:run`
- 如果存在 `build.gradle` → Java Gradle 项目，启动命令：`./gradlew bootRun`
- 如果存在 `package.json`：
  - 检查依赖中是否有 `vue` → Vue 项目，启动命令：`npm run serve`
  - 检查依赖中是否有 `react` → React 项目，启动命令：`npm start`
  - 否则 → Node.js 项目，启动命令：`npm start`
- 如果存在 `go.mod` → Go 项目，启动命令：`go run main.go`
- 如果存在 `requirements.txt` 或 `setup.py` → Python 项目，启动命令：`python app.py`

记录检测到的：项目类型、语言、框架、构建工具、启动命令。

### 2. 创建目录结构（必须执行）

**使用 Bash 工具执行以下命令：**

```bash
mkdir -p .ai-coding/specs .ai-coding/testcases .ai-coding/plans .ai-coding/results .ai-coding/analysis .ai-coding/fixes .ai-coding/reports .ai-coding/logs
```

**验证创建成功：**

```bash
ls -la .ai-coding/
```

### 3. 生成配置文件（必须执行）

**使用 Write 工具创建 `.ai-coding/config.yaml` 文件**，内容如下（替换 `<>` 中的占位符为实际检测到的值）：

```yaml
project:
  name: "<从 pom.xml 或 package.json 中读取的项目名>"
  type: "microservice"
  language: "<检测到的语言: java/python/go/javascript>"
  framework: "<检测到的框架: spring-boot/vue/react/express>"

service:
  base_url: "http://localhost:8080"
  start_command: "<根据项目类型填写启动命令>"
  health_check: "/actuator/health"
  startup_timeout: 30

middleware:
  mysql:
    enabled: false
    host: "localhost"
    port: 3306
    user: "root"
    password: ""
    database: "test_db"
  
  redis:
    enabled: false
    host: "localhost"
    port: 6379
    db: 0
  
  mongodb:
    enabled: false
    host: "localhost"
    port: 27017
    database: "test_db"
  
  rabbitmq:
    enabled: false
    host: "localhost"
    port: 5672
    username: "guest"
    password: "guest"
  
  kafka:
    enabled: false
    bootstrap_servers: "localhost:9092"
    topics: []
  
  elasticsearch:
    enabled: false
    hosts: ["http://localhost:9200"]

test:
  timeout: 30
  retry: 3
  parallel: false

logging:
  level: "INFO"
  output: "console"
```

**验证文件创建成功：**

```bash
cat .ai-coding/config.yaml
```

### 4. 显示中文摘要

用中文向用户展示初始化结果：

```
✅ AI Coding 框架初始化成功！

📋 项目信息：
- 项目名称: <项目名>
- 项目类型: <类型>
- 编程语言: <语言>
- 开发框架: <框架>
- 构建工具: <构建工具>

📁 已创建目录结构：
.ai-coding/
├── config.yaml          # 主配置文件
├── specs/              # API 规范文档
├── testcases/          # 测试用例
├── plans/              # 数据收集计划
├── results/            # 测试结果
├── analysis/           # 失败分析
├── fixes/              # 自动修复
├── reports/            # 测试报告
└── logs/               # 执行日志

⚙️ 配置信息：
- 服务地址: http://localhost:8080
- 启动命令: <启动命令>

📝 后续步骤：

1. 配置中间件连接
   编辑 .ai-coding/config.yaml，启用并配置：
   - MySQL（数据库断言）
   - Redis（缓存验证）
   - MongoDB、Kafka、RabbitMQ、Elasticsearch（如果使用）

2. 生成测试用例
   运行 /ai-coding:testcase-generator

3. 生成数据收集计划
   运行 /ai-coding:assertion-generator

4. 执行集成测试
   运行 /ai-coding:integration-test

或直接运行完整流程：
/ai-coding:full-test-pipeline

需要我帮你配置中间件连接吗？
```

## Output

The script will:
1. Detect project type and language
2. Create `.ai-coding/` directory structure:
   - `specs/` - Specification documents
   - `testcases/` - Test case definitions
   - `plans/` - Data collection plans
   - `results/` - Test execution results
   - `reports/` - Generated reports
   - `logs/` - Execution logs
3. Generate `config.yaml` with detected settings
4. Display configuration summary

## After Execution

✅ Initialization completed!

**Next steps:**
1. Review and edit `.ai-coding/config.yaml` to configure middleware connections
2. Run `/ai-coding:testcase-generator` to generate test cases from specs
3. Run `/ai-coding:assertion-generator` to generate data collection plans
4. Run `/ai-coding:integration-test` to execute tests

## Configuration

Edit `.ai-coding/config.yaml` to configure:

- **project** - Project name and type
- **service** - Service URL and startup command
- **middleware** - MySQL, Redis, MongoDB, Kafka, RabbitMQ, Elasticsearch connections
- **test** - Test execution settings
- **logging** - Log level and output

## Error Handling

**Error: Python dependencies not found**
```bash
pip install -r "$PLUGIN_PATH/requirements.txt"
```

**Error: Config file already exists**
- The script will prompt whether to overwrite
- Backup your existing config before proceeding

**Error: Cannot detect project type**
- Manually edit `.ai-coding/config.yaml` after generation
- Set `project.type` and `project.language` fields