#!/usr/bin/env python3
"""
Visualize Button Mapping for Capstone Content

This script creates a visual representation of how buttons in index.html map to 
their content (FRQ/MCQ content). It doesn't modify any files, just provides 
a clear visualization to help understand the current structure.
"""

import os
import re
import sys
from pathlib import Path
import json
from urllib.parse import urlparse, unquote
import textwrap

def extract_pdf_urls(content):
    """
    Extract all PDF URLs from the HTML content.
    """
    pdf_pattern = r'href="([^"]*\.pdf)"'
    pdf_urls = re.findall(pdf_pattern, content)
    return pdf_urls

def extract_button_info(content):
    """
    Extract information about buttons and their labels.
    """
    # Pattern to match button/link elements with their text
    button_pattern = r'<a\s+href="([^"]+\.pdf)"[^>]*>((?:(?!</a>).)*?)</a>'
    
    buttons = []
    for match in re.finditer(button_pattern, content, re.DOTALL):
        href = match.group(1)
        button_html = match.group(2)
        
        # Strip HTML tags to get the text content
        button_text = re.sub(r'<[^>]*>', '', button_html).strip()
        
        # Get surrounding context (300 characters before)
        context_before = content[max(0, match.start() - 300):match.start()]
        
        # Check if in capstone section
        is_capstone = 'capstone' in context_before.lower() or 'capstone' in button_text.lower()
        
        # Try to identify which quiz ID this belongs to
        quiz_id = None
        for i in range(1, 4):  # Looking for capstone_q1, capstone_q2, capstone_q3
            if f"capstone_q{i}" in context_before:
                quiz_id = f"capstone_q{i}"
                break
        
        # Categorize the content type based on filename and label
        filename = os.path.basename(href).lower()
        
        content_type = "Unknown"
        if 'frq' in filename or 'frq' in button_text.lower():
            content_type = "FRQ"
        elif 'mcq' in filename or 'mcq' in button_text.lower():
            content_type = "MCQ"
            if 'part a' in filename or 'part a' in button_text.lower() or 'parta' in filename:
                content_type += " Part A"
            elif 'part b' in filename or 'part b' in button_text.lower() or 'partb' in filename:
                content_type += " Part B"
        
        # Determine if this is questions or answers
        is_answers = any(term in filename.lower() or term in button_text.lower() 
                         for term in ['answer', 'solution', 'key', 'scoring'])
        content_subtype = "Answers" if is_answers else "Questions"
        
        buttons.append({
            'href': href,
            'text': button_text,
            'is_capstone': is_capstone,
            'quiz_id': quiz_id,
            'content_type': content_type,
            'content_subtype': content_subtype,
            'filename': filename
        })
    
    return buttons

def categorize_buttons(buttons):
    """
    Categorize buttons by capstone quiz ID and content type.
    """
    capstone_buttons = [b for b in buttons if b['is_capstone']]
    
    # Group by quiz ID
    quiz_groups = {}
    for button in capstone_buttons:
        quiz_id = button['quiz_id'] or 'unknown'
        if quiz_id not in quiz_groups:
            quiz_groups[quiz_id] = []
        quiz_groups[quiz_id].append(button)
    
    return quiz_groups

def is_button_label_appropriate(button):
    """
    Check if the button label appropriately describes its content.
    """
    text_lower = button['text'].lower()
    
    # Check for answer/question mismatch
    if button['content_subtype'] == 'Answers' and 'answer' not in text_lower:
        return False, "Doesn't indicate it contains answers"
    
    if button['content_subtype'] == 'Questions' and 'answer' in text_lower:
        return False, "Labeled as answers but contains questions"
    
    # Check for content type indicators
    if button['content_type'] == 'FRQ' and 'frq' not in text_lower:
        return False, "Doesn't indicate it's for FRQ"
    
    if 'MCQ' in button['content_type']:
        if 'mcq' not in text_lower:
            return False, "Doesn't indicate it's for MCQ"
        
        if 'Part A' in button['content_type'] and 'part a' not in text_lower:
            return False, "Doesn't specify it's for Part A"
            
        if 'Part B' in button['content_type'] and 'part b' not in text_lower:
            return False, "Doesn't specify it's for Part B"
    
    return True, "Label correctly indicates content"

def visualize_button_map(html_file_path):
    """
    Create a visual representation of button mappings.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print("\n" + "=" * 80)
        print(" CAPSTONE BUTTON MAPPING VISUALIZATION ".center(80, "="))
        print("=" * 80 + "\n")
        
        # Extract button information
        buttons = extract_button_info(content)
        
        # Get quiz groups
        quiz_groups = categorize_buttons(buttons)
        
        if not quiz_groups:
            print("❌ No capstone buttons found in the HTML.")
            return
        
        # Look for capstone topic in the JavaScript data
        capstone_pattern = r'id:\s*"9-capstone",[^{]*?description:\s*"([^"]*)"'
        capstone_match = re.search(capstone_pattern, content)
        
        if capstone_match:
            print(f"Capstone Topic: {capstone_match.group(1)}")
        else:
            print("Note: Couldn't find capstone topic description")
        
        print("\nButton to Content Mapping:\n")
        
        # Create table header
        header = "| Quiz ID | Content Type | Button Label | Filename | Status |"
        separator = "|" + "-" * 10 + "|" + "-" * 14 + "|" + "-" * 40 + "|" + "-" * 30 + "|" + "-" * 16 + "|"
        
        print(header)
        print(separator)
        
        # Sort quiz IDs for consistent output
        for quiz_id in sorted(quiz_groups.keys()):
            buttons = quiz_groups[quiz_id]
            
            # Sort buttons by content type and subtype
            buttons.sort(key=lambda b: (b['content_type'], b['content_subtype']))
            
            for button in buttons:
                # Truncate long labels
                label = button['text']
                if len(label) > 38:
                    label = label[:35] + "..."
                
                # Truncate long filenames
                filename = button['filename']
                if len(filename) > 28:
                    filename = filename[:25] + "..."
                
                # Check if label is appropriate
                is_appropriate, reason = is_button_label_appropriate(button)
                status = "✅ Good" if is_appropriate else f"❌ {reason}"
                
                # Format row
                content_type = f"{button['content_type']} {button['content_subtype']}"
                row = f"| {quiz_id.ljust(8)} | {content_type.ljust(12)} | {label.ljust(38)} | {filename.ljust(28)} | {status.ljust(14)} |"
                
                print(row)
        
        # Overall assessment
        print("\n" + "=" * 80)
        print(" RECOMMENDATIONS ".center(80, "="))
        print("=" * 80)
        
        print("\nBased on the analysis, buttons should be labeled as follows:")
        print("1. For FRQ content:")
        print("   - FRQ Questions")
        print("   - FRQ Answers")
        print("2. For MCQ content:")
        print("   - MCQ Part A Questions")
        print("   - MCQ Part A Answers")
        print("   - MCQ Part B Questions")
        print("   - MCQ Part B Answers")
        
        print("\nThe button label should clearly indicate BOTH:")
        print("1. The content type (FRQ, MCQ Part A, MCQ Part B)")
        print("2. Whether it contains questions or answers")
        
        print("\nTo implement these changes, you can use the Python scripts in the scripts directory:")
        print("- analyze_capstone_buttons.py - Find button labeling issues")
        print("- suggest_capstone_fixes.py - Get specific code fixes")
        
    except Exception as e:
        print(f"Error: {e}")
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
    
    visualize_button_map(index_path)

if __name__ == "__main__":
    main() 