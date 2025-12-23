#!/usr/bin/env python3
"""
Open Source Contribution Helper

This script helps find contribution opportunities in projects you use.
It checks for "good first issue" labels and helps you get started.
"""
import requests
import json
from typing import List, Dict
from datetime import datetime


# Popular open source projects you use
PROJECTS = {
    "python-dotenv": {
        "repo": "python-dotenv/python-dotenv",
        "description": "Environment variable management",
        "language": "Python"
    },
    "requests": {
        "repo": "psf/requests",
        "description": "HTTP library for Python",
        "language": "Python"
    },
    "Flask": {
        "repo": "pallets/flask",
        "description": "Web framework",
        "language": "Python"
    },
    "kafka-python": {
        "repo": "dpkp/kafka-python",
        "description": "Kafka client for Python",
        "language": "Python"
    },
    "gunicorn": {
        "repo": "benoitc/gunicorn",
        "description": "Python WSGI HTTP Server",
        "language": "Python"
    },
    "redis-py": {
        "repo": "redis/redis-py",
        "description": "Redis Python client",
        "language": "Python"
    }
}


def get_github_issues(repo: str, labels: List[str] = None) -> List[Dict]:
    """
    Fetch GitHub issues for a repository
    
    Args:
        repo: Repository in format 'owner/repo'
        labels: List of labels to filter by (e.g., ['good first issue'])
        
    Returns:
        List of issue dictionaries
    """
    url = f"https://api.github.com/repos/{repo}/issues"
    params = {
        "state": "open",
        "per_page": 10,
        "sort": "updated"
    }
    
    if labels:
        params["labels"] = ",".join(labels)
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issues for {repo}: {e}")
        return []


def format_issue(issue: Dict) -> str:
    """Format an issue for display"""
    title = issue.get("title", "No title")
    number = issue.get("number", "?")
    url = issue.get("html_url", "")
    labels = [label["name"] for label in issue.get("labels", [])]
    created = issue.get("created_at", "")
    
    return f"""
  Issue #{number}: {title}
  Labels: {', '.join(labels) if labels else 'None'}
  Created: {created}
  URL: {url}
"""


def main():
    """Main function to find contribution opportunities"""
    print("=" * 70)
    print("OPEN SOURCE CONTRIBUTION OPPORTUNITIES")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    print("Searching for 'good first issue' opportunities...")
    print()
    
    opportunities = []
    
    for project_name, project_info in PROJECTS.items():
        repo = project_info["repo"]
        print(f"Checking {project_name} ({repo})...")
        
        # Get good first issues
        issues = get_github_issues(repo, labels=["good first issue"])
        
        if issues:
            print(f"  Found {len(issues)} 'good first issue'(s)!")
            opportunities.append({
                "project": project_name,
                "repo": repo,
                "issues": issues,
                "info": project_info
            })
            
            for issue in issues[:3]:  # Show first 3
                print(format_issue(issue))
        else:
            print(f"  No 'good first issue' labels found")
        
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if opportunities:
        total_issues = sum(len(opp["issues"]) for opp in opportunities)
        print(f"Found {total_issues} contribution opportunities across {len(opportunities)} projects!")
        print()
        print("Next steps:")
        print("1. Choose an issue from the list above")
        print("2. Fork the repository: https://github.com/{repo}")
        print("3. Clone your fork and create a branch")
        print("4. Make your contribution")
        print("5. Submit a pull request")
        print()
        print("Recommended projects to start with:")
        for opp in opportunities[:3]:
            print(f"  - {opp['project']}: {len(opp['issues'])} issues available")
    else:
        print("No 'good first issue' labels found in these projects.")
        print("Try searching for other labels like 'help wanted' or 'documentation'")
    
    print()
    print("For more opportunities, visit:")
    print("  - https://github.com/topics/good-first-issue")
    print("  - https://www.firsttimersonly.com/")
    print("  - https://up-for-grabs.net/")


if __name__ == "__main__":
    main()

