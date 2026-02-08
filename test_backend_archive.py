
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

# Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "supersim_ai"

async def test_backend():
    print(f"Connecting to {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    # 1. Get a Team
    team = await db.teams.find_one({})
    if not team:
        print("No teams found. Please create a team via frontend first.")
        # Create dummy team
        res = await db.teams.insert_one({"name": "Test Team", "coach_xp": 0})
        team_id = res.inserted_id
        print(f"Created Test Team: {team_id}")
    else:
        team_id = team["_id"]
        print(f"Found Team: {team['name']} ({team_id})")

    # 2. Insert Dummy Drive
    drive_data = {
        "team_id": team_id,
        "team_name": team.get("name", "Test Team"),
        "opponent": "Commanders",
        "outcome": "win",
        "score": "24-17",
        "xp_earned": 100,
        "created_at": datetime.utcnow(),
        "frames": [], # Empty for test
        "logs": ["Log 1", "Log 2"],
        "stats": {"plays": 10}
    }
    
    res = await db.drives.insert_one(drive_data)
    drive_id = res.inserted_id
    print(f"Inserted Drive: {drive_id}")
    
    # 3. Verify Fetch (Simulation of API)
    # Get History
    cursor = db.drives.find(
        {"team_id": team_id},
        {"frames": 0, "logs": 0}
    ).sort("created_at", -1)
    
    print("\n--- Drive History (API /teams/{id}/drives) ---")
    async for drive in cursor:
        print(f"- {drive['created_at']} | {drive['outcome'].upper()} {drive['score']} vs {drive['opponent']} (ID: {drive['_id']})")
        if "frames" in drive:
            print("  ERROR: Frames included in history list!")
            
    # Get Single Drive
    print(f"\n--- Single Replay (API /drives/{drive_id}) ---")
    replay = await db.drives.find_one({"_id": drive_id})
    if replay:
        print(f"Found Replay: {replay['_id']}")
        print(f"Frames Count: {len(replay['frames'])}")
        print(f"Logs Count: {len(replay['logs'])}")
    else:
        print("ERROR: Replay not found.")

if __name__ == "__main__":
    asyncio.run(test_backend())
