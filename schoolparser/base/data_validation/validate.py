"""Verification and validation software testing.

===============================================
01. Verification and Validation Explicit Checks
===============================================

In this script, we perform Verification and Validation
 for specific processes that are necessary for repo to
 work as expected. Specifically, we will follow these steps:

1. Load test EEG data with known expected output

2. Verify processes:

    - conversion to BIDS
    - analysis of data
    - heatmap output

3. Check heatmap is the same, check that
differences numerically are up to a machine precision.

"""

import json
from pathlib import Path
from typing import Dict, Union

import mne
import numpy as np
from mne_bids import read_raw_bids

from eztrack.base.utils.errors import EZTrackRuntimeError
from eztrack.cli.base.config import logger as logger


def validate_raw_metadata(raw: mne.io.BaseRaw):
    """
    Validate metadata of the raw dataset.

    Covers requirements laid out in the 7.2 SRS of EZTrack.

    Note that MNE-Python automatically checks the following:
    1. channel name - duplicates produce an error
    2. presence of sampling rate, electrode units, and electrode type
    3. Annotations are automatically checked for onset, duration and description
    that are denoted in seconds.
    4. Conversion to volts of the raw dataset.

    Note that MNE-BIDS automatically checks the following:
    1. Electrode status through the `channels.tsv` file.

    Parameters
    ----------
    raw : instance of Raw
        The data as MNE-Python Raw object.

    Returns
    -------
    1, or 0 for success, or failure.
    """
    _fname = raw.filenames

    logger.info(f"Checking over raw dataset loaded from {_fname}")

    # sampling rate
    if raw.info["sfreq"] is None:
        logger.error("Sampling rate should be set.")

    if raw.info["sfreq"] < 250 or raw.info["sfreq"] > 2500:
        logger.warning(
            "Sampling of datasets was only tested for 250-2000 Hz. "
            f"Your dataset is {raw.info['sfreq']}."
        )

    # check recording length
    dataset_len = raw.info["sfreq"] * len(raw)
    if dataset_len < 20:
        logger.exception(
            f"Raw dataset should be at least 20 seconds. The length"
            f"of this dataset is: {dataset_len}."
        )
        raise EZTrackRuntimeError(
            f"Raw dataset should be at least 20 seconds. The length"
            f"of this dataset is: {dataset_len}."
        )

    # check anonymization
    subject_info = raw.info["subject_info"]
    if subject_info is not None:
        if any(
            [
                subject_info.get("his_id", None),
                subject_info.get("last_name", None),
                subject_info.get("first_name", None),
                subject_info.get("middle_name", None),
                subject_info.get("birthday", None),
            ]
        ):
            logger.exception(
                "Anonmyization was not done correctly. 'his_id', "
                "last_name, first_name, middle_name, and birthday "
                "should be None inside raw.info. Subject info "
                f"is: {subject_info}."
            )
            raise EZTrackRuntimeError(
                "Anonmyization was not done correctly. 'his_id', "
                "last_name, first_name, middle_name, and birthday "
                "should be None inside raw.info. Subject info "
                f"is: {subject_info}."
            )
    if raw.info["meas_date"] is not None:
        if raw.info["meas_date"].year >= 1925:
            logger.exception(
                "All measurement dates should have been set to before 1925 "
                "for anonymization purposes. The date of this dataset is: "
                f"{raw.info['meas_date']}."
            )
            raise EZTrackRuntimeError(
                "All measurement dates should have been set to before 1925 "
                "for anonymization purposes. The date of this dataset is: "
                f"{raw.info['meas_date']}."
            )

    # check number of channels
    eeg_related_chs = list(mne.pick_types(raw.info, eeg=True, ecog=True, seeg=True))
    if len(eeg_related_chs) > 200:
        logger.exception(
            f"EZTrack needs to have channel count of less than 200 channels "
            f"to run in an allotted period of time. "
            f"The current dataset has {len(eeg_related_chs)} chs."
        )
        raise EZTrackRuntimeError(
            f"EZTrack needs to have channel count of less than 200 channels "
            f"to run in an allotted period of time. "
            f"The current dataset has {len(eeg_related_chs)} chs."
        )

    # check that all the bad chs are outside the dataset
    bad_chs = raw.info["bads"]
    bad_chs_in_raw = [ch for ch in raw.ch_names if ch in bad_chs]
    if len(bad_chs_in_raw) != 0:
        logger.exception(
            f"All bad channels should be dropped. There are still bad channels "
            f"in the raw EEG dataset. {bad_chs_in_raw}"
        )
        raise EZTrackRuntimeError(
            f"All bad channels should be dropped. There are still bad channels "
            f"in the raw EEG dataset. {bad_chs_in_raw}"
        )

    # check channel types
    ch_types = raw.get_channel_types()
    if any([x not in ["eeg", "seeg", "ecog"] for x in ch_types]):
        logger.exception(
            f"Channel types left after preprocessing data should "
            f"only be 'eeg', 'ecog', or 'seeg'. Your dataset still "
            f"has channel types: {ch_types}."
        )

    return 1


def validate_eztrack_result(perturbation_mat: np.ndarray, metadata: Dict):
    """
    Validate metadata of the result dataset.

    Covers requirements laid out in the 7.3 SRS of EZTrack.

    Parameters
    ----------
    perturbation_mat : np.ndarray
    metadata : dict

    """
    ch_names = metadata["ch_names"]
    if len(ch_names) != perturbation_mat.shape[0]:
        logger.exception(
            "End EZTrack result needs to be C x T. The first axis does not "
            "line up with how many channels there are."
        )
        raise EZTrackRuntimeError(
            f"End EZTrack result needs to be C x T. The first axis does not "
            "line up with how many channels there are."
        )

    return 1


def compare_chs_raw_versus_result(
    result_json_fpath: Union[Path, str], bids_fname: str, bids_root: Union[Path, str]
):
    """
    Compare good channels in raw file versus result.

    Parameters
    ----------
    result_json_fpath :
        Output side car json filepath
    bids_fname :
        The filename of the analyzed dataset
    bids_root :
        The BIDS root directory

    """
    # load in the channels data for original raw data
    raw = read_raw_bids(bids_fname, bids_root)
    raw = raw.drop_channels(raw.info["bads"])
    raw = raw.select_channel_types(eeg=True, ecog=True, seeg=True)

    # get the raw channel names after dropping all these bad channels
    raw_ch_names = raw.ch_names

    # load resulting metadata
    with open(result_json_fpath, "r") as fin:
        metadata = json.load(fin)
    result_ch_names = metadata["ch_names"]

    ERROR = False
    for ch in raw_ch_names:
        if ch in result_ch_names:
            logger.exception(
                f"{ch} was identified as bad, but is in "
                f"the resulting sidecar json analyzed channels."
            )
            ERROR = True

    if ERROR:
        raise EZTrackRuntimeError(
            "Channels that were in raw, identified as bad "
            "were still present in the resulting analysis."
        )
