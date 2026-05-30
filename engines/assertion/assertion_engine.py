"""
断言引擎

整合快照引擎和差异引擎，完成完整的验证流程
"""

from typing import Dict, Any, Optional, Union
import logging

from models import BackendCollectionPlan, FrontendCollectionPlan, DiffResult
from ..snapshot import SnapshotEngine, SnapshotStorage
from ..diff import DiffEngine


class AssertionEngine:
    """断言引擎"""

    def __init__(
        self,
        middleware_configs: Dict[str, Dict[str, Any]],
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化断言引擎

        Args:
            middleware_configs: 中间件配置字典
            logger: 日志实例
        """
        self.middleware_configs = middleware_configs
        self.logger = logger or logging.getLogger(__name__)
        self.snapshot_engine = SnapshotEngine(middleware_configs, logger)
        self.diff_engine = DiffEngine(logger)

    def verify(
        self,
        plan: Union[BackendCollectionPlan, FrontendCollectionPlan],
        api_response: Dict[str, Any],
        output_dir: str
    ) -> DiffResult:
        """
        执行完整的验证流程

        Args:
            plan: 数据采集计划 (后端或前端)
            api_response: API响应
            output_dir: 输出目录

        Returns:
            差异报告
        """
        # Handle FrontendCollectionPlan by delegating to backend sub-plans
        if isinstance(plan, FrontendCollectionPlan):
            return self._verify_frontend(plan, api_response, output_dir)

        self.logger.info(f"Starting verification for test case: {plan.test_case_id}")

        # 1. 采集实际数据
        actual_result = self.snapshot_engine.collect(plan, api_response)

        # 2. 保存快照
        SnapshotStorage.save(plan.test_case_id, actual_result, output_dir)

        # 3. 提取所有验证规则
        all_validations = []
        for step in plan.collection_steps:
            all_validations.extend(step.validations)

        # 4. 对比预期和实际
        diff_result = self.diff_engine.compare(
            test_case_id=plan.test_case_id,
            test_type='backend',
            expected=plan.expected_result,
            actual=actual_result,
            validations=all_validations
        )

        # 5. 保存差异报告
        from models import DiffResultLoader
        diff_file = f"{output_dir}/diff-{plan.test_case_id}.yaml"
        DiffResultLoader.save_to_file(diff_result, diff_file)

        self.logger.info(f"Verification completed for test case: {plan.test_case_id}")
        return diff_result

    def _verify_frontend(
        self,
        plan: FrontendCollectionPlan,
        api_response: Dict[str, Any],
        output_dir: str
    ) -> DiffResult:
        """
        执行前端验证流程

        将前端验证配置中的后端验证子计划委托给后端验证流程
        """
        self.logger.info(f"Starting frontend verification for test case: {plan.test_case_id}")

        all_diffs = []
        total_checks = 0
        failed_checks = 0

        for validation in plan.validations:
            if validation.backend_validation:
                # 委托后端验证
                sub_result = self.verify(
                    validation.backend_validation,
                    api_response,
                    output_dir
                )
                all_diffs.append(sub_result)
                total_checks += sub_result.total_checks
                failed_checks += sub_result.failed_checks
            else:
                # 前端特有验证 (page_redirect, dom_element 等)
                self.logger.info(f"Skipping frontend-specific validation type: {validation.type}")

        # 合并结果
        if all_diffs:
            merged = all_diffs[0]
            merged.total_checks = total_checks
            merged.failed_checks = failed_checks
            merged.passed_checks = total_checks - failed_checks
            merged.status = 'PASS' if failed_checks == 0 else 'FAIL'
            return merged
        else:
            return DiffResult(
                test_case_id=plan.test_case_id,
                test_type='frontend',
                status='PASS',
                total_checks=0,
                passed_checks=0,
                failed_checks=0,
                differences=[]
            )

    def close(self):
        """关闭资源"""
        self.snapshot_engine.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
