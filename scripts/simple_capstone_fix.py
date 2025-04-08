#!/usr/bin/env python3
"""
Simple Capstone Button Fix Generator

This script focuses on the simplest and most critical fixes needed for the capstone buttons:
1. Replacing unit IDs (1 and 3 with 9)
2. Ensuring consistent button labels

It deliberately avoids complex regex patterns that might cause the script to stall.
"""

import os
import re
from pathlib import Path

def find_unit_id_issues(content):
    """Find all instances where unit IDs need to be changed from 1/3 to 9"""
    pattern = r'quiz\.quizId\s*===\s*"([13])-capstone_q(\d)"'
    matches = re.finditer(pattern, content)
    
    issues = []
    for match in re.finditer(pattern, content):
        line_num = content[:match.start()].count('\n') + 1
        original = match.group(0)
        unit_id = match.group(1)
        quiz_num = match.group(2)
        
        # Create the replacement
        replacement = original.replace(f'"{unit_id}-capstone', '"9-capstone')
        
        issues.append({
            'line': line_num,
            'original': original,
            'replacement': replacement,
            'unit_id': unit_id,
            'quiz_num': quiz_num
        })
    
    return issues

def find_label_issues(content):
    """Find instances where button labels need to be fixed"""
    patterns = [
        (r'"FRQ Questions PDF"', '"FRQ Questions"'),
        (r'"MCQ Part A PDF"', '"MCQ Part A Questions"'),
        (r'"MCQ Part B PDF"', '"MCQ Part B Questions"')
    ]
    
    issues = []
    for pattern, replacement in patterns:
        for match in re.finditer(pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            original = match.group(0)
            
            issues.append({
                'line': line_num,
                'original': original,
                'replacement': replacement
            })
    
    return issues

def analyze_simple_fixes(html_file_path):
    """Generate simple fixes for the capstone buttons"""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print(f"Analyzing {html_file_path} for simple capstone button fixes...")
        print("-" * 80)
        
        # Find unit ID issues
        unit_id_issues = find_unit_id_issues(content)
        print(f"Found {len(unit_id_issues)} instances where unit IDs need to be changed from 1/3 to 9")
        
        # Find label issues
        label_issues = find_label_issues(content)
        print(f"Found {len(label_issues)} instances where button labels need to be improved")
        
        # Display example fixes
        if unit_id_issues:
            print("\nUnit ID Fix Examples:")
            for i, issue in enumerate(unit_id_issues[:5]):
                print(f"  {i+1}. Line {issue['line']}: {issue['original']} → {issue['replacement']}")
            
            if len(unit_id_issues) > 5:
                print(f"  ... and {len(unit_id_issues) - 5} more similar fixes")
        
        if label_issues:
            print("\nLabel Fix Examples:")
            for i, issue in enumerate(label_issues[:5]):
                print(f"  {i+1}. Line {issue['line']}: {issue['original']} → {issue['replacement']}")
            
            if len(label_issues) > 5:
                print(f"  ... and {len(label_issues) - 5} more similar fixes")
        
        # Count quiz IDs by unit
        quiz_counts = {}
        for issue in unit_id_issues:
            unit_id = issue['unit_id']
            quiz_num = issue['quiz_num']
            key = f"{unit_id}-capstone_q{quiz_num}"
            quiz_counts[key] = quiz_counts.get(key, 0) + 1
        
        if quiz_counts:
            print("\nQuiz ID Counts:")
            for quiz_id, count in sorted(quiz_counts.items()):
                print(f"  {quiz_id}: {count} occurrences")
        
        # Implementation guide
        print("\n" + "=" * 80)
        print("SIMPLE IMPLEMENTATION GUIDE")
        print("=" * 80)
        print("\nTo fix the most critical issues:")
        
        print("\n1. Replace Incorrect Unit IDs")
        print("   Search for: quiz.quizId === \"1-capstone_q1\" or quiz.quizId === \"3-capstone_q1\"")
        print("   Replace with: quiz.quizId === \"9-capstone_q1\"")
        print("   (Do the same for q2 and q3)")
        
        print("\n2. Fix Button Labels")
        print("   Search for: \"FRQ Questions PDF\"")
        print("   Replace with: \"FRQ Questions\"")
        print("   \nSearch for: \"MCQ Part A PDF\"")
        print("   Replace with: \"MCQ Part A Questions\"")
        print("   \nSearch for: \"MCQ Part B PDF\"")
        print("   Replace with: \"MCQ Part B Questions\"")
        
        print("\nRemember: The goal is to ensure all capstone buttons clearly indicate:")
        print("1. Whether they're for FRQ, MCQ Part A, or MCQ Part B content")
        print("2. Whether they contain questions or answers")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        import traceback
        traceback.print_exc()

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
    
    analyze_simple_fixes(index_path)

if __name__ == "__main__":
    main() 