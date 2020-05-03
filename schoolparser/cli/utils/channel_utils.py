import re

import click
from mne_bids.tsv_handler import _from_tsv

from eztrack.base.utils.file_utils import _get_subject_channels_tsvs
from eztrack.cli.base.config import logger as logger


def print_channel_status(bids_root, subject_id, session_id, acquisition_id):
    """
    Print the channel and status of every channel for a certain acquisition type.

    Parameters
    ----------
    bids_root : Union[Path or str]
        The directory where data is being stored.
    subject_id : str
        The unique identifier of the subject
    session_id: str
        The identifier of the recording session, usually 'seizure' or 'interictal'
    acquisition_id : str
        One of 'eeg', 'ecog', or 'seeg'

    """
    channel_fpaths = _get_subject_channels_tsvs(
        bids_root, subject_id, session_id, acquisition_id
    )
    logger.info(f"Found channel files for subject {subject_id}: {channel_fpaths}")
    if len(channel_fpaths) == 0:
        logger.error(f"No channel files for subject: {subject_id}")
        raise RuntimeError(f"No channel files for subject: {subject_id}.")
    channel_fpath = channel_fpaths[0]
    logger.info(f"Using channel file '{channel_fpath}'")

    # Read in current channel statuses
    channel_tsv = _from_tsv(channel_fpath)
    bad_chs = []
    good_chs = []
    for i, ch in enumerate(channel_tsv["name"]):
        if channel_tsv["status"][i] == "bad":
            bad_chs.append(ch)
        else:
            good_chs.append(ch)

    # create string of channels to display to user
    if len(bad_chs) == 0:
        bad_channels_str = "None"
    else:
        bad_channels_str = ", ".join(bad_chs)
    if len(bad_chs) == 0:
        good_channels_str = "None"
    else:
        good_channels_str = ", ".join(good_chs)

    click.echo(f"Bad channels for {subject_id}:")
    click.echo(bad_channels_str)
    click.echo(f"Channels included in analysis for {subject_id}:")
    click.echo(good_channels_str)


def channels_to_list(channel_string):
    """
    Convert a string of a channel list into a list.

    Parameters
    ----------
    channel_string : str
        The list of channels, separated by commas, spaces, and/or semicolons

    Returns
    -------
    channel_list: list[str]
        The list object of channels

    """
    channel_string = channel_string.replace(" ", "")
    channel_list = re.split(";|,|; |, ", channel_string)
    channel_list = [ch.upper() for ch in channel_list]
    return channel_list
