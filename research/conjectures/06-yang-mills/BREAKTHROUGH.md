# Yang–Mills — Wave-2 Breakthrough

**LEGION 06, Wave 2.** This file strengthens the Gap-Transfer / Abelian-falsifier package of `REPORT.md` (Lemmas 5.2–5.4) into a single short theorem with a complete argument. Notation as in REPORT §3.2/§5: Wilson-action lattice gauge theory on ℤ^d, edge variables in a compact connected group G, β = bare inverse coupling, β₀(d,G) = Osterwalder–Seiler strong-coupling threshold (convergence radius of the cluster/character expansion), τ_x = lattice translation, θ = time reflection through the t = 0 site plane, θ_{1/2} = reflection through the t = 1/2 link plane, ⟨F; G⟩ = ⟨FG⟩ − ⟨F⟩⟨G⟩. For β̄ < β₀ set

  m̄ = m̄(β̄, d, G) := inf_{0 < β ≤ β̄} (cluster-expansion clustering rate) > 0,  ξ̄ := 1/m̄ < ∞ (lattice units).

Both horns demanded of Wave 2 are proved below: **(Horn 1)** any continuum limit taken at fixed strong bare coupling is ultralocal — its lattice correlation length stays bounded, so no finite physical mass gap survives a → 0 (the physical gap diverges like m̄/ε); **(Horn 2)** any argument valid verbatim for compact U(1) in d = 4 cannot prove a nonabelian all-couplings mass gap. They are combined into one localization theorem.

---

## Theorem

**Theorem (Two-Gate Localization Theorem).** Let d ≥ 2, G compact connected, β̄ < β₀(d, G), and let μ be the unique infinite-volume Gibbs state of the Wilson-action theory at any β ∈ (0, β̄]. Let ℋ be its Osterwalder–Schrader (OS) Hilbert space built from the time-≥ 0 observable algebra 𝔄₊, with transfer operator T and vacuum Ω.

**Part A (spectral gap and Ratio Lemma — normalization-proof, observable-proof).**
T is self-adjoint, 0 ≤ T ≤ 𝟙, TΩ = Ω, the eigenvalue 1 is simple, and

  spec( T restricted to Ω^⊥ ) ⊆ [0, e^{−m̄}].

Consequently, for **every** F in (the L²-closure of) 𝔄₊ — local or not, k-dependent, smeared, block-averaged, composite — the reflected truncated autocorrelation R_F(n) := ⟨θF · τ_n F⟩ − ⟨F⟩² satisfies

  (★)  0 ≤ R_F(n₂) ≤ e^{−m̄ (n₂ − n₁)} · R_F(n₁)  for all integers n₂ ≥ n₁ ≥ 0,

an inequality containing **no observable-dependent constant**; and for two observables, |⟨θF; τ_n G⟩| ≤ R_F(n)^{1/2} R_G(n)^{1/2}.

**Part B (fixed strong bare coupling ⇒ ultralocal limit; Horn 1).**
Let ε_k ↓ 0, β_k ≤ β̄, and let F_k ∈ 𝔄₊^{(k)} and Z_k > 0 be arbitrary. Put h_k(t) := Z_k R_{F_k}(⌊t/ε_k⌋) for physical time t > 0. Then:

1. **(Two-point rigidity.)** If limsup_k h_k(t₁) < ∞ for some t₁ > 0, then lim_k h_k(t₂) = 0 for every t₂ > t₁. Hence no subsequence, no choice of observables F_k, and no renormalization Z_k yields a limit that is finite and nonzero at two distinct physical times.
2. **(Ultralocality.)** Every pointwise subsequential limit h that is finite on (0, ∞) vanishes identically on (0, ∞): the limiting truncated two-point functions are supported on coincident points. This includes distributional limits tested against physical test functions, since smeared fields Φ_k(f) = Σ_x ε_k^d f(ε_k x) Φ_x with supp f ⊆ {t ≥ 0} are admissible F_k.
3. **(Gap divergence.)** The physical Hamiltonian gap of μ_k at spacing ε_k obeys Δ_k ≥ m̄/ε_k → ∞, and the physical correlation length obeys ε_k ξ(β_k) ≤ ε_k ξ̄ → 0. In particular **no finite correlation length in lattice units can correspond to a finite physical gap after a → 0**: a limit with gap Δ ∈ (0, ∞) forces ε_k ξ(β_k) → Δ^{−1}, i.e. ξ(β_k) → ∞, impossible for β_k ≤ β̄.
4. **(No gapped QFT limit.)** No quantum field theory possessing a mass gap Δ ∈ (0, ∞) together with **some** local hermitian operator A with (A − ⟨A⟩)Ω ≠ 0 can arise as such a limit: its Källén–Lehmann function h(t) = ∫_{[Δ,∞)} e^{−tE} dρ_A(E) is finite and strictly positive at **all** t > 0, contradicting item 1.
5. **(Trajectory constraint.)** Any bare sequence (ε_k, β_k) whose renormalized two-point functions converge, finitely and not identically to zero, at noncoincident points must satisfy limsup_k β_k ≥ β₀(d, G).

