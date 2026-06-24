"""
Banking environment state — stored in Inspect's Store via store_as().
One instance per task evaluation, isolated across samples.
"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from inspect_ai.util import store_as


class BankingState(BaseModel):
    """Live banking environment state. Read/written by tool implementations."""

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

    # Ledger
    transactions: list[dict[str, Any]] = Field(default_factory=list)
    scheduled_transactions: list[dict[str, Any]] = Field(default_factory=list)

    # Filesystem (injection vector lives here)
    files: dict[str, str] = Field(default_factory=dict)

    # Audit trail (append-only by convention)
    audit_log: list[dict[str, Any]] = Field(default_factory=list)


def get_banking_state() -> BankingState:
    """Retrieve the per-sample BankingState from Inspect's store."""
    return store_as(BankingState)