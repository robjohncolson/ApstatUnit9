#!/usr/bin/env python3
import re
import os
import sys

def update_html_file(file_path):
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False
    
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Define the marker to search for
    marker = '<p class="text-xs text-gray-500 mt-1">Scan for page link</p>'
    
    # Define the content to insert
    github_link = '''
         <a href="https://github.com/robjohncolson/ApstatUnit9.git" target="_blank" class="flex items-center text-gray-600 hover:text-blue-600 text-xs mt-2">
        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 16 16" aria-hidden="true">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"></path>
        </svg>
        View on GitHub
    </a>'''
    
    # Find the marker position
    marker_pos = content.find(marker)
    if marker_pos == -1:
        print(f"Error: Marker '{marker}' not found in the file.")
        return False
    
    marker_end_pos = marker_pos + len(marker)
    
    # Find the next closing div tag after the marker
    div_close_pattern = r'</div>'
    match = re.search(div_close_pattern, content[marker_end_pos:])
    if not match:
        print("Error: Closing div tag not found after the marker.")
        return False
    
    div_close_pos = marker_end_pos + match.start()
    
    # Check if the GitHub link is already there
    if 'View on GitHub' in content[marker_end_pos:div_close_pos]:
        print("GitHub link already exists. No changes needed.")
        return True
    
    # Insert the GitHub link after the marker but before the closing div tag
    new_content = content[:marker_end_pos] + github_link + content[marker_end_pos:]
    
    # Create a backup of the original file
    backup_file = file_path + '.bak'
    with open(backup_file, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Backup created at {backup_file}")
    
    # Write the updated content to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"Successfully updated {file_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "index.html"  # Default to index.html in the current directory
    
    update_html_file(file_path) 