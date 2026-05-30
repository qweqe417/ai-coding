---
name: auto-fixer
description: "Automatically fix code issues based on root cause analysis with confidence-based strategies"
---

# auto-fixer - Auto Fixer

AI-powered automatic code fixing based on root cause analysis.

## What This Does

Automatically fixes code based on analysis:
- Reads root cause analysis reports
- Evaluates fix confidence
- Locates problem code
- Generates fix solutions
- Applies fixes (high confidence) or creates fix plans (low confidence)
- Re-runs tests for verification

## Prerequisites

- [ ] Root cause analysis exists (run `/ai-coding:diff-analyzer {test_case_id}` first)
- [ ] Analysis report in `.ai-coding/analysis/root-cause-{test_case_id}.yaml`

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

# Execute the auto-fixer script
# Required: test_case_id
if [ -z "$1" ]; then
    echo "❌ Error: test_case_id is required"
    echo "Usage: /ai-coding:auto-fixer <test_case_id>"
    exit 1
fi

python "$PLUGIN_PATH/ai-coding/skills/auto-fixer/run.py" "$1"
```

## Arguments

- `test_case_id` (required): Test case ID to fix

Example:
```bash
python "$PLUGIN_PATH/ai-coding/skills/auto-fixer/run.py" TC001
```

## Fix Strategies

**High Confidence (≥0.9):** Auto-fix without confirmation
**Medium Confidence (0.7-0.9):** Generate fix plan, wait for confirmation
**Low Confidence (<0.7):** Generate suggestions only

## Output

Generates `.ai-coding/fixes/fix-plan-{test_case_id}.yaml` containing:
- Fix status
- Changes made
- Verification results
- Before/after code

## After Execution

**If fix succeeded:**
✅ Fix applied and verified!

**Next steps:**
- Review changes in the source files
- Run `/ai-coding:integration-test` for full regression test

**If fix failed:**
❌ Fix could not be applied automatically.

**Next steps:**
- Review fix plan in `.ai-coding/fixes/fix-plan-{test_case_id}.yaml`
- Apply fixes manually

## Safety Features

- Automatic backup before fixing
- Rollback if verification fails
- Manual review for low confidence fixes

## Error Handling

**Error: Root cause analysis not found**
- Run `/ai-coding:diff-analyzer {test_case_id}` first

**Error: Cannot modify source file**
- Check file permissions
- Ensure file is not locked