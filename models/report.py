"""
报告数据模型
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json
import yaml


@dataclass
class ProblemLocation:
    """问题位置"""
    file: str
    method: Optional[str] = None
    line: Optional[int] = None
    code_snippet: Optional[str] = None


@dataclass
class RootCauseAnalysis:
    """根因分析"""
    test_case_id: str
    test_type: str  # backend | frontend
    root_cause_type: str  # CODE_BUG | CONFIG_ERROR | TIMING_ISSUE | TEST_CASE_ERROR
    confidence: float
    description: str
    problem_location: ProblemLocation
    suggested_fix: str
    fix_confidence: str  # HIGH | MEDIUM | LOW
    auto_fixable: bool

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RootCauseAnalysis':
        """从字典创建"""
        location = ProblemLocation(**data['problem_location'])

        return cls(
            test_case_id=data['test_case_id'],
            test_type=data.get('test_type', 'backend'),
            root_cause_type=data['root_cause_type'],
            confidence=data['confidence'],
            description=data['description'],
            problem_location=location,
            suggested_fix=data['suggested_fix'],
            fix_confidence=data['fix_confidence'],
            auto_fixable=data['auto_fixable']
        )


@dataclass
class FixRecord:
    """修复记录"""
    test_case_id: str
    root_cause_analysis: RootCauseAnalysis
    fixed_files: List[str]
    fix_diff: str
    fix_timestamp: str
    regression_passed: bool

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FixRecord':
        """从字典创建"""
        root_cause = RootCauseAnalysis.from_dict(data['root_cause_analysis'])

        return cls(
            test_case_id=data['test_case_id'],
            root_cause_analysis=root_cause,
            fixed_files=data['fixed_files'],
            fix_diff=data['fix_diff'],
            fix_timestamp=data['fix_timestamp'],
            regression_passed=data['regression_passed']
        )


@dataclass
class TestCaseResult:
    """测试用例结果"""
    test_case_id: str
    name: str
    status: str  # PASS | FAIL | SKIP
    duration: float  # 执行时间（秒）
    error_message: Optional[str] = None


@dataclass
class TestSummary:
    """测试汇总"""
    total: int
    passed: int
    failed: int
    skipped: int
    pass_rate: float
    duration: float  # 总执行时间（秒）
    test_results: List[TestCaseResult]
    fixed_count: int = 0
    regression_passed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestSummary':
        """从字典创建"""
        results = [TestCaseResult(**r) for r in data.get('test_results', [])]

        return cls(
            total=data['total'],
            passed=data['passed'],
            failed=data['failed'],
            skipped=data['skipped'],
            pass_rate=data['pass_rate'],
            duration=data['duration'],
            test_results=results,
            fixed_count=data.get('fixed_count', 0),
            regression_passed=data.get('regression_passed', 0)
        )


@dataclass
class TestReport:
    """测试报告"""
    project_name: str
    test_date: str
    summary: TestSummary
    fix_records: List[FixRecord]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestReport':
        """从字典创建"""
        summary = TestSummary.from_dict(data['summary'])
        fix_records = [FixRecord.from_dict(f) for f in data.get('fix_records', [])]

        return cls(
            project_name=data['project_name'],
            test_date=data['test_date'],
            summary=summary,
            fix_records=fix_records,
            recommendations=data.get('recommendations', [])
        )


class ReportLoader:
    """报告加载器"""

    @staticmethod
    def load_root_cause_from_file(file_path: str) -> RootCauseAnalysis:
        """从文件加载根因分析"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return RootCauseAnalysis.from_dict(data)

    @staticmethod
    def save_root_cause_to_file(root_cause: RootCauseAnalysis, file_path: str):
        """保存根因分析到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(root_cause.to_dict(), f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    @staticmethod
    def load_fix_record_from_file(file_path: str) -> FixRecord:
        """从文件加载修复记录"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return FixRecord.from_dict(data)

    @staticmethod
    def save_fix_record_to_file(fix_record: FixRecord, file_path: str):
        """保存修复记录到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(fix_record.to_dict(), f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    @staticmethod
    def load_summary_from_file(file_path: str) -> TestSummary:
        """从文件加载测试汇总"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return TestSummary.from_dict(data)

    @staticmethod
    def save_summary_to_file(summary: TestSummary, file_path: str):
        """保存测试汇总到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(summary.to_dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_report_from_file(file_path: str) -> TestReport:
        """从文件加载测试报告"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return TestReport.from_dict(data)

    @staticmethod
    def save_report_to_file(report: TestReport, file_path: str):
        """保存测试报告到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
