"""
Node.js服务启动适配器

支持Express、Koa、Fastify等框架
"""

from typing import Dict, Any, Optional
import subprocess
import os
import logging

from .service_adapter import ServiceAdapter, ServiceStartError


class NodejsServiceAdapter(ServiceAdapter):
    """Node.js服务启动适配器"""

    def __init__(self, config: Dict[str, Any], project_root: str = ".", logger: Optional[logging.Logger] = None):
        """
        初始化Node.js服务适配器

        Args:
            config: 服务配置
            project_root: 项目根目录
            logger: 日志实例
        """
        super().__init__(config, logger)
        self.project_root = os.path.abspath(project_root)
        self.framework = config.get('framework', 'node')

        # 确定包管理器
        self.package_manager = self._detect_package_manager()

    def _detect_package_manager(self) -> str:
        """检测包管理器"""
        # 检查配置文件优先级
        if os.path.exists(os.path.join(self.project_root, 'pnpm-lock.yaml')):
            return 'pnpm'
        if os.path.exists(os.path.join(self.project_root, 'yarn.lock')):
            return 'yarn'
        if os.path.exists(os.path.join(self.project_root, 'bun.lockb')):
            return 'bun'
        # 默认使用 npm
        return 'npm'

    def start(self) -> subprocess.Popen:
        """启动Node.js服务"""
        try:
            start_command = self.config.get('start_command')

            if not start_command:
                if self.framework in ('express', 'koa', 'fastify'):
                    start_command = f'{self.package_manager} start'
                elif self.framework == 'next':
                    start_command = f'{self.package_manager} run build && {self.package_manager} start'
                elif self.framework == 'nuxt':
                    start_command = 'nuxt start'
                else:
                    # 默认：使用 npm start
                    start_command = f'{self.package_manager} start'

            self.logger.info(f"Starting Node.js service with command: {start_command}")
            self.logger.info(f"Working directory: {self.project_root}")
            self.logger.info(f"Package manager: {self.package_manager}")

            # 启动服务
            self.process = subprocess.Popen(
                start_command,
                shell=True,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.logger.info(f"Node.js service started with PID: {self.process.pid}")
            return self.process

        except Exception as e:
            self.logger.error(f"Failed to start Node.js service: {e}")
            raise ServiceStartError(f"Failed to start Node.js service: {e}")
