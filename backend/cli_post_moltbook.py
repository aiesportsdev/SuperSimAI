import requests
import sys
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

MOLTBOOK_API_URL = "https://www.moltbook.com/api/v1"
API_KEY = os.getenv("MOLTBOOK_API_KEY")

def post_moltbook(content, submolt="general", url=None):
    """Post to Moltbook"""
    if not API_KEY:
        print("❌ No API key found.")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "submolt": submolt,
        "title": "Coach Update",
        "content": content
    }
    if url:
        payload["url"] = url
        
    try:
        res = requests.post(f"{MOLTBOOK_API_URL}/posts", headers=headers, json=payload)
        res.raise_for_status()
        print(f"✅ Posted to Moltbook: {res.json().get('id', 'Unknown')}")
    except Exception as e:
        print(f"❌ Post failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True, help="Post content")
    parser.add_argument("--submolt", default="general", help="Submolt to post to")
    args = parser.parse_args()
    
    post_moltbook(args.content, args.submolt)
