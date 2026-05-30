"""
Kafka适配器

支持消费消息，支持超时控制
"""

from typing import Dict, Any, Optional, List
import logging

try:
    from kafka import KafkaConsumer
except ImportError:
    KafkaConsumer = None

from ..base import MiddlewareAdapter, ConnectionError, QueryError, TimeoutError


class KafkaAdapter(MiddlewareAdapter):
    """Kafka适配器"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化Kafka适配器

        Args:
            config: Kafka配置
                {
                    "bootstrap_servers": ["localhost:9092"],
                    "group_id": "test_group",
                    "auto_offset_reset": "earliest"
                }
        """
        super().__init__(config, logger)

        if KafkaConsumer is None:
            raise ImportError("kafka-python is not installed. Run: pip install kafka-python")

        self.consumer = None

    def connect(self):
        """连接到Kafka"""
        try:
            bootstrap_servers = self.config.get('bootstrap_servers', ['localhost:9092'])
            group_id = self.config.get('group_id', 'ai-coding-test')
            auto_offset_reset = self.config.get('auto_offset_reset', 'earliest')

            self.consumer = KafkaConsumer(
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                value_deserializer=lambda m: m.decode('utf-8')
            )

            self.connected = True
            self.logger.info(f"Connected to Kafka: {bootstrap_servers}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Kafka: {e}")
            raise ConnectionError(f"Failed to connect to Kafka: {e}")

    def disconnect(self):
        """断开连接"""
        if self.consumer:
            self.consumer.close()
            self.connected = False
            self.logger.info("Disconnected from Kafka")

    def query(self, query_config: Dict[str, Any]) -> Any:
        """
        执行查询（消费消息）

        Args:
            query_config: 查询配置
                {
                    "type": "consume",
                    "topic": "test_topic",
                    "timeout": 10000,  # 超时时间（毫秒）
                    "max_messages": 1  # 最多消费多少条消息
                }

        Returns:
            消息列表 List[Dict]
        """
        if not self.connected:
            raise ConnectionError("Not connected to Kafka")

        query_type = query_config.get('type', 'consume')
        topic = query_config['topic']
        timeout_ms = query_config.get('timeout', 10000)
        max_messages = query_config.get('max_messages', 1)

        try:
            if query_type == 'consume':
                return self._consume_messages(topic, timeout_ms, max_messages)
            else:
                raise QueryError(f"Unsupported query type: {query_type}")

        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise QueryError(f"Query failed: {e}")

    def _consume_messages(self, topic: str, timeout_ms: int, max_messages: int) -> List[Dict[str, Any]]:
        """消费消息"""
        self.logger.debug(f"Consuming messages from topic: {topic} (timeout={timeout_ms}ms, max={max_messages})")

        # 订阅主题
        self.consumer.subscribe([topic])

        messages = []

        try:
            # 拉取消息
            records = self.consumer.poll(timeout_ms=timeout_ms, max_records=max_messages)

            for topic_partition, records_list in records.items():
                for record in records_list:
                    message = {
                        'topic': record.topic,
                        'partition': record.partition,
                        'offset': record.offset,
                        'key': record.key,
                        'value': record.value,
                        'timestamp': record.timestamp
                    }
                    messages.append(message)
                    self.logger.debug(f"Consumed message: {message}")

            if not messages:
                self.logger.warning(f"No messages consumed from {topic} within {timeout_ms}ms")
                raise TimeoutError(f"No messages consumed from {topic} within {timeout_ms}ms")

            self.logger.debug(f"Consumed {len(messages)} messages from {topic}")
            return messages

        except Exception as e:
            if isinstance(e, TimeoutError):
                raise
            self.logger.error(f"Failed to consume messages: {e}")
            raise QueryError(f"Failed to consume messages: {e}")

    def consume(self, topic: str, timeout_ms: int = 10000, max_messages: int = 1) -> List[Dict[str, Any]]:
        """
        消费消息（便捷方法）

        Args:
            topic: 主题名称
            timeout_ms: 超时时间（毫秒）
            max_messages: 最多消费多少条消息

        Returns:
            消息列表
        """
        return self.query({
            'type': 'consume',
            'topic': topic,
            'timeout': timeout_ms,
            'max_messages': max_messages
        })
