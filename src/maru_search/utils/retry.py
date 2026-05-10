"""Retry utilities with exponential backoff and jitter."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Callable, Tuple, Type

from ..exceptions import MaruSearchError

logger = logging.getLogger(__name__)


async def with_retry(
    func: Callable,
    *args,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    **kwargs,
):
    """Call an async function with exponential backoff retry.

    Args:
        func: Async function to call.
        *args: Positional arguments for func.
        max_attempts: Maximum number of attempts.
        base_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay in seconds.
        retryable_exceptions: Exception types to retry on.
        **kwargs: Keyword arguments for func.
    """
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except retryable_exceptions as exc:
            last_exception = exc

            # Check if exception explicitly says not retryable
            if isinstance(exc, MaruSearchError) and not exc.retryable:
                raise

            if attempt >= max_attempts:
                break

            # Exponential backoff with 30% jitter
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            jitter = delay * 0.3 * (random.random() * 2 - 1)
            actual_delay = max(0.1, delay + jitter)

            logger.warning(
                "Attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                attempt,
                max_attempts,
                func.__name__,
                exc,
                actual_delay,
            )
            await asyncio.sleep(actual_delay)

    raise last_exception
