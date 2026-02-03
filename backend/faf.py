"""
Script to find where gemini-2.0-flash-exp is referenced
Run this in your D:\ARAI\backend directory
"""

import os
import sys

def find_model_references(directory):
    """Find all files containing the old model name"""
    old_model = "gemini-2.0-flash-exp"
    new_model = "gemini-1.5-flash"
    
    files_to_check = []
    
    for root, dirs, files in os.walk(directory):
        # Skip venv and other common directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if old_model in content:
                            files_to_check.append(filepath)
                            print(f"\n📁 Found in: {filepath}")
                            
                            # Show the lines containing the old model
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if old_model in line:
                                    print(f"   Line {i}: {line.strip()}")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    if not files_to_check:
        print("\n✅ No references to 'gemini-2.0-flash-exp' found!")
    else:
        print(f"\n\n🔧 Found {len(files_to_check)} file(s) that need updating.")
        print(f"\nReplace '{old_model}' with '{new_model}' in these files.")
    
    return files_to_check

if __name__ == "__main__":
    # Use current directory or provided directory
    search_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print(f"🔍 Searching for 'gemini-2.0-flash-exp' in: {search_dir}\n")
    find_model_references(search_dir)