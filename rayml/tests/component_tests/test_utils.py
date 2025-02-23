import inspect

import numpy as np
import pandas as pd
import pytest

from rayml.exceptions import MissingComponentError
from rayml.model_family import ModelFamily
from rayml.pipelines import (
    BinaryClassificationPipeline,
    MulticlassClassificationPipeline,
    RegressionPipeline,
)
from rayml.pipelines.components import ComponentBase, RandomForestClassifier
from rayml.pipelines.components.utils import (
    _all_estimators,
    all_components,
    estimator_unable_to_handle_nans,
    handle_component_class,
    make_balancing_dictionary,
    scikit_learn_wrapped_estimator,
)
from rayml.problem_types import ProblemTypes

binary = pd.Series([0] * 800 + [1] * 200)
multiclass = pd.Series([0] * 800 + [1] * 150 + [2] * 50)


minimum_dependencies_set = set(
    [
        "Baseline Classifier",
        "Baseline Regressor",
        "DFS Transformer",
        "DateTime Featurizer",
        "Decision Tree Classifier",
        "Decision Tree Regressor",
        "Time Series Featurizer",
        "Drop Columns Transformer",
        "Drop Null Columns Transformer",
        "Drop Rows Transformer",
        "Drop NaN Rows Transformer",
        "Elastic Net Classifier",
        "Elastic Net Regressor",
        "Email Featurizer",
        "Extra Trees Classifier",
        "Extra Trees Regressor",
        "Imputer",
        "KNN Classifier",
        "LSA Transformer",
        "Label Encoder",
        "Linear Discriminant Analysis Transformer",
        "Linear Regressor",
        "Log Transformer",
        "Logistic Regression Classifier",
        "One Hot Encoder",
        "PCA Transformer",
        "Per Column Imputer",
        "RF Classifier Select From Model",
        "RF Regressor Select From Model",
        "Random Forest Classifier",
        "Random Forest Regressor",
        "Replace Nullable Types Transformer",
        "SVM Classifier",
        "SVM Regressor",
        "Select Columns By Type Transformer",
        "Select Columns Transformer",
        "Simple Imputer",
        "Stacked Ensemble Classifier",
        "Stacked Ensemble Regressor",
        "Standard Scaler",
        "Target Imputer",
        "Natural Language Featurizer",
        "Time Series Baseline Estimator",
        "URL Featurizer",
        "Undersampler",
    ]
)
additional_requirements_set = set(
    [
        "ARIMA Regressor",
        "Exponential Smoothing Regressor",
        "CatBoost Classifier",
        "CatBoost Regressor",
        "LightGBM Classifier",
        "LightGBM Regressor",
        "Oversampler",
        "Polynomial Detrender",
        "Prophet Regressor",
        "Target Encoder",
        "Vowpal Wabbit Binary Classifier",
        "Vowpal Wabbit Multiclass Classifier",
        "Vowpal Wabbit Regressor",
        "XGBoost Classifier",
        "XGBoost Regressor",
    ]
)
all_requirements_set = minimum_dependencies_set.union(additional_requirements_set)
not_supported_in_conda = set(
    [
        "ARIMA Regressor",
        "Prophet Regressor",
        "Vowpal Wabbit Binary Classifier",
        "Vowpal Wabbit Multiclass Classifier",
        "Vowpal Wabbit Regressor",
    ]
)
not_supported_in_windows = set(
    [
        "Prophet Regressor",
    ]
)
not_supported_in_windows_py39 = set(
    [
        "ARIMA Regressor",
        "Polynomial Detrender",
        "Prophet Regressor",
    ]
)
not_supported_in_linux_py39 = set(
    ["ARIMA Regressor", "Polynomial Detrender", "Exponential Smoothing Regressor"]
)


def test_all_components(
    has_minimal_dependencies,
    is_running_py_39_or_above,
    is_using_conda,
    is_using_windows,
):
    if has_minimal_dependencies:
        expected_components = minimum_dependencies_set
    elif is_using_conda:
        # No prophet, ARIMA, and vowpalwabbit
        expected_components = all_requirements_set.difference(not_supported_in_conda)

    elif is_using_windows and not is_running_py_39_or_above:
        # No prophet
        expected_components = all_requirements_set.difference(not_supported_in_windows)

    elif is_using_windows and is_running_py_39_or_above:
        # No detrender, no ARIMA, no prophet
        expected_components = all_requirements_set.difference(
            not_supported_in_windows_py39
        )
    elif not is_using_windows and is_running_py_39_or_above:
        # No detrender or ARIMA
        expected_components = all_requirements_set.difference(
            not_supported_in_linux_py39
        )
    else:
        expected_components = all_requirements_set
    all_component_names = [component.name for component in all_components()]
    assert set(all_component_names) == expected_components


