import numpy as np
from sklearn.linear_model import ElasticNet as SKElasticNetRegressor

from rayml.model_family import ModelFamily
from rayml.pipelines.components.estimators.regressors import (
    ElasticNetRegressor,
)
from rayml.problem_types import ProblemTypes


def test_model_family():
    assert ElasticNetRegressor.model_family == ModelFamily.LINEAR_MODEL


def test_en_parameters():
    clf = ElasticNetRegressor(alpha=0.75, l1_ratio=0.5, random_seed=2)
    expected_parameters = {
        "alpha": 0.75,
        "l1_ratio": 0.5,
        "max_iter": 1000,
        "normalize": False,
    }
    assert clf.parameters == expected_parameters


def test_problem_types():
    assert set(ElasticNetRegressor.supported_problem_types) == {
        ProblemTypes.REGRESSION,
        ProblemTypes.TIME_SERIES_REGRESSION,
    }


def test_fit_predict(X_y_regression):
    X, y = X_y_regression

    sk_clf = SKElasticNetRegressor(
        alpha=0.0001, l1_ratio=0.15, random_state=0, normalize=False, max_iter=1000
    )
    sk_clf.fit(X, y)
    y_pred_sk = sk_clf.predict(X)

    clf = ElasticNetRegressor()
    fitted = clf.fit(X, y)
    assert isinstance(fitted, ElasticNetRegressor)

    y_pred = clf.predict(X)
    np.testing.assert_almost_equal(y_pred_sk, y_pred.values, decimal=5)


def test_feature_importance(X_y_regression):
    X, y = X_y_regression

    sk_clf = SKElasticNetRegressor(
        alpha=0.0001, l1_ratio=0.15, random_state=0, normalize=False, max_iter=1000
    )
    sk_clf.fit(X, y)

    clf = ElasticNetRegressor()
    clf.fit(X, y)

    np.testing.assert_almost_equal(sk_clf.coef_, clf.feature_importance, decimal=5)
