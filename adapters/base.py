"""
中间件适配器基类

定义所有中间件适配器的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging


class MiddlewareAdapter(ABC):
    """中间件适配器基类"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化适配器

        Args:
            config: 中间件配置
            logger: 日志实例
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.connected = False

    @abstractmethod
    def connect(self):
        """
        连接到中间件

        Raises:
            ConnectionError: 连接失败
        """
        pass

    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass

    @abstractmethod
    def query(self, query_config: Dict[str, Any]) -> Any:
        """
        执行查询

        Args:
            query_config: 查询配置

        Returns:
            查询结果

        Raises:
            QueryError: 查询失败
        """
        pass

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connected

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


class MiddlewareError(Exception):
    """中间件错误基类"""
    pass


class ConnectionError(MiddlewareError):
    """连接错误"""
    pass


class QueryError(MiddlewareError):
    """查询错误"""
    pass


class TimeoutError(MiddlewareError):
    """超时错误"""
    pass
