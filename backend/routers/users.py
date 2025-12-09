from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from database import get_db
from database.models import User
from schemas.user import UserResponse
from utils.security import get_current_user

router = APIRouter()

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    campus_card: Optional[str] = None

@router.get("/profile", response_model=UserResponse, summary="获取用户信息")
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/profile", response_model=UserResponse, summary="更新用户信息")
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    
    if user_update.phone:
        # 检查手机号是否已被其他用户使用
        existing_user = db.query(User).filter(
            User.phone == user_update.phone,
            User.user_id != current_user.user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被其他用户使用"
            )
        current_user.phone = user_update.phone
    
    if user_update.campus_card:
        # 检查校园卡号是否已被其他用户使用
        existing_user = db.query(User).filter(
            User.campus_card == user_update.campus_card,
            User.user_id != current_user.user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="校园卡号已被其他用户使用"
            )
        current_user.campus_card = user_update.campus_card
    
    db.commit()
    db.refresh(current_user)
    
    return current_user