#!/bin/bash
# Setup script to clone open source repositories for contribution
# This will clone repos locally so you can contribute later

set -e

# Directory to store all cloned repos
REPOS_DIR="/Users/alwayskamalsai/CustomProjects"
mkdir -p "$REPOS_DIR"

# List of repositories to clone
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
echo "Open Source Repository Setup"
echo "=========================================="
echo ""
echo "This script will clone the following repositories to:"
echo "$REPOS_DIR"
echo ""
echo "Repositories to clone:"
for repo in "${REPOS[@]}"; do
    echo "  - $repo"
done
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

cd "$REPOS_DIR"

# Clone each repository
for repo in "${REPOS[@]}"; do
    repo_name=$(basename "$repo")
    echo ""
    echo "=========================================="
    echo "Cloning $repo..."
    echo "=========================================="
    
    if [ -d "$repo_name" ]; then
        echo "  ⚠️  Directory $repo_name already exists, skipping..."
        echo "  (Run 'cd $repo_name && git pull' to update)"
    else
        git clone "https://github.com/$repo.git" "$repo_name" || {
            echo "  ❌ Failed to clone $repo"
            continue
        }
        echo "  ✅ Cloned $repo_name"
    fi
done

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "All repositories cloned to: $REPOS_DIR"
echo ""
echo "Next steps:"
echo "1. Fork repositories on GitHub (go to each repo and click Fork)"
echo "2. Add your fork as a remote:"
echo "   cd $REPOS_DIR/[repo-name]"
echo "   git remote add fork https://github.com/YOUR_USERNAME/[repo-name].git"
echo "3. Find 'good first issue' labels and start contributing!"
echo ""
echo "To track your contributions, see: scripts/track_contributions.md"

