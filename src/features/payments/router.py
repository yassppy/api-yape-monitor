"""HTTP endpoints for receiving and searching payment notifications."""

from datetime import date
from decimal import Decimal
from typing import Annotated

import psycopg
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from src.core.database import get_db_connection
from src.core.security import verify_api_key
from src.features.payments import service
from src.features.payments.schemas import (
    PaymentCreate,
    PaymentReceiptResponse,
    PaymentResponse,
    TestPingResponse,
)

router = APIRouter(
    tags=["Payments"],
    dependencies=[Depends(verify_api_key)],
)

DatabaseConnection = Annotated[
    psycopg.Connection,
    Depends(get_db_connection),
]


@router.post(
    "/webhook/yape",
    response_model=PaymentReceiptResponse | TestPingResponse,
    status_code=status.HTTP_201_CREATED,
)
def receive_payment(
    payload: PaymentCreate,
    connection: DatabaseConnection,
    response: Response,
) -> PaymentReceiptResponse | TestPingResponse:
    """Receives a test event or a payment notification.

    Args:
        payload: Notification fields received from Android.
        connection: Database connection provided by FastAPI.
        response: HTTP response used to set the status code.

    Returns:
        PaymentReceiptResponse | TestPingResponse:
            The connectivity test result or the saved payment.
    """
    if payload.event == "test_ping":
        response.status_code = status.HTTP_200_OK

        return TestPingResponse()

    try:
        payment, duplicate = service.register_payment(
            connection,
            payload,
        )
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save payment notification.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process payment notification.",
        ) from exc

    return PaymentReceiptResponse(
        payment=PaymentResponse.model_validate(payment),
        duplicate=duplicate,
    )


@router.get(
    "/payments/search",
    response_model=list[PaymentResponse],
)
def search_payments(
    connection: DatabaseConnection,
    sender_name: Annotated[
        str | None,
        Query(min_length=1, max_length=200),
    ] = None,
    payment_date: date | None = None,
    amount: Annotated[Decimal | None, Query(gt=0)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[PaymentResponse]:
    """Searches payment notifications using optional filters.

    Args:
        connection: Database connection provided by FastAPI.
        sender_name: Optional full or partial sender name.
        payment_date: Optional payment date in Peru's timezone.
        amount: Optional exact payment amount.
        limit: Maximum number of results, from 1 to 100.

    Returns:
        list[PaymentResponse]: Matching payment notifications.
    """
    try:
        results = service.find_payments(
            connection=connection,
            sender_name=sender_name,
            payment_date=payment_date,
            amount=amount,
            limit=limit,
        )
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to search payment notifications.",
        ) from exc

    return [PaymentResponse.model_validate(payment) for payment in results]
