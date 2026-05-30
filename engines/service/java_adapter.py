"""
Java服务启动适配器

支持Maven和Gradle构建工具
"""

from typing import Dict, Any, Optional
import subprocess
import os
import logging

from .service_adapter import ServiceAdapter, ServiceStartError


class JavaServiceAdapter(ServiceAdapter):
    """Java服务启动适配器"""

    def __init__(self, config: Dict[str, Any], project_root: str = ".", logger: Optional[logging.Logger] = None):
        """
        初始化Java服务适配器

        Args:
            config: 服务配置
            project_root: 项目根目录
            logger: 日志实例
        """
        super().__init__(config, logger)
        self.project_root = os.path.abspath(project_root)
        self.build_tool = config.get('build_tool', 'maven')

    def start(self) -> subprocess.Popen:
        """启动Java服务"""
        try:
            # 获取启动命令
            start_command = self.config.get('start_command')

            if not start_command:
                # 根据构建工具生成默认命令
                if self.build_tool == 'maven':
                    start_command = 'mvn spring-boot:run'
                elif self.build_tool == 'gradle':
                    start_command = './gradlew bootRun'
                else:
                    raise ServiceStartError(f"Unsupported build tool: {self.build_tool}")

            self.logger.info(f"Starting Java service with command: {start_command}")
            self.logger.info(f"Working directory: {self.project_root}")

            # 启动服务
            self.process = subprocess.Popen(
                start_command,
                shell=True,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.logger.info(f"Java service started with PID: {self.process.pid}")
            return self.process

        except Exception as e:
            self.logger.error(f"Failed to start Java service: {e}")
            raise ServiceStartError(f"Failed to start Java service: {e}")
