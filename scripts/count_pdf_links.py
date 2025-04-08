#!/usr/bin/env python3
"""
Count PDF Links in index.html

This is a simple script that extracts and counts all PDF links in the index.html file.
It uses a basic approach to ensure we're finding all the links.
"""

import os
import re
import sys
from pathlib import Path

def count_pdf_links(html_file_path):
    """
    Count all PDF links in the HTML file.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"Analyzing PDF links in {html_file_path}...")
        print("-" * 80)
        
        # Try multiple regex patterns to catch different ways PDF links might be formatted
        patterns = [
            r'href="([^"]*\.pdf)"',          # Standard href format
            r'href=\'([^\']*\.pdf)\'',       # Single quotes
            r'href=([^\s>]*\.pdf)',          # No quotes
            r'"([^"]*\.pdf)"',               # Just the URL in quotes
            r'src="([^"]*\.pdf)"',           # src attribute (for objects/embeds)
            r'data="([^"]*\.pdf)"'           # data attribute (for objects)
        ]
        
        all_pdf_urls = []
        for pattern in patterns:
            pdf_urls = re.findall(pattern, content)
            all_pdf_urls.extend(pdf_urls)
        
        # Remove duplicates
        unique_pdf_urls = list(set(all_pdf_urls))
        
        print(f"Found {len(unique_pdf_urls)} unique PDF links in the HTML file")
        
        # Print the first 10 links as examples
        if unique_pdf_urls:
            print("\nExample PDF links:")
            for i, url in enumerate(unique_pdf_urls[:10]):
                print(f"{i+1}. {url}")
            
            if len(unique_pdf_urls) > 10:
                print(f"... and {len(unique_pdf_urls) - 10} more")
            
            # Count capstone-related PDFs
            capstone_pdfs = [url for url in unique_pdf_urls if 'capstone' in url.lower()]
            print(f"\nFound {len(capstone_pdfs)} capstone-related PDF links")
            
            # Count specific keyword PDFs
            frq_pdfs = [url for url in unique_pdf_urls if 'frq' in url.lower()]
            mcq_pdfs = [url for url in unique_pdf_urls if 'mcq' in url.lower()]
            answer_pdfs = [url for url in unique_pdf_urls if any(term in url.lower() for term in ['answer', 'solution', 'key'])]
            
            print(f"FRQ PDFs: {len(frq_pdfs)}")
            print(f"MCQ PDFs: {len(mcq_pdfs)}")
            print(f"Answer PDFs: {len(answer_pdfs)}")
            
            # Look for unit9 PDFs
            unit9_pdfs = [url for url in unique_pdf_urls if 'unit9' in url.lower()]
            print(f"Unit 9 PDFs: {len(unit9_pdfs)}")
            
            if unit9_pdfs:
                print("\nUnit 9 PDF links:")
                for url in unit9_pdfs:
                    print(f"- {url}")
        
        # Now let's try to find the capstone button sections
        print("\nLooking for capstone button sections in the HTML...")
        capstone_sections = []
        capstone_patterns = [
            r'(quiz\.quizId\s*===\s*"\d-capstone_q\d"[^}]{1,300})',
            r'(const\s+\w+Title\s*=\s*.*?capstone_q1.*?capstone_q2.*?capstone_q3[^}]{1,300})',
            r'(capstone.*?button[^}]{1,300})'
        ]
        
        for pattern in capstone_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            capstone_sections.extend(matches)
        
        print(f"Found {len(capstone_sections)} potential capstone button sections")
        
        if capstone_sections:
            print("\nExample capstone section snippets:")
            for i, section in enumerate(capstone_sections[:3]):
                # Clean up and limit length for display
                snippet = re.sub(r'\s+', ' ', section).strip()
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                print(f"{i+1}. {snippet}")
            
            if len(capstone_sections) > 3:
                print(f"... and {len(capstone_sections) - 3} more")
        
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
    
    count_pdf_links(index_path)

if __name__ == "__main__":
    main() 