import pandas as pd
import pytest

from evalml.data_checks import (
    DataCheckMessageCode,
    TimeSeriesSplittingDataCheck,
)


def test_time_series_splitting_data_check_raises_value_error():
    with pytest.raises(
        ValueError,
        match="Valid splitting of labels in time series",
    ):
        TimeSeriesSplittingDataCheck("time series regression", n_splits=3)


@pytest.mark.parametrize(
    "problem_type,is_valid",
    [
        ["time series binary", True],
        ["time series binary", False],
        ["time series multiclass", True],
        ["time series multiclass", False],
    ],
)
def test_time_series_param_data_check(problem_type, is_valid):
    X = None
    y = pd.Series([0 if i < 10 else 1 for i in range(100)])
    invalid_splits = {}

    if not is_valid:
        if problem_type == "time series binary":
            y = pd.Series([i % 2 if i < 25 else 1 for i in range(100)])
            invalid_splits = {1: {"Validation": [25, 50]},
                              2: {"Validation": [50, 75]},
                              3: {"Validation": [75, 100]}}
        elif problem_type == "time series multiclass":
            y = pd.Series([i % 3 if i > 65 else 2 for i in range(100)])
            invalid_splits = {1: {"Training": [0, 25],
                                  "Validation": [25, 50]},
                              2: {"Training": [0, 50]}}
    else:
        if problem_type == "time series binary":
            y = pd.Series([i % 2 for i in range(100)])
        elif problem_type == "time series multiclass":
            y = pd.Series([i % 3 for i in range(100)])

    data_check = TimeSeriesSplittingDataCheck("time series binary", 3)
    results = data_check.validate(X, y)
    code = DataCheckMessageCode.TIMESERIES_TARGET_NOT_COMPATIBLE_WITH_SPLIT.name

    if not is_valid:
        assert len(results["errors"]) == 1
        assert results["errors"][0]["details"] == {
            "columns": None,
            "rows": None,
            "invalid_splits": invalid_splits,
        }
        assert results["errors"][0]["code"] == code
    else:
        assert results == {"warnings": [], "errors": [], "actions": []}