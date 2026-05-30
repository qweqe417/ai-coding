"""
快照和差异数据模型
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import yaml


@dataclass
class Difference:
    """差异项"""
    step: str
    field: str
    expected: Any
    actual: Any
    rule: str
    reason: Optional[str] = None


@dataclass
class DiffResult:
    """差异报告"""
    test_case_id: str
    test_type: str  # backend | frontend
    status: str  # PASS | FAIL
    differences: List[Difference]
    total_checks: int
    failed_checks: int
    passed_checks: int

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiffResult':
        """从字典创建"""
        differences = [Difference(**d) for d in data.get('differences', [])]

        return cls(
            test_case_id=data['test_case_id'],
            test_type=data.get('test_type', 'backend'),
            status=data['status'],
            differences=differences,
            total_checks=data['total_checks'],
            failed_checks=data['failed_checks'],
            passed_checks=data.get('passed_checks', data['total_checks'] - data['failed_checks'])
        )


@dataclass
class Snapshot:
    """数据快照"""
    test_case_id: str
    timestamp: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Snapshot':
        """从字典创建"""
        return cls(
            test_case_id=data['test_case_id'],
            timestamp=data['timestamp'],
            data=data['data']
        )


class SnapshotLoader:
    """快照加载器"""

    @staticmethod
    def load_from_file(file_path: str) -> Snapshot:
        """从文件加载快照"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return Snapshot.from_dict(data)

    @staticmethod
    def save_to_file(snapshot: Snapshot, file_path: str):
        """保存快照到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(snapshot.to_dict(), f, allow_unicode=True, default_flow_style=False, sort_keys=False)


class DiffResultLoader:
    """差异报告加载器"""

    @staticmethod
    def load_from_file(file_path: str) -> DiffResult:
        """从文件加载差异报告"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return DiffResult.from_dict(data)

    @staticmethod
    def save_to_file(diff_result: DiffResult, file_path: str):
        """保存差异报告到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(diff_result.to_dict(), f, allow_unicode=True, default_flow_style=False, sort_keys=False)
