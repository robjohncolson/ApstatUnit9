#!/usr/bin/env python3
"""
Fix Capstone Buttons in index.html

This script automatically fixes the capstone button issues in index.html by:
1. Creating a backup of the original file
2. Replacing incorrect unit IDs (1 and 3 with 8)
3. Updating button labels to clearly indicate their destinations
4. Saving the modified file
"""

import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

def create_backup(file_path):
    """Create a backup of the original file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.{timestamp}.bak"
    try:
        shutil.copy2(file_path, backup_path)
        print(f"✅ Created backup at: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False

def fix_capstone_buttons(file_path):
    """Fix capstone button issues in index.html."""
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Create a backup
        if not create_backup(file_path):
            return False
        
        print(f"Fixing capstone buttons in {file_path}...")
        print("-" * 80)
        
        # Count original instances
        unit1_count = len(re.findall(r'quiz\.quizId === "1-capstone_q\d"', content))
        unit3_count = len(re.findall(r'quiz\.quizId === "3-capstone_q\d"', content))
        
        print(f"Found {unit1_count} references to unit 1 capstone quiz IDs")
        print(f"Found {unit3_count} references to unit 3 capstone quiz IDs")
        
        # 1. Replace unit IDs
        # Replace "1-capstone_q1" with "8-capstone_q1"
        content = re.sub(
            r'(quiz\.quizId === ")1(-capstone_q1)(")',
            r'\g<1>8\g<2>\g<3>',
            content
        )
        
        # Replace "1-capstone_q2" with "8-capstone_q2"
        content = re.sub(
            r'(quiz\.quizId === ")1(-capstone_q2)(")',
            r'\g<1>8\g<2>\g<3>',
            content
        )
        
        # Replace "3-capstone_q1" with "8-capstone_q1"
        content = re.sub(
            r'(quiz\.quizId === ")3(-capstone_q1)(")',
            r'\g<1>8\g<2>\g<3>',
            content
        )
        
        # Replace "3-capstone_q2" with "8-capstone_q2"
        content = re.sub(
            r'(quiz\.quizId === ")3(-capstone_q2)(")',
            r'\g<1>8\g<2>\g<3>',
            content
        )
        
        # Replace "3-capstone_q3" with "8-capstone_q3"
        content = re.sub(
            r'(quiz\.quizId === ")3(-capstone_q3)(")',
            r'\g<1>8\g<2>\g<3>',
            content
        )
        
        # 2. Fix ternary question title expressions
        # Pattern: const questionTitle = quiz.quizId === "X-capstone_q1" ? "..." : ...
        q_title_pattern = r'(const\s+(?:questionTitle|title|linkText)\s*=\s*(?:.*?)quiz\.quizId\s*===\s*")\d(-capstone_q1"\s*\?\s*")([^"]+)("\s*:\s*(?:.*?)quiz\.quizId\s*===\s*")\d(-capstone_q2"\s*\?\s*")([^"]+)("\s*:[^"]*")([^"]*)'
        
        def q_title_replacer(match):
            prefix1 = match.group(1)
            prefix2 = match.group(4)
            prefix3 = match.group(7)
            suffix = match.group(8)
            
            # Determine if this is a questions or answers pattern
            is_question = "question" in match.group(0).lower() or "frq question" in match.group(3).lower()
            
            if is_question:
                return f'{prefix1}8-capstone_q1" ? "FRQ Questions{prefix2}8-capstone_q2" ? "MCQ Part A Questions{prefix3}MCQ Part B Questions{suffix}'
            else:
                # It's likely an answer pattern or generic
                # We'll use question as default, but the next regex pass will fix answers
                return f'{prefix1}8-capstone_q1" ? "FRQ Questions{prefix2}8-capstone_q2" ? "MCQ Part A Questions{prefix3}MCQ Part B Questions{suffix}'
            
        # Apply the ternary question title replacement
        content = re.sub(q_title_pattern, q_title_replacer, content, flags=re.DOTALL)
        
        # 3. Fix ternary answer title expressions
        # Pattern: const answerTitle = quiz.quizId === "X-capstone_q1" ? "..." : ...
        a_title_pattern = r'(const\s+answerTitle\s*=\s*(?:.*?)quiz\.quizId\s*===\s*")\d(-capstone_q1"\s*\?\s*")([^"]+)("\s*:\s*(?:.*?)quiz\.quizId\s*===\s*")\d(-capstone_q2"\s*\?\s*")([^"]+)("\s*:[^"]*")([^"]*)'
        
        def a_title_replacer(match):
            prefix1 = match.group(1)
            prefix2 = match.group(4)
            prefix3 = match.group(7)
            suffix = match.group(8)
            
            return f'{prefix1}8-capstone_q1" ? "FRQ Answers{prefix2}8-capstone_q2" ? "MCQ Part A Answers{prefix3}MCQ Part B Answers{suffix}'
            
        # Apply the ternary answer title replacement
        content = re.sub(a_title_pattern, a_title_replacer, content, flags=re.DOTALL)
        
        # 4. Fix individual label assignments
        # Pattern: if (quiz.quizId === "X-capstone_qN") { linkText = "..." }
        label_pattern = r'(if\s*\(\s*quiz\.quizId\s*===\s*")\d(-capstone_q1"\s*\)\s*\{\s*linkText\s*=\s*")([^"]+)(")'
        
        def label_replacer(match):
            prefix1 = match.group(1)
            prefix2 = match.group(2)
            suffix = match.group(4)
            
            return f'{prefix1}8{prefix2}FRQ Questions{suffix}'
            
        # Apply the label replacements
        content = re.sub(label_pattern, label_replacer, content)
        
        # 5. Fix label assignments for MCQ Part A
        label_pattern_a = r'(else\s+if\s*\(\s*quiz\.quizId\s*===\s*")\d(-capstone_q2"\s*\)\s*\{\s*linkText\s*=\s*")([^"]+)(")'
        
        def label_replacer_a(match):
            prefix1 = match.group(1)
            prefix2 = match.group(2)
            suffix = match.group(4)
            
            return f'{prefix1}8{prefix2}MCQ Part A Questions{suffix}'
            
        # Apply the MCQ Part A label replacements
        content = re.sub(label_pattern_a, label_replacer_a, content)
        
        # 6. Fix label assignments for MCQ Part B
        label_pattern_b = r'(else\s+if\s*\(\s*quiz\.quizId\s*===\s*")\d(-capstone_q3"\s*\)\s*\{\s*linkText\s*=\s*")([^"]+)(")'
        
        def label_replacer_b(match):
            prefix1 = match.group(1)
            prefix2 = match.group(2)
            suffix = match.group(4)
            
            return f'{prefix1}8{prefix2}MCQ Part B Questions{suffix}'
            
        # Apply the MCQ Part B label replacements
        content = re.sub(label_pattern_b, label_replacer_b, content)
        
        # 7. Fix specific title assignments with unique patterns
        content = content.replace(
            'quiz.quizId === "1-capstone_q1" ? "FRQ Questions PDF"',
            'quiz.quizId === "8-capstone_q1" ? "FRQ Questions"'
        )
        
        content = content.replace(
            'quiz.quizId === "1-capstone_q2" ? "MCQ Part A PDF"',
            'quiz.quizId === "8-capstone_q2" ? "MCQ Part A Questions"'
        )
        
        content = content.replace(
            'MCQ Part B PDF"',
            'MCQ Part B Questions"'
        )
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Verify the changes
        with open(file_path, 'r', encoding='utf-8') as file:
            new_content = file.read()
        
        # Count new instances
        unit8_count = len(re.findall(r'quiz\.quizId === "8-capstone_q\d"', new_content))
        unit1_after = len(re.findall(r'quiz\.quizId === "1-capstone_q\d"', new_content))
        unit3_after = len(re.findall(r'quiz\.quizId === "3-capstone_q\d"', new_content))
        
        print("\n" + "=" * 80)
        print("CHANGES SUMMARY")
        print("=" * 80)
        print(f"✅ Replaced {unit1_count + unit3_count} incorrect unit IDs with unit 8")
        print(f"✅ Now have {unit8_count} references to unit 8 capstone quiz IDs")
        
        if unit1_after > 0 or unit3_after > 0:
            print(f"⚠️ Warning: Still found {unit1_after} references to unit 1 and {unit3_after} references to unit 3")
            print("   These might be in comments or in areas not covered by the replacement patterns.")
        else:
            print("✅ All references to unit 1 and unit 3 capstone quizzes have been replaced")
        
        print(f"\n✅ Updated button labels to clearly indicate their destinations")
        print(f"✅ Modified file saved back to: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing capstone buttons: {e}")
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
    
    print(f"Found index.html at: {index_path}")
    
    # Confirm with the user
    if input("Do you want to proceed with fixing capstone buttons? This will modify index.html. (y/n): ").lower() != 'y':
        print("Operation canceled by user.")
        return
    
    # Fix the capstone buttons
    fix_capstone_buttons(index_path)

if __name__ == "__main__":
    main() 