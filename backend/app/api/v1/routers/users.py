from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.sql import user as user_model
from app.schemas import user as user_schema
from app.api.v1.deps import get_current_user
from app.core.database import get_db

router = APIRouter()


@router.get("/me", response_model=user_schema.UserMeResponse)
async def get_current_user_info(
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the currently authenticated user.
    """
    return current_user
