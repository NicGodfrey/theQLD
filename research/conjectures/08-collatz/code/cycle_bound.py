#!/usr/bin/env python3
"""
Eliahou-style lower bounds for nontrivial cycles of the accelerated Collatz map
    T(n) = n/2        (n even)
    T(n) = (3n+1)/2   (n odd),
updated to the currently published computational verification height.

Mathematical basis (proved in REPORT.md, Section 5.1):
  If a nontrivial positive cycle has K elements per period under T, of which L
  are odd, and its smallest odd element is m, then multiplying the one-step
  ratios T(n)/n around the cycle gives   prod_{odd n_i} (3 + 1/n_i) = 2^K,
  hence
        log2(3) < K/L <= log2(3 + 1/m).
  If every number below B has been verified to reach 1, then m > B, so K/L lies
  in the interval  I(B) = ( log2 3 , log2(3 + 1/B) ].
  The minimal possible K and L are given by the rational number with the
  smallest denominator inside I(B) (Stern-Brocot / continued-fraction fact:
  that fraction is unique and simultaneously minimises numerator and
  denominator, because I(B) is an interval of numbers > 1).

Certification strategy: we compute rational enclosures of the two irrational
endpoints at 250 and at 400 decimal digits, run the exact simplest-fraction
algorithm on both the inner and the outer rational interval, and accept the
answer only when the two agree.  All interval arithmetic on the candidate
fraction is then exact (Python Fractions).
"""

from fractions import Fraction
import mpmath


def simplest_between(x: Fraction, y: Fraction) -> Fraction:
    """Fraction with the smallest denominator strictly between x and y (x<y)."""
    assert x < y
    a = x.numerator // x.denominator  # floor(x)
    xf, yf = x - a, y - a             # 0 <= xf < yf
    if xf == 0:
        if yf > 1:
            return Fraction(a + 1)
        w = (Fraction(1) / yf).numerator // (Fraction(1) / yf).denominator + 1
        return a + Fraction(1, w)
    if yf > 1:
        return Fraction(a + 1)
    return a + 1 / simplest_between(1 / yf, 1 / xf)


def endpoint_enclosures(B: int, dps: int):
    """Rational enclosures of A=log2(3) and Bd=log2(3+1/B) with slack 10^-(dps-20)."""
    mpmath.mp.dps = dps
    slack = Fraction(1, 10 ** (dps - 20))
    A = mpmath.log(3) / mpmath.log(2)
    Bd = mpmath.log(mpmath.mpf(3) + mpmath.mpf(1) / B) / mpmath.log(2)
    fA = Fraction(str(mpmath.nstr(A, dps - 5, strip_zeros=False)))
    fB = Fraction(str(mpmath.nstr(Bd, dps - 5, strip_zeros=False)))
    return (fA - slack, fA + slack), (fB - slack, fB + slack)


def bound_for_height(B: int, label: str):
    (Alo, Ahi), (Blo, Bhi) = endpoint_enclosures(B, 250)
    (Alo2, Ahi2), (Blo2, Bhi2) = endpoint_enclosures(B, 400)
    inner = simplest_between(Ahi, Blo)     # subset of the true interval
    outer = simplest_between(Alo, Bhi)     # superset of the true interval
    inner2 = simplest_between(Ahi2, Blo2)
    outer2 = simplest_between(Alo2, Bhi2)
    assert inner == outer == inner2 == outer2, "enclosure mismatch - increase precision"
    frac = inner
    K, L = frac.numerator, frac.denominator
    print(f"--- verification height B = {label} ---")
    print(f"  simplest fraction K/L in (log2 3, log2(3+1/B)] : {K}/{L}")
    print(f"  => any nontrivial cycle has  L >= {L}  odd elements,")
    print(f"     K >= {K}  elements per period under T,")
    print(f"     K+L >= {K + L}  steps under the unaccelerated Collatz map.")
    # exact double-check that the fraction really lies in the certified interval
    assert Ahi < frac <= Blo
    print(f"  certified margins: K/L - log2(3)      > {float(frac - Ahi):.3e}")
    print(f"                     log2(3+1/B) - K/L  > {float(Blo - frac):.3e}")
    print()
    return K, L


if __name__ == "__main__":
    print("Lower bounds for nontrivial Collatz cycles via the cycle-ratio identity")
    print("=" * 74)
    # Sanity check: reproduce the order of Eliahou (1993), who assumed
    # verification up to 2^40 and obtained cycle length >= 17,087,915.
    bound_for_height(2 ** 40, "2^40  (Eliahou 1993 assumption)")
    # Height of Barina's first published verification (J. Supercomputing 2021).
    bound_for_height(2 ** 68, "2^68  (Barina 2021)")
    # Currently published verification height (Barina, J. Supercomputing 2025).
    bound_for_height(2 ** 71, "2^71  (Barina 2025)")
