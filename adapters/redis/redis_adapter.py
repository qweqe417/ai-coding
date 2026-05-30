"""
Redis适配器

支持GET、HGETALL、EXISTS等操作
"""

from typing import Dict, Any, Optional
import logging
import json

try:
    import redis
except ImportError:
    redis = None

from ..base import MiddlewareAdapter, ConnectionError, QueryError


class RedisAdapter(MiddlewareAdapter):
    """Redis适配器"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化Redis适配器

        Args:
            config: Redis配置
                {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "password": "password",  # 可选
                    "decode_responses": True
                }
        """
        super().__init__(config, logger)

        if redis is None:
            raise ImportError("redis is not installed. Run: pip install redis")

        self.client = None

    def connect(self):
        """连接到Redis"""
        try:
            self.client = redis.Redis(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 6379),
                db=self.config.get('db', 0),
                password=self.config.get('password'),
                decode_responses=self.config.get('decode_responses', True)
            )

            # 测试连接
            self.client.ping()
            self.connected = True
            self.logger.info(f"Connected to Redis: {self.config['host']}:{self.config['port']}/{self.config.get('db', 0)}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self.connected = False
            self.logger.info("Disconnected from Redis")

    def query(self, query_config: Dict[str, Any]) -> Any:
        """
        执行查询

        Args:
            query_config: 查询配置
                {
                    "type": "get" | "hgetall" | "exists",
                    "key": "user:1001"
                }

        Returns:
            查询结果
                - get: str 或 None
                - hgetall: Dict
                - exists: bool
        """
        if not self.connected:
            raise ConnectionError("Not connected to Redis")

        query_type = query_config.get('type', 'get')
        key = query_config['key']

        try:
            self.logger.debug(f"Executing Redis {query_type.upper()}: {key}")

            if query_type == 'get':
                result = self.client.get(key)
                self.logger.debug(f"GET returned: {result}")

                # 尝试解析JSON
                if result and isinstance(result, str):
                    try:
                        return json.loads(result)
                    except json.JSONDecodeError:
                        return result
                return result

            elif query_type == 'hgetall':
                result = self.client.hgetall(key)
                self.logger.debug(f"HGETALL returned {len(result)} fields")
                return result

            elif query_type == 'exists':
                result = self.client.exists(key)
                self.logger.debug(f"EXISTS returned: {result}")
                return bool(result)

            else:
                raise QueryError(f"Unsupported query type: {query_type}")

        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise QueryError(f"Query failed: {e}")

    def get(self, key: str) -> Any:
        """
        GET操作（便捷方法）

        Args:
            key: Redis key

        Returns:
            值（自动解析JSON）
        """
        return self.query({'type': 'get', 'key': key})

    def hgetall(self, key: str) -> Dict[str, Any]:
        """
        HGETALL操作（便捷方法）

        Args:
            key: Redis key

        Returns:
            Hash字典
        """
        return self.query({'type': 'hgetall', 'key': key})

    def exists(self, key: str) -> bool:
        """
        EXISTS操作（便捷方法）

        Args:
            key: Redis key

        Returns:
            是否存在
        """
        return self.query({'type': 'exists', 'key': key})
