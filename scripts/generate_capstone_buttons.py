#!/usr/bin/env python3
"""
Generate Improved Capstone Button Labels for index.html

This script analyzes the capstone quiz structure in index.html and generates
improved button labels that clearly indicate their destinations (FRQ, MCQ Part A, MCQ Part B).
The script does not modify any files, it only provides suggestions that can be manually
implemented.
"""

import os
import re
import sys
from pathlib import Path

def generate_button_templates():
    """
    Generate improved button templates for the capstone section of index.html
    """
    # Define templates for different quiz types
    templates = {
        "1": {
            "questions": "FRQ Questions",
            "answers": "FRQ Answers"
        },
        "2": {
            "questions": "MCQ Part A Questions",
            "answers": "MCQ Part A Answers"
        },
        "3": {
            "questions": "MCQ Part B Questions",
            "answers": "MCQ Part B Answers"
        }
    }
    
    # Generate the template code blocks
    blocks = []
    
    for q_num, labels in templates.items():
        # Generate the conditional check
        template = f"""// For quiz ID 8-capstone_q{q_num}
if (quiz.quizId === "8-capstone_q{q_num}") {{
    // For question PDF links
    const questionTitle = "{labels['questions']}";
    
    // For answer PDF links (if applicable)
    const answerTitle = "{labels['answers']}";
    
    // Example button HTML
    const buttonHtml = `
        <a href="${{quiz.questionPdf}}" target="_blank" download 
           class="flex items-center text-blue-600 hover:text-blue-800 bg-white p-2 rounded border border-blue-200 hover:bg-blue-50 flex-grow">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
            ${{questionTitle}}
        </a>`;
}}"""
        blocks.append(template)
    
    # Generate the ternary conditional template
    ternary_template = """
// Consolidated ternary operator pattern for question titles
const questionTitle = quiz.quizId === "8-capstone_q1" ? "FRQ Questions" :
                     quiz.quizId === "8-capstone_q2" ? "MCQ Part A Questions" :
                     "MCQ Part B Questions";

// Consolidated ternary operator pattern for answer titles
const answerTitle = quiz.quizId === "8-capstone_q1" ? "FRQ Answers" :
                   quiz.quizId === "8-capstone_q2" ? "MCQ Part A Answers" :
                   "MCQ Part B Answers";
"""
    blocks.append(ternary_template)
    
    return blocks

def analyze_index_html(html_file_path):
    """
    Analyze the index.html file and suggest improved button labels.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print(f"Analyzing capstone buttons in {html_file_path}...")
        print("-" * 80)
        
        # Find the capstone quiz IDs and their descriptions in the JavaScript data structure
        capstone_pattern = r'id:\s*"8-capstone",.*?quizzes:\s*\[(.*?)\].*?isCapstone:\s*true'
        match = re.search(capstone_pattern, content, re.DOTALL)
        
        if not match:
            print("❌ Could not find the capstone section in the JavaScript data structure.")
            return
        
        quizzes_section = match.group(1)
        
        # Extract each quiz ID and its files
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
        
        print(f"✅ Found {len(quiz_info)} capstone quiz items")
        
        # Identify problematic button labels
        button_label_issues = []
        
        # Check if any buttons use hardcoded old unit IDs
        hardcoded_pattern = r'quiz\.quizId === "(\d)-capstone_q(\d)"'
        hardcoded_matches = set(re.findall(hardcoded_pattern, content))
        
        for unit_id, q_num in hardcoded_matches:
            if unit_id != '8':
                button_label_issues.append(f"Hardcoded unit ID '{unit_id}' instead of '8' for quiz {q_num}")
        
        # Generate improved button templates
        improved_templates = generate_button_templates()
        
        print("\n📋 Current Quiz Information:")
        for quiz in quiz_info:
            print(f"  - ID: {quiz['id']}")
            print(f"    Question PDF: {quiz['q_pdf']}")
            print(f"    Answer PDF: {quiz['a_pdf'] or 'None'}")
            print()
        
        if button_label_issues:
            print("\n❌ Button Label Issues:")
            for issue in button_label_issues:
                print(f"  - {issue}")
        
        print("\n💡 Improved Button Label Templates:")
        for i, template in enumerate(improved_templates):
            print(f"\nTemplate {i+1}:")
            print("```javascript")
            print(template)
            print("```")
        
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
    
    analyze_index_html(index_path)

if __name__ == "__main__":
    main() 