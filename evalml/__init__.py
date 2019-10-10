# flake8:noqa

import warnings

# hack to prevent warnings from skopt
# must import sklearn first
import sklearn

import evalml.demos
import evalml.objectives
import evalml.pipelines
# import evalml.models
import evalml.preprocessing
import evalml.problem_types
import evalml.tuners
import evalml.pipelines
import evalml.model_types
import evalml.utils

from evalml.pipelines import list_model_types, save_pipeline, load_pipeline
from evalml.models import AutoClassifier, AutoRegressor
from evalml.pipelines import list_model_types, load_pipeline, save_pipeline

warnings.filterwarnings("ignore", category=DeprecationWarning)


__version__ = '0.4.1'
