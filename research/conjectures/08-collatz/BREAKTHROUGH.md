# Collatz — Wave-2 Breakthrough

**WAVE-2 LEGION 08.** Follow-up to `REPORT.md`. All computations quoted below were run in
this workspace; complete raw output is in `code/run_log.txt`. The new code is
`code/wave2_lemma_check.py`; the three Wave-1 scripts (`cycle_bound.py`,
`terras_density.py`, `cycles_z.py`) were re-run and their outputs re-certified first.

**This document does not claim a proof of the Collatz conjecture.** It proves one
conditional theorem — Krasikov–Lagarias-style divergence amplification with an explicit
exponent — by a complete, self-contained, elementary argument, and certifies its
combinatorial engine by machine.

---

## Theorem

Throughout, `T(n) = n/2` (n even), `(3n+1)/2` (n odd) is the accelerated Collatz map on
the positive integers, and for a positive integer `a`,

    pi_a(x) = #{ n <= x : T^k(n) = a for some k >= 0 }

counts the T-predecessors of `a` up to `x` (including `a` itself).

**Definition.** Let `c*` be the unique real root of

    (3/16)^c + (3/64)^c = 1.

Both terms are strictly decreasing in `c`, so the root is unique;
**certified below: 3/10 < c* < 31/100**; numerically `c* = 0.30201227557655948…`.

> **Theorem (Wave-2).**
>
> **(i) (Elementary predecessor bound.)** Let `a >= 3` be odd, not divisible by 3, and
> not an element of any T-cycle. Then for **every** `x >= a`,
>
>     pi_a(x) > (3x / 64a)^{c*}.
>
> **(ii) (Divergence amplification.)** Suppose some positive integer has a divergent
> Collatz orbit (equivalently: divergent T-orbit). Then that orbit contains an odd
> element `a`, not divisible by 3, such that for every `x >= a`
>
>     #{ n <= x : the orbit of n diverges }  >  (3x / 64a)^{c*}.
>
> In particular, if even one divergent orbit exists, the number of divergent starting
> values below `x` grows at least like a constant times `x^{3/10}` — with the fully
> explicit constant `(3/64a)^{c*}` and with no "for x sufficiently large" proviso.

Remarks. (a) The bound is completely effective: constant and threshold are explicit.
(b) By the published verification height 2^71 (Barina 2025; `REPORT.md` §3.6), any such
`a` necessarily exceeds 2^71, so the counting in (ii) has content only at astronomically
large `x` — as must be the case for a statement about a hypothetical counterexample.
(c) Divergence under `T`, under the Syracuse map, and under the unaccelerated Collatz
map `C` are equivalent (the three orbits interleave the same odd elements;
`REPORT.md` §2.1), so (ii) speaks about the Collatz map proper.

---

## Proof

All steps are elementary; nothing is used beyond arithmetic modulo 3 and induction.
The machine checks quoted in the transcript section verify the combinatorial engine
(Lemmas 1–2 exhaustively to 10^6, Lemmas 3–4 on demonstration trees) but the proof is
complete without them.

### Step 0: three trivial facts

**(D1)** If a value repeats in a T-orbit, the orbit is periodic from the first
occurrence on, hence bounded. Consequently a divergent orbit never repeats a value, and
no element of a divergent orbit lies in a cycle.

**(D2)** Every T-orbit on the positive integers contains infinitely many odd values:
if all values from some index on were even, the orbit would strictly decrease forever
(`T(v) = v/2 < v`), impossible in positive integers.

**(D3)** If `v` is odd then `T(v) ≡ 2 (mod 3)`, because `2·T(v) = 3v + 1 ≡ 1 (mod 3)`
and `2^{-1} ≡ 2 (mod 3)`. If `3 ∤ v` and `v` is even then `3 ∤ v/2 = T(v)`. Hence
**once an orbit has passed one odd step, every later element is ≢ 0 (mod 3)**.

### Step 1: inverse step (Lemma 1)

