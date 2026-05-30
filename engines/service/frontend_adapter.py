"""
前端服务启动适配器

支持Vue、React等前端框架，支持npm、yarn、pnpm
"""

from typing import Dict, Any, Optional
import subprocess
import os
import logging

from .service_adapter import ServiceAdapter, ServiceStartError


class FrontendServiceAdapter(ServiceAdapter):
    """前端服务启动适配器"""

    def __init__(self, config: Dict[str, Any], project_root: str = ".", logger: Optional[logging.Logger] = None):
        """
        初始化前端服务适配器

        Args:
            config: 服务配置
            project_root: 项目根目录
            logger: 日志实例
        """
        super().__init__(config, logger)
        self.project_root = os.path.abspath(project_root)
        self.build_tool = config.get('build_tool', 'npm')
        self.framework = config.get('framework', 'vue3')

    def start(self) -> subprocess.Popen:
        """启动前端服务"""
        try:
            # 获取启动命令
            start_command = self.config.get('start_command')

            if not start_command:
                # 根据构建工具生成默认命令
                if self.build_tool == 'npm':
                    start_command = 'npm run dev'
                elif self.build_tool == 'yarn':
                    start_command = 'yarn dev'
                elif self.build_tool == 'pnpm':
                    start_command = 'pnpm dev'
                else:
                    raise ServiceStartError(f"Unsupported build tool: {self.build_tool}")

            self.logger.info(f"Starting frontend service with command: {start_command}")
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

            self.logger.info(f"Frontend service started with PID: {self.process.pid}")
            return self.process

        except Exception as e:
            self.logger.error(f"Failed to start frontend service: {e}")
            raise ServiceStartError(f"Failed to start frontend service: {e}")
