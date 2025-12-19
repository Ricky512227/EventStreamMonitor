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
        
        if len(lines) < 10:
            return False
        
        # Find functions or classes
        indices = []
        for i, line in enumerate(lines):
            if (line.strip().startswith('def ') or line.strip().startswith('class ')) and i > 0:
                # Check if there's already a comment above
                if i > 0 and not lines[i-1].strip().startswith('#'):
                    indices.append(i)
        
        if not indices:
            return False
        
        idx = random.choice(indices)
        
        comments = [
            "# Validate input before processing",
            "# Handle edge case",
            "# Clean up resources",
            "# Process result",
        ]
        
        comment = random.choice(comments) + '\n'
        lines.insert(idx, comment)
        
        with open(filepath, 'w') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        return False


def improve_error_message(filepath):
    """Improve an error message to be more descriptive"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        changed = False
        improvements = [
            ('message_data="Database Error"', 'message_data="Database operation failed"'),
            ('message_data="Error"', 'message_data="An error occurred"'),
            ('"Unknown error caused"', '"An unexpected error occurred"'),
        ]
        
        for i, line in enumerate(lines):
            for old, new in improvements:
                if old in line:
                    lines[i] = line.replace(old, new, 1)
                    changed = True
                    break
            if changed:
                break
        
        if changed:
            with open(filepath, 'w') as f:
                f.writelines(lines)
            return True
        return False
    except Exception:
        return False


def update_docstring(filepath):
    """Add or update a docstring"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Find first function without docstring
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # Check if next line is docstring
                if i + 1 < len(lines) and not lines[i+1].strip().startswith('"""'):
                    indent = len(line) - len(line.lstrip())
                    docstring = ' ' * indent + '    """' + random.choice([
                        'Process request',
                        'Handle input',
                        'Validate data',
                    ]) + '"""\n'
                    lines.insert(i+1, docstring)
                    with open(filepath, 'w') as f:
                        f.writelines(lines)
                    return True
        return False
    except Exception:
        return False


def improve_logging(filepath):
    """Add or improve logging statements"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Skip if this is a logger file
        if 'logger' in filepath.lower() or 'logging' in filepath.lower():
            return False
        
        # Check if logger is imported
        has_logger = any('logger' in line.lower() for line in lines[:20])
        if not has_logger:
            return False
        
        # Find exception handling without logging
        for i, line in enumerate(lines):
            if 'except' in line and 'Exception' in line and i + 3 < len(lines):
                # Check if logging exists in next few lines
                has_log = any('logger.' in lines[j] for j in range(i+1, min(i+5, len(lines))))
                if not has_log:
                    indent = len(line) - len(line.lstrip())
                    log_line = ' ' * (indent + 4) + 'logger.error(f"Error processing request: {str(e)}")\n'
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
        return False, None, None
    
    # Try different activities until one works
    activities = random.sample(ACTIVITY_TYPES, len(ACTIVITY_TYPES))
    
    for activity in activities:
        if activity == "code_comment":
            success = add_helpful_comment(filepath)
        elif activity == "error_handling":
            success = improve_error_message(filepath)
        elif activity == "doc_update":
            success = update_docstring(filepath)
        elif activity == "log_improvement":
            success = improve_logging(filepath)
        else:
            continue
        
        if success:
            return True, filepath, activity
    
    return False, None, None


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
    success, filepath, activity = make_change()
    
    if not success or not filepath:
        print("No changes made this time")
        return 0
    
    # Generate commit message
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

