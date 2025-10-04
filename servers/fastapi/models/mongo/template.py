from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    layout: Dict[str, Any]
    structure: Optional[Dict[str, Any]] = None
    is_public: bool = False
    tags: Optional[List[str]] = None

class TemplateCreate(TemplateBase):
    user_id: str

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    structure: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None

class TemplateInDB(TemplateBase):
    id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

class Template(TemplateBase):
    id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
