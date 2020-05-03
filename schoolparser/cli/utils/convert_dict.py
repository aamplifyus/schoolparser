import csv
import json

from eztrack.base.utils.errors import EZTrackRuntimeError


def file_to_dict(file_fpath):
    """

    Parameters
    ----------
    json_fpath :

    Returns
    -------

    """
    if ".json" in file_fpath:
        with open(file_fpath, "r") as fin:
            dict_out = json.load(fin)
        return dict_out
    elif ".tsv" in file_fpath:
        dict_out = {}
        with open(file_fpath, newline="") as fin:
            for i, row in enumerate(csv.DictReader(fin, delimiter="\t")):
                if i == 0:
                    dict_out.update(row)
                    for key, value in dict_out.items():
                        dict_out[key] = [dict_out[key]]
                else:
                    for key, value in row.items():
                        dict_out[key].append(value)
        return dict_out


def split_dict(full_dict):
    """

    Parameters
    ----------
    full_dict :

    Returns
    -------

    """
    eeg_dict = {}
    ieeg_dict = {}
    filenames = full_dict["filename"]
    eeg_indices = [False for i in filenames]
    ieeg_indices = [False for i in filenames]
    for i, fname in enumerate(filenames):
        if "ieeg" in fname:
            ieeg_indices[i] = True
        elif "eeg" in fname:
            eeg_indices[i] = True
        else:
            raise EZTrackRuntimeError(
                f"Scans supported by EZTrack are only "
                f"'ieeg' and 'eeg'. Your scan is named: {fname}."
            )
    for key, value in full_dict.items():
        eeg_dict[key] = [
            val for is_eeg, val in zip(eeg_indices, full_dict[key]) if is_eeg
        ]
        ieeg_dict[key] = [
            val for is_ieeg, val in zip(ieeg_indices, full_dict[key]) if is_ieeg
        ]
    return eeg_dict, ieeg_dict
