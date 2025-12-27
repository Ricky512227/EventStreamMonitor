#!/usr/bin/env python3
"""
Find 'good first issue' in a GitHub repository
"""
import requests
import sys

def find_good_first_issues(repo, token=None):
    """Find good first issues in a repository"""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    params = {
        "state": "open",
        "labels": "good first issue",
        "per_page": 10,
        "sort": "updated"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        issues = response.json()
        
        # Filter out pull requests (GitHub API returns both)
        issues = [issue for issue in issues if "pull_request" not in issue]
        
        return issues
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issues: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 find_good_first_issue.py <owner/repo> [token]")
        print("Example: python3 find_good_first_issue.py tiangolo/fastapi")
        sys.exit(1)
    
    repo = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Searching for 'good first issue' in {repo}...")
    print("=" * 70)
    
    issues = find_good_first_issues(repo, token)
    
    if not issues:
        print("No 'good first issue' labels found.")
        print(f"\nTry searching manually: https://github.com/{repo}/labels/good%20first%20issue")
        return
    
    print(f"\nFound {len(issues)} good first issue(s):\n")
    
    for i, issue in enumerate(issues[:5], 1):  # Show top 5
        print(f"{i}. Issue #{issue['number']}: {issue['title']}")
        print(f"   URL: {issue['html_url']}")
        print(f"   Created: {issue['created_at']}")
        print(f"   Comments: {issue['comments']}")
        if issue.get('body'):
            body_preview = issue['body'][:100].replace('\n', ' ')
            print(f"   Preview: {body_preview}...")
        print()
    
    if issues:
        selected = issues[0]
        print("=" * 70)
        print(f"Recommended: Issue #{selected['number']}")
        print(f"Title: {selected['title']}")
        print(f"URL: {selected['html_url']}")
        print("=" * 70)

if __name__ == "__main__":
    main()

