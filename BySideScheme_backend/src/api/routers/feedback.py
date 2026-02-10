from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from src.core.database import DatabaseManager
from src.core.logger import logger

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    user_id: str
    fact: Optional[str] = None
    advice_result: Optional[Dict[str, Any]] = None
    rating: int  # 1-5
    comment: Optional[str] = None

@router.post("/submit")
async def submit_feedback(request: FeedbackRequest):
    """
    提交用户对建议的反馈
    """
    db = DatabaseManager() # Should ideally be injected, but for now this works as it handles its own connection
    
    feedback_id = str(uuid.uuid4())
    feedback_data = {
        "id": feedback_id,
        "user_id": request.user_id,
        "fact": request.fact,
        "advice_result": request.advice_result,
        "rating": request.rating,
        "comment": request.comment
    }
    
    db.save_feedback(feedback_data)
    logger.info(f"Received feedback from user {request.user_id} with rating {request.rating}")
    
    return {"message": "Feedback received", "id": feedback_id}
