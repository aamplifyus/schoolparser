from itertools import combinations
from math import factorial
from typing import List

import numpy as np


def permutation_test(
    fragmat: np.ndarray,
    hypo_inds: List,
    method="exact",
    num_rounds=1000,
    biased=False,
    seed=None,
):  # pragma: no cover
    """Run permutation test over channels selected of fragility matrix."""

    def func(x, y):
        stat = np.mean(x)  # / np.mean(y)
        return stat

    # random state for the permutation test
    rng = np.random.RandomState(seed)

    # initialize data structures
    m = fragmat.shape[0]
    n = len(hypo_inds)
    other_inds = [i for i in range(fragmat.shape[0]) if i not in hypo_inds]

    # counter for relative difference wrt ref point
    more_extreme = 0.0

    # determines the reference point
    x = fragmat[hypo_inds, :]
    y = fragmat[other_inds, :]
    reference_stat = func(x, y)

    # store the empirical differences
    empirical_diffs = []

    if m <= 10:
        if num_rounds > factorial(m) / (factorial(m) * factorial(n)):
            method = "exact"
    if method == "exact":
        if m > 10:
            raise RuntimeError(
                "Can't run exact permutation test with that many rounds."
            )

        # compute exact permutation test, which is only possible for small m and n
        for indices_x in combinations(range(m), n):
            indices_y = [i for i in range(m) if i not in indices_x]
            diff = func(fragmat[list(indices_x), :], fragmat[indices_y, :])

            # generate more extreme versus not
            if diff > reference_stat:
                more_extreme += 1.0
            empirical_diffs.append(diff)

        # compute total number of rounds
        num_rounds = factorial(m) / (factorial(m) * factorial(n))
    else:
        print("Reference statistic: ", reference_stat)
        for i in range(num_rounds):
            rng.shuffle(fragmat)
            diff = func(fragmat[hypo_inds, :], fragmat[other_inds, :])

            # generate more extreme versus not
            if diff > reference_stat:
                more_extreme += 1.0
            empirical_diffs.append(diff)

    return more_extreme / num_rounds, empirical_diffs
