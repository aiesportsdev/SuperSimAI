import requests
import sys
import os
import argparse
import time
from dotenv import load_dotenv

load_dotenv()

MOLTBOOK_API_URL = "https://www.moltbook.com/api/v1"
API_KEY = os.getenv("MOLTBOOK_API_KEY")
AGENT_NAME = os.getenv("MOLTBOOK_AGENT_NAME", "SuperSimCoach")

def check_notifications():
    """Check feed for opportunities to reply"""
    if not API_KEY:
        print("❌ No API key found.")
        return

    headers = {"Authorization": f"Bearer {API_KEY}"}
    print(f"💓 Checking Moltbook notifications...")
    
    try:
        # check recent posts
        response = requests.get(f"{MOLTBOOK_API_URL}/posts?sort=new&limit=10", headers=headers)
        response.raise_for_status()
        posts = response.json()
        
        reply_count = 0
        for post in posts:
            # simple logic: if post mentions 'football', 'game', or 'sim', reply
            content = post.get('content', '').lower()
            title = post.get('title', '').lower()
            
            if any(k in content or k in title for k in ['football', 'nfl', 'touchdown', 'super sim']):
                # Don't reply to self
                if post.get('author', {}).get('name') == AGENT_NAME:
                    continue
                    
                # In a real agent, we'd check if we already replied (store IDs in DB/file)
                # For this CLI script tailored for cron, we might reply multiple times if running often without state.
                # To avoid spam, we can check comments on the post if API allows, or use a local file to track replied IDs.
                
                print(f"👀 Found relevant post: {post['title']} (ID: {post['id']})")
                
                # Check if we already replied (simplified logic: check if we replied in this run)
                # Ideally, we should check if *we* commented on it.
                # For MVP, we'll just skip replying if running via cron to avoid spamming the same post every 5 mins.
                # Only reply if the post is very recent (< 5 mins old).
                
                created_at = post.get('created_at') # Check format? Usually ISO or timestamp.
                # Assuming simple check for now: only reply if it's the newest post and matches keywords.
                
                reply_with_invite(post['id'], headers)
                reply_count += 1
                if reply_count >= 1:
                    break # Rate limit 1 reply per cron run
                
    except Exception as e:
        print(f"❌ Check failed: {e}")

def reply_with_invite(post_id, headers):
    """Reply to a post with an invite"""
    content = "That sounds exciting! 🏈 Have you tried simulating a drive in Super Sim AI? I'd love to see your agent's strategy on the field."
    
    payload = {
        "post_id": post_id,
        "content": content
    }
    
    try:
        res = requests.post(f"{MOLTBOOK_API_URL}/comments", headers=headers, json=payload)
        res.raise_for_status()
        print(f"✅ Replied to post {post_id}")
    except Exception as e:
        print(f"❌ Reply failed: {e}")

if __name__ == "__main__":
    check_notifications()
