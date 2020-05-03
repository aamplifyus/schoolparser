# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from eztrack.base.config.config import ClinicalContactColumns, ClinicalColumnns
from eztrack.base.utils.data_structures_utils import _expand_channels
from eztrack.cli.base.config import logger as logger


def _filter_column_name(name):
    """Hardcoded filtering of column names."""
    # strip parentheses
    name = name.split("(")[0]
    name = name.split(")")[0]

    # strip whitespace
    name = name.strip()

    return name


def _format_col_headers(df):
    """Hardcoded format of column headers."""
    df = df.apply(lambda x: x.astype(str).str.upper())
    # map all empty to nans
    df = df.fillna(np.nan)
    df = df.replace("NAN", "", regex=True)
    df = df.replace("", "n/a", regex=True)
    return df


def _expand_ch_annotations(df, cols_to_expand):
    """Regular expression expansion of channels."""
    # do some string processing to expand out contacts
    for col in cols_to_expand:
        # strip out blank spacing
        df[col] = df[col].str.strip()
        # split contacts by ";", ":", or ","
        df[col] = df[col].str.split("; |: |,")
        df[col] = df[col].map(lambda x: [y.strip() for y in x])
        df[col] = df[col].map(lambda x: [y.replace(" ", "-") for y in x])

        # expand channel labels
        df[col] = df[col].apply(lambda x: _expand_channels(x))
    return df


def read_clinical_datasheet(excel_fpath, subject=None, keep_as_df=False):
    """
    Read clinical datasheet Excel file.

    Parameters
    ----------
    excel_fpath :
    subject :
    keep_as_df :

    Returns
    -------
    df : Dict, pd.DataFrame
    """
    # load in excel file
    df = pd.read_excel(excel_fpath)

    # expand contact named columns
    # lower-case column names
    df.rename(str.upper, axis="columns", inplace=True)
    # filter column names
    column_names = df.columns
    column_mapper = {name: _filter_column_name(name) for name in column_names}
    # remove any markers (extra on clinical excel sheet)
    df.rename(columns=column_mapper, errors="raise", inplace=True)

    # format column headers
    df = _format_col_headers(df)
    # expand channel annotations
    cols_to_expand = [i.value for i in ClinicalContactColumns]
    df = _expand_ch_annotations(df, cols_to_expand=cols_to_expand)

    # remove dataframes that are still Unnamed
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # if specific subject, then read in that row
    if subject is not None:
        subject = subject.upper()
        if subject not in df[ClinicalColumnns.SUBJECT_ID.value].tolist():
            logger.error(f"Subject {subject} not in Clinical data sheet.")
            return None

        if keep_as_df:
            return df.loc[df[ClinicalColumnns.SUBJECT_ID.value] == subject]
        else:
            return df.loc[df[ClinicalColumnns.SUBJECT_ID.value] == subject].to_dict(
                "records"
            )[0]
    if keep_as_df:
        return df
    else:
        return df.to_dict("records")
