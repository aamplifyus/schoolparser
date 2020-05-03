"""
Data structure manipulations and conversions
- channels
- time points
- encoding numpy data structure
"""
import collections
import json
import logging
import re
from datetime import date, datetime
from typing import List, Dict

import mne
import numpy as np
from natsort import natsorted

from eztrack.base.config.config import CHANNEL_MARKERS

logger = logging.getLogger(__name__)


def _compute_samplepoints(winsamps, stepsamps, numtimepoints):
    # Creates a [n,2] array that holds the sample range of each window that
    # is used to index the raw data for a sliding window analysis
    samplestarts = np.arange(0, numtimepoints - winsamps + 1.0, stepsamps).astype(int)
    sampleends = np.arange(winsamps, numtimepoints + 1, stepsamps).astype(int)

    samplepoints = np.append(
        samplestarts[:, np.newaxis], sampleends[:, np.newaxis], axis=1
    )
    return samplepoints


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    def default(self, obj):
        if isinstance(
            obj,
            (
                np.int_,
                np.intc,
                np.intp,
                np.int8,
                np.int16,
                np.int32,
                np.int64,
                np.uint8,
                np.uint16,
                np.uint32,
                np.uint64,
            ),
        ):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):  # This is the fix
            return obj.tolist()
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def _ensure_list(arg):
    if not (isinstance(arg, list)):
        try:  # if iterable
            if isinstance(arg, (str, dict)):
                arg = [arg]
            else:
                arg = list(arg)
        except BaseException:  # if not iterable
            arg = [arg]
    return arg


def _get_centered_data(raw: mne.io.Raw, y_labels: Dict, by_electrode=False):
    """
    Construct signal time series by subtracting mean signal for each electrode.
    Corresponding white matter/grey matter labels are also returned.
    Parameters
    ----------
        raw: mne.io.Raw
            Raw object with channel info
        y_labels: Dict[str]: int
            Mapping of channel names to {0, 1} labeling
        by_electrode: bool
            If True, the channels are grouped by electrode and the mean
            signal for each electrode is subtracted for each group
    Returns
    -------
        X: np.ndarray
            Raw signal data corresponding to each channel
        y: np.ndarray
            {0, 1} labeling for each channel
        ch_names: List[str]
            List of channel names in the order that corresponds to the
            rows of X
    """
    X = None
    y = None
    if not by_electrode:
        ch_names = raw.ch_names
        raw = raw.set_eeg_reference(ref_channels="average")
        X = raw.get_data()
        y = np.array([y_labels[ch] for ch in ch_names])
    else:
        sorted_y_labels = natsorted(y_labels.keys())
        # get all unique electrodes
        elec_names = []
        for x in sorted_y_labels:
            elec_name = re.sub("[0-9]", "", x)
            if elec_name not in elec_names:
                elec_names.append(elec_name)
        # get the channel numbers for each electrode
        elec_to_channels = collections.defaultdict(list)
        for x in sorted_y_labels:
            elec, num = re.match("^([A-Za-z]+[']?)([0-9]+)$", x).groups()
            elec_to_channels[elec].append(elec + str(num))
        # Get channel data by electrode and mean subtract them
        ch_names = []
        for elec in elec_to_channels:
            chans_list = elec_to_channels[elec]
            # Add channel names to ch_names
            ch_names += list(chans_list.keys())
            labels = [y_labels[ch] for ch in chans_list]
            labels = np.array(labels)
            # Subtract out average signal
            elec_data = raw.get_data(chans_list)
            avg_signal = np.mean(elec_data, axis=0)
            centered_data = elec_data - avg_signal
            if (X is None) or (y is None):
                X = centered_data
                y = labels
            else:
                X = np.append(X, centered_data, axis=0)
                y = np.append(y, labels)
    return X, y, ch_names


