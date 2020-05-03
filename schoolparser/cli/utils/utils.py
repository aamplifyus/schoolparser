from mne_bids.utils import _parse_bids_filename


def _linebreak(x):
    firstline = []
    i = 0
    while x[i] != "\n" and i < len(x) - 1:
        firstline.append(x[i])
        i += 1
    return "".join(["-"] * len(firstline))


def _extract_run(fname):
    params = _parse_bids_filename(fname, verbose=False)
    return params["run"]


def clear_screen():
    """
    A pythonic function to clear_screen the command line screen in the ui
    """
    print("\033[H\033[J")
