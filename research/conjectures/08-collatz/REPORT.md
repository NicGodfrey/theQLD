# LEGION 08 — The Collatz (3x+1) Conjecture

**Commander dossier — research program "TOP-10 Unsolved Conjectures"**

> **Execution disclosure.** The mission ordered ten nested specialist subagents (08-01 … 08-10).
> The execution environment provided to this commander exposes no sub-task tool, so all ten
> angles were executed directly by the commander, serially, with the same scope each specialist
> would have had. The per-angle attack log is in Section 4. All computations in this dossier
> were run in this workspace (`code/`) and their outputs are reproduced verbatim.
>
> **Honesty protocol.** Every claim carries one of these labels:
> - **[KNOWN]** — established result; citation given and verified (see ledger in Section 7).
> - **[KNOWN, RECOMPUTED HERE]** — known method or quantity independently recomputed and
>   certified by code in this dossier.
> - **[SYNTHESIS]** — a corollary assembled here from known results; presumed known to
>   experts; no claim of novelty is made.
> - **[NO-GO ANALYSIS]** — a structured argument about the limits of current methods,
>   assembled here from known ingredients.
> - **[HEURISTIC]** — probabilistic or non-rigorous reasoning, clearly not a proof.
> - **[OPEN]** — open problem.
>
> **This dossier does not claim a proof of the Collatz conjecture, and no such claim exists
> in the literature.**

---

## 1. Executive Summary and Verdict

The Collatz conjecture remains open. This legion produced no proof and — per mission rules —
fabricates none. The dossier's concrete products are:

1. **A certified, updated cycle-exclusion bound** [KNOWN, RECOMPUTED HERE]. Using the
   cycle-ratio identity and the simplest-fraction (Stern–Brocot) principle — the method of
   Eliahou (1993) — combined with the currently *published* verification height 2^71
   (Barina 2025), we certify with exact interval arithmetic: any nontrivial positive cycle
   has at least **72,057,431,991 odd elements**, at least **114,208,327,604 elements per
   period** of the accelerated map T, and at least **186,265,759,595 steps** of the
   unaccelerated Collatz map. The pipeline validates itself by reproducing Eliahou's
   published 17,087,915 exactly at his assumed height 2^40. The state of the art is
   stronger still: Hercher (2023) + Barina (2025) give ≥ 137,528,045,312 odd elements
   (≥ 355,504,839,929 Collatz steps); our computation independently locates exactly that
   figure as the *next Stern–Brocot plateau* and shows pure Eliahou reaches it once
   verification passes B* ≈ 2^71.88 (Section 5.1).
2. **An exact recomputation of the Terras stopping-time densities** [KNOWN, RECOMPUTED
   HERE], with exact integer arithmetic up to k = 120, matching the classical tables and
   exhibiting the slow O(log k / k) approach to the decay exponent η = 1 − H(log₃2) ≈ 0.05004
   (Section 5.2).
3. **A precise account of Tao's theorem** (2019 arXiv / 2022 Forum of Mathematics, Pi) and
   of exactly why "almost all orbits attain almost bounded values" in *logarithmic density*
   is far from the conjecture (Sections 3.1, 5.4, 6.4, 6.5).
4. **The main intellectual product: a four-wall no-go analysis** [NO-GO ANALYSIS]
   explaining structurally why the entire stopping-time/density toolchain — Terras,
   Allouche, Korec, and Tao's measure-stabilization method — cannot by itself finish the
   conjecture: (i) the **mirror wall** (every such argument holds verbatim for 3x−1, where
   the conclusion is false); (ii) the **2-adic ergodic wall** (Z is Haar-null in Z₂, where
   the dynamics is exactly solvable); (iii) the **Diophantine wall** (current linear-forms-
   in-logarithms technology is quantitatively too weak to exclude unrestricted cycles);
   (iv) the **invariance-loss wall** internal to Tao's method (why f → ∞ is essential).
   Section 6, including a consistency check: the conjunction of *all* known theorems is
   satisfied by a hypothetical world containing a counterexample.

**Verdict: known + incremental.** The recomputations are incremental but real and fully
certified; the no-go analysis is a synthesis with, to our knowledge, one cleanly stated
folklore corollary (Section 5.3, C5: one divergent orbit forces ≥ x^0.84 divergent starting
values below x) that we did not find stated explicitly in the sources we read. Nothing here
is a candidate breakthrough toward the full conjecture, and we say so plainly.

---

## 2. Precise Statement, Maps, and Known Cycles (angle 08-01)

### 2.1 The three standard maps [KNOWN]

On the positive integers:

- **Collatz map** C(n) = 3n + 1 if n is odd, n/2 if n is even.
- **Accelerated map** T(n) = (3n+1)/2 if n is odd, n/2 if n is even. (3n+1 is always even,
  so T merges the guaranteed halving into the odd step.)
- **Syracuse map** (odd-to-odd) Syr(n) = (3n+1)/2^{ν₂(3n+1)} on odd n, where ν₂ is the
  2-adic valuation. This is the map Tao works with.

The three maps have identical orbit structure up to bookkeeping. **Collatz conjecture:**
for every n ≥ 1 some iterate C^k(n) = 1; equivalently T-orbits all reach the cycle {1, 2};
equivalently Syr-orbits all reach 1. Equivalently again: (a) there is no nontrivial cycle
on Z⁺, and (b) there is no divergent orbit on Z⁺.

### 2.2 Parity vectors and the depth-k formula [KNOWN]

Write x_i ∈ {0,1} for the parity of T^i(n) and L_k = x_0 + ... + x_{k−1}. Then

    T^k(n) = (3^{L_k} n + ρ_k) / 2^k,   ρ_0 = 0,   ρ_{k+1} = 3^{x_k} ρ_k + x_k 2^k,

so ρ_k = Σ_{i<k} x_i 2^i 3^{L_k − L_{i+1}} ≥ 0. The first k parities depend only on
n mod 2^k, and every parity vector in {0,1}^k is realized by exactly one residue class
mod 2^k (Terras 1976). This bijection is the engine of every density result.

For a cycle, T^K(n) = n yields the **Böhm–Sontacchi equation** [KNOWN]:
n (2^K − 3^L) = ρ_K, a finite sum of terms 3^a 2^b — a purely Diophantine constraint.

### 2.3 All known cycles over the integers [KNOWN, RECOMPUTED HERE]

Extending T to all of Z, exactly five cycles are known (`code/cycles_z.py`, verified, plus
an exhaustive scan showing every |n| ≤ 2·10⁶ lands in one of them):

| cycle (under T) | length | domain |
|---|---|---|
| {1, 2} | 2 | positive (the trivial cycle; under C it is 1 → 4 → 2) |
| {0} | 1 | zero |
| {−1} | 1 | negative |
| {−5, −7, −10} | 3 | negative |
| {−17, −25, −37, −55, −82, −41, −61, −91, −136, −68, −34} | 11 | negative |

