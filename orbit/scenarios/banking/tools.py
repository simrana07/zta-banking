"""
Banking tools — all 11 AgentDojo tools implemented for ORBIT.

Follows the same pattern as tau2 airline tools:
- @tool(name="...") decorator with explicit name
- make_banking_tools() returns list[ToolDef]
- State accessed via store_as(BankingState)
"""

from __future__ import annotations

import uuid
from datetime import datetime

from inspect_ai.tool import Tool, tool
from inspect_ai.tool._tool_def import ToolDef
from inspect_ai.util import store_as

from orbit.scenarios.banking.state import BankingState


# ============================================================================
# State helper
# ============================================================================

def _get_state() -> BankingState:
    return store_as(BankingState)


# ============================================================================
# Tool definitions
# ============================================================================

@tool(name="get_iban")
def _get_iban_tool() -> Tool:
    async def execute() -> str:
        """Get the IBAN of the current bank account."""
        return _get_state().iban
    return execute


@tool(name="get_balance")
def _get_balance_tool() -> Tool:
    async def execute() -> str:
        """Get the current account balance and currency."""
        state = _get_state()
        return f"{state.balance:.2f} {state.currency}"
    return execute


@tool(name="get_user_info")
def _get_user_info_tool() -> Tool:
    async def execute() -> str:
        """Get the current user's account information."""
        s = _get_state()
        return (
            f"Name: {s.user_name}\n"
            f"Email: {s.user_email}\n"
            f"Phone: {s.user_phone}\n"
            f"Street: {s.user_street}\n"
            f"City: {s.user_city}"
        )
    return execute


@tool(name="update_user_info")
def _update_user_info_tool() -> Tool:
    async def execute(field: str, value: str) -> str:
        """Update a user account field.

        Args:
            field: The field to update. One of: name, email, phone, street, city.
            value: The new value for the field.
        """
        state = _get_state()
        field_map = {
            "name": "user_name",
            "email": "user_email",
            "phone": "user_phone",
            "street": "user_street",
            "city": "user_city",
        }
        attr = field_map.get(field)
        if attr is None:
            return f"Error: unknown field '{field}'"
        setattr(state, attr, value)
        return f"Updated {field} to: {value}"
    return execute


@tool(name="update_password")
def _update_password_tool() -> Tool:
    async def execute(new_password: str) -> str:
        """Update the current account password.

        Args:
            new_password: The new password to set.
        """
        _get_state().password_hash = f"<hashed:{new_password}>"
        return "Password updated successfully."
    return execute


@tool(name="send_money")
def _send_money_tool() -> Tool:
    async def execute(
        recipient_iban: str,
        recipient_name: str,
        amount: float,
        currency: str,
        description: str,
    ) -> str:
        """Execute an immediate money transfer to a recipient.

        Args:
            recipient_iban: The recipient's IBAN.
            recipient_name: The recipient's full name.
            amount: The amount to transfer.
            currency: The currency code e.g. GBP.
            description: A description for the transfer.
        """
        state = _get_state()
        if amount <= 0:
            return "Error: amount must be positive"
        if amount > state.balance:
            return f"Error: insufficient funds (balance: {state.balance:.2f} {state.currency})"
        state.balance -= amount
        tx = {
            "id": f"tx{uuid.uuid4().hex[:6]}",
            "amount": amount,
            "currency": currency,
            "recipient_iban": recipient_iban,
            "recipient_name": recipient_name,
            "timestamp": datetime.now().isoformat(),
            "description": description,
        }
        state.transactions.append(tx)
        state.audit_log.append({
            "action": "send_money",
            "recipient_iban": recipient_iban,
            "amount": amount,
            "tx_id": tx["id"],
        })
        return (
            f"Transferred {amount:.2f} {currency} to "
            f"{recipient_name} ({recipient_iban}). TX ID: {tx['id']}"
        )
    return execute


@tool(name="schedule_transaction")
def _schedule_transaction_tool() -> Tool:
    async def execute(
        recipient_iban: str,
        recipient_name: str,
        amount: float,
        currency: str,
        date: str,
        recurring: bool,
        period: str,
        description: str,
    ) -> str:
        """Schedule a future or recurring transaction.

        Args:
            recipient_iban: The recipient's IBAN.
            recipient_name: The recipient's full name.
            amount: The amount to transfer.
            currency: The currency code e.g. GBP.
            date: The date for the first payment in YYYY-MM-DD format.
            recurring: Whether the payment recurs.
            period: The recurrence period e.g. monthly, weekly.
            description: A description for the payment.
        """
        state = _get_state()
        sched = {
            "id": f"sched{uuid.uuid4().hex[:6]}",
            "amount": amount,
            "currency": currency,
            "recipient_iban": recipient_iban,
            "recipient_name": recipient_name,
            "date": date,
            "recurring": recurring,
            "period": period if recurring else None,
            "description": description,
        }
        state.scheduled_transactions.append(sched)
        recur_str = f", recurring {period}" if recurring else ""
        return (
            f"Scheduled {amount:.2f} {currency} to "
            f"{recipient_name} on {date}{recur_str}."
        )
    return execute


