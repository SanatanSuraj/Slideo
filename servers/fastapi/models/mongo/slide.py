from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class SlideBase(BaseModel):
    slide_number: int
    content: str
    layout: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = None
    shapes: Optional[List[Dict[str, Any]]] = None
    text_boxes: Optional[List[Dict[str, Any]]] = None

class SlideCreate(SlideBase):
    presentation_id: str

class SlideUpdate(BaseModel):
    content: Optional[str] = None
    layout: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = None
    shapes: Optional[List[Dict[str, Any]]] = None
    text_boxes: Optional[List[Dict[str, Any]]] = None

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