Basin statistics from the scan: of the 4,000,001 integers |n| ≤ 2·10⁶, the three negative
cycles capture 654,579 / 648,087 / 697,334 starting values respectively — three coexisting
attractors of comparable basin size. This is the single most important *warning datum* in
the whole subject (Section 6.1): the negative half of Z has the same drift statistics as
the positive half and yet has multiple nontrivial cycles.

Over the positive integers, {1, 2} is the only known cycle, and any other has astronomical
size (Section 5.1). It is a theorem that every cycle of T on Z₂ is rational [KNOWN;
Lagarias 1985 framework, cf. Section 3.5].

---

## 3. State of the Art — verified survey

### 3.1 Density and stopping times (angle 08-02) [KNOWN]

Define the **stopping time** σ(n) = least k with T^k(n) < n (∞ if none). Results, in
chronological order; all citations verified (Section 7):

- **Terras (1976)**, independently **Everett (1977)** (also Möller 1977, Heppner 1978 for
  Hasse-type generalizations): the set {n : σ(n) ≤ k} has a natural density F(k) for each
  k, and F(k) → 1. So **almost every n (natural density) has an iterate below n**.
- **Lagarias (1985)**: quantitatively, 1 − F(k) ≤ 2^{−ηk} with η = 1 − H(θ) ≈ 0.05,
  θ = log₃2, H = binary entropy. Our exact table of 1 − F(k) is in Section 5.2.
- **Allouche (1979)**: for any θ > 3/2 − log 2/log 3 ≈ 0.8691, almost all n have some
  iterate < n^θ. *(Precision note: the constant is 3/2 minus log₃2 ≈ 1.5 − 0.6309; some
  renderings of this constant in secondary text invert the inner fraction, which would be
  negative and is evidently a typo.)*
- **Korec (1994)**: the same with any θ > log 3/log 4 ≈ 0.7924.
- **Korec–Znám (1987)**: to prove the conjecture it suffices to verify it on a single
  residue class {m ≡ a (mod p^n)} where p is an odd prime with 2 a primitive root mod p
  and gcd(a, p) = 1 — a *sufficient set* of density p^{−n}, arbitrarily small. (Related
  earlier sufficient sets: n ≡ 1 (mod 4), Cadogan 1984; n ≡ 1 (mod 16), Andaloro 2000 —
  cited via the Lagarias bibliography and Chamberland survey.)
- **Krasikov–Lagarias (2003)**: for every a ≢ 0 (mod 3), the count π_a(x) of n ≤ x whose
  orbit hits a satisfies π_a(x) ≥ x^0.84 for large x (computer-aided linear programming
  on difference inequalities; exponent γ = log₂(1.7922310) ≈ 0.84175). In particular at
  least x^0.84 integers below x reach 1.
- **Tao (arXiv 2019; Forum of Mathematics, Pi, 2022)** — stated exactly:

  > **Theorem (Tao).** Let f : N+1 → R be any function with f(N) → +∞ as N → ∞. Then
  > Col_min(N) < f(N) for almost all N **in the sense of logarithmic density**.

  Here Col_min(N) is the minimum of the Collatz orbit of N, and "logarithmic density 1"
  means the exceptional set A satisfies (Σ_{a∈A, a≤x} 1/a)/log x → 0. Consequences and
  non-consequences:
  - One may take f(N) = log log log log N. **[KNOWN]**
  - It does **not** say almost all N reach 1, because f must tend to infinity; it does
    **not** say anything about any specific N; it is **not** "Collatz for 99% of numbers"
    in the naive sense — both "almost"s are load-bearing. **[CAVEAT, KNOWN]**
  - The proof route: stabilization of a first-passage random variable for the Syracuse
    iteration, via bounds on the characteristic function of a skew random walk on the
    3-adic cyclic groups Z/3^nZ at high frequencies (a two-dimensional renewal process
    interacting with unions of triangles). **[KNOWN — from the paper's abstract and
    introduction]**
- **Garcia–Tal (1999)**: any single divergent orbit is itself a set of density zero (for a
  class of generalized maps including this one). [KNOWN — cited via Chamberland's survey
  and the Acta Arith. record.]

**[OPEN]** Even "the set of n reaching 1 has natural density 1" is open; x^0.84 is the
record lower bound. Tao's theorem gives logarithmic-density statements about *dipping
below slowly growing thresholds*, not about reaching 1.

### 3.2 Conway's undecidability and its scope (angle 08-03) [KNOWN]

- **Conway (1972), "Unpredictable iterations"**: there is a generalized Collatz function
  g (finitely many affine branches g(n) = a_i n + b_i selected by n mod N₀) such that
  {m : some iterate g^k(m) is a power of 2} is recursively enumerable but not recursive.
  Every Minsky register machine can be encoded as such a map.
