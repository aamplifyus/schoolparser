from datetime import datetime, date, timedelta, timezone

import numpy as np
import scipy.signal


def _movingaverage(vector, window_size):
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(vector, window, "same")


def _smooth_vector(x, window_len=5, window="hanning"):
    """
    Smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the beginning and end part of the output signal.

    Parameters
    ----------
    x : the input signal
    window_len : the dimension of the smoothing window; should be an odd integer
    window : the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    Returns
    -------
    y : the smoothed signal

    Examples
    --------
    >>> from eztrack.base.utils.preprocess_utils import _smooth_vector
    >>> t=linspace(-2,2,0.1)
    >>> x=sin(t)+randn(len(t))*0.1
    >>> y=smooth(x)

    See also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if window_len < 3:
        return x

    s = np.r_[x[window_len - 1 : 0 : -1], x, x[-2 : -window_len - 1 : -1]]
    # print(len(s))
    if window == "flat":  # moving average
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")

    y = np.convolve(w / w.sum(), s, mode="valid")
    return y


def _smooth_matrix(X, axis=0, window_len=5, window="hanning"):
    if X.ndim > 2:
        raise RuntimeError("Matrix X should be only 2-dimensional.")

    if axis == 0:
        iternum = X.shape[0]
    elif axis == 1:
        iternum = X.shape[1]

    X_smooth = []
    for i in range(iternum):
        x_vec = X[i, :].squeeze()
        x_smooth_vec = _smooth_vector(x_vec, window_len, window)

        # append to matrix
        X_smooth.append(x_smooth_vec)
    X_smooth = np.array(X_smooth)
    return X_smooth


def _resample_mat(mat, desired_len):
    """
    Resample an entire matrix composed of signals x time.

    Resamples each signal, one at a time.

    Parameters
    ----------
    mat
    desired_len

    Returns
    -------

    """
    if mat.ndim != 2:
        raise ValueError("Matrix needs to be 2D.")

    # initialize resampled matrix
    resampled_mat = np.zeros((mat.shape[0], desired_len))

    # resample each vector
    for idx in range(mat.shape[0]):
        seq = mat[idx, ...].squeeze()
        resampled_mat[idx, :] = scipy.signal.resample(seq, desired_len)
    return resampled_mat


def _get_daysback_range(raw):
    """
    Get the minimum and maximum days back in order to be BIDS compliant anonymized.

    The recording date must be before 1925 after anonymization.

    Parameters
    ----------
    raw : instance of mne.io.Raw
        The raw data. It must be an instance or list of instances of mne.Raw.

    Returns
    -------
    daysback_min : int
        The minimum number of daysback necessary to be compatible with BIDS.
    daysback_max : int
        The maximum number of daysback that MNE can store.

    """

    record_date = _stamp_to_dt(raw.info["meas_date"]).date()
    daysback_min = (record_date - date(year=1924, month=12, day=31)).days
    daysback_max = (
        record_date
        - datetime.fromtimestamp(0).date()
        + timedelta(seconds=np.iinfo(">i4").max)
    ).days
    return daysback_min, daysback_max


def _stamp_to_dt(utc_stamp):
    """Convert POSIX timestamp to datetime object in Windows-friendly way."""

    if isinstance(utc_stamp, datetime):
        return utc_stamp
    stamp = [int(s) for s in utc_stamp]
    if len(stamp) == 1:  # In case there is no microseconds information
        stamp.append(0)
    return datetime.fromtimestamp(0, tz=timezone.utc) + timedelta(
        0, stamp[0], stamp[1]
    )  # day, sec, μs
