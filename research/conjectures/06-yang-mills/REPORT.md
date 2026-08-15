# LEGION 06 — Yang–Mills Existence and Mass Gap

**Mission:** Attack the Clay Millennium Problem "Quantum Yang–Mills existence and mass gap." No fake constructive QFT. Deliverables sought: (a) a mathematically precise lemma on a lattice or 2D/3D analogue; (b) a clean formulation of the missing analytic step from Osterwalder–Schrader / Wightman axioms to a mass gap; (c) a no-go for a common formal manipulation.

**Execution note.** The commander's environment provided no subagent-spawning (Task) tool, so the ten mandated lanes 06-01 … 06-10 were executed serially by the commander itself, at full depth, with literature verification by live search. Lane coverage is mapped below and audited in §7.

| Lane | Topic | Covered in |
|------|-------|-----------|
| 06-01 | Clay statement: axioms + gap | §2 |
| 06-02 | Constructive QFT successes; why 4D differs | §3.1 |
| 06-03 | Lattice YM, Wilson action, reflection positivity | §3.2 |
| 06-04 | Mass gap on the lattice: what is proved | §3.3 |
| 06-05 | Instantons, θ-vacuum, topology vs gap | §4.1 |
| 06-06 | BRST, Gribov, why physics quantization isn't a proof | §4.2 |
| 06-07 | Dimensional ladder 2D/3D vs the missing 4D RG control | §5.1, §6 |
| 06-08 | Correlation inequalities, cluster/polymer expansions | §5.2, §3.3 |
| 06-09 | Clay "existence" vs physicists' confinement/glueballs | §4.3 |
| 06-10 | Complete proof outline with the gap named | §6 |

**Honesty labels used throughout:**

- **[ESTABLISHED]** — published theorem, verified citation.
- **[PARTIAL]** — rigorous but incomplete program.
- **[DISPUTED]** — published claim whose completeness is contested in the literature.
- **[PHYSICS-LEVEL]** — persuasive physics argument, not a theorem.
- **[NUMERICAL]** — lattice Monte Carlo evidence, not a theorem.
- **[FOLKLORE, MADE PRECISE]** — statement widely understood by experts, assembled here into a precise lemma with standard proof ingredients; *no claim of new mathematics*.
- **[SYNTHESIS]** — new *assembly* of established results produced by this legion; the components are not new.
- **[OPEN]** — unproved; **[SPECULATIVE]** — our conjecture/target.

---

## 1. Executive Summary

**Verdict: no breakthrough on the Clay problem; the problem is fully open.** This legion produced no new theorem of substance and makes no claim to one. What it does deliver, per the mission's fallback tiers:

1. **A clean formulation of the missing analytic step** (mission tier (b)): **Lemma 5.1 (Gap-Transfer / Interface Lemma)** isolates, as four numbered hypotheses (H1)–(H4) about lattice measures, *exactly* what uniform estimates would convert known lattice facts into a Clay-compliant Wightman theory with mass gap Δ ≥ m₀. Everything in the conclusion is standard given the hypotheses; the entire Clay problem is the hypotheses — above all **(H2): exponential clustering with a rate that is uniform in the lattice spacing along the asymptotically free bare-coupling trajectory.** A corollary of the formulation: "existence" and "mass gap" are not sequential sub-problems; on the only known rigorous route they must be proved *simultaneously*, by the same uniform estimate.

2. **No-gos for common formal manipulations** (mission tier (c)):
   - **Lemma 5.2 + Corollary 5.3:** any continuum scaling limit taken at *fixed* bare coupling in the rigorously controlled strong-coupling regime is ultralocal (no propagating excitations, "infinite gap"); hence the theorems "lattice YM confines and has a gap at strong coupling" — which are real theorems — carry *zero* logical weight toward the Clay problem without two-sided asymptotic control of the correlation length as β → ∞. This kills the folk syllogism "strong-coupling gap + (believed) absence of phase transition ⇒ continuum gap."
   - **Lemma 5.4 (Abelian falsifier):** any proof scheme for a 4D non-abelian gap/confinement at all couplings whose steps remain valid verbatim for G = U(1) is unsound, because compact U(1) lattice gauge theory in 4D *provably* has a massless (Coulomb, deconfined) phase at weak coupling (Guth; Fröhlich–Spencer). This locates precisely the step any such proof must carry non-abelian information through — and it is exactly the disputed step in the best-known claimed proof (Tomboulis; objections of Ito–Seiler).
   - **Observation 5.5:** conditional on the standard renormalization-group identification of the continuum theory, the mass gap has an identically vanishing asymptotic expansion in the coupling; therefore *no* BRST/perturbative construction — which produces formal power series — can ever exhibit Δ > 0. Physics quantization is structurally, not just technically, insufficient.

3. **A precise target ladder on analogues** (mission tier (a), partially achieved): named open lemmas **T1–T4** in §5.3, including the *weak-to-strong crossover lemma* (T1, the single named gap of §6) and the 3D-SU(2) analogue of the Göpfert–Mack theorem (T3) — the latter being, in this legion's judgment, the most realistic "next theorem" in the subject, since Göpfert–Mack's 3D U(1) result remains the **only** nonperturbative weak-coupling mass-gap theorem ever proved in any gauge theory.

Nothing above is fake constructive QFT: every labeled component is either a verified citation or an explicitly flagged assembly.

---

## 2. The Problem, Stated Precisely (lane 06-01)

**Official statement** (Jaffe–Witten, *Quantum Yang–Mills theory*, in *The Millennium Prize Problems*, Clay Mathematics Institute / AMS, 2006, pp. 129–152) **[ESTABLISHED as the problem text]:**

> Prove that for any compact simple gauge group G, a non-trivial quantum Yang–Mills theory exists on ℝ⁴ and has a mass gap Δ > 0. Existence includes establishing axiomatic properties at least as strong as those cited in [Streater–Wightman; Osterwalder–Schrader].

Unpacking, the proof must produce:

1. **Existence.** A separable Hilbert space ℋ, a continuous unitary positive-energy representation of the Poincaré group, a unique Poincaré-invariant vacuum Ω, and local quantum fields (operator-valued distributions) satisfying the **Wightman axioms** — or Euclidean Schwinger functions satisfying the **Osterwalder–Schrader (OS) axioms** (temperedness/growth, Euclidean covariance, reflection positivity, permutation symmetry, clustering), which yield the Wightman theory by the OS reconstruction theorem (Osterwalder–Schrader, Comm. Math. Phys. 31 (1973) 83–112 and 42 (1975) 281–305) **[ESTABLISHED]**. For gauge theory the axiom-satisfying fields are the **gauge-invariant local operators** (e.g. the renormalized tr F² density); the gauge potential A_μ itself is not a Wightman field and need not be. Wilson loops are natural auxiliary (extended, non-local) observables.

2. **Identification.** The theory must *be* Yang–Mills for the given G: its short-distance behavior must match renormalized perturbation theory (asymptotic freedom), so that "a theory" is not smuggled in that satisfies the axioms vacuously (e.g. a generalized free field, or an ultralocal theory — see Lemma 5.2). This clause is often glossed over; we make it hypothesis (H4) of Lemma 5.1.

