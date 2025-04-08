#!/usr/bin/env python3
"""
Generate Focused Fixes for Capstone Buttons

This script focuses specifically on the Unit 9 capstone button issues in index.html and 
generates precise code replacements. It doesn't modify any files directly.

Based on our analysis, we need to:
1. Replace unit IDs (1 and 3) with 9
2. Ensure button labels properly indicate content type (FRQ, MCQ Part A, MCQ Part B)
"""

import os
import re
import sys
from pathlib import Path

def generate_focused_fixes(content):
    """
    Generate specific, focused fixes for capstone button issues in index.html
    """
    fixes = []
    
    # Search pattern 1: Simple unit ID replacements in direct comparisons
    # Example: quiz.quizId === "3-capstone_q1" -> quiz.quizId === "9-capstone_q1"
    pattern1 = r'(quiz\.quizId\s*===\s*")([13])(-capstone_q(\d))(")' 
    
    for match in re.finditer(pattern1, content):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        quiz_num = match.group(4)
        
        # Create replacement with correct unit ID
        replacement = f'{match.group(1)}9{match.group(3)}{match.group(5)}'
        
        # Add to fixes list
        fixes.append({
            'type': 'Unit ID Fix',
            'line': line_num,
            'original': original,
            'replacement': replacement
        })
    
    # Search pattern 2: "FRQ Questions PDF" -> "FRQ Questions"
    pattern2 = r'"(FRQ|MCQ Part A|MCQ Part B) (Questions|Answers) PDF"'
    
    for match in re.finditer(pattern2, content):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        content_type = match.group(1)
        answer_type = match.group(2)
        
        # Create replacement without "PDF" suffix
        replacement = f'"{content_type} {answer_type}"'
        
        # Add to fixes list
        fixes.append({
            'type': 'Label Suffix Fix',
            'line': line_num,
            'original': original,
            'replacement': replacement
        })
    
    # Search pattern 3: Fix complete ternary expressions for question titles
    pattern3 = r'(const\s+(?:questionTitle|title|linkText)\s*=\s*.*?quiz\.quizId\s*===\s*")(\d)(-capstone_q1"\s*\?\s*")([^"]+)("\s*:\s*.*?quiz\.quizId\s*===\s*")(\d)(-capstone_q2"\s*\?\s*")([^"]+)("\s*:\s*.*?(?:quiz\.quizId\s*===\s*")(\d)(-capstone_q3"\s*\?\s*")([^"]+)("|\s*:[^"]*"))'
    
    for match in re.finditer(pattern3, content, re.DOTALL):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        
        # Extract the structure of the ternary
        prefix = match.group(1)
        unit1 = match.group(2)
        mid1 = match.group(3)
        label1 = match.group(4)
        mid2 = match.group(5)
        unit2 = match.group(6)
        mid3 = match.group(7)
        label2 = match.group(8)
        mid4 = match.group(9)
        
        # Some ternaries have a third condition, some don't
        if len(match.groups()) >= 12:
            unit3 = match.group(10)
            mid5 = match.group(11)
            label3 = match.group(12)
            suffix = match.group(13)
            
            # Create replacement with correct unit IDs and labels
            replacement = f'{prefix}9{mid1}FRQ Questions{mid2}9{mid3}MCQ Part A Questions{mid4}9{mid5}MCQ Part B Questions{suffix}'
        else:
            # Simpler case without third condition
            suffix = match.group(10)
            replacement = f'{prefix}9{mid1}FRQ Questions{mid2}9{mid3}MCQ Part A Questions{mid4}'
        
        # Add to fixes list
        fixes.append({
            'type': 'Ternary Expression Fix',
            'line': line_num,
            'original': original[:100] + "..." if len(original) > 100 else original,
            'replacement': replacement[:100] + "..." if len(replacement) > 100 else replacement,
            'full_original': original,
            'full_replacement': replacement
        })
    
    # Search pattern 4: Fix answer title ternary expressions
    pattern4 = r'(const\s+answerTitle\s*=\s*.*?quiz\.quizId\s*===\s*")(\d)(-capstone_q1"\s*\?\s*")([^"]+)("\s*:\s*.*?quiz\.quizId\s*===\s*")(\d)(-capstone_q2"\s*\?\s*")([^"]+)("\s*:\s*.*?(?:quiz\.quizId\s*===\s*")(\d)(-capstone_q3"\s*\?\s*")([^"]+)("|\s*:[^"]*"))'
    
    for match in re.finditer(pattern4, content, re.DOTALL):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        
        # Extract structure similar to pattern3
        prefix = match.group(1)
        unit1 = match.group(2)
        mid1 = match.group(3)
        label1 = match.group(4)
        mid2 = match.group(5)
        unit2 = match.group(6)
        mid3 = match.group(7)
        label2 = match.group(8)
        mid4 = match.group(9)
        
        # Some ternaries have a third condition, some don't
        if len(match.groups()) >= 12:
            unit3 = match.group(10)
            mid5 = match.group(11)
            label3 = match.group(12)
            suffix = match.group(13)
            
            # Create replacement with correct unit IDs and labels
            replacement = f'{prefix}9{mid1}FRQ Answers{mid2}9{mid3}MCQ Part A Answers{mid4}9{mid5}MCQ Part B Answers{suffix}'
        else:
            # Simpler case without third condition
            suffix = match.group(10)
            replacement = f'{prefix}9{mid1}FRQ Answers{mid2}9{mid3}MCQ Part A Answers{mid4}'
        
        # Add to fixes list
        fixes.append({
            'type': 'Answer Ternary Fix',
            'line': line_num,
            'original': original[:100] + "..." if len(original) > 100 else original,
            'replacement': replacement[:100] + "..." if len(replacement) > 100 else replacement,
            'full_original': original,
            'full_replacement': replacement
        })
    
    # Pattern 5: Fix if-else if block for capstone quiz IDs
    pattern5 = r'(if\s*\(\s*quiz\.quizId\s*===\s*")(\d)(-capstone_q1"\s*\)\s*\{\s*linkText\s*=\s*")([^"]+)(".*?else\s+if\s*\(\s*quiz\.quizId\s*===\s*")(\d)(-capstone_q2"\s*\)\s*\{\s*linkText\s*=\s*")([^"]+)(".*?else\s+if\s*\(\s*quiz\.quizId\s*===\s*")(\d)(-capstone_q3"\s*\)\s*\{\s*linkText\s*=\s*")([^"]+)(")'
    
    for match in re.finditer(pattern5, content, re.DOTALL):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        
        # Extract all parts
        replace_parts = []
        for i in range(0, len(match.groups()), 4):
            if i+3 < len(match.groups()):
                prefix = match.group(i+1)
                unit = match.group(i+2)
                mid = match.group(i+3)
                label = match.group(i+4)
                suffix = match.group(i+5) if i+5 < len(match.groups()) else ""
                
                q_num = int(unit[-1])
                if q_num == 1:
                    new_label = "FRQ Questions"
                elif q_num == 2:
                    new_label = "MCQ Part A Questions"
                elif q_num == 3:
                    new_label = "MCQ Part B Questions"
                else:
                    new_label = label
                
                replace_parts.append((prefix, unit, mid, label, new_label, suffix))
        
        # Build replacement
        replacement = ""
        for i, parts in enumerate(replace_parts):
            prefix, unit, mid, old_label, new_label, suffix = parts
            if i < len(replace_parts) - 1:
                replacement += f'{prefix}9{mid}{new_label}{suffix}'
            else:
                replacement += f'{prefix}9{mid}{new_label}'
        
        # Add the final part
        if match.group(len(match.groups())):
            replacement += match.group(len(match.groups()))
        
        # Add to fixes list
        fixes.append({
            'type': 'If-Block Fix',
            'line': line_num,
            'original': original[:100] + "..." if len(original) > 100 else original,
            'replacement': replacement[:100] + "..." if len(replacement) > 100 else replacement,
            'full_original': original,
            'full_replacement': replacement
        })
    
    return fixes

