from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class PresentationBase(BaseModel):
    title: Optional[str] = None
    content: str
    n_slides: int
    language: str
    file_paths: Optional[List[str]] = None
    outlines: Optional[Dict[str, Any]] = None
    layout: Optional[Dict[str, Any]] = None
    structure: Optional[Dict[str, Any]] = None
    instructions: Optional[str] = None
    tone: Optional[str] = None
    verbosity: Optional[str] = None
    include_table_of_contents: bool = False
    include_title_slide: bool = True
    web_search: bool = False

class PresentationCreate(PresentationBase):
    user_id: str

class PresentationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    n_slides: Optional[int] = None
    language: Optional[str] = None
    file_paths: Optional[List[str]] = None
    outlines: Optional[Dict[str, Any]] = None
    layout: Optional[Dict[str, Any]] = None
    structure: Optional[Dict[str, Any]] = None
    instructions: Optional[str] = None
    tone: Optional[str] = None
    verbosity: Optional[str] = None
    include_table_of_contents: Optional[bool] = None
    include_title_slide: Optional[bool] = None
    web_search: Optional[bool] = None

class PresentationInDB(PresentationBase):
    id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

class Presentation(PresentationBase):
    id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
