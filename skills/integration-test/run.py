#!/usr/bin/env python3
"""
integration-test Skill - 集成测试执行器

执行完整的集成测试流程
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.config import ConfigManager
from shared.logger import get_logger
from models import TestCaseLoader
from engines.service import JavaServiceAdapter, PythonServiceAdapter, FrontendServiceAdapter, GoServiceAdapter, NodejsServiceAdapter
from engines.executor import BackendTestExecutor
from engines.collector import ReportGenerator


def main(test_case_ids=None, skip_service_start=False):
    """主函数"""
    print("=" * 60)
    print("AI Coding - 集成测试")
    print("=" * 60)
    print()

    # 获取项目根目录
    project_root = os.getcwd()

    # 1. 加载配置
    print("[1/6] 加载配置...")
    config_mgr = ConfigManager(project_root)
    logger = get_logger(
        level=config_mgr.get("logging.level", "INFO"),
        log_file=config_mgr.get("logging.file")
    )

    print(f"   ✓ 项目: {config_mgr.get('project.name')}")
    print(f"   ✓ 服务: {config_mgr.get('service.base_url')}")

    # 显示启用的中间件
    enabled_middleware = []
    for mw in ["mysql", "redis", "mongodb", "rabbitmq", "kafka", "elasticsearch"]:
        if config_mgr.get(f"middleware.{mw}.enabled", False):
            enabled_middleware.append(mw.capitalize())

    if enabled_middleware:
        print(f"   ✓ 中间件: {', '.join(enabled_middleware)}")
    else:
        print("   ⚠️  未启用任何中间件")
    print()

    # 2. 加载测试用例
    print("[2/6] 加载测试用例...")
    testcases_file = config_mgr.get_file_path("testcases")

    if not os.path.exists(testcases_file):
        print(f"❌ 错误: 测试用例文件不存在: {testcases_file}")
        print("   请先运行 /ai-coding:testcase-generator 生成测试用例")
        return 1

    testcases = TestCaseLoader.load_from_file(testcases_file)

    # 过滤测试用例
    if test_case_ids:
        testcases = [tc for tc in testcases if tc.id in test_case_ids]
        if not testcases:
            print(f"❌ 错误: 找不到指定的测试用例")
            return 1

    print(f"   ✓ 加载了 {len(testcases)} 个测试用例")
    print()

    # 3. 创建服务适配器
    if not skip_service_start:
        print("[3/6] 启动服务...")
        service_config = config_mgr.get("service")
        project_type = config_mgr.get("project.language")

        if project_type == "java":
            service_adapter = JavaServiceAdapter(service_config, project_root, logger)
        elif project_type == "python":
            service_adapter = PythonServiceAdapter(service_config, project_root, logger)
        elif project_type == "go":
            service_adapter = GoServiceAdapter(service_config, project_root, logger)
        elif project_type in ["javascript", "typescript"]:
            # 判断是前端还是后端 Node.js
            service_type = config_mgr.get("service.type", "backend")
            if service_type == "frontend":
                service_adapter = FrontendServiceAdapter(service_config, project_root, logger)
            else:
                service_adapter = NodejsServiceAdapter(service_config, project_root, logger)
        else:
            print(f"❌ 错误: 不支持的项目类型: {project_type}")
            return 1
    else:
        print("[3/6] 跳过服务启动（使用已运行的服务）...")
        service_adapter = None

    # 4. 准备中间件配置
    middleware_configs = {}
    for middleware in ["mysql", "redis", "mongodb", "rabbitmq", "kafka", "elasticsearch"]:
        if config_mgr.get(f"middleware.{middleware}.enabled", False):
            middleware_configs[middleware] = config_mgr.get(f"middleware.{middleware}")

    # 4.5. 读取认证配置
    auth_config = config_mgr.get("service.auth", {})

    # 5. 执行测试
    print()
    print("[4/6] 执行测试...")
    print("-" * 60)

    if service_adapter:
        executor = BackendTestExecutor(
            service_adapter,
            middleware_configs,
            config_mgr.get("service.base_url"),
            logger,
            auth_config
        )
    else:
        # 创建一个不启动服务的执行器
        from engines.executor.backend_executor import BackendTestExecutor

        class NoServiceExecutor(BackendTestExecutor):
            def run(self, testcases, plans_dir, results_dir):
                # 跳过服务启动和停止
                import time
                start_time = time.time()
                test_results = []

                for testcase in testcases:
                    result = self._execute_testcase(testcase, plans_dir, results_dir)
                    test_results.append(result)

                duration = time.time() - start_time
                return self._create_summary(test_results, duration)

        executor = NoServiceExecutor(
            None,
            middleware_configs,
            config_mgr.get("service.base_url"),
            logger,
            auth_config
        )

    plans_dir = config_mgr.get_directory("plans")
    results_dir = config_mgr.get_directory("results")

    try:
        summary = executor.run(testcases, plans_dir, results_dir)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 6. 生成报告
    print()
    print("[5/6] 生成测试报告...")
    reports_dir = config_mgr.get_directory("reports")

    report_generator = ReportGenerator(logger)

    # 生成改进建议
    recommendations = []
    if summary.pass_rate < 1.0:
        recommendations.append(f"有 {summary.failed} 个测试用例失败，建议检查失败原因")
    if summary.pass_rate < config_mgr.get("test.target_pass_rate", 0.95):
        target_rate = config_mgr.get("test.target_pass_rate", 0.95)
        recommendations.append(f"通过率 {summary.pass_rate:.2%} 低于目标 {target_rate:.2%}")
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
    print()

    # 7. 停止服务
    if service_adapter:
        print("[6/6] 停止服务...")
        print("   ✓ 服务已停止")
    else:
        print("[6/6] 跳过服务停止")
    print()

    # 8. 显示最终结果
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    print(f"总用例数: {summary.total}")
    print(f"通过数: {summary.passed} ✅")
    print(f"失败数: {summary.failed} ❌")
    print(f"通过率: {summary.pass_rate:.2%}")
    print(f"执行时间: {summary.duration:.2f}s")
    print("=" * 60)
    print()

    # 9. 返回退出码
    target_pass_rate = config_mgr.get("test.target_pass_rate", 0.95)
    if summary.pass_rate >= target_pass_rate:
        print("✅ 测试通过！")
        logger.info("Integration test PASSED")
        return 0
    else:
        print("❌ 测试失败！")
        print()
        print("下一步:")
        print("1. 查看差异报告: .ai-coding/results/diff-*.yaml")
        print("2. 运行 /ai-coding:diff-analyzer 分析根因")
        print("3. 运行 /ai-coding:auto-fixer 自动修复")
        print()
        logger.error("Integration test FAILED")
        return 1


if __name__ == "__main__":
    try:
        # 解析命令行参数
        test_case_ids = None
        skip_service_start = False

        if len(sys.argv) > 1:
            arg = sys.argv[1]
            if arg == "--skip-service-start":
                skip_service_start = True
            elif not arg.startswith("--"):
                test_case_ids = arg.split(",")

        if len(sys.argv) > 2 and sys.argv[2] == "--skip-service-start":
            skip_service_start = True

        exit_code = main(test_case_ids, skip_service_start)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ 测试已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
