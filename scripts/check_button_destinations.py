#!/usr/bin/env python3
"""
Check Button Destinations in index.html

This script checks if the capstone buttons in index.html correctly indicate their 
destinations (FRQ answers, MCQ Part A questions, etc.). It analyzes each button's
href attribute and its label to ensure they match.
"""

import os
import re
import sys
from pathlib import Path
import json
from urllib.parse import urlparse, unquote

def extract_file_info_from_path(file_path):
    """
    Extract meaningful information from a PDF file path.
    Returns a dict with extracted info.
    """
    # Decode URL-encoded characters
    decoded_path = unquote(file_path)
    
    # Extract filename from path
    filename = os.path.basename(decoded_path).lower()
    
    # Check for specific patterns in the filename
    info = {
        'filename': filename,
        'type': 'unknown'
    }
    
    # Check for FRQ indicators
    if 'frq' in filename:
        info['type'] = 'frq'
    
    # Check for MCQ indicators
    if 'mcq' in filename:
        info['type'] = 'mcq'
        
        # Check for Part A/B indicators
        if 'part a' in filename or 'parta' in filename or 'part_a' in filename:
            info['subtype'] = 'part_a'
        elif 'part b' in filename or 'partb' in filename or 'part_b' in filename:
            info['subtype'] = 'part_b'
    
    # Check for answer indicators
    if any(term in filename for term in ['answer', 'solution', 'key', 'scoring']):
        info['contains_answers'] = True
    else:
        info['contains_answers'] = False
    
    return info

def analyze_button_destinations(content):
    """
    Analyze button destinations by looking at href attributes and button labels.
    """
    # Pattern to match button elements with href and link text
    button_pattern = r'<a\s+href="([^"]+)"[^>]*>((?:(?!</a>).)*?)</a>'
    
    buttons = []
    for match in re.finditer(button_pattern, content, re.DOTALL):
        href = match.group(1)
        button_text = re.sub(r'<[^>]*>', '', match.group(2)).strip()  # Strip HTML tags
        
        # Only process PDF links
        if href.lower().endswith('.pdf'):
            file_info = extract_file_info_from_path(href)
            
            # Check if button is within a capstone context
            context_before = content[max(0, match.start() - 300):match.start()]
            is_capstone = 'capstone' in context_before.lower() or 'capstone' in button_text.lower()
            
            capstone_quiz_id = None
            for q_num in range(1, 4):  # Check for quiz IDs 1-3
                if f"capstone_q{q_num}" in context_before:
                    capstone_quiz_id = f"capstone_q{q_num}"
                    break
            
            button_info = {
                'href': href,
                'label': button_text,
                'file_info': file_info,
                'is_capstone': is_capstone,
                'quiz_id': capstone_quiz_id
            }
            
            # Check if label appropriately describes content
            label_match = True
            label_lower = button_text.lower()
            
            if file_info['contains_answers'] and 'answer' not in label_lower:
                label_match = False
                button_info['issue'] = "Button for answers doesn't mention 'answers'"
            elif not file_info['contains_answers'] and 'answer' in label_lower:
                label_match = False
                button_info['issue'] = "Button for questions mentions 'answers'"
            
            if file_info['type'] == 'frq' and 'frq' not in label_lower:
                if label_match:  # Only set if we haven't already found an issue
                    label_match = False
                    button_info['issue'] = "Button for FRQ doesn't mention 'FRQ'"
            elif file_info['type'] == 'mcq':
                if 'subtype' in file_info:
                    if file_info['subtype'] == 'part_a' and 'part a' not in label_lower:
                        if label_match:
                            label_match = False
                            button_info['issue'] = "Button for MCQ Part A doesn't specify 'Part A'"
                    elif file_info['subtype'] == 'part_b' and 'part b' not in label_lower:
                        if label_match:
                            label_match = False
                            button_info['issue'] = "Button for MCQ Part B doesn't specify 'Part B'"
                elif 'mcq' not in label_lower:
                    if label_match:
                        label_match = False
                        button_info['issue'] = "Button for MCQ doesn't mention 'MCQ'"
            
            button_info['label_matches_content'] = label_match
            
            buttons.append(button_info)
    
    return buttons

def check_button_destinations(html_file_path):
    """
    Check if button labels in index.html match their destinations.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print(f"Analyzing button destinations in {html_file_path}...")
        print("-" * 80)
        
        # Analyze button destinations
        buttons = analyze_button_destinations(content)
        
        # Filter to capstone buttons
        capstone_buttons = [b for b in buttons if b['is_capstone']]
        
        print(f"Found {len(buttons)} total buttons linking to PDFs")
        print(f"Found {len(capstone_buttons)} capstone-related buttons")
        
        if not capstone_buttons:
            print("❌ No capstone buttons found to analyze.")
            return
        
        # Group by quiz ID
        buttons_by_quiz = {}
        for button in capstone_buttons:
            quiz_id = button['quiz_id'] or 'unknown'
            if quiz_id not in buttons_by_quiz:
                buttons_by_quiz[quiz_id] = []
            buttons_by_quiz[quiz_id].append(button)
        
        # Check for issues with button labeling
        print("\n=== CAPSTONE BUTTON ANALYSIS ===")
        
        has_issues = False
        for quiz_id, quiz_buttons in buttons_by_quiz.items():
            print(f"\nQuiz ID: {quiz_id}")
            
            for button in quiz_buttons:
                contains_answers = button['file_info']['contains_answers']
                content_type = button['file_info']['type']
                subtype = button['file_info'].get('subtype', '')
                
                # Build expected label based on content
                expected_label = ""
                if content_type == 'frq':
                    expected_label = "FRQ "
                elif content_type == 'mcq':
                    expected_label = "MCQ "
                    if subtype == 'part_a':
                        expected_label += "Part A "
                    elif subtype == 'part_b':
                        expected_label += "Part B "
                
                expected_label += "Answers" if contains_answers else "Questions"
                
                # Check if button label matches expected
                label_lower = button['label'].lower()
                expected_lower = expected_label.lower()
                
                # Convert rich-text labels to plain text for comparison
                plain_label = re.sub(r'<[^>]*>', '', button['label']).strip()
                
                # Display button details
                print(f"  Button: '{plain_label}'")
                print(f"    - Links to: {os.path.basename(button['href'])}")
                print(f"    - Content type: {content_type.upper()}{f' ({subtype})' if subtype else ''}")
                print(f"    - Contains answers: {contains_answers}")
                print(f"    - Expected label should indicate: {expected_label}")
                
                # Check for mismatch
                if not button['label_matches_content']:
                    has_issues = True
                    print(f"    ❌ ISSUE: {button['issue']}")
                    print(f"       Suggested fix: Update label to include '{expected_label}'")
                else:
                    print(f"    ✅ Label correctly indicates content")
                
                print("")
        
        # Overall summary
        if has_issues:
            print("\n❌ Some button labels do not properly indicate their destinations.")
            print("\n💡 Recommendations:")
            print("  1. For FRQ content, buttons should clearly say 'FRQ Questions' or 'FRQ Answers'")
            print("  2. For MCQ content, buttons should indicate 'MCQ Part A/B Questions/Answers'")
            print("  3. Use the following pattern consistently:")
            print("     - FRQ Questions, FRQ Answers")
            print("     - MCQ Part A Questions, MCQ Part A Answers")
            print("     - MCQ Part B Questions, MCQ Part B Answers")
        else:
            print("\n✅ All capstone button labels correctly indicate their destinations!")
        
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
    
    check_button_destinations(index_path)

if __name__ == "__main__":
    main() 