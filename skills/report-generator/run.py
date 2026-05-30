#!/usr/bin/env python3
"""
report-generator - 测试报告生成器

生成完整的测试报告
"""

import sys
import os
import yaml
import json
from pathlib import Path
from datetime import datetime


def main():
    """主函数"""
    print("=" * 60)
    print("report-generator - 测试报告生成器")
    print("=" * 60)

    # 检查是否在Claude Code环境中
    if not os.getenv('CLAUDE_CODE'):
        print("\n⚠️  警告: 当前不在Claude Code环境中")
        print("   使用占位实现，实际使用时需要在Claude Code中运行")
        print()

    # 获取参数
    output_format = 'html'
    for i, arg in enumerate(sys.argv):
        if arg == '--format' and i + 1 < len(sys.argv):
            output_format = sys.argv[i + 1]

    print(f"\n📊 生成 {output_format.upper()} 格式报告")

    # 收集测试结果
    print("\n[1/7] 收集测试结果...")
    results_dir = Path('.ai-coding/results')
    test_results = collect_test_results(results_dir)
    print(f"   ✓ 找到 {len(test_results)} 个测试结果")

    # 收集差异分析
    print("[2/7] 收集差异分析...")
    analysis_dir = Path('.ai-coding/analysis')
    analyses = collect_analyses(analysis_dir)
    print(f"   ✓ 找到 {len(analyses)} 个差异分析")

    # 收集修复记录
    print("[3/7] 收集修复记录...")
    fixes_dir = Path('.ai-coding/fixes')
    fixes = collect_fixes(fixes_dir)
    print(f"   ✓ 找到 {len(fixes)} 个修复记录")

    # 统计数据
    print("[4/7] 统计数据...")
    stats = calculate_statistics(test_results, analyses, fixes)
    print(f"   ✓ 通过率: {stats['pass_rate']}%")

    # 生成图表数据
    print("[5/7] 生成图表数据...")
    charts = generate_chart_data(test_results)
    print(f"   ✓ 生成 {len(charts)} 个图表")

    # 生成报告
    print(f"[6/7] 生成 {output_format.upper()} 报告...")
    report_content = generate_report(output_format, stats, test_results, analyses, fixes, charts)
    print(f"   ✓ 报告大小: {len(report_content)} 字符")

    # 保存报告
    print("[7/7] 保存报告...")
    output_dir = Path('.ai-coding/reports')
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'report-{timestamp}.{output_format}'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"\n✅ 报告已生成")
    print(f"   文件: {output_file}")
    print(f"   大小: {len(report_content)} 字节")

    if output_format == 'html':
        print(f"\n🌐 在浏览器中打开:")
        print(f"   file:///{output_file.absolute()}")

    print("\n💡 下一步:")
    print("   1. 查看测试报告")
    print("   2. 分析失败原因")
    print("   3. 修复失败的测试用例")

    return 0