**Part C (Abelian falsifier; Horn 2).**
Let d = 4 and let 𝒞 be the class of pairs (G, S): G compact connected nontrivial, S a reflection-positive plaquette action of Wilson/heat-kernel (Villain) class. Call a predicate Π on 𝒞 **group-blind** if (U(1), Villain) satisfies Π whenever the nonabelian target (SU(N), Wilson) does. Then:

1. There is **no** true theorem of the form "Π(G, S) ⇒ m_lat(β; G, S) > 0 for all β ∈ (0, ∞)" with group-blind Π; likewise with the conclusion replaced by "Wilson-loop area law for all β".
2. Concretely, let 𝒯 be the toolkit {compactness; connectedness; nontrivial center acting nontrivially in the source representation; reflection positivity for site and link reflections; positive self-adjoint transfer matrix; convergent strong-coupling cluster/character expansion with gap and area law for β < β₀; Migdal–Kadanoff-type decimation inequalities}. Every member of 𝒯 holds for (U(1), Villain). Hence **no conjunction of 𝒯-members implies the all-β gap or the all-β area law**, and every sound proof for nonabelian G must use, at some specific step, a premise **false for (U(1), Villain) at large β** — necessarily a weak-coupling premise, since at β < β₀ the abelian and nonabelian theories share gap and area law.

**Corollary (localization of the Clay burden).** Combining B.5 and C.2: every route to a Clay-compliant 4D nonabelian gap must (i) control the theory along sequences leaving every strong-coupling region — where, by Part B, nothing survives except ultralocal debris — and (ii) inject a nonabelian-specific weak-coupling estimate, the minimal candidate being "ξ_{SU(N)}(β) < ∞ for all β while ξ_{U(1)}(β) = ∞ for β > β_c". This is exactly hypothesis (H2) / target T1 / step S3 of REPORT.md. No group-blind ingredient and no fixed-strong-coupling ingredient can contribute a nonzero share of the proof.

---

## Proof

### External inputs (all [ESTABLISHED]; nothing else is imported)

- **(E1) Reflection positivity and transfer formalism.** For Wilson and heat-kernel (Villain) actions, the lattice Gibbs measures are reflection positive for site reflections (planes of sites) and link reflections (planes at half-integer time), and time-translation invariant; the transfer matrix is self-adjoint and (strictly) positive. [Osterwalder–Seiler, Ann. Phys. 110 (1978) 440; Lüscher, Comm. Math. Phys. 54 (1977) 283; Seiler, LNP 159 (1982); Glimm–Jaffe, *Quantum Physics*, ch. 6.]
- **(E2) Strong-coupling cluster expansion.** For 0 < β ≤ β̄ < β₀(d, G): the infinite-volume Gibbs state exists, is unique, is invariant under lattice translations and time reflection, and there is m̄ = m̄(β̄, d, G) > 0 such that for all local gauge-invariant F, G: |⟨F; τ_x G⟩| ≤ C_{F,G} e^{−m̄|x|}. Moreover the same expansion gives the Wilson-loop area law in this regime, for every compact G — including U(1). [Osterwalder–Seiler 1978; Seiler 1982.]
- **(E3) Guth's theorem.** d = 4, G = U(1), Villain action: there is β_c < ∞ such that for β > β_c the Wilson loop obeys a perimeter law (no area law; deconfinement). [Guth, Phys. Rev. D 21 (1980) 2291.]
- **(E4) Fröhlich–Spencer theorem.** d = 4, G = U(1), Villain action: for β large the theory is in a massless Coulomb phase; in particular there exist local gauge-invariant observables (field-strength/plaquette variables) whose truncated two-point functions have free-Maxwell power-law (∼ |x|^{−4}) long-distance behavior and are **not** O(e^{−m|x|}) for any m > 0. Hence m_lat(β) = 0 for β > β_c′. [Fröhlich–Spencer, Comm. Math. Phys. 83 (1982) 411.]

