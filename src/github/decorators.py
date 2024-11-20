from functools import wraps


def rate_limit(max_requests, pause):
    def decorator(func):
        request_count = 0

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal request_count
            if request_count >= max_requests:
                raise Exception('Too many requests')
