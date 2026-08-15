# 06 — An Explicit Mass Gap for Two ℤ₂ Lattice Models: Exponential Clustering for the 2D Ising Model at High Temperature, and Exact Ultralocality plus Area Law for 2D ℤ₂ Gauge Theory

**Status: original write-up; every theorem below is proved in full, self-contained, in this file, with all constants explicit.**

**Honesty line.** The theorems here are *true and completely proved*, but they are classical in
substance: the quantitative clustering theorem (Theorem 2) is a Dobrushin-uniqueness-regime
result, proved by a coupling argument in the spirit of Dobrushin (1968) and path coupling
(Bubley–Dyer 1997); the self-avoiding-walk bound (Theorem 3) goes back to Fisher (1967); the
exact solution of two-dimensional ℤ₂ gauge theory (Theorem 4) has been folklore since
Wegner (1971) and Balian–Drouffe–Itzykson (1975). What is original here is the packaging: one
short self-contained document in which every estimate is carried out with explicit constants
(m(β) = ln(1/(4 tanh β)) on a named open interval, prefactor 2|A||B|/(1 − 4 tanh β), and a
corollary in the literal form ⟨F τ_x G⟩ − ⟨F⟩⟨G⟩ ≤ ‖F‖‖G‖e^{−m̃(β)|x|} with
m̃(β) = ln[(1 − 4 tanh β)/(8 tanh β)]), with no step outsourced to the literature. No claim of
any kind is made about four-dimensional Yang–Mills theory or the Clay problem; see §9.3. The
proofs were composed and checked line by line by the author of this note (an AI system); any
error is the author's own.

**Model choice, stated explicitly.** The quantitative clustering theorem is proved for the
**two-dimensional Ising model** on ℤ² (spins on sites), in the high-temperature interval
β ∈ (0, β₀), β₀ = ½ ln(5/3). Because the title promises a ℤ₂ *gauge* statement as well, §8
settles **two-dimensional ℤ₂ lattice gauge theory** exactly, for *all* β ∈ [0, ∞): its
gauge-invariant correlations are ultralocal (truncated correlations vanish identically at
positive separation, so the clustering bound holds with *every* rate m > 0), and its Wilson
loops obey an exact area law with string tension ln coth β > 0. The duality bookkeeping is done
correctly in §8.5: 2D ℤ₂ gauge theory is dual to a *non-interacting* ℤ₂ spin system in an
external field (not to the 2D Ising model, which is Kramers–Wannier self-dual; the
gauge–Ising duality pairs the 3D models).

---

## 1. Main results

Throughout, β ≥ 0 is the inverse coupling, t = tanh β, and

  λ = λ(β) := 4 tanh β,  m(β) := ln(1/λ(β)) = ln(1/(4 tanh β)),
  β₀ := arctanh(1/4) = ½ ln(5/3) ≈ 0.25541.

For β ∈ (0, β₀) we have 0 < λ < 1 and m(β) > 0. For comparison, the critical point of the 2D
Ising model is β_c = ½ ln(1 + √2) ≈ 0.44069, so (0, β₀) is a proper subinterval of the
high-temperature phase; see §9.2.

**Theorem 1 (infinite-volume state).** Let ⟨·⟩_Λ denote the free-boundary Ising expectation in
a finite Λ ⊂ ℤ² (definitions in §2). For every β ∈ [0, β₀) and every local function F, the limit

  ⟨F⟩ := lim_{N→∞} ⟨F⟩_{Λ_N},  Λ_N = ([−N, N] ∩ ℤ)²,

exists, is independent of the exhausting sequence, and is translation invariant:
⟨τ_x F⟩ = ⟨F⟩ for all x ∈ ℤ².

**Theorem 2 (exponential clustering with explicit rate — the mass gap).** Let β ∈ [0, β₀). Let
F, G be bounded local functions with supports A = supp F, B = supp G (finite subsets of ℤ²).
Then for every x ∈ ℤ², in the infinite-volume state of Theorem 1,

  |⟨F · τ_x G⟩ − ⟨F⟩⟨G⟩| ≤ (2 |A| |B| / (1 − λ)) · ‖F‖_∞ ‖G‖_∞ · e^{−m(β) · d₁(A, B + x)},

and the same bound holds for the covariance ⟨F · τ_x G⟩_Λ − ⟨F⟩_Λ ⟨τ_x G⟩_Λ in every finite
volume Λ ⊇ A ∪ (B + x),

where d₁ is ℓ¹ (graph) distance and m(β) = ln(1/(4 tanh β)) > 0.

**Corollary 2.1 (the requested form, verbatim).** Let β ∈ (0, β₁), where
β₁ := arctanh(1/12) = ½ ln(13/11) ≈ 0.08353, and let F, G each depend on the single spin at the
origin. Then for every x ≠ 0,

  |⟨F · τ_x G⟩ − ⟨F⟩⟨G⟩| ≤ ‖F‖_∞ ‖G‖_∞ · e^{−m̃(β) |x|₁},
  m̃(β) := ln[(1 − 4 tanh β)/(8 tanh β)] > 0.

Since |x|₁ ≥ |x|₂, the same bound holds with the Euclidean distance |x| in the exponent.

