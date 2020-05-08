# SchoolParser
Master repo with schoolparser.

[![CircleCI](https://circleci.com/gh/aamplifyus/schoolparser.svg?style=svg&circle-token=be3280d393039eac5067ac529b59241a235a2d4d)](https://circleci.com/gh/aamplifyus/schoolparser)
[![Build status](https://ci.appveyor.com/api/projects/status/phmhj02jo47c0f9o/branch/master?svg=true)](https://ci.appveyor.com/project/aamplifyus/schoolparser/branch/master)
[![Build Status](https://travis-ci.com/aamplifyus/schoolparser.svg?token=6sshyCajdyLy6EhT8YAq&branch=master)](https://travis-ci.com/aamplifyus/schoolparser)
[![Coverage Status](./coverage.svg)](./coverage.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Intended Users / Usage

schoolparser team.

     
# Installation Guide
schoolparser is intended to be a lightweight wrapper for easily analyzing large batches of patients with EEG data. eegio relies on the following libraries to work:

    numpy
    scipy
    scikit-learn
    pandas
    joblib
    requests
    requests-html bs4 colorama stem selenium
    xlrd
    openpyxl
    matplotlib
    seaborn
    
Setup environment from source

    make inplace

Setup environment directly via recipe:

Note that our repository currently depends a bit on MNE-Python and MNE-BIDS development versions, which isn't maintained in the 
conda recipe file. 

    conda env create -f ./environment.yml --name=schoolparser
    
Setup environment via Conda:

    conda create -n schoolparser
    source activate schoolparser
    conda config --add channels conda-forge
    conda install numpy pandas scipy scikit-learn joblib natsort xlrd deprecated tqdm requests  # for basic analysis
    conda install matplotlib seaborn  # for visualization
    
To install CLI:
    
    conda install click
    make install-cli
     
## Install from Github
To install, run this command in your repo:

    git clone https://github.com/aamplifyus/schoolparser
    python setup.py install

or 

    pip install https://api.github.com/repos/aamplifyus/schoolparser/zipball/master

# Documentation

    conda install sphinx sphinx-gallery sphinx_bootstrap_theme numpydoc 
    sphinx-quickstart
    make build_doc
    
# Setup Jupyter Kernel To Test
You need to install ipykernel to expose your conda environment to jupyter notebooks.
   
    conda install ipykernel
    python -m ipykernel install --name schoolparser --user
    # now you can run jupyter lab and select a kernel
    jupyter lab 

# Testing
Install testing and formatting libs:

    conda install black pytest pytest-cov coverage codespell pydocstyle
    pip install coverage-badge anybadge
    
Run tests

    black schoolparser/*
    black tests/*
    pylint ./schoolparser/
    anybadge --value=6.0 --file=pylint.svg pylint
    pytest --cov-config=.coveragerc --cov=./schoolparser/ tests/
    pytest --cov-config=.coveragerc --cov=./schoolparser/ tests/ > docs/tests/test_docs.txt
    coverage-badge -f -o coverage.svg
    