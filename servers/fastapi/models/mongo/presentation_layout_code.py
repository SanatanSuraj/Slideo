from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PresentationLayoutCodeBase(BaseModel):
    presentation: str
    layout_id: str
    layout_name: str
    layout_code: str
    fonts: Optional[List[str]] = None

class PresentationLayoutCodeCreate(PresentationLayoutCodeBase):
    pass

class PresentationLayoutCodeUpdate(BaseModel):
    layout_name: Optional[str] = None
    layout_code: Optional[str] = None
    fonts: Optional[List[str]] = None

class PresentationLayoutCodeInDB(PresentationLayoutCodeBase):
    id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class PresentationLayoutCode(PresentationLayoutCodeBase):
    id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
