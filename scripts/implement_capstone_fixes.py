#!/usr/bin/env python3
"""
Implement Capstone Button Fixes

This script implements the fixes required for the capstone buttons in index.html:
1. Replacing unit IDs (1 and 3 with 9)
2. Improving button labels to clearly indicate content type

The script creates a backup of the original file before making changes.
"""

import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

def create_backup(file_path):
    """Create a backup of the original file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.{timestamp}.bak"
    try:
        shutil.copy2(file_path, backup_path)
        print(f"✅ Created backup at: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False

def implement_fixes(html_file_path):
    """Implement the fixes to the index.html file"""
    try:
        # Read the original content
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"Fixing capstone buttons in {html_file_path}...")
        print("-" * 80)
        
        # Create a backup of the original file
        if not create_backup(html_file_path):
            return False
        
        # 1. Fix Unit IDs - replace quiz.quizId === "1-capstone_qX" or quiz.quizId === "3-capstone_qX"
        unit_id_pattern = r'(quiz\.quizId\s*===\s*")([13])(-capstone_q(\d))(")'
        
        # Count original occurrences
        unit1_count = len(re.findall(r'quiz\.quizId\s*===\s*"1-capstone_q\d"', content))
        unit3_count = len(re.findall(r'quiz\.quizId\s*===\s*"3-capstone_q\d"', content))
        
        print(f"Found {unit1_count} references to unit 1 capstone quiz IDs")
        print(f"Found {unit3_count} references to unit 3 capstone quiz IDs")
        
        # Replace all unit IDs with 9
        content = re.sub(unit_id_pattern, r'\g<1>9\g<3>\g<5>', content)
        
        # 2. Fix button labels - remove "PDF" suffix and ensure clear content type indication
        label_patterns = [
            (r'"FRQ Questions PDF"', r'"FRQ Questions"'),
            (r'"MCQ Part A PDF"', r'"MCQ Part A Questions"'),
            (r'"MCQ Part B PDF"', r'"MCQ Part B Questions"')
        ]
        
        label_count = 0
        for pattern, replacement in label_patterns:
            # Count original occurrences
            count = len(re.findall(pattern, content))
            label_count += count
            if count > 0:
                print(f"Found {count} instances of {pattern}")
            
            # Replace with improved label
            content = content.replace(pattern, replacement)
        
        # 3. Fix ternary expressions for question titles
        # This is more complex and we need to handle multiple patterns
        
        # Write the updated content back to the file
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Verify the changes
        with open(html_file_path, 'r', encoding='utf-8') as file:
            new_content = file.read()
        
        # Count new instances
        unit9_count = len(re.findall(r'quiz\.quizId\s*===\s*"9-capstone_q\d"', new_content))
        unit1_after = len(re.findall(r'quiz\.quizId\s*===\s*"1-capstone_q\d"', new_content))
        unit3_after = len(re.findall(r'quiz\.quizId\s*===\s*"3-capstone_q\d"', new_content))
        
        print("\n" + "=" * 80)
        print("CHANGES SUMMARY")
        print("=" * 80)
        print(f"✅ Replaced {unit1_count + unit3_count} incorrect unit IDs with unit 9")
        print(f"✅ Improved {label_count} button labels to clearly indicate content type")
        print(f"✅ Now have {unit9_count} references to unit 9 capstone quiz IDs")
        
        if unit1_after > 0 or unit3_after > 0:
            print(f"⚠️ There are still {unit1_after} references to unit 1 and {unit3_after} references to unit 3")
            print("   You may need to run the script again or fix these manually.")
        
        print("\nDone! The capstone buttons should now correctly indicate their content type and point to unit 9.")
        return True
        
    except Exception as e:
        print(f"Error implementing fixes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Find index.html in the current directory or parent directory
    current_dir = Path.cwd()
    index_path = current_dir / "index.html"
    
    if not index_path.exists():
        # Try parent directory
        index_path = current_dir.parent / "index.html"
    
    if not index_path.exists():
        print("❌ Could not find index.html in current or parent directory.")
        return
    
    # Ask for confirmation before modifying files
    print("This script will modify index.html to fix capstone button issues.")
    print("A backup of the original file will be created before making changes.")
    choice = input("Do you want to proceed? (y/n): ").strip().lower()
    
    if choice in ('y', 'yes'):
        implement_fixes(index_path)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main() 