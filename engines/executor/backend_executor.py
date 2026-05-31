"""
后端测试执行器

负责执行后端API测试的完整流程
"""

from typing import Dict, Any, List, Optional
import json
import logging
import requests
import time

from models import BackendTestCase, BackendCollectionPlan, TestSummary, TestCaseResult, CollectionPlanLoader
from engines.service import ServiceAdapter
from engines.assertion import AssertionEngine


class BackendTestExecutor:
    """后端测试执行器"""

    def __init__(
        self,
        service_adapter: ServiceAdapter,
        middleware_configs: Dict[str, Dict[str, Any]],
        base_url: str,
        logger: Optional[logging.Logger] = None,
        auth_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化后端测试执行器

        Args:
            service_adapter: 服务启动适配器
            middleware_configs: 中间件配置
            base_url: 服务基础URL
            logger: 日志实例
            auth_config: 认证配置
        """
        self.service_adapter = service_adapter
        self.middleware_configs = middleware_configs
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)
        self.auth_config = auth_config or {}
        self.assertion_engine = AssertionEngine(middleware_configs, logger)

    def run(
        self,
        testcases: List[BackendTestCase],
        plans_dir: str,
        results_dir: str
    ) -> TestSummary:
        """
        执行测试

        Args:
            testcases: 测试用例列表
            plans_dir: 数据采集计划目录
            results_dir: 结果输出目录

        Returns:
            测试汇总
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting backend integration test")
        self.logger.info("=" * 60)

        start_time = time.time()
        test_results = []

        # 启动服务
        self.logger.info("Starting service...")
        self.service_adapter.start()

        if not self.service_adapter.health_check():
            self.logger.error("Service failed to start")
            return self._create_summary(test_results, time.time() - start_time)

        try:
            # 执行每个测试用例
            for testcase in testcases:
                self.logger.info(f"\n{'=' * 60}")
                self.logger.info(f"Executing test case: {testcase.id} - {testcase.name}")
                self.logger.info(f"{'=' * 60}")

                result = self._execute_testcase(testcase, plans_dir, results_dir)
                test_results.append(result)

        finally:
            # 停止服务
            self.logger.info("\nStopping service...")
            self.service_adapter.stop()

            # 关闭断言引擎
            self.assertion_engine.close()

        duration = time.time() - start_time
        summary = self._create_summary(test_results, duration)

        self.logger.info("\n" + "=" * 60)
        self.logger.info("Test Summary")
        self.logger.info("=" * 60)
        self.logger.info(f"Total: {summary.total}")
        self.logger.info(f"Passed: {summary.passed}")
        self.logger.info(f"Failed: {summary.failed}")
        self.logger.info(f"Pass Rate: {summary.pass_rate:.2%}")
        self.logger.info(f"Duration: {summary.duration:.2f}s")
        self.logger.info("=" * 60)

        return summary

    def _execute_testcase(
        self,
        testcase: BackendTestCase,
        plans_dir: str,
        results_dir: str
    ) -> TestCaseResult:
        """执行单个测试用例"""
        start_time = time.time()

        try:
            # 1. 调用API
            self.logger.info(f"Calling API: {testcase.api.method} {testcase.api.url}")
            response = self._call_api(testcase)

            # 2. 验证HTTP响应
            if testcase.expected_http:
                if response.status_code != testcase.expected_http.status_code:
                    error_msg = f"HTTP status code mismatch: expected {testcase.expected_http.status_code}, got {response.status_code}"
                    self.logger.error(error_msg)
                    return TestCaseResult(
                        test_case_id=testcase.id,
                        name=testcase.name,
                        status='FAIL',
                        duration=time.time() - start_time,
                        error_message=error_msg
                    )

            # 3. 加载数据采集计划
            plan_file = f"{plans_dir}/data-collection-plan-{testcase.id}.yaml"
            plan = CollectionPlanLoader.load_from_file(plan_file)

            # 4. 执行数据验证
            try:
                api_response = response.json() if response.text else {}
            except (json.JSONDecodeError, ValueError):
                self.logger.warning(f"Response is not valid JSON, using empty dict")
                api_response = {}
            diff_result = self.assertion_engine.verify(plan, api_response, results_dir)

            # 5. 判断结果
            if diff_result.status == 'PASS':
                self.logger.info(f"✅ Test case {testcase.id} PASSED")
                return TestCaseResult(
                    test_case_id=testcase.id,
                    name=testcase.name,
                    status='PASS',
                    duration=time.time() - start_time
                )
            else:
                self.logger.error(f"❌ Test case {testcase.id} FAILED")
                self.logger.error(f"Failed checks: {diff_result.failed_checks}/{diff_result.total_checks}")
                return TestCaseResult(
                    test_case_id=testcase.id,
                    name=testcase.name,
                    status='FAIL',
                    duration=time.time() - start_time,
                    error_message=f"{diff_result.failed_checks} validation(s) failed"
                )

        except Exception as e:
            self.logger.error(f"❌ Test case {testcase.id} FAILED with exception: {e}")
            return TestCaseResult(
                test_case_id=testcase.id,
                name=testcase.name,
                status='FAIL',
                duration=time.time() - start_time,
                error_message=str(e)
            )

    def _call_api(self, testcase: BackendTestCase) -> requests.Response:
        """调用API"""
        url = f"{self.base_url}{testcase.api.url}"
        method = testcase.api.method.upper()

        kwargs = {}

        # 设置请求头
        headers = testcase.api.headers.copy() if testcase.api.headers else {}

        # 添加认证信息
        if self.auth_config.get('enabled', False):
            auth_type = self.auth_config.get('type', 'token')

            if auth_type == 'token':
                # Token 认证
                token = self.auth_config.get('token')
                header_name = self.auth_config.get('header_name', 'Authorization')
                header_prefix = self.auth_config.get('header_prefix', 'Bearer')

                if token:
                    if header_prefix:
                        headers[header_name] = f"{header_prefix} {token}"
                    else:
                        headers[header_name] = token
                    self.logger.debug(f"Added token to header: {header_name}")

            elif auth_type == 'basic':
                # Basic Auth
                username = self.auth_config.get('username')
                password = self.auth_config.get('password')
                if username and password:
                    from requests.auth import HTTPBasicAuth
                    kwargs['auth'] = HTTPBasicAuth(username, password)
                    self.logger.debug("Added Basic Auth")

        if headers:
            kwargs['headers'] = headers
        if testcase.api.body:
            kwargs['json'] = testcase.api.body
        if testcase.api.params:
            kwargs['params'] = testcase.api.params

        response = requests.request(method, url, **kwargs)
        self.logger.info(f"Response: {response.status_code}")

        return response

    def _create_summary(self, test_results: List[TestCaseResult], duration: float) -> TestSummary:
        """创建测试汇总"""
        total = len(test_results)
        passed = sum(1 for r in test_results if r.status == 'PASS')
        failed = sum(1 for r in test_results if r.status == 'FAIL')
        skipped = sum(1 for r in test_results if r.status == 'SKIP')
        pass_rate = passed / total if total > 0 else 0.0

        return TestSummary(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            pass_rate=pass_rate,
            duration=duration,
            test_results=test_results
        )

    def run_regression(
        self,
        failed_testcases: List[BackendTestCase],
        plans_dir: str,
        results_dir: str
    ) -> TestSummary:
        """
        执行回归测试

        Args:
            failed_testcases: 失败的测试用例列表
            plans_dir: 数据采集计划目录
            results_dir: 结果输出目录

        Returns:
            测试汇总
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Starting regression test")
        self.logger.info("=" * 60)

        # 重启服务
        self.logger.info("Restarting service...")
        self.service_adapter.stop()
        time.sleep(2)
        self.service_adapter.start()

        if not self.service_adapter.health_check():
            self.logger.error("Service failed to start")
            return TestSummary(
                total=len(failed_testcases),
                passed=0,
                failed=len(failed_testcases),
                skipped=0,
                pass_rate=0.0,
                duration=0.0,
                test_results=[]
            )

        # 执行测试
        return self.run(failed_testcases, plans_dir, results_dir)
