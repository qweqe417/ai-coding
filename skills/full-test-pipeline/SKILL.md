---
name: full-test-pipeline
description: "执行完整的测试流程（从生成测试用例到报告）"
---

# full-test-pipeline - 完整测试流程

一键执行完整的测试流程，从规范文档到最终报告。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

自动执行完整的测试流程：
1. 生成测试用例
2. 生成数据采集计划
3. 执行集成测试
4. 分析失败原因
5. 自动修复（可选）
6. 生成测试报告

## 前置条件

- [ ] `.ai-coding/config.yaml` 已存在（先运行 `/ai-coding:init`）
- [ ] 规范文档已准备在 `.ai-coding/specs/` 或 `docs/`
- [ ] 中间件已配置并运行

## 执行步骤

**重要：你必须按顺序执行以下所有步骤，不能跳过！**

用中文向用户展示进度：

```
🚀 开始执行完整测试流程...

执行计划：
[1/6] 生成测试用例
[2/6] 生成数据采集计划
[3/6] 执行集成测试
[4/6] 分析失败原因（如有失败）
[5/6] 自动修复（如需要）
[6/6] 生成测试报告
```

---

### [1/6] 生成测试用例

**执行 testcase-generator 的所有步骤：**

1. 使用 Glob 查找规范文档（`.ai-coding/specs/**/*.md`, `docs/**/*.md`）
2. 如果找到多个，让用户选择
3. 使用 Read 读取规范文档
4. AI 分析规范文档，生成测试用例（正常流程、边界值、异常流程、幂等性）
5. 使用 Write 保存到 `.ai-coding/testcases/testcases.yaml`
6. 使用 Bash 转换为 JSON 格式

**显示进度：**
```
[1/6] 生成测试用例
   ✓ 找到规范文档: docs/api-spec.md
   ✓ 分析 API 定义...
   ✓ 生成测试用例: 26 个
   ✓ 保存到: .ai-coding/testcases/testcases.yaml
```

---

### [2/6] 生成数据采集计划

**执行 assertion-generator 的所有步骤：**

1. 使用 Read 读取 `.ai-coding/testcases/testcases.json`
2. 对每个测试用例：
   - 使用 Glob 查找相关代码文件
   - 使用 Read 读取代码内容
   - AI 分析代码，识别中间件操作
   - 生成数据采集计划
   - 使用 Write 保存到 `.ai-coding/plans/data-collection-plan-{test_case_id}.yaml`

**显示进度：**
```
[2/6] 生成数据采集计划
   [1/26] TC001 - 正常创建用户
      ✓ 查找代码文件: 找到 5 个
      ✓ 分析代码...
      ✓ 生成采集计划
   [2/26] TC002 - 用户名最小长度
      ✓ 查找代码文件: 找到 5 个
      ✓ 分析代码...
      ✓ 生成采集计划
   ...
   ✓ 完成: 26 个采集计划
```

---

### [3/6] 执行集成测试

**调用 integration-test 脚本：**

使用 Bash 工具执行：

```bash
# 查找插件路径
PLUGIN_PATH=$(find ~/.claude/plugins/cache -path "*/ai-coding-marketplace/ai-coding/*" -name "skills" -type d | head -1 | xargs dirname)

if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

# 执行集成测试
python "$PLUGIN_PATH/skills/integration-test/run.py"
```

**显示进度：**
```
[3/6] 执行集成测试
   ✓ 加载配置
   ✓ 加载测试用例: 26 个
   ✓ 启动服务...
   ✓ 执行测试...
      [1/26] TC001: PASS (0.5s)
      [2/26] TC002: PASS (0.4s)
      [3/26] TC003: FAIL (0.6s)
      ...
   ✓ 测试完成: 通过 24/26 (92%)
```

---

### [4/6] 分析失败原因

**如果有失败的测试用例，执行 diff-analyzer 的所有步骤：**

1. 使用 Glob 查找失败的测试结果（status: FAIL）
2. 对每个失败的测试用例：
   - 使用 Read 读取差异报告
   - 使用 Glob 查找相关代码文件
   - 使用 Read 读取代码
   - AI 分析差异，定位根因
   - 分类问题类型（Real Bug / Timing Issue / Environment Issue / Assertion Issue）
   - 使用 Write 保存分析报告到 `.ai-coding/analysis/root-cause-{test_case_id}.yaml`