**Corollary 2.2 (verbatim form for general local observables).** Let β ∈ (0, β₀), let F, G have
supports inside the box Λ_L, and fix any m′ ∈ (0, m(β)). Then

  |⟨F · τ_x G⟩ − ⟨F⟩⟨G⟩| ≤ ‖F‖_∞ ‖G‖_∞ · e^{−m′ |x|₁}
  for all |x|₁ ≥ R₀ := [ln(2(2L+1)⁴/(1−λ)) + 4 m(β) L] / (m(β) − m′).

**Theorem 3 (two-point function: sharper rate on a larger interval).** For all β with
tanh β < 1/3, i.e. β ∈ [0, ½ ln 2), for every finite Λ ∋ 0, x and hence for every
infinite-volume limit point,

  0 ≤ ⟨σ₀ σ_x⟩ ≤ (4/3) · (3 tanh β)^{|x|₁} / (1 − 3 tanh β).

Since ⟨σ₀⟩ = 0 at zero field, the left side is exactly the truncated two-point function; the
decay rate is ln(1/(3 tanh β)), which beats Theorem 2's rate and holds up to β = ½ ln 2 ≈ 0.34657.

**Theorem 4 (2D ℤ₂ gauge theory: ultralocality and area law, all β).** Consider ℤ₂ lattice
gauge theory on ℤ² with Wilson action at inverse coupling β ∈ [0, ∞) (definitions in §8). Then:

  (i) (Exact solution.) In any finite simply connected box, after a change of variables the
      Gibbs measure is a *product* measure: the plaquette variables q_p are i.i.d. with
      E[q_p] = tanh β.
  (ii) (Ultralocal clustering.) If F and G are bounded local gauge-invariant observables whose
      plaquette supports P_F and P_G + x are disjoint, then ⟨F · τ_x G⟩ − ⟨F⟩⟨G⟩ = 0 exactly,
      in every volume and in the (trivially existing) infinite-volume limit. In particular the
      clustering bound |⟨F τ_x G⟩ − ⟨F⟩⟨G⟩| ≤ ‖F‖‖G‖e^{−m|x|} holds for **every** m > 0 once
      |x| exceeds the sum of the support diameters: the "mass gap" of the 2D gauge theory is +∞.
  (iii) (Area law.) For every rectangular loop C = ∂R enclosing Area(R) plaquettes,
      ⟨W_C⟩ = (tanh β)^{Area(R)} exactly; the string tension is σ(β) = ln coth β ∈ (0, ∞] for
      every β ∈ [0, ∞): confinement at all couplings.

Sample values of the rates: m(0.1) ≈ 0.9195, m(0.2) ≈ 0.2363, m(0.25) ≈ 0.0205;
m̃(0.05) ≈ 0.6942; Theorem 3's rate at β = 0.3 is ln(1/(3 tanh 0.3)) ≈ 0.1347.

---

## 2. Notation and the finite-volume model

Sites i ∈ ℤ²; i ∼ j means |i − j|₁ = 1 (each site has 4 neighbours). For finite Λ ⊂ ℤ², a
configuration is σ ∈ {−1, +1}^Λ. The free-boundary Ising measure at inverse temperature β ≥ 0
and zero field is

  μ_Λ(σ) := (1/Z_Λ) exp( β Σ_{⟨ij⟩ ⊆ Λ} σ_i σ_j ),

the sum over unordered nearest-neighbour pairs with both endpoints in Λ. All configurations
have positive weight, so all conditional probabilities below are well defined.

A function F is **local** with support A = supp F if it depends only on (σ_i)_{i∈A}, A finite.
‖F‖_∞ is the sup norm. For a site i,

  osc_i(F) := max { |F(σ) − F(σ′)| : σ, σ′ agree off i },  osc(F) := max F − min F.

Note osc_i(F) ≤ 2‖F‖_∞ and osc(F) ≤ 2‖F‖_∞. Translations: (θ_x σ)_i := σ_{i+x} and
(τ_x G)(σ) := G(θ_x σ), so supp(τ_x G) = supp(G) + x and ‖τ_x G‖_∞ = ‖G‖_∞,
osc_i(τ_x G) = osc_{i−x}(G).

**Fact 2.1 (oscillation telescoping).** If σ, σ′ differ exactly on the finite set D, then
|F(σ) − F(σ′)| ≤ Σ_{i∈D} osc_i(F).

*Proof.* Enumerate D = {j₁, …, j_r}; let ζ^k be σ with the first k sites of D flipped, so
ζ⁰ = σ, ζ^r = σ′. Consecutive ζ's differ at one site; sum the one-site oscillations. ∎

---

## 3. The coupling lemma

This is the engine of Theorems 1 and 2. It is a finite, elementary, fully self-contained
version of Dobrushin's comparison theorem, proved by running two coupled heat-bath chains.

**Setting.** V is a finite set; μ and μ′ are strictly positive probability measures on
Ω = {±1}^V. For i ∈ V write

  p_i(σ) := μ(σ_i = +1 | σ_j for all j ≠ i),  p′_i(σ) := μ′(σ_i = +1 | σ_j for all j ≠ i);

both depend only on (σ_j)_{j≠i}. Assume we are given numbers c_{ij} ≥ 0 (i, j ∈ V, c_{ii} = 0)
and b_i ≥ 0 such that

  (H1) |p_i(σ) − p_i(σ′)| ≤ c_{ij} whenever σ, σ′ agree off j;
  (H2) |p_i(σ) − p′_i(σ)| ≤ b_i for all σ;
  (H3) α := max_i Σ_j c_{ij} < 1.

