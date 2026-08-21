from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from ..ai.service import chat_with_ai, generate_insights
from ..database import get_db

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AIChatRequest(BaseModel):
    message: str
    context_page: Optional[str] = None


@router.post("/ai/chat")
async def ai_chat(request: AIChatRequest, db: Session = Depends(get_db)):
    """Chat endpoint grounded in verified backend metrics."""
    return await chat_with_ai(
        message=request.message,
        context_page=request.context_page,
        db=db,
    )


@router.get("/ai/insights")
def ai_insights(
    period: int = Query(None, description="Reporting period ID"),
    db: Session = Depends(get_db),
):
    """Automated insights generated from verified data."""
    return {"insights": generate_insights(db, period_id=period)}