def collect_test_results(results_dir):
    """收集测试结果"""
    if not results_dir.exists():
        return []

    results = []
    for file in results_dir.glob('diff-*.yaml'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                result = yaml.safe_load(f)
                results.append(result)
        except Exception as e:
            print(f"   ⚠️  无法读取 {file}: {e}")

    return results


def collect_analyses(analysis_dir):
    """收集差异分析"""
    if not analysis_dir.exists():
        return []

    analyses = []
    for file in analysis_dir.glob('root-cause-*.yaml'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                analysis = yaml.safe_load(f)
                analyses.append(analysis)
        except Exception as e:
            print(f"   ⚠️  无法读取 {file}: {e}")

    return analyses


def collect_fixes(fixes_dir):
    """收集修复记录"""
    if not fixes_dir.exists():
        return []

    fixes = []
    for file in fixes_dir.glob('fix-plan-*.yaml'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                fix = yaml.safe_load(f)
                fixes.append(fix)
        except Exception as e:
            print(f"   ⚠️  无法读取 {file}: {e}")

    return fixes


def calculate_statistics(test_results, analyses, fixes):
    """计算统计数据"""
    total = len(test_results)
    passed = sum(1 for r in test_results if r.get('status') == 'PASS')
    failed = total - passed
    pass_rate = round(passed / total * 100) if total > 0 else 0

    # 统计差异类型
    bug_types = {}
    for analysis in analyses:
        category = analysis.get('category', 'Unknown')
        bug_types[category] = bug_types.get(category, 0) + 1

    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'pass_rate': pass_rate,
        'bug_types': bug_types,
        'fixes_applied': len(fixes)
    }


def generate_chart_data(test_results):
    """生成图表数据"""
    return {
        'pass_rate_trend': [40, 50, 60, 70, 80],
        'test_distribution': {'passed': 8, 'failed': 2},
        'bug_types': {'Real Bug': 2, 'Assertion': 0, 'Environment': 0, 'Timing': 0}
    }


def generate_report(output_format, stats, test_results, analyses, fixes, charts):
    """生成报告"""
    if output_format == 'html':
        return generate_html_report(stats, test_results, analyses, fixes, charts)
    elif output_format == 'markdown':
        return generate_markdown_report(stats, test_results, analyses, fixes)
    elif output_format == 'json':
        return generate_json_report(stats, test_results, analyses, fixes)
    else:
        return generate_markdown_report(stats, test_results, analyses, fixes)


def generate_html_report(stats, test_results, analyses, fixes, charts):
    """生成HTML报告"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>集成测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .stat {{ display: inline-block; margin: 10px 20px; }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>集成测试报告</h1>

    <div class="summary">
        <h2>执行摘要</h2>
        <div class="stat">总用例数: <strong>{stats['total']}</strong></div>
        <div class="stat pass">通过: {stats['passed']} ({stats['pass_rate']}%)</div>
        <div class="stat fail">失败: {stats['failed']}</div>
        <div class="stat">修复: {stats['fixes_applied']}</div>
    </div>

    <h2>测试用例详情</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>状态</th>
            <th>通过检查</th>
            <th>失败检查</th>
        </tr>
        {''.join(f'''
        <tr>
            <td>{r.get('test_case_id', 'N/A')}</td>
            <td class="{'pass' if r.get('status') == 'PASS' else 'fail'}">{r.get('status', 'N/A')}</td>
            <td>{r.get('passed_checks', 0)}</td>
            <td>{r.get('failed_checks', 0)}</td>
        </tr>
        ''' for r in test_results)}
    </table>

    <h2>差异分析汇总</h2>
    <ul>
        {''.join(f'<li>{k}: {v} 个</li>' for k, v in stats['bug_types'].items())}
    </ul>

    <p><em>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
</body>
</html>"""


def generate_markdown_report(stats, test_results, analyses, fixes):
    """生成Markdown报告"""
    return f"""# 集成测试报告

## 执行摘要

- **总用例数**: {stats['total']}
- **通过**: {stats['passed']} ({stats['pass_rate']}%)
- **失败**: {stats['failed']}
- **修复**: {stats['fixes_applied']}

## 测试用例详情

| ID | 状态 | 通过检查 | 失败检查 |
|----|------|----------|----------|
{''.join(f"| {r.get('test_case_id', 'N/A')} | {'✅' if r.get('status') == 'PASS' else '❌'} {r.get('status', 'N/A')} | {r.get('passed_checks', 0)} | {r.get('failed_checks', 0)} |\n" for r in test_results)}

## 差异分析汇总

{''.join(f"- **{k}**: {v} 个\n" for k, v in stats['bug_types'].items())}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""


def generate_json_report(stats, test_results, analyses, fixes):
    """生成JSON报告"""
    report = {
        'summary': stats,
        'test_results': test_results,
        'analyses': analyses,
        'fixes': fixes,
        'generated_at': datetime.now().isoformat()
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(main())
