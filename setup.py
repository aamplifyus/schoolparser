import os
import sys
from distutils.core import setup

from setuptools import find_packages

"""
To re-setup: 

    python setup.py sdist bdist_wheel

    pip install -r requirements.txt --process-dependency-links

To test on test pypi:
    
    twine upload --repository testpypi dist/*
    
    # test upload
    pip install -i https://test.pypi.org/simple/ --no-deps schoolparser

    twine upload dist/* 
"""

PACKAGE_NAME = "schoolparser"
with open(os.path.join("schoolparser", "__init__.py"), "r") as fid:
    for line in (line.strip() for line in fid):
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip("'").strip('"')
            break
if version is None:
    raise RuntimeError("Could not determine version")
DESCRIPTION = "A web-scraper to get raw emails and social media handles from web urls."
URL = "https://github.com/adam2392/schoolparser/"
MINIMUM_PYTHON_VERSION = 3, 6  # Minimum of Python 3.6
REQUIRED_PACKAGES = [
    "numpy>=1.14.5",
    "scipy>=1.1.0",
    "pandas>=0.23.4",
    "joblib>=0.14",
    "requests",
    "requests-html",
    "bs4",
    "colorama",
    "stem",
    "selenium",
    "natsort",
    "tqdm",
    "xlrd",
    "click_help_colors",
]
CLASSIFICATION_OF_PACKAGE = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    "Development Status :: 3 - Alpha",
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation",
    "Natural Language :: English",
]
AUTHORS = [
    "Adam Li",
]


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {}.{}+ is required.".format(*MINIMUM_PYTHON_VERSION))


check_python_version()

setup(
    name=PACKAGE_NAME,
    version=version,
    description=DESCRIPTION,
    author=AUTHORS,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url=URL,
    license="GNU General Public License (GPL)",
    packages=find_packages(exclude=["tests"]),
    project_urls={
        "Documentation": "https://github.com/adam2392/schoolparser/docs/",
        "Source": URL,
        "Tracker": "https://github.com/adam2392/schoolparser/issues",
    },
    install_requires=REQUIRED_PACKAGES,
    include_package_data=True,
    classifiers=CLASSIFICATION_OF_PACKAGE,
)
