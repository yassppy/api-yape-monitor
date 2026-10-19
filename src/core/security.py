"""Authentication dependencies for protected API endpoints."""

import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from src.core.config import get_settings


def verify_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    """Validates the API key supplied by the client.

    Args:
        x_api_key: Secret received in the X-API-Key header.

    Raises:
        HTTPException: If the key is missing or invalid.
    """
    expected_key = get_settings().api_key

    if not x_api_key or not secrets.compare_digest(
        x_api_key,
        expected_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
