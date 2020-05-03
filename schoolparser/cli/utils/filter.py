from datetime import datetime

from eztrack.base.metrics.metrics import counted
from eztrack.cli.base.config import logger as logger
from eztrack.cli.utils.check_params import CLI_Input_Error


def filter_metadata(participants_df, toggle_options):
    """Filter metadata dataframe to rows with subjects meeting requirements."""
    cols = []
    bools = []
    keys = []
    toggle_count = 0
    # If there are filters, otherwise just returns the original dataframe
    for opt in toggle_options:
        toggle_count += 1
        # Remove any spaces the user may have enter
        opt = opt.replace(" ", "")
        # Check for equality option (i.e. sex = M)
        equals = opt.split("=")
        # If len == 2, then it was an equality
        if len(equals) == 2:
            col = equals[0]
            key = equals[1]
            cols.append(col)
            bools.append("=")
            keys.append(key)
            # Make sure the search column actually exists
            try:
                valid_col = participants_df[col]
            except KeyError:
                logger.error("{col} is not a valid option in metadata.")
                counted("CLI_exception")
                raise CLI_Input_Error(
                    f"{col} is not a valid option in metadata. \n Available columns and types"
                    f"are: \n{participants_df.dtypes}"
                )
            # Check to make sure the types match. i.e. sex > 22 makes no sense
            boolmeta = _check_types(participants_df, col, key, "=")
            # filter based on the columns
            participants_df = participants_df[boolmeta]
        # Check for greater than option (i.e. age > 22)
        greater = opt.split(">")
        if len(greater) == 2:
            col = greater[0]
            key = greater[1]
            cols.append(col)
            bools.append(">")
            keys.append(key)
            try:
                valid_col = participants_df[col]
            except KeyError:
                logger.error("{col} is not a valid option in metadata.")
                counted("CLI_exception")
                raise CLI_Input_Error(
                    f"{col} is not a valid option in metadata. \n Available columns and types "
                    f"are: {participants_df.dtypes}"
                )
            boolmeta = _check_types(participants_df, col, key, ">")
            participants_df = participants_df[boolmeta]
        # Check for less than option (i.e. age < 40)
        less = opt.split("<")
        if len(less) == 2:
            col = less[0]
            key = less[1]
            cols.append(col)
            bools.append("<")
            keys.append(key)
            try:
                valid_col = participants_df[col]
            except KeyError:
                logger.error("{col} is not a valid option in metadata.")
                counted("CLI_exception")
                raise CLI_Input_Error(
                    f"{col} is not a valid option in metadata. \n Available columns and types "
                    f"are: {participants_df.dtypes}"
                )
            boolmeta = _check_types(participants_df, col, key, "<")
            participants_df = participants_df[boolmeta]

    return participants_df, cols, bools, keys


def _check_types(df, col, key, ineq):
    if df.dtypes[col] == "int64":
        try:
            if ineq == ">":
                boolmeta = df[col] > int(key)
            elif ineq == "<":
                boolmeta = df[col] < int(key)
            else:
                boolmeta = df[col] == int(key)
            return boolmeta
        except ValueError as ex:
            logger.error(f"Column {col} has type int, but {key} was passed")
            counted("CLI_exception")
            raise CLI_Input_Error(
                f"Column {col} has type int. Please pass in a valid int"
            )
    elif df.dtypes[col] is "datetime":
        try:
            if ineq == ">":
                boolmeta = df[col] > datetime.strptime(key, format="%m/%d/%Y")
            elif ineq == "<":
                boolmeta = df[col] < datetime.strptime(key, format="%m/%d/%Y")
            else:
                boolmeta = df[col] == datetime.strptime(key, format="%m/%d/%Y")
            return boolmeta
        except ValueError as ex:
            logger.error(
                f"Column {col} has type datetime with format mm/dd/YYYY, but {key} was passed"
            )
            counted("CLI_exception")
            raise CLI_Input_Error(
                f"Column {col} has type datetime. Please pass in a valid datetime with format"
                f"mm/dd/YYYY"
            )
    else:
        # otherwise it is a str
        if ineq == "<" or ineq == ">":
            logger.error(f"Cannot compare {ineq} for type str")
            counted("CLI_exception")
            raise CLI_Input_Error(f"Cannot compare {ineq} for type str")
        else:
            boolmeta = df[col] == key
            return boolmeta
