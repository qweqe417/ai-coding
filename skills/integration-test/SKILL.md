---
name: integration-test
description: "Execute integration tests with automatic service startup, API calls, data collection, and validation"
---

# integration-test - Integration Test Executor

Execute complete integration test workflow.

## What This Does

- Starts the service automatically
- Executes test cases
- Collects and validates data from middleware
- Generates test reports
- Stops the service

## Prerequisites

- [ ] `.ai-coding/config.yaml` exists (run `/ai-coding:init` first)
- [ ] Test cases exist (run `/ai-coding:testcase-generator` first)
- [ ] Data collection plans exist (run `/ai-coding:assertion-generator` first)
- [ ] Middleware services are running (MySQL, Redis, etc.)

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

# Execute the integration-test script
# Optional: specify test case IDs (space-separated)
python "$PLUGIN_PATH/skills/integration-test/run.py" "$@"
```

## Arguments

- `test_case_ids` (optional): Space-separated test case IDs
  - If provided: executes only specified test cases
  - If omitted: executes all test cases

Examples:
```bash
# Execute all test cases
python "$PLUGIN_PATH/skills/integration-test/run.py"

# Execute specific test case
python "$PLUGIN_PATH/skills/integration-test/run.py" TC001

# Execute multiple test cases
python "$PLUGIN_PATH/skills/integration-test/run.py" TC001 TC002 TC003
```

## Workflow

1. Load configuration and test cases
2. Start service (if not already running)
3. Health check
4. Execute test cases:
   - Call API
   - Verify HTTP response
   - Collect data from middleware
   - Compare with expected results
5. Generate test reports
6. Stop service

## Output

Generated files:
- `.ai-coding/results/actual-result-{test_case_id}.yaml` - Actual data snapshot
- `.ai-coding/results/diff-{test_case_id}.yaml` - Diff report
- `.ai-coding/results/test-summary.json` - Test summary
- `.ai-coding/reports/test-report.html` - HTML report
- `.ai-coding/reports/test-report.md` - Markdown report
- `.ai-coding/reports/test-report.json` - JSON report

## After Execution

**If all tests pass:**
✅ All tests passed!

**Next steps:**
- Review test reports in `.ai-coding/reports/`
- Run `/ai-coding:report-generator` for detailed analysis

**If tests fail:**
❌ Some tests failed.

**Next steps:**
- Review diff reports in `.ai-coding/results/diff-*.yaml`
- Run `/ai-coding:diff-analyzer <test_case_id>` to analyze failures
- Run `/ai-coding:auto-fixer <test_case_id>` to attempt automatic fixes

## Configuration

Edit `.ai-coding/config.yaml` to configure:

```yaml
service:
  type: springboot
  start_command: mvn spring-boot:run
  health_check_url: http://localhost:8080/actuator/health
  base_url: http://localhost:8080
  startup_timeout: 60

middleware:
  mysql:
    enabled: true
    host: localhost
    port: 3306
    user: root
    password: password
    database: test_db

test:
  strategy: backend
  target_pass_rate: 0.95
```

## Error Handling

**Error: Service failed to start**
- Check if port is already in use
- Check service startup command in config
- Check service logs

**Error: Middleware connection failed**
- Ensure middleware services are running
- Check connection settings in config
- Test connection manually

**Error: Test case not found**
- Check if test cases exist in `.ai-coding/testcases/`
- Check if data collection plans exist in `.ai-coding/plans/`

**Error: API call failed**
- Check service health
- Check API endpoint URL
- Check request parameters

## Advanced Usage

**Execute specific test cases:**
```bash
python "$PLUGIN_PATH/skills/integration-test/run.py" TC001 TC002
```

**Skip service management (service already running):**
- Edit the script or config to skip service start/stop
- Useful for debugging or when service is managed externally