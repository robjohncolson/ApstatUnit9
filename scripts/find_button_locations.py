#!/usr/bin/env python3
"""
Find Button Locations in index.html

This script locates all the places in index.html where capstone button issues exist,
providing line numbers and the context to help quickly find and fix them.
"""

import os
import re
import sys
from pathlib import Path

def find_button_issues(file_path):
    """
    Find all locations in index.html with button labeling issues.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
            
        total_lines = len(content)
        print(f"Analyzing {file_path}...")
        print(f"File has {total_lines} lines")
        print("-" * 80)
        
        # Search patterns for problematic button code
        patterns = [
            r'quiz\.quizId === "1-capstone_q\d"',  # Unit 1 references
            r'quiz\.quizId === "3-capstone_q\d"',  # Unit 3 references
            r'const \w+Title = quiz\.quizId ===.*?capstone',  # Ternary expressions
            r'linkText = .*?capstone',  # Link text assignments
            r'title = .*?capstone'      # Title assignments
        ]
        
        # Store all findings by line number
        findings = {}
        
        for i, line in enumerate(content):
            line_num = i + 1
            for pattern in patterns:
                if re.search(pattern, line):
                    findings[line_num] = {
                        'line': line.strip(),
                        'pattern': pattern
                    }
        
        # Display results
        if findings:
            print(f"Found {len(findings)} instances that need to be fixed:")
            print("\n" + "=" * 80)
            
            # Group findings in chunks of nearby lines
            groups = []
            current_group = []
            prev_line = None
            
            for line_num in sorted(findings.keys()):
                if prev_line is None or line_num - prev_line <= 10:
                    # Add to current group if within 10 lines of previous match
                    current_group.append(line_num)
                else:
                    # Start a new group if more than 10 lines from previous match
                    groups.append(current_group)
                    current_group = [line_num]
                prev_line = line_num
            
            if current_group:
                groups.append(current_group)
            
            # Display each group with context
            for i, group in enumerate(groups):
                start_line = max(1, min(group) - 3)
                end_line = min(total_lines, max(group) + 3)
                
                print(f"\nIssue Group {i+1}: Lines {start_line}-{end_line}")
                print("-" * 80)
                
                for j in range(start_line - 1, end_line):
                    line_num = j + 1
                    line = content[j].rstrip('\n')
                    
                    if line_num in findings:
                        print(f"{line_num:4d} ➤ {line}")
                    else:
                        print(f"{line_num:4d}   {line}")
                
                print("=" * 80)
            
            print("\nSuggested fixes:")
            print("1. Replace all unit IDs '1' and '3' with '8'")
            print("2. Update button labels to clearly indicate their content:")
            print("   - For quiz_id 8-capstone_q1: 'FRQ Questions/Answers'")
            print("   - For quiz_id 8-capstone_q2: 'MCQ Part A Questions/Answers'")
            print("   - For quiz_id 8-capstone_q3: 'MCQ Part B Questions/Answers'")
            
        else:
            print("✅ No button labeling issues found.")
            
    except Exception as e:
        print(f"Error analyzing file: {e}")
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
    
    find_button_issues(index_path)

if __name__ == "__main__":
    main() 