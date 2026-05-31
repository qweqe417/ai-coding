---
name: diff-analyzer
description: "分析测试失败原因并分类问题"
---

# diff-analyzer - 差异分析器

使用 AI 分析测试失败的根本原因。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

- 对比预期结果和实际结果
- 识别差异根本原因
- 分类问题类型（真实 Bug、时序问题、环境问题、断言问题）
- 生成修复建议

## 前置条件

- [ ] 集成测试已执行
- [ ] 存在测试失败的用例

## 执行步骤

**重要：你必须按顺序执行以下所有步骤，不能跳过！**

### 1. 读取差异报告

使用 Read 工具读取 `.ai-coding/results/diff-{test_case_id}.yaml`

如果文件不存在，用中文提示：
```
❌ 错误: 差异报告不存在
请先运行集成测试：
/ai-coding:integration-test {test_case_id}
```

如果测试通过（status: PASS），用中文提示：
```
✅ 测试通过，无需分析
```

### 2. AI 分析差异（6 个步骤）

**这是核心步骤！** 你需要深入分析差异并定位根因。

**[1/6] 分析差异模式**
- 查看所有差异项
- 识别差异类型（字段缺失、值不匹配、类型错误等）
- 判断差异是否有规律

**[2/6] 追踪代码路径**
- 使用 Glob 查找相关代码文件
- 使用 Read 读取 API 实现代码
- 追踪数据流：Controller → Service → Repository → 中间件
- 识别哪个环节出了问题

**[3/6] 查看日志信息**（如果有）
- 读取 `.ai-coding/logs/` 中的日志
- 查找错误信息、异常堆栈
- 分析时序问题

**[4/6] 定位问题根因**
- 确定是代码问题还是配置问题
- 找到具体的文件、方法、行号
- 理解为什么会出现这个差异

**[5/6] 分类差异类型**

根据分析结果分类：

- **Real Bug（真实 Bug）**
  - 代码逻辑错误
  - 业务规则实现错误
  - 缺少必要的操作（如忘记写 Redis）
  - 置信度：0.8-1.0

- **Timing Issue（时序问题）**
  - 异步操作未完成
  - 消息队列延迟
  - 缓存未及时更新
  - 置信度：0.6-0.9

- **Environment Issue（环境问题）**
  - 中间件配置不一致
  - 测试数据污染
  - 网络问题
  - 置信度：0.5-0.8

- **Assertion Issue（断言问题）**
  - 预期值设置错误
  - 验证规则不合理
  - 数据采集计划错误
  - 置信度：0.7-0.95

**[6/6] 生成分析报告**

### 3. 生成 YAML 格式的分析报告

使用 Write 工具保存到 `.ai-coding/analysis/root-cause-{test_case_id}.yaml`

**YAML 格式：**

```yaml
test_case_id: TC001
category: Real Bug  # Real Bug | Timing Issue | Environment Issue | Assertion Issue
confidence: 0.92    # 0.0-1.0

root_cause: |
  UserService.create()方法中缺少设置Redis缓存的代码。
  
  代码路径分析:
  1. UserController.register() 调用 UserService.create()
  2. UserService.create() 保存用户到MySQL
  3. 但是没有调用 redisTemplate.set() 设置缓存
  
  预期行为:
  在保存用户到MySQL后，应该同时设置Redis缓存

code_location:
  file: src/main/java/com/example/service/UserService.java
  line: 45
  method: create

evidence:
  - type: code_analysis
    description: UserService.create()方法中没有Redis操作代码
    confidence: 0.95
  
  - type: diff_report
    description: 测试期望Redis中存在用户缓存，但实际不存在
    confidence: 0.90
  
  - type: log_analysis
    description: 日志中没有Redis SET操作记录
    confidence: 0.85

suggestion: |
  在 UserService.create() 方法中添加以下代码:
  
  ```java
  // 保存到Redis缓存
  String cacheKey = "user:" + user.getId();
  redisTemplate.opsForValue().set(cacheKey, user, 1, TimeUnit.HOURS);
  ```
  
  位置: src/main/java/com/example/service/UserService.java:45
  在 userRepository.save(user) 之后添加

fix_priority: high  # high | medium | low
estimated_effort: 5 minutes
```

### 4. 显示中文摘要

**必须用中文**向用户展示：

```
✅ 差异分析完成！

📊 分析结果：
- 问题类型: Real Bug
- 置信度: 92%
- 根因: UserService.create()方法中缺少设置Redis缓存的代码

📍 问题位置：
- 文件: src/main/java/com/example/service/UserService.java
- 行号: 45
- 方法: create

💡 修复建议：
在 UserService.create() 方法中添加 Redis 缓存操作
[显示前 5 行建议]

📝 后续步骤：
1. 查看完整分析报告: .ai-coding/analysis/root-cause-{test_case_id}.yaml
2. 置信度高（>90%），可以尝试自动修复
3. 运行 /ai-coding:auto-fixer {test_case_id}

需要我帮你自动修复吗？
```

如果置信度较低（<90%），提示：
```
📝 后续步骤：
1. 查看完整分析报告
2. 置信度较低，建议人工审核
3. 确认后运行 /ai-coding:auto-fixer {test_case_id}
```

## 问题分类说明

**Real Bug（真实 Bug）：**
- 代码逻辑错误
- 业务规则实现错误
- 缺少必要的操作
- **建议：自动修复或人工修复**

**Timing Issue（时序问题）：**
- 异步操作未完成
- 消息队列延迟
- 缓存未及时更新
- **建议：增加等待时间或重试机制**

**Environment Issue（环境问题）：**
- 中间件配置不一致
- 测试数据污染
- 网络问题
- **建议：检查环境配置**

**Assertion Issue（断言问题）：**
- 预期值设置错误
- 验证规则不合理
- 数据采集计划错误
- **建议：修改数据采集计划**

## 注意事项

- 必须实际分析代码，不要生成占位符
- 必须找到具体的文件和行号
- 置信度必须基于实际证据
- 所有与用户的交互必须使用中文