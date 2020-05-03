import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

from click_help_colors import HelpColorsCommand

import mne


"""
Store all hardcoded configuration settings for now.

"""
curDir = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.normpath(os.path.join(curDir, "../../../data/"))


def _get_sourcedata_path():
    return Path(os.getenv("EZTRACK_SOURCE_DIR", os.path.join(DATADIR, "sourcedata")))


def _get_bidsroot_path():
    return Path(os.getenv("BIDSROOT", os.path.join(DATADIR, "bids_layout")))


def _get_derivatives_path():
    return Path(
        os.getenv(
            "EZTRACK_DERIVATIVES_DIR", os.path.join(_get_bidsroot_path(), "derivatives")
        )
    )


def _get_home_path():
    return Path(os.getenv("HOME"), EZTRACK_HOME)


EZTRACK_HOME = os.path.normpath(os.path.join(curDir, "../.."))
LOGDIR = Path(_get_home_path() / ".eztrack" / "logs")

os.makedirs(LOGDIR, exist_ok=True)

# clin_categorization = "\nClinical Categorization: \n\t 1. Lesional \n\t 2.Focal Temporal \n\t 3. Focal Non-temporal \n\t 4. Multi-focal"
# race_categorization = (
#     "\nRace: \n\t 0. Caucasian \n\t 1. African American \n\t 2. Hispanic \n\t 3. Asian"
# )
# CLINICAL_CATEGORIES = "Categories:" + clin_categorization + race_categorization

DEFAULT_TASK = "monitor"
DEFAULT_SESSION = "seizure"
DEFAULT_ACQUISITION = "ecog"
LOG_LEVEL = logging.INFO

# initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.handlers = []

# add file print_handler
msg_format = (
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)
formatter = logging.Formatter(msg_format)
logname = os.path.join(LOGDIR, "eztrack.log")
file_handler = RotatingFileHandler(logname, maxBytes=200000, backupCount=10)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# set logging level for submodules: mne, mne-bids
mne.set_log_level(LOG_LEVEL)
mne.set_log_file(logname, msg_format, overwrite=False)

# add stream print_handler to stdout
# print_handler = logging.StreamHandler(sys.stdout)
# print_handler.setLevel(logging.DEBUG)
# logger.addHandler(print_handler)

logger.propagate = False


# Help message settings
help_colors = {
    "cls": HelpColorsCommand,
    "help_headers_color": "yellow",
    "help_options_color": "green",
}
