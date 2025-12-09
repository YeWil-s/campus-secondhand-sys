from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20, description="商品名称")
    description: Optional[str] = Field(None, max_length=500, description="商品描述")
    price: float = Field(..., ge=0, description="商品价格（元）")
    category_id: int = Field(..., gt=0, description="商品分类ID")
    image_path: Optional[str] = Field(None, description="商品图片路径")
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('价格不能为负')
        return int(v * 100)  # 转换为分


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=20, description="商品名称")
    description: Optional[str] = Field(None, max_length=500, description="商品描述")
    price: Optional[float] = Field(None, gt=0, description="商品价格（元）")
    status: Optional[int] = Field(None, ge=0, le=3, description="商品状态")
    category_id: Optional[int] = Field(None, gt=0, description="商品分类ID")  # 新增：支持更新分类
    image_path: Optional[str] = Field(None, description="商品图片路径")  # 新增：支持更新图片路径

    @field_validator('price')
    def validate_price(cls, v):
        """价格非空时，转换为分并校验"""
        if v is None:
            return v
        if v <= 0:
            raise ValueError('价格必须大于0')
        return int(round(v * 100))

class ProductSearch(BaseModel):
    keyword: Optional[str] = Field(None, description="搜索关键词")
    category_id: Optional[int] = Field(None, gt=0, description="分类ID")
    min_price: Optional[float] = Field(None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(None, ge=0, description="最高价格")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")

class ProductResponse(BaseModel):
    product_id: str
    name: str
    description: Optional[str]
    price: float  # 返回给前端的价格（元）
    created_at: datetime
    status: int
    seller_id: str
    category_id: int
    image_path: Optional[str]
    seller_username: Optional[str] = None
    seller_phone: Optional[str] = None
    category_name: Optional[str] = None
    
    @field_validator('price', mode='before')
    @classmethod
    def convert_price(cls, v):
        if isinstance(v, int):
            return v / 100.0  # 从分转换为元
        return v
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int