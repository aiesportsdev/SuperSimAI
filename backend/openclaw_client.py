"""
OpenClaw Gateway Client
Communicates with local OpenClaw gateway for AI decisions
"""
import requests
import json
import os

OPENCLAW_GATEWAY = os.getenv("OPENCLAW_GATEWAY", "http://127.0.0.1:18789")
OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "supersim-secret-token")


def get_ai_decision(game_state: dict, role: str = "defense") -> dict:
    """
    Ask OpenClaw AI for a play decision based on game state.
    
    Args:
        game_state: Current game situation (down, yards, position, etc.)
        role: "defense" or "offense"
    
    Returns:
        dict with 'play' (the AI's choice) and 'trash_talk' (optional message)
    """
    
    # Build prompt for the AI
    if role == "defense":
        prompt = f"""You are an AI defensive coordinator. The offense just called their play.

GAME STATE:
- Down: {game_state.get('down', 1)}
- Yards to go: {game_state.get('yards_to_go', 10)}
- Field position: {game_state.get('field_position', 20)} yard line
- User's play: {game_state.get('user_play', 'UNKNOWN')}

Choose your defensive play. Respond with ONLY a JSON object:
{{"play": "BLITZ" or "ZONE" or "MAN" or "PREVENT", "trash_talk": "short competitive message"}}
"""
    else:
        prompt = f"""You are an AI offensive coordinator.

GAME STATE:
- Down: {game_state.get('down', 1)}
- Yards to go: {game_state.get('yards_to_go', 10)}
- Field position: {game_state.get('field_position', 20)} yard line

Choose your offensive play. Respond with ONLY a JSON object:
{{"play": "RUN" or "PASS" or "PUNT" or "FG", "trash_talk": "short competitive message"}}
"""

    try:
        import subprocess
        
        # Use openclaw CLI to get AI decision
        result = subprocess.run(
            [
                "openclaw", "agent",
                "--to", "+15550000000",
                "--message", prompt,
                "--json"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            import json as json_mod
            try:
                response = json_mod.loads(result.stdout)
                ai_text = response.get("reply", response.get("content", ""))
                
                # Try to extract JSON from response
                start = ai_text.find("{")
                end = ai_text.rfind("}") + 1
                if start >= 0 and end > start:
                    ai_decision = json.loads(ai_text[start:end])
                    return {
                        "play": ai_decision.get("play", "ZONE"),
                        "trash_talk": ai_decision.get("trash_talk", "Let's see what you got! 🏈")
                    }
            except:
                pass
            
            # Fallback: extract play from text
            ai_upper = result.stdout.upper()
            if "BLITZ" in ai_upper:
                play = "BLITZ"
            elif "MAN" in ai_upper:
                play = "MAN"
            elif "PREVENT" in ai_upper:
                play = "PREVENT"
            else:
                play = "ZONE"
            
            return {"play": play, "trash_talk": "Here comes the heat! 🔥"}
        else:
            print(f"OpenClaw CLI error: {result.stderr}")
            return _fallback_decision(game_state, role)
            
    except Exception as e:
        print(f"OpenClaw error: {e}")
        return _fallback_decision(game_state, role)


def _fallback_decision(game_state: dict, role: str) -> dict:
    """Fallback AI when OpenClaw is unavailable"""
    down = game_state.get('down', 1)
    yards = game_state.get('yards_to_go', 10)
    
    if role == "defense":
        # Simple heuristic
        if down >= 3 and yards > 5:
            play = "PREVENT"
        elif yards <= 2:
            play = "BLITZ"
        else:
            play = "ZONE"
        return {"play": play, "trash_talk": "Bring it on! 💪"}
    else:
        if down == 4:
            play = "PUNT" if yards > 3 else "RUN"
        elif yards <= 2:
            play = "RUN"
        else:
            play = "PASS"
        return {"play": play, "trash_talk": "Watch this! 🏈"}


# Test function
if __name__ == "__main__":
    test_state = {
        "down": 3,
        "yards_to_go": 7,
        "field_position": 45,
        "user_play": "PASS"
    }
    result = get_ai_decision(test_state, "defense")
    print(f"AI Decision: {result}")
