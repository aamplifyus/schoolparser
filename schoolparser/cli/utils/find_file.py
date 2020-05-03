import os
from warnings import warn

from mne_bids import make_bids_basename

from eztrack.base.utils.bids_utils.bids_run import BidsRun
from eztrack.base.utils.errors import EZTrackValueError
from eztrack.cli.base.config import (
    DEFAULT_TASK,
    DEFAULT_ACQUISITION,
    _get_bidsroot_path,
    _get_derivatives_path,
)
from .convert_dict import file_to_dict


def find_bids_run_file(
    subject_id,
    session_id,
    task_id,
    acquisition_id,
    run_id,
    kind,
    datadir,
    ext,
    center=None,
):
    """
    Get the path of the data file of interest.

    TODO: Allow searching through other folders for preprocessed and results files for this run.
    TODO: Should this be done on BidsRun side?

    Parameters
    ----------
    subject_id : str
        The unique identifier for the subject. We may need to have some mapping functions.
    session_id : str
        The identifier for the session of the subject. Again, mapping may be necessary for anonymity.
    task_id : str or None
        Identifier for the task
    acquisition_id: str or None
        Identifier for the acquisition
    run_id : str
        The identifier for the run of the subject.
    kind : str
        The type of recording
    datadir : Union[str, os.PathLike]
        Base directory containing the bids data.
    ext : str (fif or edf)
        either fif or edf
    center : str or None
        The name of the center that the patient belongs to

    Returns
    -------
    bids_run_fpath: os.PathLike
        The location of the desired file.

    """
    if task_id is None:
        task_id = DEFAULT_TASK
    if acquisition_id is None:
        acquisition_id = DEFAULT_ACQUISITION
    bids_root = datadir
    bids_fname = make_bids_basename(
        subject=subject_id,
        session=session_id,
        task=task_id,
        acquisition=acquisition_id,
        run=run_id,
        suffix=f"{kind}.{ext}",
    )
    bids_run = BidsRun(bids_root, bids_fname)
    return bids_root, bids_fname, bids_run.fpath


def parse_bids_layout(subject_id, datadir, center):
    """
    Print the directory tree for this subject to show all available data.

    Parameters
    ----------
    subject_id : str
        The unique identifier for the subject.
    datadir : Union[str, os.PathLike]
        Base directory containing the bids data.
    center : str or None
        The name of the center that the patient belongs to

    Examples
    --------
    In this example, assume there is a directory for a subject named 'subject-01' that belongs to 'center-01'
    with the following structure:

        bids-dir/
            center-01/
                sub-01/
                    sub-01_scans.tsv
                    ses-01/
                        eeg/
                            sub-01_ses-01_run-01_eeg.edf
                            sub-01_ses-01_run-01_eeg.json
                            sub-01_ses-01_run-01_channels.tsv
                            sub-01_ses-01_run-02_eeg.edf
                            sub-01_ses-01_run-02_eeg.json
                            sub-01_ses-01_run-02_channels.tsv

    .. code-block:: python
        file_list = parse_bids_layout('subject-01', 'bids-dir', 'center-01')
        for filename in file_list:
            print(filename)

    The above code will result in the structure following mne-bids print_dir_tree structure:
        |sub-01
        |--- sub-01_scans.tsv
        |--- ses-01/
        |------ eeg/
        |--------- sub-01_ses-01_run-01_eeg.edf
        |--------- sub-01_ses-01_run-01_eeg.json
        |--------- sub-01_ses-01_run-01_channels.tsv
        |--------- sub-01_ses-01_run-02_eeg.edf
        |--------- sub-01_ses-01_run-02_eeg.json
        |--------- sub-01_ses-01_run-02_channels.tsv

    Notes
    -----
    Simplifications were made to structure to make example more easily followable.
    This is not currently Bids format.

    Returns
    -------
    subject_layout: list[str]
        The list of files with some tree structure for easy printing.

    """
    if center is None:
        main_dir = os.path.join(datadir, "sub-" + subject_id)
    else:
        main_dir = os.path.join(datadir, center, "sub-" + subject_id)
    if not os.path.exists(main_dir):
        raise EZTrackValueError("Directory does not exist: {}".format(main_dir))
    baselen = len(main_dir.split(os.sep)) - 1
    subject_layout = []
    for root, dirs, files in os.walk(main_dir):
        branchlen = len(root.split(os.sep)) - baselen
        if branchlen <= 1:
            subject_layout.append("|{}".format(os.path.basename(root)))
        else:
            subject_layout.append(
                "|{} {}".format(
                    (branchlen - 1) * "---", os.path.basename(root) + os.sep
                )
            )
        for file in files:
            subject_layout.append("|{} {}".format(branchlen * "---", file))
    return subject_layout


