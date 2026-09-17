"""Synchronous CSV import business logic.

The service owns validation, normalization, deduplication and categorization.
Keeping this logic here means a future asynchronous worker can reuse it without
changing the business rules.
"""

import csv
import io
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from app.repositories.transaction_repository import Transaction, TransactionRepository

REQUIRED_COLUMNS = (
    "transaction_date",
    "amount",
    "currency",
    "description",
    "account_id",
)

DEFAULT_CATEGORY = "Uncategorized"

_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
_WHITESPACE_PATTERN = re.compile(r"\s+")


class MissingColumnsError(Exception):
    """Raised when the CSV header lacks required columns."""

    def __init__(self, missing_columns: list[str]) -> None:
        self.missing_columns = missing_columns
        super().__init__(f"Missing required columns: {', '.join(missing_columns)}")


class ImportService:
    """Parses a CSV file and stores valid, non-duplicate transactions."""

    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    def import_csv(self, content: bytes) -> dict[str, int]:
        """Import a CSV payload and return the resulting statistics.

        Raises MissingColumnsError when required columns are absent.
        """
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        missing = self._missing_columns(reader.fieldnames)
        if missing:
            raise MissingColumnsError(missing)

        created = 0
        duplicates_skipped = 0
        invalid_rows = 0

        for row in reader:
            parsed = self._parse_row(row)
            if parsed is None:
                invalid_rows += 1
                continue

            normalized_description = self._normalize_description(parsed["description"])
            key = self._repository.deduplication_key(
                parsed["account_id"],
                parsed["transaction_date"],
                parsed["amount"],
                normalized_description,
            )
            if self._repository.exists(key):
                duplicates_skipped += 1
                continue

            self._repository.save(
                key,
                Transaction(
                    account_id=parsed["account_id"],
                    transaction_date=parsed["transaction_date"],
                    amount=parsed["amount"],
                    description=parsed["description"].strip(),
                    category=self._categorize(normalized_description),
                ),
            )
            created += 1

        return {
            "created": created,
            "duplicates_skipped": duplicates_skipped,
            "invalid_rows": invalid_rows,
        }

    @staticmethod
    def _missing_columns(fieldnames: list[str] | None) -> list[str]:
        present = set(fieldnames or ())
        return [column for column in REQUIRED_COLUMNS if column not in present]

    def _parse_row(self, row: dict[str, str | None]) -> dict[str, object] | None:
        transaction_date = self._parse_date(row.get("transaction_date"))
        amount = self._parse_amount(row.get("amount"))
        currency = (row.get("currency") or "").strip()
        description = (row.get("description") or "").strip()
        account_id = (row.get("account_id") or "").strip()

        if transaction_date is None or amount is None:
            return None
        if not _CURRENCY_PATTERN.match(currency):
            return None
        if not description or not account_id:
            return None

        return {
            "transaction_date": transaction_date,
            "amount": amount,
            "currency": currency,
            "description": description,
            "account_id": account_id,
        }

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None

    @staticmethod
    def _parse_amount(value: str | None) -> Decimal | None:
        if value is None or not value.strip():
            return None
        try:
            amount = Decimal(value.strip())
        except InvalidOperation:
            return None
        if amount == 0:
            return None
        return amount

    @staticmethod
    def _normalize_description(description: str) -> str:
        return _WHITESPACE_PATTERN.sub(" ", description).strip().lower()

    @staticmethod
    def _categorize(normalized_description: str) -> str:
        # No categorization rules exist yet; everything is uncategorized.
        return DEFAULT_CATEGORY
