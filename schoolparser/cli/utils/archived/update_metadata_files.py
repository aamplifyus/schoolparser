import pandas as pd

from mne_bids import make_bids_basename

from eztrack.cli.base.config import (
    _get_bidsroot_path,
    PARTICIPANTS_COLUMNS,
    PARTICIPANTS_DESCRIPTIONS,
)

# from eegio.loaders.bids.bids_patient import BidsPatient
from eztrack.base.utils.bids_utils.bids_run import BidsRun


# def update_participants_file(subject_id, new_data):
#     """
#
#     Parameters
#     ----------
#     subject_id :
#     new_data :
#
#     """
#     bidsPatient = BidsPatient(_get_bidsroot_path, subject_id)
#     participants_fpath = bidsPatient.loader.participantstsv_fpath
#     participants_data = pd.read_csv(participants_fpath, sep="\t")
#     colnames = participants_data.columns
#     new_data_cols = new_data.columns
#     for col, desc in zip(PARTICIPANTS_COLUMNS, PARTICIPANTS_DESCRIPTIONS):
#         if col not in new_data_cols:
#             raise ValueError(
#                 f"Column {col} not in the passed data. Check default values."
#             )
#         if col not in colnames:
#             bidsPatient.add_participants_field(col, desc, new_data[col])
#         else:
#             bidsPatient.modify_participants_field(col, new_data[col])


def update_channels_file(
    subject_id, session_id, task_id, acquisition_id, run_id, new_data
):
    """

    Parameters
    ----------
    subject_id :
    session_id :
    task_id :
    acquisition_id :
    run_id :
    new_data :

    """
    colnames = new_data.columns
    for col in colnames:
        new_data[col] = new_data[col].str.lower()

    bids_fname = make_bids_basename(
        subject=subject_id,
        session=session_id,
        task=task_id,
        acquisition=acquisition_id,
        run=run_id,
    )
    bidsRun = BidsRun(_get_bidsroot_path(), bids_fname)
    current_run_channels = bidsRun.get_channels_metadata()
    for ind, row in new_data.iterrows():
        for sind, val in row.items():
            if "bad" in val:
                bad_channel = ind + sind
                bidsRun.modify_channel_info("status", bad_channel, "bad")
                if "description" not in current_run_channels[0].keys():
                    bidsRun.append_channel_info("description", bad_channel, "bad")
                else:
                    bidsRun.modify_channel_info("description", bad_channel, "bad")
            elif "wm" in val:
                bad_channel = ind + sind
                bidsRun.modify_channel_info("status", bad_channel, "bad")
                if "description" not in current_run_channels[0].keys():
                    bidsRun.append_channel_info("description", bad_channel, "WM")
                else:
                    bidsRun.modify_channel_info("description", bad_channel, "WM")
            elif "out" in val:
                bad_channel = ind + sind
                bidsRun.modify_channel_info("status", bad_channel, "bad")
                if "description" not in current_run_channels[0].keys():
                    bidsRun.append_channel_info("description", bad_channel, "out")
                else:
                    bidsRun.modify_channel_info("description", bad_channel, "out")
            elif "csf" in val:
                bad_channel = ind + sind
                bidsRun.modify_channel_info("status", bad_channel, "bad")
                if "description" not in current_run_channels[0].keys():
                    bidsRun.append_channel_info("description", bad_channel, "csf")
                else:
                    bidsRun.modify_channel_info("description", bad_channel, "csf")
            elif "ventricle" in val:
                bad_channel = ind + sind
                bidsRun.modify_channel_info("status", bad_channel, "bad")
                if "description" not in current_run_channels[0].keys():
                    bidsRun.append_channel_info("description", bad_channel, "ventricle")
                else:
                    bidsRun.modify_channel_info("description", bad_channel, "ventricle")
            else:
                channel = ind + sind
                if "description" not in current_run_channels[0].keys():
                    bidsRun.append_channel_info("description", channel, val)
                else:
                    bidsRun.modify_channel_info("description", channel, val)
