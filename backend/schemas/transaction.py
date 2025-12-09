from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    product_id: str = Field(..., description="商品ID")

class TransactionSearch(BaseModel):
    status: Optional[int] = Field(None, ge=0, le=1, description="交易状态")
    category_id: Optional[int] = Field(None, gt=0, description="分类ID")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")

class TransactionResponse(BaseModel):
    transaction_id: str
    created_at: datetime
    amount: float  # 返回给前端的金额（元）
    status: int
    buyer_id: str
    seller_id: str
    product_id: str
    counterparty_username: Optional[str] = None
    counterparty_role: Optional[str] = None
    product_name: Optional[str] = None
    category_name: Optional[str] = None
    
    @field_validator('amount', mode='before')
    @classmethod
    def convert_amount(cls, v):
        if isinstance(v, int):
            return v / 100.0  # 从分转换为元
        return v
    
    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int