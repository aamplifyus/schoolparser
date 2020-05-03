import tempfile
from pathlib import Path

import mne
import numpy as np
import pytest
from mne_bids import read_raw_bids
from mne_bids.utils import _parse_bids_filename

from eztrack.base.data_validation.validate import (
    validate_raw_metadata,
    validate_eztrack_result,
)
from eztrack.pipeline.analysis.execute.runfrag import RunFragModel
from eztrack.pipeline.analysis.run_analysis import analyze_data
from eztrack.pipeline.visualization.run_visualization import generate_heatmap
from eztrack.preprocess.preprocess_ieeg import preprocess_ieeg


@pytest.mark.slow
@pytest.mark.usefixtures("bids_root", "bids_fname")
def test_fragilityrun(bids_root, bids_fname):
    raw = read_raw_bids(bids_fname, bids_root)
    sfreq = raw.info["sfreq"]

    # parallelized and serial analysis should be the same
    tempdir = Path("./tempdir/")
    tempdir.mkdir(exist_ok=True, parents=True)

    # set parameters
    winsize = 250
    stepsize = 125
    radius = 1.5
    perturbtype = "C"
    model_params = {
        "winsize": winsize,
        "stepsize": stepsize,
        "sfreq": 1000,
        "radius": radius,
        "perturbtype": perturbtype,
        "method_to_use": "pinv",
        "tempdir": str(tempdir),
        "numcores": 3,
    }
    rawdata = raw.get_data(return_times=False, start=0, stop=5)

    # run fragility analysis
    model = RunFragModel(**model_params)
    model.load_data(rawdata)
    numwins = model.numwins
    output_fpath = tempfile.TemporaryFile()
    _fragility_results = model.fit(parallel=True, output_fpath=output_fpath)

    output_fpath = tempfile.TemporaryFile()
    fragility_results = model.fit(parallel=False, output_fpath=output_fpath)
    for i in range(3):
        np.testing.assert_array_almost_equal(
            fragility_results[i], _fragility_results[i]
        )


@pytest.mark.slow
@pytest.mark.usefixtures("bids_root", "bids_fname")
def test_fragility_analysis_ieeg(bids_root, bids_fname):
    """Integration test for running full fragility analysis after data is preprocessed and loaded."""
    # read in raw dataset
    raw = read_raw_bids(bids_fname, bids_root)
    sfreq = raw.info["sfreq"]
    reference = "average"

    # determine kind from bids_basename
    params = _parse_bids_filename(bids_fname, verbose=False)
    kind = params["kind"]

    # preprocess the data using preprocess pipeline
    raw.info["line_freq"] = 60
    raw = preprocess_ieeg(raw, bad_chs=[])

    # verification 2.2.2 (SRS Input File Format - 7.3.2.2):
    _rawdata = np.random.random((201, 5000))
    chs = []
    for i in range(201):
        chs.append(f"ch{i}")
    _info = mne.create_info(ch_names=chs, sfreq=sfreq, ch_types="ecog")
    _raw = mne.io.RawArray(_rawdata, info=_info)
    expected_msg = (
        f"EZTrackRuntimeError: EZTrack needs to have channel count of less than 200 channels "
        f"to run in an allotted period of time. "
        f"The current dataset has {len(chs)} chs."
    )
    with pytest.raises(
        SystemExit, match=rf"{expected_msg}",
    ):
        validate_raw_metadata(_raw)

    # verification 2.2.1 (SRS Bad Channels - 7.3.2.1):
    _raw.info["bads"] = _raw.ch_names[0:5]
    expected_msg = "['ch0', 'ch1', 'ch2', 'ch3', 'ch4']"
    with pytest.raises(SystemExit, match=rf"{expected_msg}"):
        validate_raw_metadata(_raw)

    # only analyze 5 seconds
    rawdata = raw.get_data(start=0, stop=int(sfreq * 5))
    raw = mne.io.RawArray(rawdata, info=raw.info)

    # should raise an error, if there is no
    # PowerLineFrequency set
    with pytest.raises(SystemExit, match=r"EZTrackRuntimeError: Line frequency"):
        raw.info["line_freq"] = None
        raw = preprocess_ieeg(raw, bad_chs=[])

    # run fragility analysis
    with tempfile.TemporaryDirectory() as bids_root:
        output_fname = bids_fname.replace("vhdr", "npz")
        fragility_results, metadata = analyze_data(
            raw, bids_root, output_fname, reference
        )

        # test that we get the same results if already ran
        _fragility_results, _metadata = analyze_data(
            raw, bids_root, output_fname, reference
        )
        for i in range(3):
            np.testing.assert_array_almost_equal(
                fragility_results[i], _fragility_results[i]
            )

        # verification 2.3 (SRS Output File Format - 7.3.3):
        output_fpath = metadata["output_fpath"]
        assert output_fpath.endswith(".npz")
        with np.load(output_fpath) as data_dict:
            pertmats = data_dict["pertmats"]

    # verification 2.2.4 (SRS Output Data Format - 7.3.2.3):
    pertmats, adjmats, delvecs_arr = fragility_results
    pertmats = pertmats.T
    adjmats = adjmats.T
    with pytest.raises(SystemExit, match=r"EZTrackRuntimeError: End EZTrack result"):
        validate_eztrack_result(pertmats, metadata)

    # check output dimensions of fragility analysis
    pertmats, adjmats, delvecs_arr = fragility_results
    n_chs = len(raw.ch_names)
    n_wins = metadata["numwins"]
    assert pertmats.shape == (n_chs, n_wins)
    assert delvecs_arr.shape == (n_chs, n_chs, n_wins)
    assert adjmats.shape == (n_chs, n_chs, n_wins)

    # check still works if non-seizure session is used
    with tempfile.TemporaryDirectory() as bids_root:
        output_fname = output_fname.replace("seizure", "interictal")
        fragility_results, metadata = analyze_data(
            raw, bids_root, output_fname, reference
        )

    # check that visualization runs without error
    with tempfile.TemporaryDirectory() as figdir:
        fig_fname = output_fname.split(".")[0]
        ax, outputfig_fpath = generate_heatmap(
            pertmats, metadata["ch_names"], figdir, fig_fname
        )
        assert str(outputfig_fpath).endswith(".pdf")


@pytest.mark.usefixtures("bids_root", "bids_fname")
def test_ieeg_io_before_fragility(bids_root, bids_fname):
    winsize = 250
    stepsize = 125

    # test events are mapped correctly from analysis
    pass


@pytest.mark.usefixtures("bids_root", "scalp_bids_fname")
def test_fragility_analysis_eeg(bids_root, scalp_bids_fname):
    """Integration test for running full fragility analysis after data is preprocessed and loaded."""
    pass
    # read in raw dataset
    # raw = read_raw_bids(scalp_bids_fname, bids_root)
    #
    # # determine kind from bids_basename
    # params = _parse_bids_filename(scalp_bids_fname, verbose=False)
    # kind = params["kind"]
    #
    # # preprocess the data using preprocess pipeline
    # raw = preprocess_eeg(raw, bad_chs=[])
    #
    # # only analyze 5 seconds
    # sfreq = raw.info["sfreq"]
    # rawdata = raw.get_data(start=0, stop=int(sfreq * 5))
    # raw = mne.io.RawArray(rawdata, info=raw.info)
    #
    # with pytest.raises(RuntimeError):
    #     raw.info["line_freq"] = None
    #     raw = preprocess_eeg(raw, bad_chs=[])
