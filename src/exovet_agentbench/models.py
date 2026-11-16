"""Lightweight classifiers used by the evidence-acquisition environment."""

from __future__ import annotations

from itertools import combinations
from typing import Dict, FrozenSet, Iterable, List, Sequence

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import FEATURE_GROUPS, GROUP_ORDER


def subset_key(groups: Iterable[str]) -> FrozenSet[str]:
    return frozenset(groups)


def all_nonempty_subsets(group_names: Sequence[str] = GROUP_ORDER) -> List[FrozenSet[str]]:
    subsets: List[FrozenSet[str]] = []
    for size in range(1, len(group_names) + 1):
        for values in combinations(group_names, size):
            subsets.append(frozenset(values))
    return subsets


def columns_for_groups(groups: Iterable[str]) -> List[str]:
    selected = set(groups)
    return [
        column
        for group in GROUP_ORDER
        if group in selected
        for column in FEATURE_GROUPS[group]
    ]


def make_estimator(seed: int = 17) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True)),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=1200,
            class_weight="balanced",
            solver="liblinear",
            random_state=seed,
        )),
    ])


def fit_subset_models(frame: pd.DataFrame, seed: int = 17) -> Dict[FrozenSet[str], Pipeline]:
    models: Dict[FrozenSet[str], Pipeline] = {}
    y = frame["target"].to_numpy(dtype=int)
    for subset in all_nonempty_subsets():
        columns = columns_for_groups(subset)
        model = make_estimator(seed)
        model.fit(frame[columns], y)
        models[subset] = model
    return models


def predict_candidate_probability(model: Pipeline, frame: pd.DataFrame, groups: Iterable[str]) -> np.ndarray:
    columns = columns_for_groups(groups)
    return model.predict_proba(frame[columns])[:, 1]
