import pandas as pd
import pytest

from exovet_agentbench.config import (
    EXCLUDED_LEAKAGE_COLUMNS,
    FEATURE_GROUPS,
    FEATURE_QUERY,
    FEATURE_TABLE_NAME,
    LABEL_COLUMN,
    QUERY,
    RAW_COLUMNS,
    TABLE_NAME,
)
from exovet_agentbench.data import _validate_csv_text, build_download_url, prepare_dataset


def test_query_targets_supplemental_table_without_leakage_fields():
    assert TABLE_NAME == "q1_q17_dr25_sup_koi"
    assert LABEL_COLUMN == "koi_disposition"
    assert FEATURE_TABLE_NAME == "q1_q17_dr25_koi"
    assert TABLE_NAME in QUERY and FEATURE_TABLE_NAME in FEATURE_QUERY
    for query in (QUERY, FEATURE_QUERY):
        assert "koi_pdisposition" not in query
        assert "koi_score" not in query
        assert not any(column.startswith("koi_fpflag_") for column in query.split(","))
    assert LABEL_COLUMN not in FEATURE_QUERY
    feature_columns = {column for columns in FEATURE_GROUPS.values() for column in columns}
    assert not feature_columns.intersection(EXCLUDED_LEAKAGE_COLUMNS)
    assert "format=csv" in build_download_url()


def test_csv_schema_validation_counts_rows():
    header = ",".join(RAW_COLUMNS)
    values = ["1", "K00001.01", "CANDIDATE"] + ["1.0"] * (len(RAW_COLUMNS) - 3)
    assert _validate_csv_text(header + "\n" + ",".join(values), RAW_COLUMNS) == 1


def test_csv_schema_validation_rejects_missing_columns():
    with pytest.raises(ValueError):
        _validate_csv_text("kepid,kepoi_name\n1,K00001.01", RAW_COLUMNS)


def test_prepare_dataset_maps_target_and_excludes_leakage(tmp_path):
    rows = []
    for index, disposition in enumerate(["CANDIDATE", "FALSE POSITIVE", "NOT DISPOSITIONED"]):
        row = {column: "1.0" for column in RAW_COLUMNS}
        row["kepid"] = str(100 + index)
        row["kepoi_name"] = "K{:05d}.01".format(index)
        row["koi_disposition"] = disposition
        rows.append(row)
    raw_path = tmp_path / "raw.csv"
    out_path = tmp_path / "prepared.csv"
    pd.DataFrame(rows).to_csv(raw_path, index=False)
    manifest = prepare_dataset(str(raw_path), str(out_path))
    prepared = pd.read_csv(out_path)
    assert len(prepared) == 2
    assert set(prepared["target"]) == {0, 1}
    assert "koi_disposition" not in prepared.columns
    assert "koi_pdisposition" not in prepared.columns
    assert manifest["rows"] == 2


def test_prepare_dataset_rejects_empty_feature_columns(tmp_path):
    rows = []
    for index, disposition in enumerate(["CANDIDATE", "FALSE POSITIVE"] * 3):
        row = {column: "" for column in RAW_COLUMNS}
        row.update({"kepid": str(index), "kepoi_name": "K{:05d}.01".format(index), "koi_disposition": disposition, "koi_period": "3.0"})
        rows.append(row)
    raw_path = tmp_path / "raw.csv"
    pd.DataFrame(rows).to_csv(raw_path, index=False)
    with pytest.raises(ValueError, match="missing for more than"):
        prepare_dataset(str(raw_path), str(tmp_path / "prepared.csv"))
