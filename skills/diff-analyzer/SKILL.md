---
name: diff-analyzer
description: "Analyze test failures using AI to identify root causes and categorize issues (Real Bug, Timing, Environment, Assertion)"
---

# diff-analyzer - Diff Analyzer

AI-powered test failure analysis to identify root causes.

## What This Does

When tests fail, AI automatically analyzes:
- Reads diff reports
- Analyzes code logic
- Reviews log information
- Identifies root causes
- Categorizes diff types
- Generates fix suggestions

## Prerequisites

- [ ] Test has been executed (run `/ai-coding:integration-test` first)
- [ ] Diff report exists in `.ai-coding/results/diff-{test_case_id}.yaml`

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

# Execute the diff-analyzer script
# Required: test_case_id
if [ -z "$1" ]; then
    echo "❌ Error: test_case_id is required"
    echo "Usage: /ai-coding:diff-analyzer <test_case_id>"
    exit 1
fi

python "$PLUGIN_PATH/ai-coding/skills/diff-analyzer/run.py" "$1"
```

## Arguments

- `test_case_id` (required): Test case ID to analyze

Example:
```bash
python "$PLUGIN_PATH/ai-coding/skills/diff-analyzer/run.py" TC001
```

## Diff Categories

**1. Real Bug** - Actual code defects
**2. Timing Problem** - Async operations, cache delays
**3. Environment Problem** - Config issues, data state
**4. Assertion Problem** - Incorrect validation rules

## Output

Generates `.ai-coding/analysis/root-cause-{test_case_id}.yaml` containing:
- Category and confidence level
- Root cause description
- Code location
- Evidence
- Fix suggestions

## After Execution

✅ Root cause analysis completed!

**Next steps:**
- Review the analysis in `.ai-coding/analysis/root-cause-{test_case_id}.yaml`
- Run `/ai-coding:auto-fixer {test_case_id}` to attempt automatic fix

## Error Handling

**Error: Diff report not found**
- Run `/ai-coding:integration-test {test_case_id}` first
- Check if test actually failed

**Error: Cannot access source code**
- Ensure project source code is accessible
- Check file permissions