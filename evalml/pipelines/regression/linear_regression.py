from evalml.pipelines import PipelineBase


class LinearRegressionPipeline(PipelineBase):
    """Linear Regression Pipeline for regression problems"""
    name = "Linear Regressor w/ Simple Imputer + One Hot Encoder + Standard Scaler"
    component_graph = ['Simple Imputer', 'One Hot Encoder', 'Standard Scaler', 'Linear Regressor']
    problem_types = ['regression']

    hyperparameters = {
        'impute_strategy': ['most_frequent', 'mean', 'median'],
        'normalize': [False, True],
        'fit_intercept': [False, True]
    }
