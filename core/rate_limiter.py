import time
from fastapi import Request, HTTPException, status
from db.session import redis_client

# Ліміти: Анонімні: 2 запити / 60 сек, Авторизовані: 10 запитів / 60 сек
RATE_LIMITS = {
    "anonymous": (2, 60),
    "authenticated": (10, 60),
}


async def check_rate_limit(request: Request, user_email: str | None = None):
    # Визначаємо identity: email або IP
    identity = user_email or request.client.host
    limit_type = "authenticated" if user_email else "anonymous"
    limit, period = RATE_LIMITS[limit_type]

    key = f"rate_limit:{identity}"
    now = time.time()
    window_start = now - period

    try:
        # 1. Видаляємо записи поза межами вікна
        await redis_client.zremrangebyscore(key, 0, window_start)

        # 2. Рахуємо кількість запитів у вікні
        request_count = await redis_client.zcard(key)

        if request_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )

        # 3. Додаємо поточний запит
        await redis_client.zadd(key, {str(now): now})

        # 4. Встановлюємо TTL для всього ключа
        await redis_client.expire(key, period)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        # Fail-safe: якщо Redis впав, пропускаємо запит
        print(f"Redis error: {e}")