Let C = (c_{ij}) as a nonnegative matrix and s := Σ_{n≥0} Cⁿ b (the series converges: row sums
of Cⁿ are ≤ αⁿ).

**Lemma 3.1 (heat bath preserves its measure).** Fix i and let K_i be the Markov kernel on Ω
that resamples σ_i from μ(σ_i = · | σ_j, j ≠ i) and leaves the rest unchanged. Then μK_i = μ.

*Proof.* For any σ′, (μK_i)(σ′) = Σ_{σ: σ = σ′ off i} μ(σ) · μ(σ_i = σ′_i | σ_j = σ′_j, j ≠ i)
= μ(σ_j = σ′_j, j ≠ i) · μ(σ_i = σ′_i | σ_j = σ′_j, j ≠ i) = μ(σ′). ∎

**Lemma 3.2 (coupling estimate).** Under (H1)–(H3), for every function f on Ω,

  |μ(f) − μ′(f)| ≤ Σ_{i∈V} osc_i(f) · s_i,  s = Σ_{n≥0} Cⁿ b.

*Proof.* Let N = |V|. Build a coupled Markov chain (X_t, X′_t)_{t≥0} on Ω × Ω:

  • X₀ ~ μ and X′₀ ~ μ′, coupled arbitrarily (say independently).
  • At each step, draw I uniform on V and U uniform on [0,1], independent of everything;
    set X(I) ← +1 if U ≤ p_I(X), else −1; and X′(I) ← +1 if U ≤ p′_I(X′), else −1;
    leave all other coordinates unchanged.

Each marginal chain is the random-site heat-bath chain for its own measure (the update of X
never looks at X′ and vice versa), so by Lemma 3.1, X_t ~ μ and X′_t ~ μ′ for **every** t ≥ 0.

Let d_t(i) := P(X_t(i) ≠ X′_t(i)). Condition on (X_t, X′_t) and on I = i: after the update the
two chains disagree at i iff U falls between p_i(X_t) and p′_i(X′_t), which has probability

  |p_i(X_t) − p′_i(X′_t)| ≤ |p_i(X_t) − p_i(X′_t)| + |p_i(X′_t) − p′_i(X′_t)|
                          ≤ Σ_j c_{ij} 1[X_t(j) ≠ X′_t(j)] + b_i,

where the first term used (H1) with Fact-2.1-style telescoping (flip the disagreement sites of
(X_t, X′_t) one at a time; flipping site i itself does not change p_i since p_i ignores σ_i, and
c_{ii} = 0), and the second used (H2). Since P(I = i) = 1/N independently of the past,

  d_{t+1}(i) ≤ (1 − 1/N) d_t(i) + (1/N) ( b_i + Σ_j c_{ij} d_t(j) ).   (3.1)

Let M := (1 − 1/N) Id + (1/N) C, a nonnegative matrix, and recall s = Σ_{n≥0} Cⁿ b, so that
C s + b = s and hence M s + (1/N) b = (1 − 1/N)s + (1/N)(Cs + b) = s. Subtracting this identity
from (3.1): d_{t+1} − s ≤ M (d_t − s) componentwise. As M is entrywise nonnegative, induction
gives d_t − s ≤ M^t (d₀ − s) ≤ M^t 𝟙 (using d₀ ≤ 𝟙 and s ≥ 0). The row sums of M are at most
ρ := 1 − (1 − α)/N < 1, so (M^t 𝟙)_i ≤ ρ^t. Hence

  d_t(i) ≤ s_i + ρ^t for all t.

Finally, since X_t ~ μ and X′_t ~ μ′ exactly,

  |μ(f) − μ′(f)| = |E[f(X_t)] − E[f(X′_t)]| ≤ E|f(X_t) − f(X′_t)|
                 ≤ Σ_i osc_i(f) d_t(i) ≤ Σ_i osc_i(f)(s_i + ρ^t)

by Fact 2.1. Let t → ∞. ∎

---

## 4. Dobrushin coefficients of the 2D Ising model

**Lemma 4.1 (calculus).** For all real a, b: |tanh a − tanh b| ≤ 2 tanh(|a − b|/2) ≤ |a − b|.

*Proof.* tanh a − tanh b = sinh(a − b)/(cosh a cosh b) and
cosh a cosh b = ½[cosh(a + b) + cosh(a − b)] ≥ ½[1 + cosh(a − b)] = cosh²((a − b)/2). With
δ = |a − b| and sinh δ = 2 sinh(δ/2) cosh(δ/2):
|tanh a − tanh b| ≤ 2 sinh(δ/2) cosh(δ/2) / cosh²(δ/2) = 2 tanh(δ/2) ≤ δ. (Equality in the
first bound at a = −b, so it is sharp.) ∎

Consider any measure of the following type: V ⊂ ℤ² finite, and σ ∈ {±1}^V weighted by
exp(β Σ σ_i σ_j), the sum over nearest-neighbour pairs with at least one endpoint in V, where
spins outside V (if any appear) are **frozen** at prescribed values. This covers: μ_Λ (nothing
frozen), μ_Λ conditioned on the spins of a subset B (V = Λ∖B, σ_B frozen), and the conditional
distribution of μ_{Λ′} on Λ given Λ′∖Λ. For i ∈ V, the single-site conditional is

  p_i(σ) = e^{β S_i} / (e^{β S_i} + e^{−β S_i}) = (1 + tanh(β S_i))/2,
  S_i := Σ_{j ∼ i, j present} σ_j  (frozen spins included; absent neighbours contribute 0).

