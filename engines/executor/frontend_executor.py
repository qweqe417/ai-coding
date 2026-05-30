"""
前端测试执行器

使用Playwright进行浏览器自动化，执行前端UI测试
支持页面操作、API调用捕获、DOM验证等功能
"""

from typing import Dict, Any, List, Optional
import logging
import time
import json
import os

from models import (
    FrontendTestCase, FrontendCollectionPlan,
    TestSummary, TestCaseResult, CollectionPlanLoader,
    PageConfig, Action, FrontendExpected, APICall, Element
)
from engines.service import ServiceAdapter
from engines.assertion import AssertionEngine


class FrontendTestExecutor:
    """前端测试执行器"""

    def __init__(
        self,
        service_adapter: ServiceAdapter,
        middleware_configs: Dict[str, Dict[str, Any]],
        base_url: str,
        test_config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化前端测试执行器

        Args:
            service_adapter: 前端服务启动适配器
            middleware_configs: 中间件配置
            base_url: 前端服务URL
            test_config: 前端测试配置（browser, headless, viewport, timeout等）
            logger: 日志实例
        """
        self.service_adapter = service_adapter
        self.middleware_configs = middleware_configs
        self.base_url = base_url
        self.test_config = test_config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.assertion_engine = AssertionEngine(middleware_configs, logger)

        # 浏览器配置
        self.browser_type = self.test_config.get('browser', 'chromium')
        self.headless = self.test_config.get('headless', True)
        self.viewport = self.test_config.get('viewport', '1920x1080')
        self.timeout_ms = self.test_config.get('timeout', 30000)

        # 解析viewport
        if isinstance(self.viewport, str) and 'x' in self.viewport:
            w, h = self.viewport.split('x')
            self.viewport = {'width': int(w), 'height': int(h)}
        elif isinstance(self.viewport, str):
            self.viewport = {'width': 1920, 'height': 1080}

        self._browser = None
        self._playwright = None

    def run(
        self,
        testcases: List[FrontendTestCase],
        plans_dir: str,
        results_dir: str
    ) -> TestSummary:
        """
        执行前端测试

        Args:
            testcases: 前端测试用例列表
            plans_dir: 数据采集计划目录
            results_dir: 结果输出目录

        Returns:
            测试汇总
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting frontend integration test")
        self.logger.info("=" * 60)

        start_time = time.time()
        test_results = []

        # 启动前端服务
        self.logger.info("Starting frontend service...")
        self.service_adapter.start()

        if not self.service_adapter.health_check():
            self.logger.warning("Frontend service health check failed, continuing anyway...")

        try:
            # 初始化浏览器
            self.logger.info("Launching browser...")
            self._launch_browser()

            # 执行每个测试用例
            for testcase in testcases:
                self.logger.info(f"\n{'=' * 60}")
                self.logger.info(f"Executing test case: {testcase.id} - {testcase.name}")
                self.logger.info(f"{'=' * 60}")

                result = self._execute_testcase(testcase, plans_dir, results_dir)
                test_results.append(result)

        finally:
            # 关闭浏览器
            if self._browser:
                self.logger.info("Closing browser...")
                self._browser.close()

            if self._playwright:
                self._playwright.stop()

            # 停止前端服务
            self.logger.info("Stopping frontend service...")
            self.service_adapter.stop()

            # 关闭断言引擎
            self.assertion_engine.close()

        duration = time.time() - start_time
        summary = self._create_summary(test_results, duration)

        self.logger.info("\n" + "=" * 60)
        self.logger.info("Frontend Test Summary")
        self.logger.info("=" * 60)
        self.logger.info(f"Total: {summary.total}")
        self.logger.info(f"Passed: {summary.passed}")
        self.logger.info(f"Failed: {summary.failed}")
        self.logger.info(f"Pass Rate: {summary.pass_rate:.2%}")
        self.logger.info(f"Duration: {summary.duration:.2f}s")
        self.logger.info("=" * 60)

        return summary

    def _launch_browser(self):
        """启动浏览器"""
        try:
            from playwright.sync_api import sync_playwright

            self._playwright = sync_playwright().start()

            if self.browser_type == 'chromium':
                browser_launcher = self._playwright.chromium
            elif self.browser_type == 'firefox':
                browser_launcher = self._playwright.firefox
            elif self.browser_type == 'webkit':
                browser_launcher = self._playwright.webkit
            else:
                self.logger.warning(f"Unknown browser type '{self.browser_type}', falling back to chromium")
                browser_launcher = self._playwright.chromium

            self._browser = browser_launcher.launch(
                headless=self.headless
            )

            self.logger.info(f"Browser '{self.browser_type}' launched successfully")
        except ImportError:
            self.logger.error("playwright not installed. Please run: pip install playwright && playwright install")
            raise
        except Exception as e:
            self.logger.error(f"Failed to launch browser: {e}")
            raise

    def _execute_testcase(
        self,
        testcase: FrontendTestCase,
        plans_dir: str,
        results_dir: str
    ) -> TestCaseResult:
        """执行单个前端测试用例"""
        start_time = time.time()

        try:
            if not testcase.page:
                return TestCaseResult(
                    test_case_id=testcase.id,
                    name=testcase.name,
                    status='FAIL',
                    duration=time.time() - start_time,
                    error_message="No page configuration found"
                )

            # 创建页面上下文
            context = self._browser.new_context(
                viewport=self.viewport
            )
            page = context.new_page()

            # 收集API调用
            captured_api_calls: List[Dict[str, Any]] = []

            def on_request(request):
                if request.resource_type in ('xhr', 'fetch'):
                    captured_api_calls.append({
                        'url': request.url,
                        'method': request.method,
                        'headers': dict(request.headers),
                    })
                    # 尝试获取请求体
                    try:
                        post_data = request.post_data
                        if post_data:
                            try:
                                body = json.loads(post_data)
                            except json.JSONDecodeError:
                                body = post_data
                            captured_api_calls[-1]['request_body'] = body
                    except Exception:
                        pass

            def on_response(response):
                # 找到对应的请求并添加响应信息
                for call in captured_api_calls:
                    if call.get('url') == response.url and 'response_status' not in call:
                        call['response_status'] = response.status
                        try:
                            call['response_body'] = response.json()
                        except Exception:
                            try:
                                call['response_body'] = response.text()
                            except Exception:
                                pass
                        break

            page.on('request', on_request)
            page.on('response', on_response)

            try:
                # 1. 导航到页面
                target_url = self._resolve_url(testcase.page.url)
                self.logger.info(f"Navigating to: {target_url}")
                page.goto(target_url, wait_until='networkidle', timeout=self.timeout_ms)

                # 2. 执行用户操作
                for action in testcase.page.actions:
                    self.logger.info(f"Action: {action.type} -> {action.selector}")
                    self._execute_action(page, action)

                # 等待网络请求完成
                page.wait_for_timeout(1000)  # 额外等待以确保API调用完成

                # 3. 验证预期结果
                if testcase.expected:
                    failures = self._verify_expected(page, testcase.expected, captured_api_calls)

                    if failures:
                        return TestCaseResult(
                            test_case_id=testcase.id,
                            name=testcase.name,
                            status='FAIL' if failures else 'PASS',
                            duration=time.time() - start_time,
                            error_message='; '.join(failures)
                        )

                # 4. 执行数据采集计划（如果有）
                plan_file = f"{plans_dir}/data-collection-plan-{testcase.id}.yaml"
                if os.path.exists(plan_file):
                    self.logger.info(f"Loading collection plan: {plan_file}")
                    plan = CollectionPlanLoader.load_from_file(plan_file)

                    # 构造模拟API响应（从捕获的API调用中提取）
                    api_response = {
                        'captured_api_calls': captured_api_calls,
                        'page_url': page.url,
                        'page_title': page.title(),
                    }
                    diff_result = self.assertion_engine.verify(plan, api_response, results_dir)

                    if diff_result.status == 'FAIL':
                        return TestCaseResult(
                            test_case_id=testcase.id,
                            name=testcase.name,
                            status='FAIL',
                            duration=time.time() - start_time,
                            error_message=f"{diff_result.failed_checks} validation(s) failed"
                        )

                self.logger.info(f"✅ Test case {testcase.id} PASSED")
                return TestCaseResult(
                    test_case_id=testcase.id,
                    name=testcase.name,
                    status='PASS',
                    duration=time.time() - start_time
                )

            finally:
                context.close()

        except Exception as e:
            self.logger.error(f"❌ Test case {testcase.id} FAILED with exception: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return TestCaseResult(
                test_case_id=testcase.id,
                name=testcase.name,
                status='FAIL',
                duration=time.time() - start_time,
                error_message=str(e)
            )

    def _resolve_url(self, url: str) -> str:
        """解析URL"""
        if url.startswith('http://') or url.startswith('https://'):
            return url
        # 相对路径，拼接base_url
        base = self.base_url.rstrip('/')
        url = url.lstrip('/')
        return f"{base}/{url}"

    def _execute_action(self, page, action: Action):
        """执行用户操作"""
        try:
            if action.type == 'click':
                page.click(action.selector, timeout=self.timeout_ms)

            elif action.type == 'fill':
                page.fill(action.selector, action.value or '', timeout=self.timeout_ms)

            elif action.type == 'type':
                # 逐个键入字符（模拟真实输入）
                page.click(action.selector, timeout=self.timeout_ms)
                page.type(action.selector, action.value or '', timeout=self.timeout_ms)

            elif action.type == 'select':
                page.select_option(action.selector, action.value or '', timeout=self.timeout_ms)

            elif action.type == 'check':
                page.check(action.selector, timeout=self.timeout_ms)

            elif action.type == 'uncheck':
                page.uncheck(action.selector, timeout=self.timeout_ms)

            elif action.type == 'hover':
                page.hover(action.selector, timeout=self.timeout_ms)

            elif action.type == 'wait':
                wait_ms = int(action.value) if action.value and action.value.isdigit() else 2000
                page.wait_for_timeout(wait_ms)

            elif action.type == 'wait_for_selector':
                page.wait_for_selector(action.value or action.selector, timeout=self.timeout_ms)

            elif action.type == 'press':
                # 按键，如 Enter
                page.press(action.selector, action.value or 'Enter', timeout=self.timeout_ms)

            elif action.type == 'screenshot':
                # 截图操作
                screenshot_path = action.value or f"screenshot-{time.strftime('%Y%m%d_%H%M%S')}.png"
                page.screenshot(path=screenshot_path)
                self.logger.info(f"Screenshot saved: {screenshot_path}")

            else:
                self.logger.warning(f"Unknown action type: {action.type}")

        except Exception as e:
            self.logger.error(f"Failed to execute action {action.type} on {action.selector}: {e}")
            raise

    def _verify_expected(
        self,
        page,
        expected: FrontendExpected,
        captured_api_calls: List[Dict[str, Any]]
    ) -> List[str]:
        """验证预期结果，返回失败信息列表"""
        failures = []

        # 1. 验证页面跳转
        if expected.page_redirect:
            current_url = page.url
            expected_url = self._resolve_url(expected.page_redirect)
            if current_url != expected_url:
                failures.append(
                    f"Page redirect mismatch: expected '{expected_url}', got '{current_url}'"
                )

        # 2. 验证API调用
        if expected.api_calls:
            for expected_call in expected.api_calls:
                matched = False
                for captured in captured_api_calls:
                    if self._match_api_call(expected_call, captured):
                        matched = True
                        break
                if not matched:
                    failures.append(
                        f"Expected API call not found: {expected_call.method} {expected_call.url}"
                    )

        # 3. 验证DOM元素
        if expected.dom_elements:
            for element in expected.dom_elements:
                try:
                    exists = page.locator(element.selector).count() > 0
                    if element.should_exist and not exists:
                        failures.append(f"Expected element not found: {element.selector}")
                    elif not element.should_exist and exists:
                        failures.append(f"Element should not exist but found: {element.selector}")
                except Exception as e:
                    failures.append(f"Error checking element {element.selector}: {e}")

        # 4. 验证localStorage
        if expected.local_storage:
            for key, expected_value in expected.local_storage.items():
                actual_value = page.evaluate(f"localStorage.getItem('{key}')")
                if actual_value != expected_value:
                    failures.append(
                        f"localStorage mismatch for '{key}': expected '{expected_value}', got '{actual_value}'"
                    )

        return failures

    def _match_api_call(self, expected: APICall, captured: Dict[str, Any]) -> bool:
        """匹配API调用"""
        # 匹配URL和method
        if expected.method.upper() != captured.get('method', '').upper():
            return False

        # URL匹配（支持部分匹配）
        captured_url = captured.get('url', '')
        if expected.url not in captured_url and captured_url not in expected.url:
            return False

        # 匹配请求体（如果指定了）
        if expected.request_body:
            captured_body = captured.get('request_body')
            if isinstance(captured_body, str):
                try:
                    captured_body = json.loads(captured_body)
                except json.JSONDecodeError:
                    pass
            if captured_body != expected.request_body:
                return False

        # 匹配响应状态码（如果指定了）
        if expected.response_status:
            if captured.get('response_status') != expected.response_status:
                return False

        return True

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
        failed_testcases: List[FrontendTestCase],
        plans_dir: str,
        results_dir: str
    ) -> TestSummary:
        """
        执行前端回归测试

        Args:
            failed_testcases: 失败的测试用例列表
            plans_dir: 数据采集计划目录
            results_dir: 结果输出目录

        Returns:
            测试汇总
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Starting frontend regression test")
        self.logger.info("=" * 60)

        # 重启服务
        self.logger.info("Restarting frontend service...")
        self.service_adapter.stop()
        time.sleep(2)
        self.service_adapter.start()

        if not self.service_adapter.health_check():
            self.logger.warning("Frontend service health check failed, continuing...")

        # 执行测试
        return self.run(failed_testcases, plans_dir, results_dir)
