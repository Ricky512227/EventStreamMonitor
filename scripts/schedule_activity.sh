#!/bin/bash
# Schedule GitHub activity agent to run daily

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SCRIPT="$SCRIPT_DIR/github_activity_agent.py"

# Run the agent
cd "$SCRIPT_DIR/.."
python3 "$AGENT_SCRIPT"

# Push if there are commits
if [ -n "$(git log origin/main..HEAD --oneline 2>/dev/null)" ]; then
    git push origin main
fi

