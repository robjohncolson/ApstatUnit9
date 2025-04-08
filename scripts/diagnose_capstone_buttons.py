#!/usr/bin/env python3
"""
Diagnose Capstone Button Issues in index.html

This script analyzes the capstone buttons in index.html to check if they correctly
match their destinations (FRQ answers, MCQ Part A answers, etc.). It does not modify
any files - it only provides diagnostic information.
"""

import os
import re
import sys
from pathlib import Path
import json

def analyze_capstone_section(content):
    """
    Analyze the capstone section in the JavaScript data structure.
    """
    # Extract the capstone data structure for unit 9
    capstone_pattern = r'id:\s*"9-capstone",[^{]*?description:\s*"([^"]*)",[^{]*?quizzes:\s*\[(.*?)\],[^}]*?isCapstone:\s*true'
    match = re.search(capstone_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Could not find the Unit 9 capstone section in the JavaScript data structure.")
        return None, []
        
    capstone_description = match.group(1)
    quizzes_section = match.group(2)
    
    print(f"✅ Found Unit 9 capstone section: '{capstone_description}'")
    
    # Extract quiz information
    quiz_blocks = re.findall(r'{([^{}]+)}', quizzes_section)
    quiz_info = []
    
    for block in quiz_blocks:
        quiz_id_match = re.search(r'quizId:\s*"(9-capstone_q\d)"', block)
        question_pdf_match = re.search(r'questionPdf:\s*"([^"]*)"', block)
        answers_pdf_match = re.search(r'answersPdf:\s*"([^"]*)"', block)
        
        if quiz_id_match:
            quiz_data = {
                'id': quiz_id_match.group(1),
                'question_pdf': question_pdf_match.group(1) if question_pdf_match else None,
                'answers_pdf': answers_pdf_match.group(1) if answers_pdf_match else None
            }
            quiz_info.append(quiz_data)
    
    if quiz_info:
        print(f"✅ Found {len(quiz_info)} capstone quiz items.")
        
        # Determine expected labels
        for quiz in quiz_info:
            q_num = quiz['id'].split('_q')[1]
            if q_num == '1':
                quiz['expected_q_label'] = "FRQ Questions"
                quiz['expected_a_label'] = "FRQ Answers"
            elif q_num == '2':
                quiz['expected_q_label'] = "MCQ Part A Questions"
                quiz['expected_a_label'] = "MCQ Part A Answers"
            elif q_num == '3':
                quiz['expected_q_label'] = "MCQ Part B Questions"
                quiz['expected_a_label'] = "MCQ Part B Answers"
    
    return capstone_description, quiz_info

def find_button_issues(content, quiz_info):
    """
    Find all button labeling issues in the HTML content.
    """
    issues = []
    
    if not quiz_info:
        return issues
    
    # Pattern 1: Check direct quiz.quizId comparisons
    # e.g., if (quiz.quizId === "3-capstone_q1") { linkText = "FRQ Questions"; }
    direct_pattern = r'(quiz\.quizId\s*===\s*")(\d)(-capstone_q(\d))(")'
    
    for match in re.finditer(direct_pattern, content):
        unit_id = match.group(2)
        q_num = match.group(4)
        
        if unit_id != '9':
            issue = {
                'type': 'unit_id',
                'location': f"Line near {match.group(0)}",
                'issue': f"Incorrect unit ID: {unit_id} (should be 9)",
                'q_num': q_num,
                'original': match.group(0),
                'suggested_fix': f'{match.group(1)}9{match.group(3)}{match.group(5)}'
            }
            issues.append(issue)
    
    # Pattern 2: Check ternary expressions for question titles
    question_title_pattern = r'(const\s+(?:questionTitle|title|linkText)\s*=.*?quiz\.quizId\s*===\s*")(\d)(-capstone_q1"\s*\?\s*")([^"]+)(")'
    
    for match in re.finditer(question_title_pattern, content, flags=re.DOTALL):
        unit_id = match.group(2)
        label = match.group(4)
        expected_label = "FRQ Questions"
        
        if unit_id != '9':
            issue = {
                'type': 'title_unit_id',
                'location': f"Line near {match.group(0)[:50]}...",
                'issue': f"Incorrect unit ID in title ternary: {unit_id} (should be 9)",
                'q_num': '1',
                'original': match.group(0)[:50] + "...",
                'suggested_fix': f'{match.group(1)}9{match.group(3)}{expected_label}{match.group(5)}'
            }
            issues.append(issue)
        
        if expected_label.lower() not in label.lower():
            issue = {
                'type': 'title_label',
                'location': f"Line near {match.group(0)[:50]}...",
                'issue': f"Unclear label: '{label}' (should indicate {expected_label})",
                'q_num': '1',
                'original': match.group(0)[:50] + "...",
                'suggested_fix': f'{match.group(1)}{unit_id}{match.group(3)}{expected_label}{match.group(5)}'
            }
            issues.append(issue)
    
    # Pattern 3: Check ternary expressions for answer titles
    answer_title_pattern = r'(const\s+answerTitle\s*=.*?quiz\.quizId\s*===\s*")(\d)(-capstone_q1"\s*\?\s*")([^"]+)(")'
    
    for match in re.finditer(answer_title_pattern, content, flags=re.DOTALL):
        unit_id = match.group(2)
        label = match.group(4)
        expected_label = "FRQ Answers"
        
        if unit_id != '9':
            issue = {
                'type': 'answer_unit_id',
                'location': f"Line near {match.group(0)[:50]}...",
                'issue': f"Incorrect unit ID in answer ternary: {unit_id} (should be 9)",
                'q_num': '1',
                'original': match.group(0)[:50] + "...",
                'suggested_fix': f'{match.group(1)}9{match.group(3)}{expected_label}{match.group(5)}'
            }
            issues.append(issue)
        
        if expected_label.lower() not in label.lower():
            issue = {
                'type': 'answer_label',
                'location': f"Line near {match.group(0)[:50]}...",
                'issue': f"Unclear label: '{label}' (should indicate {expected_label})",
                'q_num': '1',
                'original': match.group(0)[:50] + "...",
                'suggested_fix': f'{match.group(1)}{unit_id}{match.group(3)}{expected_label}{match.group(5)}'
            }
            issues.append(issue)
    
    return issues

def visualize_button_mapping(quiz_info, content):
    """
    Create a visual representation of the button mappings for better understanding.
    """
    # Get all button labels associated with each quiz ID
    button_labels = {}
    
    for quiz in quiz_info:
        quiz_id = quiz['id']
        q_num = quiz_id.split('_q')[1]
        
        # Search for all labels associated with this quiz ID
        pattern = rf'quiz\.quizId\s*===\s*"\d-capstone_q{q_num}"[^"]*?"([^"]+)"'
        labels = re.findall(pattern, content)
        
        button_labels[quiz_id] = labels
    
    # Display the mappings
    print("\n=== BUTTON MAPPING VISUALIZATION ===")
    print("This shows how buttons are currently labeled in the HTML")
    print("-" * 50)
    
    for quiz in quiz_info:
        quiz_id = quiz['id']
        labels = button_labels.get(quiz_id, [])
        q_num = quiz_id.split('_q')[1]
        
        if q_num == '1':
            category = "FRQ"
        elif q_num == '2':
            category = "MCQ Part A"
        elif q_num == '3':
            category = "MCQ Part B"
        else:
            category = f"Quiz {q_num}"
        
        print(f"\nQuiz ID: {quiz_id} ({category})")
        print(f"  - Question PDF: {quiz['question_pdf']}")
        print(f"  - Answers PDF: {quiz['answers_pdf']}")
        print(f"  - Expected Question Label: {quiz.get('expected_q_label', 'Unknown')}")
        print(f"  - Expected Answer Label: {quiz.get('expected_a_label', 'Unknown')}")
        print(f"  - Current Labels in HTML: {', '.join(labels) if labels else 'No explicit labels found'}")

def diagnose_capstone_buttons(html_file_path):
    """
    Analyze the index.html file for capstone button issues.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print(f"Analyzing capstone buttons in {html_file_path}...")
        print("-" * 80)
        
        # First, analyze the capstone section in the JavaScript data
        capstone_description, quiz_info = analyze_capstone_section(content)
        
        if not quiz_info:
            return
        
        # Check for all button labeling issues
        issues = find_button_issues(content, quiz_info)
        
        # Create a visual representation of the button mappings
        visualize_button_mapping(quiz_info, content)
        
        # Report findings
        if issues:
            print("\n❌ Found button labeling issues:")
            
            # Group issues by type
            issues_by_type = {}
            for issue in issues:
                issue_type = issue['type']
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append(issue)
            
            for issue_type, type_issues in issues_by_type.items():
                print(f"\n  Issue Type: {issue_type.replace('_', ' ').title()}")
                for i, issue in enumerate(type_issues[:3]):  # Show max 3 issues of each type
                    print(f"    {i+1}. {issue['issue']}")
                    print(f"       Found in: {issue['location']}")
                if len(type_issues) > 3:
                    print(f"       ... and {len(type_issues) - 3} more similar issues")
            
            print("\n💡 Recommendations:")
            print("  1. Update all unit IDs to use 9 instead of other values")
            print("  2. Ensure button labels clearly indicate their content type:")
            print("     - For quiz_id 9-capstone_q1: Use 'FRQ Questions/Answers'")
            print("     - For quiz_id 9-capstone_q2: Use 'MCQ Part A Questions/Answers'")
            print("     - For quiz_id 9-capstone_q3: Use 'MCQ Part B Questions/Answers'")
            
            # Suggest how to fix with existing scripts
            print("\n🔧 How to Fix:")
            print("  Run these diagnostic-only scripts from the scripts/ directory:")
            print("  1. python find_button_locations.py - Find all occurrences")
            print("  2. python suggest_capstone_fixes.py - Get specific code snippets")
        else:
            print("\n✅ No button labeling issues found!")
            
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
    
    diagnose_capstone_buttons(index_path)

if __name__ == "__main__":
    main()