def test_handle_component_class_names():
    for cls in all_components():
        cls_ret = handle_component_class(cls)
        assert inspect.isclass(cls_ret)
        assert issubclass(cls_ret, ComponentBase)
        name_ret = handle_component_class(cls.name)
        assert inspect.isclass(name_ret)
        assert issubclass(name_ret, ComponentBase)

    invalid_name = "This Component Does Not Exist"
    with pytest.raises(
        MissingComponentError,
        match='Component "This Component Does Not Exist" was not found',
    ):
        handle_component_class(invalid_name)

    class NonComponent:
        pass

    with pytest.raises(ValueError):
        handle_component_class(NonComponent())


def test_scikit_learn_wrapper_invalid_problem_type():
    rayml_pipeline = MulticlassClassificationPipeline([RandomForestClassifier])
    rayml_pipeline.problem_type = None
    with pytest.raises(
        ValueError, match="Could not wrap rayml object in scikit-learn wrapper."
    ):
        scikit_learn_wrapped_estimator(rayml_pipeline)


def test_scikit_learn_wrapper(X_y_binary, X_y_multi, X_y_regression, ts_data):
    for estimator in [
        estimator
        for estimator in _all_estimators()
        if estimator.model_family != ModelFamily.ENSEMBLE
    ]:
        for problem_type in estimator.supported_problem_types:
            if problem_type == ProblemTypes.BINARY:
                X, y = X_y_binary
                num_classes = 2
                pipeline_class = BinaryClassificationPipeline
            elif problem_type == ProblemTypes.MULTICLASS:
                X, y = X_y_multi
                num_classes = 3
                pipeline_class = MulticlassClassificationPipeline
            elif problem_type == ProblemTypes.REGRESSION:
                X, y = X_y_regression
                pipeline_class = RegressionPipeline

            elif problem_type in [
                ProblemTypes.TIME_SERIES_REGRESSION,
                ProblemTypes.TIME_SERIES_MULTICLASS,
                ProblemTypes.TIME_SERIES_BINARY,
            ]:
                continue

            rayml_pipeline = pipeline_class([estimator])
            scikit_estimator = scikit_learn_wrapped_estimator(rayml_pipeline)
            scikit_estimator.fit(X, y)
            y_pred = scikit_estimator.predict(X)
            assert len(y_pred) == len(y)
            assert not np.isnan(y_pred).all()
            if problem_type in [ProblemTypes.BINARY, ProblemTypes.MULTICLASS]:
                y_pred_proba = scikit_estimator.predict_proba(X)
                assert y_pred_proba.shape == (len(y), num_classes)
                assert not np.isnan(y_pred_proba).all().all()


def test_make_balancing_dictionary_errors():
    with pytest.raises(ValueError, match="Sampling ratio must be in range"):
        make_balancing_dictionary(pd.Series([1]), 0)

    with pytest.raises(ValueError, match="Sampling ratio must be in range"):
        make_balancing_dictionary(pd.Series([1]), 1.1)

    with pytest.raises(ValueError, match="Sampling ratio must be in range"):
        make_balancing_dictionary(pd.Series([1]), -1)

    with pytest.raises(ValueError, match="Target data must not be empty"):
        make_balancing_dictionary(pd.Series([]), 0.5)


@pytest.mark.parametrize(
    "y,sampling_ratio,result",
    [
        (binary, 1, {0: 800, 1: 800}),
        (binary, 0.5, {0: 800, 1: 400}),
        (binary, 0.25, {0: 800, 1: 200}),
        (binary, 0.1, {0: 800, 1: 200}),
        (multiclass, 1, {0: 800, 1: 800, 2: 800}),
        (multiclass, 0.5, {0: 800, 1: 400, 2: 400}),
        (multiclass, 0.25, {0: 800, 1: 200, 2: 200}),
        (multiclass, 0.1, {0: 800, 1: 150, 2: 80}),
        (multiclass, 0.01, {0: 800, 1: 150, 2: 50}),
    ],
)
def test_make_balancing_dictionary(y, sampling_ratio, result):
    dic = make_balancing_dictionary(y, sampling_ratio)
    assert dic == result


def test_estimator_unable_to_handle_nans():
    test_estimator = RandomForestClassifier()
    assert estimator_unable_to_handle_nans(test_estimator) is True

    with pytest.raises(
        ValueError,
        match="`estimator_class` must have a `model_family` attribute.",
    ):
        estimator_unable_to_handle_nans("error")
