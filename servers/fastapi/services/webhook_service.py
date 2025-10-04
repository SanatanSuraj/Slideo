import asyncio
import aiohttp
from enums.webhook_event import WebhookEvent
from crud.webhook_crud import webhook_crud


class WebhookService:

    @classmethod
    async def send_webhook(cls, event: WebhookEvent, data: dict):
        webhook_subscriptions = await webhook_crud.get_webhook_subscriptions_by_event(event.value)
        if not webhook_subscriptions:
            return

        async_tasks = []
        for webhook_subscription in webhook_subscriptions:
            async_tasks.append(
                cls.send_request_to_webhook(webhook_subscription, data)
            )

        await asyncio.gather(*async_tasks)

    @classmethod
    async def send_request_to_webhook(
        cls, subscription, data: dict
    ):

        headers = {
            "Content-Type": "application/json",
        }
        if subscription.secret:
            headers["Authorization"] = f"Bearer {subscription.secret}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    subscription.url,
                    json=data,
                    headers=headers,
                ) as _:
                    pass

        except Exception as e:
            print(f"Error sending request to webhook {subscription.id}: {e}")
            pass
