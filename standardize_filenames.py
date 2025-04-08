import os
import re
import shutil
from pathlib import Path

def analyze_filenames(directory):
    """Analyze filenames in the directory to detect patterns and suggest standardization."""
    files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    
    # Analyze patterns
    patterns = {
        'section_quiz': r'(\d+\.\d+)_quiz\.pdf',
        'section_answers': r'(\d+\.\d+)_answers\.pdf',
        'unit_quiz': r'unit\d+_([a-z]+)_([a-z]+)(?:_([a-z]+))?\.pdf',
        'unit_answers': r'unit\d+_([a-z]+)_([a-z]+)(?:_([a-z]+))?_answers\.pdf'
    }
    
    categorized_files = {}
    uncategorized = []
    
    for file in files:
        categorized = False
        for pattern_name, pattern in patterns.items():
            if re.match(pattern, file, re.IGNORECASE):
                if pattern_name not in categorized_files:
                    categorized_files[pattern_name] = []
                categorized_files[pattern_name].append(file)
                categorized = True
                break
        
        if not categorized:
            uncategorized.append(file)
    
    return categorized_files, uncategorized

def suggest_standard_format(directory):
    """Suggest a standard format based on existing files."""
    categorized_files, uncategorized = analyze_filenames(directory)
    
    # Extract unit number from directory name if possible
    dir_name = os.path.basename(directory)
    unit_match = re.match(r'unit(\d+)', dir_name, re.IGNORECASE)
    unit_number = unit_match.group(1) if unit_match else None
    
    standards = {
        'section_quiz': 'unit{unit}_section{section}_quiz.pdf',
        'section_answers': 'unit{unit}_section{section}_answers.pdf',
        'unit_quiz': 'unit{unit}_{quiz_type}_{part_type}{part_name}.pdf',
        'unit_answers': 'unit{unit}_{quiz_type}_{part_type}{part_name}_answers.pdf'
    }
    
    return standards, unit_number, categorized_files, uncategorized

def get_new_filename(file, pattern_name, standards, unit_number):
    """Generate a new standardized filename based on the pattern."""
    if pattern_name == 'section_quiz':
        match = re.match(r'(\d+\.\d+)_quiz\.pdf', file, re.IGNORECASE)
        if match:
            section = match.group(1)
            return standards[pattern_name].format(unit=unit_number, section=section)
    
    elif pattern_name == 'section_answers':
        match = re.match(r'(\d+\.\d+)_answers\.pdf', file, re.IGNORECASE)
        if match:
            section = match.group(1)
            return standards[pattern_name].format(unit=unit_number, section=section)
    
    elif pattern_name == 'unit_quiz':
        match = re.match(r'unit\d+_([a-z]+)_([a-z]+)(?:_([a-z]+))?\.pdf', file, re.IGNORECASE)
        if match:
            quiz_type = match.group(1)
            part_type = match.group(2)
            part_name = match.group(3) if match.group(3) else ''
            return standards[pattern_name].format(
                unit=unit_number, 
                quiz_type=quiz_type, 
                part_type=part_type, 
                part_name=f"_{part_name}" if part_name else ""
            )
    
    elif pattern_name == 'unit_answers':
        match = re.match(r'unit\d+_([a-z]+)_([a-z]+)(?:_([a-z]+))?_answers\.pdf', file, re.IGNORECASE)
        if match:
            quiz_type = match.group(1)
            part_type = match.group(2)
            part_name = match.group(3) if match.group(3) else ''
            return standards[pattern_name].format(
                unit=unit_number, 
                quiz_type=quiz_type, 
                part_type=part_type, 
                part_name=f"_{part_name}" if part_name else ""
            )
    
    return None

