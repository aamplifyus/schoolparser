"""Private functions to deal with parsing MNE.Annotations."""
from typing import Dict

import mne
import numpy as np

from eztrack.base.utils.data_structures_utils import _compute_samplepoints, _ensure_list


def _map_events_to_window(
    raw: mne.io.BaseRaw, winsize: int, stepsize: int
) -> (np.ndarray, Dict):
    """Map events/events_id to window based sampling."""
    # get events and convert to annotations
    events, events_id = mne.events_from_annotations(raw, verbose=False)

    # get the length of recording
    length_recording = len(raw)

    # compute list of end-point windows for analysis
    samplepoints = _compute_samplepoints(winsize, stepsize, length_recording)

    # map each event onset to a window
    for i in range(events.shape[0]):
        event_onset_sample = events[i, 0]
        # print(event_onset_sample)
        # print(samplepoints)
        event_onset_window = _sample_to_window(event_onset_sample, samplepoints)
        events[i, 0] = event_onset_window

    return events, events_id


def _map_seizure_event_to_window(
    raw: mne.io.BaseRaw, winsize: int, stepsize: int, verbose: bool
) -> (int, int, int):
    """Map a seizure event sample to window sample."""
    # get events and convert to annotations
    events, events_id = mne.events_from_annotations(raw, verbose=verbose)

    # get the length of recording
    length_recording = len(raw)

    # compute list of end-point windows for analysis
    samplepoints = _compute_samplepoints(winsize, stepsize, length_recording)

    # compute periods of interest - seizure
    (onset_sample, offset_sample) = _find_sz_samples(events, events_id)
    clin_onset_sample = _find_clin_onset_samples(events, events_id)

    if verbose:
        print(onset_sample, offset_sample, length_recording)
    if onset_sample:
        onset_window = _sample_to_window(onset_sample, samplepoints)
    else:
        onset_window = None
    if offset_sample:
        offset_window = _sample_to_window(offset_sample, samplepoints)
    else:
        offset_window = None
    if clin_onset_sample:
        clin_onset_window = _sample_to_window(clin_onset_sample, samplepoints)
    else:
        clin_onset_window = None
    return onset_window, offset_window, clin_onset_window


def _find_sz_samples(events, events_id, verbose=False, **kwargs):
    """
    Find seizure sample points in Annotations.

    Performs find, by hardcoded lower-case keywords.

    Parameters
    ----------
    events :
    events_id :

    Returns
    -------
    onset_sample, offset_sample
    """
    onset_keywords = [
        "sz event",  # jhh
        "sz onset",  # ummc
        "definite onset",  # nih
        "onset",
        "start",
        "sz start",  # umf
        "eeg onset",
    ]
    offset_keywords = [
        "devolution",
        "electrographic end",
        "sz event over",
        "z over",
        "over",  # jhh
        "sz offset",  # ummc
        "definite off",  # nih
        "offset",
        "end",
        "sz end",  # umf
        "seizure end",
    ]

    # onset_keywords = [
    #     "sz event",
    #     "eeg onset",
    #     "sz onset",
    #     "ictal onset",
    #     "seizure onset",
    #     "sz start",
    # ]
    #
    # offset_keywords = ["end", "offset", "seizure end", "sz off", "sz end", "devolution"]

    if "onset" in kwargs.keys():
        onset_keywords.extend(_ensure_list(kwargs["onset"]))
    if "offset" in kwargs.keys():
        offset_keywords.extend(_ensure_list(kwargs["offset"]))

    onset_id = None
    offset_id = None

    # loop through keywords
    for onset_kwg in onset_keywords:
        for key, val in events_id.items():
            # if key
            if onset_id is None:
                if onset_kwg.lower() == key.lower():
                    onset_id = val
    for offset_kwg in offset_keywords:
        for key, val in events_id.items():
            # if key
            if offset_id is None:
                if offset_kwg.lower() == key.lower():
                    offset_id = val

    # loop through events
    # for key, val in events_id.items():
    #     # if key
    #     if onset_id is None:
    #         if any(x in key.lower() for x in onset_keywords):
    #             onset_id = val
    #     if offset_id is None:
    #         if any(x in key.lower() for x in offset_keywords):
    #             offset_id = val

    # hack to find onset after the first one doesn't work
    if onset_id is None:
        for key, val in events_id.items():
            # if key
            if onset_id is None:
                if any(x in key.lower() for x in ["sz", "onset"]):
                    onset_id = val
            if offset_id is None:
                if any(
                    x in key.lower() for x in ["end", "offset", "seizure end", "sz off"]
                ):
                    offset_id = val

    # inverse of ids
    inv_map = {v: k for k, v in events_id.items()}

    # find onset/offset samples
    offset_ind = np.where(events[:, 2] == offset_id)[0]
    onset_ind = np.where(events[:, 2] == onset_id)[0]
    if len(onset_ind) > 0:
        onset_ind = onset_ind[0]
        onset_sample = events[onset_ind, 0]

        if len(offset_ind) > 0:
            offset_ind = offset_ind[0]
            offset_sample = events[offset_ind, 0]
        else:
            offset_sample = None
    else:
        onset_sample = None
        offset_sample = None

    if verbose:
        print(onset_sample, offset_sample)

    if onset_id and offset_id:
        print(
            "Found events: \n'{}' and '{}'".format(
                inv_map[onset_id], inv_map[offset_id]
            )
        )
    return (onset_sample, offset_sample)


def _find_clin_onset_samples(events, events_id):
    """
    Find clinical onset samples in Annotations.

    Performs find, by hardcoded lower-case keywords.

    Parameters
    ----------
    events :
    events_id :

    Returns
    -------
    onset_sample
    """
    onset_id = None

    # inverse of ids
    inv_map = {v: k for k, v in events_id.items()}

    for key, val in events_id.items():
        if onset_id is None:
            if any(x in key.lower() for x in ["clin onset", "clin"]):
                onset_id = val
                print("Found events: {}".format(inv_map[onset_id]))
    if onset_id is None:
        return None
    onset_ind = np.where(events[:, 2] == onset_id)[0]
    if len(onset_ind) > 0:
        onset_sample = events[onset_ind[0], 0]
    else:
        onset_sample = None

    return onset_sample


def _sample_to_window(sample, samplepoints):
    return int(
        np.where((samplepoints[:, 0] <= sample) & (samplepoints[:, 1] >= sample))[0][0]
    )
