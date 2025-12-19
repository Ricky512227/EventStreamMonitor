#!/usr/bin/env python3
"""
GitHub Activity Agent - Makes small, natural daily improvements to keep repo active
"""
import os
import sys
import random
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

ACTIVITY_TYPES = [
    "code_comment",
    "doc_update",
    "variable_rename",
    "formatting",
    "error_handling",
    "log_improvement",
]


def get_random_file():
    """Get a random Python file from the codebase"""
    python_files = []
    for root, dirs, files in os.walk('services'):
        if '.git' in root or '__pycache__' in root or '.venv' in root:
            continue
        for file in files:
            if file.endswith('.py') and 'test' not in file.lower():
                python_files.append(os.path.join(root, file))
    
    return random.choice(python_files) if python_files else None


def add_helpful_comment(filepath):
    """Add a helpful comment to a random location"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 5:
            return False
        
        # Find a good spot to add comment (not in docstrings)
        indices = [i for i, line in enumerate(lines) if line.strip().startswith('def ') and i > 0]
        if not indices:
            return False
        
        idx = random.choice(indices)
        
        # Check if there's already a comment
        if idx > 0 and lines[idx-1].strip().startswith('#'):
            return False
        
        comment = "# " + random.choice([
            "Handle edge case",
            "Validate input before processing",
            "Clean up resources",
            "Better error handling needed here",
        ])
        
        lines.insert(idx, comment + '\n')
        
        with open(filepath, 'w') as f:
            f.writelines(lines)
        
        return True
    except Exception:
        return False


def improve_error_message(filepath):
    """Improve an error message to be more descriptive"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Look for generic error messages
        improvements = {
            'Error occurred': 'Operation failed',
            'Failed': 'Request processing failed',
            'Invalid': 'Invalid request parameters',
        }
        
        changed = False
        for old, new in improvements.items():
            if old in content and random.random() > 0.7:
                content = content.replace(old, new, 1)
                changed = True
                break
        
        if changed:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        return False
    except Exception:
        return False


def update_docstring(filepath):
    """Add or update a docstring"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Find functions without docstrings
        if 'def ' in content and '"""' not in content[:500]:
            # Add a simple docstring to first function
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('def ') and i + 1 < len(lines):
                    if not lines[i+1].strip().startswith('"""'):
                        docstring = '    """' + random.choice([
                            'Process the request',
                            'Handle user input',
                            'Validate data',
                        ]) + '"""'
                        lines.insert(i+1, docstring)
                        with open(filepath, 'w') as f:
                            f.write('\n'.join(lines))
                        return True
        return False
    except Exception:
        return False


def improve_logging(filepath):
    """Add or improve logging statements"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Find error handling blocks
        for i, line in enumerate(lines):
            if 'except' in line and i + 2 < len(lines):
                if 'logger' in filepath.lower() or 'logging' in filepath.lower():
                    continue
                # Add logging if not present
                if 'logger.' not in lines[i+1] and 'logger.' not in lines[i+2]:
                    indent = len(line) - len(line.lstrip())
                    log_line = ' ' * (indent + 4) + 'logger.error(f"Error: {str(e)}")\n'
                    lines.insert(i+1, log_line)
                    with open(filepath, 'w') as f:
                        f.writelines(lines)
                    return True
        return False
    except Exception:
        return False


def make_change():
    """Make a small, realistic change"""
    filepath = get_random_file()
    if not filepath:
        return False, None
    
    activity = random.choice(ACTIVITY_TYPES)
    success = False
    
    if activity == "code_comment":
        success = add_helpful_comment(filepath)
    elif activity == "error_handling":
        success = improve_error_message(filepath)
    elif activity == "doc_update":
        success = update_docstring(filepath)
    elif activity == "log_improvement":
        success = improve_logging(filepath)
    
    return success, filepath


def generate_commit_message(filepath, activity_type):
    """Generate a natural commit message"""
    filename = os.path.basename(filepath)
    
    messages = {
        "code_comment": [
            f"Add comment to {filename}",
            f"Clarify logic in {filename}",
            f"Update {filename}",
        ],
        "error_handling": [
            f"Improve error handling in {filename}",
            f"Better error messages in {filename}",
            f"Update {filename} error handling",
        ],
        "doc_update": [
            f"Update docs in {filename}",
            f"Add docstring to {filename}",
            f"Improve {filename} documentation",
        ],
        "log_improvement": [
            f"Add logging to {filename}",
            f"Improve logging in {filename}",
            f"Update {filename}",
        ],
    }
    
    default = [
        f"Small improvement to {filename}",
        f"Update {filename}",
        f"Minor change in {filename}",
    ]
    
    options = messages.get(activity_type, default)
    return random.choice(options)


def commit_change(filepath, message):
    """Commit the change"""
    try:
        subprocess.run(['git', 'add', filepath], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Main function"""
    print(f"GitHub Activity Agent - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Making a small improvement...")
    
    # Make a change
    success, filepath = make_change()
    
    if not success or not filepath:
        print("No changes made this time")
        return 0
    
    # Generate commit message
    activity = random.choice(ACTIVITY_TYPES)
    message = generate_commit_message(filepath, activity)
    
    print(f"Modified: {filepath}")
    print(f"Commit message: {message}")
    
    # Commit
    if commit_change(filepath, message):
        print("Change committed successfully")
        print("\nTo push: git push origin main")
        return 0
    else:
        print("Failed to commit")
        return 1


if __name__ == "__main__":
    sys.exit(main())

