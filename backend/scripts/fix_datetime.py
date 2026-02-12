#!/usr/bin/env python3
"""
Script to fix deprecated datetime.utcnow() calls to datetime.now(UTC)
Runs across all Python files in the backend
"""

import os
import re
from pathlib import Path

def fix_datetime_in_file(file_path: Path) -> bool:
    """Fix datetime.utcnow() in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if file uses datetime
        if 'datetime' not in content:
            return False
        
        # Fix imports - add UTC if not present
        if 'from datetime import' in content and 'UTC' not in content:
            # Find the import line
            import_pattern = r'from datetime import ([^\n]+)'
            match = re.search(import_pattern, content)
            if match:
                imports = match.group(1)
                if 'UTC' not in imports:
                    new_imports = imports.rstrip() + ', UTC'
                    content = content.replace(
                        f'from datetime import {imports}',
                        f'from datetime import {new_imports}'
                    )
        
        # Replace datetime.utcnow() with datetime.now(UTC)
        content = content.replace('datetime.utcnow()', 'datetime.now(UTC)')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in backend/app"""
    backend_dir = Path(__file__).parent.parent / 'app'
    
    fixed_count = 0
    total_files = 0
    
    for py_file in backend_dir.rglob('*.py'):
        # Skip __pycache__
        if '__pycache__' in str(py_file):
            continue
        
        total_files += 1
        if fix_datetime_in_file(py_file):
            fixed_count += 1
            print(f"✓ Fixed: {py_file.relative_to(backend_dir.parent)}")
    
    print(f"\n{'='*60}")
    print(f"Processed {total_files} files")
    print(f"Fixed {fixed_count} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
