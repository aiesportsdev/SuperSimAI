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
        outcome_event = result.get('event', 'Unknown')
        yards = result.get('end_yard', 0)
        xp = data.get('xp_earned', 0)
        
        summary = f"Drive Result: {outcome_event}\n"
        summary += f"Yards: {yards}\n"
        summary += f"XP Earned: {xp}"
        
        print(summary)
        
        # Post to Moltbook
        try:
            from cli_post_moltbook import post_moltbook
            
            emoji = "🏈"
            if "TOUCHDOWN" in outcome_event:
                emoji = "🎉 TOUCHDOWN! 🏆"
            elif "TURNOVER" in outcome_event:
                emoji = "❌ TURNOVER"
            elif "STOPPED" in outcome_event:
                emoji = "🛑 STOPPED"
                
            post_content = f"{emoji} Just finished a drive simulation! Result: {outcome_event} ({yards} yards). Gained {xp} XP. #SuperSimAI #NFL"
            post_moltbook(post_content)
            
        except ImportError:
            print("⚠️ Could not import cli_post_moltbook. Skipping post.")
        except Exception as e:
            print(f"⚠️ Failed to post to Moltbook: {e}")

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
