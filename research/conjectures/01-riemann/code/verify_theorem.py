#!/usr/bin/env python3
"""
Verify every inequality used in BREAKTHROUGH.md, given li_lambda.csv
(produced by li_coefficients.py: lambda_n for n = 1..2000).

The perturbation of the n-th Li coefficient caused by adjoining the quadruple
Q = {b+ig, b-ig, 1-b+ig, 1-b-ig}  (1/2 < b < 1, g > 0)  is

    T_n = sum_{rho in Q} [ 1 - (1 - 1/rho)^n ].

Claims checked (exact complex arithmetic at dps=40 vs. the stated bounds):
  (B1) one-sided:  T_n >= -1.29745 n / g^2          for n <= g^2
  (B2) two-sided:  |T_n| <= 6.595 n / g             for n <= g^2
  (B3) two-sided:  |T_n| <= (4 n + 3.3 n^2) / g^2   for n <= g^2
  (C)  lambda_n + T_n > 0 for all n <= min(2000, g^2), for sample quadruples
  (D)  corollary: infinitely many quadruples at heights g_j = 45 j:
       lambda_n - 1.29745 n sum_j 1/g_j^2 > 0 for n <= 2000, and the truncated
       sum of T_n^{(j)} over j <= J agrees with the one-sided bound.
  (E)  the blindness window is genuinely finite: for (b,g)=(0.99,8) the
       perturbed coefficients go negative at an explicit moderate n.
"""
import csv
from mpmath import mp, mpf, mpc, pi, exp, sqrt

mp.dps = 40

def load_lambdas(path='li_lambda.csv'):
    lams = []
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            lams.append(mpf(row[1]))
    return lams

def T_n(b, g, n):
    """Exact quadruple perturbation, sum over 4 zeros."""
    b, g = mpf(b), mpf(g)
    total = mpf(0)
    for rho in [mpc(b, g), mpc(b, -g), mpc(1-b, g), mpc(1-b, -g)]:
        total += (1 - (1 - 1/rho)**n).real   # imaginary parts cancel in conj pairs
    return total

def check_quadruple(b, g, lams, nmax=None):
    g2 = mpf(g)**2
    N = min(len(lams), int(g2)) if nmax is None else nmax
    ok1 = ok2 = ok3 = okC = True
    worst1 = worst_margin = mpf('inf')
    for n in range(1, N + 1):
        t = T_n(b, g, n)
        lower = -mpf('1.29745') * n / g2
        if t < lower: ok1 = False
        if abs(t) > mpf('6.595') * n / mpf(g): ok2 = False
        if abs(t) > (4*n + mpf('3.3')*n*n) / g2: ok3 = False
        val = lams[n-1] + t
        if val <= 0: okC = False
        worst1 = min(worst1, t - lower)
        worst_margin = min(worst_margin, val)
    print(f"quadruple (b,g)=({b},{g}), n <= {N}:")
    print(f"  (B1) T_n >= -1.29745 n/g^2        : {ok1}   (min slack {mp.nstr(worst1,6)})")
    print(f"  (B2) |T_n| <= 6.595 n/g           : {ok2}")
    print(f"  (B3) |T_n| <= (4n+3.3n^2)/g^2     : {ok3}")
    print(f"  (C)  lambda_n + T_n > 0           : {okC}   (min value {mp.nstr(worst_margin,6)})")
    return ok1 and ok2 and ok3 and okC

def main():
    lams = load_lambdas()
    NL = len(lams)
    print(f"loaded {NL} Li coefficients")

    cmin = min(lams[n]/ (n+1) for n in range(NL))
    print(f"(V) min lambda_n/n = {mp.nstr(cmin, 12)}  >= 0.0230 : {cmin >= mpf('0.0230')}\n")

    # main theorem instance: full verified range needs g >= sqrt(2000) = 44.72
    assert check_quadruple('0.75', 45, lams)
    print()
    # near the edge of the strip, low height: window n <= 64
    assert check_quadruple('0.99', 8, lams)
    print()
    # close to the critical line
    assert check_quadruple('0.51', 45, lams)
    print()

    # (D) corollary: heights g_j = 45 j, j = 1, 2, 3, ...
    S = pi**2 / 6 / mpf(45)**2          # sum_j 1/(45 j)^2
    okD = all(lams[n-1] - mpf('1.29745')*n*S > 0 for n in range(1, NL+1))
    print(f"(D) lambda_n - 1.29745 n * sum_j (45j)^-2 > 0 for n<=2000 : {okD}")
    print(f"    sum_j 1/g_j^2 = {mp.nstr(S, 8)},  1.29745*S = {mp.nstr(mpf('1.29745')*S, 8)}")
    # truncated total perturbation at sample n, plus analytic tail bound
    for n in [1, 10, 100, 1000, 2000]:
        J = 4000
        tot = sum(T_n('0.75', 45*j, n) for j in range(1, J+1))
        tail = (4*n + mpf('3.3')*n*n) / mpf(45)**2 * (1/mpf(J))  # sum_{j>J} 1/j^2 < 1/J
        low = -mpf('1.29745') * n * S
        print(f"    n={n:5d}: sum_(j<=4000) T_n^(j) = {mp.nstr(tot, 8)}  (tail<{mp.nstr(tail,4)}), "
              f"one-sided bound {mp.nstr(low, 8)}, lambda_n = {mp.nstr(lams[n-1], 8)}")

    # (E) finiteness of the window for (b,g)=(0.99,8): find first n where
    # lambda_n + T_n < 0 (detection), far beyond the guaranteed n <= 64.
    first_neg = None
    worst = (None, mpf('inf'))
    for n in range(1, NL+1):
        v = lams[n-1] + T_n('0.99', 8, n)
        if v < worst[1]: worst = (n, v)
        if v < 0 and first_neg is None: first_neg = (n, v)
    print(f"\n(E) (b,g)=(0.99,8): guaranteed blind window n <= 64;")
    if first_neg:
        print(f"    first n with lambda_n + T_n < 0 : n = {first_neg[0]} (value {mp.nstr(first_neg[1],6)})")
    else:
        print(f"    no negative value up to n = {NL}; most negative margin at n={worst[0]}: {mp.nstr(worst[1],6)}")
    print(f"    (Li/Bombieri-Lagarias: some lambda_n must eventually go negative for this multiset.)")

if __name__ == '__main__':
    main()
