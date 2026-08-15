# LEGION 05 — Navier–Stokes Existence and Smoothness (Clay Millennium Problem)

**Target.** 3D incompressible Navier–Stokes on $\mathbb{R}^3$ or $\mathbb{T}^3$: global existence and smoothness for smooth data, or a proof of finite-time breakdown.

**Method note (transparency).** The commander was instructed to spawn ten nested specialist subagents (05-01 … 05-10). The execution environment provided no subagent-spawning tool, so all ten angles were executed *inline, sequentially, by the commander itself*, with targeted literature verification (web-checked citations noted below). Nothing in this dossier depends on that logistical substitution.

**Honesty labels used throughout.**

| Label | Meaning |
|---|---|
| `[KNOWN]` | Established result in the literature; citation given. |
| `[KNOWN — proof written out here]` | Established result for which this dossier contains a complete (or complete-modulo-cited-lemma) proof, written rigorously. |
| `[SYNTHESIS]` | A conclusion assembled from known results; the assembly may not appear verbatim in the literature but contains no new mathematics. |
| `[SPECULATIVE]` | A direction or heuristic; *not* a claim. |
| `[FAILED ATTACK]` | An approach attempted during this run that did not close; the obstruction is recorded. |

**Verdict up front:** *no breakthrough on the Millennium problem*. The deliverables of this dossier are: (i) a faithful statement of the problem and the full known landscape across ten angles; (ii) three rigorously written theorems (small-data global regularity in $\dot H^{1/2}$; the Leray enstrophy blow-up rate; the $\le 1/2$-dimensionality of singular times) — all **known** results, with complete proofs written out here as the mission's "clean special-case theorem written rigorously" deliverable; (iii) a precise **no-go proposition** for energy-only methods, derived from Tao's averaged Navier–Stokes theorem; (iv) an audit of failed attacks and a constraints checklist that any successful method must satisfy.

---

## 1. Executive Summary

The Navier–Stokes Millennium problem asks whether smooth, finite-energy initial data in three dimensions always launch a globally smooth solution, or whether some smooth datum develops a singularity in finite time. After ninety years (Leray 1934 → today) the problem is open in both directions, and — unusually among the Millennium problems — there are now *theorems that explain why the standard toolkits cannot work*:

1. **Supercriticality.** Every known coercive, globally controlled quantity (energy $\|u\|_{L^2}^2$, dissipation $\int\!\!\int|\nabla u|^2$) is *supercritical* with respect to the scaling symmetry $u_\lambda(x,t)=\lambda u(\lambda x,\lambda^2 t)$: at small scales these bounds say less and less. All known regularity mechanisms (perturbative critical theory, partial regularity) live exactly at the critical scaling line and cannot cross it. `[KNOWN/SYNTHESIS]` (§3.10, §4)
2. **Energy-method no-go.** Tao (2016) constructed an *averaged* Navier–Stokes system that satisfies the same energy identity and the same abstract bilinear estimates as the true equation, yet blows up in finite time. Consequently, no proof of global regularity can succeed if its only inputs are the energy identity plus estimates insensitive to the fine structure of the nonlinearity. We state this as a precise no-go proposition. `[KNOWN + SYNTHESIS]` (§5.4)
3. **Weak-formulation no-go.** Convex integration (Buckmaster–Vicol 2019, after De Lellis–Székelyhidi and Isett) shows distributional solutions in $C_t L^2$ are wildly non-unique; with forcing, even Leray–Hopf solutions are non-unique (Albritton–Brué–Colombo 2022). Any strategy that works only with the weak formulation, without the energy *inequality* structure and more, is dead. `[KNOWN]` (§3.3)
4. **Perturbative theory is maximal.** Small-data global well-posedness holds in $BMO^{-1}$ (Koch–Tataru 2001), and the theory becomes ill-posed one notch below ($\dot B^{-1}_{\infty,\infty}$, Bourgain–Pavlović 2008). There is no room left in the perturbative direction. `[KNOWN]` (§3.4)
5. **The simplest blow-up ansatz is excluded.** Leray's backward self-similar blow-up is impossible (Nečas–Růžička–Šverák 1996; Tsai 1998), and Type I / self-similar-rate blow-up is excluded in the axisymmetric class (Chen–Strain–Tsai–Yau; Koch–Nadirashvili–Seregin–Šverák 2009). If Navier–Stokes blows up, it does so in a non-self-similar, non-Type-I way — which is also why the Euler numerics-to-proof pipeline (Luo–Hou → Chen–Hou) does not port to Navier–Stokes. `[KNOWN/SYNTHESIS]` (§3.6, §3.7)

Against that backdrop, the honest contribution of this dossier is *rigor and synthesis*, not novelty: complete proofs of the three foundational quantitative facts every attack must build on (§5), a sharpened statement of what any future proof must do differently (§4, §6), and an explicit record of three attack ideas that failed during this run and why (§6.2).

**Classification per program rubric: KNOWN / expository-synthesis. No candidate breakthrough.**

---

## 2. Precise Problem Statement

### 2.1 The equations

On $\mathbb{R}^3\times[0,\infty)$ (or $\mathbb{T}^3\times[0,\infty)$), find $u:\mathbb{R}^3\times[0,\infty)\to\mathbb{R}^3$ (velocity) and $p:\mathbb{R}^3\times[0,\infty)\to\mathbb{R}$ (pressure) with

$$
\partial_t u + (u\cdot\nabla)u = \nu\,\Delta u - \nabla p + f, \qquad
\nabla\cdot u = 0, \qquad
u(\cdot,0)=u^0,
$$

where $\nu>0$ is the kinematic viscosity and $f$ a given force.

### 2.2 The official Clay formulation `[KNOWN — Fefferman 2000, [Fef00]]`

The prize is awarded for a proof of **any one** of the following four statements:

- **(A) Existence and smoothness on $\mathbb{R}^3$.** Take $f\equiv 0$ and $u^0$ smooth, divergence-free, with $|\partial_x^\alpha u^0(x)|\le C_{\alpha K}(1+|x|)^{-K}$ for all $\alpha, K$. Then there exist smooth $u,p\in C^\infty(\mathbb{R}^3\times[0,\infty))$ solving the system with **bounded energy**: $\sup_{t\ge0}\int_{\mathbb{R}^3}|u(x,t)|^2\,dx<\infty$.
- **(B) Existence and smoothness on $\mathbb{T}^3$.** Same conclusion in the spatially periodic setting, $f\equiv 0$.
- **(C) Breakdown on $\mathbb{R}^3$.** There exist a smooth, divergence-free $u^0$ and a smooth force $f$ (both with the Schwartz-type decay bounds specified in [Fef00]) such that **no** smooth, finite-energy solution $(u,p)$ exists on all of $\mathbb{R}^3\times[0,\infty)$.
- **(D) Breakdown on $\mathbb{T}^3$.** Periodic analogue of (C).

Two structural remarks that matter for attack design `[SYNTHESIS]`:

1. Statement (A)/(B) requires *global smoothness for arbitrary* (large) smooth data. Every small-data theorem, however sharp, is strictly off-prize.
2. Statement (C)/(D) requires *non-existence of a smooth solution*, which is a genuinely different failure mode from non-uniqueness of weak solutions. In particular, the 2022 non-uniqueness of forced Leray–Hopf solutions [ABC22] does **not** satisfy (C): the constructed force is not in Clay's admissible class and the failure exhibited is non-uniqueness of weak solutions, not breakdown of a smooth one.

### 2.3 Scaling and criticality (used throughout)

If $(u,p)$ solves NS, so does $u_\lambda(x,t)=\lambda u(\lambda x,\lambda^2 t)$, $p_\lambda(x,t)=\lambda^2 p(\lambda x,\lambda^2 t)$ for every $\lambda>0$ (same $\nu$). A norm $\|\cdot\|_X$ is **critical** if $\|u_\lambda(\cdot,0)\|_X=\|u(\cdot,0)\|_X$; **subcritical** if the norm of $u_\lambda$ grows as $\lambda\to\infty$ (fine scales are penalized); **supercritical** if it shrinks. Benchmarks in 3D:

- Critical: $\dot H^{1/2}$, $L^3$, $\dot B^{-1+3/p}_{p,\infty}$ $(p<\infty)$, $BMO^{-1}$, $\dot B^{-1}_{\infty,\infty}$ (the largest).
- Supercritical: the energy $\|u\|_{L^2}$ (scales as $\lambda^{-1/2}$) and the dissipation norm $L^2_t\dot H^1_x$. These are the *only* quantities globally controlled for large data. This mismatch **is** the problem. (§3.10)

---

## 3. Known Partial Results — Ten Angle Briefs

Each brief: what is proved, what it does *not* say, and the obstruction it exposes. All content in §3 is `[KNOWN]` unless labelled otherwise; bracketed keys point to §7.

### 3.1 (05-01) Clay statement; Leray–Hopf weak solutions; suitable weak solutions

**Facts.**
- *Global weak existence* (Leray 1934 on $\mathbb{R}^3$ [Ler34]; Hopf 1951 for domains [Hop51]): for every divergence-free $u^0\in L^2$, there exists a global weak solution $u\in L^\infty_t L^2_x\cap L^2_t\dot H^1_x$ satisfying the **energy inequality**
  $\tfrac12\|u(t)\|_{L^2}^2+\nu\int_0^t\|\nabla u\|_{L^2}^2\,ds\le\tfrac12\|u^0\|_{L^2}^2.$
- *Weak–strong uniqueness* (Leray; Prodi [Pro59]; Serrin [Ser62]): while a strong solution exists, every Leray–Hopf solution with the same datum coincides with it. So the open problem is precisely whether strong solutions persist.
- *Structure theorem* (Leray): the set of singular times has Hausdorff dimension $\le 1/2$ and $u$ is smooth on an open set of times of full measure ("epochs of regularity"). Proof written out in §5.3.
- *Suitable weak solutions* (Scheffer [Sch77]; Caffarelli–Kohn–Nirenberg [CKN82]): weak solutions additionally satisfying the **local** energy inequality; these exist globally and support the partial-regularity theory of §3.5.
- *Non-uniqueness pressure from below*: distributional solutions in $C_tL^2$ (below the Leray class, without energy inequality) are non-unique [BV19]; with a designed force, even Leray–Hopf solutions are non-unique [ABC22]; Jia–Šverák gave a conditional (spectral-assumption) scenario for unforced Leray–Hopf non-uniqueness via scale-invariant data [JS14, JS15], supported by the numerics of Guillod–Šverák [GS17].