**Lemma 1.** Let `n >= 3` and `j >= 0` with `2^j n ≡ 2 (mod 3)`. Then

    m_j := (2^{j+1} n − 1) / 3

is an **odd integer >= 3** with `T^{j+1}(m_j) = n` and `3 m_j < 2^{j+1} n`.

*Proof.* `2^{j+1} n ≡ 2 · 2 ≡ 1 (mod 3)`, so `3 | 2^{j+1} n − 1` and `m_j` is a positive
integer. `2^{j+1} n − 1` is odd and equals `3 m_j`; since 3 is odd, `m_j` is odd
(3 · even is even). If `m_j = 1` then `2^{j+1} n = 4`, impossible for `n >= 3`; being
odd, `m_j >= 3`. Finally `3 m_j + 1 = 2^{j+1} n` gives `T(m_j) = (3m_j+1)/2 = 2^j n`,
and `j` further T-steps halve the even values `2^j n, 2^{j-1} n, …, 2n` down to `n`.
The size bound is immediate. ∎

### Step 2: the Two-Children Lemma (Lemma 2)

**Lemma 2.** Let `n >= 3`, `3 ∤ n`. Put `j0 = 0` if `n ≡ 2 (mod 3)` and `j0 = 1` if
`n ≡ 1 (mod 3)`. Then:

1. `2^j n ≡ 2 (mod 3)` holds exactly for `j ≡ j0 (mod 2)`; in particular for
   `j ∈ {j0, j0+2, j0+4}`, so Lemma 1 yields three candidates
   `m_{j0}, m_{j0+2}, m_{j0+4}`.
2. `m_{j+2} = 4 m_j + 1`; hence the three candidates are pairwise distinct and their
   residues mod 3 are `r, r+1, r+2` — all three classes. So **exactly one candidate is
   divisible by 3, and exactly two are not**.
3. Call the two candidates with `3 ∤ m` the **children** of `n`. Each child `m` is odd,
   `m >= 5`, `3 ∤ m`, `T^{j+1}(m) = n` for its `j <= j0 + 4 <= 5`, and
   `m < (2^{j+1}/3) n <= (64/3) n`. The pair of "size factors" `2^{j+1}/3` of the two
   children is worst (largest) when the discarded candidate is the smallest one and
   `j0 = 1`: it is then `{16/3, 64/3}`.

*Proof.* (1) The order of 2 mod 3 is 2, so `2^j n` alternates between `n` and `2n`
mod 3; since `3 ∤ n`, exactly one of `n, 2n` is `≡ 2 (mod 3)`.
(2) `m_{j+2} = (2^{j+3} n − 1)/3 = (4(2^{j+1} n − 1) + 3)/3 = 4 m_j + 1`, so
`m_{j+2} ≡ m_j + 1 (mod 3)`: three consecutive residues.
(3) By Lemma 1 each child is odd and `>= 3`; being also `≢ 0 (mod 3)`, it is `>= 5`.
The available `j` are `{j0, j0+2, j0+4} ⊆ {0,…,5}`. Discarding one candidate leaves
factor pairs, ordered from mildest to worst:
for `j0 = 0`: `{2/3, 8/3}`, `{2/3, 32/3}`, `{8/3, 32/3}`;
for `j0 = 1`: `{4/3, 16/3}`, `{4/3, 64/3}`, `{16/3, 64/3}`.
The componentwise largest pair is `{16/3, 64/3}`. ∎

*(Example with the binding case: `n = 7 ≡ 1 (mod 3)`, `j0 = 1`: candidates
`m_1 = 9` (divisible by 3, discarded), `m_3 = 37`, `m_5 = 149`; indeed `T^4(37) = 7`,
`T^6(149) = 7`. Machine check: exhaustive for all `n <= 10^6` in the transcript.)*

### Step 3: tree injectivity (Lemma 3)

**Lemma 3.** Let `a >= 3` be odd, `3 ∤ a`, and not an element of any T-cycle. Define the
infinite rooted binary tree `𝒯(a)`: the root carries value `a`; every node with value
`n` has as children the two children of `n` from Lemma 2. Then every node value is a
T-predecessor of `a`, and **the values of distinct nodes are distinct integers**.

