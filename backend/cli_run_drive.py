import requests
import sys
import json
import argparse

BACKEND_URL = "http://localhost:8000"

def get_or_create_team(wallet):
    """Get existing team or create one"""
    headers = {"x-wallet-address": wallet}
    try:
        # 1. Try to find existing team
        res = requests.get(f"{BACKEND_URL}/teams/mine", headers=headers)
        if res.status_code == 200:
            teams = res.json()
            if teams:
                print(f"✅ Found existing team: {teams[0]['name']} ({teams[0]['_id']})")
                return teams[0]['_id']
                
        # 2. Create new team if none found
        print("🌱 Creating new team for agent...")
        payload = {
            "name": "Super Sim Coach Team",
            "coach_name": "Coach Prime",
            "strategy_prompt": "Aggressive vertical passing"
        }
        res = requests.post(f"{BACKEND_URL}/teams", json=payload, headers=headers)
        res.raise_for_status()
        team = res.json()
        print(f"✅ Created new team: {team['name']} ({team['_id']})")
        return team['_id']
    except Exception as e:
        print(f"❌ Failed to get/create team: {e}")
        return None

def run_drive(team_id, wallet="0xAgent"):
    """Run a drive simulation"""
    print(f"🏈 Starting drive for team {team_id}...")
    try:
        # Create a payload compatible with the endpoint
        # Start drive
        res = requests.post(
            f"{BACKEND_URL}/drive/start", 
            json={"team_id": team_id},
            headers={"x-wallet-address": wallet}
        )
        res.raise_for_status()
        data = res.json()
        
        # Parse result
        result = data.get("result", {})
        summary = f"Drive Result: {result.get('event', 'Unknown')}\n"
        summary += f"Yards: {result.get('end_yard', 0)}\n"
        summary += f"XP Earned: {data.get('xp_earned', 0)}"
        
        print(summary)
        return data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", default=None, help="Team ID (optional, will fetch/create if missing)")
    args = parser.parse_args()
    
    wallet = "0xAgent"
    team_id = args.team
    
    if not team_id:
        team_id = get_or_create_team(wallet)
        
    if team_id:
        run_drive(team_id, wallet)
