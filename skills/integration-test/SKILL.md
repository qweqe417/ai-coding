---
name: integration-test
description: "执行集成测试并验证中间件数据"
---

# integration-test - 集成测试执行器

执行完整的集成测试流程。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

- 执行 API 调用
- 采集中间件数据
- 验证数据正确性
- 生成测试结果

## 前置条件

- [ ] `.ai-coding/config.yaml` 已存在
- [ ] 测试用例已生成
- [ ] 数据采集计划已生成
- [ ] **服务已启动**（在 IDE 或命令行中手动启动）
- [ ] 中间件已配置并运行（MySQL、Redis 等）

## 执行步骤

**重要：必须使用 Bash 工具执行 Python 脚本。**

**开发环境模式（推荐）：**

1. 先在 IDE 或命令行中启动服务
2. 确保服务可访问（如 http://localhost:8080）
3. 运行集成测试：

```bash
# 查找插件安装路径
PLUGIN_PATH=$(find ~/.claude/plugins/cache -path "*/ai-coding-marketplace/ai-coding/*" -name "skills" -type d | head -1 | xargs dirname)

if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

if [ -z "$PLUGIN_PATH" ]; then
    echo "❌ 错误: 找不到 ai-coding 插件"
    exit 1
fi

# 执行集成测试（跳过服务启动）
python "$PLUGIN_PATH/skills/integration-test/run.py" --skip-service-start
```

**CI/CD 模式（自动启动服务）：**

如果需要脚本自动启动服务（不推荐开发环境使用）：

```bash
# 不加 --skip-service-start 参数
python "$PLUGIN_PATH/skills/integration-test/run.py"
```

## 参数说明

- `test_case_id`（可选）：指定要执行的测试用例 ID

## 输出结果

生成 `.ai-coding/results/actual-result-{test_case_id}.yaml`

## 执行完成后

用中文向用户展示：

```
✅ 集成测试执行完成！

📊 测试结果：
- 通过: X 个
- 失败: X 个
- 总计: X 个

📁 结果文件：
.ai-coding/results/

📝 后续步骤：
1. 查看测试结果
2. 如有失败，运行 /ai-coding:diff-analyzer 分析差异
3. 运行 /ai-coding:report-generator 生成测试报告

需要我帮你分析失败原因吗？
```

## 错误处理

**错误：服务未启动或不可访问**
- 检查服务是否正在运行
- 检查服务地址和端口是否正确
- 检查防火墙设置

**错误：中间件连接失败**
- 检查中间件是否运行
- 检查配置文件中的连接信息

**错误：API 调用失败**
- 检查 API 路径是否正确
- 检查请求参数是否正确
- 查看服务日志了解详细错误