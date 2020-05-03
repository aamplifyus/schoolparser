import os
from pathlib import Path

import click
import numpy as np

from eztrack.base.metrics.metrics import timed
from eztrack.base.utils.normalizations import Normalize
from eztrack.cli.base.config import _get_bidsroot_path, help_colors
from eztrack.cli.base.config import logger as logger
from eztrack.cli.utils.check_params import _check_runfunc_params
from eztrack.cli.utils.find_file import (
    find_bids_run_file,
    find_run_channels,
    find_bids_file,
)
from eztrack.cli.utils.runFrag_analysis import setup_fragility
from eztrack.cli.utils.utils import clear_screen
from eztrack.visualize.plot_fragility_heatmap import PlotFragilityHeatmap


@click.command(**help_colors)
@click.pass_context
@click.option(
    "--subject_id",
    type=str,
    default=None,
    required=False,
    help="Unique EZTrack identifier for the subject",
)
@click.option(
    "--session_id",
    type=str,
    default="seizure",
    required=False,
    help="Unique identifier for the recording session",
)
@click.option(
    "--task_id",
    type=str,
    default="monitor",
    required=False,
    help="What the subject was doing during the recording. Default is monitor",
)
@click.option(
    "--acquisition_id",
    type=str,
    default="ecog",
    required=False,
    help="The log_handler_type of acquisition, from ecog, seeg, or eeg. Default is ecog",
)
@click.option(
    "--run_id",
    type=str,
    default=None,
    required=False,
    help='The run number for the session with two digits (i.e. "01")',
)
@click.option(
    "--reference",
    type=click.Choice(["monopolar", "average"]),
    default="monopolar",
    required=False,
    help="The log_handler_type of reference used. Default is monopolar",
)
@click.option(
    "--overwrite",
    type=bool,
    default=False,
    required=False,
    help="True if you want to overwrite the existing results",
)
@click.option(
    "--colorblind",
    type=bool,
    default=False,
    required=False,
    help="True if you want a colorblind-accessible heatmap",
)
@timed
def run(
    ctx,
    subject_id,
    session_id,
    task_id,
    acquisition_id,
    run_id,
    reference,
    overwrite,
    colorblind,
    clear=True,
):
    """
    Run the fragility analysis on a given subject's EEG snapshot.

    subject_id, session_id, and run_id are required.

    Command Format:
    ez run --subject_id <subject_id> --session_id <session_id> --run_id <run_id>

    """
    # Prompt for arguments not passed
    if clear:
        clear_screen()

    # perform a dynamic check on parameters passed in
    # to give user an insightful feedback
    run_params = {
        "subject_id": subject_id,
        "session_id": session_id,
        "acquisition_id": acquisition_id,
        "run_id": run_id,
    }
    _check_runfunc_params(run_params, "run")
    logger.info(
        f"ez run with subject_id: {subject_id}, session_id: {session_id}, task_id: {task_id},"
        f"acquisition_id: {acquisition_id}, run_id: {run_id}, reference: {reference}, "
        f"overwrite: {overwrite}, colorblind: {colorblind}"
    )

    # determine kind from acquisition.
    if acquisition_id in ["ecog", "seeg"]:
        kind = "ieeg"
    elif acquisition_id == "eeg":
        kind = "eeg"
    ext = "vhdr"  # files need to be in BV format

    # initialize bids_root and derivatives directories
    bids_root = _get_bidsroot_path()
    # output_path = _get_derivatives_path

    # find the bids run file
    bids_root, bids_fname, datapath = find_bids_run_file(
        subject_id=subject_id,
        session_id=session_id,
        task_id=task_id,
        acquisition_id=acquisition_id,
        run_id=run_id,
        kind=kind,
        datadir=bids_root,
        ext=ext,
    )

    # run fragility analysis
    click.echo(f"Analyzing fragility for the file {datapath}...")
    deriv_path = setup_fragility(
        subject_id,
        acquisition_id,
        run_id,
        kind,
        Path(bids_root),
        reference,
        overwrite=overwrite,
    )
    # click.echo(f"Analysis complete. Results saved in {deriv_path}...")
    logger.info("Analysis complete. Plotting.")
    click.echo("Analysis complete. Plotting.")
    plot_params = {
        "subject_id": subject_id,
        "session_id": session_id,
        "task_id": task_id,
        "acquisition_id": acquisition_id,
        "run_id": run_id,
        "kind": kind,
        "datadir": deriv_path,
    }

    ch_names = find_run_channels(**plot_params)

    # Make sure the channels is in a list
    if isinstance(ch_names, str):
        channels = ch_names.split(",")

    # Find the output .npz file
    output_fname = find_bids_file(
        deriv_path,
        subject_id,
        session_id,
        task_id,
        acquisition_id,
        run_id,
        kind,
        "output",
        True,
    )
    # Create the filename
    fig_name = output_fname.replace(".npz", "_heatmap.pdf")
    results = np.load(output_fname)
    pertmats = results["pertmats"]
    # TODO: remove once version is stable
    if pertmats.shape[1] == len(ch_names):
        pertmats = pertmats.T

    # Normalize the perturbation matrix
    fragmat = Normalize.compute_fragilitymetric(pertmats)

    # Plot the heatmap with save on
    plotter = PlotFragilityHeatmap(figure_dir=os.path.dirname(output_fname))
    plotter.plot_fragility_heatmap(
        fragmat, ch_names, colorblind=colorblind, output_fpath=fig_name, fontsize=16
    )
    logger.info("Plotting finished")
    click.echo("Plotting finished!")
