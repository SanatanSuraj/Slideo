from pydantic import BaseModel, validator
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: Optional[bool] = False
    
    @validator('password')
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot be longer than 72 bytes')
        return v

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    remember_me: Optional[bool] = False
    
    @validator('password')
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot be longer than 72 bytes')
        return v
