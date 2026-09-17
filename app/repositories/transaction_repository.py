"""In-memory persistence for imported transactions.

The MVP keeps transactions in memory. The interface (deduplication key lookup
plus save) is what a future SQL-backed repository will expose, so the service
layer can stay unchanged when persistence moves to a database.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Transaction:
    """A persisted financial transaction."""

    account_id: str
    transaction_date: date
    amount: Decimal
    description: str
    category: str


class TransactionRepository:
    """Stores transactions and detects duplicates by deterministic key."""

    def __init__(self) -> None:
        self._transactions: dict[str, Transaction] = {}

    @staticmethod
    def deduplication_key(
        account_id: str,
        transaction_date: date,
        amount: Decimal,
        normalized_description: str,
    ) -> str:
        """Build the deterministic key that identifies a duplicate."""
        return f"{account_id}|{transaction_date.isoformat()}|{amount}|{normalized_description}"

    def exists(self, key: str) -> bool:
        """Return whether a transaction with this key was already stored."""
        return key in self._transactions

    def save(self, key: str, transaction: Transaction) -> None:
        """Persist a transaction under its deduplication key."""
        self._transactions[key] = transaction
