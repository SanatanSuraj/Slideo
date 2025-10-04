from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class AssetBase(BaseModel):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    asset_type: str  # image, document, etc.
    metadata: Optional[Dict[str, Any]] = None

class AssetCreate(AssetBase):
    user_id: str

class AssetUpdate(BaseModel):
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    asset_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AssetInDB(AssetBase):
    id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

class Asset(AssetBase):
    id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
