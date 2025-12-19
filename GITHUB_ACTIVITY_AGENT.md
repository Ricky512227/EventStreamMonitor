# GitHub Activity Agent

Automated script to make small, natural improvements to keep your GitHub repository active.

## What it does

The agent makes small, realistic changes daily:
- Adds helpful code comments
- Improves error messages
- Updates documentation
- Adds logging improvements
- Makes minor code improvements

All changes are committed with natural, human-friendly messages.

## Usage

### Manual Run

```bash
python3 scripts/github_activity_agent.py
```

This will:
1. Pick a random file
2. Make a small improvement
3. Commit with a natural message
4. You can then push: `git push origin main`

### Automated Daily Schedule

#### macOS (using launchd)

1. Create plist file:
```bash
cat > ~/Library/LaunchAgents/com.github.activity.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.github.activity</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$(pwd)/scripts/schedule_activity.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
</dict>
</plist>
EOF
```

2. Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.github.activity.plist
```

#### Linux (using cron)

```bash
# Add to crontab (runs daily at 10 AM)
0 10 * * * cd /path/to/EventStreamMonitor && python3 scripts/github_activity_agent.py && git push origin main
```

#### GitHub Actions (recommended)

Create `.github/workflows/daily-activity.yml`:

```yaml
name: Daily Activity

on:
  schedule:
    - cron: '0 10 * * *'  # Run daily at 10 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  activity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Run activity agent
        run: python3 scripts/github_activity_agent.py
      
      - name: Push changes
        run: |
          git config --global user.name "GitHub Activity Bot"
          git config --global user.email "actions@github.com"
          git push origin main
```

## Types of Changes

The agent randomly makes one of these improvements:

1. **Code Comments** - Adds helpful comments to clarify logic
2. **Error Handling** - Improves error messages
3. **Documentation** - Adds or updates docstrings
4. **Logging** - Adds logging statements
5. **Formatting** - Minor code formatting improvements

## Commit Messages

All commits use natural, human-friendly messages like:
- "Add comment to user_service.py"
- "Improve error handling in task_processor.py"
- "Update documentation"
- "Small improvement to config.py"

## Notes

- Changes are small and realistic
- Only modifies Python files in `services/` directory
- Skips test files
- Avoids obvious patterns
- Natural commit messages
- Can be run manually or scheduled

## Safety

The agent:
- Only modifies code, doesn't delete anything critical
- Makes small, reversible changes
- Uses git to track all changes
- Can be disabled anytime

