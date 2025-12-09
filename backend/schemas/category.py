from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True