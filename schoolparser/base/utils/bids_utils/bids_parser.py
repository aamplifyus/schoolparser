"""
Authors: Adam Li and Patrick Myers.

Version: 1.0
"""
import os
from pathlib import Path

from bids import BIDSLayout
from mne_bids import make_bids_basename

from .basebids import BaseBids


class BidsParser(BaseBids):
    """
    Parse subject and session level bids directory.

    """

    def __init__(self, bids_root, subject_id: str):
        super(BidsParser, self).__init__(bids_root=bids_root)

        # ensures just base path
        self.subject_id = subject_id
        self.bids_root = bids_root
        self.subject_dir = Path(os.path.join(self.bids_root, "sub-" + self.subject_id))
        self.sessions = [
            os.path.basename(f) for f in os.scandir(self.subject_dir) if f.is_dir()
        ]

    def get_acquisitions(self):
        layout = BIDSLayout(self.bids_root)
        acquisition_ids = layout.get_acquisitions(subject=self.subject_id)
        return acquisition_ids

    def get_scans_fpaths(self):
        """

        Returns
        -------

        """
        scans_fpaths = []
        for ses in self.sessions:
            ses_id = ses.split("-")[-1]
            scan_fpath = make_bids_basename(
                subject=self.subject_id,
                session=ses_id,
                suffix="scans.tsv",
                prefix=os.path.join(self.bids_root, self.subject_dir, "ses-" + ses_id),
            )
            scans_fpaths.append(scan_fpath)
        return scans_fpaths
