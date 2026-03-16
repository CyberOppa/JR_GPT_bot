import time
from collections import defaultdict, deque


_REQUEST_TIMES: dict[tuple[int, str], deque[float]] = defaultdict(deque)


def get_retry_after(
    user_id: int,
    scope: str,
    limit: int,
    window_seconds: int,
) -> int:
    now = time.monotonic()
    key = (user_id, scope)
    timestamps = _REQUEST_TIMES[key]

    while timestamps and (now - timestamps[0]) > window_seconds:
        timestamps.popleft()

    if len(timestamps) >= limit:
        wait_for = window_seconds - (now - timestamps[0])
        return max(1, int(wait_for))

    timestamps.append(now)
    return 0
