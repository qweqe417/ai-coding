"""
完整的集成测试示例

展示如何使用AI Coding框架执行完整的集成测试流程
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import ConfigManager
from shared.logger import get_logger
from models import TestCaseLoader, TestSummary
from engines.service import JavaServiceAdapter, PythonServiceAdapter, FrontendServiceAdapter
from engines.executor import BackendTestExecutor
from engines.collector import ReportGenerator


def main():
    """主函数"""
    print("=" * 80)
    print("AI Coding - 集成测试框架示例")
    print("=" * 80)

    # 1. 初始化配置管理器
    print("\n[1/7] 初始化配置...")
    project_root = "."  # 当前目录，实际使用时替换为项目路径
    config_mgr = ConfigManager(project_root)

    # 2. 初始化日志
    print("[2/7] 初始化日志...")
    logger = get_logger(
        level=config_mgr.get("logging.level", "INFO"),
        log_file=config_mgr.get("logging.file")
    )
    logger.info("AI Coding Integration Test Started")

    # 3. 加载测试用例
    print("[3/7] 加载测试用例...")
    testcases_file = config_mgr.get_file_path("testcases")

    if not os.path.exists(testcases_file):
        logger.error(f"测试用例文件不存在: {testcases_file}")
        print(f"❌ 错误: 测试用例文件不存在")
        print(f"   请先创建测试用例文件: {testcases_file}")
        return

    testcases = TestCaseLoader.load_from_file(testcases_file)
    logger.info(f"Loaded {len(testcases)} test cases")
    print(f"   加载了 {len(testcases)} 个测试用例")

    # 4. 创建服务适配器
    print("[4/7] 创建服务适配器...")
    service_config = config_mgr.get("service")
    project_type = config_mgr.get("project.language")

    if project_type == "java":
        service_adapter = JavaServiceAdapter(service_config, project_root, logger)
    elif project_type == "python":
        service_adapter = PythonServiceAdapter(service_config, project_root, logger)
    elif project_type in ["javascript", "typescript"]:
        service_adapter = FrontendServiceAdapter(service_config, project_root, logger)
    else:
        logger.error(f"Unsupported project type: {project_type}")
        print(f"❌ 错误: 不支持的项目类型: {project_type}")
        return

    print(f"   服务类型: {project_type}")

    # 5. 准备中间件配置
    print("[5/7] 准备中间件配置...")
    middleware_configs = {}

    for middleware in ["mysql", "redis", "mongodb", "rabbitmq", "kafka", "elasticsearch"]:
        if config_mgr.get(f"middleware.{middleware}.enabled", False):
            middleware_configs[middleware] = config_mgr.get(f"middleware.{middleware}")
            print(f"   ✓ {middleware}")

    # 6. 执行测试
    print("[6/7] 执行集成测试...")
    print("-" * 80)

    executor = BackendTestExecutor(
        service_adapter,
        middleware_configs,
        config_mgr.get("service.base_url"),
        logger
    )

    plans_dir = config_mgr.get_directory("plans")
    results_dir = config_mgr.get_directory("results")

    try:
        summary = executor.run(testcases, plans_dir, results_dir)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"\n❌ 测试执行失败: {e}")
        return

    # 7. 生成报告
    print("\n[7/7] 生成测试报告...")
    reports_dir = config_mgr.get_directory("reports")

    report_generator = ReportGenerator(logger)

    # 生成改进建议
    recommendations = []
    if summary.pass_rate < 1.0:
        recommendations.append(f"有 {summary.failed} 个测试用例失败，建议检查失败原因")
    if summary.pass_rate < config_mgr.get("test.target_pass_rate", 0.95):
        recommendations.append(f"通过率 {summary.pass_rate:.2%} 低于目标 {config_mgr.get('test.target_pass_rate', 0.95):.2%}")
    if summary.duration > 300:
        recommendations.append(f"测试执行时间 {summary.duration:.2f}s 较长，建议优化")

    report = report_generator.generate(
        project_name=config_mgr.get("project.name"),
        summary=summary,
        fix_records=[],
        recommendations=recommendations,
        output_dir=reports_dir
    )

    print(f"   ✓ JSON报告: {reports_dir}/test-report.json")
    print(f"   ✓ Markdown报告: {reports_dir}/test-report.md")
    print(f"   ✓ HTML报告: {reports_dir}/test-report.html")

    # 8. 显示最终结果
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    print(f"总用例数: {summary.total}")
    print(f"通过数: {summary.passed} ✅")
    print(f"失败数: {summary.failed} ❌")
    print(f"通过率: {summary.pass_rate:.2%}")
    print(f"执行时间: {summary.duration:.2f}s")
    print("=" * 80)

    # 9. 返回退出码
    if summary.pass_rate >= config_mgr.get("test.target_pass_rate", 0.95):
        print("\n✅ 测试通过！")
        logger.info("Integration test PASSED")
        return 0
    else:
        print("\n❌ 测试失败！")
        logger.error("Integration test FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code or 0)
