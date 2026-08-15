#!/usr/bin/env python3
"""Computational companion to BREAKTHROUGH.md (Legion 09 Goldbach, Wave 2).

Two independent checks, pure stdlib, a few seconds at LIMIT = 10**5:

  Part 1 -- Goldbach verification: every even n in [4, LIMIT] is a sum of two
            primes; reports the largest "minimal Goldbach prime" encountered.

  Part 2 -- Modulus-Barrier numerics at N = LIMIT: compares
              (a) the exact Parseval mass  int_0^1 |S|^2 = sum_{p<=N} log^2 p,
              (b) its asymptotic prediction N log N   (Theorem, part (i)),
              (c) the singular-series main term  Sing(n)*n  at n = N,
              (d) the true weighted representation count
                  R(n) = sum_{p+q=n} (log p)(log q)   (ordered pairs),
            illustrating that the minor-arc L^2 mass exceeds the main term by
            a factor of order log N -- the barrier ratio of the theorem.

No claim beyond the computed range. The published verification record for
binary Goldbach is 4*10^18 (Oliveira e Silva-Herzog-Pardi, Math. Comp. 83,
2014); this script is an illustration, not a record attempt.
"""

import math

LIMIT = 10 ** 5
# Twin-prime constant prod_{p>2}(1-(p-1)^{-2}); numeric value [ESTABLISHED*].
C2 = 0.6601618158468696


def prime_table(n: int) -> bytearray:
    is_p = bytearray([1]) * (n + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, math.isqrt(n) + 1):
        if is_p[i]:
            is_p[i * i:: i] = bytearray(len(range(i * i, n + 1, i)))
    return is_p


def part1_goldbach(is_p: bytearray, limit: int) -> None:
    primes = [i for i in range(2, limit + 1) if is_p[i]]
    worst_p = worst_n = 0
    for n in range(4, limit + 1, 2):
        found = None
        for p in primes:
            if 2 * p > n:  # a representation with minimal p has p <= n/2
                break
            if is_p[n - p]:
                found = p
                break
        if found is None:
            raise AssertionError(f"Goldbach FAILS at n = {n}")
        if found > worst_p:
            worst_p, worst_n = found, n
    print(f"[Part 1] Binary Goldbach verified for all even n in [4, {limit}].")
    print(f"[Part 1] Largest minimal Goldbach prime: p = {worst_p} at n = {worst_n}.")


def singular_series(n: int) -> float:
    """Sing(n) = 2*C2 * prod_{p|n, p>2} (p-1)/(p-2) for even n."""
    s, m, d = 2.0 * C2, n, 2
    while d * d <= m:
        if m % d == 0:
            if d > 2:
                s *= (d - 1) / (d - 2)
            while m % d == 0:
                m //= d
        d += 1
    if m > 2:
        s *= (m - 1) / (m - 2)
    return s


def part2_barrier(is_p: bytearray, N: int) -> None:
    logs = {p: math.log(p) for p in range(2, N + 1) if is_p[p]}
    l2 = sum(v * v for v in logs.values())  # exact int_0^1 |S|^2 (Parseval)
    nlogn = N * math.log(N)
    n = N  # even target frequency
    R = sum(lp * logs[n - p] for p, lp in logs.items()
            if p <= n - 2 and is_p[n - p])
    Sn = singular_series(n)
    main = Sn * n
    print(f"[Part 2] N = n = {N}   (log N = {math.log(N):.4f})")
    print(f"[Part 2] Parseval mass  int|S|^2 = sum log^2 p = {l2:,.0f}")
    print(f"[Part 2]   vs N log N = {nlogn:,.0f}   (ratio {l2 / nlogn:.4f}; -> 1 as N -> oo)")
    print(f"[Part 2] Singular series Sing(n) = {Sn:.4f};  main term Sing(n)*n = {main:,.0f}")
    print(f"[Part 2] True weighted count R(n) = {R:,.0f}   (R / main = {R / main:.4f})")
    print(f"[Part 2] BARRIER RATIO  int|S|^2 / (Sing(n)*n) = {l2 / main:.2f}")
    print(f"[Part 2]   compare log N / Sing(n) = {math.log(N) / Sn:.2f}: the L^2 mass any")
    print(f"[Part 2]   modulus argument must pay overshoots the main term by ~ log N.")


if __name__ == "__main__":
    table = prime_table(LIMIT)
    part1_goldbach(table, LIMIT)
    part2_barrier(table, LIMIT)
