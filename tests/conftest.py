import numpy as np
import pandas as pd
import pytest

from exovet_agentbench.config import FEATURE_GROUPS


@pytest.fixture
def toy_frame():
    rng = np.random.default_rng(19)
    rows = []
    for index in range(160):
        target = index % 2
        row = {
            "kepid": "host-{:03d}".format(index),
            "kepoi_name": "K{:05d}.01".format(index),
            "target": target,
        }
        for group_index, columns in enumerate(FEATURE_GROUPS.values()):
            for column_index, column in enumerate(columns):
                signal = (target * 1.2) + (group_index * 0.05)
                row[column] = float(signal + rng.normal(0.0, 0.8) + column_index * 0.01)
        rows.append(row)
    return pd.DataFrame(rows)
