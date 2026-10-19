"""Request and response schemas for payment notifications."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class PaymentCreate(BaseModel):
    """Represents a payment notification received from Android."""

    model_config = ConfigDict(extra="ignore")

    event: str | None = None

    sender_name: str = Field(
        min_length=1,
        max_length=200,
        validation_alias=AliasChoices("sender_name", "sender"),
    )
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: Literal["PEN"] = "PEN"

    payment_datetime: datetime = Field(
        validation_alias=AliasChoices(
            "payment_datetime",
            "datetime_iso",
        ),
    )

    notification_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    device_name: str | None = Field(default=None, max_length=100)

    @field_validator("sender_name")
    @classmethod
    def normalize_sender_name(cls, value: str) -> str:
        """Normalizes whitespace in the sender name."""
        normalized = " ".join(value.split())

        if not normalized:
            raise ValueError("Sender name cannot be empty.")

        return normalized

    @field_validator("payment_datetime")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        """Ensures the payment timestamp includes a timezone."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("payment_datetime must include a timezone.")

        return value


class PaymentResponse(BaseModel):
    """Represents a payment returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_name: str
    amount: Decimal
    currency: str
    payment_datetime: datetime
    device_name: str | None
    status: str
    created_at: datetime


class PaymentReceiptResponse(BaseModel):
    """Represents the result of storing a notification."""

    payment: PaymentResponse
    duplicate: bool = False


class TestPingResponse(BaseModel):
    """Represents a successful webhook connectivity test."""

    event: Literal["test_ping"] = "test_ping"
    status: Literal["ok"] = "ok"
    message: str = "Webhook connection successful."