3. **Mass gap.** The Hamiltonian H (generator of time translations, spec H ⊆ [0, ∞)) satisfies spec(H) ⊆ {0} ∪ [Δ, ∞) with Δ > 0, {0} being the simple eigenvalue of Ω.

**Equivalence used throughout — gap ⇔ exponential clustering [ESTABLISHED, standard]:**

- (⇐) If for a dense set of local A, B: |⟨AΩ, e^{−tH} BΩ⟩ − ⟨AΩ, Ω⟩⟨Ω, BΩ⟩| ≤ C_{A,B} e^{−mt} for all t > 0, then the spectral theorem gives spec(H) ∩ (0, m) = ∅ and vacuum uniqueness on the cyclic sector. (Textbook: Glimm–Jaffe, *Quantum Physics*, 2nd ed., Springer 1987.)
- (⇒) A gap Δ implies exponential decay of Euclidean-time-separated truncated correlations at rate Δ (spectral theorem), and exponential decay in *spacelike* directions at the same rate by Lorentz covariance (Fredenhagen, "A remark on the cluster theorem," Comm. Math. Phys. 97 (1985) 461) **[ESTABLISHED]**.

So the analytic content of "mass gap" is: *uniform exponential clustering of vacuum correlations of the gauge-invariant local algebra.* This is the form in which the problem is attacked on the lattice, and the form in which Lemma 5.1 is stated.

**Context that calibrates difficulty [ESTABLISHED]:** as of this writing, *no* interacting quantum field theory satisfying the Wightman axioms has ever been constructed in four spacetime dimensions — for any model, gauge or not. The Clay problem asks for the hardest known case first. (Status assessment consistent with M. Douglas, "Report on the status of the Yang–Mills Millennium Prize problem," Clay Mathematics Institute, 2004.)

**θ-ambiguity remark.** For compact simple G, π₃(G) = ℤ, so classically a one-parameter family of quantizations (θ-vacua) exists; the Wilson lattice action corresponds to θ = 0, and the Clay statement is read as requiring (at least) that theory. See §4.1.

---

## 3. The Rigorous Landscape: What Is Actually Proved

### 3.1 Constructive QFT successes, 2D Yang–Mills, and why 4D is different (lane 06-02)

**Scalar/fermionic low-dimensional constructions [ESTABLISHED]:**

- P(φ)₂: full Wightman axioms and particle structure; mass gap at weak coupling (Glimm–Jaffe–Spencer, "The Wightman axioms and particle structure in the P(φ)₂ quantum field model," Ann. of Math. 100 (1974) 585–632; Simon, *The P(φ)₂ Euclidean (Quantum) Field Theory*, Princeton, 1974).
- φ⁴₃: existence (Glimm–Jaffe 1973); Wightman axioms and mass gap at weak coupling (Feldman–Osterwalder, Ann. Phys. 97 (1976) 80–135); modern SPDE reconstructions via regularity structures (Hairer, Invent. Math. 198 (2014) 269–504) and paracontrolled calculus.
- 2D Yukawa and Gross–Neveu models: constructed (various authors, 1970s–80s).

**Two-dimensional Yang–Mills — exactly solvable [ESTABLISHED]:**

- Lattice heat-kernel action is *exactly* self-similar under block decimation (semigroup property of the heat kernel on G; Migdal 1975), so the 2D continuum limit exists for every coupling and is explicitly computable.
- Rigorous continuum constructions: Driver, "YM₂: continuum expectations, lattice convergence, and lassos," Comm. Math. Phys. 123 (1989) 575–616; Gross–King–Sengupta, Ann. Phys. 194 (1989) 65–112; Fine, Comm. Math. Phys. 134 (1990) 273–292 and 140 (1991) 321–338; Klimek–Kondracki, Comm. Math. Phys. 113 (1987) 389–402; Sengupta, *Gauge theory on compact surfaces*, Mem. AMS 126 (1997), no. 600; Lévy, *Yang–Mills measure on compact surfaces*, Mem. AMS 166 (2003), no. 790, and *Two-dimensional Markovian holonomy fields*, Astérisque 329 (2010). Partition functions on surfaces: Witten, Comm. Math. Phys. 141 (1991) 153–209.
- Exact area law in 2D: for a simple loop enclosing area |A|, ⟨W⟩ = (heat-kernel character)(g²|A|), giving string tension σ = g² c_R/2 (c_R = Casimir of the source representation, standard normalization) for **all** couplings — confinement is exact but *kinematic* (no transverse gluon degrees of freedom in 2D).
- Large-N master field on the plane: Lévy, "The master field on the plane" (arXiv:1112.2452; Astérisque); Makeenko–Migdal loop equations (Phys. Lett. B 88 (1979) 135) proved rigorously in 2D (Driver–Hall–Kemp, arXiv:1601.06283; Driver–Gabriel–Hall–Kemp, arXiv:1602.03905). One-plaquette large-N model: Gross–Witten, Phys. Rev. D 21 (1980) 446; Wadia (1980) — third-order phase transition at N = ∞, a standing warning that large-N strong-coupling expansions can hit non-analyticities in β.
- Distributional description: the 2D YM field strength is a g-valued white noise modulo gauge; the torus measure as a random distribution: Chevyrev, Comm. Math. Phys. (2019).

**Why 2D sheds no light on the 4D gap:** 2D YM is *ultralocal* — curvature correlations are delta-correlated, there are no propagating excitations, and the "mass gap" is degenerate/infinite. It is exactly the trivial scenario of Lemma 5.2 realized benignly. Its value is as a laboratory for holonomy variables, loop equations, and measure-theoretic technique, not for gap dynamics. **[ESTABLISHED + assessment]**

**Why 4D is different — three structural reasons:**

1. **Marginality.** [g²] = mass^{4−d}. In d = 2, 3 the coupling is dimensionful (super-renormalizable: finitely many divergent structures); in d = 4 it is dimensionless and runs logarithmically — control is needed over *infinitely many* RG scales simultaneously. **[ESTABLISHED power counting]**
2. **The marginal case can be fatal.** The other famous 4D marginal theory is now a *triviality theorem*: scaling limits of critical 4D Ising/φ⁴₄ are Gaussian (Aizenman–Duminil-Copin, Ann. of Math. 194 (2021) 163–235) **[ESTABLISHED]**. Yang–Mills is expected to escape triviality *only* because its beta function has the opposite sign (asymptotic freedom) — an expectation, not a theorem, at the nonperturbative level. **[PHYSICS-LEVEL]**
3. **No ferromagnetic toolbox.** The scalar successes leaned on Griffiths/FKG-type correlation inequalities, Gaussian domination, and positive-weight polymer duals. All are missing non-abelian (§5.2).

### 3.2 Lattice Yang–Mills: Wilson action, reflection positivity, continuum limit (lane 06-03)

Setup used throughout: for ε > 0, torus Λ_{ε,L} = (εℤ/Lℤ)⁴ (or ℤ^d in lattice units), edge variables U_e ∈ G (compact, fixed faithful unitary representation), plaquette holonomy U_p, Wilson action and Gibbs measure

μ_{ε,L,β}(dU) ∝ exp( β Σ_p Re tr U_p ) Π_e dU_e ,  β = 2N/g₀² for SU(N).

