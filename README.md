# SchoolParser

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Intended Users / Usage

schoolparser team.

     
# Installation Guide
It relies on the following libraries to work:

```
pandas = "*"
joblib = "*"
requests = "*"
requests-html = "*"
bs4 = "*"
colorama = "*"
stem = "*"
selenium = "*"
xlrd = "*"
socials = "*"
tqdm = "*"
openpyxl = "*"
email-validator = "*"
```

Optionally

```
    matplotlib
    seaborn
```

Setup environment from pipenv

```
pipenv install
```

For dev packages

```
pipenv install --dev
```

Then install schoolparser

```
pipenv install -e .
```

## From Conda

    conda env create -f ./environment.yml --name=schoolparser
    
Setup environment via Conda:

    conda create -n schoolparser
    source activate schoolparser
    conda config --add channels conda-forge
    conda install numpy pandas scipy joblib natsort xlrd deprecated tqdm requests  # for basic analysis
    conda install matplotlib seaborn  # for visualization
