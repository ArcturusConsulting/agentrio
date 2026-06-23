# tests/test_site_scraper.py
import os
import sys

# Resolve repository root path and add to python path
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_DIR = os.path.abspath(os.path.join(CURRENT_FILE_DIR, ".."))
if REPO_ROOT_DIR not in sys.path:
    sys.path.insert(0, REPO_ROOT_DIR)

from modules.gateway import fetch_target_site_content

def test_scraper():
    # Test URL - feel free to swap this out with your target domain!
    test_url = "https://www.google.com" 
    
    print(f"--- TESTING SCRAPER ON: {test_url} ---")
    content = fetch_target_site_content(test_url)
    
    print("\n--- RESULTS ---")
    print(f"Returned Character Count: {len(content)}")
    print(f"Content Preview:\n{content[:500]}...\n")

if __name__ == "__main__":
    test_scraper()