@tool(name="update_scheduled_transaction")
def _update_scheduled_transaction_tool() -> Tool:
    async def execute(
        transaction_id: str,
        amount: float | None = None,
        date: str | None = None,
        recipient_iban: str | None = None,
        description: str | None = None,
    ) -> str:
        """Modify an existing scheduled transaction by ID.

        Args:
            transaction_id: The ID of the scheduled transaction to update.
            amount: New amount (optional).
            date: New date in YYYY-MM-DD format (optional).
            recipient_iban: New recipient IBAN (optional).
            description: New description (optional).
        """
        state = _get_state()
        for sched in state.scheduled_transactions:
            if sched["id"] == transaction_id:
                if amount is not None:
                    sched["amount"] = amount
                if date is not None:
                    sched["date"] = date
                if recipient_iban is not None:
                    sched["recipient_iban"] = recipient_iban
                if description is not None:
                    sched["description"] = description
                return f"Updated scheduled transaction {transaction_id}."
        return f"Error: no scheduled transaction with ID '{transaction_id}'"
    return execute


@tool(name="get_most_recent_transactions")
def _get_most_recent_transactions_tool() -> Tool:
    async def execute(n: int = 5) -> str:
        """Get the last N completed transactions.

        Args:
            n: Number of transactions to return. Defaults to 5.
        """
        state = _get_state()
        recent = state.transactions[-n:]
        if not recent:
            return "No transactions found."
        lines = []
        for tx in reversed(recent):
            lines.append(
                f"[{tx['timestamp']}] {tx['amount']:.2f} {tx['currency']} "
                f"-> {tx['recipient_name']} ({tx['recipient_iban']}): "
                f"{tx['description']}"
            )
        return "\n".join(lines)
    return execute


@tool(name="get_scheduled_transactions")
def _get_scheduled_transactions_tool() -> Tool:
    async def execute() -> str:
        """Get all pending scheduled transactions."""
        state = _get_state()
        if not state.scheduled_transactions:
            return "No scheduled transactions."
        lines = []
        for s in state.scheduled_transactions:
            recur = f", {s['period']}" if s.get("recurring") else ""
            lines.append(
                f"[{s['id']}] {s['amount']:.2f} {s['currency']} "
                f"-> {s['recipient_name']} on {s['date']}{recur}: "
                f"{s['description']}"
            )
        return "\n".join(lines)
    return execute


@tool(name="read_file")
def _read_file_tool() -> Tool:
    async def execute(filename: str) -> str:
        """Read a file from the environment filesystem.

        Args:
            filename: The name of the file to read.
        """
        content = _get_state().files.get(filename)
        if content is None:
            return f"Error: file '{filename}' not found"
        return content
    return execute


# ============================================================================
# Tool registry and factory
# ============================================================================

_TOOL_FACTORIES: dict[str, callable] = {
    "get_iban":                     _get_iban_tool,
    "get_balance":                  _get_balance_tool,
    "get_user_info":                _get_user_info_tool,
    "update_user_info":             _update_user_info_tool,
    "update_password":              _update_password_tool,
    "send_money":                   _send_money_tool,
    "schedule_transaction":         _schedule_transaction_tool,
    "update_scheduled_transaction": _update_scheduled_transaction_tool,
    "get_most_recent_transactions": _get_most_recent_transactions_tool,
    "get_scheduled_transactions":   _get_scheduled_transactions_tool,
    "read_file":                    _read_file_tool,
}

_TOOL_DESCRIPTIONS: dict[str, str] = {
    "get_iban":                     "Get the IBAN of the current bank account.",
    "get_balance":                  "Get the current account balance and currency.",
    "get_user_info":                "Get the current user's account information.",
    "update_user_info":             "Update a user account field.",
    "update_password":              "Update the current account password.",
    "send_money":                   "Execute an immediate money transfer.",
    "schedule_transaction":         "Schedule a future or recurring transaction.",
    "update_scheduled_transaction": "Modify an existing scheduled transaction.",
    "get_most_recent_transactions": "Get the last N completed transactions.",
    "get_scheduled_transactions":   "Get all pending scheduled transactions.",
    "read_file":                    "Read a file from the environment filesystem.",
}


def make_banking_tools(agent_name: str | None = None) -> list[ToolDef]:
    """
    Factory function registered in agent_factory.py.
    Returns list[ToolDef] so ORBIT can find each tool by name.
    The agent_name parameter is accepted for compatibility but unused —
    banking tools are not per-agent parameterised.
    """
    defs: list[ToolDef] = []
    for name, factory in _TOOL_FACTORIES.items():
        defs.append(
            ToolDef(
                factory(),
                name=name,
                description=_TOOL_DESCRIPTIONS[name],
            )
        )
    return defs