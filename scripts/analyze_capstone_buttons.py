#!/usr/bin/env python3
"""
Analyze Capstone Buttons in index.html

This script analyzes the capstone section of index.html to identify if button labels
correctly match their destinations. It scans for instances where buttons should properly
indicate whether they link to FRQ answers or MCQ parts.

The script does not modify any files, it only provides analysis and suggestions.
"""

import os
import re
import sys
from pathlib import Path

def analyze_capstone_buttons(html_file_path):
    """
    Analyze the capstone section of the index.html file and provide suggestions
    for improving button labels.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print(f"Analyzing capstone buttons in {html_file_path}...")
        print("-" * 80)
        
        # Extract the capstone data structure
        capstone_pattern = r'id:\s*"8-capstone",[^{]*?description:\s*"([^"]*)",[^{]*?quizzes:\s*\[(.*?)\],[^}]*?isCapstone:\s*true'
        match = re.search(capstone_pattern, content, re.DOTALL)
        
        if not match:
            print("❌ Could not find the capstone section in the JavaScript data structure.")
            return
            
        capstone_description = match.group(1)
        quizzes_section = match.group(2)
        
        print(f"✅ Found capstone section: '{capstone_description}'")
        
        # Extract quiz information
        quiz_pattern = r'quizId:\s*"(8-capstone_q\d)"'
        quiz_ids = re.findall(quiz_pattern, quizzes_section)
        
        print(f"✅ Found {len(quiz_ids)} capstone quiz IDs: {', '.join(quiz_ids)}")
        
        # Analyze button labeling in HTML
        button_issues = []
        
        # Check the capstone quiz button labeling
        for quiz_id in quiz_ids:
            q_num = quiz_id.split('_q')[1]
            
            if q_num == '1':
                expected_label = "FRQ"
            elif q_num == '2':
                expected_label = "MCQ Part A"
            elif q_num == '3':
                expected_label = "MCQ Part B"
            else:
                expected_label = f"Quiz {q_num}"
            
            # Look for hardcoded values that might not match the expected patterns
            hardcoded_pattern = rf'quiz\.quizId === "(\d-capstone_q{q_num})"[^"]*?"([^"]*?)"'
            hardcoded_matches = re.findall(hardcoded_pattern, content)
            
            for unit_id, label in hardcoded_matches:
                if unit_id != '8' and ('capstone' in label.lower() or expected_label.lower() in label.lower()):
                    button_issues.append({
                        'quiz_id': quiz_id,
                        'issue': f"Hardcoded unit ID '{unit_id}' instead of '8' for {expected_label}",
                        'line_hint': f"quiz.quizId === \"{unit_id}-capstone_q{q_num}\""
                    })
                
                if expected_label.lower() not in label.lower():
                    button_issues.append({
                        'quiz_id': quiz_id,
                        'issue': f"Button label '{label}' doesn't clearly indicate it's for {expected_label}",
                        'line_hint': f"quiz.quizId === \"{unit_id}-capstone_q{q_num}\"" 
                    })
        
        # Analyze template string usage
        template_pattern = r'quiz\.quizId === "(\d-capstone_q\d)"'
        template_matches = re.findall(template_pattern, content)
        
        for template_match in template_matches:
            if not template_match.startswith('8'):
                button_issues.append({
                    'quiz_id': 'general',
                    'issue': f"Template using unit ID '{template_match[0]}' instead of '8'",
                    'line_hint': f"quiz.quizId === \"{template_match}\""
                })
        
        # Report findings
        if button_issues:
            print("\n❌ Found button labeling issues:")
            for issue in button_issues:
                print(f"  - {issue['issue']}")
                print(f"    Near: {issue['line_hint']}")
            
            print("\n💡 Suggested Fixes:")
            print("  1. Update hardcoded quiz IDs to use unit 8 instead of other units")
            print("  2. Ensure all button labels clearly indicate their destination:")
            print("     - For quiz_id 8-capstone_q1: Use 'FRQ Questions/Answers'")
            print("     - For quiz_id 8-capstone_q2: Use 'MCQ Part A Questions/Answers'")
            print("     - For quiz_id 8-capstone_q3: Use 'MCQ Part B Questions/Answers'")
            print("  3. Check template literals to ensure they use the proper quiz IDs")
        else:
            print("\n✅ No button labeling issues found.")
            
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
    
    analyze_capstone_buttons(index_path)

if __name__ == "__main__":
    main() 