Everything below these four inputs is proved in full.

### Step 1 — The OS space and the operator properties of T

Fix β ≤ β̄ and let μ be the unique infinite-volume state (E2). Let 𝔄₊ be the algebra of bounded cylinder functions of link variables at times t ≥ 0. On 𝔄₊ define the sesquilinear form (F, G) := ⟨ (θF̄) · G ⟩_μ. Site-reflection positivity (E1) says (F, F) ≥ 0; quotient by null vectors and complete to get ℋ, with classes [F] and vacuum Ω := [𝟙]. Time-translation invariance of μ makes T[F] := [τ₁F] well defined and bounded with TΩ = Ω:

- **Self-adjointness.** ([F], T[G]) = ⟨(θF̄) τ₁G⟩ = ⟨(τ_{−1}θF̄) G⟩ = ⟨(θ τ₁F̄) G⟩ = (T[F], [G]), using translation invariance and θτ₁ = τ_{−1}θ.
- **Positivity.** Since θ = θ_{1/2} ∘ τ₁ (check on times: t ↦ t+1 ↦ 1−(t+1) = −t), for F ∈ 𝔄₊ we have ([F], T[F]) = ⟨(θF̄) τ₁F⟩ = ⟨(θ_{1/2} τ₁F̄)(τ₁F)⟩ ≥ 0 by link-reflection positivity (E1), because τ₁F depends only on links with both endpoints at t ≥ 1, strictly on the positive side of the plane t = 1/2. The set {[F] : F ∈ 𝔄₊} is dense, so T ≥ 0.
- **Contraction.** By T ≥ 0 and Cauchy–Schwarz, ([F], T[F]) ≤ ([F],[F])^{1/2}([F], T²[F])^{1/2}; iterating, ([F],T[F]) ≤ ‖[F]‖^{2−2^{1−n}} ([F], T^{2ⁿ}[F])^{2^{−n}}, and ([F], T^{2ⁿ}[F]) = ⟨(θF̄) τ_{2ⁿ}F⟩ ≤ ⟨|θF|²⟩^{1/2}⟨|F|²⟩^{1/2} is bounded uniformly in n (F bounded, μ a probability measure). Letting n → ∞ gives ([F], T[F]) ≤ ‖[F]‖², i.e. ‖T‖ ≤ 1. (Standard multiple-reflection argument; cf. Glimm–Jaffe Thm. 6.13.)

So T = T*, 0 ≤ T ≤ 𝟙, TΩ = Ω. Let E(·) be its spectral measure.

### Step 2 — Uniform spectral gap of T from clustering

For local gauge-invariant F put v_F := [F] − (Ω,[F])Ω ⊥ Ω. For local F, G, (E2) gives

  |(v_F, Tⁿ v_G)| = |⟨θF̄; τ_n G⟩| ≤ C e^{−m̄ n}  for all n ≥ 0,

since θF̄ is again a local gauge-invariant observable. Take G = F: the finite positive Borel measure ν(dλ) := ‖E(dλ) v_F‖² on [0,1] satisfies ∫ λⁿ dν(λ) ≤ C e^{−m̄ n}. For any a > e^{−m̄}: ν([a,1]) ≤ a^{−n} ∫ λⁿ dν ≤ C (e^{−m̄}/a)ⁿ → 0, hence ν((e^{−m̄}, 1]) = 0 by monotone convergence as a ↓ e^{−m̄}. So every v_F has spectral support in [0, e^{−m̄}]. The span of {v_F} ∪ {Ω} is dense (cylinder functions are dense), each v_F ⊥ Ω, so span{v_F} is dense in Ω^⊥; and {v : supp ν_v ⊆ [0, e^{−m̄}]} = Ran E([0, e^{−m̄}]) is a **closed** subspace. Therefore

  Ω^⊥ ⊆ Ran E([0, e^{−m̄}]),  i.e.  spec(T|_{Ω^⊥}) ⊆ [0, e^{−m̄}],

and in particular the eigenvalue 1 is simple. Note m̄ depends only on (β̄, d, G): the bound is **uniform in β ≤ β̄ and in the observable**.

### Step 3 — The Ratio Lemma (★)

Let F ∈ ℋ-closure of 𝔄₊, v := [F] − (Ω,[F])Ω, ν̂ := ‖E(·)v‖². Since TΩ = Ω and T commutes with the projection onto Ω^⊥,

  R_F(n) = ⟨θF̄ · τ_nF⟩ − |⟨F⟩|² = ([F], Tⁿ[F]) − |(Ω,[F])|² = (v, Tⁿ v) = ∫_{[0, e^{−m̄}]} λⁿ dν̂(λ),

