# LEGION 09 — The Binary Goldbach Conjecture: Research Dossier

**Legion:** 09 (Goldbach)
**Target:** Binary (strong/even) Goldbach: every even integer `n ≥ 4` is the sum of two primes.
**Workspace:** `/workspace/research/conjectures/09-goldbach/`
**Model:** claude-fable-5-thinking-xhigh

**Execution note (honesty):** The mission ordered ten nested Task children (09-01 … 09-10). The run
environment provided to this commander exposed **no subagent-spawning tool**, so nesting was
impossible. The ten specialist briefs below were therefore researched and written **serially by the
commander itself**, one per assigned angle, under the same model. Nothing else about the mission
was altered.

**Honesty labels used throughout:**

| Label | Meaning |
|---|---|
| `[ESTABLISHED]` | Peer-reviewed, standard, correctly attributed to the best of this legion's knowledge. |
| `[ESTABLISHED*]` | Established result, but bibliographic details recalled from memory — verify before external use. |
| `[FOLKLORE]` | Known to experts, rarely written down precisely; formalization here may not be novel. |
| `[NEW-SYNTHESIS]` | Assembly/quantification produced in this run from known parts; believed correct; novelty uncertain; needs expert referee. |
| `[PROGRAM]` | A proposed research plan, not an executed proof. |
| `[SPECULATIVE]` | Plausible but unproven; could be wrong. |
| `[FAILED]` | Attack line examined and found blocked, with the reason. |

**Standing disclaimers:** No proof of binary Goldbach is claimed. No new proof of weak (ternary)
Goldbach is claimed — Helfgott's theorem is treated as known input. No citations are invented; where
memory is uncertain the entry is flagged `[ESTABLISHED*]` or stated without bibliographic detail.

---

## 1. Executive Summary & Verdict

**Verdict: known / incremental. No breakthrough. One candidate incremental contribution.**

The binary Goldbach conjecture remains open, and this legion did not close it. What the legion
delivers, per the mission's third breakthrough criterion ("a precise barrier for the circle method
at the binary problem"), is a sharpened, quantified statement of exactly where and by how much the
circle method fails for binary Goldbach — the **Modulus Barrier** (Section 5, C1–C2). The core
facts, all elementary once stated:

1. The minor arcs carry Parseval mass `(1 + o(1)) · N log N` in `L²`, while the target main term is
   only `𝔖(n)·n ≍ n`. The trivial (triangle-inequality) bound on the minor-arc contribution
   therefore overshoots the main term by a factor `≍ log n` — the method fails "by one logarithm,"
   but that logarithm is invisible to any argument that only uses `|S(α)|`. `[FOLKLORE, formalized here]`
2. **No pointwise minor-arc bound, however strong — including square-root cancellation, stronger
   than anything GRH gives — can help**, because Parseval fixes the total `L²` mass; pointwise
   savings on minor arcs cannot reduce `∫_𝔪 |S|²`. This is a rigorous limitation on the entire
   class of "absolute-value" circle-method arguments (adversarial-phase argument, Section 5, C1). `[FOLKLORE, formalized here]`
3. **GRH cannot remove the barrier, only halve it**: under GRH the major arcs can be enlarged to
   `Q ≈ N^{1/2}`, capturing at most `(1/2 + o(1))` of the `L²` mass; at least `(1/2 − o(1)) · N log N`
   of mass remains on the minor arcs, still `≫ n`. This quantification (Section 5, C2) appears to
   be rarely stated explicitly. `[NEW-SYNTHESIS — elementary, believed correct, needs referee]`
4. Consequently the known conditional landscape is the true state of the art: binary Goldbach is
   **not known even under GRH**; GRH yields only an exceptional set `≪ x^{1/2+o(1)}`. Every route to
   "all large even n" must either average over `n` (giving almost-all results), add a variable
   (ternary, or primes + powers of 2), or relax "prime" to "P₂" (Chen) — and each of those
   relaxations is blocked from the final step by a named barrier (Parseval, parity). Sections 4, 6.

A reduction-to-computation **program** under a weaker-than-GRH, finitely-checkable hypothesis is
laid out (Section 5, C3), with the honest caveat that by items 1–3 it can only ever produce
"Goldbach up to an explicit huge `N₀` outside an explicitly enumerable thin set," never the full
conjecture. The mission's first breakthrough criterion (full reduction to a checkable range) is,
on current technology, **provably out of reach for absolute-value circle-method arguments** — that
impossibility statement, made precise, is the legion's main output.

---

## 2. Problem Statement & Precise Formulations

**Binary (strong) Goldbach.** Every even integer `n ≥ 4` can be written as `n = p + q` with `p, q`
prime. (Goldbach–Euler correspondence, 1742; the modern "binary" form is Euler's reformulation.)
`[ESTABLISHED]` as a statement; open as a theorem.

**Ternary (weak) Goldbach.** Every odd integer `n ≥ 7` is a sum of three primes. **Proved**
(Helfgott 2013; see 09-01). Binary implies ternary (write odd `n = 3 + (n − 3)` and apply binary to
the even number `n − 3`); the converse implication does not hold.

**Standard analytic normalization.** For `N` large, let

    S(α) = Σ_{m ≤ N} Λ(m) e(mα),      e(x) = exp(2πix),

with `Λ` the von Mangoldt function. The weighted representation count of an even `n ≤ N` is

    R(n) = Σ_{a+b=n} Λ(a)Λ(b) = ∫₀¹ S(α)² e(−nα) dα.

Binary Goldbach for large `n` follows if `R(n) > C√n·log²n` (enough to beat prime-power
contributions), and the expected truth is

    R(n) ~ 𝔖(n)·n,   𝔖(n) = 2C₂ · Π_{p|n, p>2} (p−1)/(p−2)   (n even),

where `C₂ = Π_{p>2} (1 − (p−1)^{−2}) ≈ 0.6602` is the twin-prime constant, so `𝔖(n) ≥ 2C₂ ≈ 1.320`
for every even `n`, and `𝔖(n) = 0` for odd `n`. Equivalently, the unweighted ordered count is
conjectured `~ 𝔖(n) · n / log²n` (Hardy–Littlewood Conjecture A). `[ESTABLISHED]` as conjecture and
normalization (Hardy & Littlewood, *Partitio Numerorum III*, Acta Math. 44, 1923).

**Exceptional set.** `E(x) = #{even n ≤ x : n is not a sum of two primes}`. Binary Goldbach is
`E(x) = 0` for `x ≥ 4` (beyond the trivial cases). All known unconditional results give
`E(x) ≪ x^{1−δ}` for some fixed `δ > 0`, not `E(x) = O(1)`.

**What would count as a breakthrough (per mission):** (i) an effective reduction of binary Goldbach
to a checkable range under a hypothesis weaker than GRH; (ii) a new major-/minor-arc estimate
lemma; (iii) a precise barrier statement for the circle method at the binary problem. This dossier
delivers a sharpened form of (iii) and a program-shaped, honestly-limited version of (i).

---

## 3. State of the Art

All items `[ESTABLISHED]` unless flagged. Chronological within themes.

**Almost-all and exceptional set (binary).**
- Hardy & Littlewood (1923): under a quasi-GRH (no zeros of Dirichlet `L`-functions with real part
  `> 3/4`), almost all even numbers are Goldbach, `E(x) ≪ x^{1/2+ε}`.
- Chudakov (1937), van der Corput (1937), Estermann (1938), independently, unconditionally:
  `E(x) ≪ x (log x)^{−A}` for every `A` — almost all even numbers are Goldbach. Built on
  Vinogradov's minor-arc estimates plus `ℓ²`-averaging over `n` (Bessel's inequality).
