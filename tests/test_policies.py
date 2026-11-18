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


def test_policy_rejects_budget_below_initial_evidence_cost(toy_frame):
    import pytest

    train = toy_frame.iloc[:100].reset_index(drop=True)
    models = fit_subset_models(train, seed=47)

    with pytest.raises(ValueError, match="budget"):
        run_single_policy(
            row=train.iloc[0],
            models=models,
            policy="adaptive",
            policy_table={},
            max_budget=0.99,
        )


def test_policy_accepts_exact_initial_evidence_budget(toy_frame):
    train = toy_frame.iloc[:100].reset_index(drop=True)
    models = fit_subset_models(train, seed=53)

    result = run_single_policy(
        row=train.iloc[0],
        models=models,
        policy="adaptive",
        policy_table={},
        max_budget=1.0,
    )

    assert result["acquisition_cost"] == 1.0
    assert result["groups_acquired"] == 1


def test_policy_rejects_non_finite_budgets(toy_frame):
    import pytest

    train = toy_frame.iloc[:100].reset_index(drop=True)
    models = fit_subset_models(train, seed=59)

    for budget in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError, match="budget"):
            run_single_policy(
                row=train.iloc[0],
                models=models,
                policy="adaptive",
                policy_table={},
                max_budget=budget,
            )


def test_acquisition_trace_has_unique_groups_and_consistent_cost(toy_frame):
    from exovet_agentbench.config import GROUP_COSTS, GROUP_ORDER

    train = toy_frame.iloc[:100].reset_index(drop=True)
    calibration = toy_frame.iloc[100:].reset_index(drop=True)
    models = fit_subset_models(train, seed=61)

    result = run_single_policy(
        row=calibration.iloc[0],
        models=models,
        policy="fixed",
        policy_table={},
        max_budget=3.6,
        confidence_threshold=0.99,
        seed=67,
    )

    acquisitions = [
        event for event in result["trace"]
        if event["action"] == "acquire"
    ]
    acquired_groups = [event["group"] for event in acquisitions]

    assert len(acquired_groups) == len(set(acquired_groups))
    assert all(group in GROUP_ORDER for group in acquired_groups)

    trace_cost = sum(float(event["cost"]) for event in acquisitions)

    assert abs(trace_cost - result["acquisition_cost"]) < 1e-9
    assert result["acquisition_cost"] <= 3.6 + 1e-9
    assert set(acquired_groups) == set(result["acquired_groups"].split(";"))
    assert all(
        abs(float(event["cost"]) - GROUP_COSTS[event["group"]]) < 1e-9
        for event in acquisitions
    )


def test_fixed_policy_respects_all_configured_budget_boundaries(toy_frame):
    from exovet_agentbench.config import GROUP_COSTS, GROUP_ORDER

    train = toy_frame.iloc[:100].reset_index(drop=True)
    models = fit_subset_models(train, seed=71)
    row = train.iloc[0]

    expected = {
        2.2: GROUP_ORDER[:2],
        3.6: GROUP_ORDER[:3],
        5.4: GROUP_ORDER[:4],
    }

    for budget, expected_groups in expected.items():
        result = run_single_policy(
            row=row,
            models=models,
            policy="fixed",
            policy_table={},
            max_budget=budget,
            confidence_threshold=1.0,
            seed=73,
        )

        expected_cost = sum(GROUP_COSTS[group] for group in expected_groups)

        assert result["acquired_groups"].split(";") == list(expected_groups)
        assert abs(result["acquisition_cost"] - expected_cost) < 1e-9
        assert result["acquisition_cost"] <= budget + 1e-9