**What this does not say.** None of the non-uniqueness results touches Clay (A)–(D): they live in weak classes or use inadmissible forces. `[SYNTHESIS]`

**Obstruction exposed.** The gap between the (supercritical) class where existence is known and the (critical) class where uniqueness/regularity is known. Ninety years of work has narrowed but not closed it.

### 3.2 (05-02) Blow-up criteria: Beale–Kato–Majda, Prodi–Serrin, Escauriaza–Seregin–Šverák, and modern refinements

**Facts.** Let $u$ be a strong solution on $[0,T)$, $T<\infty$ maximal.
- *BKM* [BKM84] (stated for Euler, valid for NS): blow-up at $T$ forces $\int_0^T\|\omega(t)\|_{L^\infty}\,dt=\infty$, $\omega=\nabla\times u$. So vorticity must pile up in an $L^1_t L^\infty_x$ sense; direction-refined versions exist (Constantin–Fefferman [CF93]: blow-up requires the vorticity *direction* to lose Lipschitz coherence in high-vorticity regions).
- *Ladyzhenskaya–Prodi–Serrin family* [Pro59, Ser62]: if $u\in L^p_tL^q_x$ on $[0,T]$ with $\frac2p+\frac3q=1$, $3<q\le\infty$, then $u$ is smooth up to $T$. Gradient version (Beirão da Veiga [BdV95]): $\nabla u\in L^p_tL^q_x$, $\frac2p+\frac3q=2$. A representative proof at a subcritical point of the family is standard Grönwall; the modern strain-based refinement (only the middle eigenvalue of the strain matters, Miller [Mil20]) shows how much slack the classical proofs still leave.
- *Endpoint ESS* [ESS03]: $u\in L^\infty_tL^3_x\Rightarrow$ regular. Proved via backward uniqueness for parabolic operators — a genuinely non-energy argument.
- *Seregin's necessary condition* [Ser12]: at a finite blow-up time $T$, $\|u(t)\|_{L^3}\to\infty$ as $t\to T$ (not merely $\limsup=\infty$).
- *Critical Besov upgrade* (Gallagher–Koch–Planchon [GKP16]): critical Besov norms $\dot B^{-1+3/p}_{p,q}$, $p,q<\infty$, must blow up at a singularity (profile-decomposition proof).
- *Quantitative ESS* (Tao [Tao21], web-verified): $\|u(t)\|_{L^3}\ge\big(\log\log\log\tfrac{1}{T-t}\big)^{c}$ along a sequence $t\uparrow T$, with triple-exponential-type effective bounds throughout — the first (slightly) supercritical blow-up criterion.

**What this does not say.** All criteria are *conditional*: they convert "no blow-up" into control of a critical (or barely supercritical) norm that nobody can bound a priori. The unconditional information they yield about a hypothetical singularity is real but thin (rates in §5.2, dimension bounds in §5.3, §3.5).

**Obstruction exposed.** The entire criterion industry sits on the critical line $\frac2p+\frac3q=1$. Crossing to *any* unconditional bound would need a supercritical a priori estimate — exactly what §5.4 says energy-only methods cannot deliver. Tao's triple-log result shows the price of even an $\varepsilon$ of supercriticality: Carleman inequalities and triple-exponential losses. `[SYNTHESIS]`

### 3.3 (05-03) Onsager, energy cascade, convex integration — what it says and does not say about the Millennium problem

**Facts.**
- *Onsager's conjecture* [Ons49]: for **Euler**, weak solutions with Hölder regularity $>1/3$ conserve energy — proved by Constantin–E–Titi [CET94] (positive side); below $1/3$, dissipative wild solutions exist — Isett [Ise18], with admissible (energy-decreasing) solutions by Buckmaster–De Lellis–Székelyhidi–Vicol [BDLSV19]; foundational scheme: De Lellis–Székelyhidi [DLS09], with earlier paradoxical examples by Scheffer [Sch93] and Shnirelman [Shn97].
- *Navier–Stokes convex integration* (Buckmaster–Vicol [BV19]): distributional (mild-in-a-weak-sense) solutions with finite kinetic energy are non-unique; they lie **below** the Leray class (no energy inequality, not in $L^2_t\dot H^1_x$). Sharper thresholds by Cheskidov–Luo [CL22].
- These constructions implement, at the level of *pathological solutions*, the physical picture of an energy cascade with anomalous dissipation.

**What this does not say.** Nothing about smooth solutions of NS: convex integration operates at regularities where the equation has lost its parabolic character, and its solutions violate the energy inequality that any physical (and any Clay-relevant) solution satisfies. It neither builds a blow-up for smooth data nor obstructs global regularity. `[SYNTHESIS]`

**What it does say (and this is important).** It **kills a class of strategies**: (i) any attempted uniqueness/regularity theory relying only on the distributional formulation; (ii) any compactness scheme whose limit class is too weak to remember the energy inequality. The weak formulation alone carries essentially *no* rigidity in 3D. `[SYNTHESIS]`

### 3.4 (05-04) Mild solutions: Kato, Fujita–Kato, Koch–Tataru

**Facts.**
- *Mild formulation*: $u(t)=e^{\nu t\Delta}u^0-\int_0^t e^{\nu(t-s)\Delta}\,\mathbb{P}\,\nabla\cdot(u\otimes u)(s)\,ds$, $\mathbb{P}$ = Leray projector. Fixed-point solutions in scale-adapted spaces.
- *Fujita–Kato* [FK64]: local well-posedness for $u^0\in H^{1/2}$; **global for small $\dot H^{1/2}$ data**. Full proof in §5.1.
- *Kato* [Kat84]: same in $L^3$, using space-time smoothing norms.
- Besov refinements (Cannone, Planchon; see [LR16, BCD11]) extend smallness to $\dot B^{-1+3/p}_{p,\infty}$, $p<\infty$, admitting data that are *large* in $L^3$ (fast-oscillating profiles). Lei–Lin [LL11] gave an elementary global class ($\int|\xi|^{-1}|\hat u^0|\,d\xi$ small).
- *Koch–Tataru* [KT01]: small-data global well-posedness in $BMO^{-1}$ — the endpoint. Solutions are smooth for $t>0$ (Germain–Pavlović–Staffilani [GPS07]).
- *Optimality*: in the strictly larger critical space $\dot B^{-1}_{\infty,\infty}$ the problem is ill-posed (norm inflation, Bourgain–Pavlović [BP08]); later works extended ill-posedness to $\dot B^{-1}_{\infty,q}$ ranges. So the perturbative small-data theory is *complete*: $BMO^{-1}$ is essentially the last stop.

**What this does not say.** Everything here is perturbation off the heat semigroup: the nonlinearity is treated as an error term, which is legitimate only when the datum is small in a critical norm (or for short time in subcritical norms). No iteration of this type can see large-data global structure — the Picard series has finite radius. `[SYNTHESIS]`

**Mission item "new mild-solution class".** Assessment: the function-space frontier is closed by [KT01]+[BP08]. A genuinely useful "new class" would have to encode *dynamical* rather than *size* information (e.g. spectral coherence, vorticity-direction regularity as in [CF93]) — no such well-posedness class is known, and none is proposed here. `[SPECULATIVE — direction only]` (§6.4)

### 3.5 (05-05) Partial regularity: CKN $\varepsilon$-regularity and the singular set

**Facts.** For suitable weak solutions (§3.1):
- *First $\varepsilon$-criterion* [CKN82]: there is a universal $\varepsilon_0>0$ such that if $r^{-2}\int\!\!\int_{Q_r(z)}(|u|^3+|p|^{3/2})\,dx\,dt\le\varepsilon_0$ on a parabolic cylinder $Q_r(z)$, then $u\in L^\infty(Q_{r/2}(z))$ (hence smooth in space there).
- *Second criterion* [CKN82]: if $\limsup_{r\to0} r^{-1}\int\!\!\int_{Q_r(z)}|\nabla u|^2\le\varepsilon_1$, then $z$ is a regular point.
- *Main theorem* [CKN82]: the singular set $S\subset\mathbb{R}^3\times(0,\infty)$ satisfies $\mathcal{P}^1(S)=0$ (one-dimensional **parabolic** Hausdorff measure zero). In particular singularities, if any, form a very sparse set — no singular curve in space-time, no singular ring at a fixed time.
- Streamlined proofs: Lin [Lin98], Ladyzhenskaya–Seregin [LS99], Vasseur (De Giorgi method) [Vas07]. Refinements since 1982 are logarithmic; the exponent 1 has never been improved.
- Consequence used in §3.6: for axisymmetric flows, singular points must lie **on the axis** (a singular ring $\{r=r_0>0\}$ at time $T$ would carry positive $\mathcal{P}^1$-measure). `[KNOWN]`

**Why the exponent is stuck at 1** `[SYNTHESIS — folklore]`: the local dissipation $\int\!\!\int_{Q_r}|\nabla u|^2$ scales like $r^{1}$ under the NS scaling — CKN extracts *exactly* the scaling content of the energy inequality, no more. Improving $1\to1-\delta$ unconditionally would be a supercritical estimate, i.e. precisely the kind of gain that §5.4 shows cannot come from energy structure alone. CKN is best-possible *for its inputs*.

### 3.6 (05-06) Axisymmetric Navier–Stokes, with and without swirl

Cylindrical coordinates $(r,\theta,z)$, $u=u_r e_r+u_\theta e_\theta+u_z e_z$, axisymmetric: no $\theta$-dependence. **Swirl** $=u_\theta$.

