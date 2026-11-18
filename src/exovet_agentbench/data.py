"""NASA Exoplanet Archive ingestion and dataset preparation."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from .config import (
    EXCLUDED_LEAKAGE_COLUMNS,
    FEATURE_COLUMNS,
    FEATURE_GROUPS,
    FEATURE_QUERY,
    FEATURE_TABLE_NAME,
    LABEL_COLUMN,
    MAX_MISSING_SHARE,
    QUERY,
    RAW_COLUMNS,
    TAP_ENDPOINT,
    TABLE_NAME,
    TARGET_MAPPING,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_download_url(query: str = QUERY) -> str:
    return TAP_ENDPOINT + "?" + urlencode({"query": query, "format": "csv"})


def _validate_csv_text(text: str, required) -> int:
    reader = csv.DictReader(text.splitlines())
    if not reader.fieldnames:
        raise ValueError("NASA TAP response did not contain a CSV header.")
    missing = sorted(set(required) - set(reader.fieldnames))
    if missing:
        raise ValueError("NASA TAP response is missing required columns: " + ", ".join(missing))
    return sum(1 for _ in reader)


def _fetch_csv(query: str, required, timeout: int) -> str:
    request = Request(
        build_download_url(query),
        headers={
            "User-Agent": "ExoVet-AgentBench/0.2.0 (reproducible research dataset client)",
            "Accept": "text/csv",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        text = response.read().decode("utf-8-sig")
    if text.lstrip().lower().startswith(("error", "<!doctype", "<html")):
        raise RuntimeError("NASA TAP returned an error page instead of CSV data: " + text[:300])
    if _validate_csv_text(text, required) == 0:
        raise RuntimeError("NASA TAP returned a valid CSV header but no rows.")
    return text


def download_dataset(output_path: str, timeout: int = 90) -> Dict[str, object]:
    """Download DR25 Supplemental labels and DR25 KOI features, join them on kepoi_name and write provenance."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    labels_text = _fetch_csv(QUERY, ["kepid", "kepoi_name", LABEL_COLUMN], timeout)
    features_text = _fetch_csv(FEATURE_QUERY, ["kepoi_name"] + FEATURE_COLUMNS, timeout)
    labels = pd.read_csv(io.StringIO(labels_text), dtype={"kepid": "string", "kepoi_name": "string"})
    features = pd.read_csv(io.StringIO(features_text), dtype={"kepoi_name": "string"})
    features = features.drop_duplicates(subset=["kepoi_name"], keep="first")
    joined = labels.merge(features, on="kepoi_name", how="inner", validate="many_to_one")
    joined = joined[RAW_COLUMNS]
    joined.to_csv(path, index=False)
    manifest: Dict[str, object] = {
        "dataset": "Kepler Q1-Q17 DR25 Supplemental dispositions joined to Q1-Q17 DR25 KOI transit fits",
        "label_table": TABLE_NAME,
        "feature_table": FEATURE_TABLE_NAME,
        "label_url": build_download_url(QUERY),
        "feature_url": build_download_url(FEATURE_QUERY),
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "label_rows": int(len(labels)),
        "feature_rows": int(len(features)),
        "row_count_raw": int(len(joined)),
        "label_rows_without_dr25_fit": int(len(labels) - len(joined)),
        "sha256": sha256_file(path),
        "label_column": LABEL_COLUMN,
        "target_mapping": TARGET_MAPPING,
        "excluded_leakage_columns": EXCLUDED_LEAKAGE_COLUMNS,
        "archive_doi": "10.26133/NEA5",
        "note": "Archive snapshot; record retrieval timestamp because the archive may update table content.",
    }
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def prepare_dataset(raw_path: str, output_path: str) -> Dict[str, object]:
    """Create a numeric, leakage-screened modelling table from the downloaded CSV."""
    raw_file = Path(raw_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(raw_file, dtype={"kepid": "string", "kepoi_name": "string"})
    required = set(RAW_COLUMNS)
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError("Raw dataset is missing required columns: " + ", ".join(missing))

    disposition = frame[LABEL_COLUMN].astype("string").str.strip().str.upper()
    frame["target"] = disposition.map(TARGET_MAPPING)
    frame = frame.loc[frame["target"].notna()].copy()
    frame = frame.dropna(subset=["kepid", "kepoi_name"])
    frame = frame.drop_duplicates(subset=["kepoi_name"], keep="first")
    frame["target"] = frame["target"].astype("int64")

    feature_columns = [column for columns in FEATURE_GROUPS.values() for column in columns]
    for column in feature_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    missing_share = frame[feature_columns].isna().mean()
    empty = sorted(missing_share[missing_share > MAX_MISSING_SHARE].index)
    if empty:
        raise ValueError(
            "These features are missing for more than {:.0%} of rows, so the download is unusable: {}".format(
                MAX_MISSING_SHARE, ", ".join(empty)
            )
        )

    keep_columns = ["kepid", "kepoi_name", "target"] + feature_columns
    prepared = frame[keep_columns].reset_index(drop=True)
    if prepared["target"].nunique() != 2:
        raise ValueError("Prepared data must contain both CANDIDATE and FALSE POSITIVE rows.")
    prepared.to_csv(output_file, index=False)

    manifest = {
        "source_raw_file": str(raw_file),
        "source_raw_sha256": sha256_file(raw_file),
        "prepared_file": str(output_file),
        "prepared_sha256": sha256_file(output_file),
        "rows": int(len(prepared)),
        "class_counts": {str(key): int(value) for key, value in prepared["target"].value_counts().sort_index().items()},
        "target_mapping": TARGET_MAPPING,
        "feature_groups": FEATURE_GROUPS,
        "excluded_columns": EXCLUDED_LEAKAGE_COLUMNS,
        "note": "Target 1=CANDIDATE and 0=FALSE POSITIVE; target and excluded leakage fields are not model inputs.",
    }
    output_file.with_suffix(output_file.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def load_prepared_dataset(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"kepid": "string", "kepoi_name": "string"})
    required = {"kepid", "kepoi_name", "target"}
    required.update(column for columns in FEATURE_GROUPS.values() for column in columns)
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError("Prepared dataset is missing required columns: " + ", ".join(missing))
    frame["target"] = pd.to_numeric(frame["target"], errors="raise").astype("int64")
    if not set(frame["target"].unique()).issubset({0, 1}):
        raise ValueError("Target must contain only 0 and 1.")
    if frame["kepid"].isna().any():
        raise ValueError("Host-star identifiers (kepid) cannot be missing for grouped splitting.")
    return frame
