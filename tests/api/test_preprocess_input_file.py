from pathlib import Path
import pandas as pd

import pytest
from bids_validator import BIDSValidator
from mne_bids import (
    make_bids_basename,
    read_raw_bids,
)
from mne_bids.tsv_handler import _from_tsv

from eztrack.pipeline.preprocess.run_add_bad_channels import add_bad_chs, remove_bad_chs
from eztrack.base.utils.file_utils import _get_subject_channels_tsvs
from eztrack.base.data_validation.validate import validate_raw_metadata
from eztrack.pipeline.preprocess.run_bids_conversion import convert_edf_to_bids
from eztrack.pipeline.preprocess.append_metadata import (
    add_subject_metadata_from_excel,
    add_bad_chs_from_excel,
)

session = "seizure"
task = "monitor"
acquisition = "seeg"
run_id = "01"
kind = "ieeg"


@pytest.mark.usefixtures("tmp_bids_root", "bids_root", "scalp_edf_fpath")
def test_preprocess_edf_files(tmp_bids_root, bids_root, scalp_edf_fpath):
    """
    Test BIDS-compatible directory creation of EEG dataset.

    We copy some explicit example from MNE-BIDS and modify small details.
    Specifically, we will follow these steps:

    1. Download repository, and use the data in example directory:
        data/
            bids_layout/
                sourcedata/
                derivatives/
                sub-XXX/
                sub-XXY/
                ...

    2. Load the source raw data, extract information, preprocess certain things
    and save in a new BIDS directory

    3. Check the result and compare it with the standard of BIDS

    """
    # prepare bids_basename
    subject = "0001"
    bids_basename = make_bids_basename(subject, session, task, acquisition, run_id)

    # create the BIDS directory structure
    bids_root = convert_edf_to_bids(tmp_bids_root, scalp_edf_fpath, bids_basename)

    # bids filename should be in BrainVision format
    bids_fname = bids_basename + f"_{kind}.vhdr"

    # run bids-validator on the filenames
    rel_bids_root = f"/sub-0001/ses-seizure/{kind}/"
    path = str(Path(rel_bids_root + bids_fname))
    is_valid = BIDSValidator().is_bids(path)

    # debug test statements
    print(BIDSValidator().is_top_level(path))
    print(BIDSValidator().is_associated_data(path))
    print(BIDSValidator().is_session_level(path))
    print(BIDSValidator().is_subject_level(path))
    print(BIDSValidator().is_phenotypic(path))
    print(BIDSValidator().is_file(path))
    print("checked filepath: ", Path(rel_bids_root + bids_fname))

    # assert created file is BIDS-valid
    assert is_valid

    # Confirm we can read in the raw dataset.
    raw = read_raw_bids(bids_fname, bids_root)
    print(raw.info)
    raw.load_data()
    raw.drop_channels(raw.info["bads"])
    raw.pick_types(eeg=True, seeg=True, ecog=True)

    # run validation checks on the raw data
    is_valid_meta = validate_raw_metadata(raw)
    assert is_valid_meta


@pytest.mark.usefixtures("tmp_bids_root", "bids_root")
def test_adding_data_from_excelfile(tmp_bids_root, bids_root):
    """Tests functionality for appending data into BIDs from excel datasheet."""
    sourcedir = Path(Path(bids_root) / "sourcedata")
    subject = "pt1"
    run_id = "01"
    bids_basename = make_bids_basename(subject, session, task, acquisition, run_id)

    # source filepath
    source_fpath = Path(
        sourcedir / subject / "ieeg" / "edf" / "pt1sz2_0001_reduced.edf"
    )

    # excel filepath
    excel_fpath = Path(sourcedir / "test_clinicaldata.xlsx")

    # create the BIDS directory structure
    tmp_bids_root = convert_edf_to_bids(tmp_bids_root, source_fpath, bids_basename)

    # append patient level metadata from excel file
    add_subject_metadata_from_excel(
        tmp_bids_root, subject=subject, excel_fpath=excel_fpath
    )

    # append bad ch_names from excel file
    add_bad_chs_from_excel(
        tmp_bids_root,
        subject=subject,
        excel_fpath=excel_fpath,
        acquisition=acquisition,
    )


@pytest.mark.parametrize(
    "acquisition", ["ecog", "eeg",],
)
@pytest.mark.usefixtures("tmp_bids_root", "bids_root")
def test_adding_bad_channels_from_cli(tmp_bids_root, bids_root, acquisition):
    """Tests functionality for appending data into BIDs from excel datasheet."""
    sourcedir = Path(Path(bids_root) / "sourcedata")
    subject = "pt1"
    run_id = "01"
    session = "seizure"
    bids_basename = make_bids_basename(subject, session, task, acquisition, run_id)

    # source filepath
    if acquisition == "ecog":
        source_fpath = Path(
            sourcedir / subject / "ieeg" / "edf" / "pt1sz2_0001_reduced.edf"
        )
    elif acquisition == "eeg":
        source_fpath = Path(sourcedir / subject / "eeg" / "edf" / "pt1sz1_0001.edf")

    # create the BIDS directory structure
    bids_root = convert_edf_to_bids(tmp_bids_root, source_fpath, bids_basename)

    # Channels to annotate as bad, then turn back to good
    # should be agnostic to letter-casing
    add_bads_list = ["AD1", "AD2", "ad3"]

    # Read in current channel statuses
    channel_fpaths = _get_subject_channels_tsvs(
        bids_root, subject, session, acquisition
    )
    channel_fpath = channel_fpaths[0]
    channel_tsv = _from_tsv(channel_fpath)
    indices = [
        i
        for i, ch in enumerate(channel_tsv["name"])
        if ch.upper() in add_bads_list
        if ch.lower() in add_bads_list
    ]
    for ind in indices:
        assert channel_tsv["status"][ind] != "bad"

    # Annotate the channels as bad
    add_bad_chs(bids_root, subject, session, acquisition, add_bads_list)

    # Read in current channel statuses
    channel_tsv = _from_tsv(channel_fpath)
    for ind in indices:
        assert channel_tsv["status"][ind] == "bad"

    # The removed bad channels should be the same as those added
    remove_bads_list = add_bads_list

    # Annotate the channels as good again
    remove_bad_chs(bids_root, subject, session, acquisition, remove_bads_list)

    # Read in current channel statuses
    channel_tsv = _from_tsv(channel_fpath)
    for ind in indices:
        assert channel_tsv["status"][ind] != "bad"
