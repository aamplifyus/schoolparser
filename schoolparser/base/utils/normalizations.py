import numpy as np
import numpy.matlib


class Normalize:
    """Class of normalization methods to apply to NxT matrices."""

    @staticmethod
    def compute_fragilitymetric(minnormpertmat):
        """
        Normalization of a NxT matrix to [0,1).

        Normalizes what we defined as the fragility metric. It emphasizes
        values over the columns that is significantly different from the
        lowest value, normalized by the range of the entire column.

        This is an unsymmetric normalization transformation.

        Parameters
        ----------
        minnormpertmat :

        Returns
        -------
        fragilitymat :
        """
        # get dimensions of the pert matrix
        N, T = minnormpertmat.shape

        # assert N < T
        fragilitymat = np.zeros((N, T))
        for icol in range(T):
            fragilitymat[:, icol] = (
                np.max(minnormpertmat[:, icol]) - minnormpertmat[:, icol]
            ) / np.max(minnormpertmat[:, icol])
        return fragilitymat

    @staticmethod
    def compute_minmaxfragilitymetric(minnormpertmat):
        """
        Min-Max normalization of a NxT matrix to [0,1].

        It emphasizes values over the columns that is
        significantly different from the lowest value,
        normalized by the range of the entire column. It maps each
        column to values with 0 and 1 definitely.

        Parameters
        ----------
        minnormpertmat :

        Returns
        -------
        fragilitymat :
        """
        # get dimensions of the pert matrix
        N, T = minnormpertmat.shape

        # get the min/max for each column in matrix
        minacrosstime = np.min(minnormpertmat, axis=0)
        maxacrosstime = np.max(minnormpertmat, axis=0)

        # normalized data with minmax scaling
        fragilitymat = -1 * np.true_divide(
            (minnormpertmat - np.matlib.repmat(maxacrosstime, N, 1)),
            np.matlib.repmat(maxacrosstime - minacrosstime, N, 1),
        )
        return fragilitymat

    @staticmethod
    def compute_znormalized_fragilitymetric(minnormpertmat):
        """
        Z-normalization of each column of a NxT matrix.

        Parameters
        ----------
        minnormpertmat :

        Returns
        -------
        fragmat :
        """
        # get mean, std
        avg_contacts = np.mean(minnormpertmat, keepdims=True, axis=1)
        std_contacts = np.std(minnormpertmat, keepdims=True, axis=1)

        # normalized data with minmax scaling
        return (minnormpertmat - avg_contacts) / std_contacts
