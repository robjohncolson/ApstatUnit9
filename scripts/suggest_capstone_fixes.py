#!/usr/bin/env python3
"""
Suggest Specific Capstone Button Fixes for index.html

This script analyzes index.html, identifies specific locations where capstone button
labels need to be updated, and provides exact code snippets that can be used as replacements.
The script does not modify any files, it only provides suggestions that can be manually implemented.
"""

import os
import re
import sys
from pathlib import Path
import difflib

def find_replacements(content):
    """
    Find specific code blocks that need to be replaced and suggest replacements.
    """
    replacements = []
    
    # Look for hardcoded capstone quiz ID references with wrong unit numbers
    # Pattern: quiz.quizId === "1-capstone_q1" or quiz.quizId === "3-capstone_q1" etc.
    hardcoded_pattern = r'(quiz\.quizId === ")(\d)(-capstone_q(\d))(")[^}]+?([^"]*)"'
    
    # Find all instances of this pattern
    for match in re.finditer(hardcoded_pattern, content):
        full_match = match.group(0)
        prefix = match.group(1)
        unit_id = match.group(2)
        suffix = match.group(3)
        q_num = match.group(4)
        quote = match.group(5)
        label = match.group(6)
        
        if unit_id != '8':
            # Create the replacement with correct unit number and appropriate label
            if q_num == '1':
                new_label = "FRQ Questions" if "question" in full_match.lower() else "FRQ Answers"
            elif q_num == '2':
                new_label = "MCQ Part A Questions" if "question" in full_match.lower() else "MCQ Part A Answers"
            elif q_num == '3':
                new_label = "MCQ Part B Questions" if "question" in full_match.lower() else "MCQ Part B Answers"
            else:
                new_label = label  # Keep the original if it's not q1, q2, or q3
                
            original = f'{prefix}{unit_id}{suffix}{quote}{label}'
            replacement = f'{prefix}8{suffix}{quote}{new_label}'
            
            # Get surrounding context for easier identification
            start = max(0, match.start() - 40)
            end = min(len(content), match.end() + 40)
            context = content[start:end]
            
            replacements.append({
                'original': original,
                'replacement': replacement,
                'context': context,
                'description': f"Replace unit '{unit_id}' with '8' and update label for quiz {q_num}"
            })
    
    # Look for ternary expressions that need updating
    ternary_pattern = r'(const \w+Title = quiz\.quizId === ")(\d)(-capstone_q1)" \? "([^"]+)" :[^"]+"(\d)(-capstone_q2)" \? "([^"]+)" :[^"]+"(\d)(-capstone_q3)" \? "([^"]+)"'
    
    for match in re.finditer(ternary_pattern, content):
        original = match.group(0)
        const_part = match.group(1)
        
        # Since this is a complete ternary expression, we'll suggest a full replacement
        type_hint = "question" if "question" in original.lower() else "answer"
        
        if type_hint == "question":
            replacement = f'{const_part}8-capstone_q1" ? "FRQ Questions" :\n' + \
                         f'                     quiz.quizId === "8-capstone_q2" ? "MCQ Part A Questions" :\n' + \
                         f'                     "MCQ Part B Questions"'
        else:
            replacement = f'{const_part}8-capstone_q1" ? "FRQ Answers" :\n' + \
                         f'                   quiz.quizId === "8-capstone_q2" ? "MCQ Part A Answers" :\n' + \
                         f'                   "MCQ Part B Answers"'
        
        # Get surrounding context
        start = max(0, match.start() - 40)
        end = min(len(content), match.end() + 40)
        context = content[start:end]
        
        replacements.append({
            'original': original,
            'replacement': replacement,
            'context': context,
            'description': f"Update entire ternary expression for {type_hint} titles"
        })
    
    return replacements

def suggest_fixes(html_file_path):
    """
    Analyze the index.html file and suggest specific fixes for capstone button labels.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print(f"Analyzing capstone buttons in {html_file_path}...")
        print("-" * 80)
        
        # Find all button label code that needs to be replaced
        replacements = find_replacements(content)
        
        if not replacements:
            print("✅ No button label issues found that need fixing.")
            return
        
        print(f"Found {len(replacements)} instances that need updating:")
        
        for i, replacement in enumerate(replacements):
            print(f"\n[{i+1}] {replacement['description']}")
            print("\nContext:")
            print(f"...{replacement['context']}...")
            
            print("\nChange From:")
            print(replacement['original'])
            
            print("\nChange To:")
            print(replacement['replacement'])
            
            # Generate a diff
            diff = difflib.unified_diff(
                replacement['original'].splitlines(),
                replacement['replacement'].splitlines(),
                lineterm='',
                n=0
            )
            
            print("\nDiff:")
            for line in diff:
                print(line)
            
            print("-" * 80)
        
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
    
    suggest_fixes(index_path)

if __name__ == "__main__":
    main() 