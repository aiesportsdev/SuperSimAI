from fastapi import FastAPI, HTTPException, Body, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from bson import ObjectId
import os

from run_nfl_sim import get_simulation_result
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


# ============= GAME ENDPOINTS =============

@app.post("/nfl/play")
async def play_nfl_game():
    """Run a drive simulation with LLM coach"""
    return get_simulation_result(num_plays=10)


# ============= TEAM ENDPOINTS =============

@app.post("/teams")
async def create_team(
    team: CreateTeamRequest = Body(...),
    x_wallet_address: Optional[str] = Header(None, alias="x-wallet-address")
):
    """Create a new team linked to wallet address"""
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