def find_bids_file(
    datadir,
    subject_id,
    session_id,
    task_id,
    acquisition_id,
    run_id,
    kind,
    type="output",
    fragility=False,
):
    """
    Find the path to any of the metadata files.

    Parameters
    ----------
    datadir : str
    subject_id : str
    session_id : str
    task_id : str
    acquisition_id : str
    run_id : str
    kind : str
    type : str
    fragility : bool

    Returns
    -------
    str:
        Path to specified file.

    """
    if not fragility:
        if datadir is None or datadir == "derivatives":
            datadir = _get_derivatives_path()
        # subdir = os.path.join(datadir, "sub-" + subject_id)
        # sesdir = os.path.join(subdir, "ses-" + session_id)
        # kinddir = os.path.join(sesdir, kind)
        bids_fname = make_bids_basename(
            subject=subject_id,
            session=session_id,
            task=task_id,
            acquisition=acquisition_id,
            run=run_id,
            suffix=f"{kind}_output.npz",
        )
    if fragility:
        if datadir is None or datadir == "derivatives":
            datadir = _get_derivatives_path()
        # fragilitydir = os.path.join(datadir, "fragility")
        # subdir = os.path.join(fragilitydir, subject_id)
        bids_fname = make_bids_basename(
            subject=subject_id,
            session=session_id,
            task=task_id,
            acquisition=acquisition_id,
            run=run_id,
            processing="fragility",
            suffix=f"{kind}.npz",
        )
    return os.path.join(datadir, bids_fname)


def find_current_run_id(subject_id, session_id, kind, bids_root=None):
    """

    Parameters
    ----------
    subject_id :
    session_id :
    kind :
    bids_root :

    Returns
    -------

    """
    if bids_root is None:
        bids_root = _get_bidsroot_path()
    subdir = os.path.join(bids_root, "sub-" + subject_id)
    sesdir = os.path.join(subdir, "ses-" + session_id)
    kinddir = os.path.join(sesdir, kind)
    if not os.path.exists(subdir):
        warn("new subject")
        return "01"
    elif not os.path.exists(sesdir):
        warn("new session")
        return "01"
    elif not os.path.exists(kinddir):
        warn("new kind")
        return "01"
    else:
        runs = [f for f in os.listdir(kinddir) if f.endswith(".edf")]
        return str(len(runs) + 1).zfill(2)


def find_run_channels(
    subject_id,
    session_id,
    task_id,
    acquisition_id,
    run_id,
    kind,
    datadir,
    type="fragility",
    center=None,
):
    """

    Parameters
    ----------
    subject_id :
    session_id :
    task_id :
    acquisition_id :
    run_id :
    kind :
    datadir :
    type :
    center :

    Returns
    -------

    """
    # typedir = os.path.join(datadir, log_handler_type)
    # subdir = os.path.join(typedir, subject_id)
    channels_fname = make_bids_basename(
        subject=subject_id,
        session=session_id,
        task=task_id,
        acquisition=acquisition_id,
        processing=type,
        run=run_id,
        suffix=f"{kind}.json",
    )
    channels_fpath = os.path.join(datadir, channels_fname)

    channel_dict = file_to_dict(channels_fpath)
    channel_names = channel_dict["ch_names"]
    return channel_names
