#!/usr/bin/env python3
"""
wave2_lemma_check.py — computational certification for the Wave-2 theorem
(see BREAKTHROUGH.md): an elementary predecessor-tree lower bound
    pi_a(x) > (3x/(64a))^{c*}   for all x >= a,
with c* = 0.3020117... the unique real root of (3/16)^c + (3/64)^c = 1,
and its corollary: one divergent Collatz orbit forces > (3x/(64a))^{c*}
divergent starting values <= x.

What this script certifies (and what it does not):

  (1) [EXACT]  3/10 < c* < 31/100, by integer k-th-root certificates
      (no floating point), plus a 25-digit value of c* by bisection (mpmath).
  (2) [EXACT, EXHAUSTIVE]  the Two-Children Lemma for every n <= 10^6 with
      3 not dividing n: with j0 = 0 if n = 2 (mod 3) and j0 = 1 if n = 1
      (mod 3), each m_j = (2^(j+1) n - 1)/3 for j in {j0, j0+2, j0+4} is an
      odd integer >= 3 with T^(j+1)(m_j) = n and 3 m_j < 2^(j+1) n; the
      three m_j satisfy m_{j+2} = 4 m_j + 1 and cover all residues mod 3,
      so EXACTLY TWO of them are not divisible by 3.
  (3) [DEMONSTRATION]  the stopped predecessor tree of the theorem, run on
      the (convergent) roots a = 5 and a = 7 at several scales x: all node
      values pairwise distinct (tree-injectivity lemma), all final leaves in
      (3x/64, x], every leaf's forward T-orbit passes through a, the mass
      inequality sum(leaf^{-c*}) >= a^{-c*} holds, and the theorem's bound
      #leaves > (3x/(64a))^{c*} holds.  NO divergent orbit is known and none
      is claimed: the demo certifies the counting engine, which transfers
      verbatim to a divergent root if one exists.
  (4) [EXACT, EXHAUSTIVE]  brute-force cross-check: the true predecessor
      count pi_5(10^6) versus the tree's leaf count and the guaranteed bound.
"""

import mpmath


