#!/usr/bin/env python3
"""
init Skill - 项目初始化

自动检测项目类型并生成配置文件
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.config import ProjectDetector, ConfigManager
from shared.logger import get_logger


def main():
    """主函数"""
    print("=" * 60)
    print("AI Coding - 项目初始化")
    print("=" * 60)
    print()

    # 获取项目根目录
    project_root = os.getcwd()
    print(f"项目目录: {project_root}")
    print()

    # 初始化日志
    logger = get_logger(level="INFO")

    # 检查是否已存在配置文件
    config_file = os.path.join(project_root, ".ai-coding", "config.yaml")
    if os.path.exists(config_file):
        print("⚠️  配置文件已存在: .ai-coding/config.yaml")
        response = input("是否覆盖? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ 初始化已取消")
            return 1
        print()

    # 1. 检测项目类型
    print("[1/4] 检测项目类型...")
    detector = ProjectDetector(project_root)
    project_type = detector.detect_project_type()

    if project_type:
        print(f"   ✓ 项目类型: {project_type.category}")
        print(f"   ✓ 语言: {project_type.language}")
        print(f"   ✓ 框架: {project_type.framework}")
        print(f"   ✓ 构建工具: {project_type.build_tool}")
    else:
        print("   ⚠️  无法自动检测项目类型")
        print("   将使用默认配置，请手动修改 .ai-coding/config.yaml")
    print()

    # 2. 生成配置文件
    print("[2/4] 生成配置文件...")
    # ConfigManager.__init__() 会自动检测项目类型并生成配置文件
    config_mgr = ConfigManager(project_root)

    print(f"   ✓ 配置文件: .ai-coding/config.yaml")
    print()

    # 3. 创建目录结构
    print("[3/4] 创建目录结构...")
    directories = [
        "specs",
        "testcases",
        "plans",
        "results",
        "analysis",
        "fixes",
        "reports",
        "logs"
    ]

    for dir_name in directories:
        dir_path = config_mgr.get_directory(dir_name)
        os.makedirs(dir_path, exist_ok=True)
        print(f"   ✓ .ai-coding/{dir_name}")
    print()

    # 4. 显示配置摘要
    print("[4/4] 配置摘要")
    print(f"   项目名称: {config_mgr.get('project.name')}")
    print(f"   服务URL: {config_mgr.get('service.base_url')}")
    print(f"   启动命令: {config_mgr.get('service.start_command')}")
    print()

    # 显示中间件配置
    print("   中间件:")
    middleware_list = ["mysql", "redis", "mongodb", "rabbitmq", "kafka", "elasticsearch"]
    enabled_count = 0

    for middleware in middleware_list:
        if config_mgr.get(f"middleware.{middleware}.enabled", False):
            host = config_mgr.get(f"middleware.{middleware}.host", "localhost")
            port = config_mgr.get(f"middleware.{middleware}.port", "")
            print(f"   ✓ {middleware.capitalize()} ({host}:{port})")
            enabled_count += 1

    if enabled_count == 0:
        print("   ⚠️  未启用任何中间件")
        print("   请编辑 .ai-coding/config.yaml 启用所需的中间件")
    print()

    # 5. 显示下一步建议
    print("=" * 60)
    print("✅ 初始化完成！")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 编辑 .ai-coding/config.yaml 配置中间件连接信息")
    print("2. 运行 /ai-coding:testcase-generator 生成测试用例")
    print("3. 运行 /ai-coding:assertion-generator 生成数据采集计划")
    print("4. 运行 /ai-coding:integration-test 执行测试")
    print()
    print("或者运行完整流程:")
    print("  /ai-coding:full-test-pipeline")
    print()

    logger.info("Project initialization completed")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ 初始化已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
