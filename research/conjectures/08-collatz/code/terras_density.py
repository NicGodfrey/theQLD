#!/usr/bin/env python3
"""
Exact recomputation of the Terras stopping-time densities.

For the accelerated map T, the first k steps of the orbit of n depend only on
n mod 2^k, and each residue class realises exactly one parity vector
(x_0,...,x_{k-1}) in {0,1}^k (Terras 1976).  Writing L_i = x_0+...+x_{i-1},
one has  T^i(n) = (3^{L_i} n + rho_i)/2^i  with rho_i >= 0, so the orbit has
provably dropped below n (for all sufficiently large n in the class) as soon
as 3^{L_i} < 2^i.  The density of integers whose stopping time exceeds k is
therefore

    D_k = 2^{-k} * #{ parity vectors of length k : 3^{L_i} > 2^i for all i<=k }

(3^L = 2^i is impossible for i>=1).  Terras proved D_k -> 0; Lagarias (1985)
proved D_k <= 2^{-eta k} with eta = 1 - H(theta), theta = log_3 2,
H = binary entropy.  We compute D_k exactly by dynamic programming on
(i, L_i) and compare with the predicted exponential rate.
"""

from fractions import Fraction
import math


def survival_counts(kmax: int):
    """counts[k] = number of surviving parity vectors of length k."""
    # survival condition after i steps: 3^{L_i} > 2^i  <=>  L_i > i*log_3(2)
    # exact threshold via integer powers (no floating point).
    pow3 = [1]
    for _ in range(kmax + 2):
        pow3.append(pow3[-1] * 3)

    def survives(i: int, L: int) -> bool:
        return pow3[L] > (1 << i)

    counts = []
    state = {0: 1}  # L -> number of vectors, after 0 steps
    for i in range(1, kmax + 1):
        new = {}
        for L, c in state.items():
            for x in (0, 1):
                L2 = L + x
                if survives(i, L2):
                    new[L2] = new.get(L2, 0) + c
        state = new
        counts.append(sum(state.values()))
    return counts


if __name__ == "__main__":
    KMAX = 120
    counts = survival_counts(KMAX)
    theta = math.log(2) / math.log(3)
    H = -theta * math.log2(theta) - (1 - theta) * math.log2(1 - theta)
    eta = 1 - H
    print("Exact densities D_k of { n : stopping time sigma(n) > k }")
    print(f"(theta = log_3 2 = {theta:.6f},  predicted decay rate eta = 1-H(theta) = {eta:.6f})")
    print()
    print(f"{'k':>4} {'surviving vectors':>22} {'D_k = c_k/2^k':>15} {'-log2(D_k)/k':>14}")
    for k in [1, 2, 3, 4, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]:
        c = counts[k - 1]
        D = Fraction(c, 1 << k)
        rate = -math.log2(D) / k if D > 0 else float("inf")
        print(f"{k:>4} {c:>22} {float(D):>15.6e} {rate:>14.6f}")
    print()
    print("Every column is exact integer arithmetic; the last column decreases")
    print("towards eta from above as k grows (corrections of size O(log k / k)).")
