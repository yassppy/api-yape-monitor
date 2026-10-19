"""Database operations for payment notifications."""

from datetime import datetime
from decimal import Decimal
from typing import Any

import psycopg
from psycopg.rows import dict_row

from src.features.payments.schemas import PaymentCreate


def create_payment(
    connection: psycopg.Connection,
    payment: PaymentCreate,
) -> tuple[dict[str, Any] | None, bool]:
    """Stores a notification unless its stable key already exists.

    Args:
        connection: Active PostgreSQL connection.
        payment: Validated notification data.

    Returns:
        tuple: The stored payment and whether it was a duplicate.
        A None payment indicates a duplicate key that already exists.
    """
    query = """
        INSERT INTO payments (
            sender_name,
            amount,
            currency,
            payment_datetime,
            notification_key,
            device_name
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (notification_key)
            WHERE notification_key IS NOT NULL
        DO NOTHING
        RETURNING
            id, sender_name, amount, currency, payment_datetime,
            device_name, status, created_at;
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            query,
            (
                payment.sender_name,
                payment.amount,
                payment.currency,
                payment.payment_datetime,
                payment.notification_key,
                payment.device_name,
            ),
        )
        result = cursor.fetchone()

        if result is not None:
            connection.commit()
            return result, False

        # The conflict means this stable key was already stored.
        connection.rollback()
        return None, True


def get_payment_by_notification_key(
    connection: psycopg.Connection,
    notification_key: str,
) -> dict[str, Any] | None:
    """Retrieves an existing payment by its notification key.

    Args:
        connection: Active PostgreSQL connection.
        notification_key: Stable identifier of the notification.

    Returns:
        dict | None: Existing payment, or None if not found.
    """
    query = """
        SELECT
            id, sender_name, amount, currency, payment_datetime,
            device_name, status, created_at
        FROM payments
        WHERE notification_key = %s;
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, (notification_key,))
        return cursor.fetchone()


def search_payments(
    connection: psycopg.Connection,
    sender_name: str | None,
    start_datetime: datetime | None,
    end_datetime: datetime | None,
    amount: Decimal | None,
    limit: int,
) -> list[dict[str, Any]]:
    conditions = []
    parameters = []

    if sender_name and sender_name.strip():
        conditions.append("sender_name ILIKE %s")
        parameters.append(f"%{sender_name.strip()}%")

    if start_datetime is not None and end_datetime is not None:
        conditions.append("payment_datetime >= %s AND payment_datetime < %s")
        parameters.extend([start_datetime, end_datetime])

    if amount is not None:
        conditions.append("amount = %s")
        parameters.append(amount)

    query = """
        SELECT
            id,
            sender_name,
            amount,
            currency,
            payment_datetime,
            device_name,
            status,
            created_at
        FROM payments
    """

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY payment_datetime DESC LIMIT %s"
    parameters.append(limit)

    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        return cursor.fetchall()
