---
name: auto-fixer
description: "基于根因分析自动修复代码问题"
---

# auto-fixer - 自动修复器

根据根因分析自动修复代码问题。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

- 读取根因分析结果
- 生成修复方案
- 自动修改代码
- 验证修复效果

## 前置条件

- [ ] 差异分析已完成
- [ ] 存在可修复的问题

## 执行步骤

**重要：你必须按顺序执行以下所有步骤，不能跳过！**

### 1. 读取根因分析报告

使用 Read 工具读取 `.ai-coding/analysis/root-cause-{test_case_id}.yaml`

如果文件不存在，用中文提示：
```
❌ 错误: 根因分析报告不存在
请先运行差异分析：
/ai-coding:diff-analyzer {test_case_id}
```

### 2. 评估修复策略

根据置信度决定修复策略：

**置信度 ≥ 0.9（高置信度）：**
- 策略：自动修复
- 提示：`✅ 置信度高 (≥0.9)，可以自动修复`
- 直接生成修复方案并应用

**置信度 0.7-0.9（中置信度）：**
- 策略：需要审核
- 提示：`⚠️ 置信度中等 (0.7-0.9)，需要审核`
- 生成修复方案，展示给用户确认后再应用

**置信度 < 0.7（低置信度）：**
- 策略：人工修复
- 提示：`❌ 置信度低 (<0.7)，建议人工修复`
- 只显示修复建议，不自动修改代码

### 3. 生成修复方案（6 个步骤）

**[1/6] 定位问题代码**
- 使用 Read 工具读取问题文件
- 找到需要修改的具体位置

**[2/6] 生成修复代码**
- 根据根因分析的建议生成修复代码
- 确保代码风格与项目一致
- 添加必要的注释

**[3/6] 验证修复方案**
- 检查修复代码的语法正确性
- 确保不会引入新问题
- 考虑边界情况

**[4/6] 备份原文件**（可选）
- 如果是重要修改，可以先备份
- 或者依赖 git 版本控制

**[5/6] 应用修复**
- 使用 Edit 工具修改代码文件
- 精确定位修改位置
- 保持代码格式

**[6/6] 重新运行测试**（可选）
- 建议用户重新运行测试验证修复
- 或者提示下一步操作

### 4. 保存修复记录

使用 Write 工具保存到 `.ai-coding/fixes/fix-record-{test_case_id}.yaml`

**YAML 格式：**

```yaml
test_case_id: TC001
fix_status: success  # success | review_required | failed
confidence: 0.92
action: auto_fix     # auto_fix | review_required | manual_fix_required

changes:
  - file: src/main/java/com/example/service/UserService.java
    line: 45
    operation: insert_after  # insert_after | replace | insert_before
    anchor: "userRepository.save(user);"
    code: |
      
      // 保存到Redis缓存
      String cacheKey = "user:" + user.getId();
      redisTemplate.opsForValue().set(cacheKey, user, 1, TimeUnit.HOURS);
      logger.info("User cached in Redis: {}", cacheKey);

verification:
  test_rerun: true
  test_result: PASS  # PASS | FAIL | NOT_RUN
  timestamp: "2026-05-31T10:30:00"

before_code: |
  public User create(UserDTO dto) {
      User user = new User();
      user.setUsername(dto.getUsername());
      user.setEmail(dto.getEmail());
      return userRepository.save(user);
  }

after_code: |
  public User create(UserDTO dto) {
      User user = new User();
      user.setUsername(dto.getUsername());
      user.setEmail(dto.getEmail());
      User savedUser = userRepository.save(user);
      
      // 保存到Redis缓存
      String cacheKey = "user:" + savedUser.getId();
      redisTemplate.opsForValue().set(cacheKey, savedUser, 1, TimeUnit.HOURS);
      logger.info("User cached in Redis: {}", cacheKey);
      
      return savedUser;
  }
```

### 5. 显示中文摘要

**高置信度（自动修复）：**

```
✅ 自动修复完成！

📊 修复结果：
- 状态: 成功
- 置信度: 92%
- 操作: 自动修复

📝 修改内容：
- 文件: src/main/java/com/example/service/UserService.java
- 行号: 45
- 操作: 在 userRepository.save(user) 后插入代码

💡 后续步骤：
1. 查看修改后的代码
2. 重新运行测试验证修复: /ai-coding:integration-test {test_case_id}
3. 如果测试通过，提交代码

需要我帮你重新运行测试吗？
```

**中置信度（需要审核）：**

先展示修复方案：
```
⚠️ 需要审核修复方案

📋 修复方案：
- 文件: src/main/java/com/example/service/UserService.java
- 行号: 45
- 操作: 在 userRepository.save(user) 后插入代码

📝 修改代码：
[显示前 10 行代码]

是否应用此修复？(y/n)
```

如果用户确认，应用修复并显示成功消息。
如果用户拒绝，显示：
```
❌ 已取消修复

💡 建议：
1. 查看完整修复方案: .ai-coding/fixes/fix-record-{test_case_id}.yaml
2. 手动修改代码
3. 重新运行测试
```

**低置信度（人工修复）：**

```
❌ 置信度低，建议人工修复

💡 修复建议：
[显示根因分析中的建议]

📝 后续步骤：
1. 查看根因分析: .ai-coding/analysis/root-cause-{test_case_id}.yaml
2. 手动修改代码
3. 重新运行测试
```

## 修复策略说明

**自动修复（置信度 ≥ 0.9）：**
- 简单逻辑错误
- 明显的类型错误
- 缺少明显的操作（如忘记写 Redis）
- **直接应用修复**

**需要审核（置信度 0.7-0.9）：**
- 业务逻辑调整
- 复杂的条件判断
- 可能影响其他功能
- **展示方案，用户确认后应用**

**人工修复（置信度 < 0.7）：**
- 架构级别问题
- 需要业务确认的问题
- 不确定的修复方案
- **只显示建议，不修改代码**

## 注意事项

- 必须实际修改代码，不要生成占位符
- 使用 Edit 工具精确修改文件
- 保持代码风格一致
- 添加必要的注释说明修复原因
- 所有与用户的交互必须使用中文