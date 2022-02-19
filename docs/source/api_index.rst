=============
API Reference
=============


Demo Datasets
=============

.. autoapisummary::
    :nosignatures:

    rayml.demos.load_breast_cancer
    rayml.demos.load_diabetes
    rayml.demos.load_fraud
    rayml.demos.load_wine
    rayml.demos.load_churn


Preprocessing
=============

Utilities to preprocess data before using rayml.

.. autoapisummary::
    :nosignatures:

    rayml.preprocessing.load_data
    rayml.preprocessing.target_distribution
    rayml.preprocessing.number_of_features
    rayml.preprocessing.split_data


Exceptions
=============

.. autoapisummary::

    rayml.exceptions.MethodPropertyNotFoundError
    rayml.exceptions.PipelineNotFoundError
    rayml.exceptions.ObjectiveNotFoundError
    rayml.exceptions.MissingComponentError
    rayml.exceptions.ComponentNotYetFittedError
    rayml.exceptions.PipelineNotYetFittedError
    rayml.exceptions.AutoMLSearchException
    rayml.exceptions.PipelineScoreError
    rayml.exceptions.DataCheckInitError
    rayml.exceptions.NullsInColumnWarning


AutoML
======

AutoML Search Interface
~~~~~~~~~~~~~~~~~~~~~~~
.. autoapisummary::

    rayml.automl.AutoMLSearch


AutoML Utils
~~~~~~~~~~~~
.. autoapisummary::
    :nosignatures:

    rayml.automl.search
    rayml.automl.get_default_primary_search_objective
    rayml.automl.make_data_splitter


AutoML Algorithm Classes
~~~~~~~~~~~~~~~~~~~~~~~~
.. autoapisummary::

    rayml.automl.automl_algorithm.AutoMLAlgorithm
    rayml.automl.automl_algorithm.IterativeAlgorithm


AutoML Callbacks
~~~~~~~~~~~~~~~~~~~~~~~~
.. autoapisummary::
    :nosignatures:

    rayml.automl.callbacks.silent_error_callback
    rayml.automl.callbacks.log_error_callback
    rayml.automl.callbacks.raise_error_callback


AutoML Engines
~~~~~~~~~~~~~~
.. autoapisummary::

    rayml.automl.engine.sequential_engine.SequentialEngine
    rayml.automl.engine.cf_engine.CFEngine
    rayml.automl.engine.dask_engine.DaskEngine

Pipelines
=========

Pipeline Base Classes
~~~~~~~~~~~~~~~~~~~~~
.. autoapisummary::

    rayml.pipelines.PipelineBase
    rayml.pipelines.classification_pipeline.ClassificationPipeline
    rayml.pipelines.binary_classification_pipeline.BinaryClassificationPipeline
    rayml.pipelines.MulticlassClassificationPipeline
    rayml.pipelines.RegressionPipeline
    rayml.pipelines.TimeSeriesClassificationPipeline
    rayml.pipelines.TimeSeriesBinaryClassificationPipeline
    rayml.pipelines.TimeSeriesMulticlassClassificationPipeline
    rayml.pipelines.TimeSeriesRegressionPipeline


Pipeline Utils
~~~~~~~~~~~~~~
.. autoapisummary::
    :nosignatures:

    rayml.pipelines.utils.make_pipeline
    rayml.pipelines.utils.generate_pipeline_code
    rayml.pipelines.utils.rows_of_interest



Component Graphs
================

.. autoapisummary::

    rayml.pipelines.ComponentGraph


Components
==========

Component Base Classes
~~~~~~~~~~~~~~~~~~~~~~
Components represent a step in a pipeline.

.. autoapisummary::

    rayml.pipelines.components.ComponentBase
    rayml.pipelines.Transformer
    rayml.pipelines.Estimator


Component Utils
~~~~~~~~~~~~~~~
.. autoapisummary::
    :nosignatures:

    rayml.pipelines.components.utils.allowed_model_families
    rayml.pipelines.components.utils.get_estimators
    rayml.pipelines.components.utils.generate_component_code


Transformers
~~~~~~~~~~~~
Transformers are components that take in data as input and output transformed data.

