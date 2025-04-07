import re
import json
import difflib
import ast

def extract_pdf_files_from_index(file_path):
    """Extract the pdfFiles array from index.html"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract the pdfFiles array section
    start_marker = "const pdfFiles = ["
    end_marker = "];"
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Could not find pdfFiles array in index.html")
        return None
    
    start_idx += len(start_marker) - 1  # position at the '['
    bracket_count = 0
    for i in range(start_idx, len(content)):
        if content[i] == '[':
            bracket_count += 1
        elif content[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_idx = i + 1
                break
    
    if bracket_count != 0:
        print("Could not find the end of pdfFiles array")
        return None
    
    array_text = content[start_idx:end_idx]
    
    # Parse the array by manually converting it to proper JSON
    try:
        # First, add quotes around property names
        json_text = re.sub(r'(\s*)(\w+)(\s*:)', r'\1"\2"\3', array_text)
        
        # Replace JavaScript literals with JSON equivalents
        json_text = json_text.replace('true', 'true').replace('false', 'false').replace('null', 'null')
        
        # Parse the JSON
        data = json.loads(json_text)
        return data
    except Exception as e:
        print(f"Error parsing pdfFiles array: {e}")
        # Fall back to simpler approach for debugging
        try:
            # Extract individual objects for analysis
            print(f"Attempting to extract first object for analysis...")
            obj_match = re.search(r'\{\s*(.*?)\s*\}', array_text, re.DOTALL)
            if obj_match:
                print(f"First object snippet: {obj_match.group(0)[:100]}...")
            return None
        except:
            return None

def extract_unit9_from_allunitsdata(file_path):
    """Extract the Unit 9 topics array from allUnitsData.js"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Look for the Unit 9 section
    unit9_pattern = r'{\s*unitId:\s*[\'"]unit9[\'"]\s*,\s*topics:\s*\['
    unit9_match = re.search(unit9_pattern, content)
    if not unit9_match:
        print("Could not find Unit 9 section in allUnitsData.js")
        return None
    
    # Find the start of the topics array
    start_idx = unit9_match.end() - 1  # position at the '['
    
    # Find the matching closing bracket
    bracket_count = 0
    for i in range(start_idx, len(content)):
        if content[i] == '[':
            bracket_count += 1
        elif content[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_idx = i + 1
                break
    
    if bracket_count != 0:
        print("Could not find the end of Unit 9 topics array")
        return None
    
    array_text = content[start_idx:end_idx]
    
    # Parse the array by manually converting it to proper JSON
    try:
        # First, add quotes around property names
        json_text = re.sub(r'(\s*)(\w+)(\s*:)', r'\1"\2"\3', array_text)
        
        # Replace JavaScript literals with JSON equivalents
        json_text = json_text.replace('true', 'true').replace('false', 'false').replace('null', 'null')
        
        # Parse the JSON
        data = json.loads(json_text)
        return data
    except Exception as e:
        print(f"Error parsing Unit 9 topics array: {e}")
        # Fall back to simpler approach for debugging
        try:
            # Extract individual objects for analysis
            print(f"Attempting to extract first object for analysis...")
            obj_match = re.search(r'\{\s*(.*?)\s*\}', array_text, re.DOTALL)
            if obj_match:
                print(f"First object snippet: {obj_match.group(0)[:100]}...")
            return None
        except:
            return None

def simple_extract_array(file_path, unit_id=None):
    """Simplified extraction method that just fetches topic IDs and quiz PDF paths"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Simplified regex to extract topic objects
    if unit_id:
        # For allUnitsData.js, look for unit9 section
        section_start = re.search(rf'unitId:\s*[\'"]unit{unit_id}[\'"]\s*,\s*topics:', content)
        if not section_start:
            print(f"Could not find Unit {unit_id} section")
            return None
        start_pos = section_start.end()
    else:
        # For index.html, look for pdfFiles array
        section_start = re.search(r'const\s+pdfFiles\s*=\s*\[', content)
        if not section_start:
            print("Could not find pdfFiles array")
            return None
        start_pos = section_start.end()
    
    # Extract all topic IDs
    topic_id_pattern = r'id:\s*[\'"]([^\'"]+)[\'"]'
    topic_ids = re.findall(topic_id_pattern, content[start_pos:start_pos + 20000])
    
    # Extract all PDF paths
    pdf_pattern = r'questionPdf:\s*[\'"]([^\'"]+)[\'"]'
    pdf_paths = re.findall(pdf_pattern, content[start_pos:start_pos + 20000])
    
    return {"ids": topic_ids, "pdfs": pdf_paths}

def compare_arrays(index_array, unit_array):
    """Compare the two arrays and identify differences"""
    differences = []
    
    if len(index_array) != len(unit_array):
        differences.append(f"Array length mismatch: index.html has {len(index_array)} items, allUnitsData.js has {len(unit_array)} items")
    
    # Compare each topic
    for i, (index_item, unit_item) in enumerate(zip(index_array, unit_array)):
        topic_diffs = []
        
        # Compare basic properties
        for field in ["id", "name", "description"]:
            if index_item.get(field) != unit_item.get(field):
                topic_diffs.append(f"Field '{field}' differs:")
                topic_diffs.append(f"  index.html: {index_item.get(field)}")
                topic_diffs.append(f"  allUnitsData.js: {unit_item.get(field)}")
        
        # Compare videos
        index_videos = index_item.get("videos", [])
        unit_videos = unit_item.get("videos", [])
        
        if len(index_videos) != len(unit_videos):
            topic_diffs.append(f"Number of videos differs: index.html has {len(index_videos)}, allUnitsData.js has {len(unit_videos)}")
        
        for j, (index_video, unit_video) in enumerate(zip(index_videos, unit_videos)):
            for field in ["url", "altUrl"]:
                if index_video.get(field) != unit_video.get(field):
                    topic_diffs.append(f"Video {j+1} field '{field}' differs:")
                    topic_diffs.append(f"  index.html: {index_video.get(field)}")
                    topic_diffs.append(f"  allUnitsData.js: {unit_video.get(field)}")
        
        # Compare quizzes
        index_quizzes = index_item.get("quizzes", [])
        unit_quizzes = unit_item.get("quizzes", [])
        
        if len(index_quizzes) != len(unit_quizzes):
            topic_diffs.append(f"Number of quizzes differs: index.html has {len(index_quizzes)}, allUnitsData.js has {len(unit_quizzes)}")
        
        for j, (index_quiz, unit_quiz) in enumerate(zip(index_quizzes, unit_quizzes)):
            for field in ["questionPdf", "answersPdf", "quizId"]:
                if index_quiz.get(field) != unit_quiz.get(field):
                    topic_diffs.append(f"Quiz {j+1} field '{field}' differs:")
                    topic_diffs.append(f"  index.html: {index_quiz.get(field)}")
                    topic_diffs.append(f"  allUnitsData.js: {unit_quiz.get(field)}")
        
        # Add isCapstone check
        if index_item.get("isCapstone") != unit_item.get("isCapstone"):
            topic_diffs.append(f"Field 'isCapstone' differs:")
            topic_diffs.append(f"  index.html: {index_item.get('isCapstone')}")
            topic_diffs.append(f"  allUnitsData.js: {unit_item.get('isCapstone')}")
        
        if topic_diffs:
            topic_name = index_item.get("name", f"Topic {i+1}")
            differences.append(f"\nDifferences in {topic_name}:")
            differences.extend(topic_diffs)
    
    return differences

def main():
    print("Comparing pdfFiles array in index.html with Unit 9 topics in allUnitsData.js...")
    
    # Try the advanced extraction methods first
    index_array = extract_pdf_files_from_index("index.html")
    unit_array = extract_unit9_from_allunitsdata("js/allUnitsData.js")
    
    # If advanced extraction fails, fall back to simple extraction
    if index_array is None or unit_array is None:
        print("\nFalling back to simplified comparison method...")
        index_data = simple_extract_array("index.html")
        unit_data = simple_extract_array("js/allUnitsData.js", 9)
        
        if index_data and unit_data:
            print("\nComparing topic IDs and PDF paths only:")
            print(f"- Found {len(index_data['ids'])} topic IDs in index.html")
            print(f"- Found {len(unit_data['ids'])} topic IDs in allUnitsData.js")
            
            # Compare topic IDs
            if index_data['ids'] != unit_data['ids']:
                print("\nTopic ID differences:")
                print(f"  index.html: {index_data['ids']}")
                print(f"  allUnitsData.js: {unit_data['ids']}")
            else:
                print("\nTopic IDs match!")
                
            # Compare PDF paths
            if index_data['pdfs'] != unit_data['pdfs']:
                print("\nPDF path differences:")
                print(f"  index.html: {index_data['pdfs']}")
                print(f"  allUnitsData.js: {unit_data['pdfs']}")
            else:
                print("\nPDF paths match!")
        else:
            print("Both extraction methods failed. Cannot compare arrays.")
        return
    
    print(f"\nSuccessfully extracted data:")
    print(f"- Found {len(index_array)} items in index.html pdfFiles array")
    print(f"- Found {len(unit_array)} items in allUnitsData.js Unit 9 topics array")
    
    differences = compare_arrays(index_array, unit_array)
    
    if differences:
        print("\nThe following differences were found:")
        for diff in differences:
            print(diff)
    else:
        print("\nNo differences found! The arrays match perfectly.")

if __name__ == "__main__":
    main() 