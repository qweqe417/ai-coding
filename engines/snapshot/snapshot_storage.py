"""
快照存储

负责保存和加载快照数据
"""

from typing import Dict, Any
import yaml
import os
from datetime import datetime


class SnapshotStorage:
    """快照存储"""

    @staticmethod
    def save(test_case_id: str, data: Dict[str, Any], output_dir: str):
        """
        保存快照

        Args:
            test_case_id: 测试用例ID
            data: 快照数据
            output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)

        snapshot = {
            'test_case_id': test_case_id,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }

        file_path = os.path.join(output_dir, f"actual-result-{test_case_id}.yaml")

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(snapshot, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    @staticmethod
    def load(test_case_id: str, input_dir: str) -> Dict[str, Any]:
        """
        加载快照

        Args:
            test_case_id: 测试用例ID
            input_dir: 输入目录

        Returns:
            快照数据
        """
        file_path = os.path.join(input_dir, f"actual-result-{test_case_id}.yaml")

        with open(file_path, 'r', encoding='utf-8') as f:
            snapshot = yaml.safe_load(f)

        return snapshot
