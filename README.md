<p align="center">
<img width=50% src="https://rayml-web-images.s3.amazonaws.com/rayml_horizontal.svg" alt="rayml" />
</p>

<p align="center">
    <a href="https://github.com/alteryx/woodwork/actions?query=branch%3Amain+workflow%3ATests" target="_blank">
        <img src="https://github.com/alteryx/woodwork/workflows/Tests/badge.svg?branch=main" alt="Tests" />
    </a>
    <a href="https://codecov.io/gh/alteryx/rayml">
        <img src="https://codecov.io/gh/alteryx/rayml/branch/main/graph/badge.svg?token=JDc0Ib7kYL"/>
    </a>
    <a href="https://rayml.alteryx.com/en/latest/?badge=stable" target="_blank">
        <img src="https://readthedocs.com/projects/feature-labs-inc-rayml/badge/?version=stable" alt="Documentation Status" />
    </a>
    <a href="https://badge.fury.io/py/rayml" target="_blank">
        <img src="https://badge.fury.io/py/rayml.svg?maxAge=2592000" alt="PyPI Version" />
    </a>
    <a href="https://anaconda.org/conda-forge/rayml" target="_blank">
        <img src="https://anaconda.org/conda-forge/rayml/badges/version.svg" alt="Anaconda Version" />
    </a>
    <a href="https://pepy.tech/project/rayml" target="_blank">
        <img src="https://pepy.tech/badge/rayml/month" alt="PyPI Downloads" />
    </a>
</p>
<hr>

rayml is an AutoML library which builds, optimizes, and evaluates machine learning pipelines using domain-specific objective functions.

**Key Functionality**

* **Automation** - Makes machine learning easier. Avoid training and tuning models by hand. Includes data quality checks, cross-validation and more.
* **Data Checks** - Catches and warns of problems with your data and problem setup before modeling.
* **End-to-end** - Constructs and optimizes pipelines that include state-of-the-art preprocessing, feature engineering, feature selection, and a variety of modeling techniques.
* **Model Understanding** - Provides tools to understand and introspect on models, to learn how they'll behave in your problem domain.
* **Domain-specific** - Includes repository of domain-specific objective functions and an interface to define your own.

## Installation 

Install from [PyPI](https://pypi.org/project/rayml/):

```bash
pip install rayml
```

or from the conda-forge channel on [conda](https://anaconda.org/conda-forge/rayml):

```bash
conda install -c conda-forge rayml
```

### Add-ons
**Update checker** - Receive automatic notifications of new Woodwork releases

PyPI:

```bash
pip install "rayml[update_checker]"
```
Conda:
```
conda install -c conda-forge alteryx-open-src-update-checker
```

## Start

#### Load and split example data 
```python
import rayml
X, y = rayml.demos.load_breast_cancer()
X_train, X_test, y_train, y_test = rayml.preprocessing.split_data(X, y, problem_type='binary')
```

#### Run AutoML
```python
from rayml.automl import AutoMLSearch
automl = AutoMLSearch(X_train=X_train, y_train=y_train, problem_type='binary')
automl.search()
```

#### View pipeline rankings
```python
automl.rankings
```

#### Get best pipeline and predict on new data
```python
pipeline = automl.best_pipeline
pipeline.predict(X_test)
```

## Next Steps

Read more about rayml on our [documentation page](https://rayml.alteryx.com/):

* [Installation](https://rayml.alteryx.com/en/stable/install.html) and [getting started](https://rayml.alteryx.com/en/stable/start.html).
* [Tutorials](https://rayml.alteryx.com/en/stable/tutorials.html) on how to use rayml.
* [User guide](https://rayml.alteryx.com/en/stable/user_guide.html) which describes rayml's features.
* Full [API reference](https://rayml.alteryx.com/en/stable/api_reference.html)

## Support

The rayml community is happy to provide support to users of rayml. Project support can be found in four places depending on the type of question:
1. For usage questions, use [Stack Overflow](https://stackoverflow.com/questions/tagged/rayml) with the `rayml` tag.
2. For bugs, issues, or feature requests start a [Github issue](https://github.com/alteryx/rayml/issues).
3. For discussion regarding development on the core library, use [Slack](https://join.slack.com/t/featuretools/shared_invite/enQtNTEwODEzOTEwMjg4LTQ1MjZlOWFmZDk2YzAwMjEzNTkwZTZkN2NmOGFjOGI4YzE5OGMyMGM5NGIxNTE4NjkzYWI3OWEwZjkyZGExYmQ).
4. For everything else, the core developers can be reached by email at open_source_support@alteryx.com

## Built at Alteryx Innovation Labs

**rayml** is an open source project built by [Alteryx](https://www.alteryx.com). To see the other open source projects we’re working on visit [Alteryx Open Source](https://www.alteryx.com/open-source). If building impactful data science pipelines is important to you or your business, please get in touch.

<a href="https://www.alteryx.com/innovation-labs">
    <img src="https://rayml-web-images.s3.amazonaws.com/alteryx_innovation_labs.png" alt="Alteryx Innovation Labs" />
</a>
