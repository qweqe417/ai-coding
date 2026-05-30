"""
快照引擎

负责根据数据采集计划采集真实数据
"""

from typing import Dict, Any, Optional, List
import logging
import re
from datetime import datetime

from models import CollectionStep, BackendCollectionPlan
from adapters import (
    MySQLAdapter,
    RedisAdapter,
    MongoDBAdapter,
    RabbitMQAdapter,
    KafkaAdapter,
    ElasticsearchAdapter
)


class SnapshotEngine:
    """快照引擎"""

    def __init__(self, middleware_configs: Dict[str, Dict[str, Any]], logger: Optional[logging.Logger] = None):
        """
        初始化快照引擎

        Args:
            middleware_configs: 中间件配置字典
                {
                    "mysql": {...},
                    "redis": {...},
                    ...
                }
            logger: 日志实例
        """
        self.middleware_configs = middleware_configs
        self.logger = logger or logging.getLogger(__name__)
        self.adapters = {}
        self.placeholders = {}  # 存储占位符的值

    def collect(self, plan: BackendCollectionPlan, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据采集计划采集数据

        Args:
            plan: 数据采集计划
            api_response: API响应（用于占位符替换）

        Returns:
            采集结果
        """
        self.logger.info(f"Starting data collection for test case: {plan.test_case_id}")

        # 初始化占位符上下文
        self.placeholders = {
            'response': api_response
        }

        result = {}

        # 按步骤采集数据
        for step in plan.collection_steps:
            self.logger.info(f"Executing step {step.step}: {step.name}")

            try:
                step_result = self._execute_step(step)
                result[f"step_{step.step}"] = step_result

                # 更新占位符上下文
                self.placeholders[f"step_{step.step}"] = step_result

            except Exception as e:
                self.logger.error(f"Step {step.step} failed: {e}")
                result[f"step_{step.step}"] = {
                    'error': str(e),
                    'status': 'failed'
                }

        self.logger.info(f"Data collection completed for test case: {plan.test_case_id}")
        return result

    def _execute_step(self, step: CollectionStep) -> Dict[str, Any]:
        """执行单个采集步骤"""
        middleware = step.middleware
        query_config = step.query

        # 获取或创建适配器
        adapter = self._get_adapter(middleware)

        # 替换占位符
        query_config_dict = self._replace_placeholders(query_config.__dict__)

        # 执行查询
        data = adapter.query(query_config_dict)

        return {
            'middleware': middleware,
            'query': query_config_dict,
            'data': data,
            'status': 'success'
        }

    def _get_adapter(self, middleware: str):
        """获取或创建中间件适配器"""
        if middleware in self.adapters:
            return self.adapters[middleware]

        # 创建新适配器
        config = self.middleware_configs.get(middleware)
        if not config:
            raise ValueError(f"No configuration found for middleware: {middleware}")

        if middleware == 'mysql':
            adapter = MySQLAdapter(config, self.logger)
        elif middleware == 'redis':
            adapter = RedisAdapter(config, self.logger)
        elif middleware == 'mongodb':
            adapter = MongoDBAdapter(config, self.logger)
        elif middleware == 'rabbitmq':
            adapter = RabbitMQAdapter(config, self.logger)
        elif middleware == 'kafka':
            adapter = KafkaAdapter(config, self.logger)
        elif middleware == 'elasticsearch':
            adapter = ElasticsearchAdapter(config, self.logger)
        else:
            raise ValueError(f"Unsupported middleware: {middleware}")

        # 连接
        adapter.connect()
        self.adapters[middleware] = adapter

        return adapter

    def _replace_placeholders(self, obj: Any) -> Any:
        """
        递归替换占位符

        支持的占位符格式：
        - {response.data.id}
        - {step_1.data.user_id}
        """
        if isinstance(obj, str):
            # 查找所有占位符
            pattern = r'\{([^}]+)\}'
            matches = re.findall(pattern, obj)

            for match in matches:
                value = self._get_placeholder_value(match)
                if value is not None:
                    obj = obj.replace(f"{{{match}}}", str(value))

            return obj

        elif isinstance(obj, dict):
            return {k: self._replace_placeholders(v) for k, v in obj.items()}

        elif isinstance(obj, list):
            return [self._replace_placeholders(item) for item in obj]

        else:
            return obj

    def _get_placeholder_value(self, path: str) -> Any:
        """
        获取占位符的值

        Args:
            path: 占位符路径，如 "response.data.id"

        Returns:
            占位符的值
        """
        parts = path.split('.')
        value = self.placeholders

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                self.logger.warning(f"Placeholder not found: {path}")
                return None

        return value

    def close(self):
        """关闭所有适配器连接"""
        for middleware, adapter in self.adapters.items():
            try:
                adapter.disconnect()
                self.logger.info(f"Disconnected from {middleware}")
            except Exception as e:
                self.logger.error(f"Failed to disconnect from {middleware}: {e}")

        self.adapters.clear()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
