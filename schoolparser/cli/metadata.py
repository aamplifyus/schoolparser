from pathlib import Path

import pandas as pd
import click
from bids import BIDSLayout
from mne_bids.tsv_handler import _from_tsv

from eztrack.base.metrics.metrics import timed
from eztrack.base.utils.bids_utils.basebids import BaseBids
from eztrack.base.utils.bids_utils.bids_parser import BidsParser
from eztrack.cli.base.config import _get_bidsroot_path, help_colors
from eztrack.cli.base.config import logger as logger
from eztrack.cli.utils.filter import filter_metadata
from eztrack.cli.utils.utils import clear_screen, _linebreak, _extract_run


@click.command(**help_colors)
@click.pass_context
@click.argument("toggle_options", nargs=-1, type=str, required=False)
@click.option(
    "--display_cols",
    type=bool,
    default=False,
    required=False,
    help="True if you want to print out the filterable columns.",
)
@timed
def metadata(ctx, toggle_options, display_cols, clear=True):
    """
    Display (filtered) metadata to the terminal.

    Metadata needs no arguments, unless you wish to see a subset of the entire patient set. When this is desired, use
    the toggle options. For instance, the below command will display only male subjects over age 20:

        ez metadata 'sex=M' 'age>20'

    """
    if clear:
        clear_screen()

    baseBids = BaseBids(_get_bidsroot_path())
    participants_path = baseBids.participants_tsv_fpath
    dateparse = lambda x: pd.datetime.strptime(x, "%m/%d/%y")
    participants_df = pd.read_csv(
        participants_path, sep="\t", parse_dates=True, date_parser=dateparse
    )

    # Print out the column names only
    if display_cols:
        click.echo(f"Available columns and types: \n {participants_df.dtypes}")
        return

    participants_df, cols, bools, keys = filter_metadata(
        participants_df, toggle_options
    )
    toggle_count = len(cols)

    sub_ids = participants_df["participant_id"]
    subject_ids = []
    for sub in sub_ids:
        sub_id = sub.split("-")[1]
        subject_ids.append(sub_id)

    # display meessage and logger output
    click.echo("Displaying Subjects: " + ", ".join(subject_ids))
    info_msg = f"{toggle_count} filters: {', '.join(''.join(x) for x in zip(cols, bools, keys))}"
    logger.info(f"ez metadata with {info_msg}")

    # define layout using pybids
    layout = BIDSLayout(_get_bidsroot_path())
    # subject_ids = layout.get_subjects()
    # faster using os.glob if too many subjects
    bids_root = Path(_get_bidsroot_path())

    # for each subject, display metadata
    # query for sessions, tasks and acquisitions before run_ids
    for ind, subject in enumerate(subject_ids):
        subj_bids_parser = BidsParser(bids_root, subject)
        scans_fpaths = subj_bids_parser.get_scans_fpaths()
        acquisition_ids = subj_bids_parser.get_acquisitions()

        # display summary for each acquisition
        for acquisition in acquisition_ids:
            # get the file paths to datasets
            _fpaths = [
                x.as_posix() for x in Path(bids_root / f"sub-{subject}").rglob("*.vhdr")
            ]
            _fpaths = [x for x in _fpaths if acquisition in x]

            # extract run
            run_ids = [_extract_run(x) for x in _fpaths]
            run_ids = ",".join(run_ids)

            # display message to user about subject, their metadata, acquisition and run_ids
            message_str = (
                f"Subject ID: {subject} - {', '.join([x + ': ' + str(participants_df.at[ind + 1, x]) for x in cols])} \n"
                f"{acquisition} run_ids: {run_ids} \n"
                f"Here is a table of each dataset:"
            )
            click.echo(_linebreak(message_str))
            click.echo(message_str)

            # display summary for all datasets with this acquisition
            for scans_fpath in scans_fpaths:
                pd.options.display.max_colwidth = 90
                # read in scans.tsv for each subject
                scans_tsv = _from_tsv(scans_fpath)
                scans_df = pd.DataFrame.from_dict(scans_tsv)
                acquisition_scans = scans_df["filename"].str.contains(acquisition)
                scans_df = scans_df[acquisition_scans]
                click.echo(scans_df)
