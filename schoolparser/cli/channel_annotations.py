from pathlib import Path

import click

from eztrack.base.metrics.metrics import timed
from eztrack.cli.base.config import _get_bidsroot_path, help_colors
from eztrack.cli.base.config import logger as logger
from eztrack.cli.utils.channel_utils import print_channel_status, channels_to_list
from eztrack.cli.utils.check_params import _check_annotatechannelfunc_params
from eztrack.cli.utils.utils import clear_screen
from eztrack.pipeline.preprocess.run_add_bad_channels import add_bad_chs, remove_bad_chs


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
    "--chs",
    type=str,
    default=None,
    required=False,
    help='A comma, semicolon, or space separated list of channels (i.e. "A1, A2, A3")',
)
@click.option(
    "--session_id",
    type=str,
    default="seizure",
    required=False,
    help="Unique identifier for the recording session",
)
@click.option(
    "--acquisition_id",
    type=str,
    default="ecog",
    required=False,
    help="The log_handler_type of acquisition, from ecog, seeg, or eeg. Default is ecog",
)
@timed
def annotate_bad_chs(ctx, subject_id, chs, session_id, acquisition_id):
    """
    Annotate (remove) channels from analysis.

    Command Format:
    ez annotate_bad_chs --subject_id <subject_id> --chs <chs> --session_id <session_id>
    --acquisition_id <acquisition_id>

    """
    clear_screen()
    input_params = {
        "subject_id": subject_id,
        "chs": chs,
        "session_id": session_id,
        "acquisition_id": acquisition_id,
    }
    _check_annotatechannelfunc_params(input_params, "annotate_bad_chs")
    logger.info(
        f"ez annotate_bad_chs with subject_id: {subject_id}, chs: {chs}, "
        f"session_id: {session_id}, and acquisition_id: {acquisition_id}"
    )
    bids_root = Path(_get_bidsroot_path())
    if acquisition_id is None:
        acquisition_ids = ["ecog", "seeg"]
        # _get_subject_acquisitions(bids_root, subject_id, session_id)
    else:
        acquisition_ids = [acquisition_id]

    for acquisition_id in acquisition_ids:
        bad_channels = channels_to_list(chs)
        add_bad_chs(bids_root, subject_id, session_id, acquisition_id, bad_channels)


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
    "--chs",
    type=str,
    default=None,
    required=False,
    help='A comma, semicolon, or space separated list of channels (i.e. "A1, A2, A3")',
)
@click.option(
    "--session_id",
    type=str,
    default="seizure",
    required=False,
    help="Unique identifier for the recording session",
)
@click.option(
    "--acquisition_id",
    type=str,
    default="ecog",
    required=False,
    help="The log_handler_type of acquisition, from ecog, seeg, or eeg. Default is ecog",
)
@timed
def delete_bad_chs(ctx, subject_id, chs, session_id, acquisition_id):
    """
    Annotate (add) channels to analysis.

    Command Format:
    ez annotate_bad_chs --subject_id <subject_id> --chs <chs> --session_id <session_id>
    --acquisition_id <acquisition_id>

    """
    clear_screen()
    input_params = {
        "subject_id": subject_id,
        "chs": chs,
        "session_id": session_id,
        "acquisition_id": acquisition_id,
    }
    _check_annotatechannelfunc_params(input_params, "delete_bad_chs")
    logger.info(
        f"ez delete_bad_chs with subject_id: {subject_id}, chs: {chs}, "
        f"session_id: {session_id}, and acquisition_id: {acquisition_id}"
    )
    bids_root = Path(_get_bidsroot_path())
    if acquisition_id is None:
        acquisition_ids = ["ecog", "seeg"]
        # _get_subject_acquisitions(bids_root, subject_id, session_id)
    else:
        acquisition_ids = [acquisition_id]

    for acquisition_id in acquisition_ids:
        good_channels = channels_to_list(chs)
        logger.info(
            f"removing {good_channels} from the bad channel list for {subject_id}'s {acquisition_id} "
            f"session {session_id}"
        )
        remove_bad_chs(bids_root, subject_id, session_id, acquisition_id, good_channels)


# @click_log.simple_verbosity_option(logger)
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
    "--acquisition_id",
    type=str,
    default="ecog",
    required=False,
    help="The log_handler_type of acquisition, from ecog, seeg, or eeg. Default is ecog",
)
@timed
def view_bad_chs(ctx, subject_id, session_id, acquisition_id):
    """Print bad channels for a specific subject.

    Command Format:
    ez view_bad_chs --subject_id <subject_id> --session_id <session_id> --acquisition_id <acquisition_id>

    """
    clear_screen()
    input_params = {
        "subject_id": subject_id,
        "session_id": session_id,
        "acquisition_id": acquisition_id,
    }
    _check_annotatechannelfunc_params(input_params, "view_bad_chs")
    logger.info(
        f"ez view_bad_chs with subject_id: {subject_id}, "
        f"session_id: {session_id}, and acquisition_id: {acquisition_id}"
    )
    bids_root = Path(_get_bidsroot_path())
    print_channel_status(bids_root, subject_id, session_id, acquisition_id)
