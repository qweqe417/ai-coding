---
name: init
description: "初始化 AI Coding 集成测试框架"
---

# AI Coding - 项目初始化

为当前项目初始化 AI Coding 集成测试框架。

## 重要规则

1. **必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文
2. **必须检查文件是否存在** - 不要凭记忆判断，要实际检查 `.ai-coding/config.yaml` 是否存在
3. **必须实际执行** - 不要只描述步骤，要真正执行命令创建文件

## 执行步骤

### 0. 检查是否已初始化

**首先使用 Bash 工具检查配置文件是否存在：**

```bash
ls -la .ai-coding/config.yaml 2>/dev/null || echo "配置文件不存在"
```

- 如果文件存在，用中文询问用户："检测到 .ai-coding/config.yaml 已存在，是否要重新初始化？（会覆盖现有配置）"
- 如果用户回答"否"或"不"，则停止执行
- 如果文件不存在，或用户同意覆盖，继续执行下面的步骤

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
# AI Coding 集成测试框架配置文件

project:
  name: "<从 pom.xml 或 package.json 中读取的项目名>"  # 项目名称
  type: "microservice"  # 项目类型：microservice(微服务) / web(网站) / api(API服务)
  language: "<检测到的语言: java/python/go/javascript>"  # 编程语言
  framework: "<检测到的框架: spring-boot/vue/react/express>"  # 开发框架

service:
  base_url: "http://localhost:8080"  # 服务访问地址
  start_command: "<根据项目类型填写启动命令>"  # 服务启动命令，如：mvn spring-boot:run
  health_check: "/actuator/health"  # 健康检查接口路径
  startup_timeout: 30  # 服务启动超时时间（秒）

middleware:
  mysql:
    enabled: false  # 是否启用 MySQL 数据验证
    host: "localhost"  # MySQL 服务器地址
    port: 3306  # MySQL 端口
    user: "root"  # 数据库用户名
    password: ""  # 数据库密码
    database: "test_db"  # 数据库名称
  
  redis:
    enabled: false  # 是否启用 Redis 缓存验证
    host: "localhost"  # Redis 服务器地址
    port: 6379  # Redis 端口
    db: 0  # Redis 数据库编号
  
  mongodb:
    enabled: false  # 是否启用 MongoDB 验证
    host: "localhost"  # MongoDB 服务器地址
    port: 27017  # MongoDB 端口
    database: "test_db"  # MongoDB 数据库名称
  
  rabbitmq:
    enabled: false  # 是否启用 RabbitMQ 消息队列验证
    host: "localhost"  # RabbitMQ 服务器地址
    port: 5672  # RabbitMQ 端口
    username: "guest"  # RabbitMQ 用户名
    password: "guest"  # RabbitMQ 密码
  
  kafka:
    enabled: false  # 是否启用 Kafka 消息队列验证
    bootstrap_servers: "localhost:9092"  # Kafka 服务器地址
    topics: []  # 需要监听的 Kafka 主题列表
  
  elasticsearch:
    enabled: false  # 是否启用 Elasticsearch 搜索引擎验证
    hosts: ["http://localhost:9200"]  # Elasticsearch 服务器地址列表

test:
  timeout: 30  # 单个测试用例超时时间（秒）
  retry: 3  # 测试失败后重试次数
  parallel: false  # 是否并行执行测试用例

logging:
  level: "INFO"  # 日志级别：DEBUG / INFO / WARNING / ERROR
  output: "console"  # 日志输出方式：console(控制台) / file(文件)
```

**验证文件创建成功：**

```bash
cat .ai-coding/config.yaml
```

### 4. 显示中文摘要

**必须用中文**向用户展示初始化结果：

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

## 注意事项

- 如果配置文件已存在，会提示用户是否覆盖
- 所有与用户的交互必须使用中文
- 必须实际执行命令，不要只描述步骤
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