- **Kurtz–Simon (2007)**: the generalized Collatz problem ("does g reach 1 on all
  inputs?") is Π⁰₂-complete — maximally undecidable at its quantifier level.
- (Reported via the BusyBeaver wiki, secondary: Kaščák 1992 constructed a universal
  generalized Collatz function with modulus 396.)

**What this does and does not imply for 3x+1** [KNOWN, sharpened in Section 6]:
it does *not* say the 3x+1 conjecture is undecidable — 3x+1 is one fixed instance, and
single instances are never "undecidable" in the Turing sense (only classes are); its truth
value is a fixed arithmetic fact. What it does rule out is any *uniform* method that would
decide all Collatz-like systems by their surface data (moduli, coefficients, drift): a
proof for 3x+1 must exploit special arithmetic structure of the pair (2, 3). It also makes
plausible (but does not prove) that the problem could be independent of strong axiom
systems; no independence result is known. **[OPEN]**

### 3.3 Cycle exclusion (angle 08-04) [KNOWN]

Under T, a cycle has K elements, L of them odd; an **m-cycle** (Simons–de Weger sense) has
m local minima, i.e. m maximal rising runs.

- **Steiner (1977/78)**: no nontrivial 1-cycle (single rising run then falling run). First
  use of Baker-type transcendence (linear forms in logarithms) on this problem.
- **Simons (2005, Math. Comp. 74, 1565–1572)**: no 2-cycles.
- **Simons–de Weger (Acta Arith. 117 (2005), 51–70)**: no m-cycles for m ≤ 68 (extended
  to m ≤ 75 as verification heights grew; they also prove: for each m there are only
  finitely many m-cycles, with explicit exponential-in-m upper bounds on K, L and the
  cycle elements, extending Brox). Method: exact Diophantine structure of the cycle
  equation + lower bounds for |K log 2 − L log 3| from transcendence theory (linear forms
  in two logarithms) + continued fractions/lattice reduction + the computational
  verification height.
- **Hercher (J. Integer Sequences 26 (2023), art. 23.3.5)**: **no m-cycles with m ≤ 91**;
  moreover, once every integer ≤ 3·2^69 is verified, the minimum number of odd elements
  (Hercher's K, our L) in any nontrivial cycle rises to ≥ 1.375·10^11. Barina's published
  verification (2^71 = 2048·2^60 > 1536·2^60 = 3·2^69, Section 3.6) satisfies that
  hypothesis, so **L ≥ 137,528,045,312 odd elements, i.e. ≥ 355,504,839,929 Collatz
  steps, holds now** (Barina 2025 states this consequence, citing Hercher).
- **Eliahou (Discrete Math. 118 (1993), 45–56)**: continued-fraction method; with the
  1993 verification height 2^40, any nontrivial cycle has period ≥ 17,087,915 under T,
  and every feasible period is of the form 301994a + 17087915b + 85137581c. Our updated,
  certified recomputation of this method at heights 2^68/2^71 is Section 5.1.

### 3.4 Stochastic models (angle 08-05) [KNOWN] + [HEURISTIC]

- **The base heuristic** [HEURISTIC]: for the Syracuse map, ν₂(3n+1) behaves like a
  geometric(1/2) variable, so one Syracuse step multiplies n by ≈ 3/2^{E[ν]} = 3/4 on
  geometric average; equivalently a T-step multiplies log n by log(3/2) or log(1/2) with
  frequency ½ each, mean (1/2)log(3/4) < 0. Trajectories are random walks with strictly
  negative drift ⇒ almost sure descent. This is the reason everyone believes the
  conjecture; it is not remotely a proof.
- **Lagarias–Weiss (Ann. Appl. Prob. 2 (1992), 229–261)** [KNOWN]: two rigorous stochastic
  models (a random walk imitating T mod 2^j; branching random walks imitating T^{-1} mod
  3^j). Both predict lim sup σ∞(n)/log n = γ_BP ≈ 41.677647 (σ∞ = total stopping time
  under T, extremal ones-ratio ≈ 0.609), against a typical value 2/log(4/3) ≈ 6.95212;
  and predict max excursion t(n) ≈ n² for record-setters. Predictions match data (then
  10^11, today 2^71 — Barina's path-record tables remain consistent).
- **Applegate–Lagarias (Math. Comp., 2003)** [KNOWN]: unconditionally, infinitely many n
  have σ∞(n) > 6.14316 log n (tree search to depth 60).
- **Sinai (Comm. Pure Appl. Math. 56 (2003), 1016–1028)** and **Kontorovich–Sinai
  (Structure Theorem for (d,g,h)-maps)** [KNOWN]: after rescaling, trajectories of the
  (d,g,h) generalizations converge to Brownian motion with drift log g − (d/(d−1)) log d;
  for 3x+1 this is log 3 − 2 log 2 = log(3/4) < 0, so "infinity is a repelling point" and
  typical trajectories return. **Kontorovich–Lagarias (2009, in "The Ultimate Challenge",
  AMS 2010)** develop this into a full stochastic-model framework, including the 5x+1
  contrast: drift log(5/4) > 0, so almost all 5x+1 orbits are predicted to diverge —
  drift alone distinguishes nothing finer than the sign of log g − 2 log 2.
- **The rigorous content and its ceiling** [NO-GO pointer]: every rigorous theorem in this
  family is a statement about *typical* trajectories of a *model*, or (Terras/Korec/Tao)
  about density-1 sets of integers. None can address the exceptional null set where
  counterexamples would live. See Section 6.

### 3.5 2-adic and 3-adic structure (angle 08-06) [KNOWN]

- T extends continuously to the 2-adic integers Z₂ and is a Haar-measure-preserving,
  **strongly mixing (hence ergodic), indeed Bernoulli** transformation, topologically and
  metrically conjugate to the 2-adic shift S, where S(x) = (x−1)/2 for x odd and x/2 for
  x even (S deletes the lowest binary digit).
- **Bernstein (Proc. AMS 121 (1994), 405–408)**: explicit non-iterative formula for the
  conjugacy; the 3x+1 conjecture restated 2-adically without iteration.
- **Bernstein–Lagarias (Canad. J. Math. 48 (1996), 1154–1169)**: the normalized conjugacy
  Φ (Φ∘S∘Φ^{-1} = T, Φ(0) = 0) is *solenoidal* (compatible with all reductions mod 2^n,
  inducing permutations Φ_n of Z/2^nZ); Φ_n has order 2^{n−4} for n ≥ 6; conjecturally Φ
  has exactly two odd fixed points (−1 and 1/3) — the "Φ fixed-point conjecture". The
  inverse Φ^{-1} = Q∞ sends a 2-adic integer to its parity vector.
- **Periodicity structure**: eventually periodic parity vector ⟹ the point is rational
  [KNOWN]; **Lagarias' Periodicity Conjecture** — every rational in Z₂ (odd denominator)
  has eventually periodic parity vector, i.e. every rational orbit is eventually cyclic —
  is **[OPEN]** and already implies there is no divergent integer trajectory.
- **3-adic side**: the forward map is not 3-adically continuous (parity is not a 3-adic
  notion), and no useful 3-adic interpolation of the forward dynamics is known
  [assessment]. What genuinely lives 3-adically is the *backward* tree: preimage counts
  mod 3^j drive the branching-process models (Lagarias–Weiss), the Applegate–Lagarias
  density-bound machinery, and Wirsching's analysis of predecessor sets (Acta Arith. 63
  (1993), 205–210, and his 1998 Springer Lecture Notes vol. 1681), and the 3-adic cyclic
  groups Z/3^nZ carry Tao's Syracuse random variables.
- **The null-set problem** [KNOWN fact, NO-GO pointer]: Z has Haar measure zero in Z₂, so
  the complete ergodic understanding of (Z₂, T) constrains integers not at all
  (Section 6.2).

### 3.6 Computational verification (angle 08-07) [KNOWN]

Published record (do not quote folklore numbers; these are the checkable ones):

- **Oliveira e Silva (Math. Comp. 68 (1999), 371–384)**: early large-scale verification
  and path/stopping-time records; his and other distributed efforts held the record in
  the low-2^60s range before Barina's project (superseded below).
- **Barina, J. Supercomputing 77 (2021), 2681–2688** (DOI 10.1007/s11227-020-03368-x):
  new algorithmic approach — replaces O(2^N)-entry precomputed tables by O(N) lookup
  tables; 4.2·10⁹ 128-bit numbers/s on one CPU, 2.2·10¹¹/s on an RTX 2080; project
  verified **all n < 2^68** (completed May 2020).
- **Barina, J. Supercomputing 81, art. 810 (2025)** (DOI 10.1007/s11227-025-07337-0):
  verified **all n < 2^71** (January 2025); total acceleration 1335× over the first CPU
  code; four new path records found; notes the cycle-length consequence of Hercher's
  theorem (Section 3.3). The live project page reports progress beyond 2^71 (≈ 2^71.02 as
  of August 2026), **unpublished** — we do not rely on it.
- **Method** (from the two papers): iterate T on 128-bit integers; sieve out residues mod
  2^k that provably fall below their start within k steps (exactly the complement of the
  surviving parity vectors counted in Section 5.2 — the same Terras combinatorics), so
  only the surviving classes are tested; verify *convergence below the starting value*
  (which, chained downward, implies reaching 1 given the base range) rather than descent
  all the way to 1; track "path records" (maximal excursions) as a by-product.
- **What verification buys**: (i) truth of the conjecture for all n below the height;
  (ii) every element of a hypothetical nontrivial cycle exceeds the height (feeding
  Section 5.1); (iii) any divergent orbit's minimum exceeds the height. What it cannot
  buy: the conjecture — and Section 5.1's plateau analysis quantifies how slowly the
  cycle bounds grow with height (roughly linearly in B per plateau jump).

### 3.7 Other domains: negatives, rationals, beyond (angle 08-09) [KNOWN]

- **Negative integers**: three nontrivial cycles known (Section 2.3). Equivalently, the
  **3x−1 system on positives** (conjugate via n ↦ −n) has cycles {1}, {5, 7, 10},
  {17, 25, 37, 55, 82, 41, 61, 91, 136, 68, 34}. The generic-descent heuristics and the
  Terras machinery apply to 3x−1 *verbatim* (Section 6.1) — the strongest known evidence
  that density methods cannot decide cycle questions.
- **Rationals with odd denominator**: T preserves each set D_k = {j/k} for k ≡ 1, 5
  (mod 6). **Lagarias (Acta Arith. 56 (1990), 33–53)** analyzed the set of rational
  cycles; rational cycles exist in abundance (each admissible parity word yields a
  rational fixed point of the corresponding affine contraction — the cycle equation of
  Section 2.2 always has the rational solution n = ρ_K/(2^K − 3^L); the integrality of
  that rational is the entire difficulty). The 3x+1 dynamics on Q_odd embeds in the Z₂
  picture; "every rational orbit eventually cyclic" is the Periodicity Conjecture
  [OPEN].
- **Z₂**: Haar-a.e. point has an aperiodic, equidistributed parity vector; the integers
  are an exceptional null family inside an exactly-understood system.
- **Moral** [SYNTHESIS]: 3x+1 on Z⁺ is the *only* domain in this family where uniqueness
  of the cycle is even conjectured; every enlargement (negatives, rationals, 2-adics)
  has provably or plausibly many cycles. Any correct proof must use positivity and
  integrality simultaneously.

### 3.8 Rewrite systems, automata, functional equations (angle 08-08) [KNOWN]

- **Tag systems (De Mol, Theor. Comput. Sci. 390 (2008), 92–101)**: the 2-tag system with
  productions a → bc, b → a, c → aaa simulates Collatz iteration (input a^n); Collatz is
  thus a halting-type question for one of the smallest interesting tag systems.
- **Finite automata (Shallit–Wilson, EATCS Bulletin 46 (1991), 182–185)**: the sets S_i of
  integers that reach 1 with exactly i odd iterates ≥ 3 are 2-automatic for each i; the
  union over i (= all of Z⁺, conjecturally) is where automaticity-based approaches stall.
- **Binomial-coefficient representation (Margenstern–Matiyasevich, Acta Arith. 91 (1999),
  367–378)**: the 3x+1 problem encoded in binomial-coefficient arithmetic (logic/rewrite
  angle).
- **Functional equations (Berg–Meinardus, Results Math. 25 (1994), 1–12; Rostock Math.
  Kolloq. 48 (1995), 11–18)**: the conjecture is equivalent to statements that certain
  functional equations for generating functions holomorphic on the unit disk admit only
  the obvious solutions.
- **Real/complex interpolation (Chamberland 1996; Letherman–Schleicher–Wood, Experiment.
  Math. 8 (1999), 241–251)**: entire and real-analytic extensions of T; the holomorphic
  dynamics viewpoint locates the integers inside Fatou-type structures; no dynamical
  obstruction to the conjecture was found this way [cited via the Lagarias bibliography;
  we did not verify the papers' internal theorems in detail].
- **IFS view** [KNOWN framing]: forward dynamics on Z₂ is the full one-sided 2-shift
  (Bernoulli); backward dynamics on Z⁺ is generated by the partial inverse maps
  n ↦ 2n and n ↦ (2n−1)/3 (defined when 2n ≡ 1 mod 3) — an expanding IFS on the 3-adic
  tree whose growth constants drive the x^0.84-type density bounds.
- **Assessment** [SYNTHESIS]: each representation faithfully re-encodes the problem, and
  each inherits the full difficulty; none has produced a constraint on 3x+1 that the
  direct parity-vector formalism does not already give. Their genuine value has been
  negative/structural (undecidability of the surrounding classes, Section 3.2).

---

## 4. Attack Log — the ten angles

**08-01 (maps & cycles).** Formalized C/T/Syr, the depth-k formula, Böhm–Sontacchi;
computed and verified the five integer cycles; exhaustive basin scan |n| ≤ 2·10⁶
(`code/cycles_z.py`). Output: Section 2. Label: [KNOWN, RECOMPUTED HERE].

**08-02 (density/stopping time).** Verified the Terras/Everett, Allouche, Korec,
Korec–Znám, Krasikov–Lagarias, and Tao results against primary or near-primary sources;
fixed a constant-rendering trap in Allouche's exponent; recomputed the Terras density
table exactly (`code/terras_density.py`). Output: Sections 3.1, 5.2. Labels: [KNOWN],
[KNOWN, RECOMPUTED HERE].

**08-03 (undecidability).** Verified Conway 1972 and Kurtz–Simon 2007 (Π⁰₂-complete);
delineated exactly what generalized undecidability does and does not imply for the fixed
instance 3x+1. Output: Sections 3.2, 6.1. Label: [KNOWN] + [NO-GO ANALYSIS].

**08-04 (cycle bounds).** Verified Steiner/Simons/Simons–de Weger/Hercher/Eliahou chain;
implemented the Eliahou method with certified exact arithmetic; validated against the 1993
figure; updated to 2^71; located the plateau structure and the exact coincidence of the
next plateau with the Hercher–Barina figure 355,504,839,929 (`code/cycle_bound.py`).
Output: Sections 3.3, 5.1. Label: [KNOWN, RECOMPUTED HERE].

**08-05 (stochastic models).** Verified Lagarias–Weiss, Sinai, Kontorovich–Sinai,
Kontorovich–Lagarias, Applegate–Lagarias; extracted the drift constants and the
γ_BP ≈ 41.677647 extremal constant; assessed the rigorous ceiling of model-based
reasoning. Output: Sections 3.4, 6. Labels: [KNOWN], [HEURISTIC] flagged as such.

**08-06 (p-adic).** Verified the Bernstein/Bernstein–Lagarias 2-adic conjugacy theory
(ergodic, Bernoulli, solenoidal, Φ_n order 2^{n−4}), the periodicity conjecture, and the
3-adic backward-tree literature (Wirsching, Applegate–Lagarias). Output: Sections 3.5,
6.2. Label: [KNOWN].

**08-07 (verification).** Established the published height: **2^71** (Barina 2025;
previously 2^68, Barina 2021), with method description; noted the live-but-unpublished
progress beyond 2^71 and did not rely on it. Output: Section 3.6. Label: [KNOWN].

**08-08 (representations).** Verified De Mol (tag systems), Shallit–Wilson (automata),
Margenstern–Matiyasevich (binomial), Berg–Meinardus (functional equations),
real/holomorphic extensions; assessed that all inherit full difficulty. Output:
Section 3.8. Label: [KNOWN] + [SYNTHESIS assessment].

**08-09 (other domains).** Computed/verified negative-integer cycles and basin statistics;
verified Lagarias 1990 rational-cycle framework; formulated the "only-domain" moral.
Output: Sections 2.3, 3.7. Labels: [KNOWN, RECOMPUTED HERE], [SYNTHESIS].

**08-10 (why almost-all ≠ all).** Assembled the exceptional-set structure theory:
logarithmic vs natural density; the divergence lemmas with proofs; the x^0.84 basin
corollary; the counterexample-shape table; the consistency check that all known theorems
coexist with a counterexample. Output: Sections 5.3, 5.4, 6.4, 6.5. Labels: [KNOWN],
[SYNTHESIS], [NO-GO ANALYSIS].

---

## 5. Technical Findings (proofs and certified computations)

### 5.1 Updated cycle-exclusion bound at height 2^71 [KNOWN, RECOMPUTED HERE]

**Lemma 1 (cycle-ratio identity; classical).** Let a nontrivial T-cycle on Z⁺ have K
elements per period, L of them odd, minimum odd element m. Then

    ∏_{odd elements n_i} (3 + 1/n_i) = 2^K,   hence   log₂3 < K/L ≤ log₂(3 + 1/m).

*Proof.* Around one period, ∏ T(n)/n = 1. Odd steps contribute (3 + 1/n_i)/2, even steps
1/2; collecting the 2's gives the identity. Each factor exceeds 3 (strictly) and is at
most 3 + 1/m. ∎

**Lemma 2 (simplest fraction; Stern–Brocot, classical).** A sufficiently narrow interval
of reals > 1 contains a unique rational K₀/L₀ (lowest terms) of least denominator among
all rationals in it. Suppose the simplest fraction in (log₂3, log₂(3 + 1/B)) is K₀/L₀
and every integer < B is verified convergent (so m > B). Then any nontrivial cycle
satisfies **L ≥ L₀** (its reduced ratio k/l lies in the interval, so l ≥ L₀, and L is a
multiple of l) and **K ≥ K₀**: indeed K > L log₂3 ≥ L₀ log₂3 = K₀ − L₀·(K₀/L₀ − log₂3)
> K₀ − L₀·w > K₀ − 1, where w is the certified interval width (w ≈ 2·10⁻²² at B = 2^71,
so L₀·w ≈ 1.5·10⁻¹¹ < 1). ∎

**Certified computation** (`code/cycle_bound.py`; endpoints enclosed rationally at 250 and
400 decimal digits, exact Fraction arithmetic in between, inner/outer interval agreement
required; final membership of K₀/L₀ in the certified interval rechecked exactly):

| verification height B | simplest K/L in interval | odd elements L ≥ | T-period K ≥ | Collatz steps K+L ≥ |
|---|---|---|---|---|
| 2^40 (Eliahou's 1993 assumption) | 17087915/10781274 | 10,781,274 | **17,087,915** | 27,869,189 |
| 2^68 (Barina 2021) | 114208327604/72057431991 | 72,057,431,991 | 114,208,327,604 | 186,265,759,595 |
| **2^71 (Barina 2025, current)** | 114208327604/72057431991 | **72,057,431,991** | **114,208,327,604** | **186,265,759,595** |

Validation: the 2^40 row reproduces Eliahou's published 17,087,915 exactly.

**Plateau structure** [KNOWN phenomenon, quantified here]: the bound is a step function of
B jumping at Stern–Brocot mediants. The current fraction stays simplest until
B* = 1/(2^{K₀/L₀} − 3) ≈ 4.358·10^21 ≈ **2^71.884**; from there to far beyond 2^80 the
simplest fraction is 217976794617/137528045312, i.e. ≥ 137,528,045,312 odd elements and
≥ **355,504,839,929** Collatz steps — *exactly* the figure that Hercher's m-cycle
refinement already achieves at the current height (Hercher 2023 showed verification to
3·2^69 suffices; Barina's 2^71 covers it; Barina 2025 quotes 355,504,839,929). Our pure
Eliahou computation independently confirms that number as the correct next plateau, and
shows what Hercher's structural work bought: reaching the plateau ~2.9× earlier in B.
Hypothetical future heights (same certified pipeline): B = 2^80 ⇒ ≥ 6.2·10^12 Collatz
steps; B = 2^90 ⇒ ≥ 1.65·10^14; B = 2^100 ⇒ ≥ 8.6·10^15. The growth is linear in B along
plateaus — this is the quantitative face of the Diophantine wall (Section 6.3).

### 5.2 Exact Terras densities [KNOWN, RECOMPUTED HERE]

By the Terras bijection (Section 2.2), the natural density of {n : σ(n) > k} equals
D_k = c_k/2^k where c_k counts parity vectors of length k with 3^{L_i} > 2^i for all
i ≤ k. Exact DP (`code/terras_density.py`), integer arithmetic throughout:

| k | surviving vectors c_k | D_k | −log₂(D_k)/k |
|---|---|---|---|
| 10 | 64 | 6.250·10⁻² | 0.4000 |
| 20 | 27,328 | 2.606·10⁻² | 0.2631 |
| 30 | 12,771,274 | 1.189·10⁻² | 0.2131 |
| 60 | 2,216,134,944,775,156 | 1.922·10⁻³ | 0.1504 |
| 120 | 131,320,930,040,438,275,830,258,155,402,960 | 9.879·10⁻⁵ | 0.1109 |

The D₃₀ value 0.011894… matches the classical published tables. The empirical exponent
decreases toward η = 1 − H(log₃2) ≈ 0.050044 with O(log k/k) corrections (ballot-problem
prefactors) — a concrete reminder that even the *easy* part of the theory converges
slowly. These surviving classes are exactly the residues a modern verification run must
still test (Section 3.6): at k = 120 that is ≈ 0.0099% of residues, which is why sieving
works so well and also why it can never do more than linear-in-B work.

### 5.3 Divergence constraints, with proofs

**Lemma 3** [KNOWN, folklore; proof included]. A T-orbit on Z⁺ that is not eventually
periodic tends to +∞. *Proof.* If lim inf n_k < ∞, some integer value recurs; the orbit
is deterministic, so it is eventually periodic. ∎

**Lemma 4** [KNOWN, folklore; proof included]. If the T-orbit of n diverges, then the
parity counts satisfy lim inf_k L_k/k ≥ log₃2 ≈ 0.6309.
*Proof.* log T(x) ≤ log x + x_i log(3/2) − (1 − x_i) log 2 + x_i log(1 + 1/(3x)) for
x ≥ 1 (odd step: T(x) = (3/2)x(1 + 1/(3x)); even step: T(x) = x/2). Summing to step k:
0 ≤ log n_k ≤ log n + L_k log(3/2) − (k − L_k) log 2 + Σ_{i<k} x_i log(1 + 1/(3n_i)).
Given ε > 0, Lemma 3 provides I with n_i > 1/(3ε) for i ≥ I; the correction sum is then
≤ I·log(4/3) + kε. Rearranging, L_k log 3 ≥ k(log 2 − ε) − O_I(1), and ε ↓ 0 gives the
claim. ∎ *(Consequence: a divergent orbit must be persistently "anti-typical": ≥ 63.09%
odd steps forever, against the 50% of a random walk — the large-deviation reason all
stochastic models assign divergence probability 0. [HEURISTIC framing of a rigorous
lemma].)*

**Corollary 5** [SYNTHESIS — assembled from Krasikov–Lagarias 2003; presumed known, not
found stated in our sources]. If even one divergent trajectory exists, then for all large
x at least x^0.84 integers ≤ x have divergent trajectories.
*Proof.* A divergent orbit contains an odd step (an all-even tail would halve forever),
and after any odd step every subsequent element is ≢ 0 (mod 3) (T(odd n) = (3n+1)/2 ≡ 2
mod 3, and halving preserves indivisibility by 3). Pick such an element a. Krasikov–
Lagarias: π_a(x) ≥ x^0.84 for large x, where π_a counts n ≤ x whose orbit hits a. Every
such n inherits a's divergence. ∎
*(Contrast: by Tao's theorem the divergent set has logarithmic density 0; by Garcia–Tal
each single orbit has density 0. A set of size x^0.84 has logarithmic density 0, so there
is no contradiction — the constraints are consistent both with emptiness and with
abundance-below-density. This is the exceptional-set squeeze of angle 08-10.)*

### 5.4 What Tao + verification does and does not give [SYNTHESIS with explicit caveat]

Take f(N) = log log log log N in Tao's theorem: the set {N : Col_min(N) ≥ f(N)} has
logarithmic density 0. For every N in the complement with f(N) ≤ 2^71 — i.e. every such
N up to exp(exp(exp(exp(2^71)))), an astronomically large but finite range — the
orbit dips into verified territory and therefore reaches 1. It is tempting to conclude
"almost all N in that range reach 1", but the published theorem is asymptotic
(logarithmic density is a limit statement), so extracting a statement about a fixed
finite range requires effective rates that the paper does not state (the method is
believed effective in principle; extracting constants has not been done in the
literature we consulted). We therefore record the honest version: **for every function
f → ∞, all N outside a log-density-zero set have orbits dipping below f(N); whenever that
dip lands under the verified height, the orbit reaches 1; and no theorem currently
converts this into "almost all N reach 1" in natural or logarithmic density.** The
obstruction to taking f bounded is structural, not technical bookkeeping — Section 6.4.

---

## 6. No-Go: why the current stopping-time/density methods cannot finish [NO-GO ANALYSIS]

The conjecture splits into three tasks: (a) verified base range; (b) no nontrivial
cycles; (c) no divergent orbits. Everything known attacks (a) by computation, (b) by
Diophantine methods + computation, (c) — nothing, beyond density statements. The four
walls below explain why the density toolchain cannot close (b) or (c). Each wall is
assembled from verified known facts; the synthesis and its quantitative sharpening are
this dossier's contribution.

### 6.1 The mirror wall: density methods cannot see the sign of the +1

The 3x−1 system on Z⁺ (equivalently 3x+1 on Z⁻, Section 2.3) satisfies:
T₋^k(n) = (3^{L_k}n − ρ_k)/2^k with the same parity-vector bijection mod 2^k, the same
coefficient thresholds 3^{L} vs 2^k, the same drift log(3/4), the same Wiener-rescaling
structure. Consequently **Terras's theorem, Allouche's and Korec's refinements, and the
entire stochastic-model apparatus hold verbatim for 3x−1** — the proofs never use the
sign of the additive constant, only parity combinatorics and drift. And for 3x−1 the
conclusion "every orbit reaches the trivial cycle" is **false**: {5, 7, 10} and the
11-element 17-cycle exist. The inputs to Tao's argument (drift plus 3-adic
equidistribution statistics of the Syracuse offsets) are likewise sign-insensitive in
this respect; nothing in an "almost all orbits dip low" conclusion can distinguish
+1 from −1, and in the 3x−1 world orbits dip low and *still* land in nontrivial cycles.

**Conclusion.** Any method whose inputs are parity-vector combinatorics, drift, or
measure-theoretic typicality proves statements that are equally true of 3x−1, and
therefore can never yield "all 3x+1 orbits reach 1". Such methods reduce the conjecture
to (b) + (c) at best; cycle exclusion is irreducibly Diophantine. This is the cleanest
formal sense in which "current stopping-time methods cannot finish".

### 6.2 The 2-adic ergodic wall: the integers are a null set of an exactly solved system

On Z₂ the dynamics of T is completely understood: Bernoulli, explicitly conjugate to the
full shift (Bernstein–Lagarias). From the measure-theoretic point of view there is
*nothing left to prove* — and the conjecture is untouched, because Z⁺ is a Haar-null,
dense subset of Z₂, and every ergodic-theoretic statement is blind to null sets. Worse:
the conjecture is equivalent to statements about which *atomic* invariant measures exist
on integer orbits (cycles) and whether escaping integer orbits exist — precisely the
questions Haar-ergodic theory cannot formulate. Explicit knowledge of the conjugacy Φ
does not help: integrality of Φ-images is not a 2-adically open/measurable-in-the-useful-
sense condition, and Bernstein–Lagarias themselves note their conjugacy framework
reproduces, rather than reduces, the difficulty (their Φ fixed-point conjecture is
"seemingly equally intractable"). **Conclusion:** any proposed proof that operates
"for a.e. 2-adic integer" or "for the invariant measure" proves nothing about even one
integer. Ergodic methods can only re-derive the heuristics.

### 6.3 The Diophantine wall: current transcendence is quantitatively too weak for cycles

A nontrivial cycle forces 0 < K log 2 − L log 3 < L/(3m) (Lemma 1), with m > 2^71: an
*extremely* good rational approximation K/L to log₂3, of quality ~10⁻²² per Section 5.1.
What is available to contradict such approximations?

- **Continued fractions + verification height B** (Eliahou, Section 5.1): excludes
  cycles up to the current Stern–Brocot plateau; the excluded region grows only
  ~linearly in B while the cost of raising B grows linearly in B too — an arms race
  with no finish line.
- **Linear forms in two logarithms** (Baker–Laurent–Mignotte–Nesterenko class, as used
  by Steiner, Simons, Simons–de Weger): lower bounds of shape
  |K log 2 − L log 3| > exp(−C (log K)(log L)) with moderate C. For a cycle one needs
  this to exceed L/(3m). With K ~ 10^11 the transcendence bound is astronomically
  smaller (e^{−C·600+} vs ~10⁻²²): **no contradiction**. The m-cycle results succeed
  only because the m-cycle structure supplies *additional* Diophantine equations that
  bound cycle elements exponentially in m (Simons–de Weger), making the comparison
  winnable *for each fixed small m*. Each increment of m then costs new computation
  (Hercher: m ≤ 91, with m = 92 needing further verified height) — linear progress at
  exponentially growing cost, with no mechanism to handle unbounded m.
- **What would suffice**: an effective irrationality measure for log₂3 with exponent
  close to 2 (so that |K log 2 − L log 3| ≫ K^{−1−ε} unconditionally), which would kill
  all sufficiently large cycles outright. Current effective exponents for this constant
  are far from 2 (the qualitative gap between Roth-type ineffective results and
  Baker-type effective ones), and closing that gap is a famous open problem in
  transcendence theory in its own right.

**Conclusion:** cycle exclusion beyond m-cycles is blocked not by lack of cleverness in
applying known bounds but by the intrinsic strength of the best known lower bounds for
linear forms in logarithms. A full cycle proof needs either a transcendence
breakthrough, or structure (integrality of ρ_K/(2^K − 3^L), Section 3.7) used in an
essentially new way.

### 6.4 The invariance-loss wall inside Tao's method: why f → ∞ is essential

Tao's advance over Terras/Korec is precisely stated in his own introduction: the uniform
measure on [1, x] is not even approximately invariant under the iteration, so density-1
statements at scale x cannot be concatenated with density-1 statements at scale x^θ —
the first step may map its good set into the second step's exceptional set. His fix is
to build a family of measures (laws of "Syracuse random variables" on Z/3^nZ) that *is*
approximately transported by the dynamics, with quantitative stabilization proved via
characteristic-function decay. The approximation degrades as the orbit descends through
scales; the total loss is controlled only if the target threshold f(N) recedes to
infinity — however slowly — so the number of scales the argument must chain is "one less
than infinite". Achieving bounded f (= the almost-all conjecture in natural density,
essentially) would require exact invariance or a summable loss across *all* scales
simultaneously, which the 3-adic characteristic-function estimates do not provide at
bounded scales. This is the Bourgain almost-sure-well-posedness analogy Tao himself
draws: the method's natural terminus is "almost bounded", not "bounded". And even
bounded-f-for-almost-all would still be a density statement, subject to walls 6.1–6.3
for the remaining null set.

### 6.5 The exceptional-set squeeze and the shape of a counterexample (angle 08-10)

Assemble everything known about a hypothetical counterexample:

**(A) A nontrivial cycle** must have: minimum element > 2^71 (Barina); ≥ 137,528,045,312
odd elements and ≥ 355,504,839,929 Collatz steps per period (Hercher + Barina; our
independent Eliahou-method floor: ≥ 186,265,759,595); ≥ 92 local minima (Hercher);
K/L within ~10⁻²² of log₂3 (Lemma 1), i.e. parity statistics indistinguishable from
"typical" to 22 digits; and it contributes an atomic invariant measure invisible to
every density theorem (its members have density 0).

**(B) A divergent orbit** must: tend to ∞ (Lemma 3); maintain ≥ 63.09% odd steps forever
(Lemma 4) — a permanent large-deviation event of every stochastic model; have orbit of
density zero (Garcia–Tal); have minimum > 2^71; and, if it exists at all, be accompanied
by ≥ x^0.84 divergent starting values below x (Corollary 5) which nevertheless form a
logarithmic-density-zero set (Tao) — a coherent squeeze, since x^0.84-sized sets are
log-null.

**Consistency check** [NO-GO ANALYSIS, key point]: the conjunction of *every theorem
cited in this dossier* is satisfiable by a world in which (A) or (B) exists. Nothing
known pins the exceptional set to ∅; the known constraints bound its density (zero),
its cardinality if nonempty (≥ x^0.84 for divergence), its parity statistics (boundary
of the large-deviation cone), and its arithmetic (Diophantine rigidity for cycles) —
and these constraints are mutually consistent. That is the precise sense in which
"almost all" is far from "all": the gap is not a thinner and thinner exceptional set
waiting to be squeezed to nothing; it is a *category* gap between measure statements
and orbit-by-orbit statements, and crossing it provably requires non-measure inputs
(6.1), non-ergodic inputs (6.2), and stronger-than-current Diophantine inputs (6.3).

**Where a finish could come from** [assessment, speculative]: (i) effective
irrationality measures for log₂3 near exponent 2 (kills cycles); (ii) a rigidity
theorem for the escaping set on Z₂ that sees integrality (kills divergence — nothing of
the sort exists); (iii) a fundamentally new invariant (height function decreasing along
some multi-step potential — many have tried, none survive the mirror test of 6.1: any
candidate potential must fail for 3x−1, i.e. must use the +1 sign); (iv) logical
independence results, which would end the game differently. Each is labeled: no partial
progress on (i)–(iii) is claimed here.

---

## 7. References and Honesty Ledger

### 7.1 Primary results (verified against primary or near-primary sources)

Verification tags: **[P]** = primary text/abstract read during this mission;
**[M]** = bibliographic metadata verified (journal/volume/pages/DOI);
**[B]** = content verified via Lagarias' annotated bibliography (arXiv:math/0309224);
**[S]** = content verified via Chamberland's survey or another secondary source.

1. R. Terras, *A stopping time problem on the positive integers*, Acta Arith. 30 (1976),
   241–252. **[P/S]** (Also: *On the existence of a density*, Acta Arith. 35 (1979), 101–102.)
2. C. J. Everett, *Iteration of the number-theoretic function f(2n)=n, f(2n+1)=3n+2*,
   Adv. Math. 25 (1977), 42–45. **[B]**
3. J.-P. Allouche, *Sur la conjecture de "Syracuse–Kakutani–Collatz"*, Sém. Théorie des
   Nombres de Bordeaux, 1978–79, Exp. 9. **[P (via EMS Magazine survey by Allouche, DOI
   10.4171/mag-64) / S]**
4. I. Korec, *A density estimate for the 3x+1 problem*, Math. Slovaca 44 (1994), 85–89.
   **[S — constant log₄3 verified via Tao's paper and two surveys]**
5. I. Korec, Š. Znám, *A note on the 3x+1 problem*, Amer. Math. Monthly 94 (1987),
   771–772. **[B]** (Sufficient set of density p^{−n}.)
6. I. Krasikov, J. C. Lagarias, *Bounds for the 3x+1 problem using difference
   inequalities*, Acta Arith. 109 (2003), 237–258, DOI 10.4064/aa109-3-4. **[P]**
   (π_a(x) ≥ x^0.84.)
7. T. Tao, *Almost all orbits of the Collatz map attain almost bounded values*, Forum of
   Mathematics, Pi 10 (2022), e12, DOI 10.1017/fmp.2022.8; arXiv:1909.03562 (2019). **[P]**
8. J. H. Conway, *Unpredictable iterations*, Proc. 1972 Number Theory Conf., Univ.
   Colorado, Boulder (1972), 49–52. **[S/M]**
9. S. A. Kurtz, J. Simon, *The undecidability of the generalized Collatz problem*, TAMC
   2007, LNCS 4484, Springer, 542–553, DOI 10.1007/978-3-540-72504-6_49. **[P (abstract)/M]**
10. R. P. Steiner, *A theorem on the Syracuse problem*, Proc. 7th Manitoba Conf. Numerical
    Math. and Computing (1977), Congressus Numerantium XX (1978), 553–559. **[B]**
11. J. L. Simons, *On the nonexistence of 2-cycles for the 3x+1 problem*, Math. Comp. 74
    (2005), 1565–1572. **[M/S]**
12. J. L. Simons, B. M. M. de Weger, *Theoretical and computational bounds for m-cycles of
    the 3n+1 problem*, Acta Arith. 117 (2005), 51–70, DOI 10.4064/aa117-1-3. **[P]**
13. C. Hercher, *There are no Collatz m-cycles with m ≤ 91*, J. Integer Sequences 26
    (2023), Article 23.3.5 (arXiv:2201.00406). **[P]** (Note: a corrigendum exists for
    this article per the JIS page; the m ≤ 91 statement stands in the published record.)
14. S. Eliahou, *The 3x+1 problem: new lower bounds on nontrivial cycle lengths*, Discrete
    Math. 118 (1993), 45–56, DOI 10.1016/0012-365X(93)90052-U. **[P (abstract)/M]**
15. J. C. Lagarias, *The 3x+1 problem and its generalizations*, Amer. Math. Monthly 92
    (1985), 3–23. **[S/M]**
16. J. C. Lagarias, A. Weiss, *The 3x+1 problem: two stochastic models*, Ann. Appl.
    Probab. 2 (1992), 229–261. **[P (abstract)]** (γ_BP ≈ 41.677647.)
17. D. Applegate, J. C. Lagarias, *Lower bounds for the total stopping time of 3x+1
    iterates*, Math. Comp. 72 (2003), 1035–1049, DOI 10.1090/S0025-5718-02-01425-4. **[P]**
18. Ya. G. Sinai, *Statistical (3x+1) problem*, Comm. Pure Appl. Math. 56 (2003),
    1016–1028. **[M/S]**
19. A. V. Kontorovich, Ya. G. Sinai, *Structure theorem for (d,g,h)-maps*,
    arXiv:math/0601622 (orig. 2002). **[P (abstract)]**
20. A. V. Kontorovich, J. C. Lagarias, *Stochastic models for the 3x+1 and 5x+1 problems*,
    arXiv:0910.1944; in *The Ultimate Challenge: The 3x+1 Problem* (J. C. Lagarias, ed.),
    AMS, 2010. **[P]**
21. D. J. Bernstein, *A non-iterative 2-adic statement of the 3N+1 conjecture*, Proc.
    Amer. Math. Soc. 121 (1994), 405–408. **[B]**
22. D. J. Bernstein, J. C. Lagarias, *The 3x+1 conjugacy map*, Canad. J. Math. 48 (1996),
    1154–1169, DOI 10.4153/cjm-1996-060-x. **[P]**
23. J. C. Lagarias, *The set of rational cycles for the 3x+1 problem*, Acta Arith. 56
    (1990), 33–53. **[M/S]**
24. D. Barina, *Convergence verification of the Collatz problem*, J. Supercomputing 77
    (2021), 2681–2688, DOI 10.1007/s11227-020-03368-x. **[P]** (2^68.)
25. D. Barina, *Improved verification limit for the convergence of the Collatz
    conjecture*, J. Supercomputing 81 (2025), art. 810, DOI 10.1007/s11227-025-07337-0.
    **[P]** (2^71; cycle-length consequence 355,504,839,929.)
26. T. Oliveira e Silva, *Maximum excursion and stopping time record-holders for the 3x+1
    problem: computational results*, Math. Comp. 68 (1999), 371–384. **[M]**
27. M. V. P. Garcia, F. A. Tal, *A note on the generalized 3n+1 problem*, Acta Arith. 90
    (1999), 245–250. **[B/S]** (Divergent orbits have density zero.)
28. L. De Mol, *Tag systems and Collatz-like functions*, Theoret. Comput. Sci. 390 (2008),
    92–101, DOI 10.1016/j.tcs.2007.10.020. **[M]**
29. J. Shallit, D. W. Wilson, *The "3x+1" problem and finite automata*, Bull. EATCS 46
    (1991), 182–185. **[B]**
30. M. Margenstern, Y. Matiyasevich, *A binomial representation of the 3x+1 problem*,
    Acta Arith. 91 (1999), 367–378. **[M — via MathWorld reference list]**
31. L. Berg, G. Meinardus, *Functional equations connected with the Collatz problem*,
    Results Math. 25 (1994), 1–12. **[B]**
32. S. Letherman, D. Schleicher, R. Wood, *On the 3X+1 problem and holomorphic dynamics*,
    Experiment. Math. 8 (1999), 241–251. **[B/M]**
33. G. J. Wirsching, *An improved estimate concerning 3N+1 predecessor sets*, Acta Arith.
    63 (1993), 205–210; and *The Dynamical System Generated by the 3n+1 Function*,
    Lecture Notes in Math. 1681, Springer, 1998. **[B]**
34. M. Chamberland, *An update on the 3x+1 problem* (survey). **[P]** (Used as a
    secondary source; also C. Böhm, G. Sontacchi (1978), Atti Accad. Naz. Lincei 64,
    260–264, cited via it and via Lagarias' bibliography.)
35. J. C. Lagarias, *The 3x+1 problem: an annotated bibliography*, arXiv:math/0309224.
    **[P]** (Used as the verification backbone for items tagged [B].)

### 7.2 Honesty ledger

- **Claimed as new to mathematics: nothing.**
- **Computed and certified here**: the cycle-bound table of §5.1 (validated against
  Eliahou 1993 and against the Hercher–Barina plateau figure), the exact Terras table of
  §5.2 (validated against the classical D₃₀), the integer-cycle scan of §2.3. Code and
  raw outputs: `code/cycle_bound.py`, `code/terras_density.py`, `code/cycles_z.py`.
- **Proved here for completeness** (folklore-level, no novelty claimed): Lemmas 1–4.
- **Synthesized here, presumed known**: Corollary 5 (divergence ⇒ x^0.84 divergent
  starters); the finite-range Tao+verification statement of §5.4 with its effectivity
  caveat; the mirror-wall formulation of §6.1; the consistency check of §6.5.
- **Numbers we refused to invent**: we cite the *published* verification height 2^71
  (Barina 2025) and explicitly flag the live project's ≈2^71.02 as unpublished; we do
  not quote an effective irrationality exponent for log₂3 because we did not verify one.
- **Known misstatement traps flagged**: Tao's theorem is logarithmic density + f → ∞,
  not "almost all reach 1" and not "Collatz proved for almost all integers" (§3.1, §5.4);
  Allouche's constant is 3/2 − log₃2 (§3.1); Conway's undecidability is about the
  generalized class, not the 3x+1 instance (§3.2); Eliahou's 17,087,915 was conditional
  on the 1993 height 2^40 (§5.1).
- **Failure disclosure**: we found no new density theorem, no new cycle-exclusion lemma
  beyond recomputation/plateau analysis, and no rigorous stochastic bound beyond the
  literature. The deliverable meeting the mission's "breakthrough" bar, if any, is the
  no-go analysis of Section 6, offered as a careful synthesis, not as a theorem about
  all possible proofs.