- Montgomery & Vaughan (*The exceptional set in Goldbach's problem*, Acta Arith. 27, 1975):
  `E(x) ≪ x^{1−δ}` for an effectively computable `δ > 0`. Engine: Gallagher's log-free zero-density
  estimate near `σ = 1` plus careful handling of a possible exceptional (Siegel) zero.
- Subsequent exponent reductions: H. Li (`E(x) ≪ x^{0.921}`, c. 2000) `[ESTABLISHED*]`; W. C. Lu
  (`E(x) ≪ x^{0.879}`, c. 2010) `[ESTABLISHED*]`; J. Pintz has announced further improvements
  (toward exponent `2/3`) in work this legion has not verified in detail `[ESTABLISHED* — treat as
  announced]`.
- Under GRH: `E(x) ≪ x^{1/2+o(1)}` (essentially Hardy–Littlewood's argument run under GRH; later
  refinements sharpen the log powers) `[ESTABLISHED*]`.

**Ternary and approximations with more summands.**
- Vinogradov (1937): every sufficiently large odd `n` is a sum of three primes, unconditionally;
  constants originally ineffective (Siegel–Walfisz). Effective thresholds: Borozdkin (`3^{3^{15}}`,
  1956) `[ESTABLISHED*]`; Chen–Wang; Liu & Wang (`e^{3100}`, 2002) `[ESTABLISHED*]`.
- Deshouillers, Effinger, te Riele, Zinoviev (1997): ternary Goldbach for **all** odd `n ≥ 7`
  **under GRH**.
- Helfgott (2013, arXiv:1312.7748, *The ternary Goldbach conjecture is true*, with companion
  major-arc and minor-arc papers): ternary Goldbach for all odd `n ≥ 7`, **unconditional**. Inputs:
  new explicit minor-arc bounds, explicit major arcs using Platt's rigorous numerical verification
  of GRH for Dirichlet `L`-functions of small modulus up to bounded height (a finite computation,
  not a hypothesis), and the Helfgott–Platt numerical verification of ternary Goldbach up to
  `~8.875 × 10^{30}` (Exp. Math., 2013), which itself leverages the binary verification below. The
  proof is book-length and has circulated in revised manuscript form; it is widely accepted.
- Schnirelmann (1930): every integer `> 1` is a sum of a bounded number of primes. Ramaré (1995):
  every even integer is a sum of at most 6 primes. Kaniecki (1995): under RH, every odd integer
  `> 1` is a sum of at most 5 primes `[ESTABLISHED*]`. Tao (Math. Comp., 2014): every odd integer
  `> 1` is a sum of at most 5 primes, unconditionally.
- Linnik (1953): every large even `n` is a sum of two primes and `K` powers of 2, `K` absolute,
  unconditionally (conditional version 1951). Heath-Brown & Puchta (2002): `K = 13` unconditionally,
  `K = 7` under GRH `[ESTABLISHED*]`. Pintz & Ruzsa (part I 2003, part II 2020): `K = 8`
  unconditionally `[ESTABLISHED* — verify exact constant]`.

**Sieve side.**
- Chen Jingrun (announced 1966; full proof Sci. Sinica, 1973): every sufficiently large even `n` is
  `p + P₂` (prime plus a number with at most two prime factors), with a lower bound of the
  conjecturally correct order `≫ 𝔖(n) n / log²n` for the number of such representations. Key
  inputs: linear sieve, the switching principle, Bombieri–Vinogradov (level of distribution `1/2`,
  1965). Explicit/effective versions of Chen's theorem exist in preprint form (e.g., Yamada, 2015)
  `[ESTABLISHED* — preprint status]`.
- Selberg's parity problem: sieve upper/lower bounds alone cannot distinguish integers with an even
  vs. odd number of prime factors; this blocks "1+2 → 1+1" (see Friedlander–Iwaniec, *Opera de
  Cribro*, 2010, for the standard treatment). Parity has been broken only for special polynomial
  sequences (Friedlander–Iwaniec, `x² + y⁴`, Ann. of Math. 1998), by injecting bilinear/algebraic
  structure Goldbach does not currently offer.

**Computation.**
- Richstein (2001): binary Goldbach verified to `4 × 10^{14}` `[ESTABLISHED*]`. Oliveira e Silva,
  Herzog & Pardi (Math. Comp. 83, 2014): verified to `4 × 10^{18}` (with prime-gap computation to
  the same height). This is the current published record. See 09-06 for method.

**Zero technology.**
- Vinogradov–Korobov (1958): zero-free region `σ ≥ 1 − c/((log t)^{2/3}(log log t)^{1/3})`; explicit
  constants by Ford (2002) and later authors. Gallagher (1970): log-free zero-density near `σ = 1`.
  These drive every unconditional exceptional-set and ternary result above.

**What is NOT known.** Binary Goldbach is not known under RH, nor under GRH, nor under GRH plus any
standard zero-density or pair-correlation hypothesis `[FOLKLORE — see Section 5, C2 for the
structural reason]`. There is no known reduction of full binary Goldbach to a finite computation
under any widely-believed hypothesis.

---

## 4. Specialist Briefs (09-01 … 09-10)

### 09-01 — Binary vs. ternary; Vinogradov; Helfgott's theorem stated correctly

**Helfgott's theorem `[ESTABLISHED]`:** *Every odd integer `n ≥ 7` is the sum of three primes.*
The proof is unconditional. Two correctness guards on common misstatements: (i) the form "every
integer `n ≥ 5` is a sum of three primes" does **not** follow — for even `n` it would require
binary Goldbach; only the odd case is proved. (ii) The correct even-number corollary is: **every
even `n ≥ 10` is a sum of four primes** (apply the ternary theorem to the odd number `n − 3`;
smaller even cases by hand). Vinogradov (1937) had it for sufficiently large odd `n`; the entire post-1937 story
is the collapse of the threshold from ineffective, to `3^{3^{15}}`, to `e^{3100}`, to `10^{27}`-scale
thresholds meeting the `8.875 × 10^{30}` verification from below (Helfgott–Platt).

**Structural asymmetry (the theme of this whole dossier):** ternary has three variables; the circle
method needs one variable to "spend" on an `L∞` (sup) bound over minor arcs and two to spend on
Parseval. Binary has only the two Parseval variables and nothing to spend on the sup. Every honest
account of binary Goldbach must center this. See 09-08 and Section 5.

**Correctness guard:** weak Goldbach being proved does **not** make binary "almost proved." The gap
is not quantitative but structural (Section 5, C1). `[FOLKLORE]`

### 09-02 — Hardy–Littlewood circle method for Goldbach; the singular series

With `S`, `R(n)`, `𝔖(n)` as in Section 2: dissect `[0,1)` into major arcs `𝔐` (α near rationals
`a/q`, `q ≤ Q = (log N)^B`, arc half-width `Q/(qN)`) and minor arcs `𝔪 = [0,1) \ 𝔐`.

- **Major arcs `[ESTABLISHED]`:** on `𝔐`, `S(a/q + β) ≈ (μ(q)/φ(q)) v(β)` with
  `v(β) = Σ_{m≤N} e(mβ)`, error governed by Siegel–Walfisz. Summing over `q ≤ Q` produces the
  truncated singular series; for even `n`,

      ∫_𝔐 S(α)² e(−nα) dα = 𝔖(n)·n + O(n / (log n)^A).

  The singular series is a genuinely finite, computable Euler product; `𝔖(n) ∈ [2C₂, O(log log n)]`
  for even `n`. Its arithmetic meaning: the local densities of solutions of `p + q = n` at each
  prime; `𝔖(n) = 0` for odd `n` is the local obstruction at 2.
- **Minor arcs:** the open problem in its entirety. `|∫_𝔪 S²e(−nα)dα| = o(n)` for all large even
  `n` would prove binary Goldbach for large `n`; no such bound is known under any standard
  hypothesis. What is known is the `ℓ²`-average over `n` (09-04) — hence almost-all results.
- **Conjecture A `[ESTABLISHED as conjecture]`:** `R(n) ~ 𝔖(n) n`. Numerically superb: the
  Hardy–Littlewood prediction tracks the true representation counts closely throughout the verified
  range (see 09-06).

### 09-03 — Chen's theorem and the 1+2 barrier

**Chen (1973) `[ESTABLISHED]`:** for all large even `n`, `#{p ≤ n : n − p ∈ P₂} ≫ 𝔖(n) n / log²n`.
Mechanics: linear (Rosser–Iwaniec-type) sieve applied to the shifted set `{n − p}`, with
Bombieri–Vinogradov supplying level of distribution `1/2` in the remainder terms, and Chen's
**switching principle** converting the count of `n − p` with three prime factors into a more
sievable bilinear count. The same machinery gives infinitely many `p` with `p + 2 ∈ P₂` — the twin
analogue, underlining 09-10.

**The barrier `[ESTABLISHED as a meta-theorem / FOLKLORE in its informal use]`:** Selberg's parity
phenomenon: sieve axioms (upper/lower bound sifting functions plus level-of-distribution input) are
consistent with two different "worlds," in one of which the sifted set contains only integers with
an even number of prime factors. Hence no argument using only those axioms can produce `P₁` (a
prime) where parity permits `P₂`. Chen's `1+2` is exactly the parity wall. Breaking parity requires
extra structure (Friedlander–Iwaniec used algebraic structure of `x² + y⁴`; Goldbach's shifted set
`{n − p}` has no known analogue). Raising the level of distribution beyond `1/2` (Elliott–Halberstam
would give level `1 − ε`) improves constants and secondary terms but **does not break parity**:
even under the full Elliott–Halberstam conjecture, `1+1` does not follow by sieves alone.
`[FOLKLORE, standard]`

### 09-04 — Montgomery–Vaughan exceptional set

**Statement `[ESTABLISHED]`:** `E(x) ≪ x^{1−δ}`, `δ > 0` effective (Acta Arith. 27, 1975).

**Method sketch:** Write the minor-arc error `E_𝔪(n) = ∫_𝔪 S²e(−nα)dα`. Parseval over the
frequency variable `n` gives `Σ_n |E_𝔪(n)|² = ∫_𝔪 |S|⁴ ≤ (sup_𝔪 |S|)² ∫₀¹ |S|²`, and Vinogradov's
sup-bound turns this into an almost-all statement (this much is Chudakov–van der Corput–Estermann).
To get a **power** saving, Montgomery–Vaughan enlarge the major arcs massively (`Q` a small power of
`x`), which forces them to control `S` near rationals of large modulus without GRH: this is done
through the explicit formula with Gallagher's log-free zero-density estimate near `σ = 1`, plus a
dedicated argument neutralizing the possible Siegel zero (whose existence would bias primes in
progressions; M–V show the bias cannot create a power-of-`x`-sized exceptional set). The exponent
`1 − δ` is a direct function of the zero-density input — better density theorems, better `δ`; the
density hypothesis would give `1/2 + ε`; GRH gives `1/2 + o(1)` and **stalls there** (see 09-05).

**Key structural lesson:** every improvement in this line improves the *average* of `E_𝔪(n)` over
`n`. None of it says anything about a single stubborn `n`. The `ℓ²→ℓ∞` gap *is* the binary Goldbach
problem. `[FOLKLORE, made explicit here]`

### 09-05 — Vinogradov–Korobov zero-free regions; dependence of the binary problem on zeros

- The Vinogradov–Korobov region `σ ≥ 1 − c/((log t)^{2/3}(log log t)^{1/3})` `[ESTABLISHED]` yields
  the best unconditional error terms in the PNT (`exp(−c(log x)^{3/5−ε})`) and, transplanted to
  Dirichlet `L`-functions together with density estimates, powers all unconditional major-arc
  expansions. Explicit constants: Ford (2002) and subsequent explicit work `[ESTABLISHED*]`.
- **Siegel zeros.** The one possible real zero `β ≈ 1` of a real character's `L`-function makes
  Siegel–Walfisz ineffective and was the historical reason Vinogradov's ternary threshold was
  ineffective. Effective treatments (through to Helfgott) either verify numerically that no such
  zero exists for the moduli in play, or run a case analysis in which the exceptional zero's bias
  is explicitly carried. Curiously, in several binary-type problems a Siegel zero *helps* (its
  existence forces strong equidistribution elsewhere — cf. Heath-Brown's theorem that Siegel zeros
  imply infinitely many twin primes, Proc. LMS 1983 `[ESTABLISHED*]`); a fully worked Goldbach
  analogue ("Siegel zeros ⇒ binary Goldbach for large n") is not in the literature to this legion's
  knowledge and is flagged `[SPECULATIVE]` as a target — see Section 7.
- **The honest dependence table:** zero-free regions and zero densities control (a) how large `Q`
  (major-arc modulus range) can be, (b) the error in each arc, hence (c) the exceptional-set
  exponent. They do **not** touch the minor-arc `L²` mass, which is fixed by Parseval. Even the
  full GRH only moves the major/minor frontier to `Q ≈ N^{1/2}` (error per arc `≈ N^{1/2}log²N`
  from GRH's `ψ(x;q,a) = x/φ(q) + O(x^{1/2}log²x)`; beyond `q ≈ N^{1/2}` the "main term" `N/φ(q)`
  drowns in the error, so the arcs stop being major). Conclusion: **the binary problem's dependence
  on zeros saturates at the exceptional-set exponent `1/2`; zeros of L-functions are the wrong
  currency for the last step.** `[NEW-SYNTHESIS — quantified in Section 5, C2]`

### 09-06 — Explicit verification up to large X: method (Oliveira e Silva–Herzog–Pardi)

`[ESTABLISHED]` Binary Goldbach holds for all even `4 ≤ n ≤ 4 × 10^{18}` (Math. Comp. 83, 2014).
Method, correctly summarized:

1. **Minimal partitions.** For each even `n`, find the *minimal Goldbach prime* `p(n)`: the least
   prime `p` such that `n − p` is prime. Empirically `p(n)` is tiny (stays below `10⁴` throughout
   the verified range `[ESTABLISHED*]`), so the expected cost per `n` is a handful of primality
   tests of `n − p` for the first few primes `p`.
2. **Segmented sieve.** Work in long segments; precompute small primes; for each `n` in the
   segment, test `n − 2, n − 3, n − 5, …` — actually `n − p` over ascending small primes `p` —
   for primality.
3. **Primality certification.** Candidates `n − p` first pass strong probable-prime tests; the
   verification then rests on deterministic/certified testing valid in the range (and the
   computation was independently double-checked with different code paths) `[ESTABLISHED* on the
   certification details]`.
4. **By-products.** The same computation extended the tables of maximal prime gaps to `4 × 10^{18}`
   and recorded the champions of `p(n)`, both of independent interest.

**Role in the broader program:** this verification is a *load-bearing input* to Helfgott's ternary
proof: Helfgott–Platt cover odd `n ≤ 8.875 × 10^{30}` by choosing a ladder of primes `q` with
consecutive gaps `< 4 × 10^{18}` so that `n − q` lands in the verified even range. It would play the
identical role as the base case of any future effective reduction (Section 5, C3). **No bound
beyond `4 × 10^{18}` is asserted here**; larger figures circulating informally are not published
verifications.

### 09-07 — Major arcs: exactly what estimate is missing for a full proof

The major arcs are **not** the problem: they already produce `𝔖(n)n + o(n)` unconditionally for
`Q = (log N)^B`. The missing estimate is entirely on `𝔪`:

> **Missing Estimate (ME).** There exists `ε > 0` such that for all sufficiently large even `n`
> (with `N = n`):
>
>     | ∫_𝔪 S(α)² e(−nα) dα |  ≤  (2C₂ − ε) · n.
>
> ME implies binary Goldbach for all large even `n` (then finite verification would finish).

Facts about ME, each elementary given Section 5:

- The trivial bound is `∫_𝔪 |S|² = (1+o(1)) N log N` — bigger than the target by `≍ log N`.
  **ME is a "one-logarithm" problem in `L¹`-norm terms.** `[FOLKLORE, quantified here]`
- ME cannot be proved by any pointwise bound on `|S|` over `𝔪` (Parseval invariance; Section 5,
  C1). It cannot be proved under GRH by enlarging `𝔐` (Section 5, C2). It is known **on average
  over n** with power savings (09-04) — the entire difficulty is a single frequency.
- ME is *false* if `e(−nα)` is replaced by an adversarial unimodular phase; hence any proof must
  use the arithmetic of the specific frequency `n` against the phase distribution of `S(α)²` on
  `𝔪` — i.e., correlations of prime phases, an object on which zero-technology is silent.
  `[FOLKLORE, formalized in Section 5, C1]`

This is the sharpest honest answer to "what estimate is missing": not a better exponent anywhere,
but the first nontrivial bound of any strength on a *signed, single-frequency* minor-arc integral.

### 09-08 — Minor arcs and bilinear forms; why three variables beat two

**The classical minor-arc bound `[ESTABLISHED]`** (Vinogradov; streamlined via Vaughan's identity,
1977): for `|α − a/q| ≤ 1/q²`, `(a,q) = 1`,

    S(α) ≪ ( N q^{−1/2} + N^{4/5} + (Nq)^{1/2} ) · log⁴N,

so on minor arcs with `(log N)^B ≤ q ≤ N/(log N)^B`: `sup_𝔪 |S| ≪ N (log N)^{B/2 − const}` — an
arbitrary-log-power saving over the trivial `N`. Mechanism: Vaughan's identity splits `Λ` into
Type I sums (long smooth sums, handled by geometric-series/divisor bounds) and Type II **bilinear**
sums `Σ_m Σ_k a_m b_k e(αmk)`, where Cauchy–Schwarz plus the large-sieve/duality principle extracts
square-root cancellation in the free variable. This is close to the ceiling of bilinear technology:
`ℓ²`-normalized bilinear forms cannot beat square-root cancellation, and `|S(α)|` genuinely is of
size `≈ (N log N)^{1/2}` on an `α`-set of positive measure (forced by Parseval). `[FOLKLORE]`

**Why ternary is easier — the counting identity:**

    ternary error = ∫_𝔪 S³ e(−nα) dα,   |·| ≤ (sup_𝔪 |S|) · ∫₀¹ |S|² ≪ N(log N)^{−A} · N log N = N² (log N)^{1−A},

which loses to the ternary main term `≍ n²`. Two variables leave `∫_𝔪 |S|²`, which Parseval pins at
`(1+o(1)) N log N ≫ n` — **no third factor exists to absorb the sup-bound's saving.** Equivalent
viewpoint: ternary Goldbach for `n` is binary Goldbach for `n − p` *averaged over a long range of
`p`*, and averaging is exactly what the `ℓ²` theory (09-04) delivers. Binary for individual `n`
enjoys no averaging. `[ESTABLISHED mechanics / FOLKLORE framing]`

**Blocked escalations examined `[FAILED]`:**
- *Hölder with exponents `(2+δ, dual)` instead of `(∞, 2)`*: needs `∫_𝔪 |S|^{2+δ} = o(N^{1+δ/2}…)`
  -type moment gains; the fourth-moment `∫|S|⁴ ≍ N³` (sieve upper bound on `R` + Parseval) shows
  moments interpolate to nothing new for the binary target.
- *Amplification / dispersion (Linnik)*: dispersion re-introduces an average over a family — it
  proves almost-all/with-powers-of-2 theorems (which is exactly where it appears historically),
  never the single-frequency bound.
- *Additive-combinatorial transference (Green–Tao style)*: transference needs either positive
  density targets or three-term structure; binary Goldbach is a density-zero two-term equation,
  outside every known transference black box. (Density three-primes: X. Shao 2014 `[ESTABLISHED*]`
  — again ternary.)

### 09-09 — Goldbach under GRH / partial GRH: exactly what is proved conditionally

Conditional ledger, stated precisely `[ESTABLISHED unless flagged]`:

| Hypothesis | Consequence | Source |
|---|---|---|
| quasi-GRH (`β ≤ 3/4`) | `E(x) ≪ x^{1/2+ε}` | Hardy–Littlewood 1923 |
| GRH | `E(x) ≪ x^{1/2} (log x)^{O(1)}` | H–L machinery, refined `[ESTABLISHED*]` |
| GRH | ternary Goldbach, all odd `n ≥ 7` | Deshouillers–Effinger–te Riele–Zinoviev 1997 |
| RH | every odd `n > 1` sum of ≤ 5 primes | Kaniecki 1995 `[ESTABLISHED*]` |
| GRH | every large even `n = p + q + 2^{k₁} + … + 2^{k₇}` | Heath-Brown–Puchta 2002 `[ESTABLISHED*]` |
| finite GRH verification (Platt) | unconditional ternary (as computational input) | Helfgott 2013 |
| — (no hypothesis) | `E(x) ≪ x^{0.879}` `[ESTABLISHED*]`; `n = p + P₂` (Chen); `n = p + q + 8 powers of 2` `[ESTABLISHED*]` | Lu; Chen; Pintz–Ruzsa |

**The two honest headlines:** (1) *Binary Goldbach for all (large) even `n` is not known under
GRH*, nor under GRH + density hypotheses, nor under Elliott–Halberstam, nor under any combination
of standard conjectures short of assuming quantitative Goldbach-type correlations themselves.
(2) What GRH buys is exactly the square-root frontier: exceptional set `x^{1/2+o(1)}`, major arcs to
`Q ≈ N^{1/2}` — and Section 5, C2 shows this is *structurally* the end of that road, not a lack of
cleverness. `[FOLKLORE + NEW-SYNTHESIS]`

**Averages and RH-equivalences (the reverse direction):** the *average* of Goldbach representations
detects RH: Fujii showed (under RH) `Σ_{n≤x} R(n) = x²/2 − 2Σ_ρ x^{ρ+1}/(ρ(ρ+1)) + smaller`, and
work of Granville and of Bhowmik–Schlage-Puchta makes precise that square-root-quality error terms
in `Σ_{n≤x} R(n)` are *equivalent* to RH `[ESTABLISHED* — details from memory]`. So Goldbach-on-
average is an RH-level statement, while Goldbach-for-every-`n` is strictly beyond: another precise
sense in which the conjecture sits above the zero hierarchy.

### 09-10 — Twin primes and binary Goldbach: two sides of Hardy–Littlewood

Both problems are single-frequency statements about the **same** object, the Fourier transform of
the primes:

- Goldbach: `R(n) = ∫₀¹ S(α)² e(−nα) dα` — the *additive convolution* `(Λ ⋆ Λ)(n)`.
- Twins (shift `h`): `T(h) = Σ_{m≤N} Λ(m)Λ(m+h) = ∫₀¹ |S(α)|² e(hα) dα + boundary terms` — the
  *autocorrelation* of `Λ`.

Hardy–Littlewood's 1923 paper conjectures both asymptotics with the **same singular series**:
`R(n) ~ 𝔖(n)n` (Conjecture A) and `T(h) ~ 𝔖(h)N` for even `h` (Conjecture B; `𝔖` literally the
same Euler product evaluated at `n` vs `h`). Twin primes = "Goldbach at frequency `−h`". The major
arcs prove both up to identical minor-arc errors; the parity barrier blocks the sieve route to both
at the same point (`p + 2 = P₂` and `n − p = P₂` are the same Chen theorem); and the following
**exact identity** `[FOLKLORE — elementary Parseval, stated precisely]` shows their errors are not
just analogous but *conserved in aggregate*:

    Σ_{n} R(n)²  =  ∫₀¹ |S(α)|⁴ dα  =  Σ_{h∈ℤ} T(h)²

(both outer sums finite ranges induced by `[1, N]`; `T(0) = Σ Λ² ≈ N log N` is the diagonal). The
second moment of Goldbach representations **equals** the second moment of twin-type correlations.
Any asymptotic for `∫|S|⁴` is equivalent to mean-square knowledge of both problems simultaneously;
its true order `≍ N³` is known by sieve upper bounds, its asymptotic is open — and *would follow
from either* Conjecture A or B in mean-square form. Differences worth recording: the twin integrand
`|S|²e(hα)` is built from a nonnegative function (positivity exploitable: Goldston–Pintz–Yıldırım,
Zhang 2014, Maynard 2015, Polymath8 got **bounded gaps** by sieving positive measures — an averaged
-over-`h` triumph with no Goldbach analogue, because Goldbach's `S²` is signed and its frequency
`n` is not averageable). Conversely Goldbach has the finite-verification + exceptional-set
structure twins lack (`E(x) ≪ x^{0.879}` has no twin analogue — "almost all shifts `h` admit twin
-like pairs" is trivial by pigeonhole on `Σ_h T(h)`). `[ESTABLISHED/FOLKLORE as labeled]`

---

## 5. Candidate Contributions of This Legion

All four are honesty-labeled; none is claimed as a proof of any open conjecture. C1–C2 constitute
the dossier's response to the mission's "precise barrier" breakthrough criterion; realistic status:
**formalized folklore plus one possibly-new quantification — incremental.**

### C1. The Modulus Barrier (precise barrier for the circle method at binary Goldbach)

**Lemma A (minor arcs carry the mass).** `[FOLKLORE; proof sketch below is rigorous]`
Let `Q = (log N)^B`, `𝔐 = ⋃_{q≤Q}⋃_{(a,q)=1} {α : |α − a/q| ≤ Q/(qN)}`, `𝔪` the complement. Then

    ∫₀¹ |S|² = (1+o(1)) N log N,     ∫_𝔐 |S|² ≍ N log Q,     hence   ∫_𝔪 |S|² = (1+o(1)) N log N.

*Proof sketch.* Parseval: `∫₀¹|S|² = Σ_{m≤N} Λ(m)² = (1+o(1)) N log N` (PNT + partial summation;
prime powers negligible). On each major arc, Siegel–Walfisz gives `S(a/q+β) = (μ(q)/φ(q))v(β) +
O(N exp(−c√(log N)))`; since `∫_{|β|≤Q/(qN)} |v|²dβ ≍ N` (the mass of `|v|²` sits in `|β| ≲ 1/N`
and each arc has width `≥ 1/N`), summing `φ(q)` arcs per `q` gives
`∫_𝔐 |S|² ≍ N Σ_{q≤Q} μ²(q)/φ(q) ≍ N log Q = O(N·B log log N) = o(N log N)`. Subtract. ∎

**Theorem B (adversarial-phase barrier).** `[FOLKLORE in spirit; this formalization produced
in-run; elementary; novelty of the formulation uncertain]`
Call an upper-bound argument for `E_𝔪(n) = ∫_𝔪 S²e(−nα)dα` a **modulus argument** if the bound it
produces remains valid when `S(α)` is replaced on `𝔪` by `|S(α)|·u(α)` for an arbitrary measurable
unimodular `u`. Then no modulus argument can prove `|E_𝔪(n)| = o(N log N)`; in particular none can
prove ME (09-07), whose target is `O(n)`. *Proof.* Choose `u(α)² = e(nα)·sign-conjugate`, i.e.
`u(α)² e(−nα) = 1`; then the integral equals `∫_𝔪 |S|² = (1+o(1))N log N` by Lemma A. ∎

*Scope and honesty:* every pointwise exponential-sum estimate (Vinogradov, Vaughan, Heath-Brown
identities, any future improvement of `sup_𝔪|S|` all the way down to the Parseval floor
`(N log N)^{1/2}`), every Hölder/moment combination applied to `|S|` restricted to `𝔪`, and every
enlargement of `𝔐` compatible with Lemma-A-type mass counts, is a modulus argument. **Not** covered
(and therefore not ruled out): arguments using the phase of `S` — `ℓ²`-averaging over `n` (Bessel;
gives 09-04's almost-all theorems: `Σ_n |E_𝔪(n)|² = ∫_𝔪|S|⁴`, which *does* use phases through
orthogonality), sieve methods (Chen), dispersion, identities coupling `n` to the primes. The
barrier thus delimits exactly the class of arguments that proved ternary Goldbach and explains,
in one line, why that toolbox cannot close binary: **ternary died to a sup-bound, and sup-bounds
are modulus arguments; binary requires a phase argument at a single frequency, and no such
argument exists in the literature.**

**Quantified gap.** The overshoot of the best possible modulus bound over the target is the factor

    ( ∫_𝔪 |S|² ) / ( 𝔖(n)·n )  ≍  log n / 𝔖(n)  ∈  [ c·log n / log log n ,  C·log n ].

Binary Goldbach via the circle method is "one logarithm" away in `L¹`, and that logarithm is
provably invisible to absolute values. Any method extracting a uniform-in-`n` relative saving
`≥ C·log N` from the phase `e(−nα)` on `𝔪` proves the conjecture for large `n`. `[NEW-SYNTHESIS
framing of folklore facts]`

### C2. GRH halves the barrier and can do no more

`[NEW-SYNTHESIS — elementary computation produced in-run; believed correct; needs referee;
possibly known to experts but not located in writing by this legion]`

Assume GRH. Per-arc errors become `O(N^{1/2}log²N)`, allowing major arcs up to `Q = N^θ`. The mass
they capture is `∫_𝔐 |S|² ≍ N Σ_{q≤N^θ} μ²(q)/φ(q) ≍ θ · N log N`, while keeping the total
major-arc error below the main term forces (error² × measure ≈ `N log⁴N · Q²/N`) the constraint
`Q ≪ N^{1/2}/log²N`, i.e. `θ ≤ 1/2`. Therefore **under GRH at least `(1/2 − o(1)) · N log N` of
`L²`-mass remains on the minor arcs**, still exceeding the target `𝔖(n)n` by `≍ log n`. Combined
with Theorem B (which applies verbatim to the shrunken minor arcs): *GRH plus any modulus argument
cannot prove binary Goldbach; the hypothesis buys at most a factor 2 of barrier mass.* This gives a
precise structural explanation of the empirical ledger in 09-09 (GRH stalls at `E(x) ≈ x^{1/2}`)
and answers, in the negative and with a reason, the perennial question "would GRH settle Goldbach?"

### C3. Reduction schema under a weaker-than-GRH, finitely checkable hypothesis

`[PROGRAM + NEW-SYNTHESIS; no new theorem claimed; constants not tracked in this run]`

Define the checkable hypothesis `ZV(Q, T, θ)`: *every zero `ρ = β + iγ` of every Dirichlet
`L`-function of modulus `q ≤ Q` with `|γ| ≤ T` satisfies `β ≤ θ`.* For `θ = 1/2` this is a finite
GRH verification of exactly the kind Platt performed (rigorous interval-arithmetic computation);
for `θ` slightly above `1/2` it is strictly weaker and cheaper. The schema:

1. Effectivize the Hardy–Littlewood/Chudakov major-arc expansion with all constants explicit,
   using `ZV(Q, T, θ)` in the explicit formula for `ψ(x; q, a)` in place of GRH (Helfgott's
   major-arc machinery is precisely this technology and can be reused).
2. Effectivize the `ℓ²` minor-arc argument (Bessel + explicit Vaughan-type sup bounds; Helfgott's
   explicit minor-arc paper again supplies constants).
3. Output shape: explicit `N₀ = N₀(Q, T, θ)` and `δ = δ(θ) > 0` with: every even
   `n ∈ [4 × 10^{18}, N₀]` is a sum of two primes, **except** for at most `N₀^{1−δ}` values lying
   in an explicitly enumerable residue-structured list; the list is then destroyed by targeted
   computation (each candidate checked as in 09-06).
4. Result: binary Goldbach verified up to `N₀` — with `N₀` astronomically beyond direct-search
   range — under a finite, checkable, weaker-than-GRH hypothesis discharged by computation, i.e.,
   unconditionally after the computation.

**Honest limitation (forced by C1/C2):** the schema can never set `N₀ = ∞`; the `ℓ²→ℓ∞` gap means
the exceptional list is thin but never provably empty. This is a *range-extension engine* (the
binary analogue of what Helfgott–Platt's ladder did for ternary), not a path to the conjecture. It
is the maximal honest content of the mission's breakthrough criterion (i) on current technology —
and the reason it is maximal is exactly C1/C2.

### C4. The energy identity (twin–Goldbach conservation law)

`[FOLKLORE — elementary; recorded because it is the sharpest one-line form of angle 09-10]`

    Σ_n R(n)² = ∫₀¹ |S|⁴ = Σ_h T(h)².

Goldbach-representation energy and twin-correlation energy are the same number. Corollaries worth
stating: (a) mean-square Goldbach asymptotics and mean-square twin asymptotics are one problem, not
two; (b) any hypothetical sequence of "Goldbach-violating" even numbers of positive lower density
in a dyadic range would force an abnormal deficit in `Σ_h T(h)²` against its sieve-bounded order —
too weak to derive a contradiction (hence `[FAILED]` as an attack: the known upper bound
`∫|S|⁴ ≪ N³` has the wrong direction and mean-square statements cannot see density-zero
exceptional sets, which is again the `ℓ²→ℓ∞` wall).

---

## 6. Obstruction Analysis: Why Binary Goldbach Resists

Consolidated failure map — each route, its best achievement, and the named wall it hits:

| Route | Best result achieved | Wall |
|---|---|---|
| Circle method, absolute values | ternary Goldbach (Helfgott); binary almost-all | **Modulus/Parseval barrier** (C1): minor-arc `L²` mass `≍ N log N ≫ n`, no third variable |
| Circle method + GRH | `E(x) ≪ x^{1/2+o(1)}`; major arcs to `N^{1/2}` | **Half-mass cap** (C2): `θ ≤ 1/2`, barrier persists |
| `ℓ²` averaging over `n` | `E(x) ≪ x^{0.879}` `[ESTABLISHED*]` | **`ℓ² → ℓ∞` gap**: averages can't reach individual `n` |
| Sieves (linear, weighted, switching) | Chen `1+2`, correct-order lower bounds | **Parity problem** (Selberg): `P₂` floor without extra structure |
| Level of distribution improvements (toward EH) | better constants; bounded gaps on twin side | parity is level-independent |
| Adding degrees of freedom | `p + q + 8·{2^k}` `[ESTABLISHED*]`; four primes for even `n` | each added variable is exactly the thing binary forbids |
| Positivity/majorant + averaging over shift | bounded prime gaps (Zhang/Maynard/Polymath8) | Goldbach's `S²` is signed and its frequency fixed — no shift to average |
| Transference/density methods | density ternary theorems `[ESTABLISHED*]` | binary is a density-zero, two-variable equation |
| Mean-square/energy identities | C4 identity; `∫|S|⁴ ≍ N³` | wrong inequality direction; blind to thin exceptional sets |
| Computation | `4 × 10^{18}` (published) | pure verification cannot terminate; C3 extends range only |

The picture is coherent rather than accidental: **every known technique factors through either an
absolute value or an average, and binary Goldbach is precisely the statement that survives both.**
The problem is not adjacent to ternary Goldbach with a bigger constant; it sits on the far side of
a barrier that ternary never had to cross. A future proof needs a genuinely new mechanism for
detecting cancellation in a *signed* prime exponential-sum square at a *single* frequency — phase
information about primes of a kind that zeros of `L`-functions demonstrably (C2) do not encode.

---

## 7. Verdict, Open Problems, Next Steps

**Verdict (per README taxonomy): known / incremental.**
- No proof, no conditional proof, no reduction of full binary Goldbach to computation — and C1/C2
  give a precise argument that the last of these is impossible for the entire absolute-value circle
  -method toolbox, GRH included.
- Candidate incremental contribution: the **Modulus Barrier** package (C1 formalization + C2
  half-mass quantification) as a precise-barrier deliverable, and the C3 range-extension schema.
  All flagged for expert refereeing; C1's core is folklore made precise, C2 may be new as an
  explicit statement, C3 is an engineering program over Helfgott-grade components.
- Explicitly not claimed: any new proof of weak Goldbach (Helfgott's theorem used as known input);
  any verification bound beyond the published `4 × 10^{18}`; any improvement of any cited exponent.

**Sharpest open sub-problems this legion would attack next, in order:**
1. **Any phase-sensitive minor-arc bound.** Prove *any* uniform-in-`n` bound
   `|E_𝔪(n)| ≤ (1 − c)·∫_𝔪|S|²` with fixed `c > 0` — i.e., beat the triangle inequality by a
   constant, not yet a log. Even this is open and would be the first crack in the modulus barrier.
2. **Siegel-zero dichotomy for Goldbach** `[SPECULATIVE]`: adapt Heath-Brown's twin-prime-from-
   Siegel-zeros mechanism to `n − p`; success would prove "either no Siegel zeros beyond X, or
   binary Goldbach for large n in explicit ranges," a genuinely new conditional structure.
3. **Execute C3** with tracked constants: target `N₀ ≥ 10^{100}`-scale verified Goldbach under a
   finite `ZV(Q, T, θ)` computation — a headline range extension by ~80 orders of magnitude over
   direct search, honest about being range-only.
4. **Energy asymptotics:** an asymptotic for `∫₀¹|S|⁴` (equivalently mean-square twin correlations)
   — below the barrier yet open, and the natural next averaged milestone after 09-04.
5. **Literature task:** determine whether C2's half-mass cap appears in print (candidate venues:
   Vaughan's tract on the Hardy–Littlewood method; surveys of the Goldbach problem); if absent,
   write it up as a short note.

---

### References (non-exhaustive; confidence-flagged where recalled from memory)

- Hardy, G. H., Littlewood, J. E., *Some problems of 'Partitio numerorum' III: On the expression of a number as a sum of primes*, Acta Mathematica 44 (1923). `[ESTABLISHED]`
- Vinogradov, I. M., *Representation of an odd number as a sum of three primes* (1937). `[ESTABLISHED]`
- Chudakov, N. G. (1937); van der Corput, J. G. (1937); Estermann, T., *On Goldbach's problem…*, Proc. London Math. Soc. (1938) — almost-all binary Goldbach. `[ESTABLISHED*]`
- Linnik, Yu. V., primes plus powers of two (1951 conditional; 1953 unconditional). `[ESTABLISHED*]`
- Bombieri, E.; Vinogradov, A. I. — mean-value theorem, level of distribution 1/2 (1965). `[ESTABLISHED]`
- Gallagher, P. X., *A large sieve density estimate near σ = 1*, Invent. Math. (1970). `[ESTABLISHED*]`
- Chen, J. R., *On the representation of a larger even integer as the sum of a prime and the product of at most two primes*, Sci. Sinica 16 (1973). `[ESTABLISHED]`
- Montgomery, H. L., Vaughan, R. C., *The exceptional set in Goldbach's problem*, Acta Arithmetica 27 (1975). `[ESTABLISHED]`
- Vaughan, R. C., identity for Λ (1977); *The Hardy–Littlewood Method*, 2nd ed., Cambridge Tracts 125 (1997). `[ESTABLISHED]`
- Heath-Brown, D. R., *Prime twins and Siegel zeros*, Proc. London Math. Soc. (1983). `[ESTABLISHED*]`
- Fujii, A., additive problems of prime numbers (c. 1991). `[ESTABLISHED*]`
- Kaniecki, L., on Šnirel'man's constant under RH, Acta Arith. (1995). `[ESTABLISHED*]`
- Ramaré, O., *On Šnirel'man's constant*, Ann. Scuola Norm. Sup. Pisa (1995) — six primes. `[ESTABLISHED]`
- Deshouillers, J.-M., Effinger, G., te Riele, H., Zinoviev, D., ternary Goldbach under GRH, Electron. Res. Announc. AMS 3 (1997). `[ESTABLISHED]`
- Friedlander, J., Iwaniec, H., primes of the form `x² + y⁴`, Ann. of Math. (1998); *Opera de Cribro*, AMS (2010). `[ESTABLISHED]`
- Li, H., exceptional set exponent ≈ 0.921 (c. 2000). `[ESTABLISHED*]`
- Richstein, J., verification to `4 × 10^{14}`, Math. Comp. 70 (2001). `[ESTABLISHED*]`
- Ford, K., *Vinogradov's integral and bounds for the Riemann zeta function*, Proc. London Math. Soc. (2002). `[ESTABLISHED*]`
- Heath-Brown, D. R., Puchta, J.-C., primes and powers of 2, Asian J. Math. (2002). `[ESTABLISHED*]`
- Liu, M.-C., Wang, T.-Z., ternary threshold `e^{3100}` (2002). `[ESTABLISHED*]`
- Pintz, J., Ruzsa, I. Z., primes and powers of 2, parts I (2003) and II (2020). `[ESTABLISHED*]`
- Granville, A., refinements of Goldbach and GRH, Funct. Approx. Comment. Math. (2007). `[ESTABLISHED*]`
- Bhowmik, G., Schlage-Puchta, J.-C., mean representation numbers (c. 2010). `[ESTABLISHED*]`
- Lu, W. C., exceptional set exponent ≈ 0.879 (c. 2010). `[ESTABLISHED*]`
- Helfgott, H. A., *Minor arcs for Goldbach's problem* (2012); *Major arcs for Goldbach's problem* (2013); *The ternary Goldbach conjecture is true*, arXiv:1312.7748 (2013). `[ESTABLISHED]`
- Helfgott, H. A., Platt, D., numerical verification of ternary Goldbach to `8.875 × 10^{30}`, Experimental Mathematics 22 (2013). `[ESTABLISHED]`
- Zhang, Y. (2014); Maynard, J. (2015); Polymath8 — bounded gaps between primes (twin-side context). `[ESTABLISHED]`
- Oliveira e Silva, T., Herzog, S., Pardi, S., empirical verification of even Goldbach and prime gaps to `4 × 10^{18}`, Math. Comp. 83 (2014). `[ESTABLISHED]`
- Tao, T., every odd number greater than 1 is a sum of at most five primes, Math. Comp. 83 (2014). `[ESTABLISHED]`
- Shao, X., density version of the three-primes theorem (2014). `[ESTABLISHED*]`
- Yamada, T., explicit Chen's theorem (2015, preprint). `[ESTABLISHED* — preprint]`

*End of dossier — LEGION 09.*