- Definition and gauge invariance exact at the cutoff: Wilson, Phys. Rev. D 10 (1974) 2445. Hamiltonian version: Kogut–Susskind, Phys. Rev. D 11 (1975) 395. **[ESTABLISHED]**
- **Reflection positivity** for the Wilson (and heat-kernel/Villain) action, for site and link reflections: Osterwalder–Seiler, "Gauge field theories on a lattice," Ann. Phys. 110 (1978) 440–471. Strictly positive self-adjoint transfer matrix: Lüscher, Comm. Math. Phys. 54 (1977) 283. Consequence: a well-defined lattice Hamiltonian and OS-type reconstruction *at every fixed ε* — the lattice theory "exists" in the Clay sense except for the continuum limit. **[ESTABLISHED]**
- Infinite-volume limit: subsequential limits always exist (compact spins); unique Gibbs state and exponential clustering at strong coupling via convergent cluster/character expansion (Osterwalder–Seiler; Seiler, *Gauge Theories as a Problem of Constructive Quantum Field Theory and Statistical Mechanics*, Lect. Notes Phys. 159, Springer, 1982). **[ESTABLISHED]**
- **Continuum limit in d = 4: open.** Rigorous multiscale programs:
  - Balaban's RG program: ultraviolet stability bounds for 3D/4D lattice YM through renormalization steps, small-field analysis plus large-field control (e.g. Comm. Math. Phys. 102 (1985) 255; 119 (1988) 243–285; 122 (1989) 175–202 and 355–392, and the surrounding series). Controls free-energy-type quantities in finite volume; was **not** pushed to correlation functions / continuum Schwinger functions. **[PARTIAL]**
  - Federbush's phase-cell program (Comm. Math. Phys. 107 (1986) 319; J. Math. Phys. 28 (1987) 1416; Comm. Math. Phys. 110 (1987) 293; 114 (1988) 317; 127 (1990) 433; Ann. IHP 47 (1987) 17). Incomplete. **[PARTIAL]**
  - Magnen–Rivasseau–Sénéor, "Construction of YM₄ with an infrared cutoff," Comm. Math. Phys. 155 (1993) 325–383: a phase-space expansion asserting UV control in finite volume. Published, but the program stopped there and the community consensus (cf. Douglas 2004; Chatterjee's 2019 survey) is that even finite-volume 4D existence is **not** settled. **[PARTIAL/DISPUTED completeness]**
  - Abelian continuum limits *are* theorems: U(1)₃ (Gross, Comm. Math. Phys. 92 (1983) 137), U(1)₄ (Driver, Comm. Math. Phys. 110 (1987) 479); abelian Higgs₂,₃ (Brydges–Fröhlich–Seiler, Ann. Phys. 121 (1979) 227; Comm. Math. Phys. 71 (1980) 159; 79 (1981) 353; King, Comm. Math. Phys. 102 (1986) 649 and 103 (1986) 323). **[ESTABLISHED]**

### 3.3 Mass gap on the lattice: exactly what is proved (lane 06-04)

**Theorems (verified):**

1. **Strong coupling, any d ≥ 2, any compact G:** for β < β₀(d, G), unique Gibbs state, exponential clustering (lattice mass gap m_lat(β) > 0), and Wilson-loop area law, via convergent cluster/character expansions. Osterwalder–Seiler (1978); Seiler (1982); Glimm–Jaffe (1987) for the expansion technology. **[ESTABLISHED]** Note m_lat is O(1) in *lattice* units there (correlation length ξ(β) = 1/m_lat(β) stays bounded — indeed small — at strong coupling); see Lemma 5.2 for why this does not touch the Clay problem.
2. **Göpfert–Mack:** 3D U(1) lattice gauge theory (Villain form) confines and has a strictly positive mass gap for **all** couplings, with the gap exponentially small (∼ e^{−cβ}) at weak coupling — proved via the exact monopole-plasma (Coulomb-gas / sine-Gordon) dual representation. Comm. Math. Phys. 82 (1982) 545–606. **[ESTABLISHED]** This is, to date, the only nonperturbative weak-coupling mass-gap theorem in any gauge theory in any dimension.
3. **4D U(1) has a massless phase:** at large β, 4D compact U(1) LGT deconfines (Guth, Phys. Rev. D 21 (1980) 2291) and exhibits massless Coulomb behavior (Fröhlich–Spencer, Comm. Math. Phys. 83 (1982) 411–454). **[ESTABLISHED]** — the pillar of the Abelian Falsifier (Lemma 5.4).
4. **Chatterjee's confinement criterion:** if G ⊂ U(n) is compact and connected with an element g₀ of its center acting as c·I ≠ I in the source representation, and the theory has a **strong mass gap** (exponential decay of local correlations with constants uniform over *all* boundary conditions), then rectangular Wilson loops obey |⟨W_ℓ⟩| ≤ C₁ e^{−C₂ · area(ℓ)} and the infinite-volume Gibbs state is unique. Chatterjee, "A probabilistic mechanism for quark confinement," Comm. Math. Phys. 385 (2021) 1007–1039. **[ESTABLISHED]** Direction: (strong) gap ⇒ confinement, conditionally on center symmetry; a rigorous one-way version of 't Hooft's 1978 lore. Note his "strong mass gap" is strictly stronger than spectral mass gap — the boundary-condition uniformity is essential and often not spelled out in physics literature.
5. **Strong-coupling structure theory:** exact large-N strong-coupling solution and 1/N expansion for SO(N)/SU(N) lattice theories via rigorous Makeenko–Migdal-type loop equations: Chatterjee, Comm. Math. Phys. 366 (2019) 203–268; Chatterjee–Jafarov (arXiv:1604.04777); Jafarov (arXiv:1610.03821); Basu–Ganguly (CPAM). Weak-coupling Wilson loop asymptotics for finite gauge groups in 4D: Chatterjee, Comm. Math. Phys. 377 (2020) 307–340 (ℤ₂); Cao (2020, finite groups); Forsström–Lenells–Viklund (2020+, finite abelian). **[ESTABLISHED]**
6. **Functional-inequality gap at strong coupling:** log-Sobolev/Poincaré inequalities, exponential ergodicity of the lattice Langevin dynamic, uniqueness of the infinite-volume measure, large-N factorization, and a positive lattice mass gap, for explicit strong-coupling thresholds of order 1/(d−1), any d: Shen–Zhu–Zhu, "A stochastic analysis approach to lattice Yang–Mills at strong coupling" (Comm. Math. Phys., 2023). **[ESTABLISHED, strong coupling only]**
7. **Free energy:** the leading term of the lattice Yang–Mills free energy in the weak-coupling (continuum-scaling) regime: Chatterjee, J. Funct. Anal. 271 (2016) 2944–3005 — the first quantitative rigorous statement *at* weak coupling for a non-abelian lattice theory in 4D. **[ESTABLISHED]**
8. **Continuum-flavored 3D objects:** state space of distributional gauge orbits for 3D Euclidean YM via the YM heat flow, with regularized Wilson loops, *conditional on GFF-like ultraviolet behavior*: Cao–Chatterjee, Comm. Math. Phys. 405 (2024) 3 (arXiv:2111.12813) and companion heat-flow paper ("The Yang–Mills heat flow with random distributional initial data"). **[ESTABLISHED as conditional construction]** Stochastic quantisation: gauge-covariant renormalized Langevin dynamics and a Markov process on gauge orbits — 2D: Chandra–Chevyrev–Hairer–Shen, Publ. Math. IHÉS 136 (2022) 1–147; 3D (YM–Higgs): Chandra–Chevyrev–Hairer–Shen, Invent. Math. (2024), arXiv:2201.03487; 2D invariance/universality developments: Chevyrev–Shen (2023). **[ESTABLISHED: local-in-time / dynamic-level; measure-level 3D existence still OPEN]**

**Claims that are not (accepted) theorems:**

- **Tomboulis:** claimed proof that 4D SU(2) LGT confines for all β via Migdal–Kadanoff-type decimation bounds plus an interpolation argument (Phys. Rev. Lett. 50 (1983) 885; arXiv:0707.2179). Ito–Seiler identified an unproven step (existence of the interpolation/twist parameter with the required properties); the claim remains unresolved and is not accepted as a theorem (Ito–Seiler, arXiv:0803.3019, and the surrounding exchange). **[DISPUTED]** See Lemma 5.4 for why the disputed step is exactly where non-abelian information must enter.
- All statements of the form "4D SU(N) has a gap at all β": **[OPEN]**, believed true. **[PHYSICS-LEVEL + NUMERICAL]**

---

## 4. Why Standard Physics Arguments Do Not Constitute a Proof

### 4.1 Instantons, θ-vacua, topology (lane 06-05)

Facts and their limits:

- Self-dual solutions with instanton number Q ∈ ℤ = π₃(G) exist (Belavin–Polyakov–Schwarz–Tyupkin, Phys. Lett. B 59 (1975) 85); one-loop fluctuation determinant computed ('t Hooft, Phys. Rev. D 14 (1976) 3432); θ-sectors (Callan–Dashen–Gross, Phys. Lett. B 63 (1976) 334; Jackiw–Rebbi, Phys. Rev. Lett. 37 (1976) 172). **[ESTABLISHED as classical/perturbative statements]**
- The dilute instanton gas is **not** a construction: the size-modulus integral diverges for large instantons (infrared), the gas is dense exactly where it would matter, and the semiclassical series is asymptotic. **[ESTABLISHED failure mode; the manipulation is PHYSICS-LEVEL]**
- Large-N: instanton weights e^{−8π²N/λ} vanish exponentially in N while the gap and θ-dependence are expected O(1) — instantons cannot be *the* gap mechanism (Witten, Nucl. Phys. B 149 (1979) 285; branch structure: Witten, Phys. Rev. Lett. 81 (1998) 2862). **[PHYSICS-LEVEL, influential]**
- On the lattice, topological charge is not even well-defined on all configurations: geometric definitions require local smallness of the action (Lüscher, "Topology of lattice gauge fields," Comm. Math. Phys. 85 (1982) 39). "Summing over sectors" is not a nonperturbative operation one is entitled to without a construction. **[ESTABLISHED]**

**Lane verdict:** topology constrains the *family* of theories (θ) and enriches the physics; it is not a substitute for existence, and no known topological mechanism yields a rigorous gap in 4D. For the Clay problem, the Wilson action (θ = 0) suffices.

### 4.2 BRST, gauge fixing, Gribov (lane 06-06)

- The Faddeev–Popov insertion (Phys. Lett. B 25 (1967) 29) is a formal partition of unity valid only if the gauge slice meets each orbit once, transversally. Nonperturbatively it does not: **Gribov copies** in Landau/Coulomb gauge (Gribov, Nucl. Phys. B 139 (1978) 1), and **Singer's theorem**: there is *no* continuous global gauge fixing — the bundle of connections over gauge orbits admits no global section (Singer, Comm. Math. Phys. 60 (1978) 7–12). **[ESTABLISHED]**
- Consequently the gauge-fixed continuum functional integral with FP determinant is not the definition of a measure; BRST symmetry (Becchi–Rouet–Stora, Ann. Phys. 98 (1976) 287; Tyutin 1975) and its cohomology define the physical state space *order by order in formal power series* only. On the lattice, naive BRST localization produces the Neuberger 0/0 problem (Neuberger, Phys. Lett. B, 1986–87). Gribov–Zwanziger horizon restrictions are **[PHYSICS-LEVEL]** with unresolved positivity issues.
- The rigorous route sidesteps all of this: with a compact group one integrates over *all* gauge fields with Haar measure — no gauge fixing is needed, and the observable algebra is the gauge-invariant one. **[ESTABLISHED]**

**Lane verdict + no-go pointer:** perturbative BRST quantization can never decide the Clay problem, not merely for rigor-hygiene reasons but structurally: the gap is invisible at every finite order (Observation 5.5).

### 4.3 Clay "existence" vs physicists' confinement and glueball mass (lane 06-09)

Four logically distinct properties of pure YM:

- (E) axiomatic existence; (Δ) mass gap; (C) confinement of static fundamental sources (Wilson-loop area law / linear potential); (S) realization of center symmetry.

The Clay problem is (E) + (Δ). It does **not** ask for (C). Relations, honestly labeled:

- (Δ) does not imply (C) in general; theories with gap and center symmetry can still be deconfining (this necessitates Chatterjee's *strong* gap hypothesis — his theorem gives (strong Δ) + (S) ⇒ (C) rigorously **[ESTABLISHED]**). Conversely (C) at strong coupling coexists with a gap, but neither implication is generic.
- The physicists' "mass gap" is the lightest glueball; lattice QCD numerics give m(0⁺⁺) ≈ 1.5–1.7 GeV for SU(3) (Morningstar–Peardon, Phys. Rev. D 60 (1999) 034509) **[NUMERICAL]** — overwhelming evidence, zero axiomatically-acceptable proof content.
- Proposed physical mechanisms — dual superconductivity, center vortices, Gribov–Zwanziger scenario — are **[PHYSICS-LEVEL]**; none has a rigorous 4D version.

**Lane verdict:** solving "confinement" as physicists mean it would not automatically win the prize (existence would still be missing), and a Clay solution need not decide confinement (though by Chatterjee's criterion a sufficiently uniform gap proof would likely deliver it too — see §5.3, Synthesis).

---

## 5. Deliverables: Interface Lemma, No-Go Package, Named Targets

Standing notation as in §3.2; d = 4, G compact simple unless stated. "Local gauge-invariant observable" = gauge-invariant function of edge variables in a bounded window (e.g. tr U_p, small Wilson loops). ⟨F; G⟩ = ⟨FG⟩ − ⟨F⟩⟨G⟩. Lattice mass gap m_lat(β) = sup{m : |⟨F; τ_n G⟩| ≤ C_{F,G} e^{−m|n|} for all local F, G}; correlation length ξ(β) = 1/m_lat(β).

### 5.1 The Interface Lemma (mission deliverable (b)) — the missing analytic step, formulated cleanly

**Lemma 5.1 (Gap-Transfer / Interface Lemma). [FOLKLORE, MADE PRECISE — conclusion standard given hypotheses; all novelty resides in the hypotheses being open]**

Let ε_k ↓ 0, L_k → ∞, and let β_k = β(ε_k) be any bare-coupling sequence. Let μ_k := μ_{ε_k, L_k, β_k} be the Wilson-action measures. Fix a family 𝒜 of local gauge-invariant observables at *physical* scale: for smooth compactly supported f and a template observable Φ, set Φ_k(f) := Z_Φ(ε_k) Σ_x ε_k⁴ f(x) Φ_x^{(k)}, with a renormalization constant Z_Φ(ε) at our disposal. Define lattice Schwinger functions S_k^{(n)}. Assume:

- **(H0) [holds automatically — ESTABLISHED]** Each μ_k is reflection positive for lattice hyperplane reflections and invariant under lattice translations and hypercubic symmetries (Osterwalder–Seiler; Lüscher).
- **(H1) Convergence + temperedness [OPEN].** For every n and test functions, S_k^{(n)}(f₁, …, f_n) converges as k → ∞ to limits S^{(n)}, with growth bounds uniform in k of OS-reconstruction strength: |S_k^{(n)}(f₁,…,f_n)| ≤ C^n (n!)^c Π_i ‖f_i‖_s for some Schwartz norm ‖·‖_s and constants independent of k (the linear-growth-type condition needed for OS reconstruction).
- **(H2) Uniform exponential clustering [OPEN — the core of the Clay problem].** There exists m₀ > 0 such that for all F, G ∈ 𝒜 there is C_{F,G} < ∞ with
  sup_k |⟨F; τ_x G⟩_{μ_k}| ≤ C_{F,G} e^{−m₀|x|} for all physical translations x with |x| ≥ r₀,
  where |x| is the Euclidean norm (in particular the bound holds in the Euclidean-time direction).
- **(H3) Symmetry restoration [OPEN].** The limits S^{(n)} are invariant under the full Euclidean group E(4).
- **(H4) Nontriviality and identification [OPEN].** Some truncated four-point function of 𝒜 is nonzero in the limit, and the short-distance behavior of the two-point function of the (renormalized) tr F² observable matches asymptotically free perturbative Yang–Mills for the given G to leading logarithmic order.

**Conclusion.** The family {S^{(n)}} satisfies the OS axioms (temperedness with the stated growth, Euclidean covariance, reflection positivity for all hyperplanes, symmetry, clustering). OS reconstruction yields a Hilbert space ℋ, a positive-energy unitary representation of the Poincaré group, local field operators for 𝒜, and a unique Poincaré-invariant vacuum Ω with

spec(H) ⊆ {0} ∪ [m₀, ∞),

i.e. a Wightman theory of the gauge-invariant local algebra, non-trivial and identified as Yang–Mills by (H4), with mass gap Δ ≥ m₀. That is: **(H1)–(H4) ⇒ the Clay problem for G.**

*Proof sketch (all steps standard).* Reflection positivity is a family of inequalities among Schwinger functions, hence stable under the pointwise limits of (H1); with (H3) one upgrades lattice-hyperplane RP to RP for all hyperplanes. (H1)'s uniform growth gives the OS temperedness/linear-growth condition, so OS reconstruction (Osterwalder–Schrader I–II) applies. (H2) passes to the limit and, read in the Euclidean-time direction, gives |⟨AΩ, e^{−tH}BΩ⟩ − ⟨AΩ,Ω⟩⟨Ω,BΩ⟩| ≤ Ce^{−m₀ t} on the cyclic domain; the spectral theorem excludes spectrum in (0, m₀) and gives vacuum uniqueness. (H4) rules out the degenerate satisfiers (generalized free / ultralocal limits). ∎

**Remark 5.1.1 (what this buys).** Nothing in the conclusion is new; the value is the *interface*: the Clay problem is equivalent to producing lattice estimates (H1)–(H4) uniformly along **some** trajectory (ε_k, β_k). All known physics says the only viable trajectory is the asymptotically free one, β(ε) → ∞ logarithmically tied to ε via the two-loop lattice Λ-parameter, a·Λ_lat = e^{−1/(2b₀ g₀²)} (b₀ g₀²)^{−b₁/(2b₀²)} (1 + O(g₀²)), b₀ = 11N/48π². **[PHYSICS-LEVEL trajectory; the lemma itself is trajectory-agnostic]**

**Remark 5.1.2 (existence and gap are one problem).** In this formulation there is no "first existence, then gap": the same hypothesis (H2) that yields the gap is what tames the infinite-volume/continuum limits enough to give a clustering, unique-vacuum theory. On the only known route, the two halves of the prize are proved by the same uniform estimate, or not at all. **[SYNTHESIS-level observation]**

### 5.2 The no-go package (mission deliverable (c))

**Lemma 5.2 (Fixed-coupling scaling limits are ultralocal). [FOLKLORE, MADE PRECISE; components ESTABLISHED]**

Let d ≥ 2, G compact, and suppose sup_k β_k =: β̄ < β₀(d, G), the strong-coupling threshold of the convergent Osterwalder–Seiler expansion. Then there is ξ̄ = ξ(β̄) < ∞ (lattice units) such that for all local gauge-invariant F, G:

|⟨F; τ_x G⟩_{μ_k}| ≤ C_{F,G} e^{−|x| / (ε_k ξ̄)} (x = physical separation).

Consequently:

(a) *Superpolynomial decoupling.* For fixed physical x ≠ 0 the truncated correlations vanish faster than any power of ε_k. Moreover, for two separations 0 < |x′| < |x| the *normalization-independent* ratio obeys ⟨F; τ_x F⟩ / ⟨F; τ_{x′} F⟩ = O(e^{−(|x|−|x′|)/(ε_k ξ̄)}) → 0; hence no choice of Z_Φ(ε) yields a limit two-point function finite and nonvanishing at two distinct separations. Any subsequential scaling limit has Schwinger functions supported on coincident points: it is **ultralocal** (no propagating excitations; every candidate "gap" is +∞).

(b) *Physical gap divergence.* The physical gap of μ_k is Δ_k ≥ m_lat(β̄)/ε_k → ∞.

(c) *No continuum theory with 0 < Δ < ∞ arises at fixed strong coupling.* More generally, if ξ(β) < ∞ on a neighborhood of the limit points of (β_k), the same conclusion holds; a finite nonzero physical gap **forces** ε_k ξ(β_k) → Δ^{−1} ∈ (0, ∞), i.e. ξ(β_k) → ∞: the bare couplings must approach a point of divergent lattice correlation length.

*Proof.* The exponential bound is the O-S cluster expansion **[ESTABLISHED]**; (a)–(c) are arithmetic. ∎

**Corollary 5.3 (What any complete proof must quantify). [FOLKLORE, MADE PRECISE]**
Under the standard conjecture (unproven) that for non-abelian G in d = 4, ξ(β) < ∞ for every finite β, any Clay-compliant continuum limit requires β_k → ∞ with ξ(β_k) = 1/(Δ ε_k) exactly calibrated. The gap *alone* does not fix the divergence rate of ξ(β) — any divergence can be absorbed into the definition of ε(β). What fixes the rate is hypothesis (H4): matching the short-distance side to asymptotic freedom with a finite Λ-parameter pins ξ(β) = exp( (12π²/(11N²)) β (1 + o(1)) ) for SU(N). Hence a complete proof must deliver **two-sided** bounds of this exponential order on the lattice correlation length as β → ∞: the lower bound on ξ (correlations survive) is the existence half, the upper bound on ξ at the calibrated scale (correlations die at rate Δ) is the gap half. **No known expansion can do either:** the strong-coupling expansion has a finite radius and lives where ξ is bounded; weak-coupling perturbation theory is asymptotic, gauge-fixed, and gapless at every order (Observation 5.5).

**No-go reading of 5.2 + 5.3:** the common manipulation "strong-coupling confinement/gap theorems + believed absence of a deconfining transition ⇒ continuum gap" is invalid *even granting the absence of phase transitions*. The theorems at fixed β control a regime whose continuum shadow is ultralocal and empty; all Clay content lives in the uncontrolled asymptotics ξ(β → ∞).

**Lemma 5.4 (Abelian falsifier). [components ESTABLISHED — Guth 1980, Fröhlich–Spencer 1982; framing sharpened here]**

Let d = 4. Let P be any set of hypotheses about a lattice gauge model (G compact, RP action, β ∈ (0, ∞)) which suffices to conclude "m_lat(β) > 0 for all β" or "Wilson-loop area law for all β." If G = U(1) (Wilson or Villain action) satisfies P, then P is inconsistent: 4D compact U(1) at large β has a deconfined, *massless* Coulomb phase.

*Consequences.*
- Any valid non-abelian gap/confinement proof must consume, quantitatively and essentially, a property that U(1) lacks — e.g. the sign of the beta function / non-commutativity of holonomies / structure of non-abelian character expansions. Compactness, reflection positivity, nontrivial center, strong-coupling bounds, and Migdal–Kadanoff-type decimation inequalities are all shared with U(1) and hence *individually and jointly insufficient*.
- Applied to the Tomboulis program **[DISPUTED]**: the MK decimation inequalities themselves hold for U(1) as well; his scheme's distinction between U(1) and SU(2) is carried entirely by the unproven interpolation-parameter step flagged by Ito–Seiler. The falsifier does not refute the program; it *proves* that the disputed step is not a technicality but the entire mathematical content. This is a precise localization of the burden of proof.
- The same test disqualifies, wholesale, heuristics of the form "compact group + RP + strong coupling extends by continuity."

**Observation 5.5 (Perturbative invisibility of the gap; BRST no-go). [conditional on RG identification (H4); the per-order gaplessness of massless-YM perturbation theory is unconditional]**

Suppose a Clay-compliant family exists along the trajectory of Corollary 5.3, with physical gap Δ = c_G Λ, Λ the (finite, nonzero) lattice Λ-parameter. Then, as a function of the bare coupling g² at fixed cutoff, Δ(g²) = O( e^{−24π²/(11N g²)} · poly(g²) ), so **every g-derivative of Δ at g = 0 vanishes**: the Taylor/asymptotic series of the mass gap in the coupling is identically zero. Therefore:

1. No construction whose output is a formal power series in g — renormalized perturbation theory, perturbative BRST cohomology, any diagrammatic resummation with finitely many controlled orders — can establish (or even *state*) Δ > 0. The infrared divergences of massless-gluon perturbation theory at each order are the visible symptom of expanding a function with an essential singularity at g = 0.
2. Combined with Gribov–Singer (§4.2), "physics quantization" fails the Clay problem twice over: the gauge-fixed continuum integral is globally ill-defined **[ESTABLISHED]**, and even its perturbative shadow is structurally blind to the gap **[conditional as stated]**.

### 5.3 Named open targets on lattice and low-dimensional analogues (mission deliverable (a) — targets, honestly labeled [OPEN]/[SPECULATIVE])

- **T1 (Crossover lemma — the named gap of §6).** Exhibit β* > β₀(4, G) and one rigorous RG blocking step ℛ (scale factor 2, with explicit large-field control) such that for all β ∈ [β₀, β*], ℛ maps the Wilson theory into the Banach space of polymer activities where the Osterwalder–Seiler expansion converges with effective coupling below threshold. Even a fixed *ε-improvement* of the strong-coupling region (β* = β₀ + δ, explicit δ > 0, via one decimation) is unproven and would be genuine progress. **[OPEN]**
- **T2 (Non-abelian correlation inequality).** Prove (or disprove) that ⟨W_γ⟩ is monotone in β for 4D SU(2) Wilson action. The abelian analogue follows from Ginibre's inequalities (Comm. Math. Phys. 16 (1970) 310) **[ESTABLISHED abelian]**; *no* Griffiths-type inequality is known for any non-abelian G — a scandalously elementary-sounding open problem whose resolution would give the first order-theoretic grip on the phase diagram. Obstruction: the dual/character expansion has sign-indefinite recoupling (6j-symbol) weights, so all positivity-based tools (Peierls, FKG, duality-to-positive-polymer-gas à la Göpfert–Mack) fail at the first step. **[OPEN; obstruction ESTABLISHED folklore]**
- **T3 (Göpfert–Mack analogue in 3D SU(2)).** Prove m_lat(β) > 0 for all β for 3D SU(2) LGT — the exact non-abelian counterpart of the only known weak-coupling gauge-theory gap theorem (Göpfert–Mack, 3D U(1)). The 3D theory is super-renormalizable (gap expected ∼ c g², no log running), the UV side has rigorous beachheads (Balaban stability; Cao–Chatterjee state space; CCHS dynamics), and Feynman's and Karabali–Nair's **[PHYSICS-LEVEL]** analyses supply mechanism candidates. Missing: any non-abelian replacement for the monopole-plasma positive-weight dual. In this legion's judgment this is the most plausible "next theorem" in the entire subject and the correct venue for a lattice-analogue breakthrough. **[OPEN; assessment SPECULATIVE]**
- **T4 (Uniform strong-gap ⇒ continuum program).** Quantify Chatterjee's strong-mass-gap hypothesis in physical units: show that if (H2) of Lemma 5.1 holds *uniformly over boundary conditions* with physically-scaled constants, then his confinement theorem survives the ε → 0 limit with finite string tension σ > 0 — which would simultaneously deliver the nontriviality clause (H4)-part (a perimeter-law/Gaussian theory cannot have σ > 0). Caveat honestly noted: his constants C₁, C₂ depend on (G, β, d) and must be tracked through the scaling; this has not been done. **[SYNTHESIS direction; OPEN]**

---

## 6. Anatomy of a Complete Proof, and the Single Named Gap (lanes 06-07, 06-10)

The dimensional ladder that frames the plan **[ESTABLISHED power counting; statuses as marked]:**

| d | coupling dimension | UV | IR/gap | status |
|---|---|---|---|---|
| 2 | mass² | trivial (exact decimation) | ultralocal, no propagating modes | solved, degenerate |
| 3 | mass¹ | super-renormalizable; Balaban stability, CCHS local dynamics, Cao–Chatterjee (conditional) | gap expected ∼ c g²; proved only for U(1) (Göpfert–Mack) | UV: partial theorems; gap: OPEN (target T3) |
| 4 | marginal | log running over all scales; Balaban/Federbush/MRS partial | gap expected ∼ Λ e-form, nonperturbative | fully OPEN |

**Steps a complete 4D proof must contain** (each with current status):

- **S0. Regularize.** Wilson (or heat-kernel) LGT on a torus: RP, positive transfer matrix, exact gauge invariance. **[DONE — Wilson 1974; Osterwalder–Seiler 1978; Lüscher 1977]**
- **S1. Choose the bare trajectory.** β(ε) tied to ε through the two-loop lattice Λ-parameter (asymptotic freedom), with Λ the free scale. **[DEFINED; the choice is canonical [PHYSICS-LEVEL], the lemma-level framework (5.1) is trajectory-agnostic]**
- **S2. UV control.** Run a rigorous RG from scale ε up to a fixed physical scale ℓ₀ ≪ Λ⁻¹: prove the effective actions stay in a controlled neighborhood of the perturbative trajectory, *including large-field regions*, with bounds strong enough to control gauge-invariant correlation functions (not only the free energy). **[PARTIAL — Balaban's stability bounds and large-field renormalization are the deepest existing mathematics here, but stop short of correlations; Federbush incomplete; MRS contested]**
- **S3. Crossover (THE GAP).** Continue the RG from ℓ₀ to ∼ Λ⁻¹, where the running coupling leaves the perturbative regime, and prove the flow **lands in the convergent strong-coupling region** β_eff < β₀ with controlled errors. Equivalently (either suffices):
  - (i) prove target T1 (a rigorous decimation step bridging [β₀, β*] and iterable down the trajectory), or
  - (ii) prove m_lat(β) > 0 for all β with the two-sided exponential asymptotics of Corollary 5.3.
  **No theorem, no candidate technique, and no nontrivial special case of this step exists. [OPEN]** This is the precisely-named missing analytic step: *uniform-in-ε exponential clustering (H2) along the asymptotically free trajectory, equivalently rigorous passage of the RG from the Balaban regime to the Osterwalder–Seiler regime.* Every other step below is standard or reduces to existing technology once S3 is granted.
- **S4. IR conclusion.** Inside the strong-coupling region, the convergent cluster expansion yields exponential clustering with physical rate m₀ ∼ c Λ, uniformly. **[ESTABLISHED given S3]**
- **S5. Limits.** Tightness and convergence of Schwinger functions (H1), restoration of E(4) invariance (H3) from lattice symmetries plus uniform continuity estimates. **[OPEN, but expected to follow from S2–S4 technology; analogous steps were carried out in every completed low-dimensional construction]**
- **S6. Reconstruction.** Lemma 5.1: OS axioms, Wightman theory, unique vacuum, Δ ≥ m₀. **[ESTABLISHED given S1–S5]**
- **S7. Identification and nontriviality (H4).** Short-distance matching to asymptotically free perturbation theory (reduces to S2 estimates); nontriviality via σ > 0 (Chatterjee's criterion, target T4) or a surviving connected 4-point function. **[OPEN; subordinate to S2–S3]**
- **S8. All compact simple G.** The Clay statement quantifies over G; S2–S4 machinery is expected to be G-uniform in structure, but every constant must be tracked. **[OPEN, routine-conditional]**

**Alternative programs and their own named gaps** (none evades S3; each relocates it):

- *Stochastic quantisation* (CCHS 2D/3D): missing 3D global well-posedness, uniqueness/existence of the invariant measure, and any gap statement. **[OPEN]**
- *Heat-flow state space* (Cao–Chatterjee 3D): conditional on GFF-like UV behavior of the measure — which is a form of S2. **[OPEN]**
- *Large-N / master field in 4D*: rigorous Makeenko–Migdal control exists only at strong coupling (Lemma 5.2 applies) or in 2D. **[OPEN]**

---

## 7. Lane Audit, Honesty Statement, References

### 7.1 Lane-by-lane verdicts

| Lane | Deliverable produced | Verdict |
|------|---------------------|---------|
| 06-01 | Precise Clay statement; gap ⇔ clustering equivalence with correct two-sided citations | known |
| 06-02 | Survey with verified citations; "why 4D differs" sharpened via the φ⁴₄ triviality contrast | known |
| 06-03 | RP/transfer-matrix status; honest grading of Balaban/Federbush/MRS | known |
| 06-04 | Complete verified inventory of lattice gap/confinement *theorems*, including 2019–2024 results | known (inventory has current-literature value) |
| 06-05 | Instanton/θ no-substitute analysis; lattice-topology caveat | known |
| 06-06 | Gribov–Singer + Neuberger no-go chain; feeds Observation 5.5 | known |
| 06-07 | Dimensional ladder; 3D named as the realistic breakthrough venue (T3) | incremental (assessment) |
| 06-08 | Sign-indefinite recoupling obstruction; T2 (non-abelian correlation inequality) named as elementary-sounding open lemma | incremental (target-naming) |
| 06-09 | Four-property disentanglement (E/Δ/C/S); Chatterjee criterion placed exactly | known |
| 06-10 | Roadmap S0–S8 with single named gap (S3 = T1 = uniform (H2)) | **primary deliverable, tier (b)** |

### 7.2 Honesty statement

- **No theorem in this report is new.** Lemmas 5.1–5.4 and Observation 5.5 are precise assemblies of published results; their proofs are standard given the cited components. Their value — if any — is architectural: a single interface (H1)–(H4), a no-go package that invalidates the three most common shortcut arguments (strong-coupling extrapolation, abelian-blind RG bounds, perturbative/BRST constructions), and a localization of the entire problem into step S3.
- **Mission tier achieved:** (b) clean formulation of the missing analytic step — yes (Lemma 5.1 + Corollary 5.3 + S3); (c) no-go for common formal manipulations — yes (Lemmas 5.2, 5.4; Observation 5.5), with the caveat that these formalize expert folklore rather than overturn any published theorem; (a) new lattice/low-dimensional lemma — **not achieved**; in its place, precisely posed targets T1–T4 with obstructions named.
- **No candidate breakthrough is claimed. The Yang–Mills existence and mass gap problem remains fully open.**
- All citations below were verified against live sources or against the bibliography of Chatterjee's survey during this run; where a detail (volume/venue) could not be verified, the entry is given as author–title–year only. No citation is invented.

### 7.3 References (verified)

**Problem statement and status.**
- A. Jaffe, E. Witten, "Quantum Yang–Mills theory," in *The Millennium Prize Problems*, Clay Math. Inst./AMS (2006), 129–152.
- M. Douglas, "Report on the status of the Yang–Mills Millennium Prize problem," Clay Math. Inst. (2004).
- R. Streater, A. Wightman, *PCT, Spin and Statistics, and All That* (1964).
- K. Osterwalder, R. Schrader, Comm. Math. Phys. 31 (1973) 83–112; Comm. Math. Phys. 42 (1975) 281–305.
- K. Fredenhagen, "A remark on the cluster theorem," Comm. Math. Phys. 97 (1985) 461.

**Lattice foundations.**
- K. Wilson, Phys. Rev. D 10 (1974) 2445. — J. Kogut, L. Susskind, Phys. Rev. D 11 (1975) 395.
- K. Osterwalder, E. Seiler, "Gauge field theories on a lattice," Ann. Phys. 110 (1978) 440–471.
- M. Lüscher, Comm. Math. Phys. 54 (1977) 283 (positive transfer matrix); Comm. Math. Phys. 85 (1982) 39 (lattice topology).
- E. Seiler, *Gauge Theories as a Problem of Constructive QFT and Statistical Mechanics*, Lect. Notes Phys. 159, Springer (1982).
- J. Glimm, A. Jaffe, *Quantum Physics: A Functional Integral Point of View*, 2nd ed., Springer (1987).

**Constructive QFT successes and triviality.**
- J. Glimm, A. Jaffe, T. Spencer, Ann. of Math. 100 (1974) 585–632. — B. Simon, *The P(φ)₂ Euclidean (Quantum) Field Theory* (1974).
- J. Feldman, K. Osterwalder, Ann. Phys. 97 (1976) 80–135.
- M. Hairer, Invent. Math. 198 (2014) 269–504.
- M. Aizenman, H. Duminil-Copin, Ann. of Math. 194 (2021) 163–235.

**2D Yang–Mills.**
- A. Migdal (1975), recursion equations (JETP). — D. Gross, E. Witten, Phys. Rev. D 21 (1980) 446; S. Wadia (1980).
- B. Driver, Comm. Math. Phys. 123 (1989) 575–616; L. Gross, C. King, A. Sengupta, Ann. Phys. 194 (1989) 65–112; D. Fine, Comm. Math. Phys. 134 (1990) 273 and 140 (1991) 321; S. Klimek, W. Kondracki, Comm. Math. Phys. 113 (1987) 389.
- A. Sengupta, Mem. AMS 126 (1997) no. 600. — T. Lévy, Mem. AMS 166 (2003) no. 790; Astérisque 329 (2010); "The master field on the plane," arXiv:1112.2452.
- E. Witten, Comm. Math. Phys. 141 (1991) 153–209.
- Y. Makeenko, A. Migdal, Phys. Lett. B 88 (1979) 135. — B. Driver, B. Hall, T. Kemp, arXiv:1601.06283; B. Driver, F. Gabriel, B. Hall, T. Kemp, arXiv:1602.03905.
- I. Chevyrev, "Yang–Mills measure on the two-dimensional torus as a random distribution," Comm. Math. Phys. (2019).

**Multiscale/RG programs (4D and 3D UV).**
- T. Balaban, Comm. Math. Phys. 102 (1985) 255; 119 (1988) 243–285; 122 (1989) 175–202; 122 (1989) 355–392 (and the surrounding CMP series, 1984–1989).
- P. Federbush, Comm. Math. Phys. 107 (1986) 319; J. Math. Phys. 28 (1987) 1416; Comm. Math. Phys. 110 (1987) 293; 114 (1988) 317; 127 (1990) 433; Ann. Inst. H. Poincaré 47 (1987) 17.
- J. Magnen, V. Rivasseau, R. Sénéor, "Construction of YM₄ with an infrared cutoff," Comm. Math. Phys. 155 (1993) 325–383.

**Abelian theorems (falsifier pillars and continuum limits).**
- A. Guth, Phys. Rev. D 21 (1980) 2291. — J. Fröhlich, T. Spencer, Comm. Math. Phys. 83 (1982) 411–454.
- M. Göpfert, G. Mack, Comm. Math. Phys. 82 (1982) 545–606.
- L. Gross, Comm. Math. Phys. 92 (1983) 137 (U(1)₃). — B. Driver, Comm. Math. Phys. 110 (1987) 479 (U(1)₄).
- D. Brydges, J. Fröhlich, E. Seiler, Ann. Phys. 121 (1979) 227; Comm. Math. Phys. 71 (1980) 159; 79 (1981) 353. — C. King, Comm. Math. Phys. 102 (1986) 649; 103 (1986) 323.
- J. Ginibre, Comm. Math. Phys. 16 (1970) 310.

**Modern lattice/probabilistic results.**
- S. Chatterjee, J. Funct. Anal. 271 (2016) 2944–3005; Comm. Math. Phys. 366 (2019) 203–268; "Yang–Mills for probabilists," Springer Proc. Math. Stat. 283 (2019) 1–16; Comm. Math. Phys. 377 (2020) 307–340; "A probabilistic mechanism for quark confinement," Comm. Math. Phys. 385 (2021) 1007–1039.
- S. Chatterjee, J. Jafarov, arXiv:1604.04777. — J. Jafarov, arXiv:1610.03821. — R. Basu, S. Ganguly, Comm. Pure Appl. Math. — S. Cao (2020), Wilson loops for finite gauge groups. — M. P. Forsström, J. Lenells, F. Viklund (2020+).
- S. Cao, S. Chatterjee, "A state space for 3D Euclidean Yang–Mills theories," Comm. Math. Phys. 405 (2024) 3 (arXiv:2111.12813); companion: "The Yang–Mills heat flow with random distributional initial data."
- A. Chandra, I. Chevyrev, M. Hairer, H. Shen, Publ. Math. IHÉS 136 (2022) 1–147 (2D); "Stochastic quantisation of Yang–Mills–Higgs in 3D," Invent. Math. (2024), arXiv:2201.03487. — I. Chevyrev, J. Math. Phys. 63 (2022) (review). — I. Chevyrev, H. Shen (2023).
- H. Shen, R. Zhu, X. Zhu, "A stochastic analysis approach to lattice Yang–Mills at strong coupling," Comm. Math. Phys. (2023).
- P. A. Faria da Veiga, M. O'Carroll, R. Schor, Comm. Math. Phys. 245 (2004) 383–405.
- C. Borgs, E. Seiler, Comm. Math. Phys. 91 (1983) 329–380.

**Disputed confinement claims.**
- E. T. Tomboulis, Phys. Rev. Lett. 50 (1983) 885; arXiv:0707.2179 (2007).
- K. R. Ito, E. Seiler, "Further discussion of Tomboulis' approach to the confinement problem," arXiv:0803.3019 (2008), and the related arXiv exchange.

**Instantons, θ, gauge fixing.**
- A. Belavin, A. Polyakov, A. Schwarz, Y. Tyupkin, Phys. Lett. B 59 (1975) 85. — G. 't Hooft, Phys. Rev. D 14 (1976) 3432.
- C. Callan, R. Dashen, D. Gross, Phys. Lett. B 63 (1976) 334. — R. Jackiw, C. Rebbi, Phys. Rev. Lett. 37 (1976) 172.
- E. Witten, Nucl. Phys. B 149 (1979) 285; Phys. Rev. Lett. 81 (1998) 2862.
- L. Faddeev, V. Popov, Phys. Lett. B 25 (1967) 29. — C. Becchi, A. Rouet, R. Stora, Ann. Phys. 98 (1976) 287; I. Tyutin (1975).
- V. Gribov, Nucl. Phys. B 139 (1978) 1. — I. Singer, Comm. Math. Phys. 60 (1978) 7–12. — H. Neuberger, Phys. Lett. B (1986–87), lattice BRST 0/0.
- A. Polyakov, Nucl. Phys. B 120 (1977) 429. — G. 't Hooft (1978), phase transition toward permanent confinement, Nucl. Phys. B.

**Physics-level 3D and numerics.**
- R. Feynman, Nucl. Phys. B 188 (1981) 479. — D. Karabali, V. P. Nair (1996); D. Karabali, C. Kim, V. P. Nair (1998).
- C. Morningstar, M. Peardon, Phys. Rev. D 60 (1999) 034509.
- G. 't Hooft, Nucl. Phys. B 72 (1974) 461 (large N).

*End of LEGION 06 report.*
