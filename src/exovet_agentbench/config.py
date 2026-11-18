"""Project configuration and feature-group definitions."""

from collections import OrderedDict

TAP_ENDPOINT = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
# Labels come from the DR25 Supplemental table, which has disposition priority in the archive.
# Its transit-fit and stellar columns are empty, so features come from the DR25 KOI table, which
# has transit-fit priority. The two are joined on kepoi_name.
TABLE_NAME = "q1_q17_dr25_sup_koi"
FEATURE_TABLE_NAME = "q1_q17_dr25_koi"

# Target is deliberately limited to the two DR25 Supplemental catalogue dispositions.
LABEL_COLUMN = "koi_disposition"
TARGET_MAPPING = {"FALSE POSITIVE": 0, "CANDIDATE": 1}

# These are normalized benchmark assumptions, not measured telescope or analyst costs.
GROUP_COSTS = OrderedDict([
    ("signal_metrics", 1.0),
    ("transit_geometry", 1.2),
    ("fit_quality", 1.4),
    ("stellar_context", 1.8),
])

FEATURE_GROUPS = OrderedDict([
    ("signal_metrics", [
        "koi_model_snr",
        "koi_num_transits",
        "koi_max_mult_ev",
        "koi_max_sngle_ev",
    ]),
    ("transit_geometry", [
        "koi_period",
        "koi_duration",
        "koi_depth",
        "koi_impact",
        "koi_ror",
        "koi_srho",
    ]),
    ("fit_quality", [
        "koi_model_chisq",
        "koi_model_dof",
    ]),
    ("stellar_context", [
        "koi_steff",
        "koi_slogg",
        "koi_smet",
        "koi_srad",
        "koi_smass",
        "koi_sage",
    ]),
])

GROUP_ORDER = tuple(FEATURE_GROUPS.keys())
INITIAL_GROUP = "signal_metrics"
FIXED_ORDER = GROUP_ORDER
DEFAULT_CONFIDENCE_THRESHOLD = 0.85
DEFAULT_MAX_BUDGET = float(sum(GROUP_COSTS.values()))

# Explicitly excluded because they directly encode or are derived from the DR25 vetting decision.
EXCLUDED_LEAKAGE_COLUMNS = [
    "koi_score",
    "koi_fpflag_nt",
    "koi_fpflag_ss",
    "koi_fpflag_co",
    "koi_fpflag_ec",
    "koi_comment",
    "koi_disp_prov",
    "koi_pdisposition",
    "koi_disposition",
]

RAW_COLUMNS = [
    "kepid",
    "kepoi_name",
    LABEL_COLUMN,
] + [column for columns in FEATURE_GROUPS.values() for column in columns]

QUERY = (
    "SELECT kepid,kepoi_name," + LABEL_COLUMN +
    " FROM " + TABLE_NAME +
    " WHERE " + LABEL_COLUMN + " IN ('CANDIDATE','FALSE POSITIVE')"
)

FEATURE_COLUMNS = [column for columns in FEATURE_GROUPS.values() for column in columns]
FEATURE_QUERY = "SELECT kepoi_name," + ",".join(FEATURE_COLUMNS) + " FROM " + FEATURE_TABLE_NAME

# A feature that is missing for more than this share of rows stops preparation with an error.
MAX_MISSING_SHARE = 0.5
