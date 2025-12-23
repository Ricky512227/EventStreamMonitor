#!/bin/bash
# Script to update local repos with fork remotes after forking

set -e

REPOS_DIR="/Users/alwayskamalsai/CustomProjects"

# Check if GITHUB_TOKEN is set to get username
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set. Please provide your GitHub username:"
    read -p "GitHub Username: " GITHUB_USERNAME
else
    USER_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
    GITHUB_USERNAME=$(echo "$USER_RESPONSE" | grep -o '"login":"[^"]*' | head -1 | cut -d'"' -f4)
    if [ -z "$GITHUB_USERNAME" ]; then
        GITHUB_USERNAME=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['login'])" 2>/dev/null)
    fi
    echo "✅ Detected GitHub username: $GITHUB_USERNAME"
fi

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required. Exiting."
    exit 1
fi

# List of repositories
declare -a REPOS=(
    "fastapi"
    "pytest"
    "kafka-python"
    "hugo"
    "cli"
    "helm"
    "kubernetes"
    "kafka-go"
    "vite"
    "typescript-eslint"
    "vitest"
    "material-ui"
    "react-use"
    "Leaflet"
    "electron"
    "cypress"
    "ToolJet"
)

echo "=========================================="
echo "Setting up fork remotes for local repos"
echo "=========================================="
echo ""

cd "$REPOS_DIR"

for repo_name in "${REPOS[@]}"; do
    if [ ! -d "$repo_name" ]; then
        echo "⚠️  $repo_name not found, skipping..."
        continue
    fi
    
    echo "Setting up $repo_name..."
    cd "$repo_name"
    
    # Check if fork remote already exists
    if git remote | grep -q "^fork$"; then
        echo "  ⚠️  Fork remote already exists, skipping..."
        cd ..
        continue
    fi
    
    # Add fork remote
    git remote add fork "https://github.com/$GITHUB_USERNAME/$repo_name.git" 2>/dev/null || {
        echo "  ⚠️  Could not add fork remote (may already exist)"
    }
    
    # Rename origin to upstream if it points to original repo
    origin_url=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ "$origin_url" == *"github.com"* ]] && [[ "$origin_url" != *"$GITHUB_USERNAME"* ]]; then
        echo "  ℹ️  Origin points to original repo, keeping as is"
        echo "  ✅ Added 'fork' remote pointing to your fork"
    else
        echo "  ✅ Added 'fork' remote"
    fi
    
    cd ..
    echo ""
done

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Your local repos now have:"
echo "  - 'origin': Original repository"
echo "  - 'fork': Your forked repository"
echo ""
echo "To push to your fork:"
echo "  git push fork your-branch-name"
echo ""

