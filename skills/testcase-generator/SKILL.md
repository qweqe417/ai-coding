---
name: testcase-generator
description: "Generate test cases from API specification documents using AI analysis"
---

# testcase-generator - Test Case Generator

AI-powered test case generation from specification documents.

## What This Does

- Parses API definitions from spec documents
- Generates normal flow test cases
- Generates boundary value test cases
- Generates error flow test cases
- Generates idempotent test cases

## Prerequisites

- [ ] `.ai-coding/config.yaml` exists (run `/ai-coding:init` first)
- [ ] Spec documents exist in `.ai-coding/specs/` or `docs/`

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

# Execute the testcase-generator script
python "$PLUGIN_PATH/skills/testcase-generator/run.py"
```

## Arguments

No arguments required. The script will:
1. Search for spec documents in `.ai-coding/specs/` and `docs/`
2. Prompt you to select which spec to process
3. Generate test cases automatically

## Output

Generates `.ai-coding/testcases/testcases.json` containing:
- Normal flow test cases
- Boundary value test cases
- Error flow test cases
- Idempotent test cases (if applicable)

## After Execution

✅ Test cases generated successfully!

**Next steps:**
- Review the generated test cases in `.ai-coding/testcases/testcases.json`
- Manually add any special scenario test cases
- Run `/ai-coding:assertion-generator` to generate data collection plans

## Test Case Types

**Normal Flow:**
- Valid input parameters
- Expected success responses

**Boundary Values:**
- Minimum/maximum values
- Empty/null values
- Special characters

**Error Flow:**
- Missing required parameters
- Invalid parameter types
- Invalid parameter formats
- Business rule violations

**Idempotent:**
- Repeated identical requests
- Verify result consistency

## Configuration

Edit `.ai-coding/config.yaml` to configure:

```yaml
testcase_generator:
  model: claude-sonnet-4
  normal_cases: 1
  boundary_cases: 2
  error_cases: 3
  generate_idempotent: true
  data_strategy: realistic
```

## Error Handling

**Error: No spec documents found**
- Create spec documents in `.ai-coding/specs/` or `docs/`
- Ensure spec documents contain API definitions

**Error: AI analysis failed**
- Check if the spec document format is correct
- Ensure API definitions are clear and complete

**Error: Cannot write test cases**
- Check if `.ai-coding/testcases/` directory exists
- Check file permissions