def T(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def iroot(x: int, k: int) -> int:
    """floor(x^(1/k)) for integers x >= 0, k >= 1 (Newton, exact)."""
    if x < 2:
        return x
    r = 1 << (x.bit_length() // k + 2)  # certainly > x^(1/k)
    while True:
        nr = ((k - 1) * r + x // r ** (k - 1)) // k
        if nr >= r:
            break
        r = nr
    assert r ** k <= x < (r + 1) ** k
    return r


# ---------------------------------------------------------------- part (1)
def part1_cstar():
    print("(1) The exponent c*: unique root of (3/16)^c + (3/64)^c = 1")
    S = 10 ** 30
    # lower certificate at c = 3/10:
    #   (3/16)^(3/10) = (27/4096)^(1/10),  (3/64)^(3/10) = (27/262144)^(1/10)
    lo1 = iroot(27 * 10 ** 300 // 4096, 10)       # floor of a lower bound * S
    lo2 = iroot(27 * 10 ** 300 // 262144, 10)
    assert lo1 + lo2 > S, "certificate c* > 3/10 FAILED"
    print(f"    exact certificate at c = 3/10 : (lo1+lo2-S)/S = "
          f"{(lo1 + lo2 - S) / S:.6e} > 0   =>  c* > 3/10")
    # upper certificate at c = 31/100:
    #   (3/16)^(31/100) = (3^31/16^31)^(1/100), etc.; use ceilings for upper bounds
    N1 = 3 ** 31 * 10 ** 3000 // 16 ** 31 + 1
    N2 = 3 ** 31 * 10 ** 3000 // 64 ** 31 + 1
    hi1 = iroot(N1, 100) + 1                       # ceil of an upper bound * S
    hi2 = iroot(N2, 100) + 1
    assert hi1 + hi2 < S, "certificate c* < 31/100 FAILED"
    print(f"    exact certificate at c = 31/100: (S-hi1-hi2)/S = "
          f"{(S - hi1 - hi2) / S:.6e} > 0   =>  c* < 31/100")
    # 25-digit numerical value by bisection
    mpmath.mp.dps = 40
    f = lambda c: mpmath.mpf(3) ** c / mpmath.mpf(16) ** c \
        + mpmath.mpf(3) ** c / mpmath.mpf(64) ** c - 1
    lo, hi = mpmath.mpf("0.30"), mpmath.mpf("0.31")
    for _ in range(140):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    cstar = (lo + hi) / 2
    print(f"    c* = {mpmath.nstr(cstar, 25)}  (bisection, 40 dps)")
    print()
    return cstar


# ---------------------------------------------------------------- part (2)
def part2_two_children(N0: int = 10 ** 6):
    print(f"(2) Two-Children Lemma, exhaustive for 3 <= n <= {N0}, 3 not | n")
    excl_pos = [0, 0, 0]   # which of the three candidates was = 0 (mod 3)
    checked = 0
    for n in range(3, N0 + 1):
        if n % 3 == 0:
            continue
        j0 = 0 if n % 3 == 2 else 1
        ms, zero_idx = [], None
        for idx, j in enumerate((j0, j0 + 2, j0 + 4)):
            num = (1 << (j + 1)) * n - 1
            assert num % 3 == 0, (n, j)
            m = num // 3
            assert m & 1 and m >= 3, (n, j, m)
            v = T(m)
            assert v == (1 << j) * n, (n, j, m)
            for _ in range(j):
                v = T(v)
            assert v == n, (n, j, m)          # T^{j+1}(m) = n verified
            assert 3 * m < (1 << (j + 1)) * n  # size bound m < 2^{j+1} n / 3
            ms.append(m)
            if m % 3 == 0:
                assert zero_idx is None, (n, "two candidates divisible by 3")
                zero_idx = idx
        assert zero_idx is not None, (n, "no candidate divisible by 3")
        assert ms[1] == 4 * ms[0] + 1 and ms[2] == 4 * ms[1] + 1, n
        excl_pos[zero_idx] += 1
        checked += 1
    print(f"    verified for {checked} values of n: exactly two children each")
    print(f"    discarded candidate was m_(j0)/m_(j0+2)/m_(j0+4) in "
          f"{excl_pos[0]}/{excl_pos[1]}/{excl_pos[2]} cases")
    print(f"    (worst case for the bound = discarding m_(j0): "
          f"{excl_pos[0]} cases, factors then {{2^(j0+3)/3, 2^(j0+5)/3}})")
    print()


# ---------------------------------------------------------------- part (3)
def stopped_tree(a: int, x: int):
    """Build the stopped predecessor tree of the theorem; verify invariants."""
    assert a % 2 == 1 and a % 3 != 0 and a >= 3 and 64 * a <= 3 * x
    seen = {a}
    leaves = []
    stack = [(a, 0)]
    nodes, maxdepth, splits, worst_pair = 1, 0, 0, 0
    while stack:
        n, d = stack.pop()
        if 64 * n > 3 * x:          # stopping rule: leaf in (3x/64, x]
            leaves.append(n)
            maxdepth = max(maxdepth, d)
            continue
        j0 = 0 if n % 3 == 2 else 1
        kids, offs = [], []
        for off, j in ((0, j0), (2, j0 + 2), (4, j0 + 4)):
            m = ((1 << (j + 1)) * n - 1) // 3
            if m % 3:
                kids.append(m)
                offs.append(off)
        assert len(kids) == 2, (n, "two-children lemma violated")
        if j0 == 1 and offs == [2, 4]:   # binding case: factors {16/3, 64/3}
            worst_pair += 1
        splits += 1
        for m in kids:
            assert m <= x, (n, m, "child escaped scale x")
            assert m not in seen, (n, m, "tree injectivity violated")
            seen.add(m)
            stack.append((m, d + 1))
            nodes += 1
    return leaves, nodes, maxdepth, splits, worst_pair


def orbit_hits(m: int, a: int, cap: int = 200000) -> bool:
    v = m
    for _ in range(cap):
        if v == a:
            return True
        v = T(v)
    return False


def part3_trees(cstar):
    print("(3) Stopped predecessor trees (theorem engine, demonstration roots)")
    mpmath.mp.dps = 30
    results = {}
    for a, x in [(5, 10 ** 6), (5, 10 ** 7), (5, 10 ** 8), (7, 10 ** 7)]:
        leaves, nodes, maxdepth, splits, worst_pair = stopped_tree(a, x)
        assert len(set(leaves)) == len(leaves)
        assert all(64 * v > 3 * x and v <= x for v in leaves)
        assert all(orbit_hits(v, a) for v in leaves)
        mass = sum(mpmath.mpf(v) ** (-cstar) for v in leaves)
        mass_floor = mpmath.mpf(a) ** (-cstar)
        assert mass >= mass_floor, "mass inequality FAILED"
        bound = (mpmath.mpf(3 * x) / (64 * a)) ** cstar
        assert len(leaves) > bound, "theorem bound FAILED"
        print(f"    a={a}, x=10^{len(str(x)) - 1}: nodes={nodes}, "
              f"splits={splits}, leaves={len(leaves)}, max depth={maxdepth}")
        print(f"        all leaves distinct, in (3x/64, x], forward orbits "
              f"all pass through {a}: verified")
        print(f"        guaranteed bound (3x/64a)^c* = "
              f"{mpmath.nstr(bound, 6)}  <  {len(leaves)} = leaves;   "
              f"mass/[a^-c*] = {mpmath.nstr(mass / mass_floor, 6)} >= 1")
        print(f"        binding factor pair {{16/3,64/3}} (j0=1, smallest "
              f"candidate discarded) occurred in {worst_pair}/{splits} splits")
        results[(a, x)] = len(leaves)
    print()
    return results


# ---------------------------------------------------------------- part (4)
def part4_bruteforce(results, cstar, N: int = 10 ** 6):
    print(f"(4) Brute-force cross-check: true pi_5({N}) vs tree vs bound")
    res = {1: False, 2: False}
    cnt = 0
    for n in range(3, N + 1):
        if n == 5:
            res[n] = True
            cnt += 1
            continue
        v = n
        while True:
            v = T(v)
            if v == 5:
                r = True
                break
            if v < n:
                r = res[v]
                break
        res[n] = r
        cnt += r
    bound = (mpmath.mpf(3 * N) / (64 * 5)) ** cstar
    tree_leaves = results[(5, N)]
    print(f"    true pi_5({N}) = {cnt}  (exact, memoised forward iteration)")
    print(f"    chain: guaranteed bound {mpmath.nstr(bound, 6)} "
          f"< tree leaves {tree_leaves} < true count {cnt}   -- consistent")
    assert bound < tree_leaves < cnt
    print()


if __name__ == "__main__":
    print("Wave-2 lemma certification "
          "(predecessor-tree bound, exponent c* > 3/10)")
    print("=" * 74)
    cstar = part1_cstar()
    part2_two_children()
    results = part3_trees(cstar)
    part4_bruteforce(results, cstar)
    print("ALL CHECKS PASSED")
