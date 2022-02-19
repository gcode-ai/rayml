"""rayml."""
import warnings

# hack to prevent warnings from skopt
# must import sklearn first
import sklearn
import rayml.demos
import rayml.model_family
import rayml.model_understanding
import rayml.objectives
import rayml.pipelines
import rayml.preprocessing
import rayml.problem_types
import rayml.utils
import rayml.data_checks
from rayml.automl import AutoMLSearch, search_iterative, search
from rayml.utils import print_info, update_checker

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    warnings.simplefilter("ignore", DeprecationWarning)
    import skopt
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

__version__ = "0.45.0"
