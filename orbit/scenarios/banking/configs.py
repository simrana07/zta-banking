"""
Banking scenario configuration model.

This is the Pydantic model that holds all the settings for a banking
experiment run. It gets passed around internally to build agents,
tasks, and samples.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BankingScenarioConfig(BaseModel, frozen=True):
    """All settings for one banking scenario run."""

    # ------------------------------------------------------------------
    # Topology — which experimental condition to run
    # ------------------------------------------------------------------

    topology: Literal[
        "baseline",
        "multi_agent_no_zta",
        "zta",
    ] = "zta"
    """
    Which agent architecture to use:
    - baseline:           single agent, all 11 tools, no ZTA
    - multi_agent_no_zta: 4-agent split (intake/planner/executor/auditor)
                          but no enforcement or safety assessment gates
    - zta:                full 18-agent Zero Trust pipeline
    """

    # ------------------------------------------------------------------
    # Attack settings
    # ------------------------------------------------------------------

    attack: Literal["none", "indirect_injection"] = "none"
    """
    Which attack to run:
    - none:               benign run, no injection
    - indirect_injection: invoice.txt contains a prompt injection payload
                          attempting to trigger an unauthorised transfer
    """

    # ------------------------------------------------------------------
    # Task filtering
    # ------------------------------------------------------------------

    task_ids: list[str] | None = None
    """
    Filter to specific task IDs (e.g. ["B001", "A001"]).
    None means run all tasks.
    """

    max_tasks: int | None = None
    """Cap on number of tasks to run. Useful for quick smoke tests."""

    # ------------------------------------------------------------------
    # Model settings
    # ------------------------------------------------------------------

    judge_model: str = "openai/gpt-4o-mini"
    """Model used for the Safety Assessment (R-Judge) layer."""

    max_turns: int = 50
    """
    Maximum orchestrator turns per task.
    ZTA needs more turns than baseline because the pipeline
    has more steps — 50 is a safe ceiling.
    """

    max_time_seconds: float = 300.0
    """Maximum wall-clock time per task in seconds."""