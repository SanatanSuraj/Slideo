from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from enums.webhook_event import WebhookEvent
from models.mongo.webhook import WebhookSubscriptionCreate
from crud.webhook_crud import webhook_crud
from auth.dependencies import get_current_active_user
from models.mongo.user import User

API_V1_WEBHOOK_ROUTER = APIRouter(prefix="/api/v1/webhook", tags=["Webhook"])


class SubscribeToWebhookRequest(BaseModel):
    url: str = Field(description="The URL to send the webhook to")
    secret: Optional[str] = Field(None, description="The secret to use for the webhook")
    event: WebhookEvent = Field(description="The event to subscribe to")


class SubscribeToWebhookResponse(BaseModel):
    id: str


@API_V1_WEBHOOK_ROUTER.post(
    "/subscribe", response_model=SubscribeToWebhookResponse, status_code=201
)
async def subscribe_to_webhook(
    body: SubscribeToWebhookRequest,
    current_user: User = Depends(get_current_active_user),
):
    webhook_data = WebhookSubscriptionCreate(
        user_id=current_user.id,
        url=body.url,
        secret=body.secret,
        event=body.event.value,
    )
    webhook_id = await webhook_crud.create_webhook_subscription(webhook_data)
    return SubscribeToWebhookResponse(id=webhook_id)


@API_V1_WEBHOOK_ROUTER.delete("/unsubscribe", status_code=204)
async def unsubscribe_to_webhook(
    id: str = Body(
        embed=True, description="The ID of the webhook subscription to unsubscribe from"
    ),
    current_user: User = Depends(get_current_active_user),
):
    webhook_subscription = await webhook_crud.get_webhook_subscription_by_id(id)
    if not webhook_subscription:
        raise HTTPException(404, "Webhook subscription not found")
    
    if webhook_subscription.user_id != current_user.id:
        raise HTTPException(403, "Not enough permissions")

    success = await webhook_crud.delete_webhook_subscription(id)
    if not success:
        raise HTTPException(500, "Failed to delete webhook subscription")
