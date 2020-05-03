from setuptools import setup, find_packages

setup(
    name="CLI_EZT",
    version="1.0",
    packages=find_packages(),
    py_modules=["ez"],
    install_requires=[
        "numpy>=1.14.5",  # basic packages
        "scipy>=1.1.0",
        "scikit-learn>=0.19.2",
        "pandas>=0.23.4",
        "joblib>=0.14",
        "natsort",
        "tqdm",
        "xlrd",
        "mne>=0.20.0",  # (i)EEG-processing
        "autoreject",
        "mne-bids>=0.4",
        "pybids>=0.10",
        "pybv>=0.2.0",
        "bids_validator",
        "click",  # click related
        "click-log",
        "click_help_colors",
        "deprecated",
        "sqlalchemy",
        "matplotlib>=3.2.1",  # plotting
        "seaborn",
    ],
    entry_points={"console_scripts": ["ez = eztrack.cli.ez:entry"]},
)
