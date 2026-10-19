"""Business logic for payment notification operations."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

import psycopg

from src.features.payments import repository
from src.features.payments.schemas import PaymentCreate

LIMA_TIMEZONE = ZoneInfo("America/Lima")


def register_payment(
    connection: psycopg.Connection,
    payment: PaymentCreate,
) -> tuple[dict[str, Any], bool]:
    """Registers a payment notification and logs its result."""

    print("=" * 50)
    print("🔔 NUEVA NOTIFICACIÓN DE YAPE")
    print(f"👤 Remitente: {payment.sender_name}")
    print(f"💰 Monto: S/ {payment.amount}")
    print(f"📅 Fecha recibida: {payment.payment_datetime}")
    print(f"🕒 Zona horaria: {payment.payment_datetime.tzinfo}")
    print("=" * 50)

    result, duplicate = repository.create_payment(connection, payment)

    if result is not None:
        print("✅ Pago insertado correctamente en Neon")
        print(f"🆔 ID: {result.get('id')}")
        print(f"📅 Fecha guardada: {result.get('payment_datetime')}")
        return result, False

    if payment.notification_key:
        existing = repository.get_payment_by_notification_key(
            connection,
            payment.notification_key,
        )
        if existing is not None:
            print("⚠️ Notificación duplicada; se devuelve el registro existente")
            print(f"🆔 ID: {existing.get('id')}")
            print(f"📅 Fecha guardada: {existing.get('payment_datetime')}")
            return existing, True

    print("❌ No se pudo recuperar el pago registrado")
    raise RuntimeError("Unable to retrieve the stored payment notification.")


def find_payments(
    connection: psycopg.Connection,
    sender_name: str | None = None,
    payment_date: date | None = None,
    amount: Decimal | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Search payments using optional filters."""

    start_datetime = None
    end_datetime = None

    if payment_date is not None:
        local_start = datetime.combine(
            payment_date,
            time.min,
            tzinfo=LIMA_TIMEZONE,
        )
        local_end = local_start + timedelta(days=1)

        start_datetime = local_start
        end_datetime = local_end

    return repository.search_payments(
        connection=connection,
        sender_name=sender_name,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        amount=amount,
        limit=limit,
    )
