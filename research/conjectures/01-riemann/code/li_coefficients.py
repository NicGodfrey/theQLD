#!/usr/bin/env python3
"""
Compute the Li coefficients lambda_n of the Riemann xi function, n = 1..N,
by Cauchy-coefficient extraction from Li's generating function

    d/dz log xi(1/(1-z))  =  sum_{n>=0} lambda_{n+1} z^n ,        (Li 1997)

using   g(z) = s^2 * (xi'/xi)(s),  s = 1/(1-z),
        xi'/xi(s) = 1/s + 1/(s-1) - (1/2) log pi + (1/2) psi(s/2) + zeta'(s)/zeta(s).

This avoids any log-branch issue (we never take log xi) and any power-series
division (no catastrophic cancellation): g is evaluated directly and its Taylor
coefficients are read off with a discrete Fourier transform on |z| = r.

Analyticity of g on |z| <= 0.995: a pole of g at z = 1 - 1/rho (rho a zeta zero)
satisfies |z_rho|^2 = 1 - (2 beta - 1)/|rho|^2 >= 1 - 1/|rho|^2; hence
|z_rho| <= 0.995 would force |rho|^2 <= 1/(1-0.995^2) < 100.3, i.e. |Im rho| <= 11,
contradicting the classical fact (Gram/Backlund, 1903-1914) that zeta has no
nontrivial zero with 0 < |Im rho| <= 14.  Zeros ON the critical line sit exactly
on |z| = 1 and never enter.

Error control (heuristic, floating point, NOT interval arithmetic):
  - trapezoidal rule on M points gives  hat c_n * r^{-n} = lambda_{n+1} + aliasing,
    aliasing = sum_{k>=1} a_{n+kM} r^{kM},  |a_j| <= G(r*) r*^{-j}  (r* = 0.995),
    so |aliasing| <= G(r*) (r/r*)^M r*^{-n} / (1 - (r/r*)^M).
  - rounding: working precision dps=40, amplified by r^{-n} <= 0.99^{-N}.
Both are reported below.  Two independent radii cross-validate.

Usage:  python3 li_coefficients.py [N] [M] [quick]
"""
import sys, time, csv
from mpmath import mp, mpf, mpc, pi, log, exp, digamma, zeta, cos, sin, sqrt, euler

mp.dps = 40

N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
M     = int(sys.argv[2]) if len(sys.argv) > 2 else 8192
R1    = sys.argv[3] if len(sys.argv) > 3 else '0.99'
R2    = sys.argv[4] if len(sys.argv) > 4 else '0.985'
assert M >= 2 * N_MAX and (M & (M - 1)) == 0, "M must be a power of 2, >= 2*N"

HALF_LOG_PI = log(pi) / 2

def xi_logderiv(s):
    """xi'(s)/xi(s) for xi(s) = (1/2) s (s-1) pi^{-s/2} Gamma(s/2) zeta(s)."""
    return (1/s + 1/(s-1) - HALF_LOG_PI + digamma(s/2)/2
            + zeta(s, derivative=1)/zeta(s))

def g(z):
    s = 1/(1 - z)
    return s*s * xi_logderiv(s)

