# 快速开始

5分钟快速上手AI Coding集成测试框架。

## 前置条件

- Python 3.9+
- 被测项目（Java/Python/Go/Node.js/Vue/React）
- 中间件（MySQL/Redis等）

## 步骤1：安装依赖

```bash
cd ai-coding
pip install -r requirements.txt

# 如果需要前端测试
playwright install
```

## 步骤2：初始化项目

```bash
cd /path/to/your/project

# 方式1：使用Python脚本
python /path/to/ai-coding/scripts/init_project.py

# 方式2：使用Claude Code
/ai-coding:init
```

这会自动创建 `.ai-coding/config.yaml` 配置文件。

## 步骤3：配置中间件

编辑 `.ai-coding/config.yaml`，配置中间件连接信息：

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

## 步骤4：准备测试用例

### 方式1：手动编写

创建 `.ai-coding/testcases/testcases.json`：

```json
{
  "testcases": [
    {
      "id": "TC001",
      "name": "测试创建用户",
      "test_type": "backend",
      "api": {
        "method": "POST",
        "url": "/api/users",
        "body": {
          "username": "test",
          "email": "test@example.com"
        }
      },
      "expected_http": {
        "status_code": 200
      }
    }
  ]
}
```

### 方式2：AI生成（推荐）

```bash
# 从Spec文档生成测试用例
/ai-coding:testcase-generator
```

## 步骤5：准备数据采集计划

### 方式1：手动编写

创建 `.ai-coding/plans/data-collection-plan-TC001.yaml`：

```yaml
test_case_id: TC001
api: POST /api/users

collection_steps:
  - step: 1
    name: 验证MySQL用户记录
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM users WHERE username = 'test'"
    validations:
      - field: step_1.data.username
        rule: equals
        value: test

expected_result:
  step_1:
    data:
      username: test
```

### 方式2：AI生成（推荐）

```bash
# AI分析代码，自动生成数据采集计划
/ai-coding:assertion-generator
```

## 步骤6：运行测试

```bash
# 使用Claude Code
/ai-coding:integration-test

# 或使用Python脚本
python examples/run_test.py
```

## 步骤7：查看结果

测试结果保存在 `.ai-coding/results/` 目录：

```bash
# 查看测试汇总
cat .ai-coding/results/test-summary.json

# 查看差异报告
cat .ai-coding/results/diff-TC001.yaml

# 生成HTML报告
/ai-coding:report-generator
```

## 完整示例

### 示例项目结构

```
my-project/
├── src/
│   └── main/
│       └── java/
│           └── com/example/
│               └── UserController.java
├── pom.xml
└── .ai-coding/
    ├── config.yaml
    ├── testcases/
    │   └── testcases.json
    ├── plans/
    │   └── data-collection-plan-TC001.yaml
    ├── results/
    │   ├── actual-result-TC001.yaml
    │   ├── diff-TC001.yaml
    │   └── test-summary.json
    └── reports/
        └── test-report.html
```

### 示例代码

**UserController.java**:
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @PostMapping
    public Result createUser(@RequestBody UserDTO userDTO) {
        User user = userService.create(userDTO);
        return Result.success(user);
    }
}
```

**UserService.java**:
```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private RedisTemplate redisTemplate;
    
    public User create(UserDTO dto) {
        // 1. 保存到MySQL
        User user = new User();
        user.setUsername(dto.getUsername());
        user.setEmail(dto.getEmail());
        userRepository.save(user);
        
        // 2. 缓存到Redis
        redisTemplate.opsForValue().set("user:" + user.getId(), user);
        
        return user;
    }
}
```

### 测试用例

**testcases.json**:
```json
{
  "testcases": [
    {
      "id": "TC001",
      "name": "创建用户",
      "test_type": "backend",
      "api": {
        "method": "POST",
        "url": "/api/users",
        "body": {
          "username": "testuser",
          "email": "test@example.com"
        }
      },
      "expected_http": {
        "status_code": 200
      }
    }
  ]
}
```

### 数据采集计划

**data-collection-plan-TC001.yaml**:
```yaml
test_case_id: TC001
api: POST /api/users

collection_steps:
  - step: 1
    name: 验证MySQL用户记录
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM users WHERE username = 'testuser'"
    validations:
      - field: step_1.data.username
        rule: equals
        value: testuser
      - field: step_1.data.email
        rule: equals
        value: test@example.com
  
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

expected_result:
  step_1:
    data:
      username: testuser
      email: test@example.com
  step_2:
    data:
      username: testuser
```

### 运行测试

```bash
cd my-project
/ai-coding:integration-test
```

### 预期输出

```
============================================================
Starting backend integration test
============================================================
Starting service...
Connected to MySQL: localhost:3306/test_db
Connected to Redis: localhost:6379/0
Service is ready

============================================================
Executing test case: TC001 - 创建用户
============================================================
Calling API: POST /api/users
Response: 200
Starting data collection for test case: TC001
Executing step 1: 验证MySQL用户记录
Executing step 2: 验证Redis缓存
Data collection completed for test case: TC001
Comparison completed: PASS (2/2 passed)
✅ Test case TC001 PASSED

Stopping service...

============================================================
Test Summary
============================================================
Total: 1
Passed: 1
Failed: 0
Pass Rate: 100.00%
Duration: 15.32s
============================================================
```

## 下一步

- 查看 [完整文档](USAGE.md)
- 查看 [API参考](API.md)
- 查看 [示例项目](../examples/)
- 加入 [社区讨论](https://github.com/your-org/ai-coding/discussions)
