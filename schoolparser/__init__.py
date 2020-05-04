"""EZTrack software for easily generating fragility heatmaps of EEG data."""
import glob
import warnings
from os.path import dirname, basename, isfile

# ignore future, deprecation and user warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=PendingDeprecationWarning)
warnings.simplefilter(action="ignore", category=UserWarning)

modules = glob.glob(dirname(__file__) + "/*.py")
__all__ = [
    basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")
]
name = "schoolparser"
__version__ = "0.1.0"
