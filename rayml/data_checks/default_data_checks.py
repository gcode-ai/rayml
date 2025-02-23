"""A default set of data checks that can be used for a variety of datasets."""
from .class_imbalance_data_check import ClassImbalanceDataCheck
from .data_checks import DataChecks
from .datetime_format_data_check import DateTimeFormatDataCheck
from .id_columns_data_check import IDColumnsDataCheck
from .invalid_target_data_check import InvalidTargetDataCheck
from .no_variance_data_check import NoVarianceDataCheck
from .null_data_check import NullDataCheck
from .target_distribution_data_check import TargetDistributionDataCheck
from .target_leakage_data_check import TargetLeakageDataCheck
from .ts_parameters_data_check import TimeSeriesParametersDataCheck
from .ts_splitting_data_check import TimeSeriesSplittingDataCheck

from rayml.problem_types import (
    ProblemTypes,
    handle_problem_types,
    is_classification,
    is_time_series,
)


class DefaultDataChecks(DataChecks):
    """A collection of basic data checks that is used by AutoML by default.

    Includes:

        - `NullDataCheck`
        - `HighlyNullRowsDataCheck`
        - `IDColumnsDataCheck`
        - `TargetLeakageDataCheck`
        - `InvalidTargetDataCheck`
        - `NoVarianceDataCheck`
        - `ClassImbalanceDataCheck` (for classification problem types)
        - `TargetDistributionDataCheck` (for regression problem types)
        - `DateTimeFormatDataCheck` (for time series problem types)
        - 'TimeSeriesParametersDataCheck' (for time series problem types)
        - `TimeSeriesSplittingDataCheck` (for time series classification problem types)

    Args:
        problem_type (str): The problem type that is being validated. Can be regression, binary, or multiclass.
        objective (str or ObjectiveBase): Name or instance of the objective class.
        n_splits (int): The number of splits as determined by the data splitter being used. Defaults to 3.
        datetime_column (str): The name of the column containing datetime information to be used for time series problems.
        Default to "index" indicating that the datetime information is in the index of X or y.
    """

    _DEFAULT_DATA_CHECK_CLASSES = [
        NullDataCheck,
        IDColumnsDataCheck,
        TargetLeakageDataCheck,
        InvalidTargetDataCheck,
        NoVarianceDataCheck,
    ]

    def __init__(self, problem_type, objective, n_splits=3, problem_configuration=None):
        default_checks = self._DEFAULT_DATA_CHECK_CLASSES
        data_check_params = {}

        if is_time_series(problem_type):
            if problem_configuration is None:
                raise ValueError(
                    "problem_configuration cannot be None for time series problems!"
                )
            if is_classification(problem_type):
                default_checks = default_checks + [TimeSeriesSplittingDataCheck]
                data_check_params.update(
                    {
                        "TimeSeriesSplittingDataCheck": {
                            "problem_type": problem_type,
                            "n_splits": n_splits,
                        }
                    }
                )
            default_checks = default_checks + [
                DateTimeFormatDataCheck,
                TimeSeriesParametersDataCheck,
            ]
            data_check_params.update(
                {
                    "DateTimeFormatDataCheck": {
                        "datetime_column": problem_configuration["time_index"],
                    },
                    "TimeSeriesParametersDataCheck": {
                        "problem_configuration": problem_configuration,
                        "n_splits": n_splits,
                    },
                }
            )

        if handle_problem_types(problem_type) in [
            ProblemTypes.REGRESSION,
            ProblemTypes.TIME_SERIES_REGRESSION,
        ]:
            default_checks = default_checks + [TargetDistributionDataCheck]
            data_check_params.update(
                {
                    "InvalidTargetDataCheck": {
                        "problem_type": problem_type,
                        "objective": objective,
                    }
                }
            )
        else:
            default_checks = default_checks + [ClassImbalanceDataCheck]
            data_check_params.update(
                {
                    "InvalidTargetDataCheck": {
                        "problem_type": problem_type,
                        "objective": objective,
                    },
                    "ClassImbalanceDataCheck": {"num_cv_folds": n_splits},
                }
            )

        super().__init__(
            default_checks,
            data_check_params=data_check_params,
        )