using Step 2 (supp ν̂ ⊆ [0, e^{−m̄}] because v ∈ Ω^⊥). Immediately R_F(n) ≥ 0, and for n₂ ≥ n₁ ≥ 0:

  R_F(n₂) = ∫ λ^{n₁} · λ^{n₂−n₁} dν̂(λ) ≤ (e^{−m̄})^{n₂−n₁} ∫ λ^{n₁} dν̂(λ) = e^{−m̄(n₂−n₁)} R_F(n₁),

because 0 ≤ λ ≤ e^{−m̄} on the support. This is (★). No constant depends on F. For two observables, |⟨θF̄; τ_nG⟩| = |(v_F, T^{n/2}·T^{n/2} v_G)| ≤ (v_F, Tⁿv_F)^{1/2}(v_G, Tⁿv_G)^{1/2} = R_F(n)^{1/2}R_G(n)^{1/2} by Cauchy–Schwarz with T ≥ 0 (for odd n use T^{n} = T^{(n−1)/2}T·T^{(n−1)/2} and ‖T^{1/2}‖ ≤ 1). **This is the step that was unproved in REPORT.md Lemma 5.2(a):** an upper bound |R(n)| ≤ Ce^{−m̄n} alone cannot bound the ratio R(n₂)/R(n₁), because no lower bound on R(n₁) is available from the cluster expansion; positivity of the transfer operator is what makes the ratio inequality true. Part A is proved. ∎

### Step 4 — Part B

Fix t₂ > t₁ > 0, and let n_i^{(k)} := ⌊t_i/ε_k⌋, so n₂^{(k)} − n₁^{(k)} ≥ (t₂ − t₁)/ε_k − 1 → ∞.

1. **(Rigidity.)** Multiply (★) by Z_k: 0 ≤ h_k(t₂) ≤ e^{−m̄(n₂^{(k)} − n₁^{(k)})} h_k(t₁). If limsup h_k(t₁) =: M < ∞, then limsup h_k(t₂) ≤ M · lim e^{−m̄((t₂−t₁)/ε_k − 1)} = 0. Note that β_k, F_k, Z_k may all vary with k: (★) holds for each k with the same m̄. ∎
2. **(Ultralocality.)** If h(t) := lim_k h_k(t) exists and is finite for every t ∈ (0, ∞) (along any subsequence), then for each t pick t₁ ∈ (0, t); finiteness at t₁ and item 1 give h(t) = 0. So h ≡ 0 on (0, ∞): all limiting truncated correlations vanish at noncoincident times; combined with the off-diagonal Cauchy–Schwarz bound of Step 3, all limiting truncated **cross**-correlations vanish there too. Smeared fields Φ_k(f) with supp f ⊆ {t ≥ 0} lie in 𝔄₊^{(k)} (finite linear combinations of link functionals, then L² limits), so the statement covers limits tested distributionally in the physical variables. Every surviving limit object is supported on coincident points: ultralocal. ∎
3. **(Gap divergence.)** Define the lattice Hamiltonian at spacing ε_k on Ω^⊥ through the spectral calculus, H_k := −ε_k^{−1} log T_k (with H_k = +∞ on ker T_k, harmless). Step 2 gives spec(H_k) ⊆ {0} ∪ [m̄/ε_k, +∞], so Δ_k ≥ m̄/ε_k → ∞. Equivalently ξ(β_k) ≤ ξ̄ in lattice units, so the physical correlation length ε_k ξ(β_k) ≤ ε_k ξ̄ → 0. If a limit theory had gap Δ ∈ (0, ∞) with correlations decaying at physical rate Δ, matching lattice decay rate m_lat(β_k)/ε_k would force ε_k ξ(β_k) → Δ^{−1} > 0 — contradiction. This is the mandated statement: **at fixed strong coupling the correlation length in lattice units stays bounded, hence cannot correspond to any finite physical gap after a → 0; the only "gap" in the limit is +∞.** ∎
4. **(No gapped QFT limit.)** Let a QFT (OS/Wightman, Hamiltonian H ≥ 0, vacuum Ω_c, gap Δ ∈ (0, ∞)) have a local hermitian operator A with w := (A − ⟨A⟩)Ω_c ≠ 0. Its Euclidean autocorrelation is h(t) = (w, e^{−tH} w) = ∫_{[Δ, ∞)} e^{−tE} dρ_A(E), where ρ_A := ‖E_H(·)w‖² is a positive measure, nonzero since w ≠ 0, and the integral converges for t > 0 (spectral theorem; temperedness). The integrand is strictly positive, so h(t) ∈ (0, ∞) for **every** t > 0 — in particular finite and nonzero at two distinct times. If the lattice family converged to this theory at those two times (that is what "the limit is this QFT" means for its two-point data, whether tested pointwise or against smeared approximants as in item 2), item 1 is violated. ∎
5. **(Trajectory constraint.)** Contrapositive of items 1–4: if limsup β_k < β₀ then eventually β_k ≤ β̄ for some β̄ < β₀ and the above applies. So a nondegenerate limit requires limsup β_k ≥ β₀(d, G). ∎