**Lemma 4.2 (coefficients).** For any such measure:
  (i) if j ∼ i (j in V or frozen), flipping σ_j changes S_i by exactly ±2, so
      |Δp_i| = ½|tanh(β S) − tanh(β(S ∓ 2))| ≤ tanh β, by Lemma 4.1 with δ = 2β;
  (ii) if j ≁ i or j = i, p_i does not change.
Hence (H1) holds with c_{ij} = tanh β · 1[i ∼ j], and α = max_i Σ_j c_{ij} ≤ 4 tanh β = λ. ∎

**Lemma 4.3 (walk bound / Neumann series).** Let C be any nonnegative V × V matrix with
C_{ij} ≤ tanh β · 1[i ∼ j] and λ = 4 tanh β < 1. Then for all i, j ∈ V:

  Σ_{n≥0} (Cⁿ)_{ij} ≤ λ^{|i−j|₁} / (1 − λ).

*Proof.* (Cⁿ)_{ij} is a sum over length-n nearest-neighbour paths i = k₀ ∼ k₁ ∼ ⋯ ∼ k_n = j
inside V of products of entries, each product ≤ (tanh β)ⁿ. The number of such paths is at most
the number of length-n walks in ℤ², i.e. ≤ 4ⁿ; and a walk from i to j needs n ≥ |i − j|₁ steps
(each step changes the ℓ¹ position by 1). So (Cⁿ)_{ij} ≤ (4 tanh β)ⁿ 1[n ≥ |i−j|₁]; sum the
geometric series. ∎

---

## 5. Proof of Theorem 1 (thermodynamic limit, translation invariance)

Fix β ∈ [0, β₀), so λ < 1. Let F be local with A = supp F. Let Λ ⊆ Λ′ be finite with A ⊆ Λ.
Write ∂Λ for the set of i ∈ Λ having a neighbour outside Λ.

**Step 1 (one comparison, uniform in Λ′).** By the Markov property of nearest-neighbour Gibbs
weights, the conditional distribution of σ_Λ under μ_{Λ′}, given σ_{Λ′∖Λ}, is the measure on
{±1}^Λ of §4-type with the spins of Λ′∖Λ frozen. Compare it with μ_Λ (free boundary,
nothing frozen) via Lemma 3.2 on V = Λ: both have (H1) with c_{ij} = tanh β 1[i∼j] (Lemma 4.2);
their single-site conditionals coincide except at sites i ∈ ∂Λ, and any difference of two
probabilities is ≤ 1, so (H2) holds with b_i = 1[i ∈ ∂Λ]. By Lemmas 3.2 and 4.3, for every
frozen configuration,

  | ⟨F⟩_Λ − E_{μ_{Λ′}}[F | σ_{Λ′∖Λ}] | ≤ Σ_{i∈A} osc_i(F) Σ_{j∈∂Λ} λ^{|i−j|₁}/(1 − λ) =: δ(F, Λ).

Averaging the conditional expectation over μ_{Λ′} gives, for **every** finite Λ′ ⊇ Λ,

  | ⟨F⟩_Λ − ⟨F⟩_{Λ′} | ≤ δ(F, Λ) ≤ 2‖F‖_∞ |A| · |∂Λ| · λ^{d₁(A, ∂Λ)} / (1 − λ).   (5.1)

**Step 2 (Cauchy along boxes).** Take A ⊆ Λ_L and Λ = Λ_N with N > L: |∂Λ_N| = 8N and
d₁(A, ∂Λ_N) ≥ N − L, so δ(F, Λ_N) ≤ 2‖F‖_∞|A| · 8N λ^{N−L}/(1 − λ) → 0 as N → ∞ (λ < 1). By
(5.1), (⟨F⟩_{Λ_N})_N is Cauchy; call the limit ⟨F⟩. By (5.1) again, any other exhausting
sequence of finite sets containing A eventually stays within δ → 0 of any huge box, so the
limit is the same.

**Step 3 (translation invariance).** Relabelling sites (the interaction and the free boundary
condition are translation covariant) gives ⟨τ_x F⟩_{Λ_N} = ⟨F⟩_{Λ_N − x}. The sets Λ_N − x
exhaust ℤ² and contain A for large N, so by Step 2, lim_N ⟨F⟩_{Λ_N − x} = ⟨F⟩. Hence
⟨τ_x F⟩ = ⟨F⟩. ∎

*(Remark: the limiting functional is linear, positive, normalized, and consistent on local
functions, hence extends to a unique probability measure on {±1}^{ℤ²} by density of local
functions in C({±1}^{ℤ²}) and Riesz–Markov; we only use the limiting expectations.)*

---

## 6. Proof of Theorem 2 and its corollaries

Fix β ∈ [0, β₀), a finite Λ, and local F, G with disjoint supports A, B ⊆ Λ. (For Theorem 2 as
stated, replace G by τ_x G, i.e. B by B + x; nothing changes. If d₁(A, B) = 0 the claimed bound
is ≥ 2‖F‖_∞‖G‖_∞ ≥ |Cov|, trivially true; so assume d₁(A, B) ≥ 1, which forces A ∩ B = ∅.)

