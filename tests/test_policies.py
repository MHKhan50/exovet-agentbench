import pandas as pd

from exovet_agentbench.models import fit_subset_models
from exovet_agentbench.policies import (
    binary_entropy,
    build_adaptive_policy_table,
    confidence_bucket,
    run_single_policy,
)


def test_entropy_and_confidence_bucket():
    assert binary_entropy(0.5) > binary_entropy(0.95)
    assert confidence_bucket(0.50) == "low"
    assert confidence_bucket(0.75) == "medium"
    assert confidence_bucket(0.95) == "high"


def test_adaptive_policy_uses_only_valid_groups(toy_frame):
    train = toy_frame.iloc[:100].reset_index(drop=True)
    calibration = toy_frame.iloc[100:].reset_index(drop=True)
    models = fit_subset_models(train, seed=7)
    table = build_adaptive_policy_table(models, calibration)
    assert table
    for group in table.values():
        assert group in {"transit_geometry", "fit_quality", "stellar_context"}


def test_single_policy_respects_budget_and_returns_trace(toy_frame):
    train = toy_frame.iloc[:100].reset_index(drop=True)
    calibration = toy_frame.iloc[100:].reset_index(drop=True)
    models = fit_subset_models(train, seed=7)
    table = build_adaptive_policy_table(models, calibration)
    result = run_single_policy(
        row=calibration.iloc[0],
        models=models,
        policy="adaptive",
        policy_table=table,
        max_budget=2.2,
        seed=11,
    )
    assert result["acquisition_cost"] <= 2.2 + 1e-9
    assert result["groups_acquired"] >= 1
    assert isinstance(result["trace"], list)
    assert result["prediction"] in (0, 1)


def test_ollama_budget_guard_blocks_over_budget_request(toy_frame):
    class OverBudgetAgent:
        def choose_next_group(self, **kwargs):
            return "fit_quality"

    train = toy_frame.iloc[:100].reset_index(drop=True)
    calibration = toy_frame.iloc[100:].reset_index(drop=True)
    models = fit_subset_models(train, seed=9)
    table = build_adaptive_policy_table(models, calibration)
    result = run_single_policy(
        row=calibration.iloc[0],
        models=models,
        policy="ollama",
        policy_table=table,
        max_budget=2.2,
        seed=23,
        ollama_agent=OverBudgetAgent(),
    )
    assert result["acquisition_cost"] <= 2.2 + 1e-9
    assert result["budget_guard_events"] == 1
    assert result["invalid_actions"] >= 1
