"""PostgreSQL connection dependency."""

from collections.abc import Generator

import psycopg
from fastapi import HTTPException, status
from psycopg.rows import dict_row

from src.core.config import get_settings


def get_db_connection() -> Generator[psycopg.Connection, None, None]:
    """Provides a PostgreSQL connection for a request.

    Yields:
        psycopg.Connection: Open connection using dictionary rows.

    Raises:
        HTTPException: If PostgreSQL cannot be reached.
    """
    connection = None

    try:
        connection = psycopg.connect(
            get_settings().database_url,
            row_factory=dict_row,
            connect_timeout=10,
        )
        yield connection

    except psycopg.OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable.",
        ) from exc

    finally:
        if connection is not None:
            connection.close()
