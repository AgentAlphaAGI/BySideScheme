from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.core.situation import SituationModel

class FactInput(BaseModel):
    user_id: str
    fact: str
    
class SituationUpdate(BaseModel):
    user_id: str
    situation: SituationModel

class MemoryQuery(BaseModel):
    user_id: str
    query: Optional[str] = None
    limit: int = 10

class AdviceResponse(BaseModel):
    decision: Dict[str, Any]
    narrative: Dict[str, Any]
    context_used: Dict[str, Any]
