---
name: full-test-pipeline
description: "执行完整的测试流程（从生成测试用例到报告）"
---

# full-test-pipeline - 完整测试流程

执行完整的测试流程，包含所有步骤。

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

- [ ] `.ai-coding/config.yaml` 已存在
- [ ] 规范文档已准备
- [ ] 中间件已配置并运行

## 执行步骤

**重要：必须使用 Bash 工具执行 Python 脚本。**

```bash
PLUGIN_PATH=$(find ~/.claude/plugins/cache -path "*/ai-coding-marketplace/ai-coding/*" -name "skills" -type d | head -1 | xargs dirname)

if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

if [ -z "$PLUGIN_PATH" ]; then
    echo "❌ 错误: 找不到 ai-coding 插件"
    exit 1
fi

python "$PLUGIN_PATH/skills/full-test-pipeline/run.py"
```

## 参数说明

无需参数，自动执行所有步骤。

## 执行流程

```
1. 生成测试用例
   ↓
2. 生成数据采集计划
   ↓
3. 执行集成测试
   ↓
4. 分析失败原因（如有失败）
   ↓
5. 自动修复（可选）
   ↓
6. 生成测试报告
```

## 执行完成后

用中文向用户展示：

```
✅ 完整测试流程执行完成！

📊 总体统计：
- 测试用例: X 个
- 通过: X 个
- 失败: X 个
- 自动修复: X 个
- 通过率: X%

📁 生成文件：
- 测试用例: .ai-coding/testcases/
- 采集计划: .ai-coding/plans/
- 测试结果: .ai-coding/results/
- 失败分析: .ai-coding/analysis/
- 修复记录: .ai-coding/fixes/
- 测试报告: .ai-coding/reports/

📝 后续步骤：
1. 查看 HTML 测试报告
2. 检查失败用例的根因分析
3. 提交代码变更

需要我帮你打开测试报告吗？
```

## 配置选项

编辑 `.ai-coding/config.yaml` 配置流程：

```yaml
pipeline:
  auto_fix: true          # 是否自动修复
  stop_on_failure: false  # 失败时是否停止
  parallel: false         # 是否并行执行
```

## 错误处理

**错误：某个步骤失败**
- 查看日志了解失败原因
- 可以单独运行失败的步骤

**错误：服务启动失败**
- 检查服务配置
- 确保端口未被占用

**错误：中间件连接失败**
- 检查中间件是否运行
- 验证连接配置