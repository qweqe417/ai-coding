"""
服务启动适配器基类

定义所有服务启动适配器的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import subprocess
import time
import requests
import logging


class ServiceAdapter(ABC):
    """服务启动适配器基类"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化适配器

        Args:
            config: 服务配置
            logger: 日志实例
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.process: Optional[subprocess.Popen] = None
        self.running = False

    @abstractmethod
    def start(self) -> subprocess.Popen:
        """
        启动服务

        Returns:
            subprocess.Popen: 服务进程

        Raises:
            ServiceStartError: 启动失败
        """
        pass

    def stop(self):
        """停止服务"""
        if self.process:
            self.logger.info("Stopping service...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("Service did not stop gracefully, killing...")
                self.process.kill()
                self.process.wait()

            self.process = None
            self.running = False
            self.logger.info("Service stopped")

    def health_check(self, max_retries: int = 30, retry_interval: int = 2) -> bool:
        """
        健康检查

        Args:
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）

        Returns:
            bool: 是否健康
        """
        health_check_url = self.config.get('health_check_url')
        if not health_check_url:
            self.logger.warning("No health_check_url configured, skipping health check")
            return True

        self.logger.info(f"Waiting for service to be ready: {health_check_url}")

        for i in range(max_retries):
            try:
                response = requests.get(health_check_url, timeout=5)
                if response.status_code == 200:
                    self.logger.info(f"Service is ready (attempt {i + 1}/{max_retries})")
                    self.running = True
                    return True
            except requests.exceptions.RequestException:
                pass

            if i < max_retries - 1:
                self.logger.debug(f"Service not ready yet, retrying in {retry_interval}s... (attempt {i + 1}/{max_retries})")
                time.sleep(retry_interval)

        self.logger.error(f"Service failed to start after {max_retries} attempts")
        return False

    def is_running(self) -> bool:
        """检查服务是否运行中"""
        return self.running and self.process is not None and self.process.poll() is None

    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        if not self.health_check():
            self.stop()
            raise ServiceStartError("Service failed health check")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


class ServiceError(Exception):
    """服务错误基类"""
    pass


class ServiceStartError(ServiceError):
    """服务启动错误"""
    pass


class ServiceStopError(ServiceError):
    """服务停止错误"""
    pass
