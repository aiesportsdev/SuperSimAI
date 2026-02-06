import requests
import json
import sys
from nfl_sim import NFLGame
from nfl_physics import NFLPhysicsWorld

def call_nfl_agent(game_state, strategy_prompt="Win the game"):
    """
    Calls Ollama to decide the next play.
    Uses the team's strategy_prompt to influence decisions.
    """
    prompt = f"""
    You are the Head Coach of an American Football team. 
    Your coaching style: {strategy_prompt}
    
    Game State:
    - Down: {game_state['down']}
    - Yards to Go: {game_state['to_go']}
    - Ball Position: {game_state['yards']} yard line
    - Score: {game_state['score']}
    
    Choose a play type: RUN or PASS.
    Provide your reasoning strictly in this format:
    ACTION: <RUN or PASS> | REASON: <Short explanation>
    """
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:1b", 
            "prompt": prompt,
            "stream": False
        })
        
        if response.status_code == 200:
            result = response.json().get("response", "")
            action = "RUN"
            reason = "Default decision"
            
            for line in result.split('\n'):
                if "ACTION:" in line.upper():
                    parts = line.split("|")
                    action = parts[0].split(":")[1].strip().upper()
                    if len(parts) > 1 and "REASON:" in parts[1].upper():
                        reason = parts[1].split(":", 1)[1].strip()
            
            # Sanity check
            if action not in ["RUN", "PASS"]: action = "RUN"
            return action, reason
            
        return "RUN", "LLM failed (Status)"
    except Exception as e:
        return "RUN", f"LLM error: {str(e)[:40]}"


def run_drive(team_name="Team", strategy_prompt="Play to win"):
    """
    Run a single drive challenge.
    Returns structured result with win/lose outcome.
    """
    game = NFLGame()
    physics_world = NFLPhysicsWorld()
    all_frames = []
    
    # Track stats for XP calculation
    stats = {
        "plays": 0,
        "total_yards": 0,
        "first_downs": 0,
        "completions": 0,
        "incompletions": 0
    }
    
    print(f"LOG:> Starting Drive Challenge for {team_name}...")
    print(f"LOG:> Strategy: {strategy_prompt}")
    print("LOG:> Coach (LLM) is connecting...")
    
    outcome = "in_progress"
    max_plays = 20  # Safety limit
    
    while outcome == "in_progress" and stats["plays"] < max_plays:
        stats["plays"] += 1
        
        # Get State
        state = game.get_state()
        
        # Add current state to frames for UI
        current_state = {
            "down": state["down"],
            "to_go": state["to_go"],
            "yard_line": state["yards"],
            "score": state["score"]
        }
        
        # Call LLM with team's strategy
        action, reason = call_nfl_agent(state, strategy_prompt)
        
        # Log Reasoning
        reason_log = f"🧠 Coach: {reason}"
        game.log(reason_log)
        print(f"LOG:> {reason_log}")
        
        # Record start position
        start_yard = game.yards
        prev_down = game.down
        
        # Execute Play
        result = game.step(action)
        
        # Track yards
        stats["total_yards"] += result["yards_gained"]
        
        # Track completions
        if action == "PASS":
            if result["event"] == "complete":
                stats["completions"] += 1
            else:
                stats["incompletions"] += 1
        
        # Check for first down
        if game.down == 1 and prev_down != 1 and result["event"] != "TOUCHDOWN":
            stats["first_downs"] += 1
        
        # Execute Physics
        print(f"LOG:> Simulating physical {action} play at {start_yard} yard line...")
        physics_world.setup_formation(start_yard)
        physics_world.run_play(action, steps=120)
        
        # Add game state to each frame
        for frame in physics_world.frames:
            frame["game_state"] = current_state
        
        all_frames.extend(physics_world.frames)
        physics_world.frames = []
        
        # Log Outcome
        outcome_log = f"Play {stats['plays']}: {result['type']} - {result['event']} ({result['yards_gained']} yds)"
        print(f"LOG:> {outcome_log}")
        
        # Check win condition (TD)
        if result["event"] == "TOUCHDOWN":
            outcome = "win"
            print(f"LOG:> 🎉 TOUCHDOWN! DRIVE SUCCESSFUL!")
            break
        
        # Check lose conditions
        if game.possession != 1:  # Possession changed = turnover
            outcome = "lose"
            print(f"LOG:> ❌ TURNOVER! DRIVE FAILED!")
            break
        
        if game.down > 4:  # 4th down stop
            outcome = "lose"
            print(f"LOG:> ❌ STOPPED ON DOWNS! DRIVE FAILED!")
            break
    
    # Calculate XP
    xp_earned = 0
    if outcome == "win":
        xp_earned = 100  # TD bonus
    else:
        xp_earned = 25  # Participation
    
    # Bonus XP for first downs
    xp_earned += stats["first_downs"] * 10
    
    # Final Result
    result = {
        "outcome": outcome,
        "team_name": team_name,
        "stats": stats,
        "xp_earned": xp_earned,
        "final_yard_line": game.yards,
        "frames": all_frames,
        "logs": game.game_log
    }
    
    return result


def get_simulation_result(num_plays=10):
    """Legacy function for backwards compatibility"""
    return run_drive("Demo Team", "Play aggressive, go for big plays.")


def run_simulation(num_plays=10):
    output = get_simulation_result(num_plays)
    print("JSON_RESULT:" + json.dumps(output))

if __name__ == "__main__":
    run_simulation()
