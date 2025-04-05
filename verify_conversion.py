import re
import os
import json
from bs4 import BeautifulSoup
import sys

def scan_file_for_patterns(filename, patterns, ignore_case=False):
    """
    Scan a file for multiple patterns.
    
    Args:
        filename (str): Path to the file to scan
        patterns (list): List of regex patterns to search for
        ignore_case (bool): Whether to ignore case in the search
    
    Returns:
        list: List of tuples (line_number, line, pattern_matched)
    """
    if not os.path.exists(filename):
        print(f"File {filename} does not exist!")
        return []
    
    matches = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file, 1):
                for pattern in patterns:
                    flags = re.IGNORECASE if ignore_case else 0
                    if re.search(pattern, line, flags):
                        matches.append((i, line.strip(), pattern))
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    
    return matches

def check_html_structure(html_file):
    """Check the HTML structure for unit-specific elements"""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Check title
    title = soup.title.string
    if "Unit 9" not in title:
        print(f"❌ HTML title does not contain 'Unit 9': {title}")
    else:
        print(f"✅ HTML title correctly contains 'Unit 9'")
    
    # Check h1
    h1 = soup.find('h1')
    if h1 and "Unit 9" not in h1.text:
        print(f"❌ H1 does not contain 'Unit 9': {h1.text}")
    else:
        print(f"✅ H1 correctly contains 'Unit 9'")
    
    # Check exam weight - search more broadly for the exam weight div
    exam_weight_div = soup.find('div', {'class': 'mt-2 bg-yellow-100'})
    if not exam_weight_div:
        print("❌ Could not find exam weight div")
    elif "2-5%" not in exam_weight_div.text:
        print(f"❌ Exam weight does not mention '2-5%': {exam_weight_div.text}")
    else:
        print(f"✅ Exam weight correctly mentions '2-5%'")

def verify_pdf_files_array(html_file):
    """Verify the pdfFiles array in the HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get the pdfFiles array
    pdf_files_match = re.search(r'const\s+pdfFiles\s*=\s*(\[[\s\S]*?\]);', content)
    if not pdf_files_match:
        print("❌ Could not find pdfFiles array in HTML")
        return False
    
    # Extract the array and attempt to parse it
    pdf_files_str = pdf_files_match.group(1)
    
    # Print a sample of the array content for debugging
    print(f"Debug - pdfFiles array excerpt (first 200 chars): {pdf_files_str[:200]}")
    
    # Check for unit9 paths
    pdf_dir = "pdfs/unit9"
    if pdf_dir not in pdf_files_str:
        print(f"❌ PDF directory path '{pdf_dir}' not found in pdfFiles array")
        return False
    else:
        print(f"✅ PDF directory path '{pdf_dir}' found in pdfFiles array")
    
    # Check for topic IDs (9-1, 9-2, etc.)
    topic_id_pattern = r'id:\s*"9-\d+"'  # Updated to match the actual format in the JS code
    topic_id_matches = re.findall(topic_id_pattern, pdf_files_str)
    if not topic_id_matches:
        print("❌ Topic IDs not updated to Unit 9 format (9-n)")
        print(f"Debug - Looking for pattern: {topic_id_pattern}")
        return False
    else:
        print(f"✅ Topic IDs correctly updated to Unit 9 format. Found {len(topic_id_matches)} matches.")
    
    # Check for topic names (Topic 9.1, Topic 9.2, etc.)
    topic_name_pattern = r'name:\s*"Topic 9\.\d+"'  # Updated to match the actual format in the JS code
    topic_name_matches = re.findall(topic_name_pattern, pdf_files_str)
    if not topic_name_matches:
        print("❌ Topic names not updated to Unit 9 format (Topic 9.n)")
        print(f"Debug - Looking for pattern: {topic_name_pattern}")
        return False
    else:
        print(f"✅ Topic names correctly updated to Unit 9 format. Found {len(topic_name_matches)} matches.")
    
    return True

def main():
    html_file = "index.html"
    
    print("\n=== Checking for Unit 8 references (should be none) ===")
    
    patterns_to_check = [
        r'Unit 8',
        r'unit8',
        r'"id": ?"8-\d+"',  # Updated to match only ID fields, not SVG paths
        r'"name": ?"Topic 8\.\d+"',
        r'apStatsUnit8TopicProgress'
    ]
    
    matches = scan_file_for_patterns(html_file, patterns_to_check)
    
    if matches:
        print(f"❌ Found {len(matches)} references to Unit 8 that should be updated:")
        for line_num, line, pattern in matches:
            print(f"  Line {line_num}: {line.strip()} [Matched pattern: {pattern}]")
    else:
        print("✅ No Unit 8 references found - good job!")
    
    print("\n=== Checking HTML structure ===")
    check_html_structure(html_file)
    
    print("\n=== Verifying pdfFiles array ===")
    verify_pdf_files_array(html_file)

if __name__ == "__main__":
    main() 