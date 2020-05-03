from pathlib import Path
from typing import Union

from mne_bids import read_raw_bids, make_bids_basename
from mne_bids.utils import (
    _parse_bids_filename,
    _handle_kind,
)
from natsort import natsorted

from eztrack.base.data_validation.validate import (
    validate_raw_metadata,
    validate_eztrack_result,
)
from eztrack.pipeline.analysis.run_analysis import analyze_data
from eztrack.pipeline.visualization.run_visualization import main_draw_heatmap
from eztrack.preprocess.preprocess_eeg import preprocess_eeg
from eztrack.preprocess.preprocess_ieeg import preprocess_ieeg


def setup_fragility(
    subject_id: str,
    acquisition_id: str,
    run_id: str,
    kind: str,
    bids_root: Union[str, Path],
    reference: str,
    deriv_path: Union[str, Path] = None,
    overwrite: bool = False,
):
    """
    Setup fragility parameters and files to run analysis.

    Parameters
    ----------
    subject_id :
    acquisition_id:
    run_id :
    bids_root :
    reference :
    deriv_path :
    overwrite : bool

    Returns
    -------
    deriv_path:
    """

    verbose = False
    # initialize a pybids layout
    # layout = bids.BIDSLayout(bids_root)
    # subj_runs = layout.get_runs(subject=subject_id)

    # get all the subject runs
    subj_dir = Path(bids_root / f"sub-{subject_id}")
    _fnames = natsorted(
        [
            x.name
            for x in subj_dir.rglob(f"*run-{run_id}_{kind}.vhdr")
            if acquisition_id in x.name
        ]
    )

    # run analysis
    for bids_fname in _fnames:
        params = _parse_bids_filename(bids_fname, verbose=verbose)
        subject = params["sub"]
        session = params["ses"]
        task = params["task"]
        acquisition = params["acq"]
        run_id = params["run"]
        output_fname = make_bids_basename(
            subject,
            session,
            task,
            acquisition,
            run_id,
            processing="fragility",
            suffix=f"{kind}.npz",
        )
        deriv_path = main(
            bids_fname,
            bids_root,
            output_fname,
            reference,
            deriv_path=deriv_path,
            verbose=verbose,
            overwrite=overwrite,
        )
    return deriv_path


def main(
    bids_fname,
    bids_root,
    output_fname,
    reference,
    deriv_path=None,
    verbose=False,
    overwrite=False,
):
    """
    Run an Example EZTrack core analysis.

    Parameters
    ----------
    bids_fname : str
        The full basename of the bids file, resulting from make_bids_basename
    bids_root : Union[str or Path]
        The base directory where the bids data is stored
    output_fname : str
        The name of the output file
    verbose : bool
        Whether to display output
    overwrite: bool
        Whether to overwrite existing output

    """
    # determine kind from bids_basename
    params = _parse_bids_filename(bids_fname, verbose=verbose)
    acquisition = params["acq"]
    subject = params["sub"]

    # load the data
    raw = read_raw_bids(bids_fname, bids_root, verbose=verbose)

    # get rid of bad ch_names
    raw.load_data()
    bad_chs = raw.info["bads"]
    raw = raw.drop_channels(bad_chs)

    # determine kind from the raw input
    kind = _handle_kind(raw)
    # only keep EEG/SEEG channel
    pick_dict = {f"{acquisition}": True}
    raw = raw.pick_types(**pick_dict)

    # preprocess the data using preprocess pipeline
    if kind == "eeg":
        raw = preprocess_eeg(raw, bad_chs=[])
    elif kind == "ieeg":
        raw = preprocess_ieeg(raw, bad_chs=[])

    # validation checks on raw data
    validate_raw_metadata(raw)

    # run fragility analysis
    if deriv_path is None:
        deriv_path = Path(
            Path(bids_root) / "derivatives" / "fragility" / reference / subject
        )
    fragility_results, metadata = analyze_data(
        raw,
        deriv_path,
        output_fname,
        reference=reference,
        overwrite=overwrite,
        verbose=verbose,
    )
    pertmats, adjmats, delvecs_array = fragility_results  # extract results from tuple

    # run validation checks on fragility output
    validate_eztrack_result(pertmats, metadata)

    # draw heatmap
    main_draw_heatmap(deriv_path, output_fname)

    return deriv_path
