import glob
import os
import warnings
from pathlib import Path
from typing import List, Union

import pandas as pd
from bids import BIDSLayout
from mne_bids.tsv_handler import _to_tsv, _from_tsv


def _find_wmchs_in_electrodestsv(fname, atlas_name=None):
    if atlas_name is None:
        atlas_name = ["desikan-killiany", "destriuex"]
    else:
        atlas_name = [atlas_name]

    electrodes_tsv = _from_tsv(fname)
    electrodes_df = pd.DataFrame.from_dict(electrodes_tsv)

    atlas_wm_chs = []
    for atlas in atlas_name:
        # get wm from destrieux/dk atlases
        electrodes_df[atlas] = electrodes_df[atlas].str.lower()
        atlas_wm = electrodes_df[electrodes_df[atlas].str.contains("white-matter")]
        wm_chs = atlas_wm["name"].tolist()
        atlas_wm_chs.append(wm_chs)

    all_wm_chs = atlas_wm_chs
    wm_chs = set().union(*all_wm_chs)
    wm_chs = [x.upper() for x in wm_chs if not x.upper().startswith("L")]
    return wm_chs


def _define_unique_tempdir(bids_root, reference, fname):
    tempdir = Path(
        bids_root / "derivatives" / "fragility" / reference / f"{fname}-tempdir"
    )
    return tempdir


def _update_sidecar_tsv_byname(
    sidecar_fname: str,
    name: Union[List, str],
    colkey: str,
    val: str,
    allow_fail=False,
    verbose=False,
):
    """Update a sidecar JSON file with a given key/value pair.

    Parameters
    ----------
    sidecar_fname : str
        Full name of the data file
    name : str
        The name of the row in column "name"
    colkey : str
        The lower-case column key in the sidecar TSV file. E.g. "type"
    val : str
        The corresponding value to change to in the sidecar JSON file.
    """
    # convert to lower case and replace keys that are
    colkey = colkey.lower()

    if isinstance(name, list):
        names = name
    else:
        names = [name]

    # load in sidecar tsv file
    sidecar_tsv = _from_tsv(sidecar_fname)

    for name in names:
        # replace certain apostrophe in Windows vs Mac machines
        name = name.replace("’", "'")

        if allow_fail:
            if name not in sidecar_tsv["name"]:
                warnings.warn(
                    f"{name} not found in sidecar tsv, {sidecar_fname}. Here are the names: {sidecar_tsv['name']}"
                )
                continue

        # get the row index
        row_index = sidecar_tsv["name"].index(name)

        # write value in if column key already exists,
        # else write "n/a" in and then adjust matching row
        if colkey in sidecar_tsv.keys():
            sidecar_tsv[colkey][row_index] = val
        else:
            sidecar_tsv[colkey] = ["n/a"] * len(sidecar_tsv["name"])
            sidecar_tsv[colkey][row_index] = val

    _to_tsv(sidecar_tsv, sidecar_fname)


def _get_subject_acquisitions(bids_root, subject_id, session_id=None):
    # get files of that subject using BIDS Layout
    layout = BIDSLayout(bids_root)
    bids_filters = {
        "subject": subject_id,
    }
    if session_id is not None:
        bids_filters["session"] = session_id
    acqs = layout.get_acquisitions(**bids_filters)
    return acqs


def _get_subject_recordings(
    fpath: Union[Path, str],
    subject: str,
    exclusion_str: List[str] = [""],
    ext: str = "edf",
) -> List:
    """Find patient recordings with extension in filepath.

    Parameters
    ----------
    fpath :
    subject :
    exclusion_str :
    ext :

    Returns
    -------
    fpaths : List
    """
    if not isinstance(fpath, str):
        fpath = str(fpath)

    if subject not in fpath:
        raise RuntimeError(f"Subject id {subject} not in filepath: {fpath}.")

    # go to the acquisition path
    datapath = Path(fpath + "/")

    # return all files with extension
    return [
        x
        for x in datapath.glob(f"*.{ext}")
        if not any(_exc_str.lower() in str(x).lower() for _exc_str in exclusion_str)
        if not x.name.startswith(".")  # make sure not a cached hidden file
    ]


def _get_subject_channels_tsvs(
    bids_root: Union[Path, str], subject: str, session: str, acquisition: str,
) -> List:
    """Find patient channel files.

    Parameters
    ----------
    bids_root :
    subject :
    session :
    acquisition :

    Returns
    -------
    fpaths : List

    """
    if not isinstance(bids_root, str):
        bids_root = str(bids_root)

    if acquisition in ["ecog", "seeg"]:
        kind = "ieeg"
    elif acquisition == "eeg":
        kind = "eeg"

    if acquisition is None:
        suffix = "**/*channels.tsv"
    else:
        suffix = f"{kind}/*channels.tsv"

    searchpath = os.path.join(bids_root, f"sub-{subject}", f"ses-{session}", suffix)

    # return all files with extension
    return [
        x
        for x in glob.glob(searchpath, recursive=True)
        if f"acq-{acquisition}" in x  # make sure acquisition matches
        if not x.startswith(".")  # make sure not a cached hidden file
    ]


def _get_prob_chs(
    electrode_fpath: Union[Path, str], key: str, contains: bool = False
) -> List:
    """Read in problematic ch_names from electrode_layout_fpath.xlsx.

    Parameters
    ----------
    electrode_fpath : Path | str
    key : str
    contains: bool

    Returns
    -------
    chs : List
    """
    ch_df = pd.read_excel(electrode_fpath, header=0, index_col=0,)

    # perform preprocessing on the strings
    key = key.upper()
    ch_df = ch_df.apply(lambda x: x.astype(str).str.upper())
    ch_df = ch_df.apply(lambda x: x.replace("’", "'"))
    ch_df = ch_df.apply(lambda x: x.replace("’", "'"))
    ch_df = ch_df.apply(lambda x: x.replace("`", "'"))
    ch_df = ch_df.apply(lambda x: x.replace(" ", ""))  # remove spaces in channel names
    ch_dict = ch_df.T.to_dict()

    chs = []
    for elec_key, elec_dict in ch_dict.items():
        for ch_ind, ch_status in elec_dict.items():
            if contains is False:
                if ch_status.strip() == key:
                    ch_name = str(elec_key) + str(ch_ind)
                    ch_name = ch_name.replace(" ", "")
                    chs.append(ch_name)
            else:
                if key in ch_status.strip():
                    ch_name = str(elec_key) + str(ch_ind)
                    ch_name = ch_name.replace(" ", "")
                    chs.append(ch_name)
    return chs


def _get_subject_electrode_layout(
    fpath: Union[Path, str], subject: str, acquisition: str = "seeg"
) -> Path:
    """Find patient electrode layout.xlsx file."""
    if not isinstance(fpath, str):
        fpath = str(fpath)

    if subject not in fpath:
        warnings.warn(f"Subject id {subject} not in filepath: {fpath}. Adding it in")
        fpath = Path(Path(fpath) / subject).as_posix()

    # go to the acquisition path
    datapath = Path(fpath + "/" + acquisition + "/electrode_layout.xlsx")

    if not datapath.exists():
        warnings.warn(
            f"Subject id {subject} does not have existing electrode layout file at {datapath.as_posix()}..."
        )

    # return all files with extension
    print(datapath)
    return datapath
