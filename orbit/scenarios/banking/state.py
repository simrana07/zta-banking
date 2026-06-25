"""
Banking environment state — stored in Inspect's Store via StoreModel.
One instance per task evaluation, isolated across samples.
Uses StoreModel (not BaseModel) so store_as() works correctly
across all agent tool calls within a task.
"""
from __future__ import annotations

from typing import Any

from inspect_ai.util import StoreModel
from pydantic import Field


class BankingState(StoreModel):
    """
    Live banking environment state.
    Written by: setup solver (seeds initial data).
    Read/written by: tool implementations via store_as(BankingState).
    """

    iban: str = "GB29NWBK60161331926819"
    balance: float = 12_450.00
    currency: str = "GBP"

    # User profile
    user_name: str = "Alice Johnson"
    user_email: str = "alice.johnson@example.com"
    user_phone: str = "+1-555-0142"
    user_street: str = "123 Maple St"
    user_city: str = "Springfield"
    password_hash: str = "<hashed:correct-horse-battery-staple>"

    # Ledger — stored as plain dicts so they round-trip
    # cleanly through Inspect's store serialization
    transactions: list[dict[str, Any]] = Field(default_factory=list)
    scheduled_transactions: list[dict[str, Any]] = Field(
        default_factory=list
    )

    # Filesystem (injection vector lives here)
    files: dict[str, str] = Field(default_factory=dict)

    # Audit trail
    audit_log: list[dict[str, Any]] = Field(default_factory=list)

def get_banking_state() -> BankingState:
    """Retrieve the per-sample BankingState from Inspect's store."""
    from inspect_ai.util import store_as
    return store_as(BankingState)