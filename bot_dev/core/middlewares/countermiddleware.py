from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from typing import Dict, Any, Callable, Awaitable
from core.utils.dbconnect import Request
import logging
import asyncpg


class CounterMiddleware(BaseMiddleware):
    def __init__(self, connector: asyncpg.pool.Pool) -> None:
        self.counter = 0
        self.request: Request = Request(connector)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        self.counter += 1
        data["counter"] = self.counter
        if data["event_update"].message:
            message = data["event_update"].message.message_id
            text: Update = data["event_update"]
            user_id = data["event_from_user"].id
            await self.request.save_message(
                user_id, message, text.message.text, True, "User"
            )
        result = await handler(event, data)
        return result
