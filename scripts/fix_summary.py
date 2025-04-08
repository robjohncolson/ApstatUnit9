#!/usr/bin/env python3
"""
Capstone Button Fix Summary

This script provides a comprehensive summary of all recommended fixes for
the capstone button issues in index.html. It displays a concise, organized list
of changes that need to be made manually.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

def get_file_content(file_path):
    """Read the content of the index.html file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def extract_capstone_data(content):
    """Extract the capstone data structure from the JavaScript."""
    capstone_pattern = r'id:\s*"8-capstone",[^{]*?description:\s*"([^"]*)",[^{]*?quizzes:\s*\[(.*?)\],[^}]*?isCapstone:\s*true'
    match = re.search(capstone_pattern, content, re.DOTALL)
    
    if not match:
        return None, []
    
    description = match.group(1)
    quizzes_section = match.group(2)
    
    # Extract quiz IDs and PDFs
    quiz_info = []
    quiz_blocks = re.findall(r'{(.*?)}', quizzes_section, re.DOTALL)
    
    for block in quiz_blocks:
        quiz_id_match = re.search(r'quizId:\s*"(8-capstone_q\d)"', block)
        q_pdf_match = re.search(r'questionPdf:\s*"([^"]*)"', block)
        a_pdf_match = re.search(r'answersPdf:\s*"([^"]*)"', block)
        
        if quiz_id_match:
            quiz_info.append({
                'id': quiz_id_match.group(1),
                'q_pdf': q_pdf_match.group(1) if q_pdf_match else None,
                'a_pdf': a_pdf_match.group(1) if a_pdf_match and a_pdf_match.group(1) != 'null' else None
            })
    
    return description, quiz_info

def find_issues(content):
    """Find all issues that need fixing."""
    # Find hardcoded unit ID patterns
    problems = defaultdict(list)
    
    # 1. Find hardcoded quiz ID references
    pattern1 = r'quiz\.quizId === "(\d)-capstone_q(\d)"'
    for match in re.finditer(pattern1, content):
        unit_id = match.group(1)
        quiz_num = match.group(2)
        if unit_id != '8':
            problems['unit_id_mismatch'].append({
                'pattern': match.group(0),
                'unit': unit_id,
                'quiz': quiz_num,
                'fix': f'quiz.quizId === "8-capstone_q{quiz_num}"'
            })
    
    # 2. Find ternary operators with hardcoded values
    patterns = [
        # Question title ternary pattern
        r'const \w+Title = quiz\.quizId === "(\d)-capstone_q1" \? "([^"]+)" :.*?quiz\.quizId === "(\d)-capstone_q2" \? "([^"]+)"',
        # Answer title ternary pattern
        r'const answerTitle = .*?quiz\.quizId === "(\d)-capstone_q1" \? "([^"]+)" :.*?quiz\.quizId === "(\d)-capstone_q2" \? "([^"]+)"'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            if "question" in match.group(0).lower():
                problems['ternary_question'].append({
                    'pattern': match.group(0),
                    'fix': 'const questionTitle = quiz.quizId === "8-capstone_q1" ? "FRQ Questions" :\n'
                           '                     quiz.quizId === "8-capstone_q2" ? "MCQ Part A Questions" :\n'
                           '                     "MCQ Part B Questions"'
                })
            else:
                problems['ternary_answer'].append({
                    'pattern': match.group(0),
                    'fix': 'const answerTitle = quiz.quizId === "8-capstone_q1" ? "FRQ Answers" :\n'
                           '                   quiz.quizId === "8-capstone_q2" ? "MCQ Part A Answers" :\n'
                           '                   "MCQ Part B Answers"'
                })
    
    # 3. Find title assignments
    title_patterns = [
        r'(const title = )quiz\.quizId === "(\d)-capstone_q1" \? "([^"]+)" :[^"]+"(\d)-capstone_q2" \? "([^"]+)"',
        r'(const linkText = ).*?quiz\.quizId === "(\d)-capstone_q1" \? "([^"]+)" :[^"]+"(\d)-capstone_q2" \? "([^"]+)"'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            problems['title_assignment'].append({
                'pattern': match.group(0),
                'fix': 'const title = quiz.quizId === "8-capstone_q1" ? "FRQ Questions" :\n'
                       '              quiz.quizId === "8-capstone_q2" ? "MCQ Part A Questions" :\n'
                       '              "MCQ Part B Questions"'
            })
    
    return problems

def display_fix_summary(file_path):
    """Display a summary of all fixes needed."""
    content = get_file_content(file_path)
    if not content:
        return
    
    print(f"Analyzing {file_path}...")
    print("-" * 80)
    
    # Get capstone information
    capstone_description, quiz_info = extract_capstone_data(content)
    if not capstone_description:
        print("❌ Could not find capstone data in the file.")
        return
    
    print(f"Capstone section: '{capstone_description}'")
    print(f"Found {len(quiz_info)} quiz items:")
    for quiz in quiz_info:
        print(f"  - {quiz['id']}: Question PDF: {quiz['q_pdf']}, Answer PDF: {quiz['a_pdf'] or 'None'}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDED FIXES")
    print("=" * 80)
    
    # Find issues
    issues = find_issues(content)
    
    # 1. Unit ID fixes
    if issues['unit_id_mismatch']:
        print("\n1️⃣ UNIT ID REPLACEMENTS:")
        print("-" * 40)
        for i, issue in enumerate(issues['unit_id_mismatch']):
            print(f"[{i+1}] Find:    {issue['pattern']}")
            print(f"    Replace: {issue['fix']}")
            print()
    
    # 2. Ternary operator fixes
    if issues['ternary_question'] or issues['ternary_answer']:
        print("\n2️⃣ TERNARY EXPRESSION REPLACEMENTS:")
        print("-" * 40)
        
        if issues['ternary_question']:
            print("\nFor Question Title Pattern:")
            print("=" * 30)
            print("Replace with:")
            print("```")
            print(issues['ternary_question'][0]['fix'])
            print("```")
            
        if issues['ternary_answer']:
            print("\nFor Answer Title Pattern:")
            print("=" * 30)
            print("Replace with:")
            print("```")
            print(issues['ternary_answer'][0]['fix'])
            print("```")
    
    # 3. Other title assignments
    if issues['title_assignment']:
        print("\n3️⃣ TITLE ASSIGNMENT REPLACEMENTS:")
        print("-" * 40)
        for i, issue in enumerate(issues['title_assignment']):
            print(f"[{i+1}] Find similar pattern to:")
            print(f"    {issue['pattern'][:80]}...")
            print("    Replace with:")
            print("    ```")
            print(f"    {issue['fix']}")
            print("    ```")
            print()
    
    # Summary of button labels
    print("\n4️⃣ RECOMMENDED BUTTON LABELS:")
    print("-" * 40)
    print("Use these labels for the capstone buttons:")
    print("  • For 8-capstone_q1:")
    print("    - Questions: 'FRQ Questions'")
    print("    - Answers:   'FRQ Answers'")
    print()
    print("  • For 8-capstone_q2:")
    print("    - Questions: 'MCQ Part A Questions'")
    print("    - Answers:   'MCQ Part A Answers'")
    print()
    print("  • For 8-capstone_q3:")
    print("    - Questions: 'MCQ Part B Questions'")
    print("    - Answers:   'MCQ Part B Answers'")
    
    print("\n" + "=" * 80)
    print("These changes will ensure that the buttons in the capstone section")
    print("correctly match their destinations and provide clear guidance to users.")
    print("=" * 80)

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
    
    display_fix_summary(index_path)

if __name__ == "__main__":
    main() 