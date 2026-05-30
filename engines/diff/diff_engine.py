"""
差异引擎

负责对比预期结果和实际结果
"""

from typing import Dict, Any, List, Optional
import logging
import re

from models import Validation, DiffResult, Difference


class DiffEngine:
    """差异引擎"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化差异引擎

        Args:
            logger: 日志实例
        """
        self.logger = logger or logging.getLogger(__name__)

    def compare(
        self,
        test_case_id: str,
        test_type: str,
        expected: Dict[str, Any],
        actual: Dict[str, Any],
        validations: List[Validation]
    ) -> DiffResult:
        """
        对比预期和实际结果

        Args:
            test_case_id: 测试用例ID
            test_type: 测试类型（backend/frontend）
            expected: 预期结果
            actual: 实际结果
            validations: 验证规则列表

        Returns:
            差异报告
        """
        self.logger.info(f"Comparing results for test case: {test_case_id}")

        differences = []
        total_checks = len(validations)
        failed_checks = 0

        for validation in validations:
            try:
                is_valid, reason = self._validate(validation, expected, actual)

                if not is_valid:
                    failed_checks += 1
                    difference = Difference(
                        step=validation.field.split('.')[0] if '.' in validation.field else 'unknown',
                        field=validation.field,
                        expected=validation.value,
                        actual=self._get_value(actual, validation.field),
                        rule=validation.rule,
                        reason=reason
                    )
                    differences.append(difference)
                    self.logger.warning(f"Validation failed: {validation.field} - {reason}")

            except Exception as e:
                failed_checks += 1
                difference = Difference(
                    step='unknown',
                    field=validation.field,
                    expected=validation.value,
                    actual=None,
                    rule=validation.rule,
                    reason=f"Validation error: {str(e)}"
                )
                differences.append(difference)
                self.logger.error(f"Validation error for {validation.field}: {e}")

        status = 'PASS' if failed_checks == 0 else 'FAIL'
        passed_checks = total_checks - failed_checks

        result = DiffResult(
            test_case_id=test_case_id,
            test_type=test_type,
            status=status,
            differences=differences,
            total_checks=total_checks,
            failed_checks=failed_checks,
            passed_checks=passed_checks
        )

        self.logger.info(f"Comparison completed: {status} ({passed_checks}/{total_checks} passed)")
        return result

    def _validate(self, validation: Validation, expected: Dict[str, Any], actual: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        执行单个验证规则

        Args:
            validation: 验证规则
            expected: 预期结果
            actual: 实际结果

        Returns:
            (是否通过, 失败原因)
        """
        field = validation.field
        rule = validation.rule
        expected_value = validation.value

        # 获取实际值
        actual_value = self._get_value(actual, field)

        # 执行验证
        if rule == 'equals':
            if actual_value == expected_value:
                return True, None
            else:
                return False, f"Expected {expected_value}, but got {actual_value}"

        elif rule == 'not_null':
            if actual_value is not None:
                return True, None
            else:
                return False, "Value is null"

        elif rule == 'contains':
            if expected_value in str(actual_value):
                return True, None
            else:
                return False, f"Expected to contain '{expected_value}', but got '{actual_value}'"

        elif rule == 'greater_than':
            if actual_value > expected_value:
                return True, None
            else:
                return False, f"Expected > {expected_value}, but got {actual_value}"

        elif rule == 'less_than':
            if actual_value < expected_value:
                return True, None
            else:
                return False, f"Expected < {expected_value}, but got {actual_value}"

        elif rule == 'regex':
            if re.match(expected_value, str(actual_value)):
                return True, None
            else:
                return False, f"Value '{actual_value}' does not match regex '{expected_value}'"

        elif rule == 'exists':
            if actual_value is not None:
                return True, None
            else:
                return False, "Field does not exist"

        else:
            return False, f"Unsupported validation rule: {rule}"

    def _get_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        从嵌套字典中获取值

        Args:
            data: 数据字典
            path: 路径，如 "step_1.data.user_id"

        Returns:
            值
        """
        parts = path.split('.')
        value = data

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value
