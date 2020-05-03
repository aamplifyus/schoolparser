import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from eztrack.base.metrics.metrics import counted
from eztrack.base.utils.bids_utils.bids_parser import BidsParser
from eztrack.cli.base.config import _get_bidsroot_path
from eztrack.cli.base.config import logger as logger
from eztrack.cli.utils.utils import _extract_run


class NoTraceBackWithLineNumber(Exception):
    def __init__(self, msg):
        self.args = ("{0.__name__}: {1}".format(type(self), msg),)
        sys.exit(self)


class CLI_Input_Error(NoTraceBackWithLineNumber):
    pass


def _check_metadatafunc_params(run_params, function):
    """Checks metadata or pat-summary function parameters and outputs user-friendly text."""
    # subject_ids = layout.get_subjects()
    # faster using os.glob if too many subjects
    bids_root = Path(_get_bidsroot_path())

    # Get subject_id from dict
    subject_id = run_params["subject_id"]
    # subject_id of None is allowed for these commands
    if subject_id is None:
        pass
    # if not none, check if a valid subject
    subject_ids = [
        os.path.basename(x).split("-")[-1]
        for x in bids_root.glob("*")
        if x.is_dir()
        if "sub" in x.as_posix()
    ]
    if subject_id not in subject_ids and subject_id is not "all":
        message_str = (
            f"Subject {subject_id} you passed in "
            f"is not a valid subject in your subject pool. "
            f"Here are the current subjects {subject_ids}."
        )
        error_msg = f"ez {function}: Subject {subject_id} is not a valid subject"
        logger.error(error_msg)
        counted("CLI_exceptions")
        raise CLI_Input_Error(message_str)


def _check_runfunc_params(run_params, function):
    """Check run or plot parameters and outputs user-friendly text."""
    bids_root = Path(_get_bidsroot_path())

    subject_id = run_params["subject_id"]
    session_id = run_params["session_id"]
    acquisition_id = run_params["acquisition_id"]
    run_id = run_params["run_id"]

    if any(x is None for x in [subject_id, session_id, run_id]):
        logger.error(
            f"ez {function} with subject_id: {subject_id}, session_id: {session_id}, "
            f"acquisition_id: {acquisition_id}, and run_id: {run_id}. \n"
            f"subject_id, session_id, and run_id must be set."
        )
        counted("CLI_exceptions")
        raise CLI_Input_Error(
            "\n\nEZTrack run requires subject_id, session_id, and run_id to be "
            "specified to analyze a specifically uploaded dataset. "
            "To see all subjects available, use the 'pat-summary' command. "
            "To see all datasets available, use the 'metadata' command. \n\n"
            "An example command looks like: "
            f"'ez {function} --subject_id <sub_id> --session_id <session_id> --run_id <run_id>'"
            "\n\nReplace words in brackets with your desired data identifiers."
        )
    subject_ids = [
        os.path.basename(x).split("-")[-1]
        for x in bids_root.glob("*")
        if x.is_dir()
        if "sub" in x.as_posix()
    ]

    if subject_id not in subject_ids:
        message_str = (
            f"Subject {subject_id} you passed in "
            f"is not a valid subject in your subject pool. "
            f"Here are the current subjects {subject_ids}."
        )
        error_msg = f"ez {function}: Subject {subject_id} is not a valid subject"
        logger.error(error_msg)
        counted("CLI_exceptions")
        raise CLI_Input_Error(message_str)

    acquisitions = ["ecog", "seeg", "eeg"]
    if acquisition_id not in acquisitions:
        error_msg = f"ez {function}: Acquisition {acquisition_id} is not supported yet."
        logger.error(error_msg)
        counted("CLI_exceptions")
        raise CLI_Input_Error(
            f"{acquisition_id} is not supported yet... "
            f"Pass 'ecog', 'seeg', or 'eeg'."
        )

    subj_bids_parser = BidsParser(bids_root, subject_id)
    # get the file paths to datasets
    _fpaths = [
        x.as_posix() for x in Path(bids_root / f"sub-{subject_id}").rglob("*.vhdr")
    ]
    _fpaths = [x for x in _fpaths if acquisition_id in x]

    # extract run
    run_ids = [_extract_run(x) for x in _fpaths]
    run_ids = ",".join(run_ids)
    if run_id not in run_ids:
        message_str = (
            f"Run {run_id} you passed in "
            f"is not a valid run for subject {subject_id} and acquisition {acquisition_id}. "
            f"Here are the current run ids {run_ids}."
        )
        error_msg = f"ez {function}: Run {run_id} is not a valid run"
        logger.error(error_msg)
        counted("CLI_exceptions")
        raise CLI_Input_Error(message_str)

    if function == "plot":
        colorblind = run_params["colorblind"]
        cmap = run_params["cmap"]
        # If colorblind is turned on, cmap should be None
        if colorblind and cmap is not None:
            logger.error(
                f"ez {function} with colorblind: True and cmap: {cmap}. Only one option can"
                f" be turned on."
            )
            counted("CLI_exceptions")
            raise CLI_Input_Error(
                "The colorblind option was turned on. You cannot also set a colormap."
            )

        # Check if a valid colormap was entered
        cmap_opts = plt.colormaps()
        if cmap not in cmap_opts and cmap is not None:
            logger.error(
                f"ez {function} with cmap: {cmap}. This is not a valid matplotlib cmap."
            )
            counted("CLI_exceptions")
            raise CLI_Input_Error(
                f"{cmap} is not a value colormap. Options are: {cmap_opts}"
            )


def _check_annotatechannelfunc_params(annotate_params, function):
    """Check channel annotation (view, write, read) function parameters and output user-friendly text."""
    bids_root = Path(_get_bidsroot_path())

    subject_id = annotate_params["subject_id"]
    session_id = annotate_params["session_id"]
    acquisition_id = annotate_params["acquisition_id"]

    subject_ids = [
        os.path.basename(x).split("-")[-1]
        for x in bids_root.glob("*")
        if x.is_dir()
        if "sub" in x.as_posix()
    ]
    if subject_id not in subject_ids:
        message_str = (
            f"Subject {subject_id} you passed in "
            f"is not a valid subject in your subject pool. "
            f"Here are the current subjects {subject_ids}."
        )
        error_msg = f"ez {function}: Subject {subject_id} is not a valid subject"
        logger.error(error_msg)
        counted("CLI_exceptions")
        raise CLI_Input_Error(message_str)

    if function is not "view_bad_chs":
        chs = annotate_params["chs"]
        if chs is None:
            logger.error(f"ez {function}: Must pass in channels to annotate.")
            counted("CLI_exceptions")
            raise CLI_Input_Error(f"ez {function}: Must pass in channels to annotate.")
