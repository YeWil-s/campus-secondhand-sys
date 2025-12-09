from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=64, description="密码")
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$', description="手机号")
    campus_card: str = Field(..., min_length=1, max_length=20, description="校园卡号")

class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class UserResponse(BaseModel):
    user_id: str
    username: str
    phone: str
    campus_card: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    user_id: str
    username: str
    phone: str
    campus_card: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None