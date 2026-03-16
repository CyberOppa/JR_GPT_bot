import asyncio
from collections import defaultdict


_CHAT_LOCKS: dict[tuple[int, str], asyncio.Lock] = defaultdict(asyncio.Lock)


def get_chat_lock(chat_id: int, scope: str) -> asyncio.Lock:
    return _CHAT_LOCKS[(chat_id, scope)]
