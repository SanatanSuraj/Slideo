from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId

class WebhookSubscriptionBase(BaseModel):
    url: str
    event: str
    secret: Optional[str] = None
    is_active: bool = True

class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    user_id: str

class WebhookSubscriptionUpdate(BaseModel):
    url: Optional[str] = None
    event: Optional[str] = None
    secret: Optional[str] = None
    is_active: Optional[bool] = None

class WebhookSubscriptionInDB(WebhookSubscriptionBase):
    id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

class WebhookSubscription(WebhookSubscriptionBase):
    id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
