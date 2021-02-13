import collections
import datetime
from typing import Dict

import pandas as pd


def scraped_emails_to_df(emails: Dict, output_fpath: str = None) -> pd.DataFrame:
    """Convert scraped emails (dictionary of lists) to Dataframe.

    Parameters
    ----------
    emails : dict
    output_fpath : str | pathlib.Path

    Returns
    -------
    school_df : pd.DataFrame
        School dataframe of ``school`` (school associated),
        ``url`` (url that was accessed), ``email`` (scraped email address),
        and ``date`` (date generated).
    """
    # generate list of dictionaries
    rows = []
    for school, url_list in emails.items():
        for url, email_list in url_list.items():
            for email in email_list:
                row = collections.OrderedDict()
                row["school"] = school
                row["url"] = url
                row["email"] = email
                row["date"] = datetime.datetime.now()
                rows.append(row)

    # create the dataframe
    school_df = pd.DataFrame(rows)
    school_df["Owner"] = ""
    school_df["Notes"] = ""

    print(school_df)
    if output_fpath is not None:
        school_df.to_excel(output_fpath, index=None)
    return school_df
