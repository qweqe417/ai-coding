"""
报告生成器

负责生成Markdown、HTML、JSON格式的测试报告
"""

from typing import Dict, Any, Optional
import logging
import json
from datetime import datetime
from jinja2 import Template

from models import TestReport, TestSummary, FixRecord


class ReportGenerator:
    """报告生成器"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化报告生成器

        Args:
            logger: 日志实例
        """
        self.logger = logger or logging.getLogger(__name__)

    def generate(
        self,
        project_name: str,
        summary: TestSummary,
        fix_records: list = None,
        recommendations: list = None,
        output_dir: str = "."
    ) -> TestReport:
        """
        生成测试报告

        Args:
            project_name: 项目名称
            summary: 测试汇总
            fix_records: 修复记录列表
            recommendations: 建议列表
            output_dir: 输出目录

        Returns:
            测试报告对象
        """
        self.logger.info("Generating test report...")

        # 创建报告对象
        report = TestReport(
            project_name=project_name,
            test_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=summary,
            fix_records=fix_records or [],
            recommendations=recommendations or []
        )

        # 生成各种格式的报告
        self._generate_json(report, output_dir)
        self._generate_markdown(report, output_dir)
        self._generate_html(report, output_dir)

        self.logger.info(f"Test report generated in {output_dir}")
        return report

    def _generate_json(self, report: TestReport, output_dir: str):
        """生成JSON格式报告"""
        file_path = f"{output_dir}/test-report.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        self.logger.info(f"JSON report saved: {file_path}")

    def _generate_markdown(self, report: TestReport, output_dir: str):
        """生成Markdown格式报告"""
        template = """# 测试报告

**项目名称**: {{ project_name }}
**测试日期**: {{ test_date }}

---

## 📊 测试汇总

| 指标 | 数值 |
|------|------|
| 总用例数 | {{ summary.total }} |
| 通过数 | {{ summary.passed }} ✅ |
| 失败数 | {{ summary.failed }} ❌ |
| 跳过数 | {{ summary.skipped }} ⏭️ |
| **通过率** | **{{ "%.2f"|format(summary.pass_rate * 100) }}%** |
| 执行时间 | {{ "%.2f"|format(summary.duration) }}s |
{% if summary.fixed_count > 0 %}| 自动修复数 | {{ summary.fixed_count }} 🔧 |
| 回归通过数 | {{ summary.regression_passed }} ✅ |{% endif %}

---

## 📋 测试用例详情

| ID | 名称 | 状态 | 耗时 | 错误信息 |
|----|------|------|------|----------|
{% for result in summary.test_results -%}
| {{ result.test_case_id }} | {{ result.name }} | {{ result.status }} | {{ "%.2f"|format(result.duration) }}s | {{ result.error_message or '-' }} |
{% endfor %}

---
{% if fix_records %}
## 🔧 自动修复记录

{% for fix in fix_records %}
### {{ fix.test_case_id }}

**根因类型**: {{ fix.root_cause_analysis.root_cause_type }}
**置信度**: {{ "%.2f"|format(fix.root_cause_analysis.confidence * 100) }}%
**问题描述**: {{ fix.root_cause_analysis.description }}

**问题位置**:
- 文件: `{{ fix.root_cause_analysis.problem_location.file }}`
{% if fix.root_cause_analysis.problem_location.method %}- 方法: `{{ fix.root_cause_analysis.problem_location.method }}`{% endif %}
{% if fix.root_cause_analysis.problem_location.line %}- 行号: {{ fix.root_cause_analysis.problem_location.line }}{% endif %}

**修复方案**: {{ fix.root_cause_analysis.suggested_fix }}

**修复文件**:
{% for file in fix.fixed_files -%}
- `{{ file }}`
{% endfor %}

**回归测试**: {{ "通过 ✅" if fix.regression_passed else "失败 ❌" }}

---
{% endfor %}
{% endif %}

{% if recommendations %}
## 💡 改进建议

{% for rec in recommendations -%}
{{ loop.index }}. {{ rec }}
{% endfor %}
{% endif %}

---

**报告生成时间**: {{ test_date }}
**生成工具**: AI Coding Integration Test Framework
"""

        t = Template(template)
        content = t.render(
            project_name=report.project_name,
            test_date=report.test_date,
            summary=report.summary,
            fix_records=report.fix_records,
            recommendations=report.recommendations
        )

        file_path = f"{output_dir}/test-report.md"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.logger.info(f"Markdown report saved: {file_path}")

    def _generate_html(self, report: TestReport, output_dir: str):
        """生成HTML格式报告"""
        template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - {{ project_name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 40px; }
        h1 { color: #333; margin-bottom: 10px; }
        .meta { color: #666; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .summary-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }
        .summary-card.success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
        .summary-card.fail { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }
        .summary-card h3 { font-size: 14px; margin-bottom: 10px; opacity: 0.9; }
        .summary-card .value { font-size: 32px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 40px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; color: #333; }
        .status-pass { color: #38ef7d; font-weight: bold; }
        .status-fail { color: #f45c43; font-weight: bold; }
        .status-skip { color: #ffa502; font-weight: bold; }
        .fix-record { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .fix-record h3 { color: #333; margin-bottom: 10px; }
        .fix-record .label { display: inline-block; background: #667eea; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; margin-right: 10px; }
        .recommendations { background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 4px; }
        .recommendations li { margin-bottom: 10px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: "Courier New", monospace; }
        .footer { text-align: center; color: #999; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 测试报告</h1>
        <div class="meta">
            <strong>项目名称:</strong> {{ project_name }} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>测试日期:</strong> {{ test_date }}
        </div>

        <h2>📊 测试汇总</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>总用例数</h3>
                <div class="value">{{ summary.total }}</div>
            </div>
            <div class="summary-card success">
                <h3>通过数</h3>
                <div class="value">{{ summary.passed }}</div>
            </div>
            <div class="summary-card fail">
                <h3>失败数</h3>
                <div class="value">{{ summary.failed }}</div>
            </div>
            <div class="summary-card">
                <h3>通过率</h3>
                <div class="value">{{ "%.1f"|format(summary.pass_rate * 100) }}%</div>
            </div>
        </div>

        <h2>📋 测试用例详情</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>状态</th>
                    <th>耗时</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>
                {% for result in summary.test_results %}
                <tr>
                    <td>{{ result.test_case_id }}</td>
                    <td>{{ result.name }}</td>
                    <td class="status-{{ result.status.lower() }}">{{ result.status }}</td>
                    <td>{{ "%.2f"|format(result.duration) }}s</td>
                    <td>{{ result.error_message or '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        {% if fix_records %}
        <h2>🔧 自动修复记录</h2>
        {% for fix in fix_records %}
        <div class="fix-record">
            <h3>{{ fix.test_case_id }}</h3>
            <p>
                <span class="label">{{ fix.root_cause_analysis.root_cause_type }}</span>
                <span class="label">置信度: {{ "%.0f"|format(fix.root_cause_analysis.confidence * 100) }}%</span>
            </p>
            <p><strong>问题描述:</strong> {{ fix.root_cause_analysis.description }}</p>
            <p><strong>问题位置:</strong> <code>{{ fix.root_cause_analysis.problem_location.file }}</code></p>
            <p><strong>修复方案:</strong> {{ fix.root_cause_analysis.suggested_fix }}</p>
            <p><strong>回归测试:</strong> {{ "通过 ✅" if fix.regression_passed else "失败 ❌" }}</p>
        </div>
        {% endfor %}
        {% endif %}

        {% if recommendations %}
        <h2>💡 改进建议</h2>
        <div class="recommendations">
            <ul>
                {% for rec in recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        <div class="footer">
            报告生成时间: {{ test_date }}<br>
            生成工具: AI Coding Integration Test Framework
        </div>
    </div>
</body>
</html>
"""

        t = Template(template)
        content = t.render(
            project_name=report.project_name,
            test_date=report.test_date,
            summary=report.summary,
            fix_records=report.fix_records,
            recommendations=report.recommendations
        )

        file_path = f"{output_dir}/test-report.html"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.logger.info(f"HTML report saved: {file_path}")