**Step 1 (conditioning on the support of G).** Let c := (max G + min G)/2, so
‖G − c‖_∞ = osc(G)/2 ≤ ‖G‖_∞. Since G − c is a function of σ_B,

  Cov_Λ(F, G) = E[ (G − c)(F − E F) ] = E[ (G − c) ( E[F | σ_B] − E F ) ]

by the tower property. Since E F is a convex combination of the values E[F | σ_B = τ′],

  |Cov_Λ(F, G)| ≤ (osc(G)/2) · max_{τ, τ′ ∈ {±1}^B} | E[F | σ_B = τ] − E[F | σ_B = τ′] |.  (6.1)

**Step 2 (telescoping over single flips).** Order B = {j₁, …, j_k} and interpolate from τ to τ′
by changing one coordinate at a time. Then the max in (6.1) is at most

  Σ_{j∈B} max { | E[F | σ_B = η] − E[F | σ_B = η^{(j)}] | : η ∈ {±1}^B },   (6.2)

where η^{(j)} is η flipped at j.

**Step 3 (coupling estimate for a single flip).** Fix j ∈ B and η. Both conditional measures
live on V := Λ∖B and are of §4-type with σ_B frozen (at η, resp. η^{(j)}). By Lemma 4.2 they
satisfy (H1) with c_{ii′} = tanh β 1[i ∼ i′], α ≤ λ < 1; and their single-site conditionals can
differ only at sites i ∼ j, where the flip of the frozen spin η_j shifts S_i by ±2, so by
Lemma 4.1, (H2) holds with b_i = tanh β · 1[i ∼ j]. Lemma 3.2 plus Lemma 4.3 give

  | E[F | η] − E[F | η^{(j)}] | ≤ Σ_{i∈A} osc_i(F) Σ_{i′∼j} (Σ_n Cⁿ)_{i i′} tanh β
    ≤ Σ_{i∈A} osc_i(F) · 4 tanh β · λ^{|i−j|₁ − 1}/(1 − λ)
    = Σ_{i∈A} osc_i(F) · λ^{|i−j|₁}/(1 − λ),

using |i − i′|₁ ≥ |i − j|₁ − 1 for i′ ∼ j, and |i − j|₁ ≥ 1.

**Step 4 (assembly).** Combining (6.1), (6.2), Step 3, osc_i(F) ≤ 2‖F‖_∞, osc(G)/2 ≤ ‖G‖_∞,
and λ^{|i−j|₁} ≤ λ^{d₁(A,B)}:

  |Cov_Λ(F, G)| ≤ (osc(G)/2) Σ_{j∈B} Σ_{i∈A} osc_i(F) λ^{|i−j|₁}/(1 − λ)
               ≤ (2 |A| |B| / (1 − λ)) ‖F‖_∞ ‖G‖_∞ λ^{d₁(A,B)}.

This holds for **every** finite Λ ⊇ A ∪ B, with a Λ-independent right-hand side. Writing
λ^{d} = e^{−m(β) d} and letting Λ ↑ ℤ² (Theorem 1: each of ⟨F τ_x G⟩_Λ, ⟨F⟩_Λ, ⟨τ_x G⟩_Λ
converges, and ⟨τ_x G⟩ = ⟨G⟩ by translation invariance) proves Theorem 2. ∎

**Proof of Corollary 2.1.** Here |A| = |B| = 1 and d₁({0}, {x}) = |x|₁ ≥ 1. Theorem 2 gives the
bound K λ^{|x|₁} ‖F‖‖G‖ with K = 2/(1 − λ) ≥ 1. For any K ≥ 1 and n ≥ 1, K λⁿ ≤ (Kλ)ⁿ. So the
bound is ≤ (2λ/(1 − λ))^{|x|₁} ‖F‖‖G‖ = e^{−m̃(β)|x|₁} ‖F‖‖G‖ with
m̃(β) = ln((1 − λ)/(2λ)) = ln[(1 − 4 tanh β)/(8 tanh β)], which is > 0 iff 12 tanh β < 1, i.e.
iff β < arctanh(1/12) = ½ ln(13/11). ∎

**Proof of Corollary 2.2.** For A, B ⊆ Λ_L: |A|, |B| ≤ (2L+1)² and, for i ∈ A, j ∈ B,
|i − (j + x)|₁ ≥ |x|₁ − |i|₁ − |j|₁ ≥ |x|₁ − 4L. So Theorem 2 gives
|Cov| ≤ C_L ‖F‖‖G‖ e^{−m(|x|₁ − 4L)} with C_L := 2(2L+1)⁴/(1 − λ). For m′ < m, the right side
is ≤ ‖F‖‖G‖e^{−m′|x|₁} as soon as (m − m′)|x|₁ ≥ ln C_L + 4mL, i.e. |x|₁ ≥ R₀. ∎

---

## 7. Proof of Theorem 3 (self-avoiding-walk bound for the two-point function)

**Lemma 7.1 (high-temperature representation).** Let Λ be finite with edge set E and let
A ⊆ Λ with |A| even (for odd |A|, ⟨σ_A⟩_Λ = 0 by the σ → −σ symmetry). With t = tanh β and
∂η := {v : deg_η(v) is odd} for an edge subset η ⊆ E,

  ⟨σ_A⟩_Λ = Σ_{η ⊆ E, ∂η = A} t^{|η|} / Σ_{η ⊆ E, ∂η = ∅} t^{|η|},  σ_A := Π_{v∈A} σ_v.

