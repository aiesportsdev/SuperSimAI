import requests
import json
import sys
from nfl_sim import NFLGame
from nfl_physics import NFLPhysicsWorld

def call_nfl_agent(game_state, instruction="Win the game"):
    """
    Calls Ollama to decide the next play.
    """
    prompt = f"""
    You are the Head Coach of an American Football team. 
    Game State:
    - Down: {game_state['down']}
    - Yards to Go: {game_state['to_go']}
    - Ball Position: {game_state['yards']} yard line
    - Score: {game_state['score']}
    
    Instruction: {instruction}
    
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

def get_simulation_result(num_plays=10):
    game = NFLGame()
    physics_world = NFLPhysicsWorld() # Core physics engine
    all_frames = []
    
    print("LOG:> Starting NFL Physics-Driven Simulation...")
    print("LOG:> Coach (LLM) is connecting...")
    
    step_count = 0
    while step_count < num_plays:
        step_count += 1
        
        # Get State
        state = game.get_state()
        
        # Call LLM
        action, reason = call_nfl_agent(state)
        
        # Log Reasoning
        reason_log = f"🧠 Coach: {reason}"
        game.log(reason_log)
        print(f"LOG:> {reason_log}")
        
        # Execute Simple Play Logic
        start_yard = game.yards
        result = game.step(action)
        
        # Execute Physics Play Simulation (The "Real" Game Animation)
        print(f"LOG:> Simulating physical {action} play at {start_yard} yard line...")
        physics_world.setup_formation(start_yard)
        physics_world.run_play(action, steps=120) # 2.4 seconds of physics
        
        # Capture frames
        all_frames.extend(physics_world.frames)
        physics_world.frames = [] # Reset for next play
        
        # Log Outcome
        outcome_log = f"Play {step_count}: {result['type']} - {result['event']} ({result['yards_gained']} yds)"
        print(f"LOG:> {outcome_log}")
        
        if result["event"] == "TOUCHDOWN":
            print(f"LOG:> TOUCHDOWN SCORED!")
            break
            
        # Stop on turnover (implied if possession changed in simple sim)
        # We need to check possession change more robustly or just let it run a set number
        # For this prototype, we just run 'num_plays' unless TD
            
    # Final Result Object
    output = {
        "drill": "nfl_proto",
        "scenario": "drive_1",
        "success": True,
        "steps": len(all_frames),
        "reward": game.points_team_1,
        "frames": all_frames,
        "logs": game.game_log
    }
    return output

def run_simulation(num_plays=10):
    output = get_simulation_result(num_plays)
    # Output with prefix for easy parsing via subprocess if needed
    print("JSON_RESULT:" + json.dumps(output))

if __name__ == "__main__":
    run_simulation()
