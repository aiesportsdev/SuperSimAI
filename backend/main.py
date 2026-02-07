from fastapi import FastAPI, HTTPException, Body, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
import os

from datetime import datetime, timedelta
from run_nfl_sim import get_simulation_result, run_drive
from database import db, teams
from schemas import NFLTeamModel, CreateTeamRequest

app = FastAPI(title="Super Sim AI API")

# CORS (Open for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= DRIVE CHALLENGE ENDPOINTS =============

class DriveRequest(BaseModel):
    team_id: str
    strategy_prompt: Optional[str] = None  # Custom strategy for this drive


@app.post("/drive/start")
async def start_drive(
    request: DriveRequest = Body(...),
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Start a Single Drive Challenge with selected team"""
    
    # 1. Fetch team from MongoDB
    team = await teams.find_one({"_id": ObjectId(request.team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # 2. Verify ownership
    if team.get("owner_wallet") and team["owner_wallet"] != x_wallet_address:
        raise HTTPException(status_code=403, detail="This is not your team")
    
    # 2.5 Rate Limit (5 mins)
    last_played = team.get("last_played_at")
    if last_played:
        # Simple check assuming datetime object
        if (datetime.utcnow() - last_played) < timedelta(minutes=5):
            remaining = 5 - int((datetime.utcnow() - last_played).total_seconds() / 60)
            raise HTTPException(
                status_code=429,
                detail=f"⏳ Coach is resting! Drills available in {remaining} min."
            )
    
    # 3. Run the drive simulation (use custom strategy if provided)
    strategy = request.strategy_prompt if request.strategy_prompt else team.get("strategy_prompt", "Play to win")
    result = run_drive(
        team_name=team.get("name", "My Team"),
        strategy_prompt=strategy
    )
    
    # 4. Update team stats in database
    update_data = {
        "$inc": {
            "coach_xp": result["xp_earned"]
        }
    }
    
    if result["outcome"] == "win":
        update_data["$inc"]["wins"] = 1
    else:
        update_data["$inc"]["losses"] = 1
    
    # Calculate new level based on XP
    current_xp = team.get("coach_xp", 0) + result["xp_earned"]
    new_level = 1
    if current_xp >= 2000:
        new_level = 5
    elif current_xp >= 1000:
        new_level = 4
    elif current_xp >= 500:
        new_level = 3
    elif current_xp >= 200:
        new_level = 2
    
    update_data["$set"] = {
        "coach_level": new_level,
        "last_played_at": datetime.utcnow()
    }
    
    await teams.update_one(
        {"_id": ObjectId(request.team_id)},
        update_data
    )
    
    # 5. Get updated team data
    updated_team = await teams.find_one({"_id": ObjectId(request.team_id)})
    updated_team["_id"] = str(updated_team["_id"])
    
    # 6. Return result with team data
    result["team"] = updated_team
    return result


# ============= LEGACY GAME ENDPOINT =============

@app.post("/nfl/play")
async def play_nfl_game():
    """Run a drive simulation with LLM coach (legacy)"""
    return get_simulation_result(num_plays=10)


# ============= AI-POWERED DRIVE PLAY =============

class PlayRequest(BaseModel):
    team_id: str
    user_play: str  # RUN, PASS, PUNT, FG
    game_state: dict  # down, yards_to_go, field_position, etc.


class GameSession:
    """Simple in-memory game state (for MVP - should be Redis/DB later)"""
    sessions = {}
    
    @classmethod
    def get_or_create(cls, team_id: str) -> dict:
        if team_id not in cls.sessions:
            cls.sessions[team_id] = {
                "down": 1,
                "yards_to_go": 10,
                "field_position": 20,
                "score_user": 0,
                "score_ai": 0,
                "plays": []
            }
        return cls.sessions[team_id]
    
    @classmethod
    def reset(cls, team_id: str):
        if team_id in cls.sessions:
            del cls.sessions[team_id]


@app.post("/drive/play")
async def execute_play(
    request: PlayRequest = Body(...),
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """
    Execute a single play with OpenClaw AI as defender.
    User picks offense, AI picks defense, physics engine resolves.
    """
    from openclaw_client import get_ai_decision
    import random
    
    # 1. Get game state
    session = GameSession.get_or_create(request.team_id)
    game_state = {
        **session,
        "user_play": request.user_play
    }
    
    # 2. Ask OpenClaw AI for defensive play
    ai_decision = get_ai_decision(game_state, role="defense")
    ai_play = ai_decision.get("play", "ZONE")
    trash_talk = ai_decision.get("trash_talk", "")
    
    # 3. Simulate play outcome
    # Calculate yards based on matchup
    user_play = request.user_play.upper()
    
    if user_play == "PASS":
        if ai_play == "BLITZ":
            # Blitz vs Pass: high risk/reward
            if random.random() < 0.4:
                yards = -5  # Sack
                event = "SACK"
            else:
                yards = random.randint(5, 25)
                event = "COMPLETE" if yards > 0 else "INCOMPLETE"
        elif ai_play == "ZONE":
            yards = random.randint(-2, 15)
            event = "COMPLETE" if yards > 0 else "INCOMPLETE"
        elif ai_play == "MAN":
            yards = random.randint(0, 20) if random.random() > 0.35 else 0
            event = "COMPLETE" if yards > 0 else "INCOMPLETE"
        else:  # PREVENT
            yards = random.randint(3, 12)
            event = "COMPLETE"
    
    elif user_play == "RUN":
        if ai_play == "BLITZ":
            yards = random.randint(-2, 8)
        elif ai_play == "ZONE":
            yards = random.randint(1, 6)
        elif ai_play == "MAN":
            yards = random.randint(2, 10)
        else:  # PREVENT
            yards = random.randint(4, 8)
        event = "RUSH"
    
    elif user_play == "PUNT":
        yards = -40  # Kick away
        event = "PUNT"
        GameSession.reset(request.team_id)
        return {
            "result": "PUNT",
            "ai_play": ai_play,
            "ai_trash_talk": "Scared already? 😏",
            "drive_over": True,
            "outcome": "loss"
        }
    
    elif user_play == "FG":
        # Field goal attempt
        fg_distance = 100 - session["field_position"] + 17
        success_chance = max(0, 1 - (fg_distance - 20) * 0.02)
        if random.random() < success_chance:
            session["score_user"] += 3
            event = "FIELD_GOAL"
            GameSession.reset(request.team_id)
            return {
                "result": "FIELD_GOAL",
                "ai_play": ai_play,
                "ai_trash_talk": "Lucky kick... 🍀",
                "drive_over": True,
                "outcome": "win",
                "xp_earned": 30
            }
        else:
            event = "MISSED_FG"
            GameSession.reset(request.team_id)
            return {
                "result": "MISSED_FG",
                "ai_play": ai_play,
                "ai_trash_talk": "WIDE RIGHT! 😂",
                "drive_over": True,
                "outcome": "loss"
            }
    else:
        yards = 0
        event = "UNKNOWN"
    
    # 4. Update game state
    session["field_position"] += yards
    session["yards_to_go"] -= yards
    session["plays"].append({
        "user": user_play,
        "ai": ai_play,
        "yards": yards,
        "event": event
    })
    
    # Check for touchdown
    if session["field_position"] >= 100:
        session["score_user"] += 7
        GameSession.reset(request.team_id)
        return {
            "result": "TOUCHDOWN",
            "yards": yards,
            "ai_play": ai_play,
            "ai_trash_talk": "You got me this time... 😤",
            "drive_over": True,
            "outcome": "win",
            "xp_earned": 100
        }
    
    # Check for first down
    if session["yards_to_go"] <= 0:
        session["down"] = 1
        session["yards_to_go"] = 10
        first_down = True
    else:
        session["down"] += 1
        first_down = False
    
    # Check for turnover on downs
    if session["down"] > 4:
        GameSession.reset(request.team_id)
        return {
            "result": "TURNOVER_ON_DOWNS",
            "yards": yards,
            "ai_play": ai_play,
            "ai_trash_talk": "My ball now! 🏈",
            "drive_over": True,
            "outcome": "loss"
        }
    
    # 5. Return result
    return {
        "result": event,
        "yards": yards,
        "first_down": first_down,
        "ai_play": ai_play,
        "ai_trash_talk": trash_talk,
        "drive_over": False,
        "new_state": {
            "down": session["down"],
            "yards_to_go": session["yards_to_go"],
            "field_position": session["field_position"],
            "score_user": session["score_user"],
            "score_ai": session["score_ai"]
        }
    }


@app.post("/drive/reset")
async def reset_drive(team_id: str = Body(..., embed=True)):
    """Reset the current drive session"""
    GameSession.reset(team_id)
    return {"status": "reset"}


# ============= TOURNAMENT ENDPOINTS =============

class TournamentStore:
    """In-memory tournament storage (MVP - use MongoDB later)"""
    tournaments = {}
    counter = 0
    
    @classmethod
    def create(cls, name: str, creator_team_id: str) -> dict:
        cls.counter += 1
        tournament = {
            "id": f"tournament_{cls.counter}",
            "name": name,
            "status": "open",  # open, in_progress, completed
            "participants": [creator_team_id],
            "matches": [],
            "winner": None,
            "created_at": None  # Would use datetime in production
        }
        cls.tournaments[tournament["id"]] = tournament
        return tournament
    
    @classmethod
    def get(cls, tournament_id: str) -> dict:
        return cls.tournaments.get(tournament_id)
    
    @classmethod
    def list_open(cls) -> list:
        return [t for t in cls.tournaments.values() if t["status"] == "open"]


class TournamentRequest(BaseModel):
    team_id: str
    name: Optional[str] = "Super Sim Tournament"


@app.get("/tournaments")
async def list_tournaments():
    """List all open tournaments"""
    return TournamentStore.list_open()


@app.post("/tournaments/create")
async def create_tournament(
    request: TournamentRequest = Body(...),
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Create a new tournament (requires Level 5+)"""
    
    # 1. Fetch team and verify level
    team = await teams.find_one({"_id": ObjectId(request.team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.get("coach_level", 1) < 5:
        raise HTTPException(
            status_code=403, 
            detail=f"🔒 Level 5 required to create tournaments. You are Level {team.get('coach_level', 1)}. Keep grinding those drills!"
        )
    
    # 2. Verify ownership
    if team.get("owner_wallet") and team["owner_wallet"] != x_wallet_address:
        raise HTTPException(status_code=403, detail="This is not your team")
    
    # 3. Create tournament
    tournament = TournamentStore.create(request.name, request.team_id)
    
    return {
        "message": "🏆 Tournament created!",
        "tournament": tournament
    }


@app.post("/tournaments/{tournament_id}/join")
async def join_tournament(
    tournament_id: str,
    request: TournamentRequest = Body(...),
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Join an existing tournament (requires Level 5+)"""
    
    # 1. Fetch team and verify level
    team = await teams.find_one({"_id": ObjectId(request.team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.get("coach_level", 1) < 5:
        raise HTTPException(
            status_code=403,
            detail=f"🔒 Level 5 required for tournaments. You are Level {team.get('coach_level', 1)}. Keep playing drills to level up!"
        )
    
    # 2. Verify ownership
    if team.get("owner_wallet") and team["owner_wallet"] != x_wallet_address:
        raise HTTPException(status_code=403, detail="This is not your team")
    
    # 3. Get tournament
    tournament = TournamentStore.get(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    if tournament["status"] != "open":
        raise HTTPException(status_code=400, detail="Tournament is not open for joining")
    
    if request.team_id in tournament["participants"]:
        raise HTTPException(status_code=400, detail="Already joined this tournament")
    
    # 4. Join
    tournament["participants"].append(request.team_id)
    
    return {
        "message": "✅ Joined tournament!",
        "tournament": tournament
    }


@app.post("/tournaments/{tournament_id}/start")
async def start_tournament(
    tournament_id: str,
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Start a tournament (runs AI vs AI matches)"""
    from openclaw_client import get_ai_decision
    import random
    
    tournament = TournamentStore.get(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    if len(tournament["participants"]) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 participants")
    
    tournament["status"] = "in_progress"
    
    # Run round-robin matches (simplified for MVP)
    participants = tournament["participants"]
    matches = []
    
    for i, team1_id in enumerate(participants):
        for team2_id in participants[i+1:]:
            # Simulate a quick match: each team gets 4 plays
            team1_score = 0
            team2_score = 0
            plays = []
            
            for play_num in range(4):
                # Team 1 offense
                offense_play = get_ai_decision({"down": 1, "yards_to_go": 10}, "offense")
                defense_play = get_ai_decision({"down": 1, "yards_to_go": 10, "user_play": offense_play["play"]}, "defense")
                yards = random.randint(-2, 15) if offense_play["play"] == "PASS" else random.randint(1, 8)
                if yards > 10:
                    team1_score += 7
                plays.append({"team": team1_id, "play": offense_play["play"], "yards": yards})
                
                # Team 2 offense
                offense_play = get_ai_decision({"down": 1, "yards_to_go": 10}, "offense")
                defense_play = get_ai_decision({"down": 1, "yards_to_go": 10, "user_play": offense_play["play"]}, "defense")
                yards = random.randint(-2, 15) if offense_play["play"] == "PASS" else random.randint(1, 8)
                if yards > 10:
                    team2_score += 7
                plays.append({"team": team2_id, "play": offense_play["play"], "yards": yards})
            
            match = {
                "team1": team1_id,
                "team2": team2_id,
                "team1_score": team1_score,
                "team2_score": team2_score,
                "winner": team1_id if team1_score > team2_score else (team2_id if team2_score > team1_score else "TIE"),
                "plays": plays
            }
            matches.append(match)
    
    tournament["matches"] = matches
    tournament["status"] = "completed"
    
    # Determine overall winner (most match wins)
    win_counts = {}
    for match in matches:
        winner = match["winner"]
        if winner != "TIE":
            win_counts[winner] = win_counts.get(winner, 0) + 1
    
    if win_counts:
        tournament["winner"] = max(win_counts, key=win_counts.get)
    
    return {
        "message": "🏆 Tournament complete!",
        "tournament": tournament
    }


@app.get("/tournaments/{tournament_id}")
async def get_tournament(tournament_id: str):
    """Get tournament details"""
    tournament = TournamentStore.get(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


# ============= TEAM ENDPOINTS =============

@app.post("/teams")
async def create_team(
    team: CreateTeamRequest = Body(...),
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Create a new team linked to wallet address"""
    
    # 0. Check Limits (1 Team until Level 5)
    if x_wallet_address:
        existing_teams = await teams.find({"owner_wallet": x_wallet_address}).to_list(length=10)
        if len(existing_teams) >= 1:
            highest_level = max([t.get("coach_level", 1) for t in existing_teams], default=1)
            if highest_level < 5:
                 raise HTTPException(
                    status_code=403,
                    detail=f"🔒 Limit Reached! Train your current team to Level 5 before creating another. (Current Max: Lv.{highest_level})"
                 )

    team_dict = {
        "name": team.name,
        "coach_name": team.coach_name,
        "strategy_prompt": team.strategy_prompt,
        "owner_wallet": x_wallet_address,
        "attributes": {"aggression": 50, "passing_focus": 50, "risk_taking": 50},
        "eliza_profile": {"bio": "A legendary AI football coach.", "style": "calculated and tactical"},
        "coach_xp": 0,
        "coach_level": 1,
        "wins": 0,
        "losses": 0,
        "team_color_primary": "#ff6b35",
        "team_color_secondary": "#ffa500"
    }
    
    result = await teams.insert_one(team_dict)
    team_dict["_id"] = str(result.inserted_id)
    return team_dict


@app.get("/teams")
async def list_teams():
    """List all teams"""
    cursor = teams.find()
    result = []
    async for team in cursor:
        team["_id"] = str(team["_id"])
        result.append(team)
    return result


@app.get("/teams/mine")
async def get_my_teams(
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Get teams owned by connected wallet"""
    if not x_wallet_address:
        return []
    
    cursor = teams.find({"owner_wallet": x_wallet_address})
    result = []
    async for team in cursor:
        team["_id"] = str(team["_id"])
        result.append(team)
    return result


@app.get("/teams/{team_id}")
async def get_team(team_id: str):
    """Get a specific team by ID"""
    team = await teams.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team["_id"] = str(team["_id"])
    return team


@app.put("/teams/{team_id}")
async def update_team(
    team_id: str,
    team_update: NFLTeamModel = Body(...),
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Update team (must be owner)"""
    existing = await teams.find_one({"_id": ObjectId(team_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check ownership
    if existing.get("owner_wallet") and existing["owner_wallet"] != x_wallet_address:
        raise HTTPException(status_code=403, detail="Not authorized to edit this team")
    
    update_data = team_update.model_dump(exclude_unset=True, by_alias=True)
    update_data.pop("_id", None)
    update_data.pop("id", None)
    
    await teams.update_one(
        {"_id": ObjectId(team_id)},
        {"$set": update_data}
    )
    
    updated = await teams.find_one({"_id": ObjectId(team_id)})
    updated["_id"] = str(updated["_id"])
    return updated


@app.delete("/teams/{team_id}")
async def delete_team(
    team_id: str,
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Delete team (must be owner)"""
    existing = await teams.find_one({"_id": ObjectId(team_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if existing.get("owner_wallet") and existing["owner_wallet"] != x_wallet_address:
        raise HTTPException(status_code=403, detail="Not authorized to delete this team")
    
    await teams.delete_one({"_id": ObjectId(team_id)})
    return {"status": "deleted", "team_id": team_id}


# ============= STATIC FILES =============
# Serve Frontend Static Files (must be last - catches all routes)
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    print("🏈 Starting Super Sim AI Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
