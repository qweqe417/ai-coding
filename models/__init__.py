"""
数据模型模块
"""

from .testcase import (
    BackendTestCase,
    FrontendTestCase,
    TestCaseLoader,
    APIConfig,
    HTTPResponse,
    PageConfig,
    Action,
    APICall,
    Element,
    FrontendExpected
)

from .assertion import (
    BackendCollectionPlan,
    FrontendCollectionPlan,
    CollectionPlanLoader,
    CollectionStep,
    QueryConfig,
    Validation
)

from .snapshot import (
    Snapshot,
    DiffResult,
    Difference,
    SnapshotLoader,
    DiffResultLoader
)

from .report import (
    RootCauseAnalysis,
    FixRecord,
    TestSummary,
    TestReport,
    TestCaseResult,
    ProblemLocation,
    ReportLoader
)

__all__ = [
    # Testcase
    'BackendTestCase',
    'FrontendTestCase',
    'TestCaseLoader',
    'APIConfig',
    'HTTPResponse',
    'PageConfig',
    'Action',
    'APICall',
    'Element',
    'FrontendExpected',
    # Assertion
    'BackendCollectionPlan',
    'FrontendCollectionPlan',
    'CollectionPlanLoader',
    'CollectionStep',
    'QueryConfig',
    'Validation',
    # Snapshot
    'Snapshot',
    'DiffResult',
    'Difference',
    'SnapshotLoader',
    'DiffResultLoader',
    # Report
    'RootCauseAnalysis',
    'FixRecord',
    'TestSummary',
    'TestReport',
    'TestCaseResult',
    'ProblemLocation',
    'ReportLoader'
]
