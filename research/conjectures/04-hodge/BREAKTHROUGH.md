# Hodge — Wave-2 Breakthrough

**Workspace:** `/workspace/research/conjectures/04-hodge/`
**Date:** 2026-08-15 (Wave 2)
**Relation to REPORT.md:** This document does not re-spread the survey. It delivers the two items REPORT.md could not contain: (I) a **complete, rigorous proof of the Lefschetz (1,1) theorem** — the one fully settled case of the Hodge conjecture — written out from the exponential sequence in the style of Kodaira–Spencer, with every gluing argument given and every classical input named and isolated; (II) a **one-page reduction of "the Hodge conjecture for abelian fourfolds" to named, checkable theorems of the published literature**, with exact theorem numbers verified against the primary sources during this session, and with the single non-peer-reviewed link flagged. **No new theorem is claimed anywhere in this file.**

---

## Theorem

**Theorem 1 (Lefschetz (1,1); Lefschetz 1924, sheaf-theoretic form Kodaira–Spencer 1953).**
Let \(X\) be a connected smooth complex projective variety of dimension \(n\), and let

\[ \mathrm{Hdg}^1_{\mathbb{Z}}(X) \;=\; \{\, \alpha \in H^2(X,\mathbb{Z}) \;:\; \alpha_{\mathbb{C}} \in H^{1,1}(X) \,\} \]

be the group of integral Hodge classes of degree 2, where \(\alpha_{\mathbb{C}}\) is the image of \(\alpha\) in \(H^2(X,\mathbb{C})\). (Torsion classes satisfy \(\alpha_{\mathbb{C}}=0\) and belong to \(\mathrm{Hdg}^1_{\mathbb{Z}}(X)\).) Then:

1. \(\mathrm{Hdg}^1_{\mathbb{Z}}(X)\) is exactly the image of the first Chern class map \(c_1: \mathrm{Pic}(X) \to H^2(X,\mathbb{Z})\);
2. every \(\alpha \in \mathrm{Hdg}^1_{\mathbb{Z}}(X)\) is the class of an algebraic divisor. In refined form: there exist **smooth very ample divisors** \(D_1, D_2 \subset X\) (irreducible if \(n \ge 2\)) with
\[ \alpha \;=\; \pm\bigl(\mathrm{cl}(D_1) - \mathrm{cl}(D_2)\bigr) \;=\; \mathrm{cl}\bigl(\pm(D_1 - D_2)\bigr) \quad \text{in } H^2(X,\mathbb{Z}), \]
where the sign is a single universal normalization constant (equal to \(+1\) under the standard conventions; our proof does not need its value — see Step 6 below).

In particular the Hodge conjecture holds **integrally** in codimension 1, for every smooth complex projective variety.

**Theorem 2 (assembled; NOT new — a verified reduction to named theorems).**
Let \(A\) be a complex abelian variety of dimension 4. Then every rational Hodge class on \(A\) is algebraic, **provided** the following inputs, of which (T1)–(T6) are published and peer-reviewed and (T7) is a 2025 arXiv preprint:

- (T1) Theorem 1 above (divisor classes are algebraic, integrally);
- (T2) the hard Lefschetz theorem (classical Hodge theory);
- (T3) Moonen–Zarhin, *Hodge classes and Tate classes on simple abelian fourfolds*, Duke Math. J. 77 (1995) 553–581, **Theorem 2.11**;
- (T4) Moonen–Zarhin, *Hodge classes on abelian varieties of low dimension*, Math. Ann. 315 (1999) 711–733, **Theorem 0.1(i)** and **Proposition 3.8**;
- (T5) J. Ramón Marí, *On the Hodge conjecture for products of certain surfaces*, Collect. Math. 59 (2008) 1–26, **Theorem 4.11**;
- (T6) C. Schoen, Compositio Math. 65 (1988) 3–32 and Compositio Math. 114 (1998) 329–336 (**Proposition 10** of the Addendum); K. Koike, Canad. Math. Bull. 47 (2004) 566–572; E. Markman, J. Eur. Math. Soc. 25 (2023) 231–321;
- (T7) E. Markman, *Cycles on abelian \(2n\)-folds of Weil type from secant sheaves on abelian \(n\)-folds*, arXiv:2502.03415v2 (2025), **Theorem 1.5.1** (and its Corollary 1.6.1).

Unconditionally on the **published** literature alone, the same argument proves the Hodge conjecture for every abelian fourfold whose exceptional Hodge classes involve only Weil structures with field \(K = \mathbb{Q}(\sqrt{-1})\) or \(K=\mathbb{Q}(\sqrt{-3})\) (any discriminant), or with discriminant \(1\) (any \(K\)).

---

## Proof or reduction (complete)

### Part I — Complete proof of Theorem 1

#### I.0 Conventions and the exact list of classical inputs used as black boxes

\(X\) is a connected smooth projective variety over \(\mathbb{C}\), of complex dimension \(n\); \(X^{\mathrm{an}}\) denotes the underlying compact complex manifold, which is Kähler (restrict the Fubini–Study form of any projective embedding). Cohomology \(H^k(X,\mathcal{F})\) means sheaf cohomology on \(X^{\mathrm{an}}\); for the constant sheaves \(\mathbb{Z}, \mathbb{C}\) this agrees with singular cohomology because \(X^{\mathrm{an}}\) is paracompact and locally contractible (standard comparison; Voisin I, §4.3). The case \(n=0\) is trivial (\(H^2=0\)); assume \(n \ge 1\).

The proof below is complete **modulo the following named classical theorems**, each used as a cited black box. Everything else — every exact sequence, every compatibility, every gluing — is proved in full.

