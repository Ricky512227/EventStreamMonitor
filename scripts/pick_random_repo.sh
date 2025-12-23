#!/bin/bash
# Pick a random repository to contribute to

REPOS_DIR="/Users/alwayskamalsai/CustomProjects"

if [ ! -d "$REPOS_DIR" ]; then
    echo "❌ Repositories directory not found!"
    echo "Run scripts/setup_opensource_repos.sh first"
    exit 1
fi

# Get list of directories
repos=($(ls -d "$REPOS_DIR"/*/ 2>/dev/null | xargs -n1 basename))

if [ ${#repos[@]} -eq 0 ]; then
    echo "❌ No repositories found in $REPOS_DIR"
    echo "Run scripts/setup_opensource_repos.sh first"
    exit 1
fi

# Pick random repo
random_repo=${repos[$RANDOM % ${#repos[@]}]}

echo "=========================================="
echo "🎲 Random Repository Selected"
echo "=========================================="
echo ""
echo "Repository: $random_repo"
echo "Path: $REPOS_DIR/$random_repo"
echo ""
echo "Next steps:"
echo "1. cd $REPOS_DIR/$random_repo"
echo "2. git checkout -b contribute/$(date +%Y%m%d)"
echo "3. Find a 'good first issue' on GitHub"
echo "4. Make your contribution!"
echo ""
echo "GitHub link: https://github.com/$(grep -oP 'url = \K.*' "$REPOS_DIR/$random_repo/.git/config" 2>/dev/null | sed 's|https://github.com/||' | sed 's|\.git||' || echo "unknown")"
echo ""