def _find_bipolar_reference(ch_names):
    ch_names = natsorted(ch_names)
    # get all unique electrodes
    elec_names = []
    for x in ch_names:
        elec_name = re.sub("[0-9]", "", x)
        if elec_name not in elec_names:
            elec_names.append(elec_name)
    # get the channel numbers for each electrode
    elec_to_channels = collections.defaultdict(list)
    for x in ch_names:
        elec, num = re.match("^([A-Za-z]+[']?)([0-9]+)$", x).groups()
        elec_to_channels[elec].append(num)
    # get bipolar reference
    anode_chs = []
    cathode_chs = []
    for _elec_name, ch_list in elec_to_channels.items():
        n = len(ch_list)
        ch_list = np.array(ch_list)
        for (ch_num0, ch_num1) in zip(ch_list[: n - 2], ch_list[1 : n - 1]):
            anode_chs.append(f"{_elec_name}{ch_num0}")
            cathode_chs.append(f"{_elec_name}{ch_num1}")
    return anode_chs, cathode_chs


def _look_for_bad_channels(
    ch_names, bad_markers: List[str] = CHANNEL_MARKERS.BAD_MARKERS.name
):
    """
    Looks for hardcoding of what are "bad ch_names"

    Parameters
    ----------
    ch_names : (list) a list of str channel labels
    bad_markers : (list) of string labels

    Returns
    -------

    """
    orig_chdict = {ch.upper(): ch for ch in ch_names}

    ch_names = [c.upper() for c in ch_names]

    # initialize a list to store channel label strings
    bad_channels = []

    # look for ch_names without letter
    bad_channels.extend([ch for ch in ch_names if not re.search("[a-zA-Z]", ch)])
    # look for ch_names that only have letters - turn off for NIH pt17
    letter_chans = [ch for ch in ch_names if re.search("[a-zA-Z]", ch)]
    bad_channels.extend([ch for ch in letter_chans if not re.search("[0-9]", ch)])

    if "$" in bad_markers:
        # look for ch_names with '$'
        bad_channels.extend([ch for ch in ch_names if re.search("[$]", ch)])
    if "FZ" in bad_markers:
        badname = "FZ"
        bad_channels.extend([ch for ch in ch_names if ch == badname])
    if "GZ" in bad_markers:
        badname = "GZ"
        bad_channels.extend([ch for ch in ch_names if ch == badname])
    if "DC" in bad_markers:
        badname = "DC"
        bad_channels.extend([ch for ch in ch_names if badname in ch])
    if "STI" in bad_markers:
        badname = "STI"
        bad_channels.extend([ch for ch in ch_names if badname in ch])

    # extract non eeg ch_names based on some rules we set
    non_eeg_channels = [
        chan
        for chan in ch_names
        if any([x in chan for x in CHANNEL_MARKERS.NON_EEG_MARKERS.value])
    ]
    # get rid of these ch_names == 'e'
    non_eeg_channels.extend([ch for ch in ch_names if ch == "E"])
    bad_channels.extend(non_eeg_channels)

    bad_channels = [orig_chdict[ch] for ch in bad_channels]
    return bad_channels


def _channel_text_scrub(raw: mne.io.BaseRaw):
    """
    Clean and formats the channel text inside a MNE-Raw data structure.

    Parameters
    ----------
    raw : MNE-raw data structure
    """

    def _reformatchanlabel(label):
        """
        Process a single channel label.

        To make sure it is:

        - upper case
        - removed unnecessary strings (POL, eeg, -ref)
        - removed empty spaces
        """
        # hard coded replacement rules
        # label = str(label).replace("POL ", "").upper()
        label = str(label).replace("POL", "").upper()
        label = label.replace("EEG", "").replace("-REF", "")

        # replace "Grid" with 'G' label
        label = label.replace("GRID", "G")
        # for BIDS format, you cannot have blank channel name
        if label == "":
            label = "N/A"
        return label

    # apply channel scrubbing
    raw = raw.rename_channels(lambda x: x.upper())

    # encapsulated into a try statement in case there are blank channel names
    # after scrubbing these characters
    try:
        raw = raw.rename_channels(
            lambda x: x.strip(".")
        )  # remove dots from channel names
        raw = raw.rename_channels(
            lambda x: x.strip("-")
        )  # remove dashes from channel names
    except ValueError as e:
        logger.error(f"Ran into an issue when debugging: {raw.info}")
        logger.exception(e)

    raw = raw.rename_channels(lambda x: x.replace(" ", ""))
    raw = raw.rename_channels(
        lambda x: x.replace("’", "'")
    )  # remove dashes from channel names
    raw = raw.rename_channels(
        lambda x: x.replace("`", "'")
    )  # remove dashes from channel names
    raw = raw.rename_channels(lambda x: _reformatchanlabel(x))

    return raw


