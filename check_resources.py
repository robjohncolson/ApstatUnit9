import os
import json

def check_resources():
    """Check what resources exist and what needs to be added to urls.json"""
    print("Checking resources...")
    
    # Load urls.json
    try:
        with open("urls.json", "r") as f:
            urls = json.load(f)
    except:
        print("❌ urls.json not found or invalid")
        return
    
    # Get unit number
    unit = urls.get("unit")
    if not unit:
        print("❌ No unit number found in urls.json")
        return
    
    # Check PDF directory
    pdf_dir = f"pdfs/unit{unit}"
    if not os.path.exists(pdf_dir):
        print(f"❌ PDF directory missing: {pdf_dir}")
        return
    
    # Get all PDFs
    pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    print(f"\n📄 Found {len(pdfs)} PDF files:")
    for pdf in pdfs:
        print(f"  - {pdf}")
    
    # Check topics in urls.json
    topics = urls.get("topics", [])
    print(f"\n📚 Topics in urls.json: {len(topics)}")
    
    # Check each topic
    for topic in topics:
        print(f"\n🔍 Topic {topic.get('id', 'unknown')}:")
        
        # Check PDFs
        for field in ['questionPdf', 'answersPdf']:
            if field in topic:
                pdf_path = topic[field]
                if os.path.exists(pdf_path):
                    print(f"  ✅ {field}: {pdf_path}")
                else:
                    print(f"  ❌ {field}: {pdf_path} (file missing)")
        
        # Check video links
        if 'videoUrl' in topic and topic['videoUrl']:
            print(f"  ✅ AP Classroom video")
        else:
            print(f"  ❌ AP Classroom video missing")
            
        if 'altVideoUrl' in topic and topic['altVideoUrl']:
            print(f"  ✅ Google Drive video")
        else:
            print(f"  ❌ Google Drive video missing")
    
    # Check progress check
    pc = urls.get("progress_check", {})
    if pc:
        print("\n📝 Progress Check:")
        for field in ['questionPdf', 'answersPdf', 'questionPdf2', 'questionPdf3']:
            if field in pc:
                pdf_path = pc[field]
                if os.path.exists(pdf_path):
                    print(f"  ✅ {field}: {pdf_path}")
                else:
                    print(f"  ❌ {field}: {pdf_path} (file missing)")

if __name__ == "__main__":
    check_resources() 