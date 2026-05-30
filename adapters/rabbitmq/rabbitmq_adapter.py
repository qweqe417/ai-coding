"""
RabbitMQ适配器

支持消费消息，支持超时控制
"""

from typing import Dict, Any, Optional, List
import logging
import time

try:
    import pika
except ImportError:
    pika = None

from ..base import MiddlewareAdapter, ConnectionError, QueryError, TimeoutError


class RabbitMQAdapter(MiddlewareAdapter):
    """RabbitMQ适配器"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化RabbitMQ适配器

        Args:
            config: RabbitMQ配置
                {
                    "host": "localhost",
                    "port": 5672,
                    "username": "guest",
                    "password": "guest",
                    "virtual_host": "/"
                }
        """
        super().__init__(config, logger)

        if pika is None:
            raise ImportError("pika is not installed. Run: pip install pika")

        self.connection = None
        self.channel = None

    def connect(self):
        """连接到RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                self.config.get('username', 'guest'),
                self.config.get('password', 'guest')
            )

            parameters = pika.ConnectionParameters(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5672),
                virtual_host=self.config.get('virtual_host', '/'),
                credentials=credentials
            )

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.connected = True
            self.logger.info(f"Connected to RabbitMQ: {self.config['host']}:{self.config['port']}")

        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise ConnectionError(f"Failed to connect to RabbitMQ: {e}")

    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
            self.connected = False
            self.logger.info("Disconnected from RabbitMQ")

    def query(self, query_config: Dict[str, Any]) -> Any:
        """
        执行查询（消费消息）

        Args:
            query_config: 查询配置
                {
                    "type": "consume",
                    "queue": "test_queue",
                    "timeout": 10,  # 超时时间（秒）
                    "max_messages": 1  # 最多消费多少条消息
                }

        Returns:
            消息列表 List[Dict]
        """
        if not self.connected:
            raise ConnectionError("Not connected to RabbitMQ")

        query_type = query_config.get('type', 'consume')
        queue = query_config['queue']
        timeout = query_config.get('timeout', 10)
        max_messages = query_config.get('max_messages', 1)

        try:
            if query_type == 'consume':
                return self._consume_messages(queue, timeout, max_messages)
            else:
                raise QueryError(f"Unsupported query type: {query_type}")

        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise QueryError(f"Query failed: {e}")

    def _consume_messages(self, queue: str, timeout: int, max_messages: int) -> List[Dict[str, Any]]:
        """消费消息"""
        self.logger.debug(f"Consuming messages from queue: {queue} (timeout={timeout}s, max={max_messages})")

        # 声明队列（如果不存在）
        self.channel.queue_declare(queue=queue, durable=True)

        messages = []
        start_time = time.time()

        while len(messages) < max_messages:
            # 检查超时
            if time.time() - start_time > timeout:
                self.logger.warning(f"Timeout after {timeout}s, got {len(messages)} messages")
                raise TimeoutError(f"Timeout after {timeout}s")

            # 获取消息
            method_frame, header_frame, body = self.channel.basic_get(queue=queue, auto_ack=True)

            if method_frame:
                message = {
                    'body': body.decode('utf-8') if isinstance(body, bytes) else body,
                    'delivery_tag': method_frame.delivery_tag,
                    'routing_key': method_frame.routing_key
                }
                messages.append(message)
                self.logger.debug(f"Consumed message: {message}")
            else:
                # 队列为空，等待一下
                time.sleep(0.1)

        self.logger.debug(f"Consumed {len(messages)} messages from {queue}")
        return messages

    def consume(self, queue: str, timeout: int = 10, max_messages: int = 1) -> List[Dict[str, Any]]:
        """
        消费消息（便捷方法）

        Args:
            queue: 队列名称
            timeout: 超时时间（秒）
            max_messages: 最多消费多少条消息

        Returns:
            消息列表
        """
        return self.query({
            'type': 'consume',
            'queue': queue,
            'timeout': timeout,
            'max_messages': max_messages
        })
