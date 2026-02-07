from datetime import datetime
from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional
from typing_extensions import Annotated

# MongoDB ID Helper
PyObjectId = Annotated[str, BeforeValidator(str)]


class NFLTeamModel(BaseModel):
    """NFL Team with AI Coach configuration"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    owner_wallet: Optional[str] = None  # Solana wallet address
    
    # Coach Configuration
    coach_name: str = "AI Coach"
    strategy_prompt: str = "Play aggressive, go for big plays."
    
    # Team Attributes (affect AI decision making)
    attributes: dict = {
        "aggression": 50,      # 0-100: Conservative to Aggressive
        "passing_focus": 50,   # 0-100: Run-heavy to Pass-heavy  
        "risk_taking": 50      # 0-100: Safe plays to Risky plays
    }
    
    # Coach Persona for LLM
    eliza_profile: dict = {
        "bio": "A legendary AI football coach.",
        "style": "calculated and tactical"
    }
    
    # Progression
    coach_xp: int = 0
    coach_level: int = 1
    wins: int = 0
    losses: int = 0
    
    # Visuals
    team_color_primary: str = "#ff6b35"
    team_color_secondary: str = "#ffa500"
    
    # Rate Limiting
    last_played_at: Optional[datetime] = None


class CreateTeamRequest(BaseModel):
    """Request body for creating a new team"""
    name: str
    coach_name: str = "AI Coach"
    strategy_prompt: str = "Play aggressive, go for big plays."
