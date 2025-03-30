import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pathlib import Path

class WebInterfaceTester:
    def __init__(self):
        # Load configuration
        with open('urls.json', 'r') as f:
            self.unit_data = json.load(f)['unit9']
        
        # Setup WebDriver
        options = webdriver.ChromeOptions()
        # Add download preferences
        prefs = {
            "download.default_directory": str(Path('pdfs/unit9').absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Track test results
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

    def setup(self):
        """Set up the test environment"""
        # Get absolute path to index.html
        index_path = os.path.abspath('index.html')
        self.driver.get(f'file:///{index_path}')
        time.sleep(2)  # Allow page to load

    def test_tab_switching(self):
        """Test that all tabs can be switched to"""
        print("\nTesting tab switching...")
        tabs = ['learning-flow', 'flowchart', 'grok-prompt', 'study-materials']
        
        for tab in tabs:
            try:
                # Wait for tab to be present
                tab_button = self.wait.until(
                    EC.presence_of_element_located((By.ID, f'tab-{tab}'))
                )
                
                # Scroll into view and ensure clickable
                self.driver.execute_script("arguments[0].scrollIntoView(true);", tab_button)
                time.sleep(0.5)  # Allow scroll to complete
                
                # Try JavaScript click if normal click fails
                try:
                    tab_button.click()
                except:
                    self.driver.execute_script("arguments[0].click();", tab_button)
                
                time.sleep(1)
                
                # Verify content is visible
                content = self.wait.until(
                    EC.visibility_of_element_located((By.ID, f'content-{tab}'))
                )
                assert content.is_displayed()
                self.results['passed'].append(f'Tab switching: {tab}')
            except Exception as e:
                self.results['failed'].append(f'Tab switching: {tab} - {str(e)}')

    def test_grok_prompt(self):
        """Test Grok prompt functionality"""
        print("\nTesting Grok prompt...")
        try:
            # Switch to Grok prompt tab
            self.driver.find_element(By.ID, 'tab-grok-prompt').click()
            time.sleep(1)

            # Test copy button
            copy_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'copy-button'))
            )
            copy_button.click()
            time.sleep(1)

            # Verify prompt text exists
            prompt_element = self.driver.find_element(By.ID, 'grok-prompt')
            assert prompt_element.text.strip() != ''
            
            self.results['passed'].append('Grok prompt functionality')
        except Exception as e:
            self.results['failed'].append(f'Grok prompt functionality - {str(e)}')

    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        print("\nTesting progress tracking...")
        try:
            # Switch to study materials tab
            self.driver.find_element(By.ID, 'tab-study-materials').click()
            time.sleep(1)

            # Test marking a topic as complete
            topic_cards = self.driver.find_elements(
                By.CSS_SELECTOR, 
                '[id^="topic-card-"]'
            )
            
            if topic_cards:
                # Find first incomplete topic
                for card in topic_cards:
                    complete_button = card.find_elements(
                        By.CSS_SELECTOR,
                        'button:not([disabled])'
                    )
                    if complete_button:
                        complete_button[0].click()
                        time.sleep(1)
                        break

            # Verify progress bar updates
            progress_bar = self.driver.find_element(By.ID, 'progress-bar')
            assert progress_bar.get_attribute('style') != ''
            
            self.results['passed'].append('Progress tracking')
        except Exception as e:
            self.results['failed'].append(f'Progress tracking - {str(e)}')

    def test_resource_links(self):
        """Test that resource links are properly formatted and point to correct locations"""
        print("\nTesting resource links...")
        try:
            # Switch to study materials tab
            self.driver.find_element(By.ID, 'tab-study-materials').click()
            time.sleep(1)

            # Test PDF links
            pdf_links = self.driver.find_elements(
                By.CSS_SELECTOR,
                'a[href$=".pdf"]'
            )
            for link in pdf_links:
                href = link.get_attribute('href')
                if href:
                    # Verify PDF path format
                    if not href.endswith('.pdf'):
                        self.results['warnings'].append(f"PDF link doesn't end with .pdf: {href}")
                    if 'pdfs/unit9/' not in href:
                        self.results['warnings'].append(f"PDF not in pdfs/unit9 directory: {href}")

            # Test video links
            video_links = self.driver.find_elements(
                By.CSS_SELECTOR,
                'a[href*="apclassroom.collegeboard.org"], a[href*="drive.google.com"]'
            )
            for link in video_links:
                href = link.get_attribute('href')
                if href:
                    # Verify AP Classroom link format
                    if 'apclassroom.collegeboard.org' in href:
                        if 'sui=33,9' not in href:
                            self.results['warnings'].append(f"AP Classroom link missing correct suite ID: {href}")
                    # Verify Google Drive link format
                    elif 'drive.google.com' in href:
                        if 'view?usp=drive_link' not in href:
                            self.results['warnings'].append(f"Google Drive link missing correct sharing parameters: {href}")

            # Verify Topic 9.1 videos specifically
            topic_91_videos = self.driver.find_elements(
                By.CSS_SELECTOR,
                '#topic-card-9-1 a[href*="apclassroom.collegeboard.org"], #topic-card-9-1 a[href*="drive.google.com"]'
            )
            if not topic_91_videos:
                self.results['warnings'].append("Topic 9.1 videos not found")
            else:
                for video in topic_91_videos:
                    href = video.get_attribute('href')
                    if not href or href.strip() == '':
                        self.results['warnings'].append("Topic 9.1 has empty video URL")

            self.results['passed'].append('Resource links')
        except Exception as e:
            self.results['failed'].append(f'Resource links - {str(e)}')

    def test_local_storage(self):
        """Test localStorage functionality"""
        print("\nTesting localStorage...")
        try:
            # Execute JavaScript to check localStorage
            storage = self.driver.execute_script(
                "return window.localStorage.getItem('apStatsTopicProgress');"
            )
            assert storage is not None
            
            # Verify it's valid JSON
            progress_data = json.loads(storage)
            assert isinstance(progress_data, list)
            
            self.results['passed'].append('localStorage functionality')
        except Exception as e:
            self.results['failed'].append(f'localStorage functionality - {str(e)}')

    def print_summary(self):
        """Print test results summary"""
        print("\n=== Test Summary ===")
        
        print("\n✓ Passed Tests:")
        for test in self.results['passed']:
            print(f"  - {test}")
            
        if self.results['failed']:
            print("\n✗ Failed Tests:")
            for test in self.results['failed']:
                print(f"  - {test}")
                print("    Details:")
                # Extract error message without stacktrace
                error_msg = str(test).split('Stacktrace:', 1)[0].strip()
                print(f"    {error_msg}")
                
        if self.results['warnings']:
            print("\n⚠ Warnings:")
            for warning in self.results['warnings']:
                print(f"  - {warning}")
        
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        success_rate = (len(self.results['passed']) / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\nTest Statistics:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {len(self.results['passed'])}")
        print(f"  Failed: {len(self.results['failed'])}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n✓ All web interface tests passed!")
        else:
            print("\n⚠ Some tests failed. Please review the issues above.")
            print("Suggestion: Run the test again - some failures might be due to timing issues.")

    def cleanup(self):
        """Clean up after tests"""
        self.driver.quit()

    def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            print("Starting web interface tests...")
            self.setup()
            
            # Run all tests
            self.test_tab_switching()
            self.test_grok_prompt()
            self.test_progress_tracking()
            self.test_resource_links()
            self.test_local_storage()
            
            self.print_summary()
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = WebInterfaceTester()
    tester.run_all_tests() 