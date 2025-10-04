from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class VectorBase(BaseModel):
    content: str
    embedding: List[float]
    metadata: Optional[Dict[str, Any]] = None
    vector_type: str  # icon, document, etc.

class VectorCreate(VectorBase):
    user_id: Optional[str] = None

class VectorUpdate(BaseModel):
    content: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None

class VectorInDB(VectorBase):
    id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Vector(VectorBase):
    id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
