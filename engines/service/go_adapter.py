"""
Go服务启动适配器

支持Gin、Echo等框架
"""

from typing import Dict, Any, Optional
import subprocess
import os
import logging

from .service_adapter import ServiceAdapter, ServiceStartError


class GoServiceAdapter(ServiceAdapter):
    """Go服务启动适配器"""

    def __init__(self, config: Dict[str, Any], project_root: str = ".", logger: Optional[logging.Logger] = None):
        """
        初始化Go服务适配器

        Args:
            config: 服务配置
            project_root: 项目根目录
            logger: 日志实例
        """
        super().__init__(config, logger)
        self.project_root = os.path.abspath(project_root)
        self.framework = config.get('framework', 'go')

    def start(self) -> subprocess.Popen:
        """启动Go服务"""
        try:
            # 获取启动命令
            start_command = self.config.get('start_command')

            if not start_command:
                # 根据框架生成默认命令
                if self.framework in ('gin', 'echo', 'go'):
                    # 查找 main.go
                    main_files = []
                    for root, dirs, files in os.walk(self.project_root):
                        # 跳过 vendor 目录
                        if 'vendor' in dirs:
                            dirs.remove('vendor')
                        for f in files:
                            if f == 'main.go':
                                main_files.append(os.path.join(root, f))

                    if main_files:
                        # 使用找到的第一个 main.go
                        main_dir = os.path.dirname(main_files[0])
                        rel_path = os.path.relpath(main_dir, self.project_root)
                        start_command = f'go run ./{rel_path}'
                    else:
                        start_command = 'go run .'
                else:
                    raise ServiceStartError(f"Unsupported framework: {self.framework}")

            self.logger.info(f"Starting Go service with command: {start_command}")
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

            self.logger.info(f"Go service started with PID: {self.process.pid}")
            return self.process

        except Exception as e:
            self.logger.error(f"Failed to start Go service: {e}")
            raise ServiceStartError(f"Failed to start Go service: {e}")
