from typing import Union, List
import numpy as np
from sklearn import metrics
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.validation import check_is_fitted, check_array

from rerf.rerfClassifier import rerfClassifier

from sklearn import preprocessing
from scipy import signal


def _unique_labels(y):
    le = preprocessing.LabelEncoder()
    labels = le.fit_transform(np.unique(y))
    return labels


def _cutoff_youdens_j(fpr, tpr, thresholds):
    j_scores = tpr - fpr
    j_ordered = sorted(zip(j_scores, thresholds))
    return j_ordered[-1][1]


def _gaussian_weight(x):
    # window = np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
    window = signal.gaussian(len(x), std=1, sym=True)
    return np.multiply(window, x)


def _uniform_weight(x):
    return x


def _exponential_weight(x):
    window = signal.exponential(
        len(x),
        # center=center,
        # tau=tau, sym=True
    )
    return np.multiply(window, x)


class FragilityHeatmapClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, window=None, threshold=None, weighting_func=None):
        self.window = window
        self.threshold = threshold
        self.weighting_func = weighting_func

    def fit(self, X: Union[np.ndarray, List], y: Union[np.ndarray, List]):
        # Check that X and y have correct shape
        # perform shape reshaping
        X, y = self._check_X_y(X, y)

        # perform error checking on the parameters
        self._check_params()

        # Store the classes seen during fit
        self.classes_ = _unique_labels(y)
        self.X_ = X
        self.y_ = y

        # compute ratios
        X = self.apply(X)

        # clf = RandomForestClassifier()
        # tau2 = -(len(cezsignal)-30 - 1) / np.log(0.01)
        # weights = np.concatenate((np.ones((30,)), scipy.signal.exponential(len(cezsignal)-30, 0, tau2, False)))
        # weights = np.ones((len(cezsignal),))
        # ratio = numnezchans / numezchans

        # Return the classifier
        return self

    def apply(self, X):
        # ratio classifier
        ratios = []
        for i, (_X) in enumerate(X):
            # perform classification on hyper-parametrized fragility map
            if self.threshold is not None:
                _X = [np.clip(sub_X, a_min=self.threshold, a_max=None) for sub_X in _X]
            if self.window is not None:
                start, end = self.window
                _X = [sub_X[..., start:end] for sub_X in _X]
            if self.weighting_func is not None:
                for sub_X in _X:
                    for j in range(sub_X.shape[0]):
                        sub_X[j, :] = self.weighting_func_(sub_X[j, :])

            # apply weight to each row of _X
            # _X = np.array([self.weighting_func_(x) for x in _X])
            soz_mat = _X[0]
            nsoz_mat = _X[1]
            try:
                ratio = np.divide(np.mean(soz_mat), np.mean(nsoz_mat))
            except Exception as e:
                print(e)
                print(i)
                ratio = 0.0
            ratios.append(ratio)
        ratios = np.array(ratios).squeeze()
        self.ratios_ = ratios

        # original classifier
        # n_est = 1000
        # timelen = X.shape[-1]
        # clf = RandomForestClassifier(max_depth=5, n_estimators=n_est, max_features=1)
        # clf = rerfClassifier(
        #     projection_matrix="S-RerF",
        #     max_features="auto",
        #     n_estimators=n_est,
        #     oob_score=False,
        #     random_state=0,
        #     image_height=1,
        #     image_width=timelen,
        #     patch_height_max=1,
        #     patch_height_min=1,
        #     patch_width_max=timelen,
        #     patch_width_min=5,
        # )

        # create data matrix from ratios
        # _X = []
        # for i, (_X, sozinds, nsozinds) in enumerate(
        #     zip(X, sozinds_list, nsozinds_list)
        # ):
        #     ratio_ts = np.mean(X[i, sozinds, :], axis=0) / np.mean(
        #         X[i, nsozinds, :], axis=0
        #     )
        #     _X.append(ratio_ts)
        # clf.fit(_X, self.y_)

        return ratios

    def score(self, X, y, sample_weight=None):
        # compute y probability - ratio values
        yprob = self.predict_proba(X)

        # compute ROC curve
        fpr, tpr, thresholds = metrics.roc_curve(y, yprob)

        # compute AUC
        auc = metrics.auc(fpr, tpr)

        # compute the youden cutoff point score
        youden_index = _cutoff_youdens_j(fpr, tpr, thresholds)

        return auc

    def predict(self, X, sozinds_list):
        ypred = self.predict_proba(X, sozinds_list)
        return ypred

    def predict_proba(self, X):
        # Check is fit had been called
        check_is_fitted(self)
        yprob = self.apply(X)
        return yprob

    def _get_nsozinds(self, X, sozinds_list):
        if len(X) != len(sozinds_list):
            raise ValueError(
                f"Length of X ({len(X)}) and y ({len(y)}) should be the same."
            )

        nsozinds_list = []
        for i, (sozinds, _X) in enumerate(zip(sozinds_list, X)):
            nsozinds = [
                ch_ind for ch_ind in range(_X.shape[0]) if ch_ind not in sozinds
            ]
            nsozinds_list.append(nsozinds)

        return nsozinds_list

    def _check_params(self):
        # check window we make
        if self.window is not None:
            start, end = self.window
            if start < 0:
                raise ValueError(f"Start of the window ({start}) can't be less than 0.")
            if end > self.xlength:
                raise ValueError(
                    f"End of the window ({end}) can't  be more then the data shape {self.xlength}"
                )

        # check threshold placed on map
        if self.threshold is not None:
            if self.threshold < 0 or self.threshold > 1.0:
                raise ValueError(
                    f"Threshold passed ({self.threshold}) must be between 0 and 1."
                )

        # check weighting function
        if self.weighting_func == "exponential":
            self.weighting_func_ = _exponential_weight
        elif self.weighting_func == "uniform":
            self.weighting_func_ = _uniform_weight
        elif self.weighting_func == "normal":
            self.weighting_func_ = _gaussian_weight
        else:
            raise AttributeError(
                "weighting_func should be a callable function "
                "uniform and exponential."
            )
        # if not callable(self.weighting_func):
        #     raise AttributeError("weighting_func should be a callable function.")

    def _check_X_y(self, X, y):
        xlength = dict()
        if len(X) != len(y):
            raise RuntimeError(
                "The length of data matrix, X ({}) and "
                "training labels, y ({}) should be "
                "the same.".format(len(X), len(y))
            )
        for i, sub_X in enumerate(X):
            if len(X[i]) != 2:
                raise RuntimeError(
                    "All entries in the data matrix, X "
                    "should be a tuple of the SOZ and "
                    "the nSOZ."
                )
            for j in range(2):
                xlength[np.array(sub_X[j]).shape[-1]] = 1

        if len(xlength.keys()) > 1:
            raise RuntimeError(
                "All data should have the same number of "
                "time points, but there are data with {} "
                "time points.".format(xlength.keys())
            )

        self.xlength = list(xlength.keys())[0]

        # X = np.array(X)
        # y = np.array(y)
        return X, y
