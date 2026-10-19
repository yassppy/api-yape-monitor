"""Application entry point for Yape Monitor API."""

from fastapi import FastAPI

from src.core.config import get_settings
from src.features.payments.router import router as payments_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "API for storing and searching payment notifications received by Yape Monitor."
    ),
    version="1.0.0",
)

app.include_router(payments_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Returns the basic application health status.

    Returns:
        dict[str, str]: Simple status response.
    """
    return {"status": "ok"}