def main():
    print("PDF Filename Standardizer")
    print("========================")
    
    # Get unit directory
    while True:
        directory = input("Enter the path to the unit's PDF directory: ")
        if os.path.isdir(directory):
            break
        print(f"Directory '{directory}' not found. Please try again.")
    
    # Prompt for unit number if not in directory name
    dir_name = os.path.basename(directory)
    unit_match = re.match(r'unit(\d+)', dir_name, re.IGNORECASE)
    
    if unit_match:
        unit_number = unit_match.group(1)
        print(f"Detected Unit {unit_number} from directory name.")
    else:
        unit_number = input("Unit number not detected in directory name. Please enter unit number: ")
    
    # Analyze files
    standards, _, categorized_files, uncategorized = suggest_standard_format(directory)
    
    # Display stats
    print("\nFile Analysis:")
    print(f"Total PDF files: {sum(len(files) for files in categorized_files.values()) + len(uncategorized)}")
    for category, files in categorized_files.items():
        print(f" - {category}: {len(files)} files")
    print(f" - Uncategorized: {len(uncategorized)} files")
    
    # Show standardization suggestions
    print("\nProposed Standardized Formats:")
    for category, format_str in standards.items():
        print(f" - {category}: {format_str.format(unit=unit_number, section='X.Y', quiz_type='type', part_type='part', part_name='')}")
    
    # Ask if user wants to proceed
    proceed = input("\nDo you want to continue with standardization? (y/n): ").lower()
    if proceed != 'y':
        print("Standardization cancelled.")
        return
    
    # Process files
    renamed_files = []
    skipped_files = []
    
    for pattern_name, files in categorized_files.items():
        for file in files:
            old_path = os.path.join(directory, file)
            new_filename = get_new_filename(file, pattern_name, standards, unit_number)
            
            if new_filename:
                if new_filename.lower() != file.lower():
                    print(f"\nOld: {file}")
                    print(f"New: {new_filename}")
                    action = input("Rename? (y/n/s=skip all, e=edit): ").lower()
                    
                    if action == 's':
                        skipped_files.extend(files)
                        break
                    elif action == 'y':
                        new_path = os.path.join(directory, new_filename)
                        if os.path.exists(new_path):
                            overwrite = input(f"File {new_filename} already exists. Overwrite? (y/n): ").lower()
                            if overwrite != 'y':
                                skipped_files.append(file)
                                continue
                        
                        shutil.move(old_path, new_path)
                        renamed_files.append((file, new_filename))
                    elif action == 'e':
                        custom_name = input("Enter custom filename: ")
                        if not custom_name.endswith('.pdf'):
                            custom_name += '.pdf'
                        new_path = os.path.join(directory, custom_name)
                        shutil.move(old_path, new_path)
                        renamed_files.append((file, custom_name))
                    else:
                        skipped_files.append(file)
                else:
                    print(f"\nFile already follows standard format: {file}")
                    skipped_files.append(file)
            else:
                skipped_files.append(file)
    
    # Handle uncategorized files
    if uncategorized:
        print("\nUncategorized Files:")
        for file in uncategorized:
            print(f"\nFile: {file}")
            action = input("How to handle? (s=skip, r=rename, c=categorize): ").lower()
            
            if action == 'r':
                new_name = input("Enter new filename: ")
                if not new_name.endswith('.pdf'):
                    new_name += '.pdf'
                shutil.move(os.path.join(directory, file), os.path.join(directory, new_name))
                renamed_files.append((file, new_name))
            elif action == 'c':
                print("Categories:")
                for i, category in enumerate(standards.keys()):
                    print(f"{i+1}. {category}")
                try:
                    cat_num = int(input("Select category number: ")) - 1
                    if 0 <= cat_num < len(standards):
                        category = list(standards.keys())[cat_num]
                        print(f"Format: {standards[category]}")
                        
                        if category in ['section_quiz', 'section_answers']:
                            section = input("Enter section number (e.g., 1.2): ")
                            new_name = standards[category].format(unit=unit_number, section=section)
                        else:
                            quiz_type = input("Enter quiz type (e.g., pc): ")
                            part_type = input("Enter part type (e.g., mcq): ")
                            part_name = input("Enter part name (optional): ")
                            new_name = standards[category].format(
                                unit=unit_number, 
                                quiz_type=quiz_type, 
                                part_type=part_type, 
                                part_name=f"_{part_name}" if part_name else ""
                            )
                        
                        shutil.move(os.path.join(directory, file), os.path.join(directory, new_name))
                        renamed_files.append((file, new_name))
                    else:
                        print("Invalid category number.")
                        skipped_files.append(file)
                except ValueError:
                    print("Invalid input.")
                    skipped_files.append(file)
            else:
                skipped_files.append(file)
    
    # Summary
    print("\nStandardization Summary:")
    print(f"Renamed: {len(renamed_files)} files")
    print(f"Skipped: {len(skipped_files)} files")
    
    if renamed_files:
        print("\nRenamed Files:")
        for old, new in renamed_files:
            print(f" - {old} → {new}")

if __name__ == "__main__":
    main() 