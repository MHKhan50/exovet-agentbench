"""Sequential policies for budgeted evidence acquisition."""

from __future__ import annotations

import math
import random
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from .config import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_MAX_BUDGET,
    FIXED_ORDER,
    GROUP_COSTS,
    GROUP_ORDER,
    INITIAL_GROUP,
)
from .models import columns_for_groups, predict_candidate_probability, subset_key


def binary_entropy(probability: float) -> float:
    p = min(max(float(probability), 1e-9), 1.0 - 1e-9)
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def confidence_bucket(probability: float) -> str:
    confidence = max(float(probability), 1.0 - float(probability))
    if confidence < 0.65:
        return "low"
    if confidence < 0.85:
        return "medium"
    return "high"


def _ordered_subset(groups: Iterable[str]) -> Tuple[str, ...]:
    selected = set(groups)
    return tuple(group for group in GROUP_ORDER if group in selected)


def build_adaptive_policy_table(
    calibration_models: Mapping[frozenset, object],
    calibration_frame: pd.DataFrame,
) -> Dict[Tuple[Tuple[str, ...], str], str]:
    """Estimate confidence-conditioned information gain using a held-out calibration split.

    The policy table uses only model probabilities on calibration rows. It does not inspect
    calibration labels or any outer-test labels when choosing the next evidence group.
    """
    table: Dict[Tuple[Tuple[str, ...], str], str] = {}
    for subset in calibration_models:
        if INITIAL_GROUP not in subset or len(subset) == len(GROUP_ORDER):
            continue
        current_model = calibration_models[subset]
        current_p = predict_candidate_probability(current_model, calibration_frame, subset)
        buckets = np.asarray([confidence_bucket(value) for value in current_p], dtype=object)
        remaining = [group for group in GROUP_ORDER if group not in subset]
        candidate_scores: Dict[str, Dict[str, float]] = {}
        for group in remaining:
            next_subset = subset_key(set(subset) | {group})
            next_model = calibration_models[next_subset]
            next_p = predict_candidate_probability(next_model, calibration_frame, next_subset)
            gains = np.asarray([
                binary_entropy(before) - binary_entropy(after)
                for before, after in zip(current_p, next_p)
            ])
            candidate_scores[group] = {}
            for bucket in ("low", "medium", "high"):
                mask = buckets == bucket
                values = gains[mask] if mask.any() else gains
                candidate_scores[group][bucket] = float(np.mean(values)) / float(GROUP_COSTS[group])
        for bucket in ("low", "medium", "high"):
            scores = {group: values[bucket] for group, values in candidate_scores.items()}
            best_group = max(scores, key=scores.get)
            if scores[best_group] <= 0.0:
                best_group = min(remaining, key=lambda group: GROUP_COSTS[group])
            table[(_ordered_subset(subset), bucket)] = best_group
    return table


def _visible_evidence(row: pd.Series, acquired: Iterable[str]) -> Dict[str, Optional[float]]:
    visible: Dict[str, Optional[float]] = {}
    for column in columns_for_groups(acquired):
        value = row.get(column)
        visible[column] = None if pd.isna(value) else float(value)
    return visible