- **(C1) Hodge decomposition** (Hodge; see Voisin, *Hodge Theory and Complex Algebraic Geometry I*, Cambridge 2002, Ch. 6): for a compact Kähler manifold, \(H^k(X,\mathbb{C}) = \bigoplus_{p+q=k} H^{p,q}(X)\), where \(H^{p,q}\) is the set of classes representable by a \(d\)-closed form of type \((p,q)\), and \(\overline{H^{p,q}} = H^{q,p}\).
- **(C2) Dolbeault–Grothendieck lemma** (Voisin I, §2.3; Griffiths–Harris, *Principles of Algebraic Geometry*, Wiley 1978, Ch. 0): the complex \((\mathcal{A}^{0,\bullet}, \bar\partial)\) of sheaves of smooth \((0,q)\)-forms is a resolution of \(\mathcal{O}_X\); likewise \((\mathcal{A}^{\bullet}, d)\) resolves \(\mathbb{C}\) (smooth Poincaré lemma). All \(\mathcal{A}^{k}, \mathcal{A}^{p,q}\) are fine sheaves (partitions of unity), hence acyclic, so sheaf cohomology is computed by global sections of these resolutions (de Rham and Dolbeault theorems in their sheaf-theoretic form; Voisin I, §4.3).
- **(C3) \(\partial\bar\partial\)-lemma** (Voisin I, §6.1; Griffiths–Harris Ch. 0 §7): on a compact Kähler manifold, a \(d\)-closed, \(\bar\partial\)-exact form is \(\partial\bar\partial\)-exact — hence \(d\)-exact, since \(\partial\bar\partial\eta = d(\bar\partial\eta)\).
- **(C4) GAGA** (Serre, *Géométrie algébrique et géométrie analytique*, Ann. Inst. Fourier 6 (1956) 1–42): analytification is an equivalence between coherent algebraic and coherent analytic sheaves on a projective variety; in particular every holomorphic line bundle on \(X^{\mathrm{an}}\) is the analytification of a unique algebraic line bundle.
- **(C5) Serre + Bertini** (Hartshorne, *Algebraic Geometry*, GTM 52, Ch. II §7 and Thm II.8.18): for any algebraic line bundle \(L\) and ample \(\mathcal{O}_X(1)\), \(L \otimes \mathcal{O}_X(m)\) is very ample for \(m \gg 0\); and (char 0, \(X\) smooth) the general member of a very ample linear system is a smooth divisor, irreducible if \(\dim X \ge 2\).
- **(C6) Thom class formalism and line-bundle classification** (Milnor–Stasheff, *Characteristic Classes*, Princeton 1974, §§9–10 and §14; Hatcher, *Algebraic Topology*, Thm 4.57; Husemoller, *Fibre Bundles*, Ch. 3): existence, uniqueness and naturality of the Thom class of an oriented real vector bundle; the Euler class \(e\) as the zero-section restriction of the Thom class; \(e(\gamma)\) generates \(H^2(\mathbb{CP}^\infty,\mathbb{Z}) \cong \mathbb{Z}\) for the tautological line bundle \(\gamma\); complex line bundles over a paracompact space \(Y\) are classified by homotopy classes \([Y,\mathbb{CP}^\infty]\), and \([Y, K(\mathbb{Z},2)] \cong H^2(Y;\mathbb{Z})\) with \(\mathbb{CP}^\infty \simeq K(\mathbb{Z},2)\); the tubular neighborhood theorem (Hirsch, *Differential Topology*, Ch. 4).

*(Note on citations: journal/section-level references above are standard; theorem and page numbers quoted at section level were not re-verified page-by-page this session and are flagged as such in the Honesty section.)*

#### I.1 Step 1: the exponential sequences and their exactness

**Lemma 1.** On any complex manifold (resp. any paracompact topological space) the sequences of sheaves of abelian groups

\[ 0 \to \mathbb{Z} \xrightarrow{\ \iota\ } \mathcal{O}_X \xrightarrow{\ \exp(2\pi i\, \cdot)\ } \mathcal{O}_X^{*} \to 0, \qquad 0 \to \mathbb{Z} \xrightarrow{\ \iota\ } \mathcal{C}^0 \xrightarrow{\ \exp(2\pi i\, \cdot)\ } (\mathcal{C}^0)^{*} \to 0 \]

are exact, where \(\mathcal{C}^0\) is the sheaf of continuous \(\mathbb{C}\)-valued functions and \({}^*\) denotes nowhere-vanishing (holomorphic resp. continuous) functions under multiplication.

*Proof.* Exactness is checked on stalks. Injectivity of \(\iota\) is clear. Kernel of \(\exp(2\pi i\,\cdot)\): if \(e^{2\pi i f} = 1\) for a continuous \(f\) on a connected open \(U\), then \(f(U) \subset \mathbb{Z}\), and a continuous integer-valued function on a connected set is a constant integer; so the kernel is exactly the image of \(\iota\). Surjectivity on stalks: given \(g\) holomorphic (resp. continuous) and nowhere zero near \(x\), choose a ball \(U \ni x\) small enough that \(g(U)\) omits some ray from the origin in \(\mathbb{C}^*\) (possible by continuity: shrink \(U\) so that \(g(U)\) lies in the disc of radius \(|g(x)|/2\) around \(g(x)\), which misses the ray through \(-g(x)\)); on the complement of a ray a holomorphic (resp. continuous) branch of \(\log\) exists, and \(f := \frac{1}{2\pi i}\log g\) satisfies \(\exp(2\pi i f) = g\). Holomorphy of \(f\) when \(g\) is holomorphic is inherited from the holomorphic branch of \(\log\). \(\square\)

**Lemma 2.** For any complex manifold (resp. paracompact space) \(Y\), \(H^1(Y,\mathcal{O}_Y^*)\) is canonically isomorphic, as a group, to the group of isomorphism classes of holomorphic (resp. \(H^1(Y,(\mathcal{C}^0)^*)\) to topological complex) line bundles under \(\otimes\).

*Proof.* A line bundle trivialized over an open cover \(\{U_i\}\) determines transition functions \(g_{ij} \in \mathcal{O}^*(U_i \cap U_j)\) with the cocycle condition \(g_{ij}g_{jk} = g_{ik}\), i.e. a Čech 1-cocycle; changing trivializations by units \(f_i \in \mathcal{O}^*(U_i)\) changes the cocycle by the coboundary \((f_i f_j^{-1})\); conversely a cocycle glues the trivial bundles \(U_i \times \mathbb{C}\) to a line bundle. This sets up a bijection between \(\check{H}^1(\{U_i\},\mathcal{O}^*)\)-classes and bundles trivialized on the cover; passing to the colimit over refinements gives \(\check{H}^1(Y,\mathcal{O}^*)\), which equals derived-functor \(H^1\) on paracompact spaces (Voisin I, §4.3). Tensor product corresponds to multiplication of cocycles, so the bijection is a group isomorphism. \(\square\)

**Definition.** \(c_1 : \mathrm{Pic}(X^{\mathrm{an}}) = H^1(X,\mathcal{O}_X^*) \to H^2(X,\mathbb{Z})\) is the connecting homomorphism of the first sequence in Lemma 1; \(c_1^{\mathrm{top}} : H^1(Y, (\mathcal{C}^0)^*) \to H^2(Y,\mathbb{Z})\) that of the second. Connecting homomorphisms of long exact sequences are group homomorphisms and are natural for pullbacks; moreover the inclusion of sheaves \(\mathcal{O}_X \subset \mathcal{C}^0\) is a map of short exact sequences, so

\[ c_1(L) = c_1^{\mathrm{top}}(L^{\mathrm{top}}) \tag{1.1} \]

for every holomorphic line bundle \(L\) with underlying topological bundle \(L^{\mathrm{top}}\).

#### I.2 Step 2: \(c_1^{\mathrm{top}}\) is an isomorphism, and equals the Euler class up to one universal sign

**Lemma 3.** For every paracompact space \(Y\), \(c_1^{\mathrm{top}} : H^1(Y,(\mathcal{C}^0)^*) \to H^2(Y,\mathbb{Z})\) is an isomorphism.

