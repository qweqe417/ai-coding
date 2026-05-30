"""
引擎模块

包含断言引擎、差异引擎、快照引擎、测试执行器、服务适配器和报告生成器
"""

from .assertion import AssertionEngine
from .diff import DiffEngine
from .snapshot import SnapshotEngine, SnapshotStorage
from .executor import BackendTestExecutor, FrontendTestExecutor
from .collector import ReportGenerator
from .service import (
    ServiceAdapter,
    ServiceError,
    ServiceStartError,
    ServiceStopError,
    JavaServiceAdapter,
    PythonServiceAdapter,
    FrontendServiceAdapter,
    GoServiceAdapter,
    NodejsServiceAdapter,
)

__all__ = [
    'AssertionEngine',
    'DiffEngine',
    'SnapshotEngine',
    'SnapshotStorage',
    'BackendTestExecutor',
    'FrontendTestExecutor',
    'ReportGenerator',
    'ServiceAdapter',
    'ServiceError',
    'ServiceStartError',
    'ServiceStopError',
    'JavaServiceAdapter',
    'PythonServiceAdapter',
    'FrontendServiceAdapter',
    'GoServiceAdapter',
    'NodejsServiceAdapter',
]
