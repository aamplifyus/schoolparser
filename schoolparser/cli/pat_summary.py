import os
from pathlib import Path

import click
import pandas as pd
from mne_bids.tsv_handler import _from_tsv
from mne_bids.utils import _find_matching_sidecar

from eztrack.base.metrics.metrics import timed
from eztrack.base.utils.bids_utils.basebids import BaseBids
from eztrack.base.utils.bids_utils.bids_parser import BidsParser
from eztrack.cli.base.config import _get_bidsroot_path, help_colors
from eztrack.cli.base.config import logger as logger
from eztrack.cli.utils.check_params import _check_metadatafunc_params
from eztrack.cli.utils.convert_dict import file_to_dict, split_dict
from eztrack.cli.utils.utils import clear_screen, _linebreak


def _populate_summary_dict(summ_dict, filenames, bids_root):
    for j, filename in enumerate(filenames):
        bids_fname, scan_ext = os.path.splitext(filename)
        sidecar_fpath = _find_matching_sidecar(
            bids_fname=bids_fname, suffix="json", bids_root=bids_root
        )
        sidecar_dict = file_to_dict(sidecar_fpath)

        if j == 0:
            for key, value in sidecar_dict.items():
                sidecar_dict[key] = [sidecar_dict[key]]
            summ_dict.update(sidecar_dict)
        else:
            for key, value in sidecar_dict.items():
                try:
                    summ_dict[key].append(value)
                except (KeyError):
                    summ_dict.update({key: value})


@click.command(**help_colors)
@click.pass_context
@click.option(
    "--subject_id",
    type=str,
    default="all",
    help="Unique EZTrack identifier for the subject",
)
@timed
def pat_summary(ctx, subject_id, clear=True):
    """
    Display the summary data for a certain patient, or all patients.

    If subject_id not specified, or listed as all, will simply print metadata again.

    Command Format:
    ez pat-summary --subject_id <subject_id>

    """
    if clear:
        clear_screen()

    summary_params = {"subject_id": subject_id}
    _check_metadatafunc_params(summary_params, "pat-summary")
    logger.info(f"ez pat-summary with subject_id: {subject_id}")

    # faster using os.glob if too many subjects - compared pybids
    bids_root = Path(_get_bidsroot_path())

    # read in participants.tsv file and display to user
    bids_parser = BaseBids(bids_root)
    participants_tsv = _from_tsv(bids_parser.participants_tsv_fpath)
    participants_df = pd.DataFrame.from_dict(participants_tsv)

    # summarize all patients
    if subject_id == "all":
        click.echo("All Subjects Summary:")
        click.echo(participants_df)

    # summarize a specific patient
    if subject_id is not None and subject_id != "all":
        # set display options for the pandas dataframes
        pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        pd.options.display.max_colwidth = 500

        # find the location of the scans file
        subj_bids_parser = BidsParser(bids_root, subject_id)
        scans_fpaths = subj_bids_parser.get_scans_fpaths()

        # for each set of scans files, print out summary data
        for i, scans_fpath in enumerate(scans_fpaths):
            # read in scans.tsv for each subject
            scans_tsv = _from_tsv(scans_fpath)
            # get the scans sidecar dictionaries for eeg and ieeg data
            eeg_dict, ieeg_dict = split_dict(scans_tsv)

            # load in files and their corresponding sidecar info
            # and add it to the summary dictionaries
            _populate_summary_dict(eeg_dict, eeg_dict["filename"], bids_root)
            _populate_summary_dict(ieeg_dict, ieeg_dict["filename"], bids_root)

        # summarize a specific subject
        participants_df = participants_df.loc[
            participants_df["participant_id"] == f"sub-{subject_id}"
        ]
        click.echo(f"Subject {subject_id} Summary:")
        click.echo(participants_df)

        message_str = "\n\nSummary of Snapshots for %s" % subject_id
        click.echo(message_str)
        click.echo(_linebreak(message_str))

        ###################################################
        # Display the summary for either EEG,  or iEEG data.
        ###################################################
        if eeg_dict["filename"] == []:
            message_str = "No scalp EEG data to summarize."
            click.echo(message_str)
            click.echo(_linebreak(message_str))
        else:
            message_str = "EEG data summary."
            click.echo(message_str)
            click.echo(_linebreak(message_str))
            eeg_df = pd.DataFrame.from_dict(eeg_dict)
            click.echo(eeg_df)

        if ieeg_dict["filename"] == []:
            message_str = "No iEEG data to summarize."
            click.echo(message_str)
            click.echo(_linebreak(message_str))
        else:
            message_str = "iEEG data summary."
            click.echo(message_str)
            click.echo(_linebreak(message_str))
            ieeg_df = pd.DataFrame.from_dict(ieeg_dict)
            click.echo(ieeg_df)
