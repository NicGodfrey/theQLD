# Goldbach — Wave-2 Breakthrough

**Legion:** 09 (Goldbach), Wave 2.
**Task:** Upgrade the *Modulus Barrier* of `REPORT.md` (§5, C1) from a lemma-plus-observation
package into a **single, self-contained theorem** with a complete proof — every integral executed —
and an explicit main-term versus minor-arc comparison.

**Standing disclaimers.** No proof of binary Goldbach is claimed or attempted. No new proof of
ternary Goldbach is claimed (Helfgott's theorem is background only). The theorem below is a
*limitation theorem*: it rigorously delimits a class of circle-method arguments and proves that this
class cannot close binary Goldbach. It says nothing about the true size of the minor-arc integral,
which is conjecturally tiny. Honesty labels are those of `REPORT.md`.

---

## Theorem

### Setup and conventions

Throughout, `N` is a large integer, `e(x) = e^{2πix}`, and `p, q` denote primes. We fix once and for
all the **weighted** generating function (the log-weighted sum over primes; used consistently
everywhere below):

    S(α) = Σ_{p ≤ N} (log p) · e(pα),        α ∈ [0, 1).

`S` is a trigonometric polynomial, hence continuous; all integrals below are finite. Fix `B ≥ 1` and
set

    Q = (log N)^B,
    𝔐(q, a) = { α ∈ [0,1) : ‖α − a/q‖ ≤ Q/(qN) },   for 1 ≤ q ≤ Q, 1 ≤ a ≤ q, gcd(a, q) = 1,
    𝔐 = ⋃_{q ≤ Q} ⋃_{(a,q)=1} 𝔐(q, a)   (major arcs),      𝔪 = [0,1) \ 𝔐   (minor arcs),

where `‖·‖` is distance to the nearest integer (so the arc at `1/1` is the arc at `0`). For even
`n ≤ N` put

    R(n)   = Σ_{p + q = n} (log p)(log q) = ∫₀¹ S(α)² e(−nα) dα     (ordered pairs),
    E_𝔪(n) = ∫_𝔪 S(α)² e(−nα) dα                                    (minor-arc contribution),

and let `𝔖(n)` be the Hardy–Littlewood singular series for even `n`:

    𝔖(n) = 2 C₂ · Π_{p | n, p > 2} (p−1)/(p−2),      C₂ = Π_{p > 2} (1 − (p−1)^{−2}).

**Definition (modulus bound).** Fix `N`, `B` (hence `𝔪`) and an even `n ≤ N`. A real number
`M ≥ 0` is a **modulus bound** at frequency `n` if

    | ∫_𝔪 f(α)² e(−nα) dα | ≤ M     for every measurable f : 𝔪 → ℂ with |f(α)| ≤ |S(α)| on 𝔪.

Let `M_min(N, n)` denote the least modulus bound.

*Scope note.* Every classical minor-arc treatment outputs a modulus bound: pointwise exponential-sum
estimates (Vinogradov, Vaughan's identity, Heath-Brown's identity, and any future refinement of
`sup_𝔪 |S|`) are upper bounds on `|S(α)|` valid on Diophantine classes of `α`, and every way of
combining them — triangle inequality, `sup × measure`, Hölder, moments of `|S|` over `𝔪` — is
monotone in the modulus, hence yields a number valid for **all** `f` with `|f| ≤ |S|`. What is *not*
a modulus bound: anything using the phase of `S`, e.g. Bessel/large-sieve averaging over `n`, sieve
methods, dispersion. See "Why binary Goldbach remains open."

### Established inputs (used with proof citations, not reproved)

- **(E1)** Prime Number Theorem with classical error term: `θ(x) := Σ_{p ≤ x} log p = x +
  O(x·exp(−c√(log x)))`; and Chebyshev's bound `θ(x) ≤ 2x` for all `x ≥ 2`. `[ESTABLISHED]`
- **(E2)** Siegel–Walfisz: for every `A > 0` there is `c_A > 0` with
  `θ(x; q, b) := Σ_{p ≤ x, p ≡ b (q)} log p = x/φ(q) + O_A(x·exp(−c_A√(log x)))`, uniformly for
  `q ≤ (log x)^A`, `gcd(b, q) = 1`. (Constants ineffective; irrelevant here.) `[ESTABLISHED]`
- **(E3)** Mertens: `Π_{p ≤ y} (1 − 1/p)^{−1} ≤ C_M log y` for `y ≥ 2`; the harmonic bound
  `Σ_{q ≤ Q} 1/q ≤ 1 + log Q`; and the Chebyshev-grade bound `p_k ≤ 2k log k` for the `k`-th prime,
  `k ≥ 3`. `[ESTABLISHED]`
- **(E4)** Ramanujan sum: `Σ_{b mod q, (b,q)=1} e(ab/q) = μ(q)` when `gcd(a, q) = 1`. `[ESTABLISHED]`
  (two-line proof included in Step 4 anyway).
- **(E5)** *(context only — cited to justify the name "main term," never used in the proof)*
  Hardy–Littlewood major-arc asymptotic: for every `A > 0` there is `B(A)` such that with
  `Q = (log N)^{B(A)}`, for even `n ∈ (N/2, N]`,
  `∫_𝔐 S(α)² e(−nα) dα = 𝔖(n)·n + O_A(n (log n)^{−A})`. `[ESTABLISHED]` (Hardy–Littlewood 1923;
  modern treatment as in Vaughan, *The Hardy–Littlewood Method*, whose ternary Chapter-3 mechanics
  are identical for the binary major arcs.)

### Theorem (Modulus Barrier for binary Goldbach — single-theorem form)

**Theorem.** *Fix `B ≥ 1` and let `N` be sufficiently large (in terms of `B`), with `S`, `𝔐`, `𝔪`,
`M_min` as above. Then:*

**(i) (Total mass — Parseval.)**

    ∫₀¹ |S(α)|² dα = Σ_{p ≤ N} (log p)² = N log N + O(N).

**(ii) (The mass lives on the minor arcs.)**

    ∫_𝔐 |S(α)|² dα ≪_B N (log log N)²,
    hence   ∫_𝔪 |S(α)|² dα = N log N · (1 + O_B((log log N)² / log N)) = (1 + o(1)) · N log N.

**(iii) (Size of the singular-series main term.)** *For every even `n ≥ 16`,*

    2C₂ ≤ 𝔖(n) ≤ (C₂/2) · (n/φ(n))² ≪ (log log n)²,     with C₂ > 0   (2C₂ = 1.3203…, numeric value [ESTABLISHED*]).

*Thus the circle-method main term `𝔖(n)·n` satisfies `𝔖(n)·n ≍ n` up to a factor `(log log n)²`.*

**(iv) (Exact optimum of the modulus class — adversarial phase.)** *For every even `n ≤ N`,*

    M_min(N, n) = ∫_𝔪 |S(α)|² dα,

*and the minimum is attained: the triangle inequality certifies `∫_𝔪 |S|²` as a valid modulus
bound, while the adversarial competitor `f*(α) = |S(α)| · u(α)` with `u(α) = e(nα/2)` (unimodular,
and 1-periodic because `n` is even) satisfies `|f*| = |S|` and*

    ∫_𝔪 f*(α)² e(−nα) dα = ∫_𝔪 |S(α)|² dα.

*In particular, within the modulus class the triangle inequality is **lossless**: the logarithm
below is not lost to crude estimation but is irrecoverable without phase information.*

**(v) (The logarithmic gap — explicit main-term vs minor-arc comparison.)** *Take `n = N` even.
Then*

    M_min(N, N) / (𝔖(N)·N)  ≥  c_B · (log N) / (log log N)²  →  ∞,

*and consequently:*

- **(v.a)** *No modulus bound is `≤ (1 − ε) N log N` for any fixed `ε > 0` and `N` large: modulus
  arguments cannot improve on the triangle inequality even by a constant factor.*
- **(v.b)** *No modulus bound can establish the Missing Estimate of `REPORT.md` §09-07, i.e.
  `|E_𝔪(n)| ≤ (2C₂ − ε)·n`; indeed none can establish even `|E_𝔪(n)| ≤ N (log N)^{1−ε}`. The
  modulus class overshoots the entire main term by a factor `≍ log N` (up to `(log log N)²`).*
- **(v.c)** *The specific classical bound shapes are each individually dominated: pointwise on `𝔪`,*

      ∫_𝔪 |S|² dα  ≤  (sup_𝔪 |S|) · ∫_𝔪 |S| dα  ≤  (sup_𝔪 |S|)² · meas(𝔪),

  *so the triangle-inequality bound, the `sup·L¹` bound, and the `sup²·measure` bound are all
  `≥ (1 − o(1)) N log N`, regardless of the quality of the pointwise estimate fed into them.*

**Corollary (pointwise bounds cannot cancel the integral — square-root floor).**

1. *Parseval forces `sup_𝔪 |S| ≥ (∫_𝔪 |S|² / meas(𝔪))^{1/2} ≥ (1 − o(1))^{1/2} (N log N)^{1/2}`:
   no pointwise bound on `𝔪` can go below the square-root floor `(N log N)^{1/2}`.*
2. *Even the impossible best case fails: if some estimate gave `|S(α)| ≤ β(α)` on `𝔪`, then the
   resulting modulus bound is `∫_𝔪 β² ≥ ∫_𝔪 |S|² = (1 − o(1)) N log N` — a logarithm above the main
   term — even for the extreme (false) hypothesis `β ≡ (N log N)^{1/2}`.*
3. *Reality is far from that extreme anyway: `sup_𝔪 |S| ≥ N/(8Q) = N (log N)^{−B}/8`, attained just
   outside the arc at `0`; so "square-root cancellation everywhere on `𝔪`" is not merely
   unprovable but false. Yet by 2. its truth would not have helped. The failure is located entirely
   in the modulus step, and by (iv) the modulus step is exactly optimal in its class.*

**Remarks.**

1. *(Normalization independence.)* With the unweighted `S₀(α) = Σ_{p ≤ N} e(pα)` one has
   `∫₀¹ |S₀|² = π(N) ~ N/log N` while the unweighted main term is `≍ 𝔖(n)·n/log²n`; the same
   factor-`log n` gap reappears. The barrier does not depend on the choice of weights; we fixed the
   weighted version throughout.
2. *(GRH does not remove the barrier.)* The theorem applies verbatim to any enlarged major-arc
   system for which `∫_𝔐 |S|² = o(N log N)`. Under GRH the arcs can grow to modulus `Q ≈ N^{1/2}`,
   capturing at most half the mass; at least `(1/2 − o(1)) N log N` remains on `𝔪` — still a
   logarithm above the main term. See `REPORT.md` §5, C2 `[NEW-SYNTHESIS]`; not reproved here.
3. *(What the theorem does not restrict.)* Arguments using the phase of `S` are outside the modulus
   class: Bessel/large-sieve averaging over `n` (which proved the almost-all theorems), sieve
   methods (Chen), dispersion, and identities coupling `n` to the primes. Each has its own named
   wall (`ℓ² → ℓ∞` gap, parity, re-averaging); see the penultimate section.

---

## Proof (complete, with integrals)

**Step 0 (conventions).** `N` large in terms of `B`; `c, C, C₁, C₂, …` denote positive constants,
`C_B`-type constants may depend on `B`. Since `Q³ = (log N)^{3B} = o(N)`, all inequalities of the
form `N > KQ³` used below hold for `N` large. `S` is a finite exponential sum, so `|S| ≤ θ(N) ≤ 2N`
everywhere (E1 Chebyshev), and every integral below converges absolutely.

**Step 1 (Parseval — proof of (i)).** Expanding the square and integrating term by term,

    ∫₀¹ |S(α)|² dα = Σ_{p, p' ≤ N} (log p)(log p') ∫₀¹ e((p − p')α) dα = Σ_{p ≤ N} (log p)²,

by orthogonality: `∫₀¹ e(kα) dα = 1` if `k = 0` and `= 0` for `k ∈ ℤ \ {0}`. Evaluate the prime sum
by Riemann–Stieltjes partial summation against `θ`:

    Σ_{p ≤ N} (log p)² = ∫_{2⁻}^{N} (log x) dθ(x) = θ(N) log N − ∫_{2}^{N} θ(x)/x dx.

By (E1), `θ(N) log N = N log N + O(N exp(−c√(log N)) · log N) = N log N + O(N)`, and by Chebyshev
`0 ≤ ∫₂^N θ(x)/x dx ≤ 2N`. Hence

    ∫₀¹ |S|² dα = N log N + O(N).                                                       ∎(i)

**Step 2 (arc geometry).** Distinct Farey fractions `a/q ≠ a'/q'` with `q, q' ≤ Q` satisfy
`|a/q − a'/q'| ≥ 1/(qq') ≥ Q^{−2}`, while the two arc half-widths sum to at most `2Q/N`. Since
`2Q/N < Q^{−2}` (i.e. `N > 2Q³`), the major arcs are **pairwise disjoint**. Their total measure is

    meas(𝔐) = Σ_{q ≤ Q} φ(q) · 2Q/(qN) ≤ (2Q/N) Σ_{q ≤ Q} 1 ≤ 2Q²/N = o(1),

so `meas(𝔪) ≥ 1 − 2Q²/N ≥ 1/2`.

**Step 3 (Lemma: Euler-quotient and Σ μ²/φ bounds).** *For all `m ≥ 3`:
`m/φ(m) = Π_{p|m}(1 − 1/p)^{−1} ≤ C₃ log log 3m`. Consequently
`Σ_{q ≤ Q} μ²(q)/φ(q) ≤ C₄ (log Q)(log log 3Q)`.*

*Proof.* Let `k = ω(m)` (number of distinct prime factors). If `k ≤ 4` the product is at most
`2⁴ = 16` and the claim holds with a suitable `C₃` since `log log 3m ≥ log log 9 > 0.78`. If
`k ≥ 5`: the map `p ↦ (1 − 1/p)^{−1}` is decreasing in `p`, so the product over the primes dividing
`m` is maximized by the `k` smallest primes:

    m/φ(m) ≤ Π_{p ≤ p_k} (1 − 1/p)^{−1} ≤ C_M log p_k     (E3, Mertens).

Since `m ≥ 2^k` we have `k ≤ (log m)/log 2`, and `p_k ≤ 2k log k` (E3) gives
`p_k ≤ C log m · log log m ≤ (log 3m)²` for `m` large, so `log p_k ≤ 2 log log 3m + O(1)`. Absorb
constants into `C₃`. For the second claim: `μ²(q)/φ(q) = μ²(q)/q · (q/φ(q)) ≤ (C₃ log log 3Q)/q`
for `q ≤ Q`, and `Σ_{q ≤ Q} 1/q ≤ 1 + log Q` (E3). ∎
*(Classically `Σ_{q ≤ Q} μ²(q)/φ(q) = log Q + O(1)`; the cruder self-contained bound above
suffices.)*

**Step 4 (pointwise major-arc approximation).** *Claim: uniformly for `q ≤ Q`, `gcd(a, q) = 1`, and
`|β| ≤ 3Q/N`,*

    S(a/q + β) = (μ(q)/φ(q)) · I(β) + O_B(N Δ_N),
    where  I(β) = ∫₀^N e(βx) dx   and   Δ_N = exp(−c_B (log N)^{1/4}).

*(Note `Δ_N = O_K((log N)^{−K})` for every `K`.)*

*Proof.* Put `T(x) = Σ_{p ≤ x} (log p) e(pa/q)`. Splitting primes into residue classes mod `q`
(primes dividing `q` contribute at most `Σ_{p|q} log p ≤ log q ≤ B log log N` in total),

    T(x) = Σ_{b mod q, (b,q)=1} e(ab/q) · θ(x; q, b) + O(log q).

*Siegel–Walfisz with a uniformity check.* Let `x₀ = exp(√(log N))`. For `x₀ ≤ x ≤ N` we have
`(log x)^{2B} ≥ (log N)^B = Q ≥ q`, so (E2) applies with `A = 2B`, and `√(log x) ≥ (log N)^{1/4}`
turns its error into `O_B(x·exp(−c_{2B}(log N)^{1/4})) ≤ N Δ'_N` per residue class. By (E4),
`Σ_{(b,q)=1} e(ab/q) = μ(q)` — proof: writing the coprimality condition with Möbius,
`Σ_{(b,q)=1} e(ab/q) = Σ_{d|q} μ(d) Σ_{c mod q/d} e(ac/(q/d)) = Σ_{d|q} μ(d)(q/d)·𝟙[(q/d) | a]`,
and `gcd(a, q) = 1` forces `q/d = 1`, leaving `μ(q)`. Hence for `x₀ ≤ x ≤ N`, summing over the
`φ(q) ≤ Q` classes,

    E(x) := T(x) − (μ(q)/φ(q))·x   satisfies   |E(x)| ≤ C_B · N Q Δ'_N.

For `2 ≤ x < x₀` trivially `|E(x)| ≤ θ(x) + x ≤ 3x₀ ≤ N Δ'_N` for `N` large (since
`√(log N) + c(log N)^{1/4} ≤ log N`). So `|E(x)| ≤ C_B N Q Δ'_N` uniformly on `[2, N]`.

*Partial summation.* By Riemann–Stieltjes integration by parts,

    S(a/q + β) = ∫_{2⁻}^{N} e(βx) dT(x) = e(βN) T(N) − 2πiβ ∫₂^N T(x) e(βx) dx.

Insert `T = (μ(q)/φ(q))x + E(x)`. The main part is, using
`d/dx [x e(βx)] = e(βx) + 2πiβ·x e(βx)` — i.e. the identity
`e(βN)N − 2πiβ ∫₂^N x e(βx) dx = ∫₂^N e(βx) dx + 2e(2β)`:

    (μ(q)/φ(q)) · ( I(β) + O(1) ).

The error part is bounded by `|E(N)| + 2π|β| ∫₂^N |E(x)| dx ≤ (1 + 2π|β|N) · C_B N Q Δ'_N`, and
`|β| ≤ 3Q/N` gives `(1 + 2π|β|N) ≤ 20Q`, so the total error is `≤ C'_B N Q² Δ'_N ≤ N Δ_N` after
absorbing `Q² = (log N)^{2B}` into the exponential. ∎

For later use, the explicit evaluation of `I`:

    |I(β)| = | (e(βN) − 1) / (2πiβ) | = |sin(πNβ)| / (π|β|) ≤ min( N, 1/(π|β|) ).

**Step 5 (major-arc `L²` mass — proof of (ii)).** On the arc `𝔐(q, a)` write `α = a/q + β`,
`|β| ≤ Q/(qN)`. From Step 4 and `(u + v)² ≤ 2u² + 2v²`:

    ∫_{𝔐(q,a)} |S|² dα ≤ 2 (μ²(q)/φ(q)²) ∫_{|β| ≤ Q/(qN)} |I(β)|² dβ + 2 · (2Q/(qN)) · N²Δ_N².

The `I`-integral is computed exactly against the majorant:

    ∫_{−∞}^{∞} min(N, 1/(π|β|))² dβ = 2 [ ∫₀^{1/(πN)} N² dβ + ∫_{1/(πN)}^{∞} dβ/(π²β²) ]
                                    = 2 [ N/π + N/π ] = 4N/π.

Summing over the `φ(q)` values of `a` and over `q ≤ Q`, using Step 3:

    ∫_𝔐 |S|² dα ≤ (8/π) N Σ_{q ≤ Q} μ²(q)/φ(q) + 4 Q N Δ_N² Σ_{q ≤ Q} φ(q)/q
                 ≤ (8C₄/π) N (log Q)(log log 3Q) + 4 Q² N Δ_N²
                 ≤ C_B · N (log log N)²,

since `log Q = B log log N` and `Q²Δ_N² → 0`. Subtracting from (i):

    ∫_𝔪 |S|² dα = N log N + O(N) − O_B(N (log log N)²) = N log N (1 + O_B((log log N)²/log N)).  ∎(ii)

**Step 6 (singular series — proof of (iii)).** *Positivity of `C₂`:* each factor
`1 − (p−1)^{−2} ∈ (3/4, 1)` for `p ≥ 3`, and using `log(1 − x) ≥ −2x` on `[0, 1/2]`,

    log C₂ = Σ_{p > 2} log(1 − (p−1)^{−2}) ≥ −2 Σ_{p > 2} (p−1)^{−2} > −∞,

so `C₂ > 0` (numerically `C₂ = 0.66016…` `[ESTABLISHED*]`). *Lower bound:* every factor
`(p−1)/(p−2) ≥ 1`, hence `𝔖(n) ≥ 2C₂` for all even `n`. *Upper bound:* for `p ≥ 3`,

    (p−1)/(p−2) ≤ (1 − 1/p)^{−2} = p²/(p−1)²
    ⟺ (p−1)³ ≤ p²(p−2) ⟺ 3p − 1 ≤ p²,   true for p ≥ 3.

Since `n` is even, `n/φ(n) = 2 · Π_{p|n, p>2} (1 − 1/p)^{−1}`, so

    Π_{p|n, p>2} (p−1)/(p−2) ≤ Π_{p|n, p>2} (1 − 1/p)^{−2} = (n/φ(n))²/4,
    𝔖(n) ≤ 2C₂ · (n/φ(n))²/4 = (C₂/2)(n/φ(n))² ≤ (C₂ C₃²/2)(log log 3n)²,

by Step 3. ∎(iii)

**Step 7 (exact optimum of the modulus class — proof of (iv)).**
*Upper direction (`∫_𝔪 |S|²` is a valid modulus bound).* For any measurable `f` with `|f| ≤ |S|`
on `𝔪`, the integral triangle inequality gives

    | ∫_𝔪 f(α)² e(−nα) dα | ≤ ∫_𝔪 |f(α)|² dα ≤ ∫_𝔪 |S(α)|² dα.

*Lower direction (adversarial phase).* Let `u(α) = e(nα/2) = e^{πinα}`; since `n` is even, `n/2 ∈ ℤ`
and `u` is a well-defined unimodular function on the circle. Put `f*(α) = |S(α)|·u(α)`; then
`|f*| = |S|` (so `f*` is in the competitor class) and

    f*(α)² e(−nα) = |S(α)|² e(nα) e(−nα) = |S(α)|²,
    ⟹ ∫_𝔪 f*(α)² e(−nα) dα = ∫_𝔪 |S(α)|² dα.

Hence every modulus bound `M` satisfies `M ≥ ∫_𝔪 |S|²`, and combining with the upper direction,

    M_min(N, n) = ∫_𝔪 |S(α)|² dα.                                                        ∎(iv)

The point of (iv): a modulus argument cannot distinguish the true `S` from the impostor `f*`, and
against `f*` the phase `e(−nα)` cancels **exactly**, converting the signed single-frequency integral
into the full nonnegative `L²` mass. Any cancellation in `E_𝔪(n)` is therefore a property of the
*phase* of `S`, invisible to `|S|`.

**Step 8 (assembly — proof of (v) and the Corollary).** Take `n = N` even and `N` large. By (iv)
and (ii),

    M_min(N, N) = ∫_𝔪 |S|² ≥ N log N (1 − C_B (log log N)²/log N) ≥ (1/2) N log N eventually,

while by (iii), `𝔖(N)·N ≤ (C₂C₃²/2)(log log 3N)²·N`. Dividing — this is the **explicit main-term
versus minor-arc comparison**:

    M_min(N, N) / (𝔖(N)·N) ≥ [ (1 − o(1)) N log N ] / [ (C₂C₃²/2) N (log log 3N)² ]
                            ≥ c_B · (log N)/(log log N)²  →  ∞.

**(v.a)** If some modulus bound were `≤ (1 − ε) N log N`, then by (iv)
`∫_𝔪 |S|² ≤ (1 − ε) N log N`, contradicting (ii) as soon as `C_B (log log N)²/log N < ε`.
**(v.b)** The Missing Estimate target `(2C₂ − ε)·n ≤ 2C₂·N` and the weaker target
`N (log N)^{1−ε}` are both eventually below `(1/2) N log N ≤ M_min(N, N)`; a modulus argument can
never certify a bound below `M_min`. **(v.c)** Pointwise on `𝔪`, `|S(α)|² ≤ (sup_𝔪 |S|)·|S(α)|`
and `|S(α)| ≤ sup_𝔪 |S|`; integrating,

    ∫_𝔪 |S|² ≤ (sup_𝔪 |S|) ∫_𝔪 |S| ≤ (sup_𝔪 |S|)² · meas(𝔪),

so the `sup·L¹` and `sup²·measure` bound shapes are numerically `≥ ∫_𝔪 |S|² = M_min ≥
(1 − o(1)) N log N`, however small `sup_𝔪 |S|` might be. This proves (v).

*Corollary, 1.:* from the last display, `(sup_𝔪 |S|)² ≥ ∫_𝔪 |S|² / meas(𝔪) ≥ ∫_𝔪 |S|²` (as
`meas(𝔪) ≤ 1`), and apply (ii). *Corollary, 2.:* if `|S| ≤ β` on `𝔪` then
`∫_𝔪 β² ≥ ∫_𝔪 |S|² = (1 − o(1)) N log N`; for the extreme case `β ≡ (N log N)^{1/2}` the output is
`N log N · meas(𝔪) ≈ N log N` — still a factor `≍ log N/(log log N)²` above `𝔖(N)N`.
*Corollary, 3.:* choose `β* = (⌊2Q⌋ + 1/2)/N`, so `|sin(πNβ*)| = 1` and `2Q/N ≤ β* ≤ 3Q/N`. The
point `α* = β*` lies in `𝔪`: its distance to `0` is `β* > Q/N` (outside `𝔐(1, 1)`), and for any
`a/q` with `q ≤ Q`, `a ≥ 1` the distance is `≥ 1/Q − 3Q/N ≥ 1/(2Q) > Q/(qN)` (as `N > 2Q³`). Step 4
with `q = 1` (where it reduces to (E1) plus partial summation) gives

    |S(α*)| ≥ |I(β*)| − N Δ_N = 1/(πβ*) − N Δ_N ≥ N/(π(2Q + 1)) − N Δ_N ≥ N/(8Q),

and `N/(8Q) = N(log N)^{−B}/8 ≫ (N log N)^{1/2} · (log N)^K` for every fixed `K`. ∎

**∎ (Theorem and Corollary.)**

---

## What is new vs REPORT.md

`REPORT.md` §5 C1 delivered the Modulus Barrier as **Lemma A** (mass count, *proof sketch*) plus
**Theorem B** (adversarial phase, one-line proof) plus prose. This file upgrades that package as
follows. Nothing conjectural is added anywhere.

1. **Single-theorem form.** One theorem, parts (i)–(v) with one corollary and one complete proof
   (Steps 0–8), replacing the lemma/observation/prose assembly — as the Wave-2 mission required.
2. **Complete proofs with every integral executed.** The Parseval evaluation via Stieltjes partial
   summation (Step 1); the arc disjointness and measure counts (Step 2); the per-arc integral
   computed exactly, `∫ min(N, 1/(π|β|))² dβ = 4N/π` (Step 5); the Ramanujan-sum identity proved
   inline (Step 4). REPORT had sketches for all of these.
3. **A glossed uniformity gap closed.** Siegel–Walfisz is uniform for `q ≤ (log x)^A`, but the
   partial summation needs it for all `2 ≤ x ≤ N` with `q ≤ (log N)^B`; the `x₀ = exp(√(log N))`
   split in Step 4 (trivial bound below `x₀`, exponent-doubling above) fixes this detail, which
   REPORT's Lemma-A sketch passed over silently.
4. **Exact characterization, not just an obstruction.** REPORT's Theorem B showed modulus arguments
   cannot get below `(1 + o(1)) N log N`. Part (iv) upgrades this to an *equality*:
   `M_min(N, n) = ∫_𝔪 |S|²` — the triangle inequality is precisely optimal within the modulus
   class, so the lost logarithm is located at a single, provably lossless-in-its-class step.
5. **Explicit deficit constant and the "(1 − ε)" sharpening.** The comparison is quantified as
   `M_min/(𝔖(n)n) ≥ c_B log N/(log log N)²`, with self-contained proofs of the singular-series
   bounds `2C₂ ≤ 𝔖(n) ≤ (C₂/2)(n/φ(n))² ≪ (log log n)²` (REPORT asserted the range). And (v.a)
   proves modulus arguments cannot even save a constant factor `(1 − ε)` over the triangle
   inequality — locating REPORT's open problem 1 (a `(1 − c)`-saving bound on `|E_𝔪(n)|`) strictly
   outside the modulus class: any such saving is *necessarily* phase-sensitive.
6. **The square-root floor made two-sided.** Corollary parts 1–3 prove both that pointwise bounds
   cannot beat `(N log N)^{1/2}` on `𝔪` (Parseval floor), and that the actual sup is much larger,
   `sup_𝔪 |S| ≥ N/(8Q)` — with an explicit minor-arc point `α* = (⌊2Q⌋ + 1/2)/N` exhibited — so
   "square-root cancellation on `𝔪`" is false, yet even its truth would not close the gap.
7. **Established-inputs ledger.** E1–E4 are the only external inputs to the proof; E5
   (Hardy–Littlewood major-arc asymptotic) is quarantined as context, cited solely to justify
   calling `𝔖(n)n` "the main term." REPORT mixed these roles.

### Computational companion

`code/goldbach_check.py` (pure stdlib, runs in well under a second). Output of the actual run:

    [Part 1] Binary Goldbach verified for all even n in [4, 100000].
    [Part 1] Largest minimal Goldbach prime: p = 293 at n = 63274.
    [Part 2] N = n = 100000   (log N = 11.5129)
    [Part 2] Parseval mass  int|S|^2 = sum log^2 p = 1,048,436
    [Part 2]   vs N log N = 1,151,293   (ratio 0.9107; -> 1 as N -> oo)
    [Part 2] Singular series Sing(n) = 1.7604;  main term Sing(n)*n = 176,043
    [Part 2] True weighted count R(n) = 176,154   (R / main = 1.0006)
    [Part 2] BARRIER RATIO  int|S|^2 / (Sing(n)*n) = 5.96
    [Part 2]   compare log N / Sing(n) = 6.54: the L^2 mass any
    [Part 2]   modulus argument must pay overshoots the main term by ~ log N.

Note the two comparisons the theorem predicts: the true count `R(N)` matches the Hardy–Littlewood
main term to 0.06% already at `N = 10⁵`, while the Parseval mass any modulus argument must pay
overshoots that main term by a factor ≈ 6 ≈ `log N/𝔖(N)` — the logarithm of the theorem, visible
at small scale. (The minimal-prime record `p = 293` at `n = 63274` agrees with published tables.)
No claim is made beyond `10⁵`; the published verification record is `4 × 10^{18}` (Oliveira e
Silva–Herzog–Pardi, 2014).

---

## Why binary Goldbach remains open

**The theorem restricts proofs, not the truth.** Conjecturally `E_𝔪(n) = o(n)` — the minor-arc
integral really is tiny, by massive cancellation of the phases of `S(α)² e(−nα)`. The theorem says
that this cancellation, however real, is *invisible to `|S|`*: every bound derivable from the
modulus alone is `≥ (1 − o(1)) N log N`, one full logarithm above the main term `𝔖(n)n ≍ n`. The
adversarial phase `f* = |S| e(nα/2)` witnesses a member of the modulus class for which no
cancellation occurs at all.

**Why ternary fell and binary did not — the variable count.** Ternary Goldbach has a third factor
of `S` to spend:

    | ∫_𝔪 S(α)³ e(−nα) dα | ≤ (sup_𝔪 |S|) · ∫₀¹ |S|² ≪_A N (log N)^{−A} · N log N = N² (log N)^{1−A},

which loses to the ternary main term `≍ n²` — a pure modulus argument suffices, and (with explicit
constants) it is how the ternary theorem was proved. Binary has exponent 2, which is exactly the
Parseval exponent: the two available factors of `S` are consumed by `L²`, nothing remains to carry
the sup-bound's saving, and by part (iv) the modulus class bottoms out at `∫_𝔪 |S|²` exactly.

**The known escapes from the modulus class, and their own walls.**

- *Averaging over `n`* (Bessel/large sieve: `Σ_n |E_𝔪(n)|² = ∫_𝔪 |S|⁴` uses phases through
  orthogonality) yields the almost-all and exceptional-set theorems, `E(x) ≪ x^{1−δ}` — but the
  `ℓ² → ℓ∞` gap means averages never reach one stubborn `n`.
- *Sieves* reach Chen's `n = p + P₂`, and are stopped one step short by the parity problem.
- *Extra variables* (three primes; two primes plus `K` powers of 2) succeed precisely by restoring
  the third factor that binary forbids.
- *GRH* enlarges the major arcs to modulus `≈ N^{1/2}`, capturing at most half the `L²` mass
  (`REPORT.md` C2); the barrier persists at `(1/2 − o(1)) N log N`, which is why binary Goldbach is
  not known even under GRH.

**What a proof would need.** By (iv)–(v), any circle-method proof must extract a uniform-in-`n`
relative saving of order `log N` from the specific phase `e(−nα)` against the phase distribution of
`S(α)²` on `𝔪` — a single-frequency, signed cancellation among prime phases. No mechanism producing
such cancellation exists in the literature, and zeros of `L`-functions demonstrably do not encode it
(they control major-arc quality and averages, not single-frequency minor-arc phases). That — and
only that — is why the problem remains open: the toolbox that closed ternary Goldbach is, by this
theorem, structurally incapable of closing binary, and no replacement tool is known.

---

## Honesty label

- **Overall label: `[FOLKLORE, formalized]` + `[NEW-SYNTHESIS]`.** The constituent facts (Parseval
  mass `N log N`; major arcs carry `o(·)` of it; `𝔖(n) ≍ 1` up to `log log` factors; the
  adversarial-phase observation) are known to experts. The contribution of this file is the
  single-theorem formalization with a complete self-contained proof, the exact-minimum
  characterization `M_min = ∫_𝔪 |S|²` (part (iv)), and the explicit deficit
  `c_B log N/(log log N)²` (part (v)). Novelty of the *formulation* is uncertain and requires a
  literature check (Vaughan's tract and Goldbach surveys first); correctness is believed solid —
  the proof is elementary given E1–E4 — but has not been externally refereed.
- **Explicitly NOT claimed:** any proof (or conditional proof) of binary Goldbach; any new proof of
  ternary Goldbach; any statement about the true size of `E_𝔪(n)` (the theorem bounds what
  *modulus arguments can certify*, not the integral itself); any new exponential-sum estimate; any
  improvement of any known exponent; any verification bound beyond the published `4 × 10^{18}`.
- **Established inputs:** E1 (PNT + Chebyshev), E2 (Siegel–Walfisz), E3 (Mertens + `p_k ≤ 2k log k`
  + harmonic sum), E4 (Ramanujan sum) — all `[ESTABLISHED]`, used in the proof. E5 (Hardy–Littlewood
  major-arc asymptotic) — `[ESTABLISHED]`, cited only to justify the phrase "main term," never used
  in any proof step. Numeric value `C₂ = 0.66016…` — `[ESTABLISHED*]` (positivity of `C₂` is proved
  in Step 6; only the decimal value is from memory).
- **GRH remark (Remark 2):** rests on `REPORT.md` §5 C2, which is labeled `[NEW-SYNTHESIS — needs
  referee]` there; it is quoted, not reproved, and nothing in the theorem depends on it.
- **Computational companion:** `code/goldbach_check.py`, output reproduced verbatim above from an
  actual run; verification only, at `10⁵`, with no extrapolation.
- **Process:** written by Legion 09 in Wave 2, serially, no subagents; no files outside
  `/workspace/research/conjectures/09-goldbach/` were touched.

*End of Wave-2 breakthrough file — LEGION 09.*
