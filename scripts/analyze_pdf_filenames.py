#!/usr/bin/env python3
"""
Analyze PDF Filenames in index.html

This script analyzes the PDF filenames referenced in index.html to help understand
the relationship between button labels and their destinations. It extracts PDF links, 
categorizes them, and identifies which buttons link to which types of content.

The script does NOT modify any files - it only provides analysis.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote
from collections import defaultdict

def extract_pdf_urls(content):
    """
    Extract all PDF URLs from the HTML content.
    """
    pdf_pattern = r'href="([^"]*\.pdf)"'
    pdf_urls = re.findall(pdf_pattern, content)
    return pdf_urls

def extract_button_context(content):
    """
    Extract buttons with PDF links and their surrounding context.
    """
    # Pattern to match <a> tags with PDF links
    button_pattern = r'<a\s+href="([^"]*\.pdf)"[^>]*>((?:(?!</a>).)*?)</a>'
    
    buttons = []
    for match in re.finditer(button_pattern, content, re.DOTALL):
        href = match.group(1)
        button_html = match.group(2)
        
        # Clean up the button text (remove HTML tags)
        button_text = re.sub(r'<[^>]*>', '', button_html).strip()
        
        # Get surrounding context
        context_start = max(0, match.start() - 200)
        context_end = min(len(content), match.end() + 200)
        context = content[context_start:match.start()] + "[BUTTON]" + content[match.end():context_end]
        
        # Check if this is in a capstone section
        is_capstone = 'capstone' in context.lower() or 'capstone' in button_text.lower()
        
        # Try to determine the quiz ID
        quiz_id = None
        for i in range(1, 4):
            if f"capstone_q{i}" in context:
                quiz_id = f"capstone_q{i}"
                break
        
        buttons.append({
            'href': href,
            'text': button_text,
            'is_capstone': is_capstone,
            'quiz_id': quiz_id,
            'context': context[:100] + "..." if len(context) > 100 else context
        })
    
    return buttons

def analyze_pdf_filename(filename):
    """
    Analyze a PDF filename to determine its content type.
    """
    filename = filename.lower()
    
    # Initialize with defaults
    info = {
        'filename': filename,
        'type': 'unknown',
        'contains_answers': False
    }
    
    # Check for content type indicators
    if 'frq' in filename:
        info['type'] = 'FRQ'
    elif 'mcq' in filename:
        info['type'] = 'MCQ'
        
        # Check for Part A/B indicators
        if 'part_a' in filename.replace(' ', '_') or 'parta' in filename:
            info['subtype'] = 'Part A'
        elif 'part_b' in filename.replace(' ', '_') or 'partb' in filename:
            info['subtype'] = 'Part B'
    
    # Check for answer indicators
    if any(term in filename for term in ['answer', 'solution', 'key', 'scoring']):
        info['contains_answers'] = True
    
    return info

def analyze_pdfs(html_file_path):
    """
    Analyze PDF files referenced in the HTML file.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print(f"Analyzing PDF references in {html_file_path}...")
        print("-" * 80)
        
        # Get all PDF URLs
        pdf_urls = extract_pdf_urls(content)
        print(f"Found {len(pdf_urls)} PDF links in the HTML file")
        
        # Get buttons with context
        buttons = extract_button_context(content)
        capstone_buttons = [b for b in buttons if b['is_capstone']]
        print(f"Found {len(capstone_buttons)} capstone-related PDF buttons")
        
        if not capstone_buttons:
            print("❌ No capstone buttons found to analyze.")
            return
        
        # Group by quiz ID
        buttons_by_quiz = defaultdict(list)
        for button in capstone_buttons:
            quiz_id = button['quiz_id'] or 'unknown'
            buttons_by_quiz[quiz_id].append(button)
        
        # Analyze each group
        print("\n=== CAPSTONE PDF CONTENT ANALYSIS ===")
        
        for quiz_id, quiz_buttons in sorted(buttons_by_quiz.items()):
            print(f"\nQuiz ID: {quiz_id}")
            print("-" * 50)
            
            for button in quiz_buttons:
                filename = os.path.basename(button['href'])
                file_info = analyze_pdf_filename(filename)
                
                # Build expected label
                expected_label = file_info['type']
                if 'subtype' in file_info:
                    expected_label += f" {file_info['subtype']}"
                expected_label += " Answers" if file_info['contains_answers'] else " Questions"
                
                # Check if button text matches expected
                button_text = button['text'].lower()
                expected_text = expected_label.lower()
                
                matches = all(term.lower() in button_text for term in expected_label.split())
                status = "✅" if matches else "❌"
                
                print(f"{status} Button: '{button['text']}'")
                print(f"  - File: {filename}")
                print(f"  - Type: {file_info['type']}{' ' + file_info['subtype'] if 'subtype' in file_info else ''}")
                print(f"  - Contains Answers: {file_info['contains_answers']}")
                print(f"  - Expected Label: {expected_label}")
                
                if not matches:
                    print(f"  - ISSUE: Button text doesn't clearly indicate it's for {expected_label}")
                
                print()
        
        # Final analysis
        print("\n=== SUMMARY OF FINDINGS ===")
        
        # Find missing quiz IDs
        expected_quiz_ids = set([f"capstone_q{i}" for i in range(1, 4)])
        found_quiz_ids = set(quiz_id for quiz_id in buttons_by_quiz.keys() if quiz_id != 'unknown')
        missing_quiz_ids = expected_quiz_ids - found_quiz_ids
        
        if missing_quiz_ids:
            print(f"⚠️ The following quiz IDs were not found in any button context:")
            for quiz_id in sorted(missing_quiz_ids):
                print(f"  - {quiz_id}")
        
        # Check for buttons without clear quiz ID
        unknown_buttons = buttons_by_quiz.get('unknown', [])
        if unknown_buttons:
            print(f"\n⚠️ Found {len(unknown_buttons)} buttons without clear quiz ID association:")
            for button in unknown_buttons:
                print(f"  - '{button['text']}' -> {os.path.basename(button['href'])}")
        
        # Provide recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("1. Ensure each button label clearly indicates:")
        print("   - The content type (FRQ, MCQ Part A, MCQ Part B)")
        print("   - Whether it contains questions or answers")
        print("\n2. Use consistent naming patterns:")
        print("   - For FRQ content: 'FRQ Questions' and 'FRQ Answers'")
        print("   - For MCQ Part A: 'MCQ Part A Questions' and 'MCQ Part A Answers'")
        print("   - For MCQ Part B: 'MCQ Part B Questions' and 'MCQ Part B Answers'")
        
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
    
    analyze_pdfs(index_path)

if __name__ == "__main__":
    main() 