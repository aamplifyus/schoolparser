"""Define fixtures available for eztrack testing."""
import os.path
import platform
import sys
from pathlib import Path
import shutil

import numpy as np
import pytest
from click.testing import CliRunner
from mne.utils import run_subprocess
from mne_bids import make_bids_basename

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "eztrack"))

np.random.seed(987654321)

# bids root
BIDS_ROOT = Path(Path(os.getcwd()) / "data/bids_layout")

# source data not in BIDS format
SOURCEDIR = Path(BIDS_ROOT / "sourcedata")

# directory of example computed results that should match output of pipeline tests
RESULTDATADIR = Path(BIDS_ROOT / "derivatives")


# WINDOWS issues:
# the bids-validator development version does not work properly on Windows as
# of 2019-06-25 --> https://github.com/bids-standard/bids-validator/issues/790
# As a workaround, we try to get the path to the executable from an environment
# variable VALIDATOR_EXECUTABLE ... if this is not possible we assume to be
# using the stable bids-validator and make a direct call of bids-validator
# also: for windows, shell = True is needed to call npm, bids-validator etc.
# see: https://stackoverflow.com/q/28891053/5201771
@pytest.fixture(scope="session")
def _bids_validate():
    """Fixture to run BIDS validator."""
    shell = False
    bids_validator_exe = ["bids-validator", "--config.error=41", "--config.error=41"]
    if platform.system() == "Windows":
        shell = True
        exe = os.getenv("VALIDATOR_EXECUTABLE", "n/a")
        if "VALIDATOR_EXECUTABLE" != "n/a":
            bids_validator_exe = ["node", exe]

    def _validate(bids_root):
        try:
            cmd = bids_validator_exe + [bids_root]
            run_subprocess(cmd, shell=shell)
        except Exception as e:
            print(e)
            return True

    return _validate


@pytest.fixture(scope="function")
def tmp_bids_root(tmp_path_factory):
    """
    Fixture of a temporary path that can be used as a bids_directory.

    Should be used for:
    - testing bids setup
    - testing bids reading after setup
    - testing bids writing after setup

    Parameters
    ----------
    tmp_path_factory :

    Returns
    -------
    bids_root : (str) the temporary path to a bids_root
    """
    bids_root = tmp_path_factory.mktemp("bids_data")
    return str(bids_root)


@pytest.fixture(scope="function")
def subjects_dir_tmp(tmp_path_factory, monkeypatch):
    """Copy MNE-testing-data subjects_dir to a temp dir for manipulation."""
    tmpdir = tmp_path_factory.mktemp("tmp_bids")
    # shutil.copytree(BIDS_ROOT, str(tmpdir))
    src = BIDS_ROOT
    dst = str(tmpdir)
    try:
        # if path already exists, remove it before copying with copytree()
        if os.path.exists(dst):
            shutil.rmtree(dst)
            shutil.copytree(src, dst)
    except OSError as e:
        print(e)

    # set temporary path now
    monkeypatch.setenv("BIDSROOT", str(tmpdir))
    return str(tmpdir)


@pytest.fixture(scope="session")
def bids_root():
    """
    Fixture of a bids_directory.

    Should be used for:
    - testing bids setup
    - testing bids reading after setup
    - testing bids writing after setup

    Returns
    -------
    bids_root : (str) the path to a bids_root
    """
    return str(BIDS_ROOT)


@pytest.fixture(scope="session")
def electrode_layout_fpath():
    """Fixture path to an example electrode_layout.xlsx file."""
    return Path(SOURCEDIR / "la02" / "ieeg" / "electrode_layout.xlsx")


@pytest.fixture(scope="class")
def scalp_edf_fpath():
    """
    FOR TESTING EDF RAWDATA OF PREFORMATTING INTO FIF+JSON PAIRS.

    Returns
    -------
    fpath
    """
    # load in edf data
    fpath = Path(SOURCEDIR / "0001" / "eeg" / "edf" / "scalp_sz_test.edf")
    return fpath


@pytest.fixture(scope="class")
def ieeg_edf_fpath():
    """
    FOR TESTING EDF RAWDATA OF PREFORMATTING INTO BRAINVISION FORMAT.

    Returns
    -------
    fpath
    """
    # load in edf data
    fpath = Path(SOURCEDIR / "la02" / "ieeg" / "edf" / "la02_ictal_reduced.edf")
    return fpath


@pytest.fixture(scope="class")
def ieeg_bv_fpath():
    """
    FOR TESTING EDF RAWDATA OF PREFORMATTING INTO BRAINVISION FORMAT.

    Returns
    -------
    fpath
    """
    # load in edf data
    fpath = Path(
        SOURCEDIR / "la02" / "ieeg" / "brainvision" / "la02_ictal_reduced.vhdr"
    )
    return fpath


@pytest.fixture(scope="class")
def ieeg_txt_fpath():
    """
    FOR TESTING EDF RAWDATA OF PREFORMATTING INTO BRAINVISION FORMAT.

    Returns
    -------
    fpath
    """
    # load in edf data
    fpath = Path(SOURCEDIR / "la02" / "ieeg" / "text" / "la02_ictal_reduced.txt")
    return fpath


@pytest.fixture(scope="session")
def bids_fname():
    """Bids filename for pytest."""
    subject = "la02"
    session = "seizure"
    task = "monitor"
    acquisition = "seeg"
    run_id = "01"
    kind = "ieeg"

    bids_basename = make_bids_basename(subject, session, task, acquisition, run_id)
    bids_fname = bids_basename + f"_{kind}.vhdr"
    return bids_fname


@pytest.fixture(scope="session")
def scalp_bids_fname():
    """Bids filename for pytest."""
    subject = "la02"
    session = "seizure"
    task = "monitor"
    acquisition = "eeg"
    run_id = "01"
    kind = "eeg"

    bids_basename = make_bids_basename(subject, session, task, acquisition, run_id)
    bids_fname = bids_basename + f"_{kind}.vhdr"
    return bids_fname


@pytest.fixture(scope="module")
def runner():
    """Fixture for CLI Runner."""
    return CliRunner()