.. autoapisummary::

    rayml.pipelines.components.DropColumns
    rayml.pipelines.components.SelectColumns
    rayml.pipelines.components.SelectByType
    rayml.pipelines.components.OneHotEncoder
    rayml.pipelines.components.TargetEncoder
    rayml.pipelines.components.PerColumnImputer
    rayml.pipelines.components.Imputer
    rayml.pipelines.components.SimpleImputer
    rayml.pipelines.components.StandardScaler
    rayml.pipelines.components.RFRegressorSelectFromModel
    rayml.pipelines.components.RFClassifierSelectFromModel
    rayml.pipelines.components.DropNullColumns
    rayml.pipelines.components.DateTimeFeaturizer
    rayml.pipelines.components.NaturalLanguageFeaturizer
    rayml.pipelines.components.TimeSeriesFeaturizer
    rayml.pipelines.components.DFSTransformer
    rayml.pipelines.components.PolynomialDetrender
    rayml.pipelines.components.Undersampler
    rayml.pipelines.components.Oversampler


Estimators
~~~~~~~~~~

Classifiers
-----------

Classifiers are components that output a predicted class label.

.. autoapisummary::

    rayml.pipelines.components.CatBoostClassifier
    rayml.pipelines.components.ElasticNetClassifier
    rayml.pipelines.components.ExtraTreesClassifier
    rayml.pipelines.components.RandomForestClassifier
    rayml.pipelines.components.LightGBMClassifier
    rayml.pipelines.components.LogisticRegressionClassifier
    rayml.pipelines.components.XGBoostClassifier
    rayml.pipelines.components.BaselineClassifier
    rayml.pipelines.components.StackedEnsembleClassifier
    rayml.pipelines.components.DecisionTreeClassifier
    rayml.pipelines.components.KNeighborsClassifier
    rayml.pipelines.components.SVMClassifier
    rayml.pipelines.components.VowpalWabbitBinaryClassifier
    rayml.pipelines.components.VowpalWabbitMulticlassClassifier


Regressors
-----------

Regressors are components that output a predicted target value.

.. autoapisummary::

    rayml.pipelines.components.ARIMARegressor
    rayml.pipelines.components.CatBoostRegressor
    rayml.pipelines.components.ElasticNetRegressor
    rayml.pipelines.components.ExponentialSmoothingRegressor
    rayml.pipelines.components.LinearRegressor
    rayml.pipelines.components.ExtraTreesRegressor
    rayml.pipelines.components.RandomForestRegressor
    rayml.pipelines.components.XGBoostRegressor
    rayml.pipelines.components.BaselineRegressor
    rayml.pipelines.components.TimeSeriesBaselineEstimator
    rayml.pipelines.components.StackedEnsembleRegressor
    rayml.pipelines.components.DecisionTreeRegressor
    rayml.pipelines.components.LightGBMRegressor
    rayml.pipelines.components.SVMRegressor
    rayml.pipelines.components.VowpalWabbitRegressor


Model Understanding
===================

Utility Methods
~~~~~~~~~~~~~~~
.. autoapisummary::
    :nosignatures:

    rayml.model_understanding.confusion_matrix
    rayml.model_understanding.normalize_confusion_matrix
    rayml.model_understanding.precision_recall_curve
    rayml.model_understanding.roc_curve
    rayml.model_understanding.calculate_permutation_importance
    rayml.model_understanding.calculate_permutation_importance_one_column
    rayml.model_understanding.binary_objective_vs_threshold
    rayml.model_understanding.get_prediction_vs_actual_over_time_data
    rayml.model_understanding.partial_dependence
    rayml.model_understanding.get_prediction_vs_actual_data
    rayml.model_understanding.get_linear_coefficients
    rayml.model_understanding.t_sne
    rayml.model_understanding.find_confusion_matrix_per_thresholds


Graph Utility Methods
~~~~~~~~~~~~~~~~~~~~~~~
.. autoapisummary::
    :nosignatures:

    rayml.model_understanding.graph_precision_recall_curve
    rayml.model_understanding.graph_roc_curve
    rayml.model_understanding.graph_confusion_matrix
    rayml.model_understanding.graph_permutation_importance
    rayml.model_understanding.graph_binary_objective_vs_threshold
    rayml.model_understanding.graph_prediction_vs_actual
    rayml.model_understanding.graph_prediction_vs_actual_over_time
    rayml.model_understanding.graph_partial_dependence
    rayml.model_understanding.graph_t_sne


Prediction Explanations
~~~~~~~~~~~~~~~~~~~~~~~

.. autoapisummary::
    :nosignatures:

    rayml.model_understanding.explain_predictions
    rayml.model_understanding.explain_predictions_best_worst


Objectives
====================

Objective Base Classes
~~~~~~~~~~~~~~~~~~~~~~

.. autoapisummary::

    rayml.objectives.ObjectiveBase
    rayml.objectives.BinaryClassificationObjective
    rayml.objectives.MulticlassClassificationObjective
    rayml.objectives.RegressionObjective