**Facts.**
- *Without swirl ($u_\theta\equiv0$): global regularity.* Ladyzhenskaya [Lad68] and Ukhovskii–Yudovich [UY68] (1968). Mechanism: $\eta:=\omega_\theta/r$ satisfies a drift–diffusion equation $\partial_t\eta+u\cdot\nabla\eta=\nu\big(\Delta+\tfrac2r\partial_r\big)\eta$ with a maximum principle, so $\|\eta(t)\|_{L^\infty}\le\|\eta_0\|_{L^\infty}$. Scaling check: $\eta_\lambda=\lambda^3\eta(\lambda x,\lambda^2 t)$, so $\|\eta\|_{L^\infty}$ is **subcritical** — the flow structure hands over, for free, exactly the kind of supercriticality-beating a priori bound that is unavailable in general (§3.10), and the argument closes. This is the standard example of a *clean special-case theorem*.
- *With swirl: open*, but with strong structure: $\Gamma:=ru_\theta$ obeys $\partial_t\Gamma+u\cdot\nabla\Gamma=\nu\big(\Delta-\tfrac2r\partial_r\big)\Gamma$, again with a maximum principle, so $\|\Gamma(t)\|_{L^\infty}\le\|\Gamma_0\|_{L^\infty}$. Scaling check: $\Gamma_\lambda(x,t)=\Gamma(\lambda x,\lambda^2t)$, so $\|\Gamma\|_{L^\infty}$ is exactly **critical** — axisymmetric-with-swirl NS possesses a globally bounded critical quantity, a luxury the general problem lacks. The frustration is that $\Gamma$ vanishes on the axis, which is precisely where any singularity must sit (§3.5): the critical bound degenerates exactly where it is needed. This is why the case is regarded as tantalizingly close yet still open. `[KNOWN facts; framing SYNTHESIS]`
- *Type I exclusion*: if an axisymmetric solution obeys the scale-invariant bound $|u(x,t)|\le C/r$ (or the self-similar rate $|u|\le C(T-t)^{-1/2}$), it does not blow up — Chen–Strain–Tsai–Yau [CSTY08, CSTY09] and Koch–Nadirashvili–Seregin–Šverák [KNSS09] (via Liouville theorems for ancient solutions). So an axisymmetric singularity, if any, must be **Type II** (faster than self-similar rate) and on the axis (§3.5).
- No-swirl-plus-perturbation and various weighted refinements exist in the recent literature; none removes the swirl obstruction.

**Assessment.** This is the tightest arena in the whole problem: one scalar constraint ($u_\theta=0$) separates a fully solved case from the open one, and in the open case the "generic" blow-up rates are already excluded. A proof of axisymmetric-with-swirl regularity would be a historic result and plausibly a stepping stone; a Type II axisymmetric blow-up construction would settle Clay (C)/(D). Both look out of reach with current tools, for the reasons in §4. `[SYNTHESIS]`

### 3.7 (05-07) Numerical blow-up searches and the gap from numerics to proof

**Facts.**
- *Euler (with boundary)*: Luo–Hou (2014) [LH14a, LH14b] found a numerically robust, nearly self-similar blow-up scenario for axisymmetric Euler in a cylinder (vorticity growth $\sim10^8$ on the boundary). Chen–Hou then *proved* finite-time blow-up for 2D Boussinesq and 3D axisymmetric Euler with smooth data **and boundary**, via nonlinear stability of an approximate self-similar profile certified with interval arithmetic — Part I analysis (arXiv:2210.07191), Part II rigorous numerics, Multiscale Model. Simul. 23 (2025) 25–130 [CH25] (web-verified). Elgindi [Elg21] had earlier proved blow-up for $C^{1,\alpha}$ (non-smooth) Euler data on $\mathbb{R}^3$.
- *Earlier cautionary tales*: Kerr's 1993 candidate was later found non-singular under higher resolution (Hou–Li [HL06] — "dynamic depletion" of vortex stretching). Numerical "blow-up" has repeatedly dissolved under scrutiny; the Luo–Hou scenario is the one that survived and became a theorem.
- *Navier–Stokes*: Hou (2023) [Hou23] reports potentially singular behavior of axisymmetric NS with smooth data ($10^7$ vorticity growth) with *nearly* self-similar structure — but explicitly not a proof, and the viscous scaling analysis there shows the scenario is under strain.

