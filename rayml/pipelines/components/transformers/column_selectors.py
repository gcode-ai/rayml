"""Initalizes an transformer that selects specified columns in input data."""
from abc import abstractmethod

from rayml.pipelines.components.transformers import Transformer
from rayml.utils import infer_feature_types


class ColumnSelector(Transformer):
    """Initalizes an transformer that selects specified columns in input data.

    Args:
        columns (list(string)): List of column names, used to determine which columns to select.
        random_seed (int): Seed for the random number generator. Defaults to 0.
    """

    def __init__(self, columns=None, random_seed=0, **kwargs):
        if columns and not isinstance(columns, list):
            raise ValueError(
                f"Parameter columns must be a list. Received {type(columns)}."
            )

        parameters = {"columns": columns}
        parameters.update(kwargs)
        super().__init__(
            parameters=parameters, component_obj=None, random_seed=random_seed
        )

    def _check_input_for_columns(self, X):
        cols = self.parameters.get("columns") or []
        column_names = X.columns

        missing_cols = set(cols) - set(column_names)
        if missing_cols:
            raise ValueError(f"Columns of type {missing_cols} not found in input data.")

    @abstractmethod
    def _modify_columns(self, cols, X, y=None):
        """How the transformer modifies the columns of the input data."""

    def fit(self, X, y=None):
        """Fits the transformer by checking if column names are present in the dataset.

        Args:
            X (pd.DataFrame): Data to check.
            y (pd.Series, ignored): Targets.

        Returns:
            self
        """
        X = infer_feature_types(X)
        self._check_input_for_columns(X)
        return self

    def transform(self, X, y=None):
        """Transform data using fitted column selector component.

        Args:
            X (pd.DataFrame): The input training data of shape [n_samples, n_features].
            y (pd.Series, optional): The target training data of length [n_samples].

        Returns:
            pd.DataFrame: Transformed data.
        """
        X = infer_feature_types(X)
        self._check_input_for_columns(X)
        cols = self.parameters.get("columns") or []
        modified_cols = self._modify_columns(cols, X, y)
        return infer_feature_types(modified_cols)


class DropColumns(ColumnSelector):
    """Drops specified columns in input data.

    Args:
        columns (list(string)): List of column names, used to determine which columns to drop.
        random_seed (int): Seed for the random number generator. Defaults to 0.
    """

    name = "Drop Columns Transformer"
    hyperparameter_ranges = {}
    """{}"""
    needs_fitting = False

    def _check_input_for_columns(self, X):
        pass

    def _modify_columns(self, cols, X, y=None):
        column_intersection = list(set(cols).intersection(X.columns))
        return X.ww.drop(column_intersection)

    def transform(self, X, y=None):
        """Transforms data X by dropping columns.

        Args:
            X (pd.DataFrame): Data to transform.
            y (pd.Series, optional): Targets.

        Returns:
            pd.DataFrame: Transformed X.
        """
        return super().transform(X, y)


class SelectColumns(ColumnSelector):
    """Selects specified columns in input data.

    Args:
        columns (list(string)): List of column names, used to determine which columns to select. If columns are not present, they will not be selected.
        random_seed (int): Seed for the random number generator. Defaults to 0.
    """

    name = "Select Columns Transformer"
    hyperparameter_ranges = {}
    """{}"""
    needs_fitting = False

    def _check_input_for_columns(self, X):
        pass

    def fit(self, X, y=None):
        """Fits the transformer by checking if column names are present in the dataset.

        Args:
            X (pd.DataFrame): Data to check.
            y (pd.Series, optional): Targets.

        Returns:
            self
        """
        return self

    def _modify_columns(self, cols, X, y=None):
        column_intersection = list(
            sorted(set(cols).intersection(X.columns), key=cols.index)
        )
        return X.ww[column_intersection]


class SelectByType(Transformer):
    """Selects columns by specified Woodwork logical type or semantic tag in input data.

    Args:
        column_types (string, ww.LogicalType, list(string), list(ww.LogicalType)): List of Woodwork types or tags, used to determine which columns to select or exclude.
        exclude (bool): If true, exclude the column_types instead of including them. Defaults to False.
        random_seed (int): Seed for the random number generator. Defaults to 0.
    """

    name = "Select Columns By Type Transformer"
    hyperparameter_ranges = {}
    """{}"""
    needs_fitting = False

    def __init__(self, column_types=None, exclude=False, random_seed=0, **kwargs):
        parameters = {"column_types": column_types, "exclude": exclude}
        parameters.update(kwargs)
        super().__init__(
            parameters=parameters,
            component_obj=None,
            random_seed=random_seed,
        )

    def _modify_columns(self, cols, X, y=None):
        if self.parameters.get("exclude"):
            return X.ww.select(exclude=cols)
        return X.ww.select(include=cols)

    def fit(self, X, y=None):
        """Fits the transformer by checking if column names are present in the dataset.

        Args:
            X (pd.DataFrame): Data to check.
            y (pd.Series, ignored): Targets.

        Returns:
            self
        """
        X = infer_feature_types(X)
        return self

    def transform(self, X, y=None):
        """Transforms data X by selecting columns.

        Args:
            X (pd.DataFrame): Data to transform.
            y (pd.Series, optional): Targets.

        Returns:
            pd.DataFrame: Transformed X.
        """
        X = infer_feature_types(X)
        cols = self.parameters.get("column_types") or []
        modified_cols = self._modify_columns(cols, X, y)
        return infer_feature_types(modified_cols)
