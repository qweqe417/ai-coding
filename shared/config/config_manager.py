"""
配置管理器

统一管理所有配置，支持自动初始化和配置读取
"""

import os
import yaml
from typing import Dict, Any, Optional
from .project_detector import ProjectDetector, ProjectType
from .auto_config import AutoConfigReader


class ConfigManager:
    """配置管理器"""

    def __init__(self, project_root: str = "."):
        self.project_root = os.path.abspath(project_root)
        self.config_file = os.path.normpath(os.path.join(self.project_root, ".ai-coding", "config.yaml"))
        self.config: Optional[Dict[str, Any]] = None

        # 检查是否已初始化
        if not os.path.exists(self.config_file):
            print("⚠️  项目未初始化")
            print("正在自动初始化...")
            self._auto_init()

        # 加载配置
        self.config = self._load_config()

    def _auto_init(self):
        """自动初始化：创建目录和配置文件"""
        # 1. 创建 .ai-coding 目录
        ai_coding_dir = os.path.normpath(os.path.join(self.project_root, ".ai-coding"))
        os.makedirs(ai_coding_dir, exist_ok=True)

        # 2. 自动检测项目信息
        detector = ProjectDetector(self.project_root)
        project_type = detector.detect_project_type()

        # 3. 生成配置文件
        config = self._generate_default_config(project_type, detector)

        # 4. 写入配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        print(f"✅ 初始化完成: {self.config_file}")
        print(f"   项目类型: {project_type.category} - {project_type.language} - {project_type.framework}")
        print(f"   构建工具: {project_type.build_tool}")

    def _generate_default_config(self, project_type: ProjectType, detector: ProjectDetector) -> Dict[str, Any]:
        """生成默认配置"""
        project_name = os.path.basename(self.project_root)

        # 基础配置
        config = {
            'version': '1.0.0',
            'project': {
                'name': project_name,
                'category': project_type.category,
                'language': project_type.language,
                'framework': project_type.framework,
                'build_tool': project_type.build_tool,
                'root': '.'
            },
            'directories': {
                'specs': '.ai-coding/specs',
                'testcases': '.ai-coding/testcases',
                'plans': '.ai-coding/plans',
                'results': '.ai-coding/results',
                'analysis': '.ai-coding/analysis',
                'fixes': '.ai-coding/fixes',
                'reports': '.ai-coding/reports',
                'logs': '.ai-coding/logs'
            },
            'naming': {
                'testcases': 'testcases.json',
                'collection_plan': 'data-collection-plan-{test_case_id}.yaml',
                'actual_result': 'actual-result-{test_case_id}.yaml',
                'diff_result': 'diff-{test_case_id}.yaml',
                'root_cause': 'root-cause-analysis-{test_case_id}.yaml',
                'fix_record': 'fix-record-{test_case_id}.yaml',
                'test_summary': 'test-summary.json',
                'regression_result': 'regression-test-result.yaml',
                'report_md': 'test-report.md',
                'report_html': 'test-report.html',
                'report_json': 'test-report.json'
            }
        }

        # 服务配置（根据项目类型）
        config['service'] = self._generate_service_config(project_type)

        # 配置源
        config['config_source'] = {
            'type': 'auto',
            'detected': 'local'  # TODO: 检测Nacos
        }

        # 中间件配置 - 自动检测
        auto_reader = AutoConfigReader(self.project_root)
        detected_middleware = auto_reader.detect_middleware_configs()

        # 合并自动检测和默认配置
        config['middleware'] = {
            'mysql': detected_middleware.get('mysql', {'enabled': False}),
            'redis': detected_middleware.get('redis', {'enabled': False}),
            'mongodb': detected_middleware.get('mongodb', {'enabled': False}),
            'rabbitmq': detected_middleware.get('rabbitmq', {'enabled': False}),
            'kafka': detected_middleware.get('kafka', {'enabled': False}),
            'elasticsearch': detected_middleware.get('elasticsearch', {'enabled': False})
        }

        # 测试配置
        config['test'] = {
            'strategy': project_type.category,
            'max_regression_rounds': 3,
            'auto_fix_enabled': True,
            'auto_fix_confidence_threshold': 0.9,
            'target_pass_rate': 0.95
        }

        # 前端测试配置
        if project_type.category in ['frontend', 'fullstack']:
            config['test']['frontend'] = {
                'browser': 'chromium',
                'headless': True,
                'viewport': '1920x1080',
                'timeout': 30000
            }

        # 审阅配置
        config['review'] = {
            'pause_for_review': True,
            'review_points': ['testcases', 'collection_plans', 'code_fixes'],
            'auto_continue': False
        }

        # Git配置
        config['git'] = {
            'auto_commit': False,
            'base_branch': 'main'
        }

        # 日志配置
        config['logging'] = {
            'level': 'INFO',
            'file': '.ai-coding/logs/integration-test.log',
            'max_size': '10MB',
            'backup_count': 5
        }

        # Spec文档路径
        config['spec_file'] = 'docs/spec.md'

        return config

    def _generate_service_config(self, project_type: ProjectType) -> Dict[str, Any]:
        """生成服务配置"""
        service_config = {
            'type': project_type.framework,
            'startup_timeout': 60
        }

        # 尝试从项目配置中自动检测服务端口和URL
        auto_reader = AutoConfigReader(self.project_root)
        detected_service = auto_reader.detect_service_config()
        if 'port' in detected_service:
            service_config['detected_port'] = detected_service['port']
        if 'base_url' in detected_service:
            service_config['detected_base_url'] = detected_service['base_url']

        # 根据项目类型生成启动命令和健康检查URL
        if project_type.category == 'backend':
            if project_type.language == 'java':
                if project_type.build_tool == 'maven':
                    service_config['start_command'] = 'mvn spring-boot:run'
                else:
                    service_config['start_command'] = './gradlew bootRun'
                service_config['health_check_url'] = 'http://localhost:8080/actuator/health'
                service_config['base_url'] = 'http://localhost:8080'

            elif project_type.language == 'python':
                if project_type.framework == 'flask':
                    service_config['start_command'] = 'python app.py'
                elif project_type.framework == 'django':
                    service_config['start_command'] = 'python manage.py runserver'
                elif project_type.framework == 'fastapi':
                    service_config['start_command'] = 'uvicorn main:app --reload'
                service_config['health_check_url'] = 'http://localhost:5000/health'
                service_config['base_url'] = 'http://localhost:5000'

            elif project_type.language == 'go':
                service_config['start_command'] = 'go run main.go'
                service_config['health_check_url'] = 'http://localhost:8080/health'
                service_config['base_url'] = 'http://localhost:8080'

            elif project_type.language == 'nodejs':
                service_config['start_command'] = 'npm start'
                service_config['health_check_url'] = 'http://localhost:3000/health'
                service_config['base_url'] = 'http://localhost:3000'

        elif project_type.category in ['frontend', 'fullstack']:
            if project_type.build_tool == 'npm':
                service_config['start_command'] = 'npm run dev'
            elif project_type.build_tool == 'yarn':
                service_config['start_command'] = 'yarn dev'
            elif project_type.build_tool == 'pnpm':
                service_config['start_command'] = 'pnpm dev'

            service_config['health_check_url'] = 'http://localhost:3000'
            service_config['base_url'] = 'http://localhost:3000'

        return service_config

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_directory(self, dir_type: str) -> str:
        """
        获取目录路径

        Args:
            dir_type: specs | testcases | plans | results | analysis | fixes | reports | logs

        Returns:
            目录绝对路径
        """
        dir_path = self.config['directories'][dir_type]
        full_path = os.path.normpath(os.path.join(self.project_root, dir_path))

        # 确保目录存在
        os.makedirs(full_path, exist_ok=True)

        return full_path

    def get_file_path(self, file_type: str, **kwargs) -> str:
        """
        获取文件路径

        Args:
            file_type: testcases | collection_plan | actual_result | diff_result |
                      root_cause | fix_record | test_summary | regression_result |
                      report_md | report_html | report_json
            **kwargs: 文件名占位符参数（如 test_case_id）

        Returns:
            文件绝对路径
        """
        # 获取文件名模板
        filename_template = self.config['naming'][file_type]

        # 替换占位符
        filename = filename_template.format(**kwargs)

        # 确定目录
        dir_mapping = {
            'testcases': 'testcases',
            'collection_plan': 'plans',
            'actual_result': 'results',
            'diff_result': 'results',
            'test_summary': 'results',
            'regression_result': 'results',
            'root_cause': 'analysis',
            'fix_record': 'fixes',
            'report_md': 'reports',
            'report_html': 'reports',
            'report_json': 'reports'
        }

        dir_type = dir_mapping[file_type]
        dir_path = self.get_directory(dir_type)

        return os.path.normpath(os.path.join(dir_path, filename))

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def save(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
