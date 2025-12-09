from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from database.models import User
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from utils.security import verify_password, get_password_hash, create_access_token
from utils.helpers import generate_user_id, validate_phone, validate_campus_card
from config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册接口"""
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否已存在
    if db.query(User).filter(User.phone == user.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被注册"
        )
    
    # 检查校园卡号是否已存在
    if db.query(User).filter(User.campus_card == user.campus_card).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="校园卡号已被注册"
        )
    
    # 验证手机号格式
    if not validate_phone(user.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 验证校园卡号格式
    if not validate_campus_card(user.campus_card):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="校园卡号格式不正确"
        )
    
    # 创建新用户
    user_id = generate_user_id()
    hashed_password = get_password_hash(user.password)
    
    db_user = User(
        user_id=user_id,
        username=user.username,
        password=hashed_password,
        phone=user.phone,
        campus_card=user.campus_card
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token, summary="用户登录")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """用户登录接口"""
    
    # 查找用户
    db_user = db.query(User).filter(User.username == user.username).first()
    
    # 验证用户和密码
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.user_id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}