Domain-Specific Objectives
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapisummary::

    rayml.objectives.FraudCost
    rayml.objectives.LeadScoring
    rayml.objectives.CostBenefitMatrix


Classification Objectives
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapisummary::

    rayml.objectives.AccuracyBinary
    rayml.objectives.AccuracyMulticlass
    rayml.objectives.AUC
    rayml.objectives.AUCMacro
    rayml.objectives.AUCMicro
    rayml.objectives.AUCWeighted
    rayml.objectives.Gini
    rayml.objectives.BalancedAccuracyBinary
    rayml.objectives.BalancedAccuracyMulticlass
    rayml.objectives.F1
    rayml.objectives.F1Micro
    rayml.objectives.F1Macro
    rayml.objectives.F1Weighted
    rayml.objectives.LogLossBinary
    rayml.objectives.LogLossMulticlass
    rayml.objectives.MCCBinary
    rayml.objectives.MCCMulticlass
    rayml.objectives.Precision
    rayml.objectives.PrecisionMicro
    rayml.objectives.PrecisionMacro
    rayml.objectives.PrecisionWeighted
    rayml.objectives.Recall
    rayml.objectives.RecallMicro
    rayml.objectives.RecallMacro
    rayml.objectives.RecallWeighted


Regression Objectives
~~~~~~~~~~~~~~~~~~~~~

.. autoapisummary::

    rayml.objectives.R2
    rayml.objectives.MAE
    rayml.objectives.MAPE
    rayml.objectives.MSE
    rayml.objectives.MeanSquaredLogError
    rayml.objectives.MedianAE
    rayml.objectives.MaxError
    rayml.objectives.ExpVariance
    rayml.objectives.RootMeanSquaredError
    rayml.objectives.RootMeanSquaredLogError


Objective Utils
~~~~~~~~~~~~~~~~~~~~~

.. autoapisummary::
    :nosignatures:

    rayml.objectives.get_all_objective_names
    rayml.objectives.get_core_objectives
    rayml.objectives.get_core_objective_names
    rayml.objectives.get_non_core_objectives
    rayml.objectives.get_objective


Problem Types
=============

.. autoapisummary::
    :nosignatures:

    rayml.problem_types.handle_problem_types
    rayml.problem_types.detect_problem_type
    rayml.problem_types.ProblemTypes


Model Family
============

.. autoapisummary::
    :nosignatures:

    rayml.model_family.handle_model_family
    rayml.model_family.ModelFamily


Tuners
======

.. autoapisummary::

    rayml.tuners.Tuner
    rayml.tuners.SKOptTuner
    rayml.tuners.GridSearchTuner
    rayml.tuners.RandomSearchTuner


Data Checks
===========

Data Check Classes
~~~~~~~~~~~~~~~~~~
.. autoapisummary::

    rayml.data_checks.DataCheck
    rayml.data_checks.InvalidTargetDataCheck
    rayml.data_checks.NullDataCheck
    rayml.data_checks.IDColumnsDataCheck
    rayml.data_checks.TargetLeakageDataCheck
    rayml.data_checks.OutliersDataCheck
    rayml.data_checks.NoVarianceDataCheck
    rayml.data_checks.ClassImbalanceDataCheck
    rayml.data_checks.MulticollinearityDataCheck
    rayml.data_checks.DateTimeFormatDataCheck
    rayml.data_checks.TimeSeriesParametersDataCheck
    rayml.data_checks.TimeSeriesSplittingDataCheck

    rayml.data_checks.DataChecks
    rayml.data_checks.DefaultDataChecks


Data Check Messages
~~~~~~~~~~~~~~~~~~~
.. autoapisummary::

    rayml.data_checks.DataCheckMessage
    rayml.data_checks.DataCheckError
    rayml.data_checks.DataCheckWarning


Data Check Message Types
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapisummary::

    rayml.data_checks.DataCheckMessageType

Data Check Message Codes
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoapisummary::

    rayml.data_checks.DataCheckMessageCode


Utils
=====

General Utils
~~~~~~~~~~~~~

.. autoapisummary::
    :nosignatures:

    rayml.utils.import_or_raise
    rayml.utils.convert_to_seconds
    rayml.utils.get_random_state
    rayml.utils.get_random_seed
    rayml.utils.pad_with_nans
    rayml.utils.drop_rows_with_nans
    rayml.utils.infer_feature_types
    rayml.utils.save_plot
    rayml.utils.is_all_numeric
    rayml.utils.get_importable_subclasses


.. toctree::
    :hidden:

    autoapi/rayml/index