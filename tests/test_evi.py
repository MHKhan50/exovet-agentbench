import pandas as pd

from exovet_agentbench.evi import select_candidate_specific_group
from exovet_agentbench.models import fit_subset_models
from exovet_agentbench.policies import run_single_policy


def test_evi_selects_only_available_evidence_groups(toy_frame):
    train = toy_frame.iloc[:100].reset_index(drop=True)
    calibration = toy_frame.iloc[100:].reset_index(drop=True)
    models = fit_subset_models(train, seed=31)

    selected = select_candidate_specific_group(
        row=calibration.iloc[0],
        acquired={"signal_metrics"},
        models=models,
        calibration_frame=calibration,
        neighbours=20,
    )

    assert selected in {
        "transit_geometry",
        "fit_quality",
        "stellar_context",
    }


def test_evi_selection_does_not_depend_on_calibration_labels(toy_frame):
    train = toy_frame.iloc[:100].reset_index(drop=True)
    calibration = toy_frame.iloc[100:].reset_index(drop=True)
    models = fit_subset_models(train, seed=37)

    original = select_candidate_specific_group(
        row=calibration.iloc[0],
        acquired={"signal_metrics"},
        models=models,
        calibration_frame=calibration,
        neighbours=20,
    )

    changed_labels = calibration.copy()
    changed_labels["target"] = 1 - changed_labels["target"]

    changed = select_candidate_specific_group(
        row=calibration.iloc[0],
        acquired={"signal_metrics"},
        models=models,
        calibration_frame=changed_labels,
        neighbours=20,
    )

    assert original == changed


def test_adaptive_policy_uses_candidate_specific_selector_and_respects_budget(
    toy_frame,
):
    train = toy_frame.iloc[:100].reset_index(drop=True)
    calibration = toy_frame.iloc[100:].reset_index(drop=True)
    models = fit_subset_models(train, seed=41)

    result = run_single_policy(
        row=calibration.iloc[0],
        models=models,
        policy="adaptive",
        policy_table={},
        calibration_frame=calibration,
        max_budget=2.2,
        confidence_threshold=0.99,
        seed=43,
    )

    assert result["acquisition_cost"] <= 2.2 + 1e-9
    assert result["groups_acquired"] >= 1
    assert result["prediction"] in (0, 1)
    assert result["acquired_groups"].startswith("signal_metrics")


def test_evi_selection_is_deterministic(toy_frame):
    train = toy_frame.iloc[:100].reset_index(drop=True)
    calibration = toy_frame.iloc[100:].reset_index(drop=True)
    models = fit_subset_models(train, seed=79)

    selections = [
        select_candidate_specific_group(
            row=calibration.iloc[0],
            acquired={"signal_metrics"},
            models=models,
            calibration_frame=calibration,
            neighbours=20,
        )
        for _ in range(5)
    ]

    assert len(set(selections)) == 1