def fft(a, invert=False):
    """Iterative radix-2 Cooley-Tukey FFT over mpmath complex numbers."""
    n = len(a)
    a = list(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        ang = 2 * pi / length * (1 if invert else -1)
        wlen = mpc(cos(ang), sin(ang))
        for i in range(0, n, length):
            w = mpc(1)
            half = length >> 1
            for k in range(i, i + half):
                u = a[k]
                v = a[k + half] * w
                a[k] = u + v
                a[k + half] = u - v
                w *= wlen
        length <<= 1
    if invert:
        a = [x / n for x in a]
    return a

def lambdas_for_radius(r):
    """Return [lambda_1 .. lambda_N_MAX] computed on circle |z| = r."""
    r = mpf(r)
    t0 = time.time()
    # conjugate symmetry: g(conj z) = conj g(z), so evaluate half the circle
    vals = [None] * M
    for m in range(M // 2 + 1):
        theta = 2 * pi * m / M
        z = r * mpc(cos(theta), sin(theta))
        vals[m] = g(z)
        if m % 512 == 0:
            print(f"    eval m={m}/{M//2}  ({time.time()-t0:.0f}s)", flush=True)
    for m in range(M // 2 + 1, M):
        vals[m] = vals[M - m].conjugate()
    print(f"    evaluations done in {time.time()-t0:.0f}s", flush=True)
    t1 = time.time()
    coeffs = fft(vals)          # coeffs[n] = sum_m vals[m] e^{-2 pi i mn/M}
    print(f"    FFT done in {time.time()-t1:.0f}s", flush=True)
    lams = []
    rn = mpf(1)
    for n in range(N_MAX):      # c_n = coeffs[n]/M,  lambda_{n+1} = c_n / r^n
        lams.append((coeffs[n] / M / rn).real)
        rn *= r
    return lams

def main():
    print(f"N = {N_MAX}, M = {M}, dps = {mp.dps}, radii = {R1}, {R2}")
    print(f"radius r1 = {R1} ...", flush=True)
    lam1 = lambdas_for_radius(R1)
    print(f"radius r2 = {R2} ...", flush=True)
    lam2 = lambdas_for_radius(R2)

    maxdiff = max(abs(a - b) for a, b in zip(lam1, lam2))
    print(f"max |lambda(r1) - lambda(r2)| over n<=N : {mp.nstr(maxdiff, 6)}")

    # closed-form anchor: lambda_1 = 1 + gamma/2 - (1/2) log(4 pi)
    lam1_exact = 1 + euler/2 - log(4*pi)/2
    print(f"lambda_1 computed  = {mp.nstr(lam1[0], 25)}")
    print(f"lambda_1 exact     = {mp.nstr(lam1_exact, 25)}")
    print(f"|difference|       = {mp.nstr(abs(lam1[0]-lam1_exact), 6)}")

    # aliasing bound (heuristic): G(0.995) ~ sup |g| on |z|=0.995, sampled coarsely
    # g is analytic on |z| <= 0.995 (see module docstring), so coefficients of g
    # obey |a_j| <= G(0.995) * 0.995^{-j} with G the sup on that circle.
    rstar = mpf('0.995')
    G = max(abs(g(rstar * mpc(cos(2*pi*k/256), sin(2*pi*k/256)))) for k in range(129))
    q = (mpf(R1) / rstar) ** M
    alias = G * q / (1 - q) * rstar ** (-(N_MAX - 1))
    print(f"sup|g| on |z|=0.995 (sampled): {mp.nstr(G, 6)}")
    print(f"aliasing bound at n=N: {mp.nstr(alias, 6)}")

    ratios = [lam1[n] / (n + 1) for n in range(N_MAX)]
    cmin = min(ratios)
    nmin = ratios.index(cmin) + 1
    print(f"min_(n<=N) lambda_n / n = {mp.nstr(cmin, 15)}   attained at n = {nmin}")

    ok = all(lam1[n] > mpf('0.0230') * (n + 1) for n in range(N_MAX))
    print(f"lambda_n >= 0.0230 * n for all n <= {N_MAX} : {ok}")

    with open('li_lambda.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n', 'lambda_n', 'lambda_n_over_n'])
        for n in range(N_MAX):
            w.writerow([n + 1, mp.nstr(lam1[n], 30), mp.nstr(ratios[n], 30)])
    print("wrote li_lambda.csv")

    print("\nsample values:")
    for n in [1,2,3,4,5,6,7,8,9,10,20,50,100,200,500,1000,1500,2000]:
        if n <= N_MAX:
            print(f"  lambda_{n:5d} = {mp.nstr(lam1[n-1], 20)}   lambda/n = {mp.nstr(ratios[n-1], 12)}")

if __name__ == '__main__':
    main()
