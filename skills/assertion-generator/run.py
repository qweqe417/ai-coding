#!/usr/bin/env python3
"""
assertion-generator Skill - 数据采集计划生成器

AI分析代码，自动生成数据采集计划
"""

import sys
import os
import json

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.config import ConfigManager
from shared.logger import get_logger
from models import TestCaseLoader, CollectionPlanLoader


def analyze_code_with_ai(testcase, code_content, config):
    """
    使用AI分析代码并生成数据采集计划

    这是一个占位函数，实际实现需要调用Claude API
    在Claude Code环境中，这个函数会被替换为实际的AI调用
    """

    # 判断请求方法
    method = testcase.api.method.upper()

    # 提取参数（根据请求方法）
    if method == 'GET':
        # GET 请求从 URL 参数中提取
        params = testcase.api.params if hasattr(testcase.api, 'params') and testcase.api.params else {}
        # 如果没有参数，使用默认值
        sample_field = list(params.keys())[0] if params else 'id'
        sample_value = list(params.values())[0] if params else '1'
    else:
        # POST/PUT/DELETE 从 body 中提取
        body = testcase.api.body if testcase.api.body else {}
        sample_field = list(body.keys())[0] if body else 'id'
        sample_value = list(body.values())[0] if body else 'test'

    # 构建AI提示词
    prompt = f"""你是一个集成测试专家。请分析以下代码，生成数据采集计划。

测试用例:
ID: {testcase.id}
名称: {testcase.name}
API: {testcase.api.method} {testcase.api.url}
请求参数: {json.dumps(params if method == 'GET' else body, indent=2, ensure_ascii=False)}

代码:
{code_content}

请识别:
1. 这个API会操作哪些中间件（MySQL/Redis/MongoDB/RabbitMQ/Kafka/Elasticsearch）
2. 每个中间件的具体操作（INSERT/UPDATE/SET/PUBLISH等）
3. 需要验证哪些字段
4. 字段的预期值是什么

输出格式: YAML格式的数据采集计划，包含:
- test_case_id
- api
- collection_steps (每个步骤包含: step, name, middleware, timing, query, validations)
- expected_result

示例输出:
```yaml
test_case_id: {testcase.id}
api: {testcase.api.method} {testcase.api.url}

collection_steps:
  - step: 1
    name: 验证MySQL中的记录
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM table_name WHERE field = 'value'"
    validations:
      - field: step_1.data.field_name
        rule: equals
        value: expected_value
        reason: 字段应该正确保存

expected_result:
  step_1:
    data:
      field_name: expected_value
```

请直接输出YAML内容，不要包含其他说明文字。
"""

    # 在实际的Claude Code环境中，这里会调用AI
    # 这里返回一个示例计划作为占位

    # 根据请求方法生成不同的查询
    if method == 'GET':
        # GET 请求通常是查询操作
        return f"""test_case_id: {testcase.id}
api: {testcase.api.method} {testcase.api.url}

collection_steps:
  - step: 1
    name: 验证数据库查询结果
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM account WHERE {sample_field} = '{sample_value}'"
    validations:
      - field: step_1.data.{sample_field}
        rule: equals
        value: {sample_value}
        reason: 查询结果应该包含正确的{sample_field}

expected_result:
  step_1:
    data:
      {sample_field}: {sample_value}
"""
    else:
        # POST/PUT/DELETE 请求通常是写操作
        return f"""test_case_id: {testcase.id}
api: {testcase.api.method} {testcase.api.url}

collection_steps:
  - step: 1
    name: 验证数据库记录
    middleware: mysql
    timing: after_api
    query:
      type: select
      sql: "SELECT * FROM account WHERE {sample_field} = '{sample_value}'"
    validations:
      - field: step_1.data.{sample_field}
        rule: equals
        value: {sample_value}
        reason: {sample_field}应该正确保存到数据库

expected_result:
  step_1:
    data:
      {sample_field}: {sample_value}
"""