*Proof.* e^{βσ_uσ_v} = cosh β · (1 + t σ_u σ_v) since (σ_uσ_v)² = 1. Expand the product over
edges: Σ_σ σ_A Π_e e^{βσσ′} = (cosh β)^{|E|} Σ_{η⊆E} t^{|η|} Σ_σ Π_v σ_v^{deg_η(v) + 1_A(v)}.
The spin sum is 2^{|Λ|} if every exponent is even — i.e. iff ∂η = A — and 0 otherwise. Divide
by the same formula with A = ∅. All terms are ≥ 0 (β ≥ 0), so in particular ⟨σ₀σ_x⟩_Λ ≥ 0. ∎

**Proof of Theorem 3.** Take A = {0, x}, x ≠ 0. Let η satisfy ∂η = {0, x}. In the connected
component of η containing 0, the number of odd-degree vertices is even, and the only candidates
in all of η are 0 and x; hence x lies in that component, and η contains a self-avoiding path
from 0 to x. Fix any deterministic rule selecting one such path ω(η) ⊆ η (e.g. the
lexicographically least). Removing ω(η) lowers deg by 2 at interior path vertices and by 1 at
0 and x, so ξ := η ∖ ω(η) satisfies ∂ξ = ∅. The map η ↦ (ω(η), ξ) is injective (η = ω ⊔ ξ is
recovered from the pair), and lands in { (ω, ξ) : ω a SAW from 0 to x, ∂ξ = ∅ }. Since all
weights are nonnegative, dropping the disjointness constraint only increases the sum:

  Σ_{∂η={0,x}} t^{|η|} ≤ ( Σ_{ω: SAW 0→x} t^{|ω|} ) · ( Σ_{∂ξ=∅} t^{|ξ|} ).

Divide by Σ_{∂ξ=∅} t^{|ξ|} and use Lemma 7.1:

  ⟨σ₀σ_x⟩_Λ ≤ Σ_{ω: SAW 0→x in Λ} t^{|ω|} ≤ Σ_{ω: SAW 0→x in ℤ²} t^{|ω|}.

A SAW from 0 to x has length n ≥ |x|₁, and the number of SAWs of length n from 0 in ℤ² is at
most 4 · 3^{n−1} (4 choices for the first step, then never reverse). Hence for 3t < 1:

  ⟨σ₀σ_x⟩_Λ ≤ Σ_{n ≥ |x|₁} 4·3^{n−1} tⁿ = (4/3) (3t)^{|x|₁} / (1 − 3t).

The bound is uniform in Λ, so it passes to every infinite-volume limit point (and in particular
to the state of Theorem 1 when β < β₀). ∎

---

## 8. 2D ℤ₂ gauge theory: exact solution, ultralocal clustering, area law

**8.1 The model.** Work on the box B_N = ([0, N] ∩ ℤ)², vertex set V (|V| = (N+1)²), edge
("bond") set E (|E| = 2N(N+1)), plaquette set P — the unit squares p(x, y), 0 ≤ x, y ≤ N−1 —
(|P| = N²). A gauge configuration assigns σ_e ∈ {±1} to each bond. For a plaquette p, the
plaquette variable is q_p(σ) := Π_{e ∈ ∂p} σ_e. The Wilson-action Gibbs measure at β ∈ [0, ∞) is

  ν_N(σ) := (1/Z) exp( β Σ_{p∈P} q_p(σ) ).

