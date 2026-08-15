# Wave 2 — ten checkable breakthroughs

**Date:** 2026-08-15
**Method:** a second parallel Fable-5-max (`claude-fable-5-thinking-xhigh`) pass. Each legion was forbidden to rewrite its survey and was required to deliver **one theorem with a complete proof** (or a machine transcript).

**Standing claim, unchanged:** none of the ten conjectures is proved. Wave 2 upgrades Wave 1’s *named walls* into *checkable theorems*.

| Legion | Theorem (short) | File | Honesty |
|--------|-----------------|------|---------|
| 01 | Finite Li positivity cannot see off-line zeros below height \(\asymp\sqrt{N}\); first 2000 Li coefficients computed | `01-riemann/BREAKTHROUGH.md` | New (proved here) + computational |
| 02 | Deterministic hardness-certification probe complexity is \(\Theta(s\log s/n)\): \((s\log_2 s)/(20n) < D_n(s) \le 3s\log_2 s+1\) | `02-p-vs-np/BREAKTHROUGH.md` | New (proved here; elementary) |
| 03 | BSD I for the infinite family \(y^2=x^3-p^2x\), \(p\equiv 3\pmod 8\); gp sweep of 2214 curves of conductor \(\le 500\) | `03-bsd/BREAKTHROUGH.md` | Classical content, fully written + computed |
| 04 | Self-contained Lefschetz (1,1); Hodge for abelian fourfolds reduced to named theorems | `04-hodge/BREAKTHROUGH.md` | Known, proof written out |
| 05 | Beale–Kato–Majda at enstrophy level, Grönwall constant exactly 2 | `05-navier-stokes/BREAKTHROUGH.md` | Known, proof written out |
| 06 | Two-Gate Localization: fixed strong coupling is ultralocal; Abelian falsifier | `06-yang-mills/BREAKTHROUGH.md` | Synthesis from established inputs |
| 07 | \(M_2\le 2\log 2<2\) proved in-file; explicit admissible 50-tuple of 25 twin pairs, diameter 752 | `07-twin-primes/BREAKTHROUGH.md` | Polymath ceiling proved here; new small lemma |
| 08 | One divergent orbit \(\Rightarrow \gg x^{3/10}\) divergent starters; scripts re-run | `08-collatz/BREAKTHROUGH.md` | Elementary reconstruction |
| 09 | Modulus Barrier as a single theorem: \(M_{\min}=\int_{\mathfrak m}\|S\|^2\), gap \(\asymp\log N\) | `09-goldbach/BREAKTHROUGH.md` | Folklore formalized + small Goldbach check to \(10^5\) |
| 10 | Mason–Stothers + polynomial Fermat; \(P(abc)>2\log\log c\) from Stewart–Yu | `10-abc/BREAKTHROUGH.md` | Function-field proved; number-field conditional on Stewart–Yu |

## How this is a research breakthrough (and how it is not)

It **is** a breakthrough in the only sense this program can honestly claim: each popular attack is now blocked by a **statement a referee can check**, not by a slogan. Several items include live computation (Li coefficients, Pari/GP BSD, Collatz cycle bounds, Goldbach to \(10^5\)).

It **is not** a breakthrough in the Clay / Annals sense. No zero was moved onto the critical line, no SAT circuit lower bound was proved, no rank-2 Euler system was built, no 3D NS solution was continued, no 4D YM continuum limit was constructed, and abc is not taken as proved via IUT.

## Read order

1. This file (one-line theorems).
2. The matching `BREAKTHROUGH.md` (the proof).
3. The Wave-1 `REPORT.md` (landscape and why the theorem is the wall).
4. `SYNTHESIS.md` (cross-legion pattern).
