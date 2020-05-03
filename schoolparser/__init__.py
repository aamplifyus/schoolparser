"""EZTrack software for easily generating fragility heatmaps of EEG data."""
import glob
import warnings
from os.path import dirname, basename, isfile

from .base.config import config as config

# base functions
from .base.config.config import *
from .base.metrics import metrics as metrics

# import fragility
from .fragility import linearsystem, mvarmodel, perturbationmodel

# import pipeline
from .pipeline.analysis.execute import runfrag, runmerge
from .pipeline.preprocess import run_bids_conversion

# import preprocess
from .preprocess.preprocess_eeg import preprocess_eeg
from .preprocess.preprocess_ieeg import preprocess_ieeg

# ignore future, deprecation and user warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=PendingDeprecationWarning)
warnings.simplefilter(action="ignore", category=UserWarning)

modules = glob.glob(dirname(__file__) + "/*.py")
__all__ = [
    basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")
]
name = "eztrack"
__version__ = "0.1.0"
