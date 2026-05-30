"""
数据采集计划数据模型
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import yaml


@dataclass
class QueryConfig:
    """查询配置"""
    type: str  # select, get, find_one, consume, search
    sql: Optional[str] = None  # MySQL SQL
    key: Optional[str] = None  # Redis key
    collection: Optional[str] = None  # MongoDB collection
    query: Optional[Dict[str, Any]] = None  # MongoDB/ES query
    queue: Optional[str] = None  # RabbitMQ/Kafka queue
    timeout: Optional[int] = None  # 超时时间（秒）


@dataclass
class Validation:
    """验证规则"""
    field: str
    rule: str  # equals, not_null, contains, greater_than, less_than, regex
    value: Optional[Any] = None
    source: Optional[str] = None  # request.xxx, response.xxx
    reason: Optional[str] = None


@dataclass
class CollectionStep:
    """数据采集步骤"""
    step: int
    name: str
    middleware: str  # mysql, redis, mongodb, rabbitmq, kafka, elasticsearch
    timing: str  # before_api, after_api
    query: QueryConfig
    validations: List[Validation]


@dataclass
class BackendCollectionPlan:
    """后端数据采集计划"""
    test_case_id: str
    api: str
    collection_steps: List[CollectionStep]
    expected_result: Dict[str, Any]
    expected_summary: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackendCollectionPlan':
        """从字典创建"""
        steps = []
        for step_data in data.get('collection_steps', []):
            query = QueryConfig(**step_data['query'])
            validations = [Validation(**v) for v in step_data.get('validations', [])]
            steps.append(CollectionStep(
                step=step_data['step'],
                name=step_data['name'],
                middleware=step_data['middleware'],
                timing=step_data['timing'],
                query=query,
                validations=validations
            ))

        return cls(
            test_case_id=data['test_case_id'],
            api=data['api'],
            collection_steps=steps,
            expected_result=data['expected_result'],
            expected_summary=data.get('expected_summary')
        )


@dataclass
class ValidationConfig:
    """前端验证配置"""
    type: str  # page_redirect, api_call, dom_element, storage
    config: Dict[str, Any]
    backend_validation: Optional[BackendCollectionPlan] = None


@dataclass
class FrontendCollectionPlan:
    """前端数据采集计划"""
    test_case_id: str
    page_url: str
    validations: List[ValidationConfig]
    expected_result: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrontendCollectionPlan':
        """从字典创建"""
        validations = []
        for val_data in data.get('validations', []):
            backend_val = None
            if val_data.get('backend_validation'):
                backend_val = BackendCollectionPlan.from_dict(val_data['backend_validation'])

            validations.append(ValidationConfig(
                type=val_data['type'],
                config=val_data['config'],
                backend_validation=backend_val
            ))

        return cls(
            test_case_id=data['test_case_id'],
            page_url=data['page_url'],
            validations=validations,
            expected_result=data['expected_result']
        )


class CollectionPlanLoader:
    """数据采集计划加载器"""

    @staticmethod
    def load_from_file(file_path: str) -> Any:
        """从文件加载数据采集计划"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # 根据是否有page_url判断是前端还是后端
        if 'page_url' in data:
            return FrontendCollectionPlan.from_dict(data)
        else:
            return BackendCollectionPlan.from_dict(data)

    @staticmethod
    def save_to_file(plan: Any, file_path: str):
        """保存数据采集计划到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(plan.to_dict(), f, allow_unicode=True, default_flow_style=False, sort_keys=False)
