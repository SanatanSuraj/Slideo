from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class PresentationFinalEditBase(BaseModel):
    presentation_id: str
    user_id: str
    title: Optional[str] = None
    template_id: Optional[str] = None
    slides: Optional[Dict[str, Any]] = None  # JSON field for slides data
    thumbnail_url: Optional[str] = None
    s3_pptx_url: Optional[str] = None
    s3_pdf_url: Optional[str] = None
    is_published: bool = False

class PresentationFinalEditCreate(PresentationFinalEditBase):
    pass

class PresentationFinalEditUpdate(BaseModel):
    title: Optional[str] = None
    template_id: Optional[str] = None
    slides: Optional[Dict[str, Any]] = None
    thumbnail_url: Optional[str] = None
    s3_pptx_url: Optional[str] = None
    s3_pdf_url: Optional[str] = None
    is_published: Optional[bool] = None

class PresentationFinalEditInDB(PresentationFinalEditBase):
    id: Optional[str] = None
    edited_at: datetime
    created_at: datetime
    updated_at: datetime

class PresentationFinalEdit(PresentationFinalEditBase):
    id: Optional[str] = None
    edited_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
