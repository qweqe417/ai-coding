"""
测试用例数据模型
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class APIConfig:
    """API配置"""
    method: str  # GET, POST, PUT, DELETE
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None


@dataclass
class HTTPResponse:
    """HTTP响应"""
    status_code: int
    body: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None


@dataclass
class BackendTestCase:
    """后端测试用例"""
    id: str
    name: str
    test_type: str = "backend"
    api: Optional[APIConfig] = None
    expected_http: Optional[HTTPResponse] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackendTestCase':
        """从字典创建"""
        api_data = data.get('api')
        api = APIConfig(**api_data) if api_data else None

        expected_http_data = data.get('expected_http')
        expected_http = HTTPResponse(**expected_http_data) if expected_http_data else None

        return cls(
            id=data['id'],
            name=data['name'],
            test_type=data.get('test_type', 'backend'),
            api=api,
            expected_http=expected_http,
            description=data.get('description')
        )


@dataclass
class Action:
    """用户操作"""
    type: str  # fill, click, wait
    selector: str
    value: Optional[str] = None


@dataclass
class PageConfig:
    """页面配置"""
    url: str
    actions: List[Action]


@dataclass
class APICall:
    """API调用"""
    url: str
    method: str
    request_body: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None


@dataclass
class Element:
    """DOM元素"""
    selector: str
    should_exist: bool = True


@dataclass
class FrontendExpected:
    """前端预期结果"""
    page_redirect: Optional[str] = None
    api_calls: Optional[List[APICall]] = None
    dom_elements: Optional[List[Element]] = None
    local_storage: Optional[Dict[str, Any]] = None


@dataclass
class FrontendTestCase:
    """前端测试用例"""
    id: str
    name: str
    test_type: str = "frontend"
    page: Optional[PageConfig] = None
    expected: Optional[FrontendExpected] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrontendTestCase':
        """从字典创建"""
        page_data = data.get('page')
        page = None
        if page_data:
            actions = [Action(**a) for a in page_data.get('actions', [])]
            page = PageConfig(url=page_data['url'], actions=actions)

        expected_data = data.get('expected')
        expected = None
        if expected_data:
            api_calls = [APICall(**a) for a in expected_data.get('api_calls', [])]
            dom_elements = [Element(**e) for e in expected_data.get('dom_elements', [])]
            expected = FrontendExpected(
                page_redirect=expected_data.get('page_redirect'),
                api_calls=api_calls,
                dom_elements=dom_elements,
                local_storage=expected_data.get('local_storage')
            )

        return cls(
            id=data['id'],
            name=data['name'],
            test_type=data.get('test_type', 'frontend'),
            page=page,
            expected=expected,
            description=data.get('description')
        )


class TestCaseLoader:
    """测试用例加载器"""

    @staticmethod
    def load_from_file(file_path: str) -> List[Any]:
        """从文件加载测试用例"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        testcases = []
        for item in data.get('testcases', []):
            test_type = item.get('test_type', 'backend')
            if test_type == 'backend':
                testcases.append(BackendTestCase.from_dict(item))
            elif test_type == 'frontend':
                testcases.append(FrontendTestCase.from_dict(item))

        return testcases

    @staticmethod
    def save_to_file(testcases: List[Any], file_path: str):
        """保存测试用例到文件"""
        data = {
            'testcases': [tc.to_dict() for tc in testcases]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
