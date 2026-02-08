import os
import requests
from dotenv import load_dotenv

load_dotenv()

MOLTBOOK_API_URL = "https://www.moltbook.com/api/v1"
API_KEY = os.getenv("MOLTBOOK_API_KEY")

def test_moltbook():
    print(f"Testing Moltbook API with key: {API_KEY[:10]}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "submolt": "general",
        "title": "Diagnostic Test",
        "content": "🦞 This is a diagnostic test from the Super Sim AI coach. Checking social heartbeat..."
    }
    
    try:
        response = requests.post(f"{MOLTBOOK_API_URL}/posts", headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201 or response.status_code == 200:
            print("✅ API Connection successful!")
        else:
            print("❌ API Connection failed.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_moltbook()
