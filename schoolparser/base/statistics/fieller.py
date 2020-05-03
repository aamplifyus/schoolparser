import math
from scipy.stats import t


# TODO: verify Fieller statistic is a good capture of a ratio statistic between proposed
# SOZ and not SOZ
class Fieller(object):  # noqa
    r"""
    FIELLER: calculates confidence limits for a ratio.

    According Fieller''s theorem (see Finney\'s book).

    Output includes the approximate SD of the ratio r = a / b,
    given the SD of a (the numerator) and of b (the denominator)
    and the correlation coefficient between a & b (zero if they are independent).

    Fieller requires the t-statistic which can be provided from a table
    or calculated from alpha and the degrees of freedom.

    Alpha-level deviation is for two tailed distribution (e.g. 0.05 leaves 90% area).

    Parameters
    ----------
    a : array_like
        Sample observation of numerator.
    b : array_like
        Sample observation of denominator.
    sigma_a : array_like

    sigma_b : array_like

    popmean : float or array_like
        Expected value in null hypothesis. If array_like, then it must have the
        same shape as `a` excluding the axis dimension.
    axis : int or None, optional
        Axis along which to compute test. If None, compute over the whole
        array `a`.
    nan_policy : {'propagate', 'raise', 'omit'}, optional
        Defines how to handle when input contains nan.
        The following options are available (default is 'propagate'):
          * 'propagate': returns nan
          * 'raise': throws an error
          * 'omit': performs the calculations ignoring nan values
    Returns
    -------
    statistic : float or array
        t-statistic.
    pvalue : float or array
        Two-sided p-value.
    """

    def __init__(self, a, b, sigma_a, sigma_b, r, alpha, N):
        self.a, self.b = a, b
        self.sigma_a, self.sigma_b = sigma_a, sigma_b
        self.r = r
        self.Ntot = N
        self.alpha = alpha
        self.__calculate_t()
        self.calcFieller()

    def __calculate_t(self):
        self.df = self.Ntot - 2
        two_tail = 1 - float(self.alpha)
        self.tval = t.cdf(two_tail, self.df)
        # self.tval = s.InverseStudentT(self.df, two_tail)

    def calcFieller(self):
        """Fieller formula calculator."""
        va = self.sigma_a * self.sigma_a
        vb = self.sigma_b * self.sigma_b
        cov = self.r * self.sigma_a * self.sigma_b
        self.g = self.tval * self.tval * vb / (self.b * self.b)
        self.ratio = self.a / self.b
        rat2 = self.ratio * self.ratio
        # Write disc in a way that does not appear to divide by vb
        # (which actually cancels) so OK to use vb=0
        # disc=va - 2.0*ratio*cov + rat2*vb - g*(va-cov*cov/vb)
        disc = (
            va
            - 2.0 * self.ratio * cov
            + rat2 * vb
            - self.g * (va - self.r * self.r * va)
        )

        self.clower, self.cupper = 0.0, 0.0
        self.appsd, self.applo = 0.0, 0.0
        self.apphi = 0.0
        self.cvr = 0.0
        self.dlow, self.dhi = 0.0, 0.0

        if disc >= 0:
            d = (self.tval / self.b) * math.sqrt(disc)
            # Write pre in a way that does not appear to divide by vb
            # (which actually cancels) so OK to use vb=0 (use g=tval*tval*vb/(b*b))
            # 	pre=ratio - g*cov/vb
            pre = self.ratio - (
                self.tval * self.tval * self.r * self.sigma_a * self.sigma_b
            ) / (self.b * self.b)
            f = 1.0 / (1.0 - self.g)
            self.clower = f * (pre - d)
            self.cupper = f * (pre + d)
            self.dlow = self.clower - self.ratio
            self.dhi = self.cupper - self.ratio
            # Approximation for small g
            self.appsd = math.sqrt(va + rat2 * vb - 2.0 * self.ratio * cov) / self.b
            self.applo = self.ratio - self.tval * self.appsd
            self.apphi = self.ratio + self.tval * self.appsd
            if self.ratio != 0:
                self.cvr = 100.0 * self.appsd / self.ratio

    def __repr__(self):
        return (
            "\n Fieller calculation result: "
            + "\n Ratio (=a/b) = {0:.6f}".format(self.ratio)
            + "\n g = {0:.6f};\n alpha = {1:.2f};\n degree of freedom  = {2:d};\n t(df, alpha) = {3:.6f}".format(
                self.g, self.alpha, int(self.df), self.tval
            )
            + "\n\n Confidence limits: lower {0:.6f}, upper {1:.6f}".format(
                self.clower, self.cupper
            )
            + "\n i.e deviations: lower {0:.6f}, upper {1:.6f}".format(
                self.dlow, self.dhi
            )
            + "\n Approximate SD of ratio = {0:.6f}".format(self.appsd)
            + "\n Approximate CV of ratio (%) = {0:.6f}".format(self.cvr)
            + "\n Approximate limits: lower {0:.6f}, upper {0:.6f}".format(
                self.applo, self.apphi
            )
        )
