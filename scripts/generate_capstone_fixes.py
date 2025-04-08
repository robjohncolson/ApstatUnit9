#!/usr/bin/env python3
"""
Generate Capstone Button Fixes

This script analyzes index.html and generates the necessary code changes to fix
capstone button issues:
1. Replacing incorrect unit IDs (1 and 3) with 9
2. Ensuring button labels clearly indicate content type (FRQ, MCQ Part A, MCQ Part B)

The script does NOT modify any files - it only prints the suggested changes.
"""

import os
import re
import sys
from pathlib import Path
import difflib
from pprint import pprint

def generate_button_fixes(content):
    """
    Generate fixes for capstone button issues
    """
    fixes = []
    
    # 1. Replace quiz.quizId === "1-capstone_qX" and quiz.quizId === "3-capstone_qX" with "9-capstone_qX"
    # Find all direct ID comparisons
    direct_pattern = r'(quiz\.quizId\s*===\s*")([13])(-capstone_q(\d))(")'
    
    for match in re.finditer(direct_pattern, content):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        
        # Generate the fixed version
        fixed = f'{match.group(1)}9{match.group(3)}{match.group(5)}'
        
        # Get some context
        start = max(0, match.start() - 30)
        end = min(len(content), match.end() + 30)
        context = content[start:end]
        
        fixes.append({
            'type': 'direct_comparison',
            'line': line_num,
            'original': original,
            'fixed': fixed,
            'context': context.strip()
        })
    
    # 2. Fix ternary expressions for question titles
    # Pattern for: const questionTitle/title/linkText = quiz.quizId === "X-capstone_qY" ? "..."
    title_pattern = r'(const\s+(?:questionTitle|title|linkText)\s*=\s*(?:.*?)quiz\.quizId\s*===\s*")([13])(-capstone_q1"\s*\?\s*")([^"]+)("\s*:\s*(?:.*?)quiz\.quizId\s*===\s*")([13])(-capstone_q2"\s*\?\s*")([^"]+)("\s*:[^"]*")([^"]*)'
    
    for match in re.finditer(title_pattern, content, re.DOTALL):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        
        # Generate the fixed version with proper labels
        fixed = (f'{match.group(1)}9{match.group(3)}FRQ Questions{match.group(5)}9{match.group(7)}'
                f'MCQ Part A Questions{match.group(9)}MCQ Part B Questions{match.group(10)}')
        
        # Get some context (first 100 chars)
        context_snippet = original[:100] + "..." if len(original) > 100 else original
        
        fixes.append({
            'type': 'question_title_ternary',
            'line': line_num,
            'original': context_snippet,
            'fixed': fixed[:100] + "..." if len(fixed) > 100 else fixed,
            'full_original': original,
            'full_fixed': fixed,
            'context': context_snippet  # Add context here to avoid KeyError
        })
    
    # 3. Fix ternary expressions for answer titles
    # Pattern for: const answerTitle = quiz.quizId === "X-capstone_qY" ? "..."
    answer_pattern = r'(const\s+answerTitle\s*=\s*(?:.*?)quiz\.quizId\s*===\s*")([13])(-capstone_q1"\s*\?\s*")([^"]+)("\s*:\s*(?:.*?)quiz\.quizId\s*===\s*")([13])(-capstone_q2"\s*\?\s*")([^"]+)("\s*:[^"]*")([^"]*)'
    
    for match in re.finditer(answer_pattern, content, re.DOTALL):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        
        # Generate the fixed version with proper labels
        fixed = (f'{match.group(1)}9{match.group(3)}FRQ Answers{match.group(5)}9{match.group(7)}'
                f'MCQ Part A Answers{match.group(9)}MCQ Part B Answers{match.group(10)}')
        
        # Get some context (first 100 chars)
        context_snippet = original[:100] + "..." if len(original) > 100 else original
        
        fixes.append({
            'type': 'answer_title_ternary',
            'line': line_num,
            'original': context_snippet,
            'fixed': fixed[:100] + "..." if len(fixed) > 100 else fixed,
            'full_original': original,
            'full_fixed': fixed,
            'context': context_snippet  # Add context here to avoid KeyError
        })
    
    # 4. Fix "FRQ Questions PDF" to "FRQ Questions"
    pdf_pattern = r'("FRQ Questions PDF"|"MCQ Part A PDF"|"MCQ Part B PDF")'
    
    for match in re.finditer(pdf_pattern, content):
        original = match.group(0)
        line_num = content[:match.start()].count('\n') + 1
        
        # Generate the fixed version
        if 'FRQ' in original:
            fixed = '"FRQ Questions"'
        elif 'Part A' in original:
            fixed = '"MCQ Part A Questions"'
        elif 'Part B' in original:
            fixed = '"MCQ Part B Questions"'
        
        # Get some context
        start = max(0, match.start() - 30)
        end = min(len(content), match.end() + 30)
        context = content[start:end]
        
        fixes.append({
            'type': 'pdf_label',
            'line': line_num,
            'original': original,
            'fixed': fixed,
            'context': context.strip()
        })
    
    return fixes

