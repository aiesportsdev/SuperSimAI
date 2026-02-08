import motor.motor_asyncio
import asyncio
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    uri = os.getenv("MONGO_URI")
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client.supersim_ai
    drives = db.drives
    latest = await drives.find().sort('created_at', -1).limit(1).to_list(1)
    if latest:
        drive = latest[0]
        print(f"Latest Drive ID: {drive['_id']}")
        print(f"Team Name: {drive.get('team_name')}")
        print(f"Outcome: {drive.get('outcome')}")
        print(f"Moltbook URL: {drive.get('moltbook_url')}")
        print(f"Created At: {drive.get('created_at')}")
    else:
        print("No drives found.")

if __name__ == "__main__":
    asyncio.run(check())
