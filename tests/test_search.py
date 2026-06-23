# tests/test_search.py
import os
import sys
from dotenv import load_dotenv

# 1. Dynamically resolve the absolute repository root path
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_DIR = os.path.abspath(os.path.join(CURRENT_FILE_DIR, ".."))
if REPO_ROOT_DIR not in sys.path:
    sys.path.insert(0, REPO_ROOT_DIR)

# 2. Automatically load the environment variables from your root .env file
dotenv_path = os.path.join(REPO_ROOT_DIR, ".env")
load_dotenv(dotenv_path)

# 3. Import the actual production tool function from your codebase
from modules.gateway import fetch_live_market_data

if __name__ == "__main__":
    topic = "SpaceX SPCX post-IPO crash June 2026"
    print(f"--- TRIGGERING LIVE ROUTER LOGIC FOR: {topic} ---")
    
    # Run the live API search query step
    context = fetch_live_market_data(topic)
    
    # 4. INSULATE OUTPUTS INSIDE AN ARTIFACTS DIRECTORY
    artifacts_dir = os.path.join(REPO_ROOT_DIR, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)  # Create the directory if it's missing
    
    output_path = os.path.join(artifacts_dir, "last_search_result.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(context)
        
    print(f"\n[SUCCESS] Search results successfully stored in: {output_path}")