*Proof.* Every node value is odd, `≥ 3`, `≢ 0 (mod 3)` (root by hypothesis, children by
Lemma 2), so the construction never halts; composing Lemma 1 along the path from a node
to the root gives `T^s(value) = a` for some `s >= 0`.

(1) *`a` occurs at most once in any forward orbit.* If `T^i(m) = T^{i'}(m) = a` with
`i < i'`, then `T^{i'-i}(a) = a`, making `a` a cycle element — excluded.

(2) *The branch of a node is readable off its forward orbit.* Let `u` be a node with
value `m`, depth `d >= 1`, and parent value `p`. The orbit of `m` starts
`m, 2^j p, 2^{j-1} p, …, 2p, p`: every value strictly between `m` and `p` is even
(there are none if `j = 0`). So `p` is the **first odd value after `m`** in the orbit
of `m`. Iterating: the sequence of odd values of the forward orbit of `m`, up to the
first (by (1): only) occurrence of `a`, is exactly the branch of `u` read upward:
`m`, parent value, grandparent value, …, `a`.

(3) *Branch values determine the node.* The two children of any node have distinct
values (`m_{j+2} = 4 m_j + 1`, `m_{j+4} = 16 m_j + 5`). So, descending from the root,
each successive branch value selects a unique child: the branch value sequence
determines the tree path.

Now suppose distinct nodes `u ≠ v` had the same value `m`. By (2) both branches equal
the same odd-value sequence of the single forward orbit of `m`; by (3) equal branch
sequences force equal paths, i.e. `u = v`. Contradiction. ∎

### Step 4: weighted counting (Lemma 4 — the mass argument)

**Lemma 4.** Let `a` be as in Lemma 3 and `x >= 64a/3`. Then the number of distinct
T-predecessors of `a` lying in `(3x/64, x]` is `> (3x/64a)^{c*}`.

*Proof.* Run the **stopped process**: start with the one-node tree `{a}`; while some
leaf has value `v <= 3x/64`, split it, i.e. attach its two children (Lemma 2).

*All values stay `<= x`:* a split leaf has `v <= 3x/64`, and its children are
`< (64/3) v <= x`. The root satisfies `a <= 3x/64` by hypothesis.

*Termination:* by Lemma 3 all node values are pairwise distinct positive integers
`<= x`, so at most `x` nodes are ever created; each split adds two, so the process
stops. At termination every leaf value lies in `(3x/64, x]`.

*Mass is non-decreasing:* let `Φ = Σ_{leaves} (value)^{-c*}`; initially `Φ = a^{-c*}`.
A split replaces `v^{-c*}` by `m_1^{-c*} + m_2^{-c*}` with `m_i < (2^{j_i+1}/3) v`
(Lemma 2), hence

    m_1^{-c*} + m_2^{-c*} > [ (3/2^{j_1+1})^{c*} + (3/2^{j_2+1})^{c*} ] · v^{-c*}
                          >= [ (3/16)^{c*} + (3/64)^{c*} ] · v^{-c*}  =  v^{-c*},

where the middle inequality holds because `{3/16, 3/64}` is the componentwise smallest
factor pair that Lemma 2 permits, and the final equality is the definition of `c*`.

So at termination `Σ_{leaves} (value)^{-c*} >= a^{-c*}`, while every leaf contributes
`< (3x/64)^{-c*}` (its value exceeds `3x/64`). With `N` leaves:

    N · (3x/64)^{-c*} > a^{-c*},   i.e.   N > (3x/64a)^{c*}.

The leaves are pairwise distinct T-predecessors of `a` in `(3x/64, x]` (Lemma 3). ∎

### Step 5: the exponent (certified)

`f(c) = (3/16)^c + (3/64)^c` is strictly decreasing with `f(0) = 2` and `f(1) < 1`,
so `c*` exists and is unique. Exact integer certificates (see transcript, part (1);
no floating point):