def find_code_files(project_root, api_path):
    """
    查找相关的代码文件

    Args:
        project_root: 项目根目录
        api_path: API路径，如 /api/users

    Returns:
        代码文件路径列表
    """
    # 简化实现：查找包含API路径的文件
    # 实际实现应该更智能，使用AST分析等

    code_files = []

    # 常见的代码目录
    code_dirs = [
        "src/main/java",
        "src",
        "app",
        "lib",
        "controllers",
        "services"
    ]

    for code_dir in code_dirs:
        dir_path = os.path.join(project_root, code_dir)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(('.java', '.py', '.go', '.js', '.ts')):
                        code_files.append(os.path.join(root, file))

    return code_files[:10]  # 限制文件数量


def read_code_content(code_files):
    """读取代码内容"""
    content = []

    for file_path in code_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                content.append(f"// File: {file_path}\n{file_content}\n")
        except Exception as e:
            continue

    return "\n".join(content)


def main(test_case_id=None):
    """主函数"""
    print("=" * 60)
    print("AI Coding - 数据采集计划生成器")
    print("=" * 60)
    print()

    # 获取项目根目录
    project_root = os.getcwd()

    # 初始化配置和日志
    config_mgr = ConfigManager(project_root)
    logger = get_logger(level="INFO")

    # 加载测试用例
    testcases_file = config_mgr.get_file_path("testcases")

    if not os.path.exists(testcases_file):
        print(f"❌ 错误: 测试用例文件不存在: {testcases_file}")
        print("   请先运行 /ai-coding:testcase-generator 生成测试用例")
        return 1

    testcases = TestCaseLoader.load_from_file(testcases_file)

    # 过滤测试用例
    if test_case_id:
        testcases = [tc for tc in testcases if tc.id == test_case_id]
        if not testcases:
            print(f"❌ 错误: 找不到测试用例 {test_case_id}")
            return 1

    print(f"找到 {len(testcases)} 个测试用例")
    print()

    plans_dir = config_mgr.get_directory("plans")
    os.makedirs(plans_dir, exist_ok=True)

    # 处理每个测试用例
    for i, testcase in enumerate(testcases, 1):
        print(f"[{i}/{len(testcases)}] 处理测试用例: {testcase.id} - {testcase.name}")
        print(f"   API: {testcase.api.method} {testcase.api.url}")

        # 1. 查找相关代码文件
        print("   [1/5] 查找相关代码...")
        code_files = find_code_files(project_root, testcase.api.url)
        print(f"      找到 {len(code_files)} 个代码文件")

        # 2. 读取代码内容
        print("   [2/5] 读取代码内容...")
        code_content = read_code_content(code_files)
        print(f"      代码总行数: {len(code_content.splitlines())}")

        # 3. AI分析代码
        print("   [3/5] AI分析代码...")
        print("      ⚠️  注意: 当前使用示例计划")
        print("      在Claude Code环境中会调用真实的AI分析")

        plan_yaml = analyze_code_with_ai(testcase, code_content, config_mgr.config)

        # 4. 保存数据采集计划
        print("   [4/5] 保存数据采集计划...")
        plan_file = os.path.join(plans_dir, f"data-collection-plan-{testcase.id}.yaml")

        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan_yaml)

        print(f"      ✓ {plan_file}")

        # 5. 验证计划
        print("   [5/5] 验证计划...")
        try:
            plan = CollectionPlanLoader.load_from_file(plan_file)
            print(f"      ✓ 计划有效，包含 {len(plan.collection_steps)} 个采集步骤")
        except Exception as e:
            print(f"      ⚠️  计划验证失败: {e}")

        print()

    # 显示总结
    print("=" * 60)
    print("✅ 数据采集计划生成完成！")
    print("=" * 60)
    print()
    print(f"生成了 {len(testcases)} 个数据采集计划")
    print(f"保存位置: {plans_dir}")
    print()
    print("下一步:")
    print("1. 审核生成的数据采集计划")
    print("2. 运行 /ai-coding:integration-test 执行测试")
    print()

    logger.info(f"Generated {len(testcases)} data collection plans")
    return 0


if __name__ == "__main__":
    try:
        # 获取命令行参数
        test_case_id = sys.argv[1] if len(sys.argv) > 1 else None

        exit_code = main(test_case_id)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ 已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
