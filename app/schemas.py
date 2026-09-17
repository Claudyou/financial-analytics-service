"""Pydantic schemas shared across the API layer."""

from pydantic import BaseModel


class ImportResult(BaseModel):
    """Statistics returned after a synchronous CSV import."""

    created: int
    duplicates_skipped: int
    invalid_rows: int
