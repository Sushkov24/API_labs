import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, Request
from core.rate_limiter import check_rate_limit


@pytest.mark.asyncio
async def test_rate_limit_authenticated_ok():
    # Мокаємо весь модуль redis_client
    with patch("core.rate_limiter.redis_client", new_callable=AsyncMock) as mock_redis:
        mock_redis.zcard.return_value = 5  # Менше ліміту 10
        request = MagicMock(spec=Request)

        # Не має викидати помилку
        await check_rate_limit(request, user_email="user@test.com")
        assert mock_redis.zcard.called


@pytest.mark.asyncio
async def test_rate_limit_authenticated_fail():
    with patch("core.rate_limiter.redis_client", new_callable=AsyncMock) as mock_redis:
        mock_redis.zcard.return_value = 10  # Ліміт досягнуто
        request = MagicMock(spec=Request)

        with pytest.raises(HTTPException) as exc:
            await check_rate_limit(request, user_email="user@test.com")

        assert exc.value.status_code == 429
        assert exc.value.detail == "Too many requests. Please try again later."


@pytest.mark.asyncio
async def test_rate_limit_anonymous_ok():
    with patch("core.rate_limiter.redis_client", new_callable=AsyncMock) as mock_redis:
        mock_redis.zcard.return_value = 1  # Менше ліміту 2
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"

        await check_rate_limit(request, user_email=None)
        assert mock_redis.zcard.called


@pytest.mark.asyncio
async def test_rate_limit_anonymous_fail():
    with patch("core.rate_limiter.redis_client", new_callable=AsyncMock) as mock_redis:
        mock_redis.zcard.return_value = 2  # Ліміт досягнуто (2 >= 2)
        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"

        with pytest.raises(HTTPException) as exc:
            await check_rate_limit(request, user_email=None)

        assert exc.value.status_code == 429