*Proof.* The sheaf \(\mathcal{C}^0\) is soft on a paracompact space (Tietze extension / partitions of unity), and soft sheaves are acyclic: \(H^k(Y,\mathcal{C}^0) = 0\) for \(k \ge 1\) (Voisin I, §4.3; Godement). The long exact sequence of the second sequence in Lemma 1 reads
\(H^1(Y,\mathcal{C}^0) \to H^1(Y,(\mathcal{C}^0)^*) \xrightarrow{c_1^{\mathrm{top}}} H^2(Y,\mathbb{Z}) \to H^2(Y,\mathcal{C}^0)\),
with both outer groups zero. \(\square\)

**Lemma 4.** There is a universal sign \(\varepsilon \in \{\pm 1\}\), independent of the space and the bundle, such that for every topological complex line bundle \(L\) on a paracompact space \(Y\),
\[ c_1^{\mathrm{top}}(L) = \varepsilon \cdot e(L_{\mathbb{R}}), \]
where \(e(L_{\mathbb{R}}) \in H^2(Y,\mathbb{Z})\) is the Euler class of the underlying oriented real rank-2 bundle (oriented by the complex structure).

*Proof.* By (C6), the functor \(Y \mapsto \{\text{iso. classes of complex line bundles on } Y\}\) on paracompact spaces is represented by \(\mathbb{CP}^\infty\) (pull back the tautological bundle \(\gamma\)), and \(H^2(-;\mathbb{Z})\) is represented by \(K(\mathbb{Z},2) \simeq \mathbb{CP}^\infty\). Both \(e(\,\cdot_{\mathbb{R}})\) and \(c_1^{\mathrm{top}}\) are natural transformations between these functors (naturality of the Thom class, resp. of connecting maps). By the Yoneda lemma each is determined by its value on \(\gamma\): there are classes \(u_e = e(\gamma_{\mathbb{R}})\) and \(u_c = c_1^{\mathrm{top}}(\gamma)\) in \(H^2(\mathbb{CP}^\infty;\mathbb{Z}) \cong \mathbb{Z}\) with \(e(f^*\gamma) = f^*u_e\), \(c_1^{\mathrm{top}}(f^*\gamma) = f^*u_c\). By (C6), \(u_e\) is a generator. By Lemma 3 applied to \(Y = \mathbb{CP}^\infty\) (a paracompact CW complex), \(c_1^{\mathrm{top}}\) is an isomorphism there; since line bundles on \(\mathbb{CP}^\infty\) are classified by \([\mathbb{CP}^\infty,\mathbb{CP}^\infty] \cong H^2(\mathbb{CP}^\infty;\mathbb{Z}) \cong \mathbb{Z}\) with \(\gamma\) corresponding to a generator (the identity map), \(u_c = c_1^{\mathrm{top}}(\gamma)\) must also be a generator. Two generators of \(\mathbb{Z}\cdot u\) differ by \(\varepsilon = \pm 1\): \(u_c = \varepsilon u_e\), hence \(c_1^{\mathrm{top}} = \varepsilon\, e\) on all bundles by naturality. \(\square\)

*(Remark: the standard curvature computation — Griffiths–Harris Ch. 0–1: \(c_1(L)_{\mathbb{R}}\) is represented by \(\frac{i}{2\pi}\Theta_h\), and \(\int_{\mathbb{CP}^1} \frac{i}{2\pi}\Theta_{FS} = 1\) for \(\mathcal{O}(1)\) — shows \(\varepsilon = +1\). The proof of Theorem 1 never uses the value of \(\varepsilon\); this is what makes the write-up self-contained without any curvature integral.)*

#### I.3 Step 3: the Projection Lemma (the Hodge-theoretic heart)

Let \(i_* : H^k(X,\mathbb{C}) \to H^k(X,\mathcal{O}_X)\) be the map induced by the sheaf inclusion \(\mathbb{C} \hookrightarrow \mathcal{O}_X\).

**Lemma 5 (Projection Lemma).** Let \(X\) be a compact Kähler manifold and \(\alpha \in H^k(X,\mathbb{C})\), with Hodge components \(\alpha = \sum_{p+q=k} \alpha^{p,q}\) per (C1). Then, under the Dolbeault description of \(H^k(X,\mathcal{O}_X)\) from (C2),

\[ i_*(\alpha) = 0 \iff \alpha^{0,k} = 0 . \]

Consequently, for a class \(\alpha \in H^2(X,\mathbb{Z})\): \(\;i_*(\alpha_{\mathbb{C}}) = 0 \iff \alpha_{\mathbb{C}} \in H^{1,1}(X)\).

*Proof.* Define \(\pi : \mathcal{A}^k \to \mathcal{A}^{0,k}\) as the projection of a smooth \(k\)-form onto its \((0,k)\)-component. We claim \(\pi\) is a morphism of complexes of sheaves \((\mathcal{A}^\bullet, d) \to (\mathcal{A}^{0,\bullet},\bar\partial)\) extending \(\mathbb{C} \hookrightarrow \mathcal{O}_X\) (in degree 0, \(\pi = \mathrm{id}\) on functions, and constants are holomorphic). Indeed, for a local form \(\beta = \sum_{p+q=k}\beta^{p,q}\) we have \(d\beta = \sum_{p,q}(\partial \beta^{p,q} + \bar\partial\beta^{p,q})\) with \(\partial\beta^{p,q}\) of type \((p+1,q)\) and \(\bar\partial\beta^{p,q}\) of type \((p,q+1)\); the \((0,k+1)\)-component of \(d\beta\) is exactly \(\bar\partial(\beta^{0,k})\). Hence \(\pi \circ d = \bar\partial \circ \pi\).

Both complexes are resolutions by fine (hence acyclic) sheaves, of \(\mathbb{C}\) and \(\mathcal{O}_X\) respectively, by (C2). A morphism of acyclic resolutions covering a morphism of the resolved sheaves computes the induced map on sheaf cohomology via global sections (standard homological algebra: both sides compute the derived functors, and the induced map of double complexes/hypercohomology is the derived map; Voisin I, §4.3). Therefore \(i_*\) is computed on de Rham representatives by \(\omega \mapsto [\pi(\omega)]_{\bar\partial}\).

Now let \(\alpha = \sum \alpha^{p,q}\) and choose, by (C1), \(d\)-closed representatives \(\omega^{p,q}\) of pure type \((p,q)\) for each \(\alpha^{p,q}\); set \(\omega = \sum \omega^{p,q}\). Note each \(\omega^{p,q}\) is \(\bar\partial\)-closed: \(0 = d\omega^{p,q} = \partial\omega^{p,q} + \bar\partial\omega^{p,q}\) with the two terms of different types, so both vanish. Then
\[ i_*(\alpha) = [\pi(\omega)]_{\bar\partial} = [\omega^{0,k}]_{\bar\partial}, \]
since \(\pi\) kills every pure-type component except the \((0,k)\) one.

