---
name: full-test-pipeline
description: "Execute complete test pipeline from test case generation to reporting with optional auto-fix"
---

# full-test-pipeline - Full Test Pipeline

One-command execution of the complete test workflow.

## What This Does

Automates the entire test pipeline:
- Generates test cases (optional)
- Generates data collection plans
- Starts test environment
- Executes tests
- Analyzes failures
- Auto-fixes issues (optional)
- Generates reports

## Prerequisites

- [ ] `.ai-coding/config.yaml` exists (run `/ai-coding:init` first)
- [ ] Middleware services are running (MySQL, Redis, etc.)

## How To Execute

**IMPORTANT:** You MUST execute the Python script using the Bash tool.

```bash
# Find plugin installation path
PLUGIN_PATH=$(find ~/.claude/plugins/cache -path "*/ai-coding-marketplace/ai-coding/*" -name "skills" -type d | head -1 | xargs dirname)

# If not found in cache, try local
if [ -z "$PLUGIN_PATH" ]; then
    PLUGIN_PATH=$(find ~/.claude/plugins/local -name "ai-coding" -type d | head -1)
fi

# If still not found, report error
if [ -z "$PLUGIN_PATH" ]; then
    echo "❌ Error: ai-coding plugin not found"
    exit 1
fi

# Execute the full-test-pipeline script
python "$PLUGIN_PATH/skills/full-test-pipeline/run.py"
```

## Arguments

No arguments required. The script executes all test cases in the pipeline.

## Execution Modes

**Quick Mode (default):**
- Generate plans → Execute tests → Generate reports
- Fast, suitable for CI/CD

**Standard Mode:**
- Generate plans → Execute tests → Analyze failures → Generate reports
- Includes AI analysis

**Full Mode:**
- Generate plans → Execute tests → Analyze failures → Auto-fix → Re-test → Generate reports
- Complete automation with fixes

## Workflow

```
1. Load test cases
   ↓
2. Generate data collection plans (AI)
   ↓
3. Start service
   ↓
4. Execute tests
   ↓
5. Analyze failures (AI)
   ↓
6. Auto-fix (optional, AI)
   ↓
7. Re-test (if fixed)
   ↓
8. Generate reports
   ↓
9. Stop service
```

## Output

Complete test artifacts:
- Test cases: `.ai-coding/testcases/`
- Collection plans: `.ai-coding/plans/`
- Test results: `.ai-coding/results/`
- Analysis: `.ai-coding/analysis/`
- Fixes: `.ai-coding/fixes/`
- Reports: `.ai-coding/reports/`

## After Execution

**If all tests pass:**
✅ All tests passed! Pipeline completed successfully.

**If tests fail (without auto-fix):**
⚠️ Some tests failed. Review analysis reports.

**Next steps:**
- Review failure analysis in `.ai-coding/analysis/`
- Run `/ai-coding:auto-fixer {test_case_id}` to fix issues
- Or re-run with auto-fix enabled

**If tests fail (with auto-fix):**
🔧 Fixes applied. Re-testing...

**Result:**
- ✅ All tests passed after fixes
- Or ❌ Some tests still failing (manual intervention needed)

## Configuration

Edit `.ai-coding/config.yaml` to configure:

```yaml
full_test_pipeline:
  default_mode: standard
  auto_fix: false
  auto_fix_threshold: 0.9
  stop_on_failure: false
  generate_html_report: true
```

## Error Handling

**Error: Service failed to start**
- Check service configuration
- Check if port is available
- Review service logs

**Error: Middleware connection failed**
- Ensure middleware services are running
- Check connection settings in config

**Error: Test execution failed**
- Review test logs in `.ai-coding/logs/`
- Check API endpoints
- Verify test data
