#!/bin/bash
# Create a draft PR using GitHub CLI or API

set -e

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Usage: $0 <owner/repo> <branch> <title> [body] [token]"
    echo "Example: $0 streamich/react-use fix/remove-warnings-useDeepCompareEffect 'fix: Remove warnings' 'Fixes #755'"
    exit 1
fi

REPO=$1
BRANCH=$2
TITLE=$3
BODY=${4:-"Fixes #755"}
TOKEN=${5:-$GITHUB_TOKEN}

if [ -z "$TOKEN" ]; then
    echo "Error: GitHub token required"
    exit 1
fi

# Get your username
USERNAME=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/user | python3 -c "import sys, json; print(json.load(sys.stdin)['login'])" 2>/dev/null)

echo "Creating draft PR..."
echo "Repository: $REPO"
echo "Branch: $BRANCH"
echo "Title: $TITLE"
echo ""

# Create draft PR
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d "{
    \"title\": \"$TITLE\",
    \"body\": \"$BODY\",
    \"head\": \"$USERNAME:$BRANCH\",
    \"base\": \"master\",
    \"draft\": true
  }" \
  "https://api.github.com/repos/$REPO/pulls")

PR_URL=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('html_url', 'Error'))" 2>/dev/null)

if [[ "$PR_URL" == *"github.com"* ]]; then
    echo "✅ Draft PR created successfully!"
    echo "URL: $PR_URL"
else
    echo "❌ Failed to create PR"
    echo "Response: $RESPONSE"
    exit 1
fi

