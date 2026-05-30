---
name: report-generator
description: "Generate comprehensive test reports in HTML, Markdown, and JSON formats with charts and trend analysis"
---

# report-generator - Report Generator

Generate comprehensive test reports in multiple formats.

## What This Does

Generates complete test reports:
- Test results summary
- Test case details
- Data change records
- Diff analysis results
- Fix records
- Trend analysis
- Coverage statistics

## Prerequisites

- [ ] Tests have been executed (run `/ai-coding:integration-test` first)
- [ ] Test results exist in `.ai-coding/results/`

## How To Execute

**IMPORTANT:** You MUST execute the Python script using the Bash tool.

```bash
# Find plugin installation path
PLUGIN_PATH=$(find ~/.claude/plugins/cache -name "ai-coding" -type d | grep -E "ai-coding/[0-9]" | head -1)

# If not found in cache, try local
if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

# If still not found, report error
if [ -z "$PLUGIN_PATH" ]; then
    echo "❌ Error: ai-coding plugin not found"
    exit 1
fi

# Execute the report-generator script
python "$PLUGIN_PATH/ai-coding/skills/report-generator/run.py"
```

## Arguments

No arguments required. The script will generate reports for the latest test execution.

## Output Formats

Generates three report formats:
- `.ai-coding/reports/test-report.html` - Interactive HTML report with charts
- `.ai-coding/reports/test-report.md` - Markdown report for documentation
- `.ai-coding/reports/test-report.json` - JSON report for programmatic access

## Report Contents

1. **Execution Summary** - Pass rate, duration, timestamp
2. **Test Case Details** - Status, duration, API calls, data changes
3. **Data Change Statistics** - MySQL, Redis, MongoDB, etc.
4. **Diff Analysis Summary** - Categorized failures
5. **Fix Records** - Applied fixes and verification results
6. **Trend Analysis** - Historical pass rate trends
7. **Coverage Statistics** - API, database, middleware coverage

## After Execution

✅ Reports generated successfully!

**Generated files:**
- HTML: `.ai-coding/reports/test-report.html`
- Markdown: `.ai-coding/reports/test-report.md`
- JSON: `.ai-coding/reports/test-report.json`

**Next steps:**
- Open HTML report in browser for interactive view
- Share Markdown report in documentation
- Use JSON report for CI/CD integration

## Error Handling

**Error: No test results found**
- Run `/ai-coding:integration-test` first
- Check if `.ai-coding/results/` directory exists

**Error: Cannot generate charts**
- Charts require test history data
- Run tests multiple times to build history