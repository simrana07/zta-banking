"""
Banking scenario configuration model.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BankingScenarioConfig(BaseModel, frozen=True):
    """All settings for one banking scenario run."""

    topology: Literal[
        "baseline",
        "naive_multi_agent",
        "zta_no_rules",
        "zta_r4_only",
        "zta_r1_r2_only",
        "zta_r1_r2_r3",
        "zta",
        "zta_split_enforcement",
        "zta_verification",
        "zta_audit",
        "zta_credential_broker",
    ] = "zta"
    """
    Which agent architecture to use:
    - baseline:          single agent, all 11 tools, no ZTA
    - naive_multi_agent: 7-agent split, no safety logic anywhere
    - enforcement:       + Enforcement Agent with embedded policy rules
    - zta:               + Audit Layer (Auditor + Anomaly Detection)
    """

    attack: Literal["none", "indirect_injection"] = "none"
    """
    Which attack to run:
    - none:               benign run, no injection
    - indirect_injection: invoice.txt contains a prompt injection payload
    """

    task_ids: list[str] | None = None
    """Filter to specific task IDs. None means run all tasks."""

    max_tasks: int | None = None
    """Cap on number of tasks. Useful for smoke tests."""

    judge_model: str = "openai/gpt-4o-mini"
    """Model used for the Safety Assessment layer."""

    max_turns: int = 50
    """Maximum orchestrator turns per task."""

    max_time_seconds: float = 300.0
    """Maximum wall-clock time per task in seconds."""