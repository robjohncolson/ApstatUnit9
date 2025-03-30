import os
import json
import requests
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

class ResourceVerifier:
    def __init__(self):
        self.pdf_dir = Path('pdfs/unit9')
        with open('urls.json', 'r') as f:
            self.data = json.load(f)
        self.unit_data = self.data['unit9']
        self.results = {
            'pdfs': {'success': [], 'missing': []},
            'urls': {'success': [], 'failed': []},
            'structure': {'valid': [], 'invalid': []}
        }

    def verify_pdf_presence(self):
        """Verify all PDFs exist in the correct directory with correct names"""
        print("\nVerifying PDF files...")
        expected_pdfs = []

        # Collect expected PDFs from topics
        for topic_id, topic in self.unit_data['topics'].items():
            if 'pdfs' in topic and topic['pdfs']:
                for pdf_type, pdf_info in topic['pdfs'].items():
                    if isinstance(pdf_info, dict) and 'filename' in pdf_info:
                        expected_pdfs.append(pdf_info['filename'])

        # Add Progress Check PDFs
        if 'progressCheck' in self.unit_data and 'pdfs' in self.unit_data['progressCheck']:
            for pdf_info in self.unit_data['progressCheck']['pdfs'].values():
                if isinstance(pdf_info, dict) and 'filename' in pdf_info:
                    expected_pdfs.append(pdf_info['filename'])

        # Check each expected PDF
        for pdf_name in expected_pdfs:
            pdf_path = self.pdf_dir / pdf_name
            if pdf_path.exists():
                print(f"✓ Found: {pdf_name}")
                self.results['pdfs']['success'].append(pdf_name)
            else:
                print(f"✗ Missing: {pdf_name}")
                self.results['pdfs']['missing'].append(pdf_name)

    def check_url(self, url, context):
        """Check if a URL is accessible"""
        try:
            # For Google Drive links, just verify the format
            if 'drive.google.com' in url:
                parsed = urlparse(url)
                if parsed.path.startswith('/file/d/') and 'view?usp=drive_link' in url:
                    return True, context
                return False, context

            # For AP Classroom links, verify the format
            if 'apclassroom.collegeboard.org' in url:
                parsed = urlparse(url)
                if parsed.path.startswith('/d/') and 'sui=33,9' in url:
                    return True, context
                return False, context

            # For any other URLs, try a HEAD request
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200, context

        except Exception as e:
            return False, context

    def verify_urls(self):
        """Verify all URLs are properly formatted and accessible"""
        print("\nVerifying URLs...")
        urls_to_check = []

        # Collect URLs from topics
        for topic_id, topic in self.unit_data['topics'].items():
            if 'videos' in topic:
                videos = topic['videos']
                if isinstance(videos, dict):
                    # Handle different video structures
                    if 'apClassroom' in videos:
                        if isinstance(videos['apClassroom'], dict):
                            if 'url' in videos['apClassroom']:
                                urls_to_check.append((
                                    videos['apClassroom']['url'],
                                    f"AP Classroom - Topic {topic_id}"
                                ))
                            for key in ['primary', 'additional1', 'additional2']:
                                if key in videos['apClassroom'] and isinstance(videos['apClassroom'][key], dict):
                                    url = videos['apClassroom'][key].get('url')
                                    if url:
                                        urls_to_check.append((
                                            url,
                                            f"AP Classroom - Topic {topic_id} ({key})"
                                        ))
                    if 'backup' in videos:
                        if isinstance(videos['backup'], dict):
                            if 'url' in videos['backup']:
                                urls_to_check.append((
                                    videos['backup']['url'],
                                    f"Google Drive Backup - Topic {topic_id}"
                                ))
                            for key in ['primary', 'additional1', 'additional2']:
                                if key in videos['backup'] and isinstance(videos['backup'][key], dict):
                                    url = videos['backup'][key].get('url')
                                    if url:
                                        urls_to_check.append((
                                            url,
                                            f"Google Drive Backup - Topic {topic_id} ({key})"
                                        ))

        # Check URLs in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self.check_url, url, context): (url, context)
                for url, context in urls_to_check
            }

            for future in as_completed(future_to_url):
                url, context = future_to_url[future]
                try:
                    is_valid, context = future.result()
                    if is_valid:
                        print(f"✓ Valid URL: {context}")
                        self.results['urls']['success'].append((url, context))
                    else:
                        print(f"✗ Invalid URL: {context}")
                        self.results['urls']['failed'].append((url, context))
                except Exception as e:
                    print(f"✗ Error checking URL {context}: {str(e)}")
                    self.results['urls']['failed'].append((url, context))

    def verify_structure(self):
        """Verify the structure of urls.json matches expected format"""
        print("\nVerifying data structure...")
        expected_fields = {
            'metadata': ['lastUpdated', 'resourceStatus', 'topicStatus'],
            'topics': dict,
            'progressCheck': dict
        }

        for field, expected_type in expected_fields.items():
            if field in self.unit_data:
                if isinstance(expected_type, type):
                    if isinstance(self.unit_data[field], expected_type):
                        print(f"✓ Valid structure: {field}")
                        self.results['structure']['valid'].append(field)
                    else:
                        print(f"✗ Invalid type for {field}")
                        self.results['structure']['invalid'].append(field)
                else:
                    missing_fields = [f for f in expected_type if f not in self.unit_data[field]]
                    if not missing_fields:
                        print(f"✓ Valid structure: {field}")
                        self.results['structure']['valid'].append(field)
                    else:
                        print(f"✗ Missing fields in {field}: {', '.join(missing_fields)}")
                        self.results['structure']['invalid'].append(field)
            else:
                print(f"✗ Missing section: {field}")
                self.results['structure']['invalid'].append(field)

    def print_summary(self):
        """Print a summary of all verification results"""
        print("\n=== Verification Summary ===")
        
        print("\nPDF Files:")
        print(f"✓ Found: {len(self.results['pdfs']['success'])}")
        print(f"✗ Missing: {len(self.results['pdfs']['missing'])}")
        if self.results['pdfs']['missing']:
            print("  Missing files:")
            for pdf in self.results['pdfs']['missing']:
                print(f"  - {pdf}")

        print("\nURLs:")
        print(f"✓ Valid: {len(self.results['urls']['success'])}")
        print(f"✗ Invalid: {len(self.results['urls']['failed'])}")
        if self.results['urls']['failed']:
            print("  Failed URLs:")
            for url, context in self.results['urls']['failed']:
                print(f"  - {context}")

        print("\nStructure:")
        print(f"✓ Valid sections: {len(self.results['structure']['valid'])}")
        print(f"✗ Invalid sections: {len(self.results['structure']['invalid'])}")
        if self.results['structure']['invalid']:
            print("  Invalid sections:")
            for section in self.results['structure']['invalid']:
                print(f"  - {section}")

        # Overall status - Fixed calculation
        total_success = len(self.results['pdfs']['success']) + \
                       len(self.results['urls']['success']) + \
                       len(self.results['structure']['valid'])
        
        total_checks = (len(self.results['pdfs']['success']) + len(self.results['pdfs']['missing'])) + \
                      (len(self.results['urls']['success']) + len(self.results['urls']['failed'])) + \
                      (len(self.results['structure']['valid']) + len(self.results['structure']['invalid']))
        
        print("\nOverall Status:")
        success_rate = (total_success / total_checks) * 100 if total_checks > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n✓ All verifications passed! Unit 9 resources are ready to use.")
        else:
            print("\n⚠ Some verifications failed. Please review the issues above.")

def main():
    print("Starting Unit 9 resource verification...")
    verifier = ResourceVerifier()
    
    verifier.verify_structure()
    verifier.verify_pdf_presence()
    verifier.verify_urls()
    
    verifier.print_summary()

if __name__ == "__main__":
    main() 