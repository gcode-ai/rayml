from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_require = {
    'update_checker': ['alteryx-open-src-update-checker >= 2.0.0'],
    'prophet': ['cmdstan-builder == 0.0.8']
}
extras_require['complete'] = sorted(set(sum(extras_require.values(), [])))

setup(
    name='rayml',
    version='0.45.0',
    author='GCODE.ai',
    author_email='mike@gcode.ai',
    description='RayML is based on rayml and modified to integrate ray, which builds, optimizes, and evaluates machine learning pipelines using domain-specific objective functions.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/gcode-ai/rayml/',
    python_requires='>=3.8, <4',
    install_requires=open('core-requirements.txt').readlines() + open('requirements.txt').readlines()[1:],
    extras_require=extras_require,
    tests_require=open('test-requirements.txt').readlines(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'rayml = rayml.__main__:cli'
        ]
    },
    data_files=[('rayml/tests/data', ['rayml/tests/data/churn.csv',
                                       'rayml/tests/data/daily-min-temperatures.csv',
                                       'rayml/tests/data/fraud_transactions.csv.gz',
                                       'rayml/tests/data/tips.csv',
                                       'rayml/tests/data/titanic.csv'])],
)
