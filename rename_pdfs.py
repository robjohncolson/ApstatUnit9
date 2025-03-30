import os
import json
import shutil
from pathlib import Path
from difflib import get_close_matches

def load_rename_mappings():
    """Load the PDF rename mappings from urls.json"""
    with open('urls.json', 'r') as f:
        data = json.load(f)
        return data['unit9']['pdfRenames']

def find_best_match(filename, candidates):
    """Find the best matching filename from candidates using fuzzy matching"""
    # Remove file extension for matching
    filename_no_ext = os.path.splitext(filename)[0]
    candidate_names = [os.path.splitext(c)[0] for c in candidates]
    
    # Get the best match
    matches = get_close_matches(filename_no_ext, candidate_names, n=1, cutoff=0.8)
    if matches:
        # Find the original filename with extension
        idx = candidate_names.index(matches[0])
        return candidates[idx]
    return None

def rename_pdfs():
    """Rename PDFs according to the mappings"""
    mappings = load_rename_mappings()
    pdf_dir = Path('pdfs/unit9')
    
    # Get list of actual files in directory
    actual_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    print(f"\nFound {len(actual_files)} PDF files in directory.")
    
    # First, print all files for verification
    print("\nFiles in directory:")
    for f in actual_files:
        print(f"  {f}")
    
    # Create mapping dictionary
    success = True
    rename_pairs = []
    
    print("\nMatching files...")
    for mapping in mappings:
        target_file = mapping['original']
        best_match = find_best_match(target_file, actual_files)
        
        if best_match:
            print(f"Matched: {best_match} -> {mapping['new']}")
            rename_pairs.append((best_match, mapping['new']))
        else:
            print(f"Warning: No match found for {target_file}")
            success = False
    
    # Ask for confirmation
    if success:
        print("\nProposed renaming operations:")
        for old, new in rename_pairs:
            print(f"  {old} -> {new}")
        
        confirm = input("\nProceed with renaming? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return False
        
        # Perform the renaming
        for old_name, new_name in rename_pairs:
            try:
                old_path = pdf_dir / old_name
                new_path = pdf_dir / new_name
                old_path.rename(new_path)
                print(f"Renamed: {old_name} -> {new_name}")
            except Exception as e:
                print(f"Error renaming {old_name}: {str(e)}")
                success = False
        
        if success:
            # Update urls.json with new statuses
            with open('urls.json', 'r') as f:
                data = json.load(f)
            
            # Update all PDF statuses
            for topic in data['unit9']['topics'].values():
                if 'pdfs' in topic:
                    for pdf in topic['pdfs'].values():
                        if 'status' in pdf:
                            pdf['status'] = 'completed'
            
            # Update progress check PDF statuses
            for pdf in data['unit9']['progressCheck']['pdfs'].values():
                pdf['status'] = 'completed'
            
            # Update metadata
            data['unit9']['metadata']['resourceStatus']['pdfs']['uploaded'] = 12
            
            # Write back to urls.json
            with open('urls.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print("\nAll PDFs renamed successfully!")
            print("urls.json updated with new statuses")
    
    return success

if __name__ == "__main__":
    print("Starting PDF renaming process...")
    if rename_pdfs():
        print("\nProcess completed successfully!")
    else:
        print("\nProcess completed with errors. Please check the messages above.") 