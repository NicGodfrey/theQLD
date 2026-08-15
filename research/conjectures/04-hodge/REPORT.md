# LEGION 04 — THE HODGE CONJECTURE
## Commander's Report

**Workspace:** `/workspace/research/conjectures/04-hodge/`
**Date:** 2026-08-15
**Mission:** Attack the Hodge conjecture. No fake proof. Deliverable: a new proved special case, a new obstruction class, or a precise reduction to a checkable Hodge class on a specific variety with a viable cycle-construction plan.

**Mission execution note (honesty).** The tasking called for 10 nested subagents (04-01 … 04-10). No subagent-spawning tool was available in this session, so the commander executed all ten angle investigations directly and sequentially, with live literature verification (web searches against arXiv, journal pages, and author preprints performed during this mission). The ten angles are reported in Section 3 exactly as tasked.

**Honesty labels used throughout:**

- **[PROVED — classical]** — established theorem; standard reference; details stable in the literature.
- **[PROVED — recent, verified]** — recent theorem whose statement was verified against primary sources (arXiv/journal pages) during this mission.
- **[REPORTED]** — claim found in a reliable source during this mission but not independently checked in detail.
- **[MEMORY]** — statement or citation from the commander's training knowledge, not re-verified this mission; check before external use.
- **[REDUCTION]** — a precise, proved equivalence or implication (with attribution).
- **[PROGRAM]** — a proposed strategy; plausible but NOT executed; no claim of proof.
- **[HEURISTIC]** — plausibility argument, not a proof.
- **[OPEN]** — genuinely open as far as this mission could determine.

**No new theorem is proved in this report.** The deliverable is of the third permitted type: precise reductions to checkable Hodge classes on specific varieties, with cycle-construction plans (Section 4), plus a verified map of the post-2023 frontier, which has moved substantially (Section 2).

---

## 1. Statement of the problem

### 1.1 The conjecture

Let \(X\) be a smooth complex projective variety of dimension \(n\). For \(0 \le k \le n\) define the group of **rational Hodge classes** of degree \(2k\):

\[ \mathrm{Hdg}^k(X) := H^{2k}(X,\mathbb{Q}) \cap H^{k,k}(X) \subset H^{2k}(X,\mathbb{C}). \]

The cycle class map \(\mathrm{cl}: \mathrm{CH}^k(X)\otimes\mathbb{Q} \to H^{2k}(X,\mathbb{Q})\) lands in \(\mathrm{Hdg}^k(X)\).

> **Hodge Conjecture (HC).** For every smooth complex projective \(X\) and every \(k\), the map \(\mathrm{cl}: \mathrm{CH}^k(X)\otimes\mathbb{Q} \to \mathrm{Hdg}^k(X)\) is **surjective**: every rational \((k,k)\)-class is a \(\mathbb{Q}\)-linear combination of classes of algebraic subvarieties of codimension \(k\).

We write HC\((k)\) for the statement in codimension \(k\) on a given \(X\). [PROVED — classical: this is the standard modern formulation, descending from Hodge's 1950 ICM address.]

### 1.2 Integral vs. rational — the rational coefficients are essential

The integral statement (surjectivity onto \(H^{2k}(X,\mathbb{Z}) \cap H^{k,k}\), "IHC") is **false**, in several genuinely different ways:

- **Torsion obstruction.** Atiyah–Hirzebruch (1962) produced torsion classes (detected by Steenrod operations) that are not algebraic; Totaro (1997) reinterpreted and strengthened this via complex cobordism: the cycle map factors through \(MU^{2k}(X)\otimes_{MU^*}\mathbb{Z}\), giving a whole hierarchy of obstructions. Soulé–Voisin gave 5-dimensional examples. [PROVED — classical]
- **Degree obstruction on non-torsion classes.** Kollár (1992, Trento examples): on a very general hypersurface \(X_d \subset \mathbb{P}^4\) of suitable composite degree (e.g. \(p^3 \mid d\), \(p \ge 5\) prime), every algebraic curve has degree divisible by \(p\), while \(H_2(X,\mathbb{Z})\cong\mathbb{Z}\) with a degree-1 generator: that generator is a non-torsion, non-algebraic integral Hodge class. Rational HC is trivially true there. [PROVED — classical; divisibility hypothesis quoted from memory]
- **Kodaira dimension zero.** Benoist–Ottem (Comment. Math. Helv. 95 (2020)): IHC for 1-cycles fails on \(S \times B\), \(S\) an Enriques surface, \(B\) a very general curve of genus \(\ge 1\); first failures in Kodaira dimension 0 and first non-algebraic degree-4 torsion classes on threefolds. Sharp against Voisin's positive results (§3, angle 04-05). [PROVED — recent, verified]

So HC is irreducibly a statement about **cycles with denominators**; any correct proof must construct cycles only up to a multiple. The failure modes of IHC (the "defect groups" \(Z^{2k}(X) := \mathrm{Hdg}^{2k}_{\mathbb{Z}}(X)/\mathrm{im}(\mathrm{cl}_{\mathbb{Z}})\)) are themselves now structured objects: birational invariants in key degrees, computed by unramified cohomology in favorable cases (Colliot-Thélène–Voisin, Duke 2012). [PROVED — classical/recent mix]

### 1.3 Projectivity is essential — the Kähler statement is false

Voisin (IMRN 2002): there exist compact Kähler manifolds (4-dimensional complex tori of Weil type) carrying rational Hodge classes of type (2,2) that are **not** in the algebra generated by Chern classes of coherent analytic sheaves — the weakest reasonable Kähler analogue of "algebraic". So HC, if true, is true for reasons that use projectivity/arithmetic essentially, not merely Kähler Hodge theory. [PROVED — classical, verified via Voisin's 2025 survey reference list]

### 1.4 Grothendieck's amended (generalized) Hodge conjecture

Hodge also proposed a "generalized" version for coniveau: that \(F^cH^k(X,\mathbb{C}) \cap H^k(X,\mathbb{Q})\) should be supported on a codimension-\(c\) subvariety. Grothendieck ("Hodge's general conjecture is false for trivial reasons", Topology 8 (1969)) showed this is false as stated — \(F^c \cap H^k(X,\mathbb{Q})\) need not even be a sub-Hodge structure — and posed the corrected statement:

> **Generalized Hodge Conjecture (GHC), Grothendieck's form.** For every sub-Hodge structure \(L \subset H^k(X,\mathbb{Q})\) with \(L_{\mathbb{C}} \subset F^cH^k(X,\mathbb{C})\), there is a closed algebraic subset \(Z \subset X\) of codimension \(\ge c\) with \(L\) supported on \(Z\) (i.e. \(L \subset \ker(H^k(X,\mathbb{Q}) \to H^k(X\setminus Z,\mathbb{Q}))\)).

GHC contains HC (take \(k=2c\), \(L\) the span of a Hodge class) and is open even in the first genuinely new cases (e.g. coniveau of the transcendental \(H^3\) of threefolds). [PROVED — classical for the falsity and the corrected formulation; the GHC itself OPEN]

### 1.5 The variational form

The **variational Hodge conjecture** (Grothendieck): if a cycle class deforms as a flat/Hodge section in a family, it stays algebraic. It is implied by HC and is the natural target of all deformation-theoretic attacks (semiregularity — Bloch, Buchweitz–Flenner). Markman's 2025 breakthrough (Section 2) is precisely a successful execution of the variational strategy on a specific 9-dimensional family. For abelian varieties, the variational form is known to imply the full HC. [MEMORY for the last implication; the rest PROVED — classical]

---

## 2. Known theorems: the current proved perimeter

Ordered roughly from classical to 2025-frontier. Items marked ★ were verified against primary sources during this mission.

**Universal statements (all \(X\)):**

1. **Lefschetz (1,1)** — HC\((1)\), integrally: every class in \(H^2(X,\mathbb{Z}) \cap H^{1,1}\) is a divisor class. (Lefschetz 1924; modern proof via the exponential sequence.) [PROVED — classical]
2. **HC\((n-1)\)** (1-cycles) — by hard Lefschetz \(L^{n-2}: H^2 \xrightarrow{\sim} H^{2n-2}\) (rational coefficients) combined with (1,1). Consequently **HC holds for all varieties of dimension \(\le 3\)**. [PROVED — classical]
3. **Cattani–Deligne–Kaplan (JAMS 1995)** — Hodge loci are algebraic: in any polarized variation of Hodge structure over a quasi-projective base, the locus where a given class stays Hodge is a countable union of algebraic subvarieties. The single strongest unconditional consistency check for HC. [PROVED — classical]
4. ★ **Baldi–Klingler–Ullmo (Invent. math. 2024)** — refined structure of the Hodge locus: the atypical part is a *finite* union of maximal special subvarieties; for variations of level \(\ge 3\) the positive-period-dimension Hodge locus is algebraic (finite union); in level 1–2 the typical Hodge locus, if nonempty, is analytically dense. [PROVED — recent, verified]

**Families of varieties:**

5. **Fourfolds with small \(\mathrm{CH}_0\)** — HC\((2)\) holds if \(\mathrm{CH}_0(X)\) is supported on a threefold (Bloch–Srinivas 1983, decomposition of the diagonal); in particular for uniruled and unirational fourfolds (also Conte–Murre 1978 directly). Zucker (1977) for cubic fourfolds via normal functions. [PROVED — classical]
6. **Abelian varieties, structural results** — Hodge classes on abelian varieties are *absolute Hodge* (Deligne 1982) and *motivated* (André 1996). Tankeev: HC for simple abelian varieties of prime dimension. Moonen–Zarhin (1995, 1999): classification of Hodge classes on abelian varieties of low dimension; on abelian fourfolds all Hodge classes are generated by divisor classes and Weil classes. [PROVED — classical]
7. ★ **Markman (2023)** — Hodge–Weil classes are algebraic for every abelian fourfold of Weil type with trivial discriminant (any imaginary quadratic field \(K\)), via hyperholomorphic sheaves on hyper-Kähler manifolds of generalized Kummer type and the Markman–O'Grady link between Weil fourfolds and intermediate Jacobians of Kummer-type varieties. Earlier sporadic cases: Schoen (1988, 1998) for \(K=\mathbb{Q}(\sqrt{-3})\) (arbitrary discriminant) and \(K=\mathbb{Q}(i)\) (discriminant 1; also van Geemen). [PROVED — recent, verified]
8. ★ **Markman (arXiv 2502.03415, "Cycles on abelian 2n-folds of Weil type from secant sheaves on abelian n-folds", 2025)** — via **secant sheaves** and the Buchweitz–Flenner semiregularity theorem: for every imaginary quadratic \(K=\mathbb{Q}(\sqrt{-d})\), the Hodge–Weil classes are algebraic on the 9-dimensional family of polarized abelian **sixfolds** of Weil type with discriminant \(-1\); by a specialization argument this yields algebraicity of Hodge–Weil classes on abelian **fourfolds** of Weil type with **arbitrary discriminant**. Combined with Moonen–Zarhin (item 6): **the Hodge conjecture holds for all abelian fourfolds.** (Preprint; widely cited as correct by Voisin's 2025 survey and by Floccari–Fu 2026, but label: [PROVED — recent, verified statement; peer-review status of the 2025 preprint not confirmed this mission].)
9. ★ **Floccari (2023, arXiv 2308.02267)** — HC (and the Tate conjecture) for **all six-dimensional hyper-Kähler varieties of generalized Kummer type** — the first locally complete families of projective varieties of dimension \(>2\) with \(h^{2,0}\neq 0\) where HC is fully verified. Mechanism: a K3 surface \(S_K\) canonically associated to the sixfold, with an algebraic correspondence reducing HC to powers of \(S_K\). Fourfolds of Kum\(^2\)-type follow by combining with Foster and Varesco. ★ Floccari–Fu (J. Math. Pures Appl. 2026): independent proof via singular OG6 varieties; HC and Tate for all OG6-type varieties of that construction and their powers. [PROVED — recent, verified]
10. ★ **Floccari (2504.13607-adjacent, verified via Floccari–Fu intro)** — HC for **all powers** of any abelian fourfold of Weil type with discriminant 1. [PROVED — recent, verified]
11. ★ **Buskin (Crelle 2019)** — every rational Hodge isometry \(H^2(S_1,\mathbb{Q}) \to H^2(S_2,\mathbb{Q})\) between projective K3 surfaces is algebraic (Shafarevich's 1970 ICM conjecture); Huybrechts strengthened this motivically. Corollary: HC for \(S\times S\) when the transcendental endomorphism field of \(S\) is CM. Markman extended Hodge-isometry algebraicity to K3\(^{[n]}\)-type hyper-Kähler varieties [MEMORY for this last extension]. [PROVED — recent, verified]
12. **Fermat varieties** — Shioda–Katsura inductive structure (1979); HC for Fermat varieties \(X^n_m\) whenever the combinatorial condition \((P_m)\) holds — verified for \(m \le 20\); Aoki (1987): also for \(m=p^2\) via "standard cycles" beyond the inductive structure. ★ da Silva (2021): HC for Fermat **fourfolds** \(X^4_m\) for all \(m \le 100\) coprime to 6; and \((P_{33})\) is **false** with an explicit witness not of standard type (see Section 4, Target B). [PROVED — classical + recent, verified]
13. **Integral HC, positive direction** — Voisin (2006): IHC for 1-cycles on uniruled and K-trivial threefolds (with Totaro's later strengthening [MEMORY for the exact scope]); ★ Voisin (2007) for cubic fourfolds in degree 4, reproved and extended to Gushel–Mukai fourfolds by Perry (Compositio 2022) via 2-dimensional Calabi–Yau categories (a categorical variational IHC); Mongardi–Ottem: IHC for 1-cycles on hyper-Kähler varieties of K3\(^{[n]}\) and generalized Kummer type [MEMORY]. [mixed labels as marked]
14. **Standard-conjecture side** — Lefschetz standard conjecture B(X) known for abelian varieties (Lieberman), surfaces, flag varieties, and ★ hyper-Kähler varieties of K3\(^{[n]}\)-type (Charles–Markman, Compositio 2013); Künneth over finite fields (Katz–Messing 1974); ★ Ancona (Invent. math. 2021): the standard conjecture of Hodge type for abelian fourfolds in positive characteristic; with Clozel (1999): numerical = \(\ell\)-adic homological equivalence on abelian fourfolds for infinitely many \(\ell\). [PROVED — classical + recent, verified]

**Reading of the perimeter.** Every single positive entry above lives in the world of **abelian motives and level \(\le 2\) Hodge structures** (divisors, abelian varieties, K3s and their Hilbert/Kummer relatives, Fermat = CM motives), or follows from small Chow groups. There is still not one verified nontrivial Hodge class on, say, a general-type hypersurface with large level. That asymmetry is quantified in Section 6.

---

## 3. Nested findings (angles 04-01 … 04-10)

### 04-01 — Precise statement; integral vs. rational; Grothendieck's refinement; generalized Hodge

Covered in Section 1 in full. Additional findings:

- The conjecture is equivalent to its restriction to (a) middle degree \(2k=n\) on even-dimensional varieties (by taking products with projective spaces and hyperplane sections — standard reductions [PROVED — classical]), and (b) \(\mathbb{Q}\)-spanning by *irreducible subvarieties*; no strengthening to effective classes is possible.
- **Finding (structural):** the three known failure modes of the integral statement (torsion/cobordism, degree divisibility, Enriques-type 2-torsion) are *all* annihilated by \(\otimes\mathbb{Q}\), and no rational-coefficient obstruction formalism exists in the literature. This mission also failed to produce one (see Section 4.3 for the honest negative result and what it would have to look like). [ASSESSMENT]
- GHC status: open even for coniveau-1 statements on general threefolds; Voisin (2015 [MEMORY]) proved GHC and the generalized Bloch conjecture are *equivalent* for general complete intersections — evidence that GHC is entangled with Chow-group structure (angle 04-07).

### 04-02 — Lefschetz (1,1): the only fully settled degree

- The (1,1) theorem is the unique degree where the **integral** statement holds and the unique degree with a *cohomological mechanism*: the exponential sequence \(0 \to \mathbb{Z} \to \mathcal{O}_X \to \mathcal{O}_X^* \to 0\) identifies \(\mathrm{NS}(X)\) with the kernel of \(H^2(X,\mathbb{Z}) \to H^2(X,\mathcal{O}_X)\), and Hodge theory identifies that kernel (mod torsion) with the integral (1,1) classes. [PROVED — classical]
- **Why it does not generalize:** for \(k\ge 2\) the sought classes are not the kernel of any map of sheaf cohomologies induced by a short exact sequence of sheaves on \(X\); higher analogues of \(\mathcal{O}^*\) (gerbes, \(H^2(X,\mathcal{O}_X^*)\)) compute Brauer-type invariants, not codimension-2 cycles. The torsion counterexamples (04-01) *prove* no such integral mechanism can exist in higher codimension. [ASSESSMENT, standard]
- Lefschetz's own 1924 proof went through **normal functions** attached to Lefschetz pencils — historically important because it is the template for the Green–Griffiths program (04-04), the only known plan that would prove HC in *all* degrees at once.
- Degree \(2n-2\) (1-cycles) follows rationally by hard Lefschetz; note the inverse \((L^{n-2})^{-1}\) is not known to be induced by a correspondence (that is conjecture B, angle 04-10) — the argument works because it transports *classes*, not cycles, and lands in degree 2 where (1,1) is available. It fails integrally (Kollár, 04-01). [PROVED — classical]

### 04-03 — Standard conjectures, hard Lefschetz, motives

- Grothendieck's standard conjectures (Bombay 1968): **A** (Lefschetz type, algebraicity of \(\Lambda\)-inverses), **B** (algebraicity of the Lefschetz operator inverse \(\Lambda\) as a correspondence), **C** (Künneth projectors algebraic), **D** (homological = numerical equivalence), **Hdg** (Hodge-type positivity). Over \(\mathbb{C}\): Hdg holds (Hodge index/Hodge–Riemann); B \(\Rightarrow\) A, C; B + Hdg \(\Rightarrow\) D (Kleiman). [PROVED — classical]
- **HC \(\Rightarrow\) B over \(\mathbb{C}\):** \(\Lambda\) and the Künneth projectors are Hodge classes on \(X\times X\) (they are morphisms of Hodge structures), so HC makes them algebraic. B in turn is *far* weaker than HC — this is the correct formalization of "the standard conjectures are the real wall" (angle 04-10). [PROVED — classical implication]
- Known cases of B: abelian varieties (Lieberman 1968), surfaces, generalized flag varieties, varieties with algebraic cohomology, K3\(^{[n]}\)-type hyper-Kähler varieties (Charles–Markman 2013 ★). Künneth (C) over finite fields: Katz–Messing 1974 from Deligne's Weil I. [PROVED — classical/recent, verified]
- **Motives:** with D (or B), Grothendieck's category of pure motives becomes (graded) semisimple abelian (unconditionally proved for numerical motives by Jannsen 1992); André's *motivated cycles* (IHES 1996) build an unconditional semisimple Tannakian theory by formally adjoining \(\Lambda\) — inside it, all Hodge classes on abelian varieties are motivated. Every recent breakthrough (Markman, Floccari) can be read as promoting specific motivated classes to algebraic ones. [PROVED — classical]

### 04-04 — Intermediate Jacobians, Abel–Jacobi, normal functions

- Griffiths' intermediate Jacobian \(J^{2k-1}(X) = H^{2k-1}(X,\mathbb{C})/(F^k + H^{2k-1}(X,\mathbb{Z}))\) and Abel–Jacobi maps \(AJ: \mathrm{CH}^k(X)_{\hom} \to J^{2k-1}(X)\) refine the cycle class map. Key phenomena: Griffiths (1969): homological \(\ne\) algebraic equivalence (lines on the quintic threefold); Clemens (1983): the Griffiths group of a general quintic threefold is not finitely generated even \(\otimes\mathbb{Q}\); Green and Voisin (1988–89): for very general \(X_d \subset \mathbb{P}^4\), \(d\ge 6\), the image of \(AJ\) is torsion — so *Jacobi inversion fails badly* in general and the naive Lefschetz-style induction cannot run. [PROVED — classical]
- **Normal functions and singularities (the live program).** Zucker (1977) proved HC(2) for cubic fourfolds via Poincaré normal functions, the last unconditional success of the classical method. Green–Griffiths (2007) proposed the correct general invariant: the **singularities** of the normal function \(\nu_\zeta\) attached to a primitive Hodge class \(\zeta\) over the dual variety of a sufficiently ample linear system. Brosnan–Fang–Nie–Pearlstein (Invent. math. 2009): **HC is equivalent to the existence of singularities** of these admissible normal functions for sufficiently ample \(L\) [REDUCTION — classical-recent; exact ampleness quantifiers in the cited paper]. Complementary: Brosnan–Pearlstein (Ann. of Math. 2009): zero loci of admissible normal functions are algebraic. So HC is equivalent to a (currently uncheckable) *existence* statement for degenerations of normal functions. Nontorsion Hodge classes are exactly the ones forced to produce nontorsion singularities.
- **Assessment:** this is the only known program formally equivalent to full HC; its bottleneck is that no tool exists to force a singularity to appear (the known local invariants can all vanish for ample enough \(L\) without contradiction). [ASSESSMENT]

### 04-05 — Voisin's work; integral Hodge failures; uniruled and hyper-Kähler cases

- **Kähler failure** (Voisin 2002): see §1.3 — kills any proof strategy that does not use projectivity. Voisin also showed the coherent-sheaf Chern-class formulation is genuinely weaker than the projective one on tori. [PROVED — classical]
- **Positive integral results:** Voisin (2006): IHC for 1-cycles on uniruled threefolds and on Calabi–Yau threefolds; Totaro strengthened the Kodaira-dimension-0 scope [MEMORY for exact scope]; sharpness: Benoist–Ottem's Enriques \(\times\) curve counterexample has \(2K_X = 0\), \(K_X \ne 0\) ★. Voisin (2007): IHC(2) for cubic fourfolds; Perry (2022) ★: categorical proof + Gushel–Mukai fourfolds, via a variational IHC for CY2 categories (deform the Kuznetsov component to \(D^b(K3)\), realize Hodge classes as Mukai vectors of stable objects — moduli-space nonemptiness supplies the cycle). This "realize the class as a Chern character of an object that deforms" mechanism is the same engine as Markman's (04-06). [PROVED — recent, verified]
- **Unramified cohomology as obstruction:** Colliot-Thélène–Voisin (2012): the degree-4 IHC defect is computed by \(H^3_{nr}(X,\mathbb{Q}/\mathbb{Z})\) for many classes of \(X\); Schreieder's refined unramified cohomology extends the calculus [MEMORY for the extension]. These are the *only* structured obstruction theories known — all integral. [PROVED — classical/recent]
- **Hyper-Kähler cases:** Voisin's "Footnotes to papers of O'Grady and Markman" fed the Markman–O'Grady bridge (Weil fourfolds \(\leftrightarrow\) Kummer-type intermediate Jacobians). Floccari ★: HC + Tate for all Kum\(^3\)-type sixfolds; with Foster and Varesco for Kum\(^2\) fourfolds; Floccari–Fu ★: HC + Tate for singular-moduli OG6 resolutions and their powers; Mongardi–Ottem: IHC for 1-cycles on K3\(^{[n]}\)/Kummer type [MEMORY]. K3\(^{[n]}\)-type HC in full is OPEN, but B(X) is known there (Charles–Markman) and rational Hodge isometries are algebraic (Buskin; Markman) — the remaining gap is genuinely about non-isometry classes. [mixed labels as marked]

### 04-06 — Abelian varieties: Weil classes, Lefschetz group — the 2023–2025 breakthrough zone

- **Weil classes.** \(A\) of even dimension \(2n\) is of \(K=\mathbb{Q}(\sqrt{-d})\)-**Weil type** if \(K \hookrightarrow \mathrm{End}_{\mathbb{Q}}(A)\) with \(\sqrt{-d}\) acting on \(T_0A\) with eigenvalues \(\pm\sqrt{-d}\) of equal multiplicity \(n\). Then \(\wedge^{2n}_K H^1(A,K)\) contributes a 2-dimensional space \(HW \subset H^{n,n}(A,\mathbb{Q})\) of **Hodge–Weil classes**, exceptional (not divisor-generated) for the general member (Weil 1977). Families: dimension \(n^2\), indexed by \((n, K, \delta)\) with discriminant \(\delta \in \mathbb{Q}^*/\mathrm{Nm}(K^*)\). ★ [PROVED — classical; normalization of \(\delta\) as in Markman 2025]
- **Lefschetz group calculus.** Divisor-generated classes = invariants of the Lefschetz group; all Hodge classes = invariants of the Mumford–Tate group; exceptional classes exist iff \(MT \subsetneq \mathrm{Lef}\). Tankeev: no exceptional classes for simple \(A\) of prime dimension \(\Rightarrow\) HC. Moonen–Zarhin: complete analysis in dimension \(\le 5\); on fourfolds, Hodge ring = divisors + Weil classes. [PROVED — classical]
- **The breakthrough chain (all ★, verified this mission):**
  1. Markman–O'Grady: Weil fourfolds of discriminant 1 arise as third intermediate Jacobians of Kummer-type hyper-Kähler varieties, in complete families.
  2. Markman 2023 (EMS Press): monodromy + hyperholomorphic-sheaf deformation \(\Rightarrow\) Hodge–Weil classes algebraic for all Weil fourfolds of discriminant 1, every \(K\).
  3. Voisin, Varesco, Floccari: bootstrap to all powers and to Kummer-type hyper-Kähler varieties.
  4. **Markman 2025 (arXiv 2502.03415):** the secant-sheaf construction. On \(X \times \hat{X}\) (\(X\) an abelian \(n\)-fold), a "\(K\)-secant" 2-plane \(P \subset H^{ev}(X,\mathbb{Q})\) of Hodge classes meeting the spinorial variety in two conjugate \(K\)-points induces a Weil structure \((X\times\hat{X}, \eta, h)\). Orlov's derived equivalence sends sheaves with Chern character in \(P\) to an object \(E\) on \(X\times\hat{X}\) whose modified character \(\exp(-c_1(E)/\mathrm{rk} E)\,ch(E)\) *stays Hodge under all Weil-type deformations*. For \(n=3\), for **every** \(d\), Markman produces a simple reflexive secant sheaf \(E\) and proves (Buchweitz–Flenner semiregularity) that it deforms over the whole 9-dimensional moduli of polarized Weil sixfolds of discriminant \(-1\): Hodge–Weil classes there are algebraic. Specialization (sixfolds \(\rightsquigarrow\) fourfolds) then gives **all discriminants in dimension 4**, hence with Moonen–Zarhin: **HC for all abelian fourfolds** (CM cases included; Weil's original candidate counterexamples eliminated).
- **What remains open here [OPEN]:** abelian varieties of dimension \(\ge 5\) in general; Weil sixfolds with discriminant \(\ne -1\) beyond Schoen's \(K=\mathbb{Q}(\sqrt{-3}),\ \delta = 1\) case; all CM abelian varieties in general dimension. This is the launchpad for Target A (Section 4).

### 04-07 — Chow groups and Bloch–Beilinson

- Mumford (1968): \(p_g > 0 \Rightarrow \mathrm{CH}_0\) infinite-dimensional — Chow groups are enormous, and cycle construction cannot proceed by finite-dimensional parameter counts. Roitman (1980): torsion of \(\mathrm{CH}_0\) = torsion of Alb. Bloch's conjecture (converse to Mumford) known for surfaces of Kodaira dimension \(< 2\) (Bloch–Kas–Lieberman) and many special general-type surfaces, open in general. [PROVED — classical]
- **Bloch–Srinivas (1983) decomposition of the diagonal:** if \(\mathrm{CH}_0(X)\) is supported on a low-dimensional subvariety, the diagonal decomposes, forcing cohomology into coniveau \(\ge 1\) and yielding HC(2) when \(\mathrm{CH}_0\) is supported on a threefold. This is the *only* general mechanism deriving HC-type conclusions from Chow-group smallness. Voisin's converse program: for general complete intersections, GHC \(\Leftrightarrow\) generalized Bloch conjecture [MEMORY for exact scope]. [PROVED — classical]
- The conjectural **Bloch–Beilinson filtration** \(F^\bullet \mathrm{CH}^k\) with \(\mathrm{gr}^j\) controlled by \(H^{2k-j}\) would organize all of the above; Murre's conjectures give the motivic form; Jannsen proved the numerical-motive semisimplicity that any such theory needs. Status: not constructed for a single variety with nontrivial \(H^{>1}\)-transcendental part. **Relevance to the mission:** HC is the \(j=0\) shadow of this structure; the absence of *any* candidate filtration is a structural explanation of why cycle construction is hard (Section 6). [ASSESSMENT]

### 04-08 — Absolute Hodge classes (Deligne) vs. Hodge

- Deligne (LNM 900, 1982): every Hodge class on an abelian variety is **absolute Hodge** (its de Rham + \(\ell\)-adic avatars remain Hodge under all automorphisms of \(\mathbb{C}\)). André (1996): they are even **motivated**. Consequences: HC for abelian varieties (and anything motivically dominated by them: K3s via Kuga–Satake, Fermat varieties, known hyper-Kähler types — Soldatenkov, Floccari [REPORTED]) reduces to arithmetic questions over \(\bar{\mathbb{Q}}\). [PROVED — classical]
- Voisin (Compositio 2007): for absolute classes, Hodge loci are defined over \(\bar{\mathbb{Q}}\) with Galois-conjugate components again Hodge loci; HC for absolute Hodge classes reduces to varieties over \(\bar{\mathbb{Q}}\). Combined with CDK and now BKU (★), the arithmetic of Hodge loci is the sharpest structural evidence: **if HC fails, it fails on an atypical, \(\bar{\mathbb{Q}}\)-arithmetic, finite-in-number locus** for level \(\ge 3\) variations. [PROVED — recent, verified for BKU; the synthesis is ASSESSMENT]
- **The gap:** "absolute Hodge \(\Rightarrow\) algebraic" is itself open; the Weil classes were absolute Hodge (Deligne) for 40 years before becoming algebraic (Markman) in dimension 4 — a proof-of-concept that the gap is bridgeable but only by hard geometry (sheaf deformation), not by formal arguments. Whether *all* Hodge classes are absolute is open beyond the abelian-motivated world; a counterexample would refute HC. [OPEN]

### 04-09 — Computational and explicit targets

- **Fermat calculus (the most explicit laboratory).** \(H^{n}_{prim}(X^n_m)\) decomposes into 1-dimensional character eigenspaces \(V(\alpha)\), \(\alpha=(a_0,\dots,a_{n+1})\), \(a_i \in (\mathbb{Z}/m)^\times\), \(\sum a_i \equiv 0\); Hodge classes are enumerated combinatorially; Shioda's inductive structure (Shioda–Katsura 1979) generates algebraic classes from lower dimension; condition \((P_m)\) = "induction reaches everything". Verified: \(m\le 20\) (Shioda 1979); \(m=p^2\) via Aoki's standard cycles (1987); ★ fourfolds \(X^4_m\), \(m\le 100\), \(\gcd(m,6)=1\) (da Silva 2021, SAGE-assisted). **First explicit stuck case: \(m=33\), \(n=4\)** — see Target B. All Fermat Hodge classes are absolute Hodge (CM motives, Deligne), so these are exactly "checkable Hodge classes with no known cycle". [PROVED — classical/recent, verified]
- **Weil-class tables:** van Geemen's explicit theta-based descriptions of Weil classes; Schoen's explicit cycle constructions for \(\mathbb{Q}(\sqrt{-3})\) (elliptic-curve automorphism tricks) — the only *hands-on* cycle constructions ever found for exceptional abelian classes; everything since goes through moduli of sheaves. [PROVED — classical]
- **K3 world:** Buskin ★ (Hodge isometries algebraic); Kuga–Satake algebraicity for new Picard-16 families via Floccari's \(S_K\) construction ★; Paranjape's six-line double covers (classical). Suspicious-but-open explicit classes: Kuga–Satake classes for a *general* polarized K3 (level 2, but the correspondence lives on \(S \times \mathrm{KS}(S)^2\) — open in general). [PROVED — recent, verified / OPEN as marked]
- **Noether–Lefschetz side:** CDK + BKU make the *loci* where extra classes appear algebraic and (in level \(\ge 3\), positive period dimension) finite; for the universal degree-\(d\) hypersurface family in \(\mathbb{P}^5\) this is exactly where any explicit fourfold counterexample would have to live. No computational sweep of such loci exists; a targeted one is proposed as Target C. [ASSESSMENT]

### 04-10 — Homological vs. numerical equivalence; the standard conjectures as the real wall

- Conjecture D (hom = num) is known for: divisors (Matsusaka 1957), abelian varieties over \(\mathbb{C}\) (via Lieberman's B + Hdg), ★ abelian fourfolds in char \(p\) for infinitely many \(\ell\) (Ancona 2021 + Clozel 1999). Open in general even for abelian varieties over \(\mathbb{C}\) in high dimension? — no: over \(\mathbb{C}\), B(abelian) holds in all dimensions, so D holds for all complex abelian varieties [PROVED — classical]; the open frontier is char \(p\) and general \(X\).
- **HC \(\Rightarrow\) D over \(\mathbb{C}\)** (classical argument, included for self-containedness): if \(\alpha\) is algebraic and homologically nontrivial, Poincaré duality and the semisimplicity of polarized Hodge structures give a *Hodge* class \(\beta\) with \(\langle\alpha,\beta\rangle \ne 0\); HC makes \(\beta\) algebraic, so \(\alpha\) is numerically nontrivial. [PROVED — classical implication]
- **Why this is "the real wall":** every known route to HC-type statements needs correspondences (projectors, \(\Lambda\), transfers) to move classes between varieties; B/C/D are precisely the statements that the *necessary* correspondences exist. The unconditional substitutes — André's motivated cycles, absolute Hodge cycles — solve the bookkeeping but cannot output subvarieties. Jannsen's theorem shows the numerical world is as good as semisimple; the wall is *lifting* numerical/homological data to actual cycles, which is also exactly what HC asks. In slogan form: **HC = (standard conjectures) + (Jacobi-type inversion in each fiber), and neither summand has a general mechanism.** [ASSESSMENT]
- Char-\(p\) note: Ancona's p-adic proof of Hdg for abelian fourfolds is methodologically important for this legion: it is the first standard-conjecture case proved by *p-adic* positivity, suggesting arithmetic routes to positivity statements that complex Hodge theory cannot see. [PROVED — recent, verified; the suggestion is HEURISTIC]

---

## 4. Candidate breakthrough

No proof is claimed. Three targets are specified, in decreasing order of strategic value and increasing order of concreteness. Targets A and B are precise reductions to checkable classes on specific varieties with cycle-construction plans, per the mission definition of breakthrough.

### 4.1 Target A [PROGRAM] — Weil abelian sixfolds of arbitrary discriminant via Markman's secant-sheaf engine

**Status of the frontier (verified):** Hodge–Weil classes are algebraic for Weil sixfolds \((A, K, h)\) with \(\delta = -1\) (Markman 2025, all \(K\)) and for \(K = \mathbb{Q}(\sqrt{-3}), \delta = 1\) (Schoen). All other \((K,\delta)\) components of the 9-dimensional moduli spaces are **open**, and they are the lowest-dimensional structured open cases of HC on abelian varieties.

**Precise target.** Fix \(K = \mathbb{Q}(\sqrt{-1})\) and a nontrivial discriminant class, e.g. \(\delta = 3 \in \mathbb{Q}^*/\mathrm{Nm}(\mathbb{Q}(i)^*)\) (3 is not a norm from \(\mathbb{Q}(i)\): a sum of two rational squares has 3-adic valuation even). Let \(\mathcal{M}_{K,\delta}\) be the corresponding 9-dimensional moduli of polarized Weil sixfolds. **Checkable Hodge class:** the 2-dimensional space \(HW \subset H^{3,3}(A,\mathbb{Q})\) on any \(A \in \mathcal{M}_{K,\delta}\).

**Cycle-construction plan (Markman's own machinery, one computation short):**

1. In Markman 2025, the Weil structure on \(X \times \hat{X}\) (\(X\) an abelian threefold) is induced by a \(K\)-secant 2-plane \(P \subset H^{ev}(X,\mathbb{Q})\) through the spinorial variety. The polarization \(h\) and hence the hermitian form and its discriminant \(\det H \in \mathbb{Q}^*/\mathrm{Nm}(K^*)\) are *determined by lattice data of \(P\)* (the restriction of the spin-invariant pairing to \(P\) and its position relative to \(H^{ev}(X,\mathbb{Z})\)).
2. **The checkable step:** compute the image of the map \(\{K\text{-secants } P \text{ realizable by sheaf Chern characters}\} \to \mathbb{Q}^*/\mathrm{Nm}(K^*),\ P \mapsto \det H\). Markman's construction realizes \(\delta = -1\). The computation of the full image is finite-dimensional linear algebra over \(\mathbb{Q}\) on \(H^{ev}(X,\mathbb{Q}) = \wedge^* V\), \(V = H^1(X)\oplus H^1(\hat{X})\), with the constraint that \(P\) contain Chern characters \(ch(F_1), ch(F_2)\) of sheaves with \(\mathrm{rk}\,\Phi(F_1^\vee \boxtimes F_2) \ne 0\).
3. If some realizable secant has \(\det H = \delta \ne -1\): rerun the Buchweitz–Flenner semiregularity argument for the associated reflexive sheaf \(E\) on \(X\times\hat{X}\). Markman's Hodge-type-invariance theorem (the class \(\exp(-c_1/r)\,ch(E)\) stays Hodge along *all* Weil deformations) is already proved for arbitrary secants, so only the *deformability of \(E\)* along the \(\delta\)-component needs the semiregularity verification.
4. If the image is exactly \(\{-1\}\) (an obstruction of parity/spinor-norm type is conceivable), that itself is a *new structural fact*: it would show the secant-sheaf engine has a lattice-theoretic ceiling, and would sharply motivate the alternative: prove the \(n=4\) (abelian eightfold, \(\delta=-1\)) case of Markman's semiregularity step, and then imitate the **specialization argument** (Markman/Voisin-survey mechanism: discriminant-\(-1\) statements in dimension \(2n+2\) specialize to all-discriminant statements in dimension \(2n\)) to capture all Weil sixfolds.

**Payoff.** All-\(\delta\) Weil sixfolds + Moonen–Zarhin-style classification in dimension 6 would be the decisive step toward HC for all abelian sixfolds, and (by the product/power bootstraps of Floccari–Varesco type) a large new tranche of hyper-Kähler and Kuga–Satake cases. **Risk:** step 2 may yield only \(\delta = -1\) (see 4 for the fallback); step 3's semiregularity is genuinely hard analysis of reflexive sheaves on singular loci. [PROGRAM — not executed; all inputs verified]

### 4.2 Target B [PROGRAM] — the explicit stuck Hodge classes on the Fermat fourfold \(X^4_{33}\)

**The variety:** \(X^4_{33} = \{x_0^{33} + x_1^{33} + \dots + x_5^{33} = 0\} \subset \mathbb{P}^5\), dimension 4, degree 33.

**The checkable class (verified from da Silva 2021):** condition \((P_{33})\) fails: there is an explicit character datum (published as the vector \((0,0,0,0,0,0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,3)\) in the monoid \(\mathfrak{M}_{33}\)) whose eigenspaces \(V(\alpha) \subset H^{2,2}(X^4_{33},\mathbb{Q})\) consist of Hodge classes that are (i) **not quasi-decomposable** — not reachable by the Shioda–Katsura inductive structure from Fermat curves/surfaces — and (ii) **not of Aoki's standard type**. These are, to this mission's knowledge, the most explicit Hodge classes in the literature for which no algebraicity proof and no cycle candidate exists. They are absolute Hodge (Deligne, CM motive), so they cannot be attacked by arithmetic obstructions — a cycle must be found (or HC is false here, and this is where to look).

**Cycle-construction plan:**

1. **Identify the motive.** Each \(V(\alpha)\) is a CM Hodge structure with CM by \(\mathbb{Q}(\zeta_{33})\). Compute its Mumford–Tate group and determine whether \(V(\alpha)\oplus V(\bar\alpha)\) is a **Weil-class system** for one of the imaginary quadratic subfields... — \(\mathbb{Q}(\zeta_{33})\) contains \(\mathbb{Q}(\sqrt{-11})\) and \(\mathbb{Q}(\sqrt{-3})\) — realized on an abelian variety isogeny factor of the Fermat-Jacobian package (the motive of \(X^4_{33}\) lies in the Tannakian category generated by Jacobians of quotients of the Fermat curve \(C_{33}\); Shioda–Katsura + Deligne). This is a finite character-theoretic computation (CM types, reflex fields) — checkable in SAGE/PARI.
2. **If Weil-type for \(\mathbb{Q}(\sqrt{-3})\):** Schoen's theorem (arbitrary discriminant for \(\mathbb{Q}(\sqrt{-3})\)) or its 2025 descendants may *already imply algebraicity* — the missing work is transporting the class through the explicit isogeny correspondences between the Fermat motive and the abelian variety, all of which are algebraic (graphs of quotient maps and inductive-structure correspondences). A positive outcome here would be a **new proved special case: HC for \(X^4_{33}\)** — the first Fermat fourfold beyond the \((P_m)\)/Aoki calculus — by *assembly* of proved components. This is the single most plausible near-term "new proved special case" this legion identified. [PROGRAM; the assembly plausibility is HEURISTIC until step 1 is computed]
3. **If not Weil-type:** the class defines a *new species* of CM Hodge class (beyond divisor products, inductive classes, standard cycles, and Weil classes) on an explicit fourfold — the sharpest possible testbed for either Markman-style sheaf methods (moduli of stable sheaves/complexes on \(X^4_{33}\) with prescribed character — note \(X^4_{33}\) has ample canonical bundle, so Bridgeland/Gieseker moduli are available) or for genuine doubt about HC. Either branch is scientifically valuable.

**Why this target is honest:** every input is published; the open status of the class is explicitly documented (da Silva 2021, Cambridge *Experimental Results*); the plan's first two steps are finite computations, not hopes. [PROGRAM]

### 4.3 The obstruction-class question — honest negative finding

The mission allowed "a new obstruction class" as a breakthrough. Finding: **all known obstruction formalisms (Atiyah–Hirzebruch/Steenrod, Totaro's \(MU\)-factorization, Kollár degeneration/divisibility, Colliot-Thélène–Voisin unramified cohomology, Benoist–Ottem torsion) obstruct only the integral statement and die after \(\otimes\mathbb{Q}\)** — verified by inspecting each mechanism (torsion-based or divisibility-based). A rational obstruction class would have to be: (i) a Hodge-theoretic or arithmetic invariant of a rational Hodge class, (ii) vanishing on all algebraic classes, (iii) computable and nonzero somewhere. Constraints discovered this mission: by CDK + BKU + Voisin's \(\bar{\mathbb{Q}}\)-descent, such an invariant cannot be locally analytic in moduli (Hodge loci are algebraic and arithmetic), and by Deligne–André it must vanish on all motivated classes — which include every explicitly known Hodge class (all abelian-motivated). **So any rational obstruction must be blind to the entire abelian-motive world — there is currently no known nonvacuous domain on which to define it.** This is a real (if negative) structural insight: the search for counterexamples and the search for obstructions are both starved by the same fact — we cannot exhibit any Hodge class provably outside the motivated world. [ASSESSMENT — argued above from verified components; not a theorem]

### 4.4 Honorable mention — Target C [PROGRAM, harder]

Run the Brosnan–Fang–Nie–Pearlstein criterion *backwards* on Target B: for \(\zeta\) one of the stuck classes on \(X^4_{33}\), the associated normal function over the discriminant of \(|\mathcal{O}(\ell)|\), \(\ell \gg 0\), must develop a singularity somewhere if HC is true. Fermat symmetry (\(\mu_{33}^6 \rtimes S_6\)) cuts the search space: singularities can be sought on the finitely many symmetry-stable strata of the dual variety first. No one has attempted a symmetry-reduced singularity search on any concrete fourfold; \(X^4_{33}\) is the canonical candidate. [PROGRAM — computationally heavy; equivalence to algebraicity of a multiple of \(\zeta\) is the verified BFNP reduction]

---

## 5. Strongest claim we can honestly defend

**Claim (assessment, defensible from verified sources):**

1. **The proved perimeter of the Hodge conjecture moved further in 2022–2025 than in the preceding forty years**, and it moved by exactly one method: realizing Hodge classes as characteristic classes of sheaves/objects that deform over complete moduli of the polarized structures (Buskin; Markman 2023, 2025; Perry's categorical IHC; Floccari; Floccari–Fu). In particular **the Hodge conjecture now holds for all abelian fourfolds** (Markman 2025 + Moonen–Zarhin — modulo final peer review of arXiv 2502.03415, which Voisin's 2025 survey and the 2026 Floccari–Fu J. Math. Pures Appl. paper treat as established) and for all hyper-Kähler sixfolds of generalized Kummer type (Floccari) — the first complete families of dimension \(> 2\) with \(h^{2,0} \ne 0\). [Every component verified this mission.]
2. **Precise reduction (Target A):** the algebraicity of the Hodge–Weil classes for *every* polarized Weil abelian sixfold reduces, via Markman's proved Hodge-type-invariance theorem for secant-sheaf characteristic classes plus Buchweitz–Flenner semiregularity, to a finite, explicitly specified lattice-theoretic computation (which discriminants \(\det H\) are realized by sheaf-realizable \(K\)-secant planes) followed by a semiregularity verification on the new components. No step requires new conjectures. [REDUCTION assembled from verified components; the two remaining steps are open work, not formalities.]
3. **Sharpest checkable class (Target B):** the explicitly published character classes on the degree-33 Fermat fourfold \(X^4_{33}\) are the most concrete Hodge classes in the literature with no known cycle, and there is a finite computation (CM-type/Weil-type identification inside \(\mathbb{Q}(\zeta_{33})\)-motives) that would either route them through the Schoen–Markman theorems — yielding a genuinely **new proved special case** — or certify them as the first known Hodge classes outside every existing algebraicity mechanism.

**Explicitly NOT claimed:** no new theorem, no proof of any open case, no obstruction class, no counterexample. Items 2–3 are precise reductions with executable first steps, which is the mission's third category of breakthrough.

---

## 6. Why not full Hodge — the structural barriers

1. **No cycle-construction technology.** Divisors come from the exponential sequence; 1-cycles from hard Lefschetz; everything else ever proved comes from special geometry (abelian/HK moduli of sheaves, CM/Fermat combinatorics, small Chow groups). There is no general mechanism that inputs a Hodge class and outputs a subvariety, and the Kähler counterexample (Voisin 2002) proves no purely local/analytic mechanism can exist: any proof must use projectivity and (by the \(\bar{\mathbb{Q}}\)-descent picture) likely arithmetic.
2. **The integral pathologies calibrate the difficulty.** Torsion, divisibility and Kodaira-0 counterexamples show the conjecture survives only with denominators; hence no topological/cohomological formalism (which cannot distinguish \(\alpha\) from \(m\alpha\) only by allowing denominators *of unknown size*) can settle it. Known proofs of special cases produce denominators from geometry (moduli, isogenies); nothing bounds them in general.
3. **Chow groups are infinite-dimensional (Mumford)** and no Bloch–Beilinson filtration has ever been constructed. HC is the top graded piece of a structure whose existence is itself conjectural; attacks that avoid Chow-group structure (normal functions, sheaf deformation) succeed exactly where the motive is small (abelian, level \(\le 2\)... — the entire verified perimeter of Section 2).
4. **The standard conjectures wall (04-10).** We cannot produce the correspondences (\(\Lambda\), Künneth projectors) whose existence is *implied* by HC and *needed* by every inductive strategy; the unconditional surrogates (motivated/absolute classes) cannot output cycles. Even hom = num is open in general.
5. **Evidence asymmetry at high level.** By Noether–Lefschetz-type genericity and now BKU: for level \(\ge 3\) variations (e.g. hypersurfaces of high degree), extra Hodge classes exist only on an atypical, at-most-finite (in positive period dimension), arithmetically defined locus — where nobody has ever computed a single example. All positive evidence lives in level \(\le 2\)/abelian territory. HC in its hard range is a statement about varieties we cannot currently exhibit, let alone test — with the Fermat family (Target B) as the lone explicit exception, which is precisely why this report elevates it.
6. **The absolute-Hodge gap.** Even the "formal half" of the problem — every Hodge class is absolute — is open in general; and closing it would still leave the 40-year Weil-class gap (absolute \(\to\) algebraic) that only sheaf-theoretic geometry has ever bridged, one moduli space at a time.

Conclusion: full HC is out of reach of current mathematics not because of missing cleverness on one step but because *three independent infrastructures are missing* (cycle construction, Chow filtration, standard conjectures). The rational frontier — Weil sixfolds, \(X^4_{33}\), K3\(^{[n]}\)-type — is where the one working engine (deforming sheaves over complete moduli) still has unburned fuel.

---

## 7. References

Honesty coding: **[V]** = statement verified against the source (or its arXiv/journal page) during this mission; **[M]** = standard reference cited from training knowledge — bibliographic details should be double-checked before external use. No invented citations: every item below corresponds to a real, identifiable work.

**Foundational / classical**

1. [M] W. V. D. Hodge, *The topological invariants of algebraic varieties*, Proc. ICM 1950.
2. [M] S. Lefschetz, *L'Analysis situs et la géométrie algébrique*, Gauthier-Villars, 1924.
3. [M] M. F. Atiyah, F. Hirzebruch, *Analytic cycles on complex manifolds*, Topology 1 (1962).
4. [V] A. Grothendieck, *Hodge's general conjecture is false for trivial reasons*, Topology 8 (1969) 299–303.
5. [M] A. Grothendieck, *Standard conjectures on algebraic cycles*, Bombay Colloquium, 1968.
6. [M] S. Kleiman, *The standard conjectures*, in Motives (Seattle), Proc. Sympos. Pure Math. 55, AMS, 1994.
7. [M] D. Lieberman, *Numerical and homological equivalence of algebraic cycles on Hodge manifolds*, Amer. J. Math. 90 (1968).
8. [M] N. Katz, W. Messing, *Some consequences of the Riemann hypothesis for varieties over finite fields*, Invent. Math. 23 (1974).
9. [M] T. Matsusaka, *The criteria for algebraic equivalence and the torsion group*, Amer. J. Math. 79 (1957).
10. [M] P. Deligne (notes by J. Milne), *Hodge cycles on abelian varieties*, in LNM 900, Springer, 1982.
11. [M] Y. André, *Pour une théorie inconditionnelle des motifs*, Publ. Math. IHÉS 83 (1996).
12. [M] U. Jannsen, *Motives, numerical equivalence, and semi-simplicity*, Invent. Math. 107 (1992).
13. [M] E. Cattani, P. Deligne, A. Kaplan, *On the locus of Hodge classes*, J. Amer. Math. Soc. 8 (1995) 483–506.

**Intermediate Jacobians, normal functions, Chow groups**

14. [M] P. Griffiths, *On the periods of certain rational integrals I, II*, Ann. of Math. 90 (1969).
15. [M] H. Clemens, *Homological equivalence, modulo algebraic equivalence, is not finitely generated*, Publ. Math. IHÉS 58 (1983).
16. [M] S. Zucker, *The Hodge conjecture for cubic fourfolds*, Compositio Math. 34 (1977).
17. [M] M. Green, *Griffiths' infinitesimal invariant and the Abel–Jacobi map*, J. Differential Geom. 29 (1989); C. Voisin, CRAS note on the infinitesimal invariant of normal functions (1988).
18. [M] M. Nori, *Algebraic cycles and Hodge-theoretic connectivity*, Invent. Math. 111 (1993).
19. [M] M. Green, P. Griffiths, *Algebraic cycles and singularities of normal functions*, in Algebraic Cycles and Motives, LMS Lecture Notes 343, 2007.
20. [M] P. Brosnan, H. Fang, Z. Nie, G. Pearlstein, *Singularities of admissible normal functions*, Invent. Math. 177 (2009).
21. [M] P. Brosnan, G. Pearlstein, *The zero locus of an admissible normal function*, Ann. of Math. 170 (2009).
22. [M] D. Mumford, *Rational equivalence of 0-cycles on surfaces*, J. Math. Kyoto Univ. 9 (1968).
23. [M] A. A. Roitman, *The torsion of the group of 0-cycles modulo rational equivalence*, Ann. of Math. 111 (1980).
24. [M] S. Bloch, A. Kas, D. Lieberman, *Zero cycles on surfaces with \(p_g = 0\)*, Compositio Math. 33 (1976).
25. [M] S. Bloch, V. Srinivas, *Remarks on correspondences and algebraic cycles*, Amer. J. Math. 105 (1983).
26. [M] A. Conte, J. P. Murre, *The Hodge conjecture for fourfolds admitting a covering by rational curves*, Math. Ann. 238 (1978).

**Integral Hodge conjecture**

27. [M] B. Totaro, *Torsion algebraic cycles and complex cobordism*, J. Amer. Math. Soc. 10 (1997).
28. [M] J. Kollár, Trento examples, in *Classification of irregular varieties*, LNM 1515, Springer, 1992.
29. [M] C. Soulé, C. Voisin, *Torsion cohomology classes and algebraic cycles on complex projective manifolds*, Adv. Math. 198 (2005).
30. [M] C. Voisin, *On integral Hodge classes on uniruled or Calabi–Yau threefolds*, in Moduli Spaces and Arithmetic Geometry, Adv. Stud. Pure Math. 45 (2006).
31. [M] J.-L. Colliot-Thélène, C. Voisin, *Cohomologie non ramifiée et conjecture de Hodge entière*, Duke Math. J. 161 (2012).
32. [V] O. Benoist, J. C. Ottem, *Failure of the integral Hodge conjecture for threefolds of Kodaira dimension zero*, Comment. Math. Helv. 95 (2020) 27–35.
33. [V] A. Perry, *The integral Hodge conjecture for two-dimensional Calabi–Yau categories*, Compositio Math. (2022); arXiv:2004.03163.
34. [M] G. Mongardi, J. C. Ottem, *Curve classes on irreducible holomorphic symplectic varieties* (c. 2020).

**Kähler counterexample, Hodge loci, absolute Hodge**

35. [V] C. Voisin, *A counterexample to the Hodge conjecture extended to Kähler varieties*, Int. Math. Res. Not. 2002, no. 20, 1057–1075.
36. [M] C. Voisin, *Hodge loci and absolute Hodge classes*, Compositio Math. 143 (2007).
37. [V] G. Baldi, B. Klingler, E. Ullmo, *On the distribution of the Hodge locus*, Invent. Math. (2024); arXiv:2107.08838.
38. [M] F. Charles, C. Schnell, *Notes on absolute Hodge classes*, in Hodge Theory (Princeton, 2014).

**Abelian varieties and Weil classes**

39. [M] A. Weil, *Abelian varieties and the Hodge ring*, Collected Papers III, 1977.
40. [M] S. Tankeev, *Cycles on simple abelian varieties of prime dimension*, Izv. Akad. Nauk SSSR (1982).
41. [M] B. Moonen, Y. Zarhin, *Hodge classes and Tate classes on simple abelian fourfolds*, Duke Math. J. 77 (1995); *Hodge classes on abelian varieties of low dimension*, Math. Ann. 315 (1999).
42. [M] C. Schoen, *Hodge classes on self-products of a variety with an automorphism*, Compositio Math. 65 (1988); Addendum, Compositio Math. 114 (1998).
43. [M] B. van Geemen, *An introduction to the Hodge conjecture for abelian varieties*, in LNM 1594, Springer, 1994; and (with Schoen-related constructions) *Weil classes and decomposable abelian fourfolds* — [V] the latter as: B. van Geemen et al., SIGMA 18 (2022) 097.
44. [V] E. Markman, *The monodromy of generalized Kummer varieties and algebraic cycles on their intermediate Jacobians*, EMS Press (J. Eur. Math. Soc., c. 2023) — Hodge–Weil classes algebraic for discriminant-1 Weil fourfolds.
45. [V] E. Markman, *Cycles on abelian 2n-folds of Weil type from secant sheaves on abelian n-folds*, arXiv:2502.03415 (2025) — discriminant \(-1\) Weil sixfolds for all \(K\); implies HC for all abelian fourfolds.
46. [V] C. Voisin, *Hodge and generalized Hodge conjectures, coniveau and algebraic cycles* (survey, 2025; DOI 10.56994/jomp.001.001.002) — source for the specialization argument and the frontier statement on sixfolds.
47. [M] K. O'Grady, *Compact tori associated to hyperkähler manifolds of Kummer type*, IMRN (c. 2021).
48. [M] G. Ancona, *Standard conjectures for abelian fourfolds*, Invent. Math. 223 (2021) 149–212 — [V] statement verified.
49. [M] L. Clozel, *Équivalence numérique et équivalence cohomologique pour les variétés abéliennes sur les corps finis*, Ann. of Math. 150 (1999).

**K3 surfaces and hyper-Kähler varieties**

50. [V] N. Buskin, *Every rational Hodge isometry between two K3 surfaces is algebraic*, J. reine angew. Math. (Crelle) 755 (2019); arXiv:1510.02852.
51. [V] D. Huybrechts, *Motives of isogenous K3 surfaces*, Comment. Math. Helv. (2019).
52. [M] F. Charles, E. Markman, *The standard conjectures for holomorphic symplectic varieties deformation equivalent to Hilbert schemes of K3 surfaces*, Compositio Math. 149 (2013).
53. [V] S. Floccari, *Sixfolds of generalized Kummer type and K3 surfaces*, Compositio Math. (2023/24); DOI 10.1112/S0010437X23007625.
54. [V] S. Floccari, *The Hodge and Tate conjectures for hyper-Kähler sixfolds of generalized Kummer type*, arXiv:2308.02267 (2023).
55. [V] S. Floccari, L. Fu, *The Hodge conjecture for Weil fourfolds with discriminant 1 via singular OG6-varieties*, J. Math. Pures Appl. (2026); arXiv:2504.13607.
56. [M] M. Varesco, work on the Hodge conjecture for powers of K3 surfaces of Picard number 16 (double covers of \(\mathbb{P}^2\) branched along six lines), c. 2022–23 — cited as [65]/[67] in Floccari–Fu.
57. [M] C. Voisin, *Footnotes to papers of O'Grady and Markman*, c. 2022 (Math. Z. or similar).

**Fermat varieties**

58. [V] T. Shioda, T. Katsura, *On Fermat varieties*, Tôhoku Math. J. 31 (1979) 97–115.
59. [V] T. Shioda, *The Hodge conjecture and the Tate conjecture for Fermat varieties*, Proc. Japan Acad. 55 (1979); and *The Hodge conjecture for Fermat varieties*, Math. Ann. (1979) [M for the Math. Ann. details].
60. [M] N. Aoki, standard cycles on Fermat varieties and the case \(m = p^2\), 1987 (as cited in [61]).
61. [V] G. da Silva Jr., *Notes on the Hodge conjecture for Fermat varieties*, Experimental Results (Cambridge) 2 (2021); arXiv:2101.04739 — source for \(X^4_m\), \(m\le 100\), \(\gcd(m,6)=1\), and the failure of \((P_{33})\) with the explicit non-standard class on \(X^4_{33}\).

---

*End of LEGION 04 report. No fake proofs were harmed—or produced—in the making of this document.*