**The structural gap for NS** `[SYNTHESIS]`:
1. The proved Euler blow-ups lean on a **boundary** (the Chen–Hou profile is anchored at the cylinder wall) or on low regularity [Elg21]. Clay's NS problem has no boundary ($\mathbb{R}^3$/$\mathbb{T}^3$).
2. The numerics-to-proof pipeline requires a (nearly) **self-similar profile** whose stability can be certified. For NS, backward self-similar blow-up is a *theorem-level impossibility* (Leray's ansatz excluded in $L^3$ by Nečas–Růžička–Šverák [NRS96], in the local-energy class by Tsai [Tsa98]); axisymmetric Type I is excluded (§3.6). So the pipeline's key object *provably does not exist* for NS in the natural classes; any NS blow-up must be non-self-similar (e.g. with slowly drifting scaling exponents), for which no certification technology exists.
3. Viscosity sets a dissipative cutoff scale; a candidate singularity must outrun it, i.e. the numerics must resolve an unbounded range of scales with certified error — currently beyond interval-arithmetic methods without a stable profile to renormalize onto.

### 3.8 (05-08) Stochastic Navier–Stokes and almost-sure well-posedness — does anything transfer?

**Facts.**
- *Existence*: martingale (weak probabilistic) solutions exist globally (Flandoli–Gątarek [FG95]); Markov selections exist (Flandoli–Romito [FR08]); under nondegenerate noise, selections have ergodicity/smoothing properties (Da Prato–Debussche [DPD03]). Hairer–Mattingly's celebrated ergodicity theorem is **2D** [HM06] — where deterministic regularity is classical anyway.
- *Noise does not (so far) regularize 3D NS*: Hofmanová–Zhu–Zhu proved non-uniqueness **in law** for stochastic 3D NS (J. Eur. Math. Soc. 26 (2024) 163–260 [HZZ24], web-verified) and existence + non-uniqueness of global probabilistically strong solutions (Ann. Probab. 51 (2023) 524–579 [HZZ23], web-verified): convex integration survives the noise.
- *Where noise genuinely helps*: linear transport equations (Flandoli–Gubinelli–Priola [FGP10]) and some model problems — mechanisms that rely on linearity or on the noise dominating the drift; neither applies to the NS nonlinearity at criticality.
- *Randomized data*: almost-sure existence results for supercritical data via Wiener randomization (e.g. Nahmod–Pavlović–Staffilani [NPS13]) give weak/mild solutions for "generic" rough data. They do not touch the worst-case smooth-data problem: randomization improves integrability, not scaling.

**Transfer assessment** `[SYNTHESIS]`: There is no known mechanism by which almost-sure or in-law statements about stochastic NS constrain a specific deterministic smooth datum; and the 3D convex-integration results show the stochastic framework inherits, rather than repairs, the deterministic pathologies. Verdict: this angle currently *imports* obstructions rather than exporting solutions.

### 3.9 (05-09) Euler vs Navier–Stokes; the inviscid limit

**Facts.**
- On $\mathbb{R}^3/\mathbb{T}^3$ (no boundary), for a fixed smooth Euler solution on $[0,T]$, NS solutions with the same data converge to it as $\nu\to0$, with $O(\nu)$-rate energy bounds (classical; Kato 1972, Swann, Constantin — see [RRS16] for exposition). With boundaries, the inviscid limit is a famously open problem governed by Kato's boundary-layer dissipation criterion.
- Euler blow-up is now *proved* in restricted settings: $C^{1,\alpha}$ data on $\mathbb{R}^3$ [Elg21]; smooth data with cylindrical boundary [CH25]. Smooth-data, no-boundary 3D Euler blow-up remains open. In 2D, Euler is globally regular but exhibits provable small-scale creation (Kiselev–Šverák [KS14]) — a hint of the inviscid mechanisms available.
- Formal relations `[SYNTHESIS]`: (i) An Euler blow-up does **not** imply NS blow-up: viscosity is a singular perturbation that dominates below the dissipation scale; the known Euler scenarios are boundary-anchored or low-regularity, and both features are destroyed or fundamentally altered by viscosity (boundary layers; instantaneous smoothing). (ii) Conversely, NS global regularity would say nothing about Euler ($\nu\to0$ limits lose all subcritical bounds). (iii) BKM (§3.2) applies to both, but vorticity control is *harder* for Euler; the useful traffic between the two problems consists of mechanisms (vortex stretching geometry, depletion) rather than theorems.

**Bottom line.** Euler blow-up — even if proved for smooth no-boundary data — would not settle any Clay alternative for NS, and vice versa. The problems share a nonlinearity but not a criticality structure: Euler has no dissipative scale, NS's whole difficulty is the fight between stretching and dissipation across scales. `[SYNTHESIS]`

### 3.10 (05-10) Criticality: why 3D is supercritical, and Tao's averaged NS as a barrier

**Facts.**
- Under $u_\lambda=\lambda u(\lambda x,\lambda^2t)$: kinetic energy scales as $\|u_\lambda(0)\|_{L^2}^2=\lambda^{-1}\|u(0)\|_{L^2}^2$; dissipation likewise. In **2D** energy is critical (better: enstrophy is subcritically coercive) — global regularity, Ladyzhenskaya 1950s–60s [Lad69]. In 3D both controlled quantities are supercritical: zooming in ($\lambda\to\infty$) makes the known bounds vacuous. The problem is *supercritical* — the structural class in which no large-data global regularity theorem has ever been proved by soft/energy methods.
- *Hyperdissipation calibration*: replace $-\Delta$ by $(-\Delta)^\alpha$. For $\alpha\ge5/4$ energy becomes critical and global regularity holds (Lions [Lio69]); Tao [Tao09] pushed to logarithmically supercritical dissipation; Katz–Pavlović [KP02] analyzed the dyadic model. The known techniques fail *immediately* below the critical calibration — quantifying how thin the margin is.
- *Model blow-ups*: cheap/dyadic models with the same scaling and energy identity blow up (Montgomery-Smith [MS01]; Katz–Pavlović [KP02]).
- *Tao's averaged NS* [Tao16]: there is a bilinear operator $\tilde B$, an *average* of rotated/dilated Fourier-localized versions of the true nonlinearity $B(u,u)=\mathbb{P}\nabla\cdot(u\otimes u)$, preserving divergence-free vector fields, the cancellation $\langle\tilde B(u,u),u\rangle=0$ (hence the **same energy identity**), the same scaling, and the standard "abstract" harmonic-analysis estimates of $B$ — such that $\partial_t u=\Delta u+\tilde B(u,u)$ blows up in finite time from smooth data. Formalized as a no-go in §5.4.

**Consequence** `[SYNTHESIS]`: 3D NS global regularity, if true, is true for reasons *invisible* to: the energy identity; scaling-consistent bilinear estimates; the weak formulation. Any successful method must exploit fine structure — candidates: the exact Biot–Savart geometry of vortex stretching (used by [CF93] conditionally, by the no-swirl miracle §3.6 unconditionally in a special case), maximum principles for specific scalar quantities ($\Gamma$, $\omega_\theta/r$), or non-perturbative uses of viscosity (backward uniqueness/Carleman, as in [ESS03, Tao21]). This checklist is expanded in §6.3.

---

## 4. Main Technical Obstructions (Synthesis)

`[SYNTHESIS]` — assembled from §3; each item cites the theorem that *enforces* it.

**O1. Supercriticality of all coercive bounds.** The only large-data global quantities (energy, dissipation) shrink under zoom-in; every known regularity mechanism requires critical-or-better information ([Fef00] framing; §3.10). Enforced by: scaling algebra (elementary).

**O2. Energy-only methods provably cannot close.** Any argument using only the energy identity + estimates stable under Tao's averaging class applies equally to the averaged equation, which blows up [Tao16]. See Proposition 5.4 for the precise statement.

**O3. The weak formulation has no rigidity.** Convex integration produces continua of finite-energy distributional solutions [BV19, CL22]; with forcing, non-uniqueness reaches the Leray class [ABC22]. Enforced by: those constructions. Consequence: compactness/weak-limit schemes must propagate strictly more than the weak formulation (local energy inequalities at minimum — and §3.5 shows how little even those buy beyond CKN).

**O4. The perturbative frontier is closed.** Small-data global well-posedness ends at $BMO^{-1}$ [KT01]; one step larger is ill-posed [BP08]. Large-data results cannot come from Picard iteration in any function space of "size" type.

**O5. The simplest singularity ansätze are excluded.** No backward self-similar blow-up [NRS96, Tsa98]; no axisymmetric Type I [CSTY08, CSTY09, KNSS09]; $L^3$-norm must diverge at blow-up [Ser12] at a (very slowly) quantified rate [Tao21]. Consequence: any blow-up construction must be non-self-similar and Type II — beyond both current rigorous technology and current certification technology for numerics (§3.7).

**O6. Both directions are hard simultaneously.** O1–O4 block regularity proofs; O5 blocks blow-up constructions. This two-sided rigidity is the modern signature of the problem: the theorems of the last two decades have mostly been *no-go* theorems, each shrinking the space of possible proofs — from both sides.

---

## 5. Rigorous Results (Attack Deliverables, with Complete Proofs)

Per the mission's breakthrough menu, the deliverable here is the "clean special-case theorem written rigorously" option, times three, plus a formalized no-go. **All four results are known**; the value added is a self-contained, correct, fully quantified write-up with explicit constants, suitable as a foundation layer for future legion runs. Function spaces are homogeneous Sobolev spaces $\dot H^s(\mathbb{R}^3)$, $\|f\|_{\dot H^s}^2=\int|\xi|^{2s}|\hat f(\xi)|^2 d\xi$; $\mathbb{P}=\mathrm{Id}-\nabla\Delta^{-1}\mathrm{div}$ is the Leray projector (a bounded Fourier multiplier on every $\dot H^s$).

### 5.1 Theorem (Fujita–Kato: small-data global regularity in $\dot H^{1/2}$) `[KNOWN — proof written out here]`

**Theorem 5.1.** There is an absolute constant $\varepsilon_0>0$ with the following property. Let $u^0\in\dot H^{1/2}(\mathbb{R}^3)$ be divergence-free with
$$\|u^0\|_{\dot H^{1/2}}\le \varepsilon_0\,\nu .$$
Then there exists a global mild solution
$$u\in C\big([0,\infty);\dot H^{1/2}\big)\cap L^2\big((0,\infty);\dot H^{3/2}\big)$$
of the Navier–Stokes equations with datum $u^0$; it is unique in the open ball $\{\|u\|_{X}< \tfrac{\nu}{8C_0}\}$ of the space $X$ defined below ($C_0$ the constant of Lemma 5.1.5), and it is smooth on $\mathbb{R}^3\times(0,\infty)$.

*Remark (honesty).* Critical-space smallness is essential to this argument; the theorem contributes nothing to Clay (A). One may take the same statement on $\mathbb{T}^3$ for mean-zero data. Uniqueness in the full space $C_t\dot H^{1/2}\cap L^2_t\dot H^{3/2}$ without the ball restriction is also true but requires a separate argument not reproduced here.

**Setup.** For $T\in(0,\infty]$ let
$$X_T:=\Big\{u\in C([0,T);\dot H^{1/2}):\ \|u\|_{X_T}<\infty\Big\},\qquad
\|u\|_{X_T}:=\sup_{0\le t<T}\|u(t)\|_{\dot H^{1/2}}+\nu^{1/2}\Big(\int_0^T\|u(t)\|_{\dot H^{3/2}}^2\,dt\Big)^{1/2}.$$
Write $X:=X_\infty$. The mild formulation is $u=a+B(u,u)$ with
$$a(t):=e^{\nu t\Delta}u^0,\qquad B(u,v)(t):=-\int_0^t e^{\nu(t-s)\Delta}\,\mathbb{P}\,\nabla\!\cdot\!\big(u(s)\otimes v(s)\big)\,ds .$$

**Lemma 5.1.1 (abstract fixed point).** Let $(Y,\|\cdot\|)$ be a Banach space, $\mathcal B:Y\times Y\to Y$ bilinear with $\|\mathcal B(x,y)\|\le\gamma\|x\|\,\|y\|$, and $a\in Y$ with $4\gamma\|a\|<1$. Then $x=a+\mathcal B(x,x)$ has a solution with $\|x\|\le2\|a\|$, and this is the only solution in the open ball $B(0,\tfrac{1}{2\gamma})$.

*Proof.* $\Phi(x):=a+\mathcal B(x,x)$ maps $\bar B(0,2\|a\|)$ to itself: $\|\Phi(x)\|\le\|a\|+\gamma(2\|a\|)^2=\|a\|(1+4\gamma\|a\|)<2\|a\|$. It is a contraction there: $\|\Phi(x)-\Phi(y)\|\le\gamma\|x-y\|(\|x\|+\|y\|)\le4\gamma\|a\|\,\|x-y\|$, and $4\gamma\|a\|<1$. Banach's theorem gives existence, with $\|x\|\le2\|a\|<\tfrac1{2\gamma}$. If $y\in B(0,\tfrac1{2\gamma})$ is any solution, then $\|x-y\|=\|\mathcal B(x,x)-\mathcal B(y,y)\|\le\gamma(\|x\|+\|y\|)\|x-y\|$ and $\gamma(\|x\|+\|y\|)<\gamma\big(\tfrac1{2\gamma}+\tfrac1{2\gamma}\big)=1$, forcing $\|x-y\|=0$. $\square$

**Lemma 5.1.2 (linear estimates).** For divergence-free $u^0\in\dot H^{1/2}$: $a\in X$ and $\|a\|_{X}\le 2\|u^0\|_{\dot H^{1/2}}$.

*Proof.* By Plancherel, $\|a(t)\|_{\dot H^{1/2}}^2=\int|\xi|\,e^{-2\nu t|\xi|^2}|\hat u^0|^2d\xi\le\|u^0\|_{\dot H^{1/2}}^2$, with strong continuity in $t$ by dominated convergence (and continuity at $t=0^+$ likewise). For the dissipative part, Fubini gives
$$\int_0^\infty\|a(t)\|_{\dot H^{3/2}}^2dt=\int|\xi|^{3}|\hat u^0(\xi)|^2\int_0^\infty e^{-2\nu t|\xi|^2}dt\,d\xi=\frac1{2\nu}\|u^0\|_{\dot H^{1/2}}^2 .$$
Hence $\|a\|_X\le\|u^0\|_{\dot H^{1/2}}+\nu^{1/2}(2\nu)^{-1/2}\|u^0\|_{\dot H^{1/2}}\le2\|u^0\|_{\dot H^{1/2}}$. $\square$

**Lemma 5.1.3 (product law).** There is an absolute $C_{\mathrm{pr}}$ with
$$\|fg\|_{\dot H^{1/2}(\mathbb{R}^3)}\le C_{\mathrm{pr}}\|f\|_{\dot H^{1}}\|g\|_{\dot H^{1}} .$$

*Proof (complete modulo standard Littlewood–Paley facts, cf. [BCD11, Ch. 2]).* Let $\Delta_j$ be homogeneous LP blocks, $S_j=\sum_{k\le j-1}\Delta_k$, and use Bony's decomposition $fg=T_fg+T_gf+R(f,g)$, $T_fg=\sum_jS_{j-1}f\,\Delta_jg$, $R(f,g)=\sum_{|j-j'|\le1}\Delta_jf\,\Delta_{j'}g$.
*Paraproducts:* By Bernstein, $\|S_{j-1}f\|_{L^\infty}\le\sum_{k\le j-2}2^{3k/2}\|\Delta_kf\|_{L^2}=\sum_{k\le j-2}2^{k/2}\,(2^{k}\|\Delta_kf\|_{L^2})\le C2^{j/2}\|f\|_{\dot H^1}$ (Cauchy–Schwarz on the geometric weight $2^{k/2}$, $k\le j-2$). Since $\Delta_j(S_{j-1}f\,\Delta_jg)$ is frequency-localized at $\sim2^j$ up to a fixed number of neighbours,
$$2^{j/2}\|\Delta_j(T_fg)\|_{L^2}\le C\,2^{j/2}\,2^{j/2}\|f\|_{\dot H^1}\|\Delta_{\tilde j}g\|_{L^2}\le C\|f\|_{\dot H^1}\,\big(2^{\tilde j}\|\Delta_{\tilde j}g\|_{L^2}\big),$$
which is square-summable in $j$ with sum $\le C\|f\|_{\dot H^1}\|g\|_{\dot H^1}$. Symmetrically for $T_gf$.
*Remainder:* $\Delta_jR(f,g)$ collects products $\Delta_kf\Delta_{k'}g$ with $k,k'\ge j-N_0$, $|k-k'|\le1$. By Bernstein ($L^1\to L^2$ on frequencies $\lesssim 2^j$),
$$\|\Delta_jR(f,g)\|_{L^2}\le C2^{3j/2}\sum_{k\ge j-N_0}\|\Delta_kf\|_{L^2}\|\Delta_kg\|_{L^2}\le C2^{3j/2}\sum_{k\ge j-N_0}2^{-2k}c_kd_k\|f\|_{\dot H^1}\|g\|_{\dot H^1},$$
with $(c_k),(d_k)\in\ell^2$ unit vectors. Multiplying by $2^{j/2}$ gives $2^{j/2}\|\Delta_jR(f,g)\|_{L^2}\le C\sum_{k\ge j-N_0}2^{2(j-k)}c_kd_k\,\|f\|_{\dot H^1}\|g\|_{\dot H^1}$; the sequence $(c_kd_k)_k$ is $\ell^1$ (Cauchy–Schwarz) and the kernel $2^{2m}\mathbf 1_{m\le N_0}$ (in $m=j-k$) is $\ell^1$, so by Young's convolution inequality the left side is square-summable (indeed summable) in $j$ with the same bound. Summing the three pieces yields the lemma. $\square$

**Lemma 5.1.4 (Duhamel/energy estimate).** Let $F\in L^2((0,T);\dot H^{-1/2})$ and $w(t)=\int_0^te^{\nu(t-s)\Delta}F(s)ds$. Then $w\in C([0,T);\dot H^{1/2})\cap L^2((0,T);\dot H^{3/2})$ and
$$\sup_{t<T}\|w(t)\|_{\dot H^{1/2}}^2+\nu\int_0^T\|w\|_{\dot H^{3/2}}^2\,dt\ \le\ \frac1\nu\int_0^T\|F\|_{\dot H^{-1/2}}^2\,dt .$$

*Proof.* For smooth compactly-frequency-supported $F$ (then conclude by density), $w$ solves $\partial_tw=\nu\Delta w+F$, $w(0)=0$, and
$$\tfrac{d}{dt}\|w\|_{\dot H^{1/2}}^2=-2\nu\|w\|_{\dot H^{3/2}}^2+2\langle F,w\rangle_{\dot H^{1/2}},\qquad
\langle F,w\rangle_{\dot H^{1/2}}=\int|\xi|\hat F\overline{\hat w}\,d\xi\le\|F\|_{\dot H^{-1/2}}\|w\|_{\dot H^{3/2}},$$
using $|\xi|=|\xi|^{-1/2}\cdot|\xi|^{3/2}$ and Cauchy–Schwarz. Young's inequality $2ab\le\nu^{-1}a^2+\nu b^2$ gives
$\tfrac{d}{dt}\|w\|_{\dot H^{1/2}}^2+\nu\|w\|_{\dot H^{3/2}}^2\le\nu^{-1}\|F\|_{\dot H^{-1/2}}^2$; integrate. Continuity in $\dot H^{1/2}$ follows from the same inequality applied on subintervals. $\square$

**Lemma 5.1.5 (bilinear estimate).** For $u,v\in X_T$,
$$\|B(u,v)\|_{X_T}\ \le\ \frac{4C_0}{\nu}\,\|u\|_{X_T}\|v\|_{X_T},\qquad C_0:=C_{\mathrm{pr}} .$$

*Proof.* Interpolation $\|u\|_{\dot H^1}\le\|u\|_{\dot H^{1/2}}^{1/2}\|u\|_{\dot H^{3/2}}^{1/2}$ (Cauchy–Schwarz on Plancherel) gives
$$\|u\|_{L^4_T\dot H^1}\le\Big(\sup_t\|u\|_{\dot H^{1/2}}\Big)^{1/2}\|u\|_{L^2_T\dot H^{3/2}}^{1/2}\le\nu^{-1/4}\|u\|_{X_T}.$$
By Lemma 5.1.3 and Hölder in time, $F:=-\mathbb{P}\nabla\cdot(u\otimes v)$ satisfies
$$\|F\|_{L^2_T\dot H^{-1/2}}\le\|u\otimes v\|_{L^2_T\dot H^{1/2}}\le C_{\mathrm{pr}}\|u\|_{L^4_T\dot H^1}\|v\|_{L^4_T\dot H^1}\le C_{\mathrm{pr}}\nu^{-1/2}\|u\|_{X_T}\|v\|_{X_T},$$
since $\mathbb P$ and $\partial_k|\nabla|^{-1}$-type multipliers are bounded and $\mathrm{div}$ costs one derivative: $\|\mathbb P\nabla\cdot G\|_{\dot H^{-1/2}}\le\|G\|_{\dot H^{1/2}}$. Writing $w:=B(u,v)$, Lemma 5.1.4 gives both $\sup_t\|w\|_{\dot H^{1/2}}\le\nu^{-1/2}\|F\|_{L^2_T\dot H^{-1/2}}$ and $\nu^{1/2}\|w\|_{L^2_T\dot H^{3/2}}=\big(\nu\!\int\|w\|_{\dot H^{3/2}}^2\big)^{1/2}\le\nu^{-1/2}\|F\|_{L^2_T\dot H^{-1/2}}$, hence
$$\|B(u,v)\|_{X_T}\ \le\ 2\nu^{-1/2}\|F\|_{L^2_T\dot H^{-1/2}}\ \le\ \frac{2C_{\mathrm{pr}}}{\nu}\|u\|_{X_T}\|v\|_{X_T}\ \le\ \frac{4C_0}{\nu}\|u\|_{X_T}\|v\|_{X_T}. \qquad\square$$

**Proof of Theorem 5.1.** Apply Lemma 5.1.1 in $Y=X$ with $\gamma=4C_0/\nu$ and $\|a\|_X\le2\|u^0\|_{\dot H^{1/2}}\le2\varepsilon_0\nu$. The smallness condition $4\gamma\|a\|<1$ holds if $\varepsilon_0<\tfrac{1}{64C_0}$. This produces a global mild solution with $\|u\|_X\le4\varepsilon_0\nu$, unique in the open ball $B(0,\tfrac\nu{8C_0})$ of $X$. Divergence-freeness is preserved by $a$ and $B$ (both commute with $\mathbb P$ on divergence-free fields). Smoothness for $t>0$ is the standard parabolic bootstrap for Kato-class mild solutions — `[KNOWN, cited]`: see [LR16, Ch. 5], [GPS07] (even for the larger $BMO^{-1}$ class), or [RRS16, Ch. 6–8]; it is not reproved here. $\blacksquare$

### 5.2 Theorem (Enstrophy inequality and the Leray blow-up rate) `[KNOWN — proof written out here]`

**Theorem 5.2.** Let $u$ be a strong solution on $[0,T)$ with $u^0\in H^1(\mathbb{R}^3)$ divergence-free (i.e. $u\in C([0,T);H^1)\cap L^2_{loc}([0,T);H^2)$, smooth for $t>0$), and suppose $T<\infty$ is the **maximal** existence time. Then there is an absolute constant $c>0$ such that
$$\|\nabla u(t)\|_{L^2}\ \ge\ c\,\nu^{3/4}\,(T-t)^{-1/4}\qquad\text{for all }t\in[0,T).$$
Consequently $\int_0^T\|\nabla u(t)\|_{L^2}^4\,dt=\infty$, and the maximal time obeys the lower bound $T\ge c^4\nu^3/\|\nabla u^0\|_{L^2}^4$.

**Lemma 5.2.1 (standard local theory; cited, not reproved).** For divergence-free $u^0\in H^1(\mathbb{R}^3)$ there is a unique strong solution on a maximal interval $[0,T_{\max})$, and if $T_{\max}<\infty$ then $\|\nabla u(t)\|_{L^2}\to\infty$ as $t\uparrow T_{\max}$. `[KNOWN]` — Kato-type local well-posedness in $H^1$ (subcritical): see [FK64], [RRS16, Ch. 6–9], [LR16].

**Lemma 5.2.2 (enstrophy differential inequality).** For a strong solution as above and $t\in(0,T)$,
$$\frac{d}{dt}\,\|\nabla u(t)\|_{L^2}^2\ \le\ \frac{K_0}{\nu^{3}}\,\|\nabla u(t)\|_{L^2}^{6},\qquad K_0\ \text{absolute}.$$

*Proof.* Pair the equation with $-\Delta u$ in $L^2$. The pressure term vanishes: $\int\nabla p\cdot\Delta u=-\int p\,\Delta(\nabla\cdot u)=0$. The time term gives $\langle\partial_tu,-\Delta u\rangle=\tfrac12\tfrac{d}{dt}\|\nabla u\|_{L^2}^2$. The viscous term gives $-\nu\|\Delta u\|_{L^2}^2$ on the right. Hence
$$\tfrac12\tfrac{d}{dt}\|\nabla u\|_{L^2}^2+\nu\|\Delta u\|_{L^2}^2=\int(u\cdot\nabla)u\cdot\Delta u\le\|u\cdot\nabla u\|_{L^2}\|\Delta u\|_{L^2}.$$
Now estimate, using Hölder, Sobolev $\|f\|_{L^6}\le C_S\|\nabla f\|_{L^2}$, interpolation $\|g\|_{L^3}\le\|g\|_{L^2}^{1/2}\|g\|_{L^6}^{1/2}$, and the Plancherel identity $\|\nabla^2u\|_{L^2}=\|\Delta u\|_{L^2}$ on $\mathbb{R}^3$:
$$\|u\cdot\nabla u\|_{L^2}\le\|u\|_{L^6}\|\nabla u\|_{L^3}\le C_S\|\nabla u\|_{L^2}\cdot\|\nabla u\|_{L^2}^{1/2}\|\nabla u\|_{L^6}^{1/2}\le C\,\|\nabla u\|_{L^2}^{3/2}\|\Delta u\|_{L^2}^{1/2}.$$
Therefore, with $X(t):=\|\nabla u(t)\|_{L^2}^2$,
$$\tfrac12X'+\nu\|\Delta u\|_{L^2}^2\le C\,X^{3/4}\|\Delta u\|_{L^2}^{3/2}\le\tfrac\nu2\|\Delta u\|_{L^2}^2+\frac{C'}{\nu^{3}}X^{3},$$
by Young's inequality with exponents $(4/3,4)$: $ab\le\tfrac{3\varepsilon}{4}a^{4/3}+\tfrac{1}{4\varepsilon^3}b^4$ applied to $a=\|\Delta u\|^{3/2}$, $b=CX^{3/4}$, $\varepsilon\sim\nu$. Dropping the nonnegative dissipation term gives the claim with $K_0=2C'$. $\square$

**Proof of Theorem 5.2.** Set $K:=K_0\nu^{-3}$, so $X'\le KX^3$ on $(0,T)$, and $X(s)\to\infty$ as $s\uparrow T$ by Lemma 5.2.1 (maximality). For $0\le t<s<T$, integrate $\tfrac{d}{ds}X^{-2}=-2X^{-3}X'\ge-2K$:
$$X^{-2}(s)\ \ge\ X^{-2}(t)-2K(s-t).$$
Let $s\uparrow T$; the left side tends to $0$, so $X^{-2}(t)\le2K(T-t)$, i.e.
$$\|\nabla u(t)\|_{L^2}=X(t)^{1/2}\ \ge\ \big(2K\big)^{-1/4}(T-t)^{-1/4}=c\,\nu^{3/4}(T-t)^{-1/4},\quad c:=(2K_0)^{-1/4}.$$
Then $\int_0^T\|\nabla u\|_{L^2}^4dt\ge c^4\nu^3\int_0^T\frac{dt}{T-t}=\infty$. Taking $t=0$ rearranges to $T\ge c^4\nu^3\|\nabla u^0\|_{L^2}^{-4}$. $\blacksquare$

*Remark.* This is Leray's 1934 rate [Ler34] in modern dress. Note the honest scope: it constrains *how* blow-up would happen; it neither produces nor excludes blow-up.

### 5.3 Theorem (Singular times have Hausdorff dimension $\le\tfrac12$) `[KNOWN — proof written out here, modulo cited Lemmas 5.2.1 and weak–strong uniqueness]`

**Theorem 5.3.** Let $u$ be a Leray–Hopf weak solution on $\mathbb{R}^3\times(0,\infty)$ with $u^0\in L^2$ divergence-free, satisfying the strong energy inequality. Define the **regular set** $\mathcal R\subset(0,\infty)$ as the set of times possessing a neighbourhood on which $u$ agrees with a strong solution, and $\Sigma:=(0,\infty)\setminus\mathcal R$. Then $\Sigma$ is a bounded, relatively closed subset of $(0,\infty)$ of Lebesgue measure zero with $\mathcal H^{1/2}(\Sigma)=0$; in particular $\dim_{\mathcal H}\Sigma\le\tfrac12$, and $u$ is smooth on $\mathbb{R}^3\times\mathcal R$ with $\mathcal R$ open of full measure. Moreover $\Sigma\subset(0,T_*]$ for some finite $T_*$ (eventual regularity). (If in addition $u^0\in H^1$, then $\Sigma$ is bounded away from $0$, hence compact.)

*Ingredients used as cited lemmas:* (a) Lemma 5.2.1 (local $H^1$ theory + continuation criterion + instantaneous $H^1$-regularization within epochs, standard); (b) weak–strong uniqueness [Pro59, Ser62] `[KNOWN]`.

*Proof.* We use a Leray–Hopf solution satisfying the **strong energy inequality** (energy inequality from a.e. starting time $t_0$, valid for Leray's construction — `[KNOWN]`, see [RRS16]); this is what weak–strong uniqueness requires below. Since $\int_0^\infty\|\nabla u\|_{L^2}^2dt<\infty$ (energy inequality), $\|\nabla u(t)\|_{L^2}<\infty$ for a.e. $t$. For a.e. $t_0$ with $\|\nabla u(t_0)\|_{L^2}<\infty$, Lemma 5.2.1 launches a strong solution on $[t_0,t_0+\delta)$ with $\delta\ge c^4\nu^3\|\nabla u(t_0)\|_{L^2}^{-4}$ by Theorem 5.2, and weak–strong uniqueness identifies it with $u$ there. Hence $\mathcal R$ contains $\bigcup(t_0,t_0+\delta(t_0))$ over a.e. such $t_0$; it is open by definition and has full measure; $\Sigma$ is closed with Lebesgue measure zero.

*Eventual regularity:* since $\int_0^\infty\|\nabla u\|_{L^2}^2dt<\infty$ and $\|u(t)\|_{L^2}\le\|u^0\|_{L^2}$, there are a.e.-times $t_1$ with $\|\nabla u(t_1)\|_{L^2}$ arbitrarily small; by interpolation $\|u(t_1)\|_{\dot H^{1/2}}\le\|u(t_1)\|_{L^2}^{1/2}\|\nabla u(t_1)\|_{L^2}^{1/2}\le\|u^0\|_{L^2}^{1/2}\|\nabla u(t_1)\|_{L^2}^{1/2}$, so we may pick $t_1$ with $\|u(t_1)\|_{\dot H^{1/2}}\le\varepsilon_0\nu$. Theorem 5.1 (started at $t_1$) plus weak–strong uniqueness gives $[t_1,\infty)\subset\mathcal R$; thus $\Sigma\subset(0,t_1]$ is bounded. (For $u^0\in H^1$, Lemma 5.2.1 gives an initial epoch $[0,\delta_0)\subset\mathcal R\cup\{0\}$, so $\Sigma\subset[\delta_0/2,t_1]$ is then compact.)

*Dimension bound.* Fix $\eta>0$ and an open $U\supset\Sigma$ with $\int_U\|\nabla u\|_{L^2}^2dt\le\eta$ (absolute continuity of the integral, using $|\Sigma|=0$). For $\sigma\in\Sigma$ and any sufficiently small $\delta_\sigma>0$ with $[\sigma-\delta_\sigma,\sigma]\subset U$, set $I_\sigma:=(\sigma-\delta_\sigma,\sigma)$. Almost every $t\in I_\sigma$ has $\|\nabla u(t)\|_{L^2}<\infty$ and launches a strong solution which, by weak–strong uniqueness, agrees with $u$ up to its maximal time $T(t)$; since $\sigma\notin\mathcal R$, necessarily $T(t)\le\sigma$. Theorem 5.2 applied on $[t,T(t))$ gives
$$\|\nabla u(t)\|_{L^2}^2\ \ge\ c^2\nu^{3/2}\,(T(t)-t)^{-1/2}\ \ge\ c^2\nu^{3/2}(\sigma-t)^{-1/2}\quad\text{for a.e. }t\in I_\sigma,$$
where the last step uses $T(t)\le\sigma$. Integrating,
$$\int_{I_\sigma}\|\nabla u\|_{L^2}^2\,dt\ \ge\ c^2\nu^{3/2}\int_{\sigma-\delta_\sigma}^{\sigma}\frac{dt}{(\sigma-t)^{1/2}}\ =\ 2c^2\nu^{3/2}\,\delta_\sigma^{1/2}. \tag{5.3.1}$$
The closed intervals $\{[\sigma-\delta_\sigma,\sigma]\}_{\sigma\in\Sigma}$, with $\delta_\sigma$ ranging over all sufficiently small values, form a Vitali cover of $\Sigma$. By the Vitali covering lemma choose a countable *disjoint* subfamily $\{[\sigma_j-\delta_j,\sigma_j]\}$ with $\Sigma\subset\bigcup_j[\sigma_j-5\delta_j,\sigma_j+5\delta_j]$ (5r-version). Disjointness, $(5.3.1)$, and $I_{\sigma_j}\subset U$ give
$$\sum_j\delta_j^{1/2}\ \le\ \frac{1}{2c^2\nu^{3/2}}\int_U\|\nabla u\|_{L^2}^2dt\ \le\ \frac{\eta}{2c^2\nu^{3/2}},$$
while the enlarged intervals have $\mathcal H^{1/2}$-content $\sum_j(10\delta_j)^{1/2}\le\sqrt{10}\sum_j\delta_j^{1/2}$. Since $\delta_j$ can be taken uniformly small (fine cover) and $\eta>0$ arbitrary, $\mathcal H^{1/2}(\Sigma)=0$. $\blacksquare$

*Remark.* This is Leray's structure theorem [Ler34] (refined by Scheffer); the space-time upgrade is CKN's $\mathcal P^1(S)=0$ [CKN82] (§3.5), which we do not reprove.

### 5.4 Proposition (No-go for energy-only methods) `[KNOWN core + SYNTHESIS corollary]`

**Theorem (Tao [Tao16]).** `[KNOWN]` In this subsection only, let $B_{NS}(u,v):=-\tfrac12\mathbb P\big(\nabla\cdot(u\otimes v)+\nabla\cdot(v\otimes u)\big)$ denote the symmetrized Navier–Stokes bilinear operator (not the Duhamel operator of §5.1). There exists a bilinear operator $\tilde B$ on divergence-free vector fields — an average of Fourier-multiplier rotations/dilations of $B_{NS}$ — with the following properties: $\tilde B$ obeys the cancellation $\langle\tilde B(u,u),u\rangle_{L^2}=0$ (hence solutions of $(\ast)$ below obey the **same energy identity** as Navier–Stokes), $\tilde B$ obeys the same scaling and essentially all abstract harmonic-analysis estimates that $B_{NS}$ does (boundedness properties insensitive to the fine multiplier structure); and yet the Cauchy problem
$$\partial_tu=\Delta u+\tilde B(u,u)\qquad(\ast)$$
admits smooth, compactly-supported-in-frequency (Schwartz) divergence-free data whose unique mild solution blows up in finite time.

**Proposition 5.4 (formalized no-go).** `[SYNTHESIS — a logical corollary, stated carefully]` Call a putative global-regularity argument **energy-abstract** if its validity depends only on the following interfaces: (i) the linear semigroup $e^{t\Delta}$ and its standard estimates; (ii) the energy identity $\langle B(u,u),u\rangle=0$; (iii) a family of estimates for the nonlinearity that hold uniformly for every operator in Tao's averaging class (in particular, for $\tilde B$). Then no energy-abstract argument can prove global regularity for 3D Navier–Stokes.

*Proof.* An energy-abstract argument, applied verbatim with $B$ replaced by $\tilde B$, would prove global regularity for $(\ast)$, contradicting Tao's theorem. $\square$

*Scope and honesty.* The force of the proposition depends entirely on how large the class (iii) really is; [Tao16] establishes it contains the standard scaling-consistent bilinear/paraproduct estimates used in the perturbative theory (§3.4) and in energy-flux arguments. What survives the no-go: arguments using the *exact* structure of the Biot–Savart law and vortex stretching (e.g. geometric depletion [CF93], the axisymmetric maximum principles §3.6), and arguments using viscosity non-perturbatively (backward uniqueness/Carleman, [ESS03], [Tao21]). This is not a proof that NS is hard; it is a proof that a *specific, popular class of proofs* cannot exist — the mission's "no-go for a popular method", delivered at the maximal rigor the literature supports. `[SYNTHESIS]`

---

## 6. Candidate New Material, Failed Attacks, Honesty Audit

### 6.1 What in this dossier might be new

Nothing at theorem level. Specific items audited:

- Theorems 5.1–5.3 and their proofs: **known** (Fujita–Kato 1964; Leray 1934). Value: complete, constant-explicit write-ups in one place, aligned notation, honest scoping of every cited lemma. `[KNOWN — proofs written out here]`
- Proposition 5.4: the underlying theorem is Tao's `[KNOWN]`; the formalization as an interface-based no-go is a **synthesis** that we believe matches how experts already read [Tao16] (cf. Tao's own commentary [Tao07]). Not claimed as new. `[SYNTHESIS]`
- §3.5 "why CKN is stuck at dimension 1" and §3.7 "self-similar exclusion breaks the numerics-to-proof pipeline for NS": folklore-level observations assembled explicitly. `[SYNTHESIS — likely folklore]`
- The constraints checklist (§6.3): assembly is ours; every constraint is enforced by a cited theorem. `[SYNTHESIS]`

### 6.2 Failed attacks from this run `[FAILED ATTACK — recorded for future legions]`

1. **Coherence-weighted enstrophy.** Idea: weight the enstrophy inequality (Lemma 5.2.2) by a functional of the vorticity direction's local Lipschitz constant, hoping the Constantin–Fefferman mechanism [CF93] turns the conditional criterion into an unconditional interpolation gain. Failure: the coherence hypothesis enters as an $L^\infty$-type assumption on $\nabla(\omega/|\omega|)$ in high-vorticity regions; any attempt to *bound* that quantity by energy-controlled norms reintroduces exactly the supercritical gap (the direction field costs one derivative of $\omega$ where $|\omega|$ is small). No inequality closed. Post-hoc explanation: a closure here would be an energy-abstract argument in the sense of §5.4 unless the Biot–Savart geometry enters quantitatively, which we did not achieve.
2. **Interpolating [Ser12] with [Tao21] for an unconditional bound.** Idea: combine Seregin's $\|u(t)\|_{L^3}\to\infty$ with Tao's triple-log lower rate to squeeze a contradiction against the energy inequality (the $L^3$ norm is bounded by interpolation $\|u\|_{L^3}\le\|u\|_{L^2}^{1/2}\|u\|_{L^6}^{1/2}$ with energy-dissipation control *in time average*). Failure: the interpolation gives only $u\in L^4_tL^3_x$ globally — a time-averaged bound; blow-up of the *pointwise-in-time* $L^3$ norm on a $(T-t)$-shrinking set is fully consistent with it. The scaling bookkeeping shows the gap is again exactly one factor of criticality. No contradiction is available at any rate slower than $(T-t)^{-1/4}$-type in $L^3$, far beyond [Tao21].
3. **Localizing CKN below dimension 1.** Idea: re-run the CKN iteration with the local energy replaced by a pressure-flux-corrected quantity, hoping for $r^{1+\delta}$ decay. Failure: every candidate corrected quantity we wrote down either (a) fails scale-covariance (so the iteration doesn't telescope), or (b) is scale-covariant with the *same* $r^1$ weight — consistent with the §3.5 folklore that dimension 1 is the exact shadow of the energy inequality. This matches the historical record (only logarithmic improvements since 1982).

### 6.3 Constraints checklist for any future successful method `[SYNTHESIS]`

A proof of Clay (A)/(B) must simultaneously:
1. **Break energy-abstraction** (§5.4): use the exact nonlinearity — Biot–Savart kernel structure, vortex-stretching geometry, or special scalar quantities with maximum principles ($ru_\theta$; $\omega_\theta/r$).
2. **Beat scaling non-perturbatively**: produce a bound on some critical-or-subcritical quantity for *large* data — no size-based function space can carry the argument (§3.4).
3. **Survive the weak-formulation pathologies**: whatever compactness or limiting procedures are used must propagate strictly more than distributional structure (§3.3).
4. **Use viscosity as more than a regularizer**: the Euler analogue must fail or be irrelevant to the argument (Euler likely blows up, §3.9); mechanisms of ESS type (backward uniqueness, Carleman) are the proven template (§3.2).

A proof of Clay (C)/(D) must simultaneously:
1. Construct **Type II, non-self-similar** dynamics ([NRS96, Tsa98]; §3.6) — no stationary profile in self-similar variables;
2. defeat the **triple-log** lower-bound environment of [Tao21] (its quantitative pieces constrain any construction's norm growth);
3. either avoid axisymmetry or produce axisymmetric blow-up **on the axis at Type II rates** (§3.5–3.6);
4. if computer-assisted, develop certification for **time-dependent (non-stationary) renormalized profiles** — technology that does not exist yet (§3.7).

### 6.4 Speculative directions `[SPECULATIVE — no claims]`

- **Dynamical mild-solution classes**: well-posedness classes defined by coherence functionals (direction regularity of $\omega$, spectral concentration) rather than norms; the obstacle is a product estimate replacing Lemma 5.1.3 in which the coherence functional is propagated by the flow. Nothing proved.
- **Quantitative axisymmetric program**: combine the $\Gamma=ru_\theta$ maximum principle with [Tao21]-style Carleman quantification near the axis, aiming at "axisymmetric + bounded $\Gamma$ ⇒ no Type II on the axis". The known Liouville technology [KNSS09] covers Type I only; the Type II Liouville statement needed is open and possibly false.
- **Porting Chen–Hou certification to NS**: requires renormalization group flow on profile *space* (profiles drifting with scale), i.e. certified control of a PDE on an infinite-dimensional slow manifold. Flagged as the single most concrete (if distant) blow-up-side program.

### 6.5 Final verdict (program rubric)

**known / expository-synthesis.** Rigorous deliverables: §5.1–5.3 (complete proofs of known theorems, per the mission's special-case-theorem option) and §5.4 (formalized known no-go). No candidate breakthrough; no fake regularity proof; all conditionality explicitly labelled.

---

## 7. References

Citations verified by web search during this run are marked ✓. For a few older items, page ranges are omitted where memory confidence was insufficient; no reference below is invented.

- [ABC22] D. Albritton, E. Brué, M. Colombo, *Non-uniqueness of Leray solutions of the forced Navier–Stokes equations*, Ann. of Math. 196 (2022).
- [BCD11] H. Bahouri, J.-Y. Chemin, R. Danchin, *Fourier Analysis and Nonlinear Partial Differential Equations*, Springer, 2011.
- [BdV95] H. Beirão da Veiga, *A new regularity class for the Navier–Stokes equations in $\mathbb{R}^n$*, Chinese Ann. Math. Ser. B 16 (1995).
- [BKM84] J. T. Beale, T. Kato, A. Majda, *Remarks on the breakdown of smooth solutions for the 3-D Euler equations*, Comm. Math. Phys. 94 (1984), 61–66.
- [BP08] J. Bourgain, N. Pavlović, *Ill-posedness of the Navier–Stokes equations in a critical space in 3D*, J. Funct. Anal. 255 (2008), 2233–2247.
- [BDLSV19] T. Buckmaster, C. De Lellis, L. Székelyhidi Jr., V. Vicol, *Onsager's conjecture for admissible weak solutions*, Comm. Pure Appl. Math. 72 (2019).
- [BV19] T. Buckmaster, V. Vicol, *Nonuniqueness of weak solutions to the Navier–Stokes equation*, Ann. of Math. 189 (2019), 101–144.
- [CKN82] L. Caffarelli, R. Kohn, L. Nirenberg, *Partial regularity of suitable weak solutions of the Navier–Stokes equations*, Comm. Pure Appl. Math. 35 (1982), 771–831.
- [CET94] P. Constantin, W. E, E. S. Titi, *Onsager's conjecture on the energy conservation for solutions of Euler's equation*, Comm. Math. Phys. 165 (1994), 207–209.
- [CF93] P. Constantin, C. Fefferman, *Direction of vorticity and the problem of global regularity for the Navier–Stokes equations*, Indiana Univ. Math. J. 42 (1993).
- [CH25] J. Chen, T. Y. Hou, *Stable nearly self-similar blowup of the 2D Boussinesq and 3D Euler equations with smooth data*, Part I: arXiv:2210.07191; Part II: Multiscale Model. Simul. 23 (2025), 25–130. ✓
- [CL22] A. Cheskidov, X. Luo, *Sharp nonuniqueness for the Navier–Stokes equations*, Invent. Math. 229 (2022).
- [CSTY08] C.-C. Chen, R. M. Strain, H.-T. Yau, T.-P. Tsai, *Lower bound on the blow-up rate of the axisymmetric Navier–Stokes equations*, Int. Math. Res. Not. (2008).
- [CSTY09] C.-C. Chen, R. M. Strain, T.-P. Tsai, H.-T. Yau, *Lower bounds on the blow-up rate of the axisymmetric Navier–Stokes equations II*, Comm. Partial Differential Equations 34 (2009).
- [DLS09] C. De Lellis, L. Székelyhidi Jr., *The Euler equations as a differential inclusion*, Ann. of Math. 170 (2009).
- [DPD03] G. Da Prato, A. Debussche, *Ergodicity for the 3D stochastic Navier–Stokes equations*, J. Math. Pures Appl. 82 (2003).
- [Elg21] T. M. Elgindi, *Finite-time singularity formation for $C^{1,\alpha}$ solutions to the incompressible Euler equations on $\mathbb{R}^3$*, Ann. of Math. 194 (2021).
- [ESS03] L. Escauriaza, G. Seregin, V. Šverák, *$L_{3,\infty}$-solutions of Navier–Stokes equations and backward uniqueness*, Russian Math. Surveys 58 (2003), 211–250.
- [Fef00] C. L. Fefferman, *Existence and smoothness of the Navier–Stokes equation*, Clay Mathematics Institute Millennium Prize problem description, 2000.
- [FG95] F. Flandoli, D. Gątarek, *Martingale and stationary solutions for stochastic Navier–Stokes equations*, Probab. Theory Related Fields 102 (1995).
- [FGP10] F. Flandoli, M. Gubinelli, E. Priola, *Well-posedness of the transport equation by stochastic perturbation*, Invent. Math. 180 (2010).
- [FK64] H. Fujita, T. Kato, *On the Navier–Stokes initial value problem I*, Arch. Rational Mech. Anal. 16 (1964), 269–315.
- [FR08] F. Flandoli, M. Romito, *Markov selections for the 3D stochastic Navier–Stokes equations*, Probab. Theory Related Fields 140 (2008).
- [GKP16] I. Gallagher, G. S. Koch, F. Planchon, *Blow-up of critical Besov norms at a potential Navier–Stokes singularity*, Comm. Math. Phys. 343 (2016).
- [GPS07] P. Germain, N. Pavlović, G. Staffilani, *Regularity of solutions to the Navier–Stokes equations evolving from small data in $BMO^{-1}$*, Int. Math. Res. Not. (2007).
- [GS17] J. Guillod, V. Šverák, *Numerical investigations of non-uniqueness for the Navier–Stokes initial value problem in borderline spaces*, arXiv:1704.00560.
- [HL06] T. Y. Hou, R. Li, *Dynamic depletion of vortex stretching and non-blowup of the 3-D incompressible Euler equations*, J. Nonlinear Sci. 16 (2006).
- [HM06] M. Hairer, J. C. Mattingly, *Ergodicity of the 2D Navier–Stokes equations with degenerate stochastic forcing*, Ann. of Math. 164 (2006), 993–1032.
- [Hop51] E. Hopf, *Über die Anfangswertaufgabe für die hydrodynamischen Grundgleichungen*, Math. Nachr. 4 (1951), 213–231.
- [Hou23] T. Y. Hou, *Potentially singular behavior of the 3D Navier–Stokes equations*, Found. Comput. Math. 23 (2023); arXiv:2107.06509.
- [HZZ23] M. Hofmanová, R. Zhu, X. Zhu, *Global-in-time probabilistically strong and Markov solutions to stochastic 3D Navier–Stokes equations: existence and nonuniqueness*, Ann. Probab. 51 (2023), 524–579. ✓
- [HZZ24] M. Hofmanová, R. Zhu, X. Zhu, *Nonuniqueness in law of stochastic 3D Navier–Stokes equations*, J. Eur. Math. Soc. 26 (2024), 163–260. ✓
- [Ise18] P. Isett, *A proof of Onsager's conjecture*, Ann. of Math. 188 (2018), 871–963.
- [JS14] H. Jia, V. Šverák, *Local-in-space estimates near initial time for weak solutions of the Navier–Stokes equations and forward self-similar solutions*, Invent. Math. 196 (2014).
- [JS15] H. Jia, V. Šverák, *Are the incompressible 3d Navier–Stokes equations locally ill-posed in the natural energy space?*, J. Funct. Anal. 268 (2015).
- [Kat84] T. Kato, *Strong $L^p$-solutions of the Navier–Stokes equation in $\mathbb{R}^m$, with applications to weak solutions*, Math. Z. 187 (1984), 471–480.
- [KNSS09] G. Koch, N. Nadirashvili, G. Seregin, V. Šverák, *Liouville theorems for the Navier–Stokes equations and applications*, Acta Math. 203 (2009), 83–105.
- [KP02] N. H. Katz, N. Pavlović, *A cheap Caffarelli–Kohn–Nirenberg inequality for the Navier–Stokes equation with hyper-dissipation*, Geom. Funct. Anal. 12 (2002).
- [KS14] A. Kiselev, V. Šverák, *Small scale creation for solutions of the incompressible two-dimensional Euler equation*, Ann. of Math. 180 (2014).
- [KT01] H. Koch, D. Tataru, *Well-posedness for the Navier–Stokes equations*, Adv. Math. 157 (2001), 22–35.
- [Lad68] O. A. Ladyzhenskaya, *Unique global solvability of the three-dimensional Cauchy problem for the Navier–Stokes equations in the presence of axial symmetry*, Zap. Nauchn. Sem. LOMI 7 (1968) (Russian).
- [Lad69] O. A. Ladyzhenskaya, *The Mathematical Theory of Viscous Incompressible Flow*, Gordon and Breach, 1969.
- [Ler34] J. Leray, *Sur le mouvement d'un liquide visqueux emplissant l'espace*, Acta Math. 63 (1934), 193–248.
- [Lin98] F.-H. Lin, *A new proof of the Caffarelli–Kohn–Nirenberg theorem*, Comm. Pure Appl. Math. 51 (1998), 241–257.
- [Lio69] J.-L. Lions, *Quelques méthodes de résolution des problèmes aux limites non linéaires*, Dunod, 1969.
- [LL11] Z. Lei, F.-H. Lin, *Global mild solutions of Navier–Stokes equations*, Comm. Pure Appl. Math. 64 (2011).
- [LH14a] G. Luo, T. Y. Hou, *Potentially singular solutions of the 3D axisymmetric Euler equations*, Proc. Natl. Acad. Sci. USA 111 (2014), 12968–12973.
- [LH14b] G. Luo, T. Y. Hou, *Toward the finite-time blowup of the 3D axisymmetric Euler equations: a numerical investigation*, Multiscale Model. Simul. 12 (2014).
- [LR16] P. G. Lemarié-Rieusset, *The Navier–Stokes Problem in the 21st Century*, CRC Press, 2016.
- [LS99] O. A. Ladyzhenskaya, G. A. Seregin, *On partial regularity of suitable weak solutions to the three-dimensional Navier–Stokes equations*, J. Math. Fluid Mech. 1 (1999).
- [Mil20] E. Miller, *A regularity criterion for the Navier–Stokes equation involving only the middle eigenvalue of the strain tensor*, Arch. Ration. Mech. Anal. 235 (2020).
- [MS01] S. Montgomery-Smith, *Finite time blow up for a Navier–Stokes like equation*, Proc. Amer. Math. Soc. 129 (2001).
- [NPS13] A. R. Nahmod, N. Pavlović, G. Staffilani, *Almost sure existence of global weak solutions for supercritical Navier–Stokes equations*, SIAM J. Math. Anal. 45 (2013).
- [NRS96] J. Nečas, M. Růžička, V. Šverák, *On Leray's self-similar solutions of the Navier–Stokes equations*, Acta Math. 176 (1996), 283–294.
- [Ons49] L. Onsager, *Statistical hydrodynamics*, Nuovo Cimento (Supplemento) 6 (1949), 279–287.
- [Pro59] G. Prodi, *Un teorema di unicità per le equazioni di Navier–Stokes*, Ann. Mat. Pura Appl. 48 (1959), 173–182.
- [RRS16] J. C. Robinson, J. L. Rodrigo, W. Sadowski, *The Three-Dimensional Navier–Stokes Equations*, Cambridge University Press, 2016.
- [RS11] W. Rusin, V. Šverák, *Minimal initial data for potential Navier–Stokes singularities*, J. Funct. Anal. 260 (2011).
- [Sch77] V. Scheffer, *Hausdorff measure and the Navier–Stokes equations*, Comm. Math. Phys. 55 (1977), 97–112.
- [Sch93] V. Scheffer, *An inviscid flow with compact support in space-time*, J. Geom. Anal. 3 (1993).
- [Ser62] J. Serrin, *On the interior regularity of weak solutions of the Navier–Stokes equations*, Arch. Rational Mech. Anal. 9 (1962), 187–195.
- [Ser12] G. Seregin, *A certain necessary condition of potential blow up for Navier–Stokes equations*, Comm. Math. Phys. 312 (2012), 833–845.
- [Shn97] A. Shnirelman, *On the nonuniqueness of weak solution of the Euler equation*, Comm. Pure Appl. Math. 50 (1997).
- [Tao07] T. Tao, *Why global regularity for Navier–Stokes is hard*, blog essay, terrytao.wordpress.com, 2007.
- [Tao09] T. Tao, *Global regularity for a logarithmically supercritical hyperdissipative Navier–Stokes equation*, Anal. PDE 2 (2009), 361–366.
- [Tao16] T. Tao, *Finite time blowup for an averaged three-dimensional Navier–Stokes equation*, J. Amer. Math. Soc. 29 (2016), 601–674.
- [Tao21] T. Tao, *Quantitative bounds for critically bounded solutions to the Navier–Stokes equations*, in: Nine Mathematical Challenges — An Elucidation, Proc. Sympos. Pure Math. 104, Amer. Math. Soc., 2021, 149–193. ✓
- [Tsa98] T.-P. Tsai, *On Leray's self-similar solutions of the Navier–Stokes equations satisfying local energy estimates*, Arch. Rational Mech. Anal. 143 (1998), 29–51.
- [UY68] M. R. Ukhovskii, V. I. Yudovich, *Axially symmetric flows of ideal and viscous fluids filling the whole space*, J. Appl. Math. Mech. 32 (1968).
- [Vas07] A. Vasseur, *A new proof of partial regularity of solutions to Navier–Stokes equations*, NoDEA Nonlinear Differential Equations Appl. 14 (2007).

*Angle-to-source map:* 05-01 → [Fef00, Ler34, Hop51, CKN82, Pro59, Ser62, BV19, ABC22, JS14, JS15, GS17]; 05-02 → [BKM84, Pro59, Ser62, BdV95, CF93, Mil20, ESS03, Ser12, GKP16, Tao21]; 05-03 → [Ons49, CET94, Ise18, DLS09, BDLSV19, BV19, CL22, Sch93, Shn97]; 05-04 → [FK64, Kat84, KT01, GPS07, BP08, LL11, LR16, BCD11]; 05-05 → [Sch77, CKN82, Lin98, LS99, Vas07]; 05-06 → [Lad68, UY68, CSTY08, CSTY09, KNSS09]; 05-07 → [HL06, LH14a, LH14b, CH25, Hou23, Elg21, NRS96, Tsa98]; 05-08 → [FG95, FR08, DPD03, HM06, HZZ23, HZZ24, FGP10, NPS13]; 05-09 → [Elg21, CH25, KS14, BKM84, RRS16]; 05-10 → [Lio69, Tao09, KP02, MS01, Tao16, Tao07, RS11].