### Step 5 — Part C

1. Suppose Π is group-blind and "Π(G,S) ⇒ ∀β: m_lat(β; G, S) > 0" were a true theorem on 𝒞. Instantiate at (U(1), Villain) ∈ 𝒞 (compact, connected, RP heat-kernel action — admissible by (E1)). The conclusion asserts m_lat(β) > 0 for all β; but (E4) gives local gauge-invariant observables with non-exponentially-decaying truncated correlations at large β, i.e. m_lat(β) = 0 there. Contradiction. For the area-law version, (E3) gives a perimeter law at large β, contradicting an all-β area law — this horn consumes only Guth's theorem, whose statement is unambiguous. ∎
2. Verification that (U(1), Villain) satisfies every member of 𝒯, each [ESTABLISHED]: compactness/connectedness — trivial; nontrivial center acting nontrivially — U(1) is its own center and acts by e^{iα} ≠ 1 in the charge-1 representation; RP for both reflections and positive self-adjoint transfer matrix — (E1), since the heat-kernel action has nonnegative character coefficients; convergent strong-coupling expansion with m_lat(β) > 0 and area law for β < β₀(4, U(1)) — (E2), whose proofs are group-agnostic; Migdal–Kadanoff decimation inequalities — valid for every compact group, U(1) included (this is precisely why they cannot alone separate SU(2) from U(1); cf. the Ito–Seiler analysis of Tomboulis' program, arXiv:0803.3019). Hence 𝒯 ∪ {any consequences of 𝒯} is group-blind, and by C.1 no conjunction of 𝒯-members implies the all-β gap or area law. Therefore any sound proof for nonabelian G contains a premise P* outside the deductive closure of 𝒯 with P* false at (U(1), Villain). Finally, P* must be false for U(1) **at large β specifically**: for β < β₀(4, U(1)) the abelian theory *does* have a gap and an area law (E2), so any property of the strong-coupling regime alone is shared and cannot be the separating premise. ∎

**Remark (referee test; Tomboulis localization).** C.2 yields a mechanical soundness test: given any claimed all-β nonabelian gap/confinement proof, run each step at (U(1), Villain); a sound proof must have at least one step that provably breaks there, in the weak-coupling regime. For the Migdal–Kadanoff program of Tomboulis [DISPUTED, cf. REPORT §3.3], the decimation inequalities pass the U(1) test (they hold there), so the entire nonabelian content is carried by the contested interpolation/twist step flagged by Ito–Seiler — which is therefore not a technical gap but the whole theorem.

### Step 6 — Corollary

By B.5, a Clay-compliant limit lives only on trajectories with limsup β_k ≥ β₀; by B.3, along any such trajectory a finite physical gap forces ξ(β_k) → ∞. By C.2, the estimate that achieves this for SU(N) must fail for U(1)₄ — and "ξ(β) < ∞ for all β" is exactly such a statement, true (conjecturally) for SU(N), false for U(1) beyond β_c (E4). Producing that two-sided control of ξ(β → ∞) is hypothesis (H2) of REPORT Lemma 5.1, equivalently target T1 / step S3. Both easy regimes — fixed strong coupling and group-blind structure — are closed by Parts B and C respectively; hence they can contribute nothing, and the Clay burden is localized entirely in the nonabelian weak-coupling crossover. ∎

**Sharpness.** The threshold in B.5 is not vacuous: for U(1)₄ itself, once β_k > β_c (outside the strong-coupling region), nondegenerate scaling limits *do* exist — the free-Maxwell limit (Fröhlich–Spencer; Driver's U(1)₄ continuum limit). And Göpfert–Mack's 3D U(1) theorem exhibits the intended nonabelian-4D pattern (ξ(β) → ∞ with m_lat(β) > 0 for all β) in the one case where a positive-weight dual exists. Part B is thus tight: it kills exactly the fixed-strong-coupling route, no more.

---

## What is new vs REPORT.md

1. **A proof where REPORT had a gap.** REPORT Lemma 5.2(a) asserted the normalization-independent ratio decay ⟨F; τ_xF⟩/⟨F; τ_{x′}F⟩ → 0 with the one-word proof "arithmetic". That step was **not** arithmetic: the cluster expansion yields only an upper bound on correlations, and an upper bound on the numerator plus an upper bound on the denominator bounds no ratio. Wave 2 supplies the correct and complete argument (Steps 1–3): reflection positivity for link reflections makes the transfer operator **positive**, the truncated autocorrelation becomes a moment sequence ∫λⁿ dν̂ of a positive spectral measure supported in [0, e^{−m̄}], and (★) follows with no observable-dependent constants. The package is thereby upgraded from [FOLKLORE, MADE PRECISE — proof sketched] to a fully argued theorem.
2. **Strictly stronger statement.** REPORT's Lemma 5.2 fixed a local observable F and a template renormalization Z_Φ(ε). The theorem here allows the observable itself to vary arbitrarily with k within the time-≥ 0 algebra — including block-spin averages, physically smeared fields, and k-dependent composite renormalized operators — and any Z_k. This closes the loopholes ("choose cleverer ε-dependent observables / distributional limits") that the REPORT version left formally open, via the operator-level bound spec(T|_{Ω^⊥}) ⊆ [0, e^{−m̄}], uniform in β ≤ β̄ and in the observable.
3. **The falsifier is now a schema with a proof, not prose.** Lemma 5.4's "any set of hypotheses P" is replaced by a precise class 𝒞, a group-blindness predicate, an explicit shared toolkit 𝒯 with itemized U(1)-verification, and a disjunctive conclusion in which the area-law horn consumes only Guth's theorem. New sharpening: the separating premise must live in the **weak-coupling** regime, because at strong coupling U(1) and SU(N) provably share gap and area law — this welds the falsifier to the ultralocality gate.
4. **Unification.** Lemmas 5.2 + 5.3 + 5.4 become one theorem with one corollary that localizes the entire Clay burden in a single sentence: *nothing group-blind and nothing at fixed strong coupling can contribute; all content is a nonabelian-specific estimate on ξ(β → ∞)* — i.e. (H2)/T1/S3, now with both closures fully proved rather than sketched.

## Why Clay YM remains open

Both gates are **negative** results: they prove that certain proof strategies cannot work; they construct nothing. Hypotheses (H1)–(H4) of REPORT Lemma 5.1 are untouched: no convergence of Schwinger functions along the asymptotically free trajectory β(ε) → ∞, no uniform clustering (H2), no Euclidean-invariance restoration, no nontriviality/identification. Part B applies only where β_k stays in a strong-coupling region; on the physically mandatory trajectory β_k → ∞ nothing here (or anywhere in the literature) controls the theory — that is exactly step S3, for which no theorem, technique, or nontrivial special case exists. Part C shows what any future proof must contain (a U(1)-false weak-coupling premise) without providing any candidate for it. Targets T1–T4 of REPORT §5.3 all remain open. The Yang–Mills existence and mass gap problem is fully open.

## Honesty label

**[SYNTHESIS] with complete proofs from [ESTABLISHED] inputs.** The four external inputs (E1)–(E4) are published theorems (Osterwalder–Seiler 1978 / Lüscher 1977 / Seiler 1982; Guth 1980; Fröhlich–Spencer 1982); every other step — OS construction bookkeeping, positivity of T via θ = θ_{1/2}∘τ₁, the spectral-support moment argument, the Ratio Lemma, the ultralocality/gap-divergence/trajectory corollaries, the falsifier instantiation — is argued in full above. No fake constructive QFT: nothing is constructed, no continuum nonabelian object is claimed to exist. The theorem is expert folklore in spirit; its value is that the folklore is here **actually proved**, in a form robust against renormalization, observable choice, and subsequence tricks, with the one genuinely non-arithmetic step (positivity ⇒ ratio bound) identified and supplied. **No progress on the Clay problem itself is claimed; it remains open.** Classification per REPORT §7.2: mission tier (c) strengthened to theorem grade; tiers (a)/(b) unchanged.

*End of Wave-2 breakthrough file, LEGION 06.*