def display_fixes(fixes):
    """
    Display the fixes in a readable format
    """
    # Group fixes by type
    fixes_by_type = {}
    for fix in fixes:
        fix_type = fix['type']
        if fix_type not in fixes_by_type:
            fixes_by_type[fix_type] = []
        fixes_by_type[fix_type].append(fix)
    
    # Print summary
    print(f"\nFound {len(fixes)} total fixes needed across {len(fixes_by_type)} categories:\n")
    for fix_type, type_fixes in fixes_by_type.items():
        print(f"- {fix_type}: {len(type_fixes)} occurrences")
    
    # Print detailed fixes by type
    print("\n" + "=" * 80)
    print("DETAILED FIXES BY TYPE")
    print("=" * 80)
    
    for fix_type, type_fixes in fixes_by_type.items():
        print(f"\n{fix_type} ({len(type_fixes)} occurrences):")
        print("-" * 80)
        
        # Show examples of each type
        for i, fix in enumerate(type_fixes[:3]):
            print(f"Example {i+1} (line {fix['line']}):")
            print("  ORIGINAL: " + fix['original'])
            print("  REPLACE WITH: " + fix['replacement'])
            print()
        
        if len(type_fixes) > 3:
            print(f"... and {len(type_fixes) - 3} more similar fixes")
    
    # Print implementation guide
    print("\n" + "=" * 80)
    print("IMPLEMENTATION GUIDE")
    print("=" * 80)
    
    print("\nTo fix the capstone buttons in index.html, make the following changes:")
    
    # Unit ID fixes
    if 'Unit ID Fix' in fixes_by_type:
        print("\n1. Replace Incorrect Unit IDs")
        print("   Search for: quiz.quizId === \"1-capstone_q1\" or quiz.quizId === \"3-capstone_q1\"")
        print("   Replace with: quiz.quizId === \"9-capstone_q1\"")
        print("   (Do the same for q2 and q3)")
    
    # Label fixes
    if 'Label Suffix Fix' in fixes_by_type:
        print("\n2. Fix Button Labels")
        print("   Remove 'PDF' suffix from labels and ensure they clearly indicate content type:")
        print("   - \"FRQ Questions PDF\" → \"FRQ Questions\"")
        print("   - \"MCQ Part A PDF\" → \"MCQ Part A Questions\"")
        print("   - \"MCQ Part B PDF\" → \"MCQ Part B Questions\"")
    
    # Ternary fixes
    if 'Ternary Expression Fix' in fixes_by_type or 'Answer Ternary Fix' in fixes_by_type:
        print("\n3. Fix Ternary Expressions")
        print("   These are more complex. Look for expressions like:")
        print("   const questionTitle = quiz.quizId === \"1-capstone_q1\" ? \"...\" : ...")
        print("   const answerTitle = quiz.quizId === \"3-capstone_q1\" ? \"...\" : ...")
        print("   Replace unit IDs with 9 and update labels to clearly indicate content type")
    
    # If-block fixes
    if 'If-Block Fix' in fixes_by_type:
        print("\n4. Fix If-Block Structures")
        print("   Look for if-else if blocks that check quiz.quizId and set linkText")
        print("   Update unit IDs to 9 and ensure labels are clear and accurate")
    
    print("\nRemember: The goal is to ensure all capstone buttons clearly indicate:")
    print("1. Whether they're for FRQ, MCQ Part A, or MCQ Part B content")
    print("2. Whether they contain questions or answers")

def analyze_html_file(html_file_path):
    """
    Analyze HTML file and generate focused fixes
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"Analyzing {html_file_path} for capstone button issues...")
        print("-" * 80)
        
        # Generate focused fixes
        fixes = generate_focused_fixes(content)
        
        if not fixes:
            print("✅ No issues found that need fixing.")
            return
        
        # Display the fixes
        display_fixes(fixes)
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        import traceback
        traceback.print_exc()
        return

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
    
    analyze_html_file(index_path)

if __name__ == "__main__":
    main() 