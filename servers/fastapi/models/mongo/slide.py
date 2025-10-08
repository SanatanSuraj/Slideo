from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class SlideBase(BaseModel):
    slide_number: int
    content: str
    layout: Optional[str] = None
    layout_group: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = None
    shapes: Optional[List[Dict[str, Any]]] = None
    text_boxes: Optional[List[Dict[str, Any]]] = None

class SlideCreate(SlideBase):
    presentation_id: str

class SlideUpdate(BaseModel):
    content: Optional[str] = None
    layout: Optional[str] = None
    layout_group: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = None
    shapes: Optional[List[Dict[str, Any]]] = None
    text_boxes: Optional[List[Dict[str, Any]]] = None

class SlideUpdateFromFrontend(BaseModel):
    """Model for handling slide updates from frontend format"""
    id: Optional[str] = None
    presentation_id: Optional[str] = None
    slide_number: Optional[int] = None
    content: Optional[str] = None
    layout: Optional[str] = None
    layout_group: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = None
    shapes: Optional[List[Dict[str, Any]]] = None
    text_boxes: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class SlideInDB(SlideBase):
    id: Optional[str] = None
    presentation_id: str
    created_at: datetime
    updated_at: datetime

class Slide(SlideBase):
    id: Optional[str] = None
    presentation_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
