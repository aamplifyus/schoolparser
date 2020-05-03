import os
from pathlib import Path

import click
import numpy as np

from eztrack.base.metrics.metrics import timed, counted
from eztrack.base.utils.normalizations import Normalize
from eztrack.cli.base.config import _get_derivatives_path, help_colors
from eztrack.cli.base.config import logger as logger
from eztrack.cli.utils.check_params import _check_runfunc_params
from eztrack.cli.utils.find_file import find_bids_file, find_run_channels
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
    "--colorblind",
    type=bool,
    default=False,
    required=False,
    help="True if you want a colorblind-accessible heatmap",
)
@click.option(
    "--reference",
    type=click.Choice(["monopolar", "average"]),
    default="monopolar",
    required=False,
    help="The log_handler_type of reference used. Default is monopolar",
)
@click.option(
    "--ext",
    type=click.Choice(["pdf", "png"]),
    default="pdf",
    required=False,
    help="The file extension of the saved figure. Default is pdf",
)
@click.option(
    "--cmap",
    type=str,
    default=None,
    required=False,
    help="The matplotlib.pyplot colormap code. This is a more advanced option.",
)
@timed
def plot(
    ctx,
    subject_id,
    session_id,
    task_id,
    acquisition_id,
    run_id,
    colorblind,
    reference,
    ext,
    cmap,
    clear=True,
):
    """
    Display the heatmap from the fragility analysis.


    .. code-block:: python
        ez plot --subject_id=<subject_id> --run_id=<run_id>
    """
    if clear:
        clear_screen()

    plot_params = {
        "subject_id": subject_id,
        "session_id": session_id,
        "acquisition_id": acquisition_id,
        "run_id": run_id,
        "colorblind": colorblind,
        "cmap": cmap,
    }
    _check_runfunc_params(plot_params, "plot")
    del plot_params["colorblind"]
    del plot_params["cmap"]

    logger.info(
        f"ez plot with subject_id: {subject_id}, session_id: {session_id}, task_id: {task_id},"
        f"acquisition_id: {acquisition_id}, run_id: {run_id}, colorblind: {colorblind}, "
        f"reference: {reference}, ext: {ext}, cmap: {cmap}"
    )
    counted("replotting")

    if "ecog" in acquisition_id or "seeg" in acquisition_id:
        kind = "ieeg"
    elif "eeg" in acquisition_id:
        kind = "eeg"

    # output_path = _get_derivatives_path
    deriv_path = Path(_get_derivatives_path() / "fragility" / reference / subject_id)

    plot_params["task_id"] = task_id
    plot_params["kind"] = kind
    plot_params["datadir"] = deriv_path
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
    fig_name = output_fname.replace(".npz", f"_heatmap.{ext}")
    fig_name = os.path.join(
        os.path.dirname(fig_name), "figures", os.path.basename(fig_name)
    )
    results = np.load(output_fname)
    pertmats = results["pertmats"]
    if pertmats.shape[1] == len(ch_names):
        pertmats = pertmats.T

    # Normalize the perturbation matrix
    fragmat = Normalize.compute_fragilitymetric(pertmats)

    # Plot the heatmap with save on
    plotter = PlotFragilityHeatmap(
        figure_dir=os.path.join(os.path.dirname(output_fname), "figures")
    )
    plotter.plot_fragility_heatmap(
        fragmat,
        ch_names,
        colorblind=colorblind,
        cmap=cmap,
        output_fpath=fig_name,
        fontsize=16,
    )
    logger.info("Plotting completed")
    click.echo("Plotting finished!")
