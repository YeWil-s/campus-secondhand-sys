from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
import os
import shutil
from datetime import datetime
from pathlib import Path
from database.models import User
from utils.security import get_current_user

router = APIRouter()

# 上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload", summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传商品图片"""
    
    # 检查文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片格式 (JPEG, PNG, GIF, WEBP)"
        )
    
    # 检查文件大小 (5MB)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过 5MB"
        )
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(file.filename)[1]
    filename = f"{current_user.user_id}_{timestamp}{ext}"
    file_path = UPLOAD_DIR / filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    return {
        "filename": filename,
        "url": f"/uploads/{filename}"
    }

@router.get("/uploads/{filename}", summary="获取上传的文件")
async def get_uploaded_file(filename: str):
    """获取上传的文件"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    return FileResponse(file_path)