**显示进度：**
```
[4/6] 分析失败原因
   发现 2 个失败用例
   
   [1/2] TC003 - 缺少用户名
      ✓ 读取差异报告
      ✓ 分析代码路径...
      ✓ 定位根因: Real Bug
      ✓ 置信度: 92%
      ✓ 保存分析报告
   
   [2/2] TC011 - 重复用户名
      ✓ 读取差异报告
      ✓ 分析代码路径...
      ✓ 定位根因: Real Bug
      ✓ 置信度: 88%
      ✓ 保存分析报告
   
   ✓ 分析完成
```

如果没有失败，显示：
```
[4/6] 分析失败原因
   ✓ 所有测试通过，跳过分析
```

---

### [5/6] 自动修复

**如果有失败的测试用例，执行 auto-fixer 的所有步骤：**

1. 对每个失败的测试用例：
   - 使用 Read 读取根因分析报告
   - 评估置信度
   - 如果置信度 ≥ 0.9：自动修复
   - 如果置信度 0.7-0.9：询问用户是否修复
   - 如果置信度 < 0.7：跳过，建议人工修复
   - 使用 Read 读取问题文件
   - AI 生成修复代码
   - 使用 Edit 修改代码文件
   - 使用 Write 保存修复记录到 `.ai-coding/fixes/fix-record-{test_case_id}.yaml`

**显示进度：**
```
[5/6] 自动修复
   
   [1/2] TC003 - 缺少用户名
      ✓ 置信度: 92% (高)
      ✓ 生成修复方案...
      ✓ 修改文件: src/main/java/com/example/service/UserService.java
      ✓ 保存修复记录
      ✓ 修复成功
   
   [2/2] TC011 - 重复用户名
      ⚠️  置信度: 88% (中)
      
      修复方案：
      - 文件: src/main/java/com/example/service/UserService.java
      - 操作: 添加唯一性检查
      
      是否应用此修复？(y/n)
```

如果用户选择 y，应用修复；选择 n，跳过。

**可选：重新运行测试验证修复**

询问用户：
```
💡 是否重新运行测试验证修复？(y/n)
```

如果用户选择 y，重新执行步骤 [3/6]。

---

### [6/6] 生成测试报告

**执行 report-generator 的所有步骤：**

1. 使用 Glob 查找所有测试结果文件
2. 使用 Read 读取所有结果、分析、修复记录
3. 统计数据（总数、通过、失败、通过率、问题分类）
4. 使用 Write 生成 HTML 报告（`.ai-coding/reports/test-report.html`）
5. 使用 Write 生成 Markdown 报告（`.ai-coding/reports/test-report.md`）
6. 使用 Write 生成 JSON 报告（`.ai-coding/reports/test-report.json`）

**显示进度：**
```
[6/6] 生成测试报告
   ✓ 收集测试结果: 26 个
   ✓ 收集差异分析: 2 个
   ✓ 收集修复记录: 2 个
   ✓ 统计数据...
   ✓ 生成 HTML 报告
   ✓ 生成 Markdown 报告
   ✓ 生成 JSON 报告
```

---

## 最终摘要

**必须用中文**向用户展示完整摘要：

```
✅ 完整测试流程执行完成！

📊 总体统计：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
测试用例      : 26 个
通过          : 24 个
失败          : 2 个
通过率        : 92%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
问题分类      :
  - Real Bug        : 2 个
  - Timing Issue    : 0 个
  - Environment     : 0 个
  - Assertion       : 0 个
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
自动修复      : 2 个
修复成功      : 2 个
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 生成文件：
- 测试用例    : .ai-coding/testcases/ (26 个)
- 采集计划    : .ai-coding/plans/ (26 个)
- 测试结果    : .ai-coding/results/ (26 个)
- 失败分析    : .ai-coding/analysis/ (2 个)
- 修复记录    : .ai-coding/fixes/ (2 个)
- 测试报告    : .ai-coding/reports/

🌐 查看报告：
HTML 报告: file:///{绝对路径}/test-report.html

📝 后续步骤：
1. 在浏览器中打开 HTML 报告查看详情
2. 检查修复的代码是否正确
3. 提交代码变更到 Git

需要我帮你打开 HTML 报告吗？
```

## 错误处理

如果某个步骤失败：

```
❌ 步骤 [X/6] 执行失败

错误信息: {错误详情}

💡 建议：
1. 检查错误信息
2. 手动运行失败的步骤: /ai-coding:{skill-name}
3. 修复问题后重新运行完整流程

是否继续执行后续步骤？(y/n)
```

## 注意事项

- 整个流程可能需要 5-15 分钟，取决于测试用例数量
- 确保中间件（MySQL、Redis 等）已启动
- 如果某个步骤失败，可以选择跳过或中止
- 所有与用户的交互必须使用中文
- 每个步骤完成后显示清晰的进度信息
