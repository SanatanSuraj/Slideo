from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from models.mongo.webhook import WebhookSubscription, WebhookSubscriptionCreate, WebhookSubscriptionUpdate, WebhookSubscriptionInDB
from db.mongo import get_database

class WebhookCRUD:
    def __init__(self):
        self._db = None
        self._collection = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.db.webhook_subscriptions
        return self._collection
    
    async def create_webhook_subscription(self, webhook: WebhookSubscriptionCreate) -> str:
        """Create a new webhook subscription"""
        webhook_data = {
            "user_id": webhook.user_id,
            "url": webhook.url,
            "event": webhook.event,
            "secret": webhook.secret,
            "is_active": webhook.is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(webhook_data)
        return str(result.inserted_id)
    
    async def get_webhook_subscription_by_id(self, webhook_id: str) -> Optional[WebhookSubscriptionInDB]:
        """Get webhook subscription by ID"""
        webhook_data = await self.collection.find_one({"_id": ObjectId(webhook_id)})
        if webhook_data:
            webhook_data["id"] = str(webhook_data["_id"])
            del webhook_data["_id"]
            return WebhookSubscriptionInDB(**webhook_data)
        return None
    
    async def get_webhook_subscriptions_by_event(self, event: str) -> List[WebhookSubscriptionInDB]:
        """Get webhook subscriptions by event"""
        cursor = self.collection.find({"event": event, "is_active": True})
        webhooks = []
        async for webhook_data in cursor:
            webhook_data["id"] = str(webhook_data["_id"])
            del webhook_data["_id"]
            webhooks.append(WebhookSubscriptionInDB(**webhook_data))
        return webhooks
    
    async def get_webhook_subscriptions_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[WebhookSubscriptionInDB]:
        """Get webhook subscriptions by user ID"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        webhooks = []
        async for webhook_data in cursor:
            webhook_data["id"] = str(webhook_data["_id"])
            del webhook_data["_id"]
            webhooks.append(WebhookSubscriptionInDB(**webhook_data))
        return webhooks
    
    async def update_webhook_subscription(self, webhook_id: str, webhook_update: WebhookSubscriptionUpdate) -> Optional[WebhookSubscriptionInDB]:
        """Update webhook subscription"""
        update_data = webhook_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.collection.update_one(
                {"_id": ObjectId(webhook_id)},
                {"$set": update_data}
            )
        return await self.get_webhook_subscription_by_id(webhook_id)
    
    async def delete_webhook_subscription(self, webhook_id: str) -> bool:
        """Delete webhook subscription"""
        result = await self.collection.delete_one({"_id": ObjectId(webhook_id)})
        return result.deleted_count > 0

# Global instance
webhook_crud = WebhookCRUD()
