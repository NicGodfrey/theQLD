#!/usr/bin/env python3
"""
Verification of the known cycles of T(n) = n/2 (n even), (3n+1)/2 (n odd)
over ALL integers (positive, zero, negative), plus an exhaustive check that
every starting value |n| <= 2*10^6 falls into one of the five known cycles.
"""

def T(n: int) -> int:
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


KNOWN_CYCLES = {
    "trivial(+)": [1, 2],
    "zero": [0],
    "neg-1": [-1],
    "neg-5": [-5, -7, -10],
    "neg-17": [-17, -25, -37, -55, -82, -41, -61, -91, -136, -68, -34],
}


def check_cycles():
    for name, cyc in KNOWN_CYCLES.items():
        for i, v in enumerate(cyc):
            assert T(v) == cyc[(i + 1) % len(cyc)], (name, v)
        print(f"  cycle {name:<10} length {len(cyc):>2} under T : {cyc}  -- verified")


def exhaustive_scan(limit: int):
    cycle_members = {v for cyc in KNOWN_CYCLES.values() for v in cyc}
    landed = {name: 0 for name in KNOWN_CYCLES}
    member_of = {v: name for name, cyc in KNOWN_CYCLES.items() for v in cyc}
    for n in range(-limit, limit + 1):
        v = n
        steps = 0
        while v not in cycle_members:
            v = T(v)
            steps += 1
            assert abs(v) < 10 ** 30 and steps < 10 ** 6, f"suspicious orbit from {n}"
        landed[member_of[v]] += 1
    total = 2 * limit + 1
    print(f"  scanned all |n| <= {limit} ({total} integers): every orbit entered a known cycle")
    for name, cnt in landed.items():
        print(f"    -> {name:<10}: {cnt} starting values")


if __name__ == "__main__":
    print("Known cycles of T on the integers:")
    check_cycles()
    print()
    print("Exhaustive scan:")
    exhaustive_scan(2 * 10 ** 6)
