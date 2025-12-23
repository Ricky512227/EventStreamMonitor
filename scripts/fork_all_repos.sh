#!/bin/bash
# Script to fork all open source repositories using GitHub API

set -e

# List of repositories to fork
declare -a REPOS=(
    "tiangolo/fastapi"
    "pytest-dev/pytest"
    "dpkp/kafka-python"
    "gohugoio/hugo"
    "docker/cli"
    "helm/helm"
    "kubernetes/kubernetes"
    "segmentio/kafka-go"
    "vitejs/vite"
    "typescript-eslint/typescript-eslint"
    "vitest-dev/vitest"
    "mui/material-ui"
    "streamich/react-use"
    "Leaflet/Leaflet"
    "electron/electron"
    "cypress-io/cypress"
    "ToolJet/ToolJet"
)

echo "=========================================="
echo "GitHub Repository Forking Script"
echo "=========================================="
echo ""
echo "This script will fork ${#REPOS[@]} repositories to your GitHub account."
echo ""

# Check if token provided as argument
if [ ! -z "$1" ]; then
    GITHUB_TOKEN="$1"
fi

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN environment variable is not set."
    echo ""
    echo "Usage: $0 [GITHUB_TOKEN]"
    echo "   or: export GITHUB_TOKEN='your-token' && $0"
    echo ""
    echo "To get a token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Generate a new token (classic) with 'repo' scope"
    echo "3. Copy the token and run: $0 YOUR_TOKEN"
    echo ""
    read -p "Or enter your token now (will not be saved): " -s GITHUB_TOKEN
    echo ""
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "❌ Token is required. Exiting."
        exit 1
    fi
fi

# Get GitHub username
echo "Fetching your GitHub username..."
USER_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
USERNAME=$(echo "$USER_RESPONSE" | grep -o '"login":"[^"]*' | head -1 | cut -d'"' -f4)

# Fallback to Python if grep fails
if [ -z "$USERNAME" ]; then
    USERNAME=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['login'])" 2>/dev/null)
fi

if [ -z "$USERNAME" ]; then
    echo "❌ Failed to authenticate. Please check your token."
    exit 1
fi

echo "✅ Authenticated as: $USERNAME"
echo ""
read -p "Continue forking ${#REPOS[@]} repositories? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Starting to fork repositories..."
echo "=========================================="

SUCCESS=0
FAILED=0
ALREADY_FORKED=0

for repo in "${REPOS[@]}"; do
    repo_name=$(basename "$repo")
    echo ""
    echo "Forking $repo..."
    
    # Check if already forked
    response=$(curl -s -w "\n%{http_code}" -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$USERNAME/$repo_name")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" == "200" ]; then
        echo "  ⚠️  Already forked: https://github.com/$USERNAME/$repo_name"
        ((ALREADY_FORKED++))
        continue
    fi
    
    # Fork the repository
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$repo/forks")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" == "202" ] || [ "$http_code" == "200" ]; then
        echo "  ✅ Successfully forked: https://github.com/$USERNAME/$repo_name"
        ((SUCCESS++))
    elif [ "$http_code" == "403" ]; then
        echo "  ❌ Rate limit exceeded or insufficient permissions"
        echo "     Response: $body"
        ((FAILED++))
    elif [ "$http_code" == "404" ]; then
        echo "  ❌ Repository not found: $repo"
        ((FAILED++))
    else
        echo "  ❌ Failed (HTTP $http_code)"
        echo "     Response: $body"
        ((FAILED++))
    fi
    
    # Be nice to GitHub API - small delay
    sleep 1
done

echo ""
echo "=========================================="
echo "Forking Complete!"
echo "=========================================="
echo "✅ Successfully forked: $SUCCESS"
echo "⚠️  Already forked: $ALREADY_FORKED"
echo "❌ Failed: $FAILED"
echo ""
echo "View your forks at: https://github.com/$USERNAME?tab=repositories"
echo ""

