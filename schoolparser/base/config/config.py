# coding=utf-8

import logging
import os
from datetime import datetime
from enum import Enum
from logging.handlers import RotatingFileHandler

import eztrack

EZTrack_log_name = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../..", "logs", "eztrack.log"
    )
)

EZTrack_metric_log_name = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../..",
        "logs",
        "eztrack_metric.log",
    )
)

logger = logging.getLogger(__name__)

# set logging level
logger.setLevel(logging.DEBUG)

# add file handler
file_handler = RotatingFileHandler(EZTrack_log_name, maxBytes=200000, backupCount=10)
formatter = logging.Formatter(
    "%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# set logging configuration for mne
logging.getLogger("mne").setLevel(logging.ERROR)
logging.getLogger("mne").handlers = []  # set mne handlers to none
logging.getLogger("mne").addHandler(file_handler)  # redirect mne logs to file
logging.getLogger("mne").propagate = False

logger.propagate = True

# base file dir name for eztrack
OUTBASENAME = "eztrack_logs"


class CHANNEL_MARKERS(Enum):
    # non-eeg markers
    NON_EEG_MARKERS = [
        "DC",
        "EKG",
        "REF",
        "EMG",
        "ECG",
        "EVENT",
        "MARK",
        "STI014",
        "STIM",
        "STI",
        "RFC",
    ]
    # bad marker channel names
    BAD_MARKERS = ["$", "FZ", "GZ", "DC", "STI"]


class ClinicalContactColumns(Enum):
    """Clinical excel sheet columns to support regular exp expansion."""

    BAD_CONTACTS = "BAD_CONTACTS"
    WM_CONTACTS = "WM_CONTACTS"
    OUT_CONTACTS = "OUT_CONTACTS"
    SOZ_CONTACTS = "SOZ_CONTACTS"


class ClinicalColumnns(Enum):
    """Clinical excel sheet columns to be used."""

    CURRENT_AGE = "SURGERY_AGE"
    ONSET_AGE = "ONSET_AGE"
    ENGEL_SCORE = "ENGEL_SCORE"
    ILAE_SCORE = "ILAE_SCORE"
    OUTCOME = "OUTCOME"
    GENDER = "GENDER"
    HANDEDNESS = "HAND"
    SUBJECT_ID = "PATIENT_ID"


class GenericConfig(object):
    _module_path = os.path.dirname(eztrack.__file__)


class OutputConfig(object):
    subfolder = None

    def __init__(self, out_base=None, separate_by_run=False):
        """
        :param work_folder: Base folder where logs/figures/result should be kept
        :param separate_by_run: Set TRUE, when you want logs/result/figures to be in different files / each run
        """
        self._out_base = out_base or os.path.join(os.getcwd(), OUTBASENAME)
        self._separate_by_run = separate_by_run

    @property
    def FOLDER_LOGS(self):
        folder = os.path.join(self._out_base, "logs")
        if self._separate_by_run:
            folder = folder + datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")
        if not (os.path.isdir(folder)):
            os.makedirs(folder)
        return folder

    @property
    def FOLDER_RES(self):
        folder = os.path.join(self._out_base, "res")
        if self._separate_by_run:
            folder = folder + datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")
        if not (os.path.isdir(folder)):
            os.makedirs(folder)
        if self.subfolder is not None:
            os.path.join(folder, self.subfolder)
        return folder

    @property
    def FOLDER_TEMP(self):
        return os.path.join(self._out_base, "temp")


Config = OutputConfig


class FiguresConfig(object):
    LARGE_SIZE = (20, 15)
    SMALL_SIZE = (15, 10)
    VERY_LARGE_SIZE = (40, 20)
    # SUPER_LARGE_SIZE = (80, 40)
    SUPER_LARGE_SIZE = (150, 80)

    VERY_LARGE_PORTRAIT = (30, 50)
    SUPER_LARGE_PORTRAIT = (40, 70)

    FIG_FORMAT = "pdf"  # 'eps' 'pdf' 'svg'
    SAVE_FLAG = True
    SHOW_FLAG = True  # interactive mode and show?
    MOUSE_HOOVER = False
    MATPLOTLIB_BACKEND = "Agg"  # '#"Qt4Agg"  # , "Agg", "qt5"''

    NORMAL_FONT_SIZE = 30
    LARGE_FONT_SIZE = 50
    VERY_LARGE_FONT_SIZE = 70

    CBAR_NORMAL_FONT_SIZE = 45