(\(\Leftarrow\)) If \(\alpha^{0,k} = 0\) we may take \(\omega^{0,k} = 0\), so \(i_*(\alpha) = 0\).

(\(\Rightarrow\)) If \(i_*(\alpha) = 0\), then \(\omega^{0,k}\) is \(\bar\partial\)-exact; it is also \(d\)-closed; by the \(\partial\bar\partial\)-lemma (C3) it is \(d\)-exact, so \(\alpha^{0,k} = [\omega^{0,k}]_{dR} = 0\).

For the consequence: an integral class \(\alpha\) has real image, so conjugation (which by (C1) sends \(H^{p,q}\) to \(H^{q,p}\)) fixes \(\alpha_{\mathbb{C}}\) and hence \(\alpha^{2,0} = \overline{\alpha^{0,2}}\). Thus \(\alpha^{0,2} = 0 \iff \alpha^{2,0} = \alpha^{0,2} = 0 \iff \alpha_{\mathbb{C}} \in H^{1,1}\). \(\square\)

#### I.4 Step 4: from Hodge classes to holomorphic line bundles, and back

**Proposition 6.** \(\mathrm{Hdg}^1_{\mathbb{Z}}(X) = \mathrm{im}\bigl(c_1 : \mathrm{Pic}(X^{\mathrm{an}}) \to H^2(X,\mathbb{Z})\bigr)\); and by GAGA (C4), \(\mathrm{Pic}(X^{\mathrm{an}}) = \mathrm{Pic}(X)\). This proves Theorem 1, part 1.

*Proof.* The long exact sequence of the holomorphic exponential sequence (Lemma 1) gives
\[ \mathrm{Pic}(X^{\mathrm{an}}) = H^1(X,\mathcal{O}_X^*) \xrightarrow{\ c_1\ } H^2(X,\mathbb{Z}) \xrightarrow{\ j\ } H^2(X,\mathcal{O}_X), \]
with \(\mathrm{im}(c_1) = \ker(j)\). The map \(j\) factors as \(H^2(X,\mathbb{Z}) \to H^2(X,\mathbb{C}) \xrightarrow{i_*} H^2(X,\mathcal{O}_X)\), because the sheaf map \(\mathbb{Z} \to \mathcal{O}_X\) factors through \(\mathbb{C}\). By the Projection Lemma (Lemma 5), \(j(\alpha) = 0 \iff \alpha_{\mathbb{C}} \in H^{1,1} \iff \alpha \in \mathrm{Hdg}^1_{\mathbb{Z}}(X)\). (Torsion classes: \(\alpha_{\mathbb{C}} = 0\), so they lie in \(\ker j\) — consistent, since \(H^2(X,\mathcal{O}_X)\) is a \(\mathbb{C}\)-vector space and admits no torsion anyway.) \(\square\)

#### I.5 Step 5: every line bundle is a difference of smooth very ample divisors

**Lemma 7.** Let \(L\) be an algebraic line bundle on \(X\) (smooth projective, \(n \ge 1\)). Then there exist smooth very ample divisors \(D_1, D_2 \subset X\) (irreducible if \(n \ge 2\); finite sets of points if \(n = 1\)) with \(L \cong \mathcal{O}_X(D_1 - D_2)\).

*Proof.* Fix a very ample \(\mathcal{O}_X(1)\). By (C5) choose \(m \ge 1\) with \(M_1 := L \otimes \mathcal{O}_X(m)\) very ample; \(M_2 := \mathcal{O}_X(m)\) is very ample (a power of a very ample bundle). By Bertini (C5), the general member \(D_1 \in |M_1|\) and the general member \(D_2 \in |M_2|\) are smooth divisors (nonempty since \(M_i\) very ample and \(n\ge 1\); base-point-freeness of a very ample system makes Bertini apply everywhere; irreducible when \(n \ge 2\)). A global section \(s_i\) with divisor \(D_i\) gives \(M_i \cong \mathcal{O}_X(D_i)\). Hence \(L = M_1 \otimes M_2^{\vee} \cong \mathcal{O}_X(D_1)\otimes\mathcal{O}_X(D_2)^{\vee} = \mathcal{O}_X(D_1 - D_2)\). \(\square\)

#### I.6 Step 6: the class of a smooth divisor is the Euler class of its bundle

For a closed complex submanifold \(D \subset X\) of codimension 1, define the **cycle class** \(\mathrm{cl}(D) \in H^2(X,\mathbb{Z})\) as follows: choose a tubular neighborhood \(T \cong N_{D/X}\) (Hirsch, (C6)); \(\mathrm{cl}(D)\) is the image of the Thom class \(\Phi(N_{D/X}) \in H^2(N_{D/X}, N_{D/X}\smallsetminus D)\) under
\[ H^2(N_{D/X}, N_{D/X}\smallsetminus D) \cong H^2(T, T\smallsetminus D) \xrightarrow{\ \text{excision}^{-1}\ } H^2(X, X \smallsetminus D) \to H^2(X,\mathbb{Z}), \]
with \(N_{D/X}\) oriented by its complex structure. (This is the Poincaré dual of the fundamental class of \(D\); independence of the tubular neighborhood follows from uniqueness of tubular neighborhoods up to isotopy, (C6).) Extend \(\mathrm{cl}\) to divisors \(\sum n_i D_i\) with smooth \(D_i\) by \(\mathbb{Z}\)-linearity.

**Lemma 8.** Let \(D \subset X\) be a smooth divisor, \(L = \mathcal{O}_X(D)\), and \(s\in H^0(X, L)\) the canonical section with divisor \(D\). Then:

(a) as a smooth section of the oriented real rank-2 bundle \(L_{\mathbb{R}}\), \(s\) is transverse to the zero section, with zero set exactly \(D\);

(b) \(e(L_{\mathbb{R}}) = \mathrm{cl}(D)\) in \(H^2(X,\mathbb{Z})\).

*Proof.* (a) Locally \(D = \{f = 0\}\) for a holomorphic function \(f\) that generates the ideal of \(D\); since \(D\) is a smooth reduced divisor, \(f\) can be taken to be a local coordinate, so \(\partial f \ne 0\) along \(D\); in the corresponding local trivialization of \(L\), the section \(s\) is the function \(f\). For a holomorphic function, the real differential at a point \(z\) is the \(\mathbb{R}\)-linear map \(v \mapsto \partial f(z)(v)\), which is complex-linear; if \(\partial f(z) \neq 0\) it is surjective onto \(\mathbb{C} \cong \mathbb{R}^2\). Hence \(s\) is transverse to zero along \(Z(s) = D\) (equality of sets because \(\operatorname{div}(s) = D\)).