- at `c = 3/10`: `(3/16)^{3/10} + (3/64)^{3/10} = (27/4096)^{1/10} + (27/262144)^{1/10} > 1`,
  certified by integer 10-th roots at scale 10^30 (margin `4.49·10^{-3}`), so `c* > 3/10`;
- at `c = 31/100`: certified `< 1` by integer 100-th roots (margin `1.76·10^{-2}`),
  so `c* < 31/100`.

Bisection at 40 significant digits gives `c* = 0.3020122755765594830905774…`.

### Step 6: proof of the Theorem

**(i)** If `x >= 64a/3`, Lemma 4 already exhibits more than `(3x/64a)^{c*}` distinct
predecessors of `a` that are `<= x`. If `a <= x < 64a/3`, then `(3x/64a)^{c*} < 1`
while `pi_a(x) >= 1` (count `a` itself, `k = 0`). ∎

**(ii)** Let some positive orbit diverge. By (D2) it contains infinitely many odd
values; by (D3) all values after its first odd step are `≢ 0 (mod 3)`. Choose `a` = any
odd orbit value occurring after the first odd step. Then `a` is odd, `3 ∤ a`, `a >= 3`,
its orbit diverges, and by (D1) `a` is in no cycle — so `a` satisfies the hypotheses of
part (i). Every T-predecessor `n` of `a` has an orbit that reaches `a` and then follows
`a`'s divergent orbit, so `n` diverges. By (i), for every `x >= a` there are more than
`(3x/64a)^{c*}` such `n <= x`. Since `c* > 3/10`, this is `≫ x^{3/10}`. ∎

---

## Computation transcript (if any)

Full raw log: `code/run_log.txt` (all five script runs, verbatim, with exit codes).
Environment: Python 3.12.3, mpmath 1.4.1, 2026-08-15 UTC.

**(a) Wave-1 scripts re-run (outputs match `REPORT.md` §§2.3, 5.1, 5.2 exactly).**
Cycle-exclusion pipeline (`cycle_bound.py`): reproduces Eliahou's 17,087,915 at height
2^40 and certifies, at the published height 2^71 (Barina 2025 — the only verification
height this dossier uses; no unsourced heights are invoked):

```
--- verification height B = 2^71  (Barina 2025) ---
  simplest fraction K/L in (log2 3, log2(3+1/B)] : 114208327604/72057431991
  => any nontrivial cycle has  L >= 72057431991  odd elements,
     K >= 114208327604  elements per period under T,
     K+L >= 186265759595  steps under the unaccelerated Collatz map.
```

Terras densities (`terras_density.py`): exact to k = 120
(`D_120 = 131320930040438275830258155402960 / 2^120 ≈ 9.88·10^-5`). Integer-cycle scan
(`cycles_z.py`): the five known cycles verified; all 4,000,001 integers `|n| <= 2·10^6`
land in one of them.

**(b) New Wave-2 certification (`wave2_lemma_check.py`), verbatim:**

