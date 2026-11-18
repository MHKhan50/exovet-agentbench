"""Candidate-specific evidence-value estimation using calibration neighbours."""

from __future__ import annotations

from typing import Iterable, Mapping

import numpy as np
import pandas as pd

from .config import GROUP_COSTS, GROUP_ORDER
from .models import (
    columns_for_groups,
    predict_candidate_probability,
    subset_key,
)
from .policies import binary_entropy


def _robust_scale(values: np.ndarray) -> float:
    """Return a stable scale estimate for a numeric feature."""
    q25, q75 = np.nanpercentile(values, [25, 75])
    scale = float(q75 - q25)

    if not np.isfinite(scale) or scale <= 1e-12:
        scale = float(np.nanstd(values))

    if not np.isfinite(scale) or scale <= 1e-12:
        return 1.0

    return scale


def _nearest_calibration_rows(
    row: pd.Series,
    calibration_frame: pd.DataFrame,
    acquired: Iterable[str],
    neighbours: int = 50,
) -> pd.DataFrame:
    """Find calibration rows most similar on currently acquired evidence only."""
    columns = columns_for_groups(acquired)

    if not columns:
        raise ValueError("At least one evidence group must be acquired.")

    if calibration_frame.empty:
        raise ValueError("Calibration frame must not be empty.")

    reference = calibration_frame[columns].astype(float)
    medians = reference.median(axis=0).fillna(0.0)

    reference = reference.fillna(medians)
    candidate = pd.to_numeric(
        row.reindex(columns), errors="coerce"
    ).fillna(medians)

    scales = pd.Series(
        {
            column: _robust_scale(
                reference[column].to_numpy(dtype=float)
            )
            for column in columns
        }
    )

    reference_scaled = (
        reference - medians
    ).div(scales, axis=1)

    candidate_scaled = (
        candidate - medians
    ).div(scales)

    distances = np.sqrt(
        np.square(
            reference_scaled.to_numpy(dtype=float)
            - candidate_scaled.to_numpy(dtype=float)
        ).mean(axis=1)
    )

    count = min(max(1, int(neighbours)), len(calibration_frame))
    nearest_indices = np.argsort(distances, kind="stable")[:count]

    return calibration_frame.iloc[nearest_indices].copy()


def select_candidate_specific_group(
    row: pd.Series,
    acquired: Iterable[str],
    models: Mapping[frozenset, object],
    calibration_frame: pd.DataFrame,
    neighbours: int = 50,
) -> str:
    """Select the group with greatest local entropy-reduction proxy per cost.

    Calibration labels are never inspected. Neighbour selection uses only
    features from groups already acquired by the agent. Unacquired calibration
    features are used only to estimate how the fitted subset models would
    change their predictions if that evidence group became available.

    This is a model-based acquisition heuristic, not exact expected
    information gain or proof of physical information value.
    """
    acquired_set = set(acquired)
    available = [
        group for group in GROUP_ORDER
        if group not in acquired_set
    ]

    if not available:
        raise ValueError("No evidence groups remain available.")

    current_subset = subset_key(acquired_set)

    if current_subset not in models:
        raise ValueError("No fitted model exists for the acquired evidence subset.")

    local_frame = _nearest_calibration_rows(
        row=row,
        calibration_frame=calibration_frame,
        acquired=acquired_set,
        neighbours=neighbours,
    )

    current_probabilities = predict_candidate_probability(
        models[current_subset],
        local_frame,
        acquired_set,
    )

    current_entropies = np.asarray(
        [binary_entropy(value) for value in current_probabilities]
    )

    scores = {}

    for group in available:
        next_subset = subset_key(acquired_set | {group})

        if next_subset not in models:
            raise ValueError(
                "No fitted model exists for evidence subset: "
                + ",".join(sorted(next_subset))
            )

        next_probabilities = predict_candidate_probability(
            models[next_subset],
            local_frame,
            acquired_set | {group},
        )

        next_entropies = np.asarray(
            [binary_entropy(value) for value in next_probabilities]
        )

        mean_reduction = float(
            np.mean(current_entropies - next_entropies)
        )

        scores[group] = mean_reduction / float(GROUP_COSTS[group])

    best_group = max(available, key=lambda group: scores[group])

    if scores[best_group] <= 0.0:
        return min(available, key=lambda group: GROUP_COSTS[group])

    return best_group
