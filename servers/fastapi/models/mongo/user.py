from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    plan: Optional[str] = "free"
    is_active: bool = True

class UserCreate(UserBase):
    password: Optional[str] = None
    
    @validator('password')
    def validate_password_length(cls, v):
        if v is not None and len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot be longer than 72 bytes')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: Optional[str] = None
    hashed_password: str
    created_at: datetime
    updated_at: datetime

class User(UserBase):
    id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