def run_single_policy(
    row: pd.Series,
    models: Mapping[frozenset, object],
    policy: str,
    policy_table: Mapping[Tuple[Tuple[str, ...], str], str],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    max_budget: float = DEFAULT_MAX_BUDGET,
    seed: int = 17,
    ollama_agent: Optional[object] = None,
) -> Dict[str, object]:
    """Run one policy on one candidate without exposing unrequested feature groups."""
    if policy not in {"signal_only", "fixed", "random", "adaptive", "full_information", "ollama"}:
        raise ValueError("Unknown policy: " + policy)
    acquired = {INITIAL_GROUP}
    spent = float(GROUP_COSTS[INITIAL_GROUP])
    trace: List[Dict[str, object]] = [{
        "action": "acquire",
        "group": INITIAL_GROUP,
        "cost": float(GROUP_COSTS[INITIAL_GROUP]),
        "reason": "initial low-cost signal evidence",
    }]
    invalid_actions = 0
    fallback_actions = 0
    budget_guard_events = 0
    rng = random.Random(seed)

    if policy == "full_information":
        for group in GROUP_ORDER:
            if group == INITIAL_GROUP:
                continue
            acquired.add(group)
            spent += float(GROUP_COSTS[group])
            trace.append({"action": "acquire", "group": group, "cost": float(GROUP_COSTS[group]), "reason": "full-information reference"})
    elif policy != "signal_only":
        while True:
            current_subset = subset_key(acquired)
            current_model = models[current_subset]
            current_probability = float(predict_candidate_probability(current_model, pd.DataFrame([row]), acquired)[0])
            confidence = max(current_probability, 1.0 - current_probability)
            if policy != "ollama" and confidence >= confidence_threshold:
                trace.append({"action": "stop", "reason": "confidence threshold reached", "confidence": confidence})
                break
            available = [group for group in GROUP_ORDER if group not in acquired]
            if not available:
                trace.append({"action": "stop", "reason": "all evidence groups acquired"})
                break
            if spent >= max_budget:
                trace.append({"action": "stop", "reason": "budget exhausted"})
                break

            next_group: Optional[str]
            if policy == "fixed":
                next_group = next((group for group in FIXED_ORDER if group in available), None)
            elif policy == "random":
                next_group = rng.choice(available)
            elif policy == "adaptive":
                key = (_ordered_subset(acquired), confidence_bucket(current_probability))
                next_group = policy_table.get(key)
                if next_group not in available:
                    next_group = min(available, key=lambda group: GROUP_COSTS[group])
            else:  # optional local Ollama agent
                try:
                    next_group = ollama_agent.choose_next_group(
                        available_groups=available,
                        acquired_groups=sorted(acquired, key=GROUP_ORDER.index),
                        remaining_budget=max_budget - spent,
                        current_probability=current_probability,
                        visible_features=_visible_evidence(row, acquired),
                    )
                    if next_group is not None and next_group not in available:
                        raise ValueError("Ollama returned a group that is not available.")
                except Exception as exc:  # fail closed to a deterministic policy
                    invalid_actions += 1
                    fallback_actions += 1
                    key = (_ordered_subset(acquired), confidence_bucket(current_probability))
                    next_group = policy_table.get(key)
                    if next_group not in available:
                        next_group = min(available, key=lambda group: GROUP_COSTS[group])
                    trace.append({"action": "fallback", "reason": type(exc).__name__})

            if next_group is None:
                trace.append({"action": "stop", "reason": "agent elected to stop"})
                break
            if spent + float(GROUP_COSTS[next_group]) > max_budget:
                if policy == "ollama":
                    budget_guard_events += 1
                    invalid_actions += 1
                    fallback_actions += 1
                    trace.append({"action": "budget_guard", "requested_group": next_group, "reason": "requested group exceeds remaining budget"})
                    key = (_ordered_subset(acquired), confidence_bucket(current_probability))
                    adaptive_group = policy_table.get(key)
                    if adaptive_group in available and spent + float(GROUP_COSTS[adaptive_group]) <= max_budget:
                        next_group = adaptive_group
                affordable = [group for group in available if spent + float(GROUP_COSTS[group]) <= max_budget]
                if not affordable:
                    trace.append({"action": "stop", "reason": "no remaining group fits budget"})
                    break
                if next_group not in affordable:
                    next_group = min(affordable, key=lambda group: GROUP_COSTS[group])
            acquired.add(next_group)
            spent += float(GROUP_COSTS[next_group])
            trace.append({
                "action": "acquire",
                "group": next_group,
                "cost": float(GROUP_COSTS[next_group]),
                "reason": "sequential evidence request",
            })

    final_subset = subset_key(acquired)
    final_model = models[final_subset]
    final_probability = float(predict_candidate_probability(final_model, pd.DataFrame([row]), acquired)[0])
    prediction = int(final_probability >= 0.5)
    return {
        "probability_candidate": final_probability,
        "prediction": prediction,
        "acquisition_cost": spent,
        "groups_acquired": len(acquired),
        "acquired_groups": ";".join(group for group in GROUP_ORDER if group in acquired),
        "trace": trace,
        "invalid_actions": invalid_actions,
        "fallback_actions": fallback_actions,
        "budget_guard_events": budget_guard_events,
    }
