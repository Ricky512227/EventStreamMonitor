# Open Source Contribution Tracker

## Repository Status

| Repository | Cloned | Forked | Issue Selected | Branch Created | PR Status |
|------------|--------|--------|----------------|----------------|-----------|
| FastAPI | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Pytest | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| kafka-python | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Hugo | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Docker CLI | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Helm | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Kubernetes | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| kafka-go | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Vite | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| typescript-eslint | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Vitest | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Material-UI | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| react-use | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Leaflet | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Electron | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Cypress | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| ToolJet | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## Contribution Workflow

1. **Clone Repository** ✅ (Run setup script)
2. **Fork on GitHub** - Go to repo and click Fork
3. **Add Fork Remote**:
   ```bash
   cd ~/opensource-contributions/[repo-name]
   git remote add fork https://github.com/YOUR_USERNAME/[repo-name].git
   ```
4. **Find Good First Issue** - Look for "good first issue" label
5. **Create Branch**:
   ```bash
   git checkout -b fix/issue-[number]-[description]
   ```
6. **Make Changes** - Implement the fix/feature
7. **Commit & Push**:
   ```bash
   git add .
   git commit -m "fix: [description] (fixes #issue-number)"
   git push fork fix/issue-[number]-[description]
   ```
8. **Create Draft PR** - On GitHub, create PR as draft
9. **Review & Submit** - Review your changes, then mark PR as ready

## Quick Commands

### Pick a random repo to contribute to:
```bash
cd ~/opensource-contributions
ls | shuf -n 1
```

### Update all repos:
```bash
cd ~/opensource-contributions
for dir in */; do
    echo "Updating $dir"
    cd "$dir" && git pull && cd ..
done
```

### Find good first issues:
Visit: https://github.com/[org]/[repo]/labels/good%20first%20issue