def format_code_block(code):
    """Format code for better readability"""
    if not code:
        return "N/A"
    lines = code.split('\n')
    if len(lines) > 5:
        return '\n'.join(lines[:4]) + '\n// ... more lines ...'
    return code

def generate_suggestions(html_file_path):
    """
    Analyze the HTML file and generate suggestions for fixes
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"Analyzing {html_file_path} for capstone button issues...")
        print("-" * 80)
        
        # Generate fixes
        fixes = generate_button_fixes(content)
        
        if not fixes:
            print("✅ No issues found that need fixing.")
            return
        
        # Group fixes by type
        fixes_by_type = {}
        for fix in fixes:
            fix_type = fix['type']
            if fix_type not in fixes_by_type:
                fixes_by_type[fix_type] = []
            fixes_by_type[fix_type].append(fix)
        
        # Print fixes by type
        for fix_type, type_fixes in fixes_by_type.items():
            print(f"\n{fix_type.replace('_', ' ').title()} Fixes ({len(type_fixes)} occurrences):")
            print("-" * 80)
            
            # Show a few examples of each type
            for i, fix in enumerate(type_fixes[:3]):
                print(f"Example {i+1} (line {fix['line']}):")
                print(f"  Original: {fix['original']}")
                print(f"  Fixed:    {fix['fixed']}")
                
                # Safely access context (now all fix types should have context)
                if 'context' in fix:
                    context_str = fix['context']
                    if len(context_str) > 60:
                        context_str = context_str[:57] + "..."
                    print(f"  Context:  {context_str}")
                print()
            
            if len(type_fixes) > 3:
                print(f"... and {len(type_fixes) - 3} more similar fixes")
        
        # Generate complete implementation sample for one instance of each type
        print("\n" + "=" * 80)
        print("IMPLEMENTATION GUIDE")
        print("=" * 80)
        
        print("\nHere are code snippets you can use as reference to fix the issues:")
        
        # Direct comparison fix
        if 'direct_comparison' in fixes_by_type and fixes_by_type['direct_comparison']:
            example = fixes_by_type['direct_comparison'][0]
            print("\n1. Replace Unit IDs in Direct Comparisons")
            print("   Find: quiz.quizId === \"1-capstone_qX\" or quiz.quizId === \"3-capstone_qX\"")
            print("   Replace with: quiz.quizId === \"9-capstone_qX\"")
            print("\n   Example:")
            print(f"   FROM: {example['original']}")
            print(f"   TO:   {example['fixed']}")
        
        # Question title ternary fix
        if 'question_title_ternary' in fixes_by_type and fixes_by_type['question_title_ternary']:
            example = fixes_by_type['question_title_ternary'][0]
            print("\n2. Fix Question Title Ternary Expressions")
            print("   Example:")
            print("\n   FROM:")
            print(f"   {format_code_block(example.get('full_original', example['original']))}")
            print("\n   TO:")
            print(f"   {format_code_block(example.get('full_fixed', example['fixed']))}")
        
        # Answer title ternary fix
        if 'answer_title_ternary' in fixes_by_type and fixes_by_type['answer_title_ternary']:
            example = fixes_by_type['answer_title_ternary'][0]
            print("\n3. Fix Answer Title Ternary Expressions")
            print("   Example:")
            print("\n   FROM:")
            print(f"   {format_code_block(example.get('full_original', example['original']))}")
            print("\n   TO:")
            print(f"   {format_code_block(example.get('full_fixed', example['fixed']))}")
        
        # Generate a complete summary
        print("\n" + "=" * 80)
        print("SUMMARY OF CHANGES NEEDED")
        print("=" * 80)
        
        total_fixes = sum(len(fixes) for fixes in fixes_by_type.values())
        print(f"\nTotal changes needed: {total_fixes}")
        
        for fix_type, type_fixes in fixes_by_type.items():
            print(f"- {fix_type.replace('_', ' ').title()}: {len(type_fixes)} occurrences")
        
        print("\nImplementation Strategy:")
        print("1. Use search functionality to find each pattern")
        print("2. Replace with the corresponding fixed version")
        print("3. Make sure unit IDs are consistently set to 9 for all capstone references")
        print("4. Ensure button labels clearly indicate content type and whether they're for questions or answers")
        
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
    
    generate_suggestions(index_path)

if __name__ == "__main__":
    main() 