```
Wave-2 lemma certification (predecessor-tree bound, exponent c* > 3/10)
==========================================================================
(1) The exponent c*: unique root of (3/16)^c + (3/64)^c = 1
    exact certificate at c = 3/10 : (lo1+lo2-S)/S = 4.486476e-03 > 0   =>  c* > 3/10
    exact certificate at c = 31/100: (S-hi1-hi2)/S = 1.759425e-02 > 0   =>  c* < 31/100
    c* = 0.3020122755765594830905774  (bisection, 40 dps)

(2) Two-Children Lemma, exhaustive for 3 <= n <= 1000000, 3 not | n
    verified for 666665 values of n: exactly two children each
    discarded candidate was m_(j0)/m_(j0+2)/m_(j0+4) in 222222/222222/222221 cases
    (worst case for the bound = discarding m_(j0): 222222 cases, factors then {2^(j0+3)/3, 2^(j0+5)/3})

(3) Stopped predecessor trees (theorem engine, demonstration roots)
    a=5, x=10^6: nodes=13041, splits=6520, leaves=6521, max depth=78
        all leaves distinct, in (3x/64, x], forward orbits all pass through 5: verified
        guaranteed bound (3x/64a)^c* = 15.8338  <  6521 = leaves;   mass/[a^-c*] = 290.629 >= 1
        binding factor pair {16/3,64/3} (j0=1, smallest candidate discarded) occurred in 1102/6520 splits
    a=5, x=10^7: nodes=114381, splits=57190, leaves=57191, max depth=106
        all leaves distinct, in (3x/64, x], forward orbits all pass through 5: verified
        guaranteed bound (3x/64a)^c* = 31.7392  <  57191 = leaves;   mass/[a^-c*] = 1271.13 >= 1
        binding factor pair {16/3,64/3} (j0=1, smallest candidate discarded) occurred in 9550/57190 splits
    a=5, x=10^8: nodes=988819, splits=494409, leaves=494410, max depth=155
        all leaves distinct, in (3x/64, x], forward orbits all pass through 5: verified
        guaranteed bound (3x/64a)^c* = 63.6222  <  494410 = leaves;   mass/[a^-c*] = 5484.05 >= 1
        binding factor pair {16/3,64/3} (j0=1, smallest candidate discarded) occurred in 82272/494409 splits
    a=7, x=10^7: nodes=23335, splits=11667, leaves=11668, max depth=73
        all leaves distinct, in (3x/64, x], forward orbits all pass through 7: verified
        guaranteed bound (3x/64a)^c* = 28.6724  <  11668 = leaves;   mass/[a^-c*] = 287.612 >= 1
        binding factor pair {16/3,64/3} (j0=1, smallest candidate discarded) occurred in 1926/11667 splits

(4) Brute-force cross-check: true pi_5(1000000) vs tree vs bound
    true pi_5(1000000) = 937711  (exact, memoised forward iteration)
    chain: guaranteed bound 15.8338 < tree leaves 6521 < true count 937711   -- consistent

ALL CHECKS PASSED
```