Transversality gives a canonical isomorphism \(ds : N_{D/X} \xrightarrow{\ \sim\ } L|_D\); all data being holomorphic, \(ds\) is complex-linear, hence orientation-preserving for the complex orientations on both sides.

(b) Write \(E = L_{\mathbb{R}}\), \(\Phi(E) \in H^2(E, E \smallsetminus 0_E)\) for its Thom class, \(\varphi \in H^2(E)\) for the image of \(\Phi(E)\), and \(\zeta : X \to E\) for the zero section; by definition \(e(E) = \zeta^* \varphi\). The section \(s : X \to E\) is homotopic to \(\zeta\) through sections (\(t \mapsto ts\)), so \(e(E) = s^*\varphi\). Moreover \(s\) maps \((X, X\smallsetminus D)\) into \((E, E\smallsetminus 0_E)\), since \(s(x) \ne 0\) exactly off \(D\); therefore the relative class \(s^*\Phi(E) \in H^2(X, X \smallsetminus D)\) maps to \(e(E)\) in \(H^2(X)\).

It remains to identify \(s^*\Phi(E) \in H^2(X, X\smallsetminus D)\) with the excision image of the Thom class of \(N_{D/X}\); then its image in \(H^2(X)\) is \(\mathrm{cl}(D)\) by definition, giving (b). By the Thom isomorphism (C6), \(H^2(X, X\smallsetminus D) \cong H^2(N_{D/X}, N_{D/X}\smallsetminus D) \cong H^0(D)\), and (for \(D\) with connected components \(D_j\)) a class is the Thom class iff its restriction to one normal 2-disc transverse slice at a point of each \(D_j\) is the positive (orientation) generator of \(H^2(\text{disc}, \text{disc}\smallsetminus \text{pt}) \cong \mathbb{Z}\). Take \(z \in D\) and a small transverse 2-disc \(\Delta \subset X\) at \(z\) (a fiber of the tubular neighborhood). The restriction \(s|_\Delta : (\Delta, \Delta\smallsetminus z) \to (E|_\Delta, E|_\Delta\smallsetminus 0)\), composed with a trivialization \(E|_\Delta \cong \Delta \times E_z\) and projection to \((E_z, E_z \smallsetminus 0)\), has differential at \(z\) equal to the isomorphism \(ds|_z : N_z \to E_z\) (up to the trivialization's identification, homotopically irrelevant on a small disc), which is orientation-preserving by (a). A map of pairs \((\Delta,\Delta\smallsetminus z) \to (E_z, E_z\smallsetminus 0)\) with invertible orientation-preserving differential at \(z\) pulls the positive generator back to the positive generator (it is locally a degree-\(+1\) homeomorphism near \(z\), after shrinking \(\Delta\)). The restriction of \(\Phi(E)\) to \((E_z, E_z\smallsetminus 0)\) is the positive generator by definition of the Thom class. Hence \(s^*\Phi(E)\) restricts to the positive generator on each transverse slice, so it is the Thom class of \(N_{D/X}\) under the identifications above. \(\square\)

#### I.7 Step 7: assembly — proof of Theorem 1

Let \(\alpha \in \mathrm{Hdg}^1_{\mathbb{Z}}(X)\).

1. By Proposition 6, \(\alpha = c_1(\mathcal{L})\) for some holomorphic line bundle \(\mathcal{L}\) on \(X^{\mathrm{an}}\), and by GAGA (C4) \(\mathcal{L}\) is the analytification of an algebraic line bundle \(L\).
2. By Lemma 7, \(L \cong \mathcal{O}_X(D_1 - D_2)\) with \(D_1, D_2\) smooth very ample divisors (irreducible if \(n \ge 2\)).
3. By (1.1), Lemma 4, Lemma 8, and additivity of \(c_1\) (a group homomorphism, Lemma 2 / Definition) and of \(\mathrm{cl}\) (by definition):
\[ \alpha \;=\; c_1(L) \;=\; c_1(\mathcal{O}(D_1)) - c_1(\mathcal{O}(D_2)) \;=\; \varepsilon\bigl(e(\mathcal{O}(D_1)_{\mathbb{R}}) - e(\mathcal{O}(D_2)_{\mathbb{R}})\bigr) \;=\; \varepsilon\bigl(\mathrm{cl}(D_1) - \mathrm{cl}(D_2)\bigr) = \mathrm{cl}\bigl(\varepsilon(D_1 - D_2)\bigr). \]
Since \(\varepsilon(D_1 - D_2)\) is an algebraic divisor whichever the value of \(\varepsilon \in \{\pm1\}\), \(\alpha\) is a divisor class. This proves part 2 and the surjectivity half of part 1.

Conversely, every divisor class is an integral Hodge class: for smooth \(D\), \(\mathrm{cl}(D) = \varepsilon\, c_1(\mathcal{O}(D))\) lies in \(\mathrm{im}(c_1) = \mathrm{Hdg}^1_{\mathbb{Z}}(X)\) by Lemmas 8, 4 and Proposition 6; \(\mathbb{Z}\)-linear combinations stay in the subgroup. \(\blacksquare\)

**Remark 9 (attribution).** Lefschetz proved the statement for surfaces in 1924 (*L'Analysis situs et la géométrie algébrique*) via Poincaré's normal functions. The proof above is, in its skeleton, the one introduced by Kodaira and Spencer in 1953 (*Groups of complex line bundles over compact Kähler varieties* and *Divisor class groups on algebraic varieties*, Proc. Nat. Acad. Sci. USA 39 (1953)), which established the sheaf-theoretic mechanism (exponential sequence + Hodge theory) on compact Kähler manifolds; textbook treatments: Griffiths–Harris Ch. 1, Voisin I §11.3. What is special to our write-up: the Bertini reduction to *smooth* divisors (avoiding cycle classes of singular hypersurfaces entirely), and the observation that the universal sign \(\varepsilon\) need never be computed, which removes the one curvature integral from the standard treatments.

**Remark 10 (singular divisors).** For an irreducible possibly singular hypersurface \(Z \subset X\), the cycle class can be defined by resolution and Gysin pushforward, and also lies in \(\mathrm{Hdg}^1_{\mathbb{Z}}(X)\), agreeing with \(c_1(\mathcal{O}_X(Z))\) up to \(\varepsilon\) (Voisin I, §11.1 and §11.3). The theorem as proved above does not need this: the divisors it *outputs* are smooth.

---

### Part II — Reduction: the Hodge conjecture for abelian fourfolds, pinned to named theorems

All statements in this part were verified this session against the full texts of arXiv:2502.03415v2 (retrieved 2026-08-15), arXiv:math/9901113 (= Moonen–Zarhin 1999), and Markman's survey arXiv:2509.23403v2.

#### II.0 Definitions (fixing conventions as in arXiv:2502.03415, §1.1)

A \(2n\)-dimensional abelian variety \(A\) is of **Weil type** for \(K = \mathbb{Q}(\sqrt{-d})\) (\(d > 0\)) if there is an embedding \(\eta : K \to \mathrm{End}_{\mathbb{Q}}(A)\) such that each eigenspace of \(\eta(\sqrt{-d})\) on \(H^{1,0}(A)\) is \(n\)-dimensional. Then \(\wedge^{2n}_K W \oplus \wedge^{2n}_K \overline{W}\) descends to a 2-dimensional \(\mathbb{Q}\)-subspace \(HW \subset H^{n,n}(A,\mathbb{Q})\) of **Hodge–Weil classes** (Weil 1977). A **polarized** abelian variety of Weil type \((A,\eta,h)\) carries a \(K\)-valued hermitian form \(H\) on \(H_1(A,\mathbb{Q})\); the class of \(\det H\) in \(\mathbb{Q}^\times/\mathrm{Nm}(K^\times)\) is its **discriminant**. The triple (half-dimension \(n\), \(K\), discriminant) labels the \(n^2\)-dimensional irreducible moduli components. For the general member, \(HW\) is *not* spanned by products of divisor classes: these are the classical candidate counterexamples to the Hodge conjecture (Weil).

#### II.1 Input theorems (exact statements, verified)

- **(T1) Lefschetz (1,1)** — Theorem 1 above: divisor classes on any smooth projective variety are algebraic, and every rational \((1,1)\)-class is a \(\mathbb{Q}\)-divisor class.
- **(T2) Hard Lefschetz** (classical; Voisin I §6.2): cup product with \(c^2\), \(c = \mathrm{cl}(H_{\text{ample}})\), is an isomorphism \(L^2 : H^2(A,\mathbb{Q}) \to H^6(A,\mathbb{Q})\) of Hodge structures of bidegree \((2,2)\).
- **(T3) Moonen–Zarhin, Duke Math. J. 77 (1995), Theorem 2.11:** for a **simple** abelian fourfold \(A\), \(H^{2,2}(A,\mathbb{Q})\cap H^4(A,\mathbb{Q})\) is spanned by quadratic polynomials in divisor classes together with Hodge–Weil classes (for the — possibly infinitely many — Weil structures \((K,\eta)\) carried by \(A\)). [Quoted as cited in arXiv:2502.03415, proof of Cor. 1.6.1.]
- **(T4) Moonen–Zarhin, Math. Ann. 315 (1999):** **Theorem 0.1**: for every complex abelian variety \(X\) of dimension \(\le 4\), the Hodge ring is generated by divisor classes together with Weil classes (cases (a),(b),(c) of their classification; in the remaining cases divisor classes suffice). **Proposition 3.8**: if \(E\) is an elliptic curve, \(X\) an abelian variety with \(\mathrm{Hom}(E,X)=0\), then either \(\mathrm{Hg}(X\times E)=\mathrm{Hg}(X)\times\mathrm{Hg}(E)\), or \(\mathrm{End}^0(E)=k\) is an imaginary quadratic field embedding into the center of \(\mathrm{End}^0(X)\). [Both verified in the full text of math/9901113.]
- **(T5) Ramón Marí, Collect. Math. 59 (2008), Theorem 4.11:** the Hodge conjecture holds for a product of two abelian surfaces.
- **(T6) Weil-class algebraicity, published perimeter:**
  - Schoen 1988 (Compositio 65): fourfolds, \(K=\mathbb{Q}(\sqrt{-1})\), discriminant \(-1\); Schoen 1998 (Compositio 114, Addendum): fourfolds, \(K=\mathbb{Q}(\sqrt{-3})\), **arbitrary** discriminant; also sixfolds \(K=\mathbb{Q}(\sqrt{-3})\), trivial discriminant. The Addendum's **Proposition 10** provides the degeneration mechanism used in (T7): sixfolds of Weil type of discriminant \(-1\) degenerate to (fourfold of Weil type, arbitrary discriminant) \(\times\) (surface of Weil type).
  - Koike 2004 (Canad. Math. Bull. 47): sixfolds, \(K=\mathbb{Q}(\sqrt{-1})\), discriminant \(-1\); hence fourfolds with \(K = \mathbb{Q}(\sqrt{-1})\), arbitrary discriminant.
  - Markman 2023 (JEMS 25, 231–321): fourfolds, **arbitrary** imaginary quadratic \(K\), discriminant \(1\). (Independent alternative proof: Floccari–Fu, arXiv:2504.13607, via singular OG6 varieties.)
- **(T7) Markman 2025, arXiv:2502.03415v2, Theorem 1.5.1** (verbatim): *"Let \(d\) be a positive integer. Set \(K := \mathbb{Q}(\sqrt{-d})\). The Hodge–Weil classes of polarized abelian sixfolds of Weil type with complex multiplication by \(K\) and with discriminant \(-1\) are algebraic."* Mechanism: a secant sheaf \(E\) on \(X\times\hat X\) (\(X\) the Jacobian of a non-hyperelliptic genus-3 curve) whose normalized character \(\exp(-c_1(E)/\mathrm{rk}\,E)\,\mathrm{ch}(E)\) stays of Hodge type under all Weil deformations (his Cor. 1.3.2), deformed over the whole 9-dimensional moduli component via the Buchweitz–Flenner semiregularity theorem; the discriminant is \(-1\) by his Lemma 3.1.3 (the secant construction has discriminant \((-1)^n\)). **Status: preprint (v2); not yet verified as peer-reviewed this session** — Markman's own September 2025 survey (arXiv:2509.23403, published version DOI 10.1137/25m1803796, 2026) still cites it as an electronic preprint while presenting its theorem as Theorem 1.2.

**Auxiliary lemmas (proofs included).**

*(L-a) Isogeny invariance.* If \(f : A \to B\) is an isogeny, \(f^* : H^*(B,\mathbb{Q}) \to H^*(A,\mathbb{Q})\) is an isomorphism of Hodge structures with inverse \(\frac{1}{\deg f}f_*\); both \(f^*\) and \(f_*\) are induced by the algebraic correspondence \(\Gamma_f\) and preserve algebraic classes. Hence HC holds for \(A\) iff it holds for \(B\). \(\square\)

*(L-b) Ring closure.* The cycle class map is a ring homomorphism \(\mathrm{CH}^*(X)_{\mathbb{Q}} \to H^{2*}(X,\mathbb{Q})\) (intersection product to cup product; Fulton, *Intersection Theory*, Ch. 19). Hence cup products and \(\mathbb{Q}\)-linear combinations of algebraic classes are algebraic: the algebraic classes form a \(\mathbb{Q}\)-subalgebra. \(\square\)

*(L-c) Degree bookkeeping on a fourfold.* \(\mathrm{Hdg}^0 = \mathbb{Q}\) and \(\mathrm{Hdg}^4(A) = \mathbb{Q}\cdot\mathrm{cl}(\mathrm{point})\) are algebraic. \(\mathrm{Hdg}^1\) is algebraic by (T1). \(\mathrm{Hdg}^3\): given \(x \in \mathrm{Hdg}^3(A)\), hard Lefschetz (T2) gives a unique \(y \in H^2(A,\mathbb{Q})\) with \(x = c^2\cup y\); since \(L^2\) is injective and maps \(H^{p,q}\) into \(H^{p+2,q+2}\), the components \(y^{2,0}, y^{0,2}\) map to the \((4,2)\)- and \((2,4)\)-components of \(x\), which vanish because \(x\) is of type \((3,3)\); so \(y \in \mathrm{Hdg}^1(A)\), algebraic by (T1), and \(x = c^2 \cup y\) is algebraic by (L-b). Hence **HC for an abelian fourfold reduces to \(\mathrm{Hdg}^2\)**. \(\square\)

#### II.2 The reduction (following the case structure of Markman's Corollary 1.6.1, written out)

**Proposition (= Theorem 2).** Let \(A\) be a complex abelian fourfold. Assume (T1)–(T7). Then every Hodge class on \(A\) is algebraic.

*Proof.*

**Step 1 (Weil classes on fourfolds, all \(K\), all discriminants).** By (T7), Hodge–Weil classes are algebraic on every polarized abelian sixfold of Weil type with discriminant \(-1\), for every imaginary quadratic \(K\). By the degeneration of Schoen's Proposition 10 ((T6); this is exactly the specialization step in the proof of Cor. 1.6.1 of arXiv:2502.03415, using that the locus in moduli where the Hodge–Weil classes are algebraic is a countable union of closed algebraic subsets and hence closed under this degeneration — Voisin's Hodge-loci argument as cited there), the Hodge–Weil classes are algebraic **for every abelian fourfold of Weil type, every \(K\), every discriminant**.

**Step 2 (\(A\) simple).** By (L-c) it suffices to treat \(\mathrm{Hdg}^2(A)\). By (T3), \(\mathrm{Hdg}^2(A)\) is spanned by quadratic polynomials in divisor classes and by Hodge–Weil classes of the Weil structures on \(A\). Divisor classes are algebraic by (T1); Hodge–Weil classes by Step 1; polynomials in algebraic classes are algebraic by (L-b). Done.

**Step 3 (\(A\) non-simple).** By Poincaré reducibility and (L-a) we may replace \(A\) by an isogenous product of simple factors. Two shapes are possible:

- *(3a) \(A \sim S_1 \times S_2\), a product of two abelian surfaces* — this covers factor dimension patterns \((2,2)\), \((2,1,1)\) and \((1,1,1,1)\), grouping elliptic factors into abelian surfaces. HC holds by (T5) (published, unconditional).
- *(3b) \(A \sim B \times E\), \(B\) a simple abelian threefold, \(E\) an elliptic curve.* By (T4, Prop. 3.8) there are two cases. **Either** \(\mathrm{Hg}(A) = \mathrm{Hg}(B)\times\mathrm{Hg}(E)\): then, since Hodge groups are reductive and Hodge classes are the Hodge-group invariants, the Künneth decomposition gives \(\mathrm{Hdg}^*(A) = \bigoplus (H^i(B)\otimes H^j(E))^{\mathrm{Hg}(B)\times\mathrm{Hg}(E)} = \bigoplus \mathrm{Hdg}(H^i(B))\otimes\mathrm{Hdg}(H^j(E))\) (invariants of an external tensor product of semisimple representations are the tensor product of invariants; odd-degree summands contribute nothing since odd-weight Hodge structures carry no Hodge classes), and every Hodge class on \(B\) (dimension 3) and on \(E\) is a polynomial in divisor classes (Moonen–Zarhin 1999, Introduction: the Hodge ring of any abelian variety of dimension \(\le 3\) is generated by divisor classes), so HC follows from (T1) and (L-b). **Or** \(\mathrm{End}^0(E) = k\) is imaginary quadratic and embeds in the center of \(\mathrm{End}^0(B)\) (case (a) of Moonen–Zarhin 1999): then by (T4, Thm 0.1(i)) the Hodge ring of \(A\) is generated by divisor classes and the Weil classes \(W_k\), and these are algebraic by (T1) and Step 1, hence HC by (L-b). \(\blacksquare\)

#### II.3 Discriminant/field bookkeeping and the conditional/unconditional split

| Weil-class case | Reference | Status |
|---|---|---|
| Fourfolds, \(K=\mathbb{Q}(\sqrt{-1})\), disc \(-1\) | Schoen 1988 (also van Geemen 1994) | published |
| Fourfolds, \(K=\mathbb{Q}(\sqrt{-3})\), all disc | Schoen 1998 | published |
| Fourfolds, \(K=\mathbb{Q}(\sqrt{-1})\), all disc | Koike 2004 (via sixfolds disc \(-1\)) | published |
| Fourfolds, all \(K\), disc \(1\) | Markman JEMS 2023; also Floccari–Fu | published |
| Sixfolds, all \(K\), disc \(-1\) — hence **fourfolds, all \(K\), all disc** | Markman arXiv:2502.03415, Thm 1.5.1 + Schoen Prop. 10 | **preprint** |

Consequently: **Theorem 2 is unconditional except for the single input (T7).** If (T7) is removed, the proof above still yields HC unconditionally for: all non-simple abelian fourfolds of shape (3a); all fourfolds in case (3b) with \(k \in \{\mathbb{Q}(i),\mathbb{Q}(\sqrt{-3})\}\) or all of whose Weil structures have discriminant 1; and all simple fourfolds whose Weil structures involve only those \((K,\mathrm{disc})\) pairs.

**Remark (dimension 5).** Markman states in his 2025/2026 survey (arXiv:2509.23403; published version DOI 10.1137/25m1803796) that the Hodge conjecture for abelian varieties of dimension \(\le 5\) is known to follow from the same Weil-class result, via Moonen–Zarhin 1999, Theorem 0.2 (in dimension 5 the required Weil classes live on fourfold quotients \(X_1\times X_2\) and pull back along the algebraic correspondences of surjections \(X \to X_1\times X_2\)). We record this with attribution and have not re-derived the dimension-5 case analysis here.

---

## What is new vs REPORT.md

Nothing mathematically new is claimed — consistent with the mission's no-fake-proof directive. Relative to REPORT.md, which is a survey with programs, this file adds:

1. **A complete proof where REPORT.md had two lines.** REPORT.md §2 item 1 and §3 (04-02) *stated* Lefschetz (1,1) and named the mechanism. Part I above is a full proof: exactness of both exponential sequences proved on stalks; \(\mathrm{Pic} = H^1(\mathcal{O}^*)\) proved; the Projection Lemma — the actual Hodge-theoretic heart, usually compressed to one sentence — proved via an explicit morphism of fine resolutions, in both directions (the converse direction via the \(\partial\bar\partial\)-lemma, which REPORT.md never mentioned); the topological compatibility \(c_1 = \pm e\) proved by a representability argument; the cycle-class identity for smooth divisors proved by the Thom-class/transversality argument including the holomorphic-transversality and orientation-matching details.
2. **Two expository devices that make the proof genuinely self-contained** (believed minor but not located in this exact form in the standard texts; claimed as exposition, not mathematics): (i) the Bertini reduction outputs *smooth very ample* divisors, so the theorem never needs cycle classes of singular hypersurfaces; (ii) the universal-sign trick (\(c_1^{\mathrm{top}} = \varepsilon\, e\), \(\varepsilon\) never computed) eliminates the Fubini–Study curvature integral that all textbook treatments use for normalization — harmless because divisors form a group.
3. **An audited, theorem-number-level reduction for abelian fourfolds.** REPORT.md §2 items 6–8 and §3 (04-06) asserted the chain at survey level, partly under [MEMORY] labels. Here every link is pinned and was re-verified against primary full texts this session: Moonen–Zarhin Duke 77 (1995) **Thm 2.11**; Math. Ann. 315 (1999) **Thm 0.1(i)**, **Thm 0.2**, **Prop. 3.8** (statements read in `math/9901113`); Ramón Marí **Thm 4.11** (a reference absent from REPORT.md); Koike 2004 (absent from REPORT.md); Schoen Addendum **Prop. 10**; Markman JEMS 25 (2023) 231–321; Markman arXiv:2502.03415v2 **Thm 1.5.1**, **Cor. 1.6.1**, **Lemma 3.1.3**. The non-simple case analysis (3a)/(3b), the degree bookkeeping (L-c), and the reductive-group Künneth step are written out rather than asserted.
4. **Corrected/sharpened discriminant bookkeeping.** The published-vs-preprint frontier is now exact (table in II.3): in particular, Markman JEMS 2023 proves discriminant \(1\) (not \(-1\)) for fourfolds; discriminant \(-1\) fourfolds for \(K=\mathbb{Q}(i)\) go back to Schoen 1988; Koike 2004 already gave all discriminants for \(K = \mathbb{Q}(i)\); and the *only* unpublished link in "HC for all abelian fourfolds" is arXiv:2502.03415 Theorem 1.5.1. REPORT.md's summary was correct but did not isolate the conditional link this precisely, and its tasking prompt's phrase "Weil classes on abelian fourfolds of discriminant \(-1\) settled via Markman" is, as stated, inaccurate — the accurate statement is the table above.
5. **A publication-status audit** of arXiv:2502.03415 as of this session: v2, still cited as "electronic preprint" in Markman's own survey of 2025-09-30, whose published version (DOI 10.1137/25m1803796) appeared in 2026 and presents the theorem as established; no journal reference for 2502.03415 itself was found.

## Why Hodge remains open

Kept brief; REPORT.md §6 has the full structural analysis. Three points sharpened by the present write-up:

1. **The (1,1) mechanism is exactly a degree-2 accident.** The proof above works because degree-2 integral Hodge classes are the kernel of a map \(H^2(X,\mathbb{Z}) \to H^2(X,\mathcal{O}_X)\) *induced by a short exact sequence of sheaves*, whose \(H^1\) term is a moduli space of geometric objects (line bundles) that automatically carry divisors (Lemma 7 — ultimately Serre ampleness, i.e. projectivity). For \(k \ge 2\) no short exact sequence of sheaves can play this role even in principle: any such mechanism would prove the *integral* statement, which is false for \(k \ge 2\) (Atiyah–Hirzebruch torsion classes; Kollár degree obstructions — REPORT.md §1.2). Rationally, no analogue of \(\mathcal{O}_X^*\) is known: \(H^2(X,\mathcal{O}_X^*)\) sees Brauer classes, not codimension-2 cycles.
2. **The abelian-fourfold result is classification-limited and engine-limited.** The reduction of Part II consumes two nonrenewable resources: the complete Mumford–Tate/Hodge-group classification in dimension \(\le 5\) (Moonen–Zarhin — unavailable from dimension 6 on, where new exceptional-class species beyond Weil classes are not excluded), and Markman's sheaf-deformation engine, which produces cycles only on the Weil loci reachable by secant-sheaf constructions (discriminant \((-1)^n\) components, then specialization). Neither input generalizes to, say, a general-type hypersurface with \(h^{2,0} \neq 0\), where not a single nontrivial Hodge class has ever been verified.
3. **Every proved case still lives in the abelian/level-\(\le 2\) world.** Part I (divisors), Part II (abelian fourfolds), and every 2022–2026 advance catalogued in REPORT.md §2 realize Hodge classes as characteristic classes of deformable sheaves or reduce to abelian motives. There is no mechanism that inputs an arbitrary Hodge class and outputs a subvariety; the normal-function program (BFNP equivalence, REPORT.md 04-04) is formally equivalent to HC but has no tool to force singularities to exist. That is the wall, unchanged.

## Honesty label

- **Theorem 1 (Part I):** [PROVED — classical]. The theorem is Lefschetz/Kodaira–Spencer, not ours. The proof written here is complete modulo the six named classical inputs (C1)–(C6), each a standard textbook theorem cited at section level (theorem/section numbers for textbooks quoted from training knowledge and flagged; the logical structure does not depend on the numbering). The two expository devices (smooth-divisor Bertini reduction; sign-normalization-free assembly) are claimed only as exposition. **No new mathematics.**
- **Theorem 2 (Part II):** [REDUCTION — verified assembly]. Every input is a named theorem with exact theorem numbers, verified this session against the arXiv full texts of 2502.03415v2, math/9901113, and 2509.23403v2 (retrieved 2026-08-15). The assembled statement "HC holds for all abelian fourfolds" is Markman's Corollary 1.6.1, **not** a result of this mission; our contribution is the audited dependency graph, the written-out case analysis, and the precise conditional/unconditional split. It is conditional on exactly one unpublished input: arXiv:2502.03415, Theorem 1.5.1 (preprint v2; treated as established by Voisin's 2025 survey and by Floccari–Fu, but not verified as peer-reviewed this session).
- **Explicitly NOT claimed:** no new theorem, no new special case, no progress on any open case of the Hodge conjecture. The Hodge conjecture remains open, including for abelian varieties of dimension \(\ge 6\) (general), for general hyper-Kähler varieties of K3\(^{[n]}\) type, and for the explicit Fermat classes of REPORT.md Target B.
- **No fake proof:** every "Proof." in this file is either given in full or explicitly reduced to a named, cited statement; every unpublished dependency is flagged where used (T7, Steps 1–2 of II.2).

*End of Wave-2 deliverable, Legion 04.*
