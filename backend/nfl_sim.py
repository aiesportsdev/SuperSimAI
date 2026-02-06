import random

class NFLGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.yards = 25  # Starting yard line (0-100)
        self.down = 1
        self.yards_to_go = 10
        self.points_team_1 = 0
        self.points_team_2 = 0
        self.possession = 1 # Team 1 or 2
        
        # Game constants
        self.PTS_TD = 6
        self.PTS_FG = 3
        self.PTS_XP = 1
        
        # Log of events
        self.game_log = []

    def log(self, message):
        self.game_log.append(message)
        print(f"[NFL] {message}")

    def get_state(self):
        return {
            "yards": self.yards,
            "down": self.down,
            "to_go": self.yards_to_go,
            "score": f"{self.points_team_1} - {self.points_team_2}",
            "possession": self.possession
        }

    def switch_possession(self):
        self.possession = 2 if self.possession == 1 else 1
        self.yards = 100 - self.yards
        self.down = 1
        self.yards_to_go = 10
        self.log(f"Possession switched to Team {self.possession}")

    def score(self, points):
        if self.possession == 1:
            self.points_team_1 += points
        else:
            self.points_team_2 += points
        self.log(f"SCORE! Team {self.possession} gets {points} points.")

    def touchdown(self):
        self.score(self.PTS_TD)
        # Assume XP is automatic for now
        self.score(self.PTS_XP)
        self.kickoff()

    def kickoff(self):
        # Simple kickoff logic
        kick_dist = random.randint(40, 70)
        self.yards = 35 + kick_dist # Kicking from 35 standard
        if self.yards > 100:
            self.yards = 25 # Touchback
            self.log("Kickoff is a Touchback.")
        else:
            self.yards = 100 - self.yards # Return logic simplified
            self.log(f"Kickoff returned to the {self.yards} yard line.")
        
        self.switch_possession() # Wait, kickoff implies possession change BEFORE? 
        # Actually logic: Team A scores -> Team A kicks -> Team B gets ball.
        # So we just reset state for the receiving team.
        self.down = 1
        self.yards_to_go = 10

    def check_first_down(self):
        if self.yards_to_go <= 0:
            self.down = 1
            self.yards_to_go = 10
            self.log("FIRST DOWN!")
            return True
        return False

    def step(self, action_type):
        """
        Executes a play.
        action_type: 'PASS', 'RUN', 'PUNT', 'FG'
        Returns: play_result dict
        """
        result = {
            "type": action_type,
            "yards_gained": 0,
            "start_yard": self.yards,
            "end_yard": self.yards,
            "event": "normal" # TD, TURNOVER, INCOMPLETE
        }

        if action_type == 'PASS':
            roll = random.random()
            if roll < 0.6: # 60% completion
                gain = random.randint(5, 20)
                if random.random() < 0.1: gain += 30 # Big play
                result["yards_gained"] = gain
                self.yards += gain
                self.yards_to_go -= gain
                result["event"] = "complete"
                self.log(f"Pass complete for {gain} yards.")
            else:
                result["yards_gained"] = 0
                result["event"] = "incomplete"
                self.log("Pass incomplete.")
                self.down += 1

        elif action_type == 'RUN':
            gain = random.randint(-2, 8)
            if random.random() < 0.05: gain += 20 # Breakaway
            result["yards_gained"] = gain
            self.yards += gain
            self.yards_to_go -= gain
            self.log(f"Run for {gain} yards.")
            if gain == 0: self.down += 1

        elif action_type == 'PUNT':
            punt_dist = random.randint(30, 50)
            self.yards += punt_dist
            if self.yards > 100: self.yards = 80 # Touchback equivalent?
            self.switch_possession()
            self.log(f"Punted {punt_dist} yards.")
            return result # Turn ending

        # Check TD
        if self.yards >= 100:
            result["event"] = "TOUCHDOWN"
            self.touchdown()
            return result

        # Check First Down (if not TD)
        if result["event"] not in ["incomplete"] and action_type != 'PUNT':
             if not self.check_first_down():
                 self.down += 1

        # Turnover on downs
        if self.down > 4:
            self.log("Turnover on downs!")
            self.switch_possession()
            self.yards = 100 - self.yards # Ball control flips field side

        result["end_yard"] = self.yards
        return result
