import os
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Annotated

from dotenv import load_dotenv

load_dotenv()

# MongoDB Config
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in environment or .env file")

client = AsyncIOMotorClient(MONGO_URI)
db = client.supersim_ai

teams = db.get_collection("teams")

# Helper for ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]
