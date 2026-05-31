---
name: assertion-generator
description: "Generate data collection plans by analyzing code and tracking data flow across middleware (MySQL, Redis, MongoDB, etc.)"
---

# assertion-generator - Data Collection Plan Generator

**Core Skill** - AI analyzes code to automatically generate data collection plans.

## What This Does

This is the core skill of the framework. It uses AI to:
- Identify API data flow
- Track data flow across middleware (MySQL, Redis, MongoDB, Kafka, etc.)
- Generate complete data collection plans
- Generate validation rules

## Prerequisites

- [ ] `.ai-coding/config.yaml` exists (run `/ai-coding:init` first)
- [ ] Test cases exist in `.ai-coding/testcases/` (run `/ai-coding:testcase-generator` first)
- [ ] Project source code is accessible

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

# Execute the assertion-generator script
# Optional: specify test_case_id
python "$PLUGIN_PATH/skills/assertion-generator/run.py" "$1"
```

## Arguments

- `test_case_id` (optional): Specific test case ID to generate plan for
  - If provided: generates plan for that test case only
  - If omitted: generates plans for all test cases

## Output

Generates `.ai-coding/plans/data-collection-plan-{test_case_id}.yaml` for each test case.

Each plan contains:
- Collection steps (what data to collect from which middleware)
- Validation rules (what to verify)
- Expected results

## After Execution

✅ Data collection plans generated successfully!

**Next steps:**
- Review the generated plans in `.ai-coding/plans/`
- Manually adjust complex data flows if needed
- Run `/ai-coding:integration-test` to execute tests with the plans

## AI Analysis Strategy

**1. Code Path Tracking**

Traces from Controller → Service → Repository:
- Identifies API entry point
- Follows method calls
- Tracks data transformations

**2. Data Flow Identification**

Detects middleware operations:
- **MySQL**: `save()`, `insert()`, `update()`, `delete()`
- **Redis**: `set()`, `hset()`, `setex()`
- **MongoDB**: `insert()`, `save()`, `updateOne()`
- **RabbitMQ**: `send()`, `publish()`
- **Kafka**: `send()`, `produce()`
- **Elasticsearch**: `index()`, `update()`

**3. Validation Rule Generation**

Creates rules based on code logic:
- Field values are correctly saved
- Data types are correct
- Related data is consistent
- Cache is updated

## Configuration

Edit `.ai-coding/config.yaml` to configure:

```yaml
assertion_generator:
  model: claude-opus-4
  analysis_depth: 3
  include_code_snippets: true
  validation_strategy: comprehensive
```

## Error Handling

**Error: Test case not found**
- Run `/ai-coding:testcase-generator` first
- Check if test case ID exists in `.ai-coding/testcases/testcases.json`

**Error: Cannot access source code**
- Ensure project source code is in the current directory
- Check file permissions

**Error: AI analysis failed**
- Code structure may be too complex
- Try specifying code path manually
- Consider manual plan creation

## Advanced Usage

**Generate for all test cases:**
```bash
python "$PLUGIN_PATH/skills/assertion-generator/run.py"
```

**Generate for specific test case:**
```bash
python "$PLUGIN_PATH/skills/assertion-generator/run.py" TC001
```
