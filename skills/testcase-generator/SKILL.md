---
name: testcase-generator
description: "从 API 规范文档生成测试用例"
---

# testcase-generator - 测试用例生成器

使用 AI 从规范文档自动生成测试用例。

## 重要规则

**必须用中文与用户交流** - 所有输出、提示、摘要都必须使用中文。

## 功能说明

- 解析 API 规范文档
- 生成正常流程测试用例
- 生成边界值测试用例
- 生成异常流程测试用例
- 生成幂等性测试用例

## 前置条件

- [ ] `.ai-coding/config.yaml` 已存在（先运行 `/ai-coding:init`）
- [ ] 规范文档存在于 `.ai-coding/specs/` 或 `docs/` 目录

## 执行步骤

**重要：必须使用 Bash 工具执行 Python 脚本。**

```bash
# 查找插件安装路径
PLUGIN_PATH=$(find ~/.claude/plugins/cache -path "*/ai-coding-marketplace/ai-coding/*" -name "skills" -type d | head -1 | xargs dirname)

# 如果 cache 中没找到，尝试 local
if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

# 如果还是没找到，报错
if [ -z "$PLUGIN_PATH" ]; then
    echo "❌ 错误: 找不到 ai-coding 插件"
    exit 1
fi

# 执行测试用例生成脚本
python "$PLUGIN_PATH/skills/testcase-generator/run.py"
```

## 参数说明

无需参数。脚本会：
1. 在 `.ai-coding/specs/` 和 `docs/` 中搜索规范文档
2. 提示你选择要处理的规范文档
3. 自动生成测试用例

## 输出结果

生成 `.ai-coding/testcases/testcases.json`，包含：
- 正常流程测试用例
- 边界值测试用例
- 异常流程测试用例
- 幂等性测试用例（如适用）

## 执行完成后

用中文向用户展示：

```
✅ 测试用例生成成功！

📊 生成统计：
- 正常流程用例: X 个
- 边界值用例: X 个
- 异常流程用例: X 个
- 幂等性用例: X 个
- 总计: X 个测试用例

📁 输出文件：
.ai-coding/testcases/testcases.json

📝 后续步骤：
1. 查看生成的测试用例
2. 手动添加特殊场景用例（如需要）
3. 运行 /ai-coding:assertion-generator 生成数据采集计划

需要我帮你生成数据采集计划吗？
```

## 测试用例类型

**正常流程：**
- 有效的输入参数
- 预期成功响应

**边界值：**
- 最小/最大值
- 空值/null 值
- 特殊字符

**异常流程：**
- 缺少必需参数
- 无效参数类型
- 无效参数格式
- 业务规则违反

**幂等性：**
- 重复相同请求
- 验证结果一致性

## 配置说明

编辑 `.ai-coding/config.yaml` 配置：

```yaml
testcase_generator:
  model: claude-sonnet-4
  normal_cases: 1      # 每个 API 生成的正常用例数
  boundary_cases: 2    # 边界值用例数
  error_cases: 3       # 异常用例数
  generate_idempotent: true  # 是否生成幂等性用例
  data_strategy: realistic   # 数据生成策略
```

## 错误处理

**错误：找不到规范文档**
- 在 `.ai-coding/specs/` 或 `docs/` 中创建规范文档
- 确保规范文档包含 API 定义

**错误：AI 分析失败**
- 检查规范文档格式是否正确
- 确保 API 定义清晰完整

**错误：无法写入测试用例**
- 检查 `.ai-coding/testcases/` 目录是否存在
- 检查文件权限
