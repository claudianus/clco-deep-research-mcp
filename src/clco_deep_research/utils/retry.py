"""Simple retry utilities with exponential backoff."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Callable, TypeVar

from ..exceptions import ResearchError

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retry(
    fn: Callable[..., T],
    *args,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    **kwargs,
) -> T:
    """Execute an async function with exponential backoff retry.

    Args:
        fn: Async function to call.
        max_attempts: Maximum number of attempts (including first).
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        retryable_exceptions: Exception types that trigger retry.
        *args, **kwargs: Arguments passed to fn.
    """
    last_exception: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await fn(*args, **kwargs)
        except retryable_exceptions as exc:
            last_exception = exc

            # Check if exception explicitly says it's not retryable
            if isinstance(exc, ResearchError) and not exc.retryable:
                raise

            if attempt >= max_attempts:
                logger.warning("Max retries (%d) exceeded for %s", max_attempts, fn.__name__)
                raise

            # Exponential backoff with jitter
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            jitter = random.uniform(0, delay * 0.3)
            sleep_time = delay + jitter

            logger.info(
                "Retry %d/%d for %s in %.1fs: %s",
                attempt, max_attempts, fn.__name__, sleep_time, exc
            )
            await asyncio.sleep(sleep_time)

    # Should never reach here, but just in case
    raise last_exception or RuntimeError("Unexpected retry loop exit")