def _expand_channels(ch_list):
    ch_list = [a.replace("’", "'").replace("\n", "").replace(" ", "") for a in ch_list]

    new_list = []
    for string in ch_list:
        if string == "nan":
            continue

        if not string.strip():
            continue

        # A'1,2,5,7
        match = re.match("^([A-Za-z]+[']*)([0-9,]*)([A-Za-z]*)$", string)
        if match:
            name, fst_idx, last_idx = match.groups()
            numbers = fst_idx.split(",")
            new_list.extend([name + str(char) for char in numbers if char != ","])
            continue

        # A'1
        match = re.match("^([A-Za-z]+[']*)([0-9]+)$", string)
        if match:
            new_list.append(string)
            continue

        # A'1-10
        match = re.match("^([A-Za-z]+[']*)([0-9]+)-([0-9]+)$", string)
        if match:
            name, fst_idx, last_idx = match.groups()
            new_list.extend(
                [name + str(i) for i in range(int(fst_idx), int(last_idx) + 1)]
            )
            continue

        # A'1-A10
        match = re.match("^([A-Za-z]+[']*)([0-9]+)-([A-Za-z]+[']*)([0-9]+)$", string)
        if match:
            name1, fst_idx, name2, last_idx = match.groups()
            if name1 == name2:
                new_list.extend(
                    [name1 + str(i) for i in range(int(fst_idx), int(last_idx) + 1)]
                )
                continue

        # A'1,B'1,
        match = re.match("^([A-Za-z]+[']*)([0-9,])([A-Za-z]*)$", string)
        if match:
            name, fst_idx, last_idx = match.groups()
            numbers = fst_idx.split(",")
            new_list.extend([name + str(char) for char in numbers if char != ","])
            continue

        match = string.split(",")
        if match:
            new_list.extend([ch for ch in match])
            continue
        print("expand_channels: Cannot parse this: %s" % string)
    return new_list


def _set_channel_types(raw: mne.io.BaseRaw, verbose: bool) -> mne.io.BaseRaw:
    """Set channel types in raw using rules.

    Parameters
    ----------
    raw : mne.io.BaseRaw
    verbose : bool

    Returns
    -------
    raw : mne.io.BaseRaw
    """
    # set DC channels -> MISC for now
    picks = mne.pick_channels_regexp(raw.ch_names, regexp="DC|[$]")
    raw.set_channel_types(
        {raw.ch_names[pick]: "misc" for pick in picks}, verbose=verbose
    )
    # set channels named "E" to miscellaneous
    if "E" in raw.ch_names:
        raw.set_channel_types({"E": "misc"}, verbose=verbose)

    # set vagal nerve stimulation channels to 'bio'
    if "VNS" in raw.ch_names:
        raw.set_channel_types({"VNS": "bio"})

    # set bio channels (e.g. EKG, EMG, EOG)
    picks = mne.pick_channels_regexp(raw.ch_names, regexp="EKG|ECG")
    raw.set_channel_types(
        {raw.ch_names[pick]: "ecg" for pick in picks}, verbose=verbose
    )
    picks = mne.pick_channels_regexp(raw.ch_names, regexp="EMG")
    raw.set_channel_types(
        {raw.ch_names[pick]: "emg" for pick in picks}, verbose=verbose
    )
    picks = mne.pick_channels_regexp(raw.ch_names, regexp="EOG")
    raw.set_channel_types(
        {raw.ch_names[pick]: "eog" for pick in picks}, verbose=verbose
    )

    # set non-eeg channels leftover as 'misc'
    for chan in raw.ch_names:
        if any([x in chan for x in CHANNEL_MARKERS.NON_EEG_MARKERS.value]):
            raw.set_channel_types({chan: "misc"})

    return raw