Interpretation of (3): the demonstration roots `a = 5, 7` are of course convergent (no
divergent orbit is known — none is claimed); the runs certify by machine every
mechanical ingredient of Lemmas 2–4 (two children always exist; all tree values
distinct — Lemma 3's injectivity never fails across ~10^6 nodes; leaves land in
`(3x/64, x]`; mass never drops below `a^{-c*}`; the final count beats the guaranteed
bound, by a wide margin since the guaranteed exponent 0.302 is far below the empirical
tree-growth exponent ≈ 0.8, consistent with the literature's `x^{0.84}`).

---

## What is new vs REPORT.md

- `REPORT.md` §5.3, Corollary 5 already stated divergence amplification with the
  stronger exponent 0.84 — but only by invoking Krasikov–Lagarias (2003) as a **black
  box** (their bound rests on computer-aided linear programming over difference
  inequalities). Wave-2 replaces the black box: **part (i) is proved here from
  scratch**, in two pages of elementary arithmetic, with the explicit exponent
  `c* = 0.30201… > 3/10` — a complete elementary proof of a positive `c`, which is
  exactly what Corollary 5 lacked.
- The Wave-2 bound is **fully effective and non-asymptotic**: it holds for every
  `x >= a` with the explicit constant `(3/64a)^{c*}`, whereas the Krasikov–Lagarias
  route gives "for all sufficiently large x" with an unspecified threshold.
- The bound is **uniform in the root `a`** (any odd `a >= 3`, `3 ∤ a`, not on a cycle),
  and the transfer to divergent seeds (Step 6(ii), via D1–D3) is written out with all
  hypotheses discharged, including the choice of an admissible `a` inside the divergent
  orbit.
- New machine artefacts: exact integer certificates for `3/10 < c* < 31/100`; an
  exhaustive verification of the Two-Children Lemma to 10^6; stopped-tree runs
  validating injectivity, the mass inequality and the final bound; and a brute-force
  `pi_5(10^6) = 937,711` cross-check. None of this existed in Wave-1.
- **What is explicitly not claimed as new to mathematics:** predecessor-tree counting
  is the classical route (Crandall 1978 obtained `pi_1(x) > x^{0.05}` elementarily;
  Krasikov 1989, Applegate–Lagarias 1995, Krasikov–Lagarias 2003 pushed it to
  `x^{3/7}`, `x^{0.81}`, `x^{0.84}` with increasing machinery; Wirsching 1998 develops
  the 3-adic tree theory). Experts would regard a bound of this shape as known in
  principle. We did not find, in the sources listed in `REPORT.md` §7, this specific
  statement — the equation `(3/16)^c + (3/64)^c = 1` for the exponent, the everywhere-
  explicit constant, and the packaged divergence-amplification form — but we assume it
  is folklore-adjacent and claim only the self-contained write-up and certification.

## Why Collatz remains open

Nothing above touches the two live questions (`REPORT.md` §6):

- **Existence is untouched.** The theorem is conditional ("if one divergent orbit
  exists, divergent seeds are `≫ x^{3/10}`-abundant"). It squeezes the exceptional set
  from below, complementing Tao's logarithmic-density-zero squeeze from above — the two
  are consistent (an `x^{0.84}`- or `x^{0.302}`-sized set is log-density zero), so no
  contradiction can be extracted from this pincer, and emptiness cannot be decided by
  density statements at all (`REPORT.md` §6.5).
- **The mirror test.** The whole argument survives the sign flip: for `3x − 1` the
  inverse step is `m = (2^{j+1} n + 1)/3` and Lemmas 1–4 go through verbatim, where
  nontrivial cycles actually exist. So this machinery is constitutionally unable to
  prove "no divergent orbits/no cycles" — it counts predecessors of whatever exists
  (`REPORT.md` §6.1).
- **Cycles remain irreducibly Diophantine** — governed by the quality of rational
  approximations `K/L` to `log₂3` (re-certified here at height 2^71: any nontrivial
  cycle needs ≥ 186,265,759,595 Collatz steps by the pure Eliahou pipeline; the
  published Hercher + Barina record is ≥ 355,504,839,929) — and current linear-forms-
  in-logarithms technology is quantitatively far too weak to finish (`REPORT.md` §6.3).
- Tao's method stalls structurally at "almost bounded" (`f → ∞` is load-bearing), and
  measure-theoretic tools cannot see the Haar-null integers inside `Z₂`
  (`REPORT.md` §§6.2, 6.4).

## Honesty label

**[SYNTHESIS / ELEMENTARY RECONSTRUCTION — with certified computation. No claim of
novelty to experts. No proof, and no claimed progress on the truth, of the Collatz
conjecture.]**

Itemised:

- Theorem (i)+(ii) and Lemmas 1–4, D1–D3: **proved completely in this document**;
  elementary; believed folklore-adjacent (Crandall-style); the specific constants and
  packaging were assembled here and not found stated in the sources read.
- `3/10 < c* < 31/100`: **[CERTIFIED, exact integer arithmetic]** (`run_log.txt`, part 1).
- Two-Children Lemma to `n <= 10^6`: **[CERTIFIED, exhaustive]** (part 2); for all `n`:
  proved (Lemma 2).
- Tree demonstrations and `pi_5(10^6) = 937,711`: **[COMPUTED HERE]** (parts 3–4);
  demonstration roots are convergent; they certify the engine, not divergence.
- Wave-1 recomputations (cycle bounds at 2^71, Terras table, integer-cycle scan):
  **[KNOWN, RECOMPUTED HERE]** — outputs match `REPORT.md`; only the published
  verification height 2^71 (Barina 2025) is used, per `REPORT.md` §3.6; no unpublished
  or unsourced heights are invoked.
- Exponent comparison stated plainly: the published record for predecessor counts is
  `x^{0.84}` (Krasikov–Lagarias 2003, computer-aided); our `x^{0.302}` is weaker as a
  number and stronger only in proof economy (self-contained, effective, uniform).
- No statement in this file asserts or implies that the Collatz conjecture, the
  no-divergence half, or the no-cycle half has been resolved. They remain **[OPEN]**.