A gauge transformation is ε : V → {±1} acting by (σ^ε)_{⟨uv⟩} := ε_u σ_{⟨uv⟩} ε_v. Every q_p is
gauge invariant (each corner's ε appears squared), hence ν_N is gauge invariant. For a loop C
(closed circuit of bonds), the Wilson loop is W_C(σ) := Π_{e∈C} σ_e, gauge invariant.

**8.2 The comb gauge and the product structure.** Let T ⊂ E consist of **all vertical bonds**
together with the **horizontal bonds of the bottom row** y = 0. Then |T| = N(N+1) + N =
(N+1)² − 1 = |V| − 1, and T is connected (descend vertically to the bottom row, then move
horizontally), hence T is a spanning tree. Note |E| − |T| = N² = |P|. Fix the root r = (0, 0).

For a configuration σ define

  g_v(σ) := Π { σ_e : e on the tree path from r to v }  (g_r = 1),  q_p(σ) as above,

and Ψ(σ) := ( (g_v)_{v ≠ r}, (q_p)_{p ∈ P} ) ∈ {±1}^{V∖{r}} × {±1}^{P}.

**Lemma 8.1.** Ψ is a bijection, and it maps ν_N to the product measure
Unif({±1}^{V∖{r}}) ⊗ Π_{p∈P} ν_β, where ν_β(±1) = e^{±β}/(2 cosh β). In particular, under ν_N
the plaquette variables (q_p)_{p∈P} are i.i.d. with E[q_p] = tanh β.

*Proof.* (a) *Canonical form.* Given q ∈ {±1}^P, there is exactly one configuration σ̄(q) with
all tree bonds equal to +1 and plaquette variables q: writing h(x, y) for the horizontal bond
from (x, y) to (x+1, y), all vertical bonds are in T (hence +1), so
q_{p(x,y)} = h(x, y) · h(x, y+1); with h(x, 0) = +1 (bottom row is in T), the recursion
h(x, y+1) = q_{p(x,y)} h(x, y) determines every non-tree bond uniquely, and conversely this
configuration realizes q.

(b) *Ψ is a bijection.* Given σ, set ε := g(σ). For a tree bond ⟨u, v⟩ with v the endpoint
farther from r in T, g_v = g_u σ_{⟨uv⟩}, so (σ^ε)_{⟨uv⟩} = g_u σ_{⟨uv⟩} g_v = +1. Since the q_p
are gauge invariant, σ^ε is the canonical form: σ^ε = σ̄(q(σ)). As (σ^ε)^ε = σ, we can
reconstruct σ = σ̄(q)^g from Ψ(σ) = (g, q): Ψ is injective. It is surjective because both sides
have cardinality 2^{|E|} = 2^{|V|−1+|P|}; alternatively, directly: given any (g, q), the
configuration σ := σ̄(q)^g has plaquettes q, and its tree-path products telescope to
g_r (Π σ̄ along the path) g_v = g_v, so Ψ(σ) = (g, q).

(c) *Pushforward.* The weight exp(β Σ_p q_p) depends on Ψ(σ) only through q, so the image
measure is (counting measure in g) ⊗ (Π_p e^{β q_p}), normalized — exactly the stated product.
Finally E_{ν_β}[q] = (e^β − e^{−β})/(e^β + e^{−β}) = tanh β. ∎

**8.3 Local gauge-invariant observables are plaquette functions.**

**Lemma 8.2.** Let R ⊆ B_N be a rectangle and let F be a bounded function of (σ_e)_{e∈E(R)}
that is invariant under all gauge transformations of B_N. Then there is F̃ with
F(σ) = F̃( (q_p(σ))_{p∈P(R)} ) and ‖F̃‖_∞ ≤ ‖F‖_∞.

*Proof.* Apply the construction of Lemma 8.1 inside R: let T_R be the comb tree of R with root
a corner of R, and for σ let g^R be the tree-path products computed within R. Extend to
ε : V(B_N) → {±1} by ε := g^R on V(R) and ε := 1 elsewhere; ε is a gauge transformation of B_N.
By invariance, F(σ) = F(σ^ε). On E(R), σ^ε has all T_R-bonds +1 and plaquettes (q_p)_{p∈P(R)},
so by the uniqueness in Lemma 8.1(a) applied to R, σ^ε|_{E(R)} = σ̄_R((q_p)_{p∈P(R)}) — a
function of the plaquette values in R alone. Since F only reads bonds in E(R),
F(σ) = F̃((q_p)_{p∈P(R)}) with F̃(q) := F(any extension of σ̄_R(q)). ∎

**8.4 Proof of Theorem 4.** (i) is Lemma 8.1.

(ii) Let F, G be bounded gauge-invariant observables supported on bonds of rectangles R_F, R_G,
and let x be such that P(R_F) ∩ (P(R_G) + x) = ∅. Take any box B_N containing R_F and R_G + x.
By Lemma 8.2, F = F̃((q_p)_{p∈P(R_F)}) and τ_x G = G̃((q_p)_{p∈P(R_G)+x}). By Lemma 8.1 these are
functions of two disjoint sub-collections of i.i.d. variables, hence independent:

  ⟨F · τ_x G⟩_{B_N} − ⟨F⟩_{B_N} ⟨τ_x G⟩_{B_N} = 0, exactly, for every such N and every β ∈ [0, ∞).

Moreover ⟨F⟩_{B_N} = E[F̃] is independent of N (the q's are i.i.d. in every volume), so the
thermodynamic limit exists trivially, is translation invariant, and the truncated correlation
vanishes identically at any separation making the plaquette supports disjoint. In particular,
for all such x, the bound ‖F‖‖G‖e^{−m|x|} holds for every m > 0: the clustering rate ("mass
gap") of gauge-invariant correlations in the 2D theory is infinite (ultralocality; equivalently
the correlation length is 0).

(iii) Let R be an a × b rectangle of plaquettes and C = ∂R. In Π_{p∈P(R)} q_p, every interior
bond of R occurs in exactly two plaquettes and every boundary bond in exactly one, so
Π_{p∈P(R)} q_p = Π_{e∈C} σ_e = W_C. By independence,

  ⟨W_C⟩ = Π_{p∈P(R)} E[q_p] = (tanh β)^{ab},

exactly, for every β ∈ [0, ∞) — an area law with string tension

  σ(β) = −(1/ab) ln ⟨W_C⟩ = ln(1/tanh β) = ln coth β,

which lies in (0, ∞] for every β ∈ [0, ∞) (it equals +∞ at β = 0 and is finite and strictly
positive for β > 0). No large-area limit is needed: the formula is exact at every finite
area. ∎

**8.5 Duality, done correctly.** Lemma 8.1 says that in the plaquette (dual-site) variables the
2D ℤ₂ gauge theory *is* a product measure: one independent ℤ₂ "spin" q_p per dual lattice site,
in an external field β, with no interaction whatsoever. So the Kramers–Wannier dual of 2D ℤ₂
gauge theory is a **non-interacting** spin system — a "0-dimensional" model — which is exactly
why (ii) and (iii) are exact. It is **not** dual to the 2D Ising model: the 2D Ising model is
self-dual (Kramers–Wannier 1941, with β* given by e^{−2β*} = tanh β), while the ℤ₂
gauge ↔ Ising duality pairs the **three**-dimensional models (Wegner 1971). This is the reason
the quantitative content of this note (Theorems 1–3) lives on the Ising side: in two dimensions
the gauge theory has no propagating degrees of freedom, and its clustering statement, while
exact and valid at all couplings, is ultralocal rather than a finite-rate decay.

---

## 9. Remarks: sharpness, range, and what is not claimed

**9.1 Sharpness.** The rates proved here are not optimal and are not claimed to be. From the
exact solution (Onsager 1944; McCoy–Wu 1973) the true inverse correlation length of the 2D
Ising model for 0 < β < β_c is known to be m_exact(β) = 2(β* − β) with e^{−2β*} = tanh β; e.g.
m_exact(0.1) ≈ 2.106 versus our m(0.1) ≈ 0.9195 and Theorem 3's ln(1/(3 tanh 0.1)) ≈ 1.207.
Nothing in this file uses or proves the exact formula; it is quoted only for calibration.

**9.2 Range of β.** Exponential clustering in fact holds in the entire high-temperature phase
β < β_c = ½ ln(1+√2) (sharpness of the phase transition: Aizenman–Barsky–Fernández 1987;
Duminil-Copin–Tassion 2016), and in the pure low-temperature phases (e.g. plus boundary
conditions) truncated correlations again decay exponentially — though not in the free-boundary
state used here, which at low temperature converges to the symmetric mixture and does not
cluster. Those proofs are long. The deliberate trade made here: a proof that is
complete on the page, on the *named open interval* (0, β₀) = (0, ½ ln(5/3)) — with the two-point
bound extended to (0, ½ ln 2) by Theorem 3 — with every constant explicit. On one side of the
transition, with an explicit constant, as promised.

**9.3 What this does not do.** These are two-dimensional, abelian, exactly-controllable
models. Nothing here constructs a continuum quantum field theory, takes a continuum limit
uniformly in the lattice spacing, or bears on the existence and mass gap of four-dimensional
quantum Yang–Mills theory. The theorems above are stated and proved for what they are: complete
lattice statements with explicit rates.

**9.4 Summary of the explicit formulas.**

  Interval:   β ∈ (0, β₀),  β₀ = ½ ln(5/3) ≈ 0.25541  (Theorems 1–2)
  Rate:       m(β) = ln(1/(4 tanh β))
  Prefactor:  2|A||B|/(1 − 4 tanh β)
  Verbatim:   |⟨F τ_x G⟩ − ⟨F⟩⟨G⟩| ≤ ‖F‖‖G‖ e^{−m̃(β)|x|}, m̃(β) = ln[(1−4 tanh β)/(8 tanh β)],
              for one-site F, G, x ≠ 0, β ∈ (0, ½ ln(13/11))  (Corollary 2.1)
  Two-point:  ⟨σ₀σ_x⟩ ≤ (4/3)(3 tanh β)^{|x|₁}/(1 − 3 tanh β), β ∈ (0, ½ ln 2)  (Theorem 3)
  2D gauge:   truncated correlations ≡ 0 at positive separation (every β);
              ⟨W_C⟩ = (tanh β)^{Area}; string tension ln coth β  (Theorem 4)

---

## References

1. R. L. Dobrushin, *The description of a random field by means of conditional probabilities
   and conditions of its regularity*, Theory Probab. Appl. 13 (1968) 197–224.
2. R. Bubley, M. Dyer, *Path coupling: a technique for proving rapid mixing in Markov chains*,
   FOCS 1997.
3. M. E. Fisher, *Critical temperatures of anisotropic Ising lattices II. General upper
   bounds*, Phys. Rev. 162 (1967) 480–485. (Source of the SAW bound on ⟨σ₀σ_x⟩.)
4. H. A. Kramers, G. H. Wannier, *Statistics of the two-dimensional ferromagnet I*, Phys. Rev.
   60 (1941) 252–262.
5. L. Onsager, *Crystal statistics I. A two-dimensional model with an order–disorder
   transition*, Phys. Rev. 65 (1944) 117–149.
6. B. M. McCoy, T. T. Wu, *The Two-Dimensional Ising Model*, Harvard Univ. Press, 1973.
7. F. J. Wegner, *Duality in generalized Ising models and phase transitions without local
   order parameters*, J. Math. Phys. 12 (1971) 2259–2272.
8. R. Balian, J. M. Drouffe, C. Itzykson, *Gauge fields on a lattice. II. Gauge-invariant Ising
   model*, Phys. Rev. D 11 (1975) 2098–2103. (2D ℤ₂ gauge theory solved exactly.)
9. M. Aizenman, D. J. Barsky, R. Fernández, *The phase transition in a general class of
   Ising-type models is sharp*, J. Stat. Phys. 47 (1987) 343–374.
10. H. Duminil-Copin, V. Tassion, *A new proof of the sharpness of the phase transition for
    Bernoulli percolation and the Ising model*, Comm. Math. Phys. 343 (2016) 725–745.
11. H.-O. Georgii, *Gibbs Measures and Phase Transitions*, 2nd ed., de Gruyter, 2011.
    (Chapter 8: Dobrushin uniqueness; quoted for context, not used.)
12. S. Friedli, Y. Velenik, *Statistical Mechanics of Lattice Systems*, Cambridge Univ. Press,
    2017. (General reference for §2 and §7 formalism; all needed facts reproved above.)
