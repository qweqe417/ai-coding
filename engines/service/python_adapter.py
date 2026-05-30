"""
Python服务启动适配器

支持Flask、Django、FastAPI等框架
"""

from typing import Dict, Any, Optional
import subprocess
import os
import logging

from .service_adapter import ServiceAdapter, ServiceStartError


class PythonServiceAdapter(ServiceAdapter):
    """Python服务启动适配器"""

    def __init__(self, config: Dict[str, Any], project_root: str = ".", logger: Optional[logging.Logger] = None):
        """
        初始化Python服务适配器

        Args:
            config: 服务配置
            project_root: 项目根目录
            logger: 日志实例
        """
        super().__init__(config, logger)
        self.project_root = os.path.abspath(project_root)
        self.framework = config.get('framework', 'flask')

    def start(self) -> subprocess.Popen:
        """启动Python服务"""
        try:
            # 获取启动命令
            start_command = self.config.get('start_command')

            if not start_command:
                # 根据框架生成默认命令
                if self.framework == 'flask':
                    start_command = 'python app.py'
                elif self.framework == 'django':
                    start_command = 'python manage.py runserver'
                elif self.framework == 'fastapi':
                    start_command = 'uvicorn main:app --reload'
                else:
                    raise ServiceStartError(f"Unsupported framework: {self.framework}")

            self.logger.info(f"Starting Python service with command: {start_command}")
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

            self.logger.info(f"Python service started with PID: {self.process.pid}")
            return self.process

        except Exception as e:
            self.logger.error(f"Failed to start Python service: {e}")
            raise ServiceStartError(f"Failed to start Python service: {e}")
