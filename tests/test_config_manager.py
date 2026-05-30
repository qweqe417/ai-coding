"""
测试配置管理器

用于验证项目类型检测和配置初始化功能
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import ConfigManager


def test_config_manager():
    """测试配置管理器"""
    print("=" * 60)
    print("测试配置管理器")
    print("=" * 60)

    # 测试当前项目
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"\n项目根目录: {project_root}")

    # 初始化配置管理器
    print("\n初始化配置管理器...")
    config_mgr = ConfigManager(project_root)

    # 显示配置信息
    print("\n项目配置:")
    print(f"  名称: {config_mgr.get('project.name')}")
    print(f"  类别: {config_mgr.get('project.category')}")
    print(f"  语言: {config_mgr.get('project.language')}")
    print(f"  框架: {config_mgr.get('project.framework')}")
    print(f"  构建工具: {config_mgr.get('project.build_tool')}")

    print("\n服务配置:")
    print(f"  启动命令: {config_mgr.get('service.start_command')}")
    print(f"  健康检查: {config_mgr.get('service.health_check_url')}")
    print(f"  基础URL: {config_mgr.get('service.base_url')}")

    print("\n测试配置:")
    print(f"  测试策略: {config_mgr.get('test.strategy')}")
    print(f"  目标通过率: {config_mgr.get('test.target_pass_rate')}")
    print(f"  自动修复: {config_mgr.get('test.auto_fix_enabled')}")

    print("\n目录配置:")
    print(f"  Specs目录: {config_mgr.get_directory('specs')}")
    print(f"  测试用例目录: {config_mgr.get_directory('testcases')}")
    print(f"  报告目录: {config_mgr.get_directory('reports')}")

    print("\n文件路径:")
    print(f"  测试用例文件: {config_mgr.get_file_path('testcases')}")
    print(f"  采集计划文件: {config_mgr.get_file_path('collection_plan', test_case_id='TC001')}")
    print(f"  HTML报告: {config_mgr.get_file_path('report_html')}")

    print("\n" + "=" * 60)
    print("✅ 配置管理器测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_config_manager()
