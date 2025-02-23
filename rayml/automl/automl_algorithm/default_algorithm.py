"""An automl algorithm that consists of two modes: fast and long, where fast is a subset of long."""
import inspect
import logging

import numpy as np
from skopt.space import Categorical, Integer, Real

from .automl_algorithm import AutoMLAlgorithm

from rayml.model_family import ModelFamily
from rayml.pipelines.components import (
    RFClassifierSelectFromModel,
    RFRegressorSelectFromModel,
)
from rayml.pipelines.components.transformers.column_selectors import (
    SelectByType,
    SelectColumns,
)
from rayml.pipelines.components.utils import (
    get_estimators,
    handle_component_class,
)
from rayml.pipelines.utils import (
    _make_pipeline_from_multiple_graphs,
    make_pipeline,
)
from rayml.problem_types import is_regression, is_time_series
from rayml.utils import infer_feature_types
from rayml.utils.logger import get_logger


class DefaultAlgorithm(AutoMLAlgorithm):
    """An automl algorithm that consists of two modes: fast and long, where fast is a subset of long.

    1. Naive pipelines:
        a. run baseline with default preprocessing pipeline
        b. run naive linear model with default preprocessing pipeline
        c. run basic RF pipeline with default preprocessing pipeline
    2. Naive pipelines with feature selection
        a. subsequent pipelines will use the selected features with a SelectedColumns transformer

    At this point we have a single pipeline candidate for preprocessing and feature selection

    3. Pipelines with preprocessing components:
        a. scan rest of estimators (our current batch 1).
    4. First ensembling run

    Fast mode ends here. Begin long mode.

    6. Run top 3 estimators:
        a. Generate 50 random parameter sets. Run all 150 in one batch
    7. Second ensembling run
    8. Repeat these indefinitely until stopping criterion is met:
        a. For each of the previous top 3 estimators, sample 10 parameters from the tuner. Run all 30 in one batch
        b. Run ensembling

    Args:
        X (pd.DataFrame): Training data.
        y (pd.Series): Target data.
        problem_type (ProblemType): Problem type associated with training data.
        sampler_name (BaseSampler): Sampler to use for preprocessing.
        tuner_class (class): A subclass of Tuner, to be used to find parameters for each pipeline. The default of None indicates the SKOptTuner will be used.
        random_seed (int): Seed for the random number generator. Defaults to 0.
        pipeline_params (dict or None): Pipeline-level parameters that should be passed to the proposed pipelines. Defaults to None.
        custom_hyperparameters (dict or None): Custom hyperparameter ranges specified for pipelines to iterate over. Defaults to None.
        n_jobs (int or None): Non-negative integer describing level of parallelism used for pipelines. Defaults to -1.
        text_in_ensembling (boolean): If True and ensembling is True, then n_jobs will be set to 1 to avoid downstream sklearn stacking issues related to nltk. Defaults to False.
        top_n (int): top n number of pipelines to use for long mode.
        num_long_explore_pipelines (int): number of pipelines to explore for each top n pipeline at the start of long mode.
        num_long_pipelines_per_batch (int): number of pipelines per batch for each top n pipeline through long mode.
        allow_long_running_models (bool): Whether or not to allow longer-running models for large multiclass problems. If False and no pipelines, component graphs, or model families are provided,
            AutoMLSearch will not use Elastic Net or XGBoost when there are more than 75 multiclass targets and will not use CatBoost when there are more than 150 multiclass targets. Defaults to False.
        verbose (boolean): Whether or not to display logging information regarding pipeline building. Defaults to False.
    """

    def __init__(
        self,
        X,
        y,
        problem_type,
        sampler_name,
        tuner_class=None,
        random_seed=0,
        pipeline_params=None,
        custom_hyperparameters=None,
        n_jobs=-1,
        text_in_ensembling=False,
        top_n=3,
        num_long_explore_pipelines=50,
        num_long_pipelines_per_batch=10,
        allow_long_running_models=False,
        verbose=False,
    ):
        super().__init__(
            allowed_pipelines=[],
            custom_hyperparameters=custom_hyperparameters,
            tuner_class=None,
            random_seed=random_seed,
        )
        self.X = infer_feature_types(X)
        self.y = infer_feature_types(y)
        self.problem_type = problem_type
        self.sampler_name = sampler_name

        self.n_jobs = n_jobs
        self._best_pipeline_info = {}
        self.text_in_ensembling = text_in_ensembling
        self._pipeline_params = pipeline_params or {}
        self._custom_hyperparameters = custom_hyperparameters or {}
        self._top_n_pipelines = None
        self.num_long_explore_pipelines = num_long_explore_pipelines
        self.num_long_pipelines_per_batch = num_long_pipelines_per_batch
        self.top_n = top_n
        self.verbose = verbose
        self._selected_cat_cols = []
        self._split = False
        self.allow_long_running_models = allow_long_running_models
        self._X_with_cat_cols = None
        self._X_without_cat_cols = None
        self._ensembling = True if not is_time_series(self.problem_type) else False
        if verbose:
            self.logger = get_logger(f"{__name__}.verbose")
        else:
            self.logger = logging.getLogger(__name__)

        self._set_additional_pipeline_params()
        if custom_hyperparameters and not isinstance(custom_hyperparameters, dict):
            raise ValueError(
                f"If custom_hyperparameters provided, must be of type dict. Received {type(custom_hyperparameters)}"
            )

        for param_name_val in self._pipeline_params.values():
            for param_val in param_name_val.values():
                if isinstance(param_val, (Integer, Real, Categorical)):
                    raise ValueError(
                        "Pipeline parameters should not contain skopt.Space variables, please pass them "
                        "to custom_hyperparameters instead!"
                    )
        for hyperparam_name_val in self._custom_hyperparameters.values():
            for hyperparam_val in hyperparam_name_val.values():
                if not isinstance(hyperparam_val, (Integer, Real, Categorical)):
                    raise ValueError(
                        "Custom hyperparameters should only contain skopt.Space variables such as Categorical, Integer,"
                        " and Real!"
                    )

    @property
    def default_max_batches(self):
        """Returns the number of max batches AutoMLSearch should run by default."""
        return 4 if not is_time_series(self.problem_type) else 3

    def _naive_estimators(self):
        if is_regression(self.problem_type):
            naive_estimators = [
                "Elastic Net Regressor",
                "Random Forest Regressor",
            ]
        else:
            naive_estimators = [
                "Logistic Regression Classifier",
                "Random Forest Classifier",
            ]
        estimators = [
            handle_component_class(estimator) for estimator in naive_estimators
        ]
        return estimators

    def _create_tuner(self, pipeline):
        pipeline_hyperparameters = pipeline.get_hyperparameter_ranges(
            self._custom_hyperparameters
        )
        self._tuners[pipeline.name] = self._tuner_class(
            pipeline_hyperparameters, random_seed=self.random_seed
        )

    def _create_pipelines_with_params(self, pipelines, parameters={}):
        return [
            pipeline.new(
                parameters=self._transform_parameters(pipeline, parameters),
                random_seed=self.random_seed,
            )
            for pipeline in pipelines
        ]

    def _create_naive_pipelines(self, use_features=False):
        feature_selector = None

        if use_features:
            feature_selector = [
                (
                    RFRegressorSelectFromModel
                    if is_regression(self.problem_type)
                    else RFClassifierSelectFromModel
                )
            ]
        else:
            feature_selector = []

        estimators = self._naive_estimators()
        pipelines = [
            make_pipeline(
                X=self.X,
                y=self.y,
                estimator=estimator,
                problem_type=self.problem_type,
                sampler_name=self.sampler_name,
                extra_components_after=feature_selector,
                parameters=self._pipeline_params,
                known_in_advance=self._pipeline_params.get("pipeline", {}).get(
                    "known_in_advance", None
                ),
            )
            for estimator in estimators
        ]

        pipelines = self._create_pipelines_with_params(pipelines, parameters={})
        return pipelines

    def _find_component_names(self, original_name, pipeline):
        names = []
        for component in pipeline.component_graph.compute_order:
            split = component.split(" - ")
            split = split[1] if len(split) > 1 else split[0]
            if original_name == split:
                names.append(component)
        return names

    def _create_split_select_parameters(self):
        parameters = {
            "Categorical Pipeline - Select Columns Transformer": {
                "columns": self._selected_cat_cols
            },
            "Numeric Pipeline - Select Columns By Type Transformer": {
                "column_types": ["category"],
                "exclude": True,
            },
            "Numeric Pipeline - Select Columns Transformer": {
                "columns": self._selected_cols
            },
        }
        return parameters

    def _create_select_parameters(self):
        parameters = {}
        if self._selected_cols:
            parameters = {
                "Select Columns Transformer": {"columns": self._selected_cols}
            }
        elif self._selected_cat_cols:
            parameters = {
                "Select Columns Transformer": {"columns": self._selected_cat_cols}
            }

        if self._split:
            parameters = self._create_split_select_parameters()
        return parameters

    def _find_component_names_from_parameters(self, old_names, pipelines):
        new_names = {}
        for component_name in old_names:
            for pipeline in pipelines:
                new_name = self._find_component_names(component_name, pipeline)
                if new_name:
                    for name in new_name:
                        if name not in new_names:
                            new_names[name] = old_names[component_name]
        return new_names

    def _rename_pipeline_parameters_custom_hyperparameters(self, pipelines):
        names_to_value_pipeline_params = self._find_component_names_from_parameters(
            self._pipeline_params, pipelines
        )
        names_to_value_custom_hyperparameters = (
            self._find_component_names_from_parameters(
                self._custom_hyperparameters, pipelines
            )
        )
        self._pipeline_params.update(names_to_value_pipeline_params)
        self._custom_hyperparameters.update(names_to_value_custom_hyperparameters)

    def _create_fast_final(self):
        estimators = [
            estimator
            for estimator in get_estimators(self.problem_type)
            if estimator not in self._naive_estimators()
        ]
        estimators = self._filter_estimators(
            estimators,
            self.problem_type,
            self.allow_long_running_models,
            None,
            self.y.nunique(),
            self.logger,
        )
        pipelines = self._make_pipelines_helper(estimators)

        if self._split:
            self._rename_pipeline_parameters_custom_hyperparameters(pipelines)

        next_batch = []
        for pipeline in pipelines:
            parameters = self._create_select_parameters()
            pipeline = pipeline.new(
                parameters=self._transform_parameters(pipeline, parameters),
                random_seed=self.random_seed,
            )
            next_batch.append(pipeline)

        for pipeline in next_batch:
            self._create_tuner(pipeline)
        return next_batch

    def _create_n_pipelines(self, pipelines, n):
        next_batch = []
        for _ in range(n):
            for pipeline in pipelines:
                if pipeline.name not in self._tuners:
                    self._create_tuner(pipeline)

                select_parameters = self._create_select_parameters()
                proposed_parameters = self._tuners[pipeline.name].propose()
                parameters = self._transform_parameters(pipeline, proposed_parameters)
                parameters.update(select_parameters)
                next_batch.append(
                    pipeline.new(parameters=parameters, random_seed=self.random_seed)
                )
        return next_batch

    def _create_long_exploration(self, n):
        estimators = [
            (pipeline_dict["pipeline"].estimator, pipeline_dict["mean_cv_score"])
            for pipeline_dict in self._best_pipeline_info.values()
        ]
        estimators.sort(key=lambda x: x[1])
        estimators = estimators[:n]
        estimators = [estimator[0].__class__ for estimator in estimators]
        pipelines = self._make_pipelines_helper(estimators)
        self._top_n_pipelines = pipelines
        return self._create_n_pipelines(pipelines, self.num_long_explore_pipelines)

    def _make_pipelines_helper(self, estimators):
        pipelines = []
        if is_time_series(self.problem_type):
            pipelines = [
                make_pipeline(
                    X=self.X,
                    y=self.y,
                    estimator=estimator,
                    problem_type=self.problem_type,
                    sampler_name=self.sampler_name,
                    parameters=self._pipeline_params,
                    known_in_advance=self._pipeline_params.get("pipeline", {}).get(
                        "known_in_advance", None
                    ),
                )
                for estimator in estimators
            ]
        else:
            pipelines = [
                self._make_split_pipeline(estimator) for estimator in estimators
            ]
        return pipelines

    def next_batch(self):
        """Get the next batch of pipelines to evaluate.

        Returns:
            list(PipelineBase): a list of instances of PipelineBase subclasses, ready to be trained and evaluated.
        """
        if self._ensembling:
            if self._batch_number == 0:
                next_batch = self._create_naive_pipelines()
            elif self._batch_number == 1:
                next_batch = self._create_naive_pipelines(use_features=True)
            elif self._batch_number == 2:
                next_batch = self._create_fast_final()
            elif self.batch_number == 3:
                next_batch = self._create_ensemble()
            elif self.batch_number == 4:
                next_batch = self._create_long_exploration(n=self.top_n)
            elif self.batch_number % 2 != 0:
                next_batch = self._create_ensemble()
            else:
                next_batch = self._create_n_pipelines(
                    self._top_n_pipelines, self.num_long_pipelines_per_batch
                )
        else:
            if self._batch_number == 0:
                next_batch = self._create_naive_pipelines()
            elif self._batch_number == 1:
                next_batch = self._create_naive_pipelines(use_features=True)
            elif self._batch_number == 2:
                next_batch = self._create_fast_final()
            elif self.batch_number == 3:
                next_batch = self._create_long_exploration(n=self.top_n)
            else:
                next_batch = self._create_n_pipelines(
                    self._top_n_pipelines, self.num_long_pipelines_per_batch
                )

        self._pipeline_number += len(next_batch)
        self._batch_number += 1
        return next_batch

    def add_result(self, score_to_minimize, pipeline, trained_pipeline_results):
        """Register results from evaluating a pipeline. In batch number 2, the selected column names from the feature selector are taken to be used in a column selector. Information regarding the best pipeline is updated here as well.

        Args:
            score_to_minimize (float): The score obtained by this pipeline on the primary objective, converted so that lower values indicate better pipelines.
            pipeline (PipelineBase): The trained pipeline object which was used to compute the score.
            trained_pipeline_results (dict): Results from training a pipeline.
        """
        if pipeline.model_family != ModelFamily.ENSEMBLE:
            if self.batch_number >= 3:
                super().add_result(
                    score_to_minimize, pipeline, trained_pipeline_results
                )

        if (
            self.batch_number == 2
            and self._selected_cols is None
            and not is_time_series(self.problem_type)
        ):
            if is_regression(self.problem_type):
                self._selected_cols = pipeline.get_component(
                    "RF Regressor Select From Model"
                ).get_names()
            else:
                self._selected_cols = pipeline.get_component(
                    "RF Classifier Select From Model"
                ).get_names()

            if list(self.X.ww.select("categorical").columns):
                ohe = pipeline.get_component("One Hot Encoder")
                feature_provenance = ohe._get_feature_provenance()
                for original_col in feature_provenance:
                    selected = False
                    for encoded_col in feature_provenance[original_col]:
                        if encoded_col in self._selected_cols:
                            selected = True
                            self._selected_cols.remove(encoded_col)
                    if selected:
                        self._selected_cat_cols.append(original_col)

        current_best_score = self._best_pipeline_info.get(
            pipeline.model_family, {}
        ).get("mean_cv_score", np.inf)
        if (
            score_to_minimize is not None
            and score_to_minimize < current_best_score
            and pipeline.model_family != ModelFamily.ENSEMBLE
        ):
            self._best_pipeline_info.update(
                {
                    pipeline.model_family: {
                        "mean_cv_score": score_to_minimize,
                        "pipeline": pipeline,
                        "parameters": pipeline.parameters,
                        "id": trained_pipeline_results["id"],
                    }
                }
            )

    def _transform_parameters(self, pipeline, proposed_parameters):
        """Given a pipeline parameters dict, make sure pipeline_params, custom_hyperparameters, n_jobs are set properly."""
        parameters = {}
        if "pipeline" in self._pipeline_params:
            parameters["pipeline"] = self._pipeline_params["pipeline"]

        for (
            name,
            component_instance,
        ) in pipeline.component_graph.component_instances.items():
            component_class = type(component_instance)
            component_parameters = proposed_parameters.get(name, {})
            init_params = inspect.signature(component_class.__init__).parameters
            # For first batch, pass the pipeline params to the components that need them
            if name in self._custom_hyperparameters and self._batch_number <= 2:
                for param_name, value in self._custom_hyperparameters[name].items():
                    if isinstance(value, (Integer, Real)):
                        # get a random value in the space
                        component_parameters[param_name] = value.rvs(
                            random_state=self.random_seed
                        )[0]
                    # Categorical
                    else:
                        component_parameters[param_name] = value.rvs(
                            random_state=self.random_seed
                        )
            if name in self._pipeline_params:
                for param_name, value in self._pipeline_params[name].items():
                    component_parameters[param_name] = value
            # Inspects each component and adds the following parameters when needed
            if "n_jobs" in init_params:
                component_parameters["n_jobs"] = self.n_jobs
            names_to_check = [
                "Drop Columns Transformer",
                "Known In Advance Pipeline - Select Columns Transformer",
                "Not Known In Advance Pipeline - Select Columns Transformer",
            ]
            if (
                name in self._pipeline_params
                and name in names_to_check
                and self._batch_number > 0
            ):
                component_parameters["columns"] = self._pipeline_params[name]["columns"]
            if "pipeline" in self._pipeline_params:
                for param_name, value in self._pipeline_params["pipeline"].items():
                    if param_name in init_params:
                        component_parameters[param_name] = value
            parameters[name] = component_parameters
        return parameters

    def _make_split_pipeline(self, estimator, pipeline_name=None):
        if self._X_with_cat_cols is None or self._X_without_cat_cols is None:
            self._X_without_cat_cols = self.X.ww.drop(self._selected_cat_cols)
            self._X_with_cat_cols = self.X.ww[self._selected_cat_cols]

        if self._selected_cat_cols and self._selected_cols:
            self._split = True

            categorical_pipeline_parameters = {
                "Select Columns Transformer": {"columns": self._selected_cat_cols}
            }
            numeric_pipeline_parameters = {
                "Select Columns Transformer": {"columns": self._selected_cols},
                "Select Columns By Type Transformer": {
                    "column_types": ["category"],
                    "exclude": True,
                },
            }

            categorical_pipeline = make_pipeline(
                self._X_with_cat_cols,
                self.y,
                estimator,
                self.problem_type,
                sampler_name=self.sampler_name,
                parameters=categorical_pipeline_parameters,
                extra_components_before=[SelectColumns],
                use_estimator=False,
            )

            numeric_pipeline = make_pipeline(
                self._X_without_cat_cols,
                self.y,
                estimator,
                self.problem_type,
                sampler_name=self.sampler_name,
                parameters=numeric_pipeline_parameters,
                extra_components_before=[SelectByType],
                extra_components_after=[SelectColumns],
                use_estimator=False,
            )

            input_pipelines = [numeric_pipeline, categorical_pipeline]
            sub_pipeline_names = {
                numeric_pipeline.name: "Numeric",
                categorical_pipeline.name: "Categorical",
            }
            return _make_pipeline_from_multiple_graphs(
                input_pipelines,
                estimator,
                self.problem_type,
                pipeline_name=pipeline_name,
                random_seed=self.random_seed,
                sub_pipeline_names=sub_pipeline_names,
            )
        elif self._selected_cat_cols and not self._selected_cols:
            categorical_pipeline_parameters = {
                "Select Columns Transformer": {"columns": self._selected_cat_cols}
            }
            categorical_pipeline = make_pipeline(
                self._X_with_cat_cols,
                self.y,
                estimator,
                self.problem_type,
                sampler_name=self.sampler_name,
                parameters=categorical_pipeline_parameters,
                extra_components_before=[SelectColumns],
            )
            return categorical_pipeline
        else:
            numeric_pipeline_parameters = {
                "Select Columns Transformer": {"columns": self._selected_cols},
            }
            numeric_pipeline = make_pipeline(
                self.X,
                self.y,
                estimator,
                self.problem_type,
                sampler_name=self.sampler_name,
                parameters=numeric_pipeline_parameters,
                extra_components_after=[SelectColumns],
            )
            return numeric_pipeline
