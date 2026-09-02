"""Top-level HTTP routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return the service availability status."""
    return {"status": "ok"}