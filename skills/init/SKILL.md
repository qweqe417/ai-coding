---
name: init
description: "Initialize AI Coding integration test framework in current project"
---

# AI Coding - Project Initialization

Initialize the AI Coding integration testing framework for the current project.

## What This Does

- Automatically detects project type (Java/Python/Go/Node.js/Vue/React)
- Generates `.ai-coding/config.yaml` configuration file
- Creates necessary directory structure
- Provides configuration suggestions

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
    echo "Please install the plugin first:"
    echo "  /install https://github.com/ai-coding-team/ai-coding"
    exit 1
fi

# Check dependencies (first time only)
python -c "import yaml, requests, pymysql, redis, pymongo, pika, kafka, elasticsearch, jinja2, rich" 2>/dev/null || {
    echo "⚠️  Installing Python dependencies..."
    pip install -r "$PLUGIN_PATH/requirements.txt"
}

# Execute the init script
python "$PLUGIN_PATH/ai-coding/skills/init/run.py"
```

## Output

The script will:
1. Detect project type and language
2. Create `.ai-coding/` directory structure:
   - `specs/` - Specification documents
   - `testcases/` - Test case definitions
   - `plans/` - Data collection plans
   - `results/` - Test execution results
   - `reports/` - Generated reports
   - `logs/` - Execution logs
3. Generate `config.yaml` with detected settings
4. Display configuration summary

## After Execution

✅ Initialization completed!

**Next steps:**
1. Review and edit `.ai-coding/config.yaml` to configure middleware connections
2. Run `/ai-coding:testcase-generator` to generate test cases from specs
3. Run `/ai-coding:assertion-generator` to generate data collection plans
4. Run `/ai-coding:integration-test` to execute tests

## Configuration

Edit `.ai-coding/config.yaml` to configure:

- **project** - Project name and type
- **service** - Service URL and startup command
- **middleware** - MySQL, Redis, MongoDB, Kafka, RabbitMQ, Elasticsearch connections
- **test** - Test execution settings
- **logging** - Log level and output

## Error Handling

**Error: Python dependencies not found**
```bash
pip install -r "$PLUGIN_PATH/requirements.txt"
```

**Error: Config file already exists**
- The script will prompt whether to overwrite
- Backup your existing config before proceeding

**Error: Cannot detect project type**
- Manually edit `.ai-coding/config.yaml` after generation
- Set `project.type` and `project.language` fields