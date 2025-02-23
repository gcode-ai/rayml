import pandas as pd
import pytest

from rayml.automl import AutoMLSearch
from rayml.problem_types import ProblemTypes

PERIODS = 500


@pytest.mark.parametrize(
    "problem_type",
    [
        ProblemTypes.TIME_SERIES_BINARY,
        ProblemTypes.TIME_SERIES_MULTICLASS,
        ProblemTypes.TIME_SERIES_REGRESSION,
    ],
)
def test_can_run_automl_for_time_series_with_categorical_and_boolean_features(
    problem_type,
):

    X = pd.DataFrame(
        {
            "features": range(101, 101 + PERIODS),
            "date": pd.date_range("2010-10-01", periods=PERIODS),
        }
    )
    y = pd.Series(range(PERIODS))
    if problem_type == ProblemTypes.TIME_SERIES_BINARY:
        y = y % 2
    elif problem_type == ProblemTypes.TIME_SERIES_MULTICLASS:
        y = y % 3

    X.ww.init()
    X.ww["bool_feature"] = (
        pd.Series([True, False])
        .sample(n=X.shape[0], replace=True)
        .reset_index(drop=True)
    )
    X.ww["cat_feature"] = (
        pd.Series(["a", "b", "c"])
        .sample(n=X.shape[0], replace=True)
        .reset_index(drop=True)
    )

    automl = AutoMLSearch(
        X,
        y,
        problem_type=problem_type,
        problem_configuration={
            "max_delay": 5,
            "gap": 3,
            "forecast_horizon": 2,
            "time_index": "date",
        },
        optimize_thresholds=False,
    )
    automl.search()
    automl.best_pipeline.fit(X, y)
    X_valid = pd.DataFrame(
        {
            "date": pd.date_range(
                pd.Timestamp(X.date.iloc[-1]) + pd.Timedelta("4d"), periods=2
            )
        }
    )
    # Treat all features as not known-in-advanced
    automl.best_pipeline.predict(X_valid, X_train=X, y_train=y)


@pytest.mark.parametrize(
    "problem_type",
    [
        ProblemTypes.TIME_SERIES_BINARY,
        ProblemTypes.TIME_SERIES_MULTICLASS,
        ProblemTypes.TIME_SERIES_REGRESSION,
    ],
)
def test_can_run_automl_for_time_series_known_in_advance(
    problem_type,
):

    X = pd.DataFrame(
        {
            "features": range(101, 101 + PERIODS),
            "date": pd.date_range("2010-10-01", periods=PERIODS),
        }
    )
    y = pd.Series(range(PERIODS))
    if problem_type == ProblemTypes.TIME_SERIES_BINARY:
        # So that we have coverage for sampling
        y = (
            pd.Series([1] * 50 + [0] * 450)
            .sample(frac=1, random_state=0, replace=False)
            .reset_index(drop=True)
        )
    elif problem_type == ProblemTypes.TIME_SERIES_MULTICLASS:
        y = y % 3

    X.ww.init()
    X.ww["bool_feature"] = (
        pd.Series([True, False])
        .sample(n=X.shape[0], replace=True)
        .reset_index(drop=True)
    )
    X.ww["cat_feature"] = (
        pd.Series(["a", "b", "c"])
        .sample(n=X.shape[0], replace=True)
        .reset_index(drop=True)
    )

    automl = AutoMLSearch(
        X,
        y,
        problem_type=problem_type,
        problem_configuration={
            "max_delay": 5,
            "gap": 3,
            "forecast_horizon": 2,
            "time_index": "date",
            "known_in_advance": ["bool_feature", "cat_feature"],
        },
        optimize_thresholds=False,
        sampler_method="Undersampler",
    )
    automl.search()
    automl.best_pipeline.fit(X, y)
    X_valid = pd.DataFrame(
        {
            "date": pd.date_range(
                pd.Timestamp(X.date.iloc[-1]) + pd.Timedelta("4d"), periods=2
            ),
            "bool_feature": [True, False],
            "cat_feature": ["a", "c"],
        }
    )
    # Treat all features as not known-in-advanced
    automl.best_pipeline.predict(X_valid, X_train=X, y_train=y)
