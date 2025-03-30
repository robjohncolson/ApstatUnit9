import os
import json
import shutil
from pathlib import Path

def load_rename_mappings():
    """Load the PDF rename mappings from urls.json"""
    with open('urls.json', 'r') as f:
        data = json.load(f)
        return data['unit9']['pdfRenames']

def rename_pdfs():
    """Rename PDFs according to the mappings"""
    mappings = load_rename_mappings()
    pdf_dir = Path('pdfs/unit9')
    
    # Ensure all original files exist
    for mapping in mappings:
        original_path = pdf_dir / mapping['original']
        if not original_path.exists():
            print(f"Warning: Original file not found: {mapping['original']}")
            return False
    
    # Perform the renaming
    success = True
    for mapping in mappings:
        try:
            original_path = pdf_dir / mapping['original']
            new_path = pdf_dir / mapping['new']
            
            # Rename the file
            original_path.rename(new_path)
            print(f"Renamed: {mapping['original']} -> {mapping['new']}")
            
            # Update status in urls.json
            mapping['status'] = 'completed'
            
        except Exception as e:
            print(f"Error renaming {mapping['original']}: {str(e)}")
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