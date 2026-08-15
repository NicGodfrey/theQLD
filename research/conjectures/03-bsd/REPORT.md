# Birch and Swinnerton-Dyer — Legion 03

**Commander's execution note (honesty first).** The mission ordered 10 nested specialist children
(03-01 … 03-10). The toolset available to this commander seat contains **no subagent-spawning tool**,
so the children could not be launched. Per standing orders ("if children fail to launch, do the work
yourself"), all ten angles were executed directly by the commander and are reported in §3. All
numerical computations quoted below were **actually executed in this session** in Pari/GP 2.15.4
(script preserved as [`verification.gp`](./verification.gp) in this directory).

**Honesty labels used throughout:**

| Label | Meaning |
|---|---|
| [PROVED–CLASSICAL] | A theorem of the classical literature; where a proof is given here it is complete and was checked line by line. |
| [PROVED–CITED] | A theorem of the modern literature, cited but not reproved here. |
| [COMPUTED] | Numerically computed in this session (floating point with Pari's error management; a computation, not a formal proof, except where nonvanishing at stated precision is the only thing used). |
| [SYNTHESIS] | An organizing analysis of known results. The substance is known to experts; only the formulation may be new. **No priority claimed.** |
| [HEURISTIC] | Suggestive but not rigorous. |
| [OPEN] | Not proved by anyone, including us. |
| [CONJECTURAL] | A named conjecture of the literature. |

**Bottom line up front.** No new theorem toward BSD is claimed. The deliverables are:
(1) a fully self-contained, checked proof of the algebraic side of a rank-0 special case
(Fermat's descent for the congruent-number curve), paired with executed analytic verification (§5);
(2) executed numerical verification of the full leading-term formula for ranks 0, 1, 2, 3 and for
curves with #Sha = 4 and 9 (§3.9); and (3) a precise no-go analysis — the **rank-2 wall** — 
identifying the single common mechanism by which every known method fails at rank ≥ 2, together
with a checklist of exactly what any successful attack must construct (§4–§6).

---

## 1. Precise statement

Let \(E/\mathbb{Q}\) be an elliptic curve of conductor \(N\). For each prime \(p\) let
\(a_p = p + 1 - \#\widetilde{E}(\mathbb{F}_p)\) (good reduction), and define the Hasse–Weil L-function

\[
L(E,s) \;=\; \prod_{p \nmid N}\bigl(1 - a_p p^{-s} + p^{1-2s}\bigr)^{-1}\prod_{p \mid N}\bigl(1 - a_p p^{-s}\bigr)^{-1},
\]

convergent for \(\mathrm{Re}(s) > 3/2\). By the modularity theorem (§3.3) \(L(E,s)\) is entire and
\(\Lambda(s) = N^{s/2}(2\pi)^{-s}\Gamma(s)L(E,s)\) satisfies \(\Lambda(s) = w\,\Lambda(2-s)\) with
root number \(w = \pm 1\). Without modularity (or CM), the order of vanishing at \(s = 1\) would not
even be defined; this is why the conjecture only became well-posed for all \(E/\mathbb{Q}\) in 2001.

**BSD I (rank conjecture)** [CONJECTURAL]:

\[
\operatorname{ord}_{s=1} L(E,s) \;=\; \operatorname{rank}_{\mathbb{Z}} E(\mathbb{Q}).
\]

**BSD II (leading-coefficient / "strong" BSD)** [CONJECTURAL]: with \(r = \operatorname{ord}_{s=1}L(E,s)\),

\[
\lim_{s\to 1}\frac{L(E,s)}{(s-1)^r}
\;=\;
\frac{\#\Sha(E/\mathbb{Q}) \cdot \Omega_E \cdot \mathrm{Reg}(E/\mathbb{Q}) \cdot \prod_p c_p}{\bigl(\#E(\mathbb{Q})_{\mathrm{tors}}\bigr)^2},
\]

where:

- \(\Sha(E/\mathbb{Q}) = \ker\bigl(H^1(\mathbb{Q}, E) \to \prod_v H^1(\mathbb{Q}_v, E)\bigr)\) is the
  Tate–Shafarevich group — everywhere-locally-trivial torsors. **The formula presupposes \(\Sha\) is
  finite, which is itself part of the conjecture** (§3.7).
- \(\Omega_E = \int_{E(\mathbb{R})} |\omega|\) for a Néron (global minimal) differential \(\omega\)
  (equal to the real period or twice it, according as \(E(\mathbb{R})\) has one or two components).
- \(\mathrm{Reg}(E/\mathbb{Q}) = \det\bigl(\langle P_i, P_j\rangle\bigr)\) is the Néron–Tate regulator
  on a basis of \(E(\mathbb{Q})/\mathrm{tors}\).
- \(c_p = [E(\mathbb{Q}_p) : E^0(\mathbb{Q}_p)]\) are the Tamagawa numbers (equal to 1 except at bad primes).

**Original 1965 form.** Birch and Swinnerton-Dyer, computing on EDSAC 2 with the CM families
\(y^2 = x^3 - Dx\), conjectured \(\prod_{p\le X} \#\widetilde{E}(\mathbb{F}_p)/p \sim C (\log X)^r\)
[Birch–Swinnerton-Dyer 1965]. Two subtleties, both genuine theorems [PROVED–CITED]: Goldfeld (1982)
showed this product form implies the Riemann hypothesis for \(L(E,s)\), so it is *strictly stronger*
than BSD I; and K. Conrad (2005) showed that if the asymptotic holds, the constant \(C\) differs
from the BSD leading coefficient by a factor of \(\sqrt{2}\). The naive form is thus not equivalent
to the modern form — a cautionary tale about "obvious" reformulations.

**Scope.** The conjecture extends to abelian varieties over global fields (Tate 1966). Over function
fields, dramatically more is known (§3.10). BSD is one of the seven Clay Millennium Prize Problems;
the official problem description is by Wiles.

---

## 2. Best known theorems

The complete list of what is unconditionally known over \(\mathbb{Q}\), in order of logical strength.
All entries [PROVED–CITED]; references in §7.

1. **Modularity** (Wiles, Taylor–Wiles 1995; Breuil–Conrad–Diamond–Taylor 2001). Every
   \(E/\mathbb{Q}\) is modular; \(L(E,s)\) is entire with functional equation. Prerequisite for
   everything below, but *not itself* progress on rank (§3.3).

2. **Rank 0, CM** (Coates–Wiles 1977). If \(E\) has CM and \(L(E,1) \neq 0\), then
   \(E(\mathbb{Q})\) is finite. The first theorem ever linking an L-value to a Mordell–Weil group.

3. **Analytic rank ≤ 1** (Gross–Zagier 1986 + Kolyvagin 1988–90, with nonvanishing input from
   Bump–Friedberg–Hoffstein and Murty–Murty). If \(\operatorname{ord}_{s=1}L(E,s) \le 1\) then
   \(\operatorname{rank} E(\mathbb{Q}) = \operatorname{ord}_{s=1}L(E,s)\) **and** \(\Sha(E/\mathbb{Q})\)
   is finite. *This is the strongest general theorem toward BSD that exists.* It covers no curve of
   analytic rank ≥ 2.

4. **Rank 0 via Euler system in \(K_2\)** (Kato 2004). If \(L(E,1)\ne 0\) then \(E(\mathbb{Q})\) and
   \(\Sha[p^\infty]\) are finite (for good primes) — a second, independent proof of the rank-0 rank
   statement, plus one divisibility of the Iwasawa Main Conjecture.

5. **Iwasawa Main Conjecture** (Skinner–Urban 2014, combined with Kato; supersingular analogues by
   Kobayashi, Pollack, Sprung, Wan). Under standard hypotheses (odd good ordinary \(p\), irreducible
   residual representation, a ramification condition), the full Main Conjecture holds. Corollaries:
   the *p-part of BSD II* in analytic rank 0; and the converse direction
   \(L(E,1)=0 \Rightarrow \operatorname{corank}\, \mathrm{Sel}_{p^\infty} \ge 1\).

6. **p-part of BSD II in rank 1** (W. Zhang 2014; Jetchev–Skinner–Wan 2017), under hypotheses.

7. **Converse theorems** (Skinner 2020; W. Zhang 2014). Under hypotheses: if
   \(\operatorname{corank}\,\mathrm{Sel}_{p^\infty}(E/\mathbb{Q}) = 1\) then
   \(\operatorname{ord}_{s=1}L(E,s) = 1\). So rank 1 + finite \(\Sha[p^\infty]\) forces analytic rank 1.

8. **Parity** (Dokchitser–Dokchitser 2010, building on Nekovář, Kim). Unconditionally for all
   \(E/\mathbb{Q}\): the parity of the \(p^\infty\)-Selmer corank equals the root number. Hence
   **if \(\Sha[p^\infty]\) is finite for one \(p\), BSD I holds mod 2** for that curve.

9. **Statistical BSD** (Bhargava–Shankar 2015; Bhargava–Skinner–Zhang 2014 *[preprint — label
   accordingly]*). The average rank is bounded (< 0.885); a positive proportion of curves have rank 0
   and satisfy BSD I; combining with 3, 5, 7: a majority (> 66%) of all elliptic curves ordered by
   height satisfy BSD I. Alexander Smith's work on \(2^\infty\)-Selmer groups in quadratic twist
   families (arXiv 2017, since revised) pushes this to 100% of twists in suitable families
   *[preprint-based — treat with corresponding care]*.

10. **Exceptional-zero / p-adic BSD input** (Greenberg–Stevens 1993): the Mazur–Tate–Teitelbaum
    derivative formula (§3.6).

11. **Function fields** (Tate 1966; Milne 1975; Kato–Trihan 2003; Ulmer 2002; Yun–Zhang 2017):
    rank ≤ analytic rank *always*; BSD equivalent to finiteness of \(\Sha\) (one prime suffices);
    proven-BSD curves of arbitrarily large rank exist; higher Gross–Zagier for *all* Taylor
    coefficients on moduli of shtukas (§3.10).

**What is *not* on this list, anywhere:** a single theorem giving rank equality, or finiteness of
\(\Sha\), for a general class of curves of rank ≥ 2 over a number field. [OPEN]

---

## 3. Nested specialist findings

*(All ten angles executed by the commander after child launch failed; see execution note at top.)*

### 3.1 (03-01) The precise statement, dissected

Covered in §1. Three load-bearing subtleties found:

- **Well-posedness requires modularity.** Before BCDT 2001, "\(\operatorname{ord}_{s=1}L(E,s)\)" was
  undefined for non-CM curves not known to be modular. BSD as a Clay problem is a statement *about
  the analytic continuation modularity provides*.
- **BSD II presupposes BSD-\(\Sha\).** The leading-coefficient formula quantifies over
  \(\#\Sha\), which is not known to be finite. Strong BSD is really three nested conjectures:
  \(\Sha\) finite; ranks equal; leading coefficient exact.
- **The 1965 product form is *stronger* than the modern form** (Goldfeld 1982: it implies RH for
  \(L(E,s)\); K. Conrad 2005: the constant is off by \(\sqrt2\)). [PROVED–CITED]

### 3.2 (03-02) Coates–Wiles, Gross–Zagier, Kolyvagin: what is actually proved

- **Coates–Wiles (1977)** [PROVED–CITED]: \(E\) with CM by an imaginary quadratic field of class
  number 1; \(L(E,1)\ne 0 \Rightarrow E(\mathbb{Q})\) finite. Method: elliptic units. Does **not**
  prove \(\Sha\) finite. Rubin (1987) later supplied \(\Sha\) finiteness in the CM rank-0 case —
  historically the *first* elliptic curves with provably finite \(\Sha\).
- **Gross–Zagier (1986)** [PROVED–CITED]: for \(K\) imaginary quadratic satisfying the Heegner
  hypothesis, the Heegner point \(P_K \in E(K)\) satisfies
  \(\widehat{h}(P_K) = c(E,K)\, L'(E/K,1)\) with an explicit nonzero constant. Corollaries:
  analytic rank 1 over \(K\) ⟹ \(P_K\) non-torsion ⟹ rank ≥ 1; and (with Goldfeld's theorem and
  the rank-3 curve 5077a1) the first effective lower bounds for class numbers of imaginary
  quadratic fields.
- **Kolyvagin (1988–90)** [PROVED–CITED]: if \(P_K\) is non-torsion, then
  \(\operatorname{rank} E(K) = 1\) and \(\Sha(E/K)\) is finite, with explicit annihilators from
  derived Heegner classes. Descent to \(\mathbb{Q}\) uses existence of a good auxiliary \(K\)
  (Bump–Friedberg–Hoffstein; Murty–Murty). Net theorem: item 3 of §2.
- **Modern converses** [PROVED–CITED]: Skinner (2020), W. Zhang (2014): Selmer corank 1 (under
  hypotheses) forces analytic rank 1. So in rank ≤ 1 the analytic and algebraic sides are now
  *bi-directionally* linked.
- **Finding:** every one of these arguments manufactures or consumes **one** distinguished
  cohomology class. None has a second class to offer. This observation is developed into the
  no-go analysis of §4. [SYNTHESIS]

### 3.3 (03-03) Modularity is the bridge, not the destination

[PROVED–CITED] Wiles/Taylor–Wiles (semistable, 1995), BCDT (all \(E/\mathbb{Q}\), 2001): there is a
weight-2 newform \(f\) of level \(N\) with \(L(E,s) = L(f,s)\), and a modular parametrization
\(\varphi: X_0(N) \to E\). What BSD consumes from this:

1. analytic continuation + functional equation (makes BSD well-posed; gives the sign/parity);
2. the parametrization \(\varphi\), the *carrier* of Heegner points (§3.8);
3. the cohomology of modular curves, the *home* of Kato's Euler system (§3.4);
4. congruences between modular forms, the engine of Skinner–Urban (§3.5).

Why modularity is not BSD: it identifies \(L(E,s)\) with an automorphic L-function but says nothing
about \(E(\mathbb{Q})\). Concretely: modularity is invariant under quadratic twist bookkeeping, while
ranks of twists fluctuate wildly; no statement about \(\operatorname{ord}_{s=1}\) follows. For
modular abelian varieties \(A_f\) (Shimura's construction), Kolyvagin–Logachev extended the
rank ≤ 1 machinery; the same wall appears at rank 2. [PROVED–CITED / SYNTHESIS]

### 3.4 (03-04) Euler systems and the missing higher-rank system

An Euler system for a \(p\)-adic Galois representation \(T\) is a norm-compatible family of classes
\(c_F \in H^1(F, T)\) over abelian extensions, with compatibilities twisted by Euler factors; the
Kolyvagin/Rubin machine (Rubin 2000; Mazur–Rubin 2004) converts one into an annihilator of the
Selmer group. Complete inventory of Euler systems with proved arithmetic consequences over number
fields [PROVED–CITED]:

| System | Author(s) | What it bounds | Effective rank regime |
|---|---|---|---|
| Cyclotomic units | (classical), Rubin | ideal class groups | — |
| Elliptic units | Coates–Wiles, Rubin | CM Selmer groups | rank 0 |
| Heegner points | Kolyvagin | \(\mathrm{Sel}(E/K)\) | rank exactly 1 |
| Kato's Beilinson elements | Kato 2004 | \(\mathrm{Sel}(E/\mathbb{Q})\) | rank 0 |
| Beilinson–Flach | Lei–Loeffler–Zerbes, Kings–Loeffler–Zerbes | Rankin–Selberg Selmer | rank 0 analogues |
| Diagonal cycles / triple product | Darmon–Rotger; Bertolini–Seveso–Venerucci | triple-product Selmer | rank 0/1 analogues |
| Bipartite systems (level-raising) | Bertolini–Darmon, Howard | anticyclotomic Selmer | rank ≤ 1 |

**The structural fact** [SYNTHESIS, formalizing Mazur–Rubin]: all of these are Euler systems of
**core rank 1** — the machine's output is governed by a single leading class
\(c_1 \in H^1_f(\mathbb{Q}, T)\). Two exhaustive cases:

- \(c_1 \neq 0\): the derived classes bound the Selmer group by the index of \(c_1\), *forcing*
  corank ≤ 1. The machine cannot certify corank 2 because its own success bounds corank by 1.
- \(c_1 = 0\): (which Gross–Zagier-type formulas *force* whenever analytic rank ≥ 2, since the
  class's "size" is a first derivative that vanishes) — the machine outputs nothing at all.

Mazur–Rubin (Kolyvagin systems) and Perrin-Riou developed the *abstract* theory of rank-\(r\)
Euler/Stark systems, which would do exactly the right thing for rank \(r\). **No construction of a
rank ≥ 2 Euler system linked to derivatives of L-functions is known over any number field.** [OPEN]
The only place a genuine "higher-rank class ↔ higher derivative" theorem exists is over function
fields (Yun–Zhang, §3.10).

### 3.5 (03-05) Iwasawa theory and the Main Conjecture

[PROVED–CITED] Mazur's control theorem (1972) relates \(\mathrm{Sel}(E/\mathbb{Q}_\infty)\) over the
cyclotomic \(\mathbb{Z}_p\)-tower to \(\mathrm{Sel}(E/\mathbb{Q})\). Mazur–Swinnerton-Dyer (1974)
constructed the \(p\)-adic L-function \(L_p(E)\) (good ordinary \(p\)). The **Main Conjecture**:
\(\mathrm{char}_{\Lambda}\bigl(\mathrm{Sel}_{p^\infty}(E/\mathbb{Q}_\infty)^\vee\bigr) = (L_p(E))\).

- Kato (2004): \(\subseteq\)-divisibility (via his Euler system).
- Skinner–Urban (2014): \(\supseteq\)-divisibility (via Eisenstein congruences on U(2,2)), under
  hypotheses (odd good ordinary \(p\), \(\bar\rho\) irreducible, a ramified quotient condition).
- Supersingular \(p\): Kobayashi's ±-Selmer groups (2003), Pollack's ±-L-functions (2003); main
  conjectures by Sprung and X. Wan [PROVED–CITED, stated without detailed hypotheses].
- CM: Rubin (1991), the imaginary-quadratic main conjecture.

Consequences: the exact \(p\)-part of BSD II in analytic rank 0 (Skinner–Urban) and rank 1
(Jetchev–Skinner–Wan 2017), and \(L(E,1)=0 \Rightarrow\) Selmer corank ≥ 1.

**Why the Main Conjecture does not crack rank ≥ 2** [SYNTHESIS]: it is an equality of
*characteristic ideals* — it controls **orders/lengths**, not ranks. To convert "\(L_p\) vanishes to
order ≥ 2 at the trivial character" into "Mordell–Weil rank ≥ 2" requires the \(p\)-adic height
pairing to be nondegenerate (Schneider's conjecture) — **open** — and conversely, extracting
analytic-rank information from algebraic rank ≥ 2 requires nonvanishing of \(p\)-adic regulators,
equally open. Perrin-Riou made this precise: Main Conjecture + nondegenerate \(p\)-adic heights ⟹
\(p\)-adic BSD I. The wall reappears as a *regulator nondegeneracy* problem, not solved by any
Iwasawa-theoretic input. [OPEN]

### 3.6 (03-06) p-adic BSD and exceptional zeros

[PROVED–CITED] Mazur–Tate–Teitelbaum (1986) conjectured the \(p\)-adic analogue:
\(\operatorname{ord}_{s=1} L_p(E,s) = \operatorname{rank} E(\mathbb{Q})\), **except** when \(E\) has
split multiplicative reduction at \(p\): then the interpolation factor \((1 - a_p p^{-1}\cdots)\)
vanishes and \(L_p\) has a forced "exceptional zero", so the conjecture becomes
\(\operatorname{ord} = \operatorname{rank} + 1\) with

\[
L_p'(E,1) \;=\; \mathcal{L}_p(E)\,\cdot\, \frac{L(E,1)}{\Omega_E},
\qquad
\mathcal{L}_p(E) = \frac{\log_p q_E}{\operatorname{ord}_p q_E}
\]

(\(q_E\) the Tate period). **Proved by Greenberg–Stevens (1993)** via Hida families — one of the few
derivative formulas ever proved. \(\mathcal{L}_p(E) \neq 0\) is also a theorem: by
Barré-Sirieix–Diaz–Gramain–Philibert (1996, the \(p\)-adic Mahler–Manin conjecture) \(q_E\) is
transcendental, and the kernel of \(\log_p\) consists of algebraic numbers \(p^n\zeta\); so
\(\log_p q_E \ne 0\). [PROVED–CITED]

Findings: (i) the \(p\)-adic world *can* prove derivative formulas (Greenberg–Stevens) because
deformation in a \(p\)-adic family supplies a second direction to differentiate — an idea with no
archimedean counterpart yet; (ii) the leading-term \(p\)-adic BSD involves Schneider's \(p\)-adic
height, and its nondegeneracy is open (same wall as §3.5); (iii) higher-order exceptional zeros
(two split-multiplicative primes) have proved formulas in restricted cases
(Bertolini–Darmon; Venerucci) — these are derivative formulas of order 2, but for *forced trivial
zeros*, not for rank-2 Mordell–Weil growth; instructive but not a breach of the wall. [SYNTHESIS]

### 3.7 (03-07) Sha: finiteness, Cassels–Tate, and dependence of BSD II

- **Definition and status.** \(\Sha[n]\) is finite for every \(n\) (classical descent); full
  finiteness is known **only** for curves of analytic rank ≤ 1 (Rubin 1987 CM; Kolyvagin 1988–90;
  Kato for \(p^\infty\)-parts). **There is no elliptic curve over \(\mathbb{Q}\) of rank ≥ 2 for
  which \(\Sha\) is known to be finite** (to our knowledge, as of this writing). [OPEN]
- **Cassels–Tate pairing** [PROVED–CITED]: \(\Sha \times \Sha \to \mathbb{Q}/\mathbb{Z}\),
  nondegenerate modulo divisible part; *alternating* for elliptic curves (Cassels 1962), so if
  finite, \(\#\Sha\) is a perfect square. Poonen–Stoll (1999): for Jacobians of higher genus the
  order can be twice a square — the square phenomenon is special, not generic. Our computed
  examples (§3.9) give implied \(\#\Sha = 1, 4, 9\): squares, as demanded. [COMPUTED]
- **Sha can be large**: \(\Sha[3]\) is unbounded over \(\mathbb{Q}\) (Cassels 1964); unboundedness
  is also known for \(\Sha[5], \Sha[7]\) (Fisher 2001) and other small primes by several authors.
- **Dependence of BSD II on Sha**: the formula contains \(\#\Sha\) as a factor, so strong BSD is
  unfalsifiable-in-principle for a given curve until \(\Sha\) is controlled. In practice the
  logic runs *backwards*: one computes every other term to high precision and *defines* the
  "analytic Sha"; verification means showing it is a perfect-square integer and, where the
  Iwasawa machinery applies, proving the \(p\)-parts match (GJPST 2009 and successors carried
  this out for thousands of rank ≤ 1 curves). [PROVED–CITED/COMPUTED]
- **Parity linkage** [PROVED–CITED]: Dokchitser–Dokchitser: \(p^\infty\)-Selmer parity = root
  number, unconditionally. Hence finiteness of \(\Sha[p^\infty]\) alone would already give BSD I
  mod 2 for every curve. The parity half of BSD is "known modulo Sha".

### 3.8 (03-08) Heegner points: the rank-1 engine and its exact point of failure

**The construction** [PROVED–CITED]: a CM point on \(X_0(N)\) attached to an order in an imaginary
quadratic \(K\) satisfying the Heegner hypothesis, pushed to \(E\) via the modular parametrization,
traced to \(E(K)\). Gross–Zagier: \(\widehat h(P_K) \doteq L'(E/K,1)\). Kolyvagin: derived classes
over ring class fields bound Selmer. Executed demonstration [COMPUTED]: Pari's `ellheegner` on the
rank-1 curve 37a1 returned the generator \(P = (0,0)\), \(\widehat h(P) = 0.05111140824\), and
\(L'(E,1) = 0.305999773834\) — the Gross–Zagier ratio checks against
\(\Omega \cdot \widehat h(P) / (\text{explicit constant})\) to 12 digits (see §3.9 table:
implied \(\#\Sha = 1.000000000000\)).

**Why the engine stalls at rank ≥ 2** [SYNTHESIS of proved facts]:

1. If \(\operatorname{ord}_{s=1} L(E/K,s) \ge 2\), Gross–Zagier *itself* forces
   \(\widehat h(P_K) = 0\): the construction provably outputs a torsion point. The tool's success
   formula is its own kill switch.
2. All Heegner points over all ring class fields lie in a Galois-module of rank ≤ 1 per character
   eigenspace; there is no second independent point to be had from the construction.
3. The conjectural rank-2 analogue would relate \(L''(E,1)\) to a **Beilinson–Bloch height of a
   codimension-2 cycle** (e.g. on \(X_0(N)^3\) or a Kuga–Sato variety). Not one instance of such an
   archimedean higher-height formula is proved over a number field. [OPEN]
4. Candidate replacements, honestly assessed: Darmon's Stark–Heegner points (real quadratic,
   \(p\)-adically constructed; globality/rationality conjectural [CONJECTURAL]); Darmon–Rotger
   generalized Kato classes (proved \(p\)-adic formulas in rank-2 *settings*, detecting a
   two-dimensional Selmer space under hypotheses — closest existing approach to "seeing" rank 2,
   but no archimedean L-derivative link); Chow–Heegner points (constructible, but heights again
   tied to first derivatives).

### 3.9 (03-09) Computational BSD — executed this session

All numbers below were computed in this session (Pari/GP 2.15.4; script in
[`verification.gp`](./verification.gp)); they match the Cremona/LMFDB tables. [COMPUTED]

**Leading-term verification across ranks 0–3** (first curve of each rank by conductor):

| Curve | \(N\) | rank\(_{an}\) | rank\(_{alg}\) | \(L^{(r)}(1)/r!\) | \(\Omega\prod c_p/|T|^2\) | Regulator | implied #Sha |
|---|---|---|---|---|---|---|---|
| 32a1 (\(y^2{=}x^3{-}x\)) | 32 | 0 | 0 | 0.655514388573 | 0.655514388573 | 1 | **1.000000000000** |
| 37a1 | 37 | 1 | 1 | 0.305999773834 | 5.98691729246 | 0.051111408240 | **1.000000000000** |
| 389a1 | 389 | 2 | 2 | 0.759316500288 | 4.98042512171 | 0.152460177943 | **1.000000000000** |
| 5077a1 | 5077 | 3 | 3 | 1.731849900120 | 4.15168798309 | 0.417143558758 | **1.000000000000** |

**Nontrivial Sha** (rank 0): 571a1 → implied #Sha = 4.000000000000; 681b1 → 9.000000000000.
Perfect squares, as Cassels' pairing requires.

**Congruent-number family** \(y^2 = x^3 - N^2x\): computed rank\(_{an}\) = rank\(_{alg}\) and
implied #Sha = 1.0000000000 for \(N = 1,2,3\) (rank 0, sign +1), \(N=5,6,7\) (rank 1, sign −1),
\(N = 34\) (rank 2, sign +1) — the exact pattern that led Birch and Swinnerton-Dyer to the
conjecture.

**A methodological pitfall worth recording**: the raw output of `ellrank` on the positive-rank
curves generated an index-3 subgroup of the Mordell–Weil group; the unsaturated regulator was
\(9\times\) too large and the implied #Sha came out as \(1/9\). Saturation
(`ellsaturation`) fixed all three curves to #Sha = 1.000000000000. Every numerical BSD
verification in the literature must (and does) handle saturation; the index enters squared, so it
silently mimics a fake non-square Sha. [COMPUTED]

**The provability frontier for analytic ranks** [SYNTHESIS of standard facts]:

- rank\(_{an}\) = 0 or the fact \(L(E,1)=0\): *provable exactly* — \(L(E,1)/\Omega\) is a rational
  number of bounded denominator, computed exactly by modular symbols.
- rank\(_{an}\) = 1: provable — sign −1 forces \(L(1)=0\); \(L'(1)\neq 0\) is a robust numerical
  nonvanishing. \(L'(1) = 0\) (needed for rank 3) is provable via Gross–Zagier: exhibit an auxiliary
  \(K\) with \(L(E^K,1)\ne0\) and a *torsion* Heegner point.
- rank\(_{an}\) = 2, 3: provable for individual curves by combining the above with the functional
  equation (this is exactly how 389a1 and 5077a1 are *proved* to have analytic ranks 2, 3).
- rank\(_{an}\) ≥ 4: **no technique exists to certify \(L''(E,1) = 0\)**. To our knowledge no
  elliptic curve over \(\mathbb{Q}\) is *proven* to have analytic rank ≥ 4 — including the famous
  high-rank record curves (Elkies' rank ≥ 28 curve of 2006; Elkies–Klagsbrun rank ≥ 29, 2024
  [announcements, algebraic-rank lower bounds only]). The verification frontier and the theorem
  frontier break at the *same derivative*, for the same reason (§4). [OPEN]

Tables/infrastructure: Cremona's tables (all \(N \le 500{,}000\)), LMFDB; systematic strong-BSD
verification for rank ≤ 1 curves of small conductor (GJPST 2009, completed at many remaining primes
by later Iwasawa-theoretic work). No numerical discrepancy with BSD II has ever been found.

### 3.10 (03-10) Function fields: where BSD is almost a theorem, and what fails to transfer

Setting: \(K = \mathbb{F}_q(C)\), \(E/K\) non-isotrivial; \(E\) spreads out to an elliptic surface
\(\mathcal{E} \to C\). All [PROVED–CITED]:

1. \(L(E,s)\) is a **polynomial** in \(q^{-s}\) (Grothendieck–Deligne): its zeros are Frobenius
   eigenvalues on \(H^2\) of the surface, and \(\operatorname{ord}_{s=1}L\) is the multiplicity of
   the eigenvalue \(q\). The "order of vanishing" is a *dimension of an eigenspace* — a cohomological
   object. Nothing like this exists over \(\mathbb{Q}\).
2. **Tate's inequality**: \(\operatorname{rank} E(K) \le \operatorname{ord}_{s=1} L(E,s)\),
   *unconditionally*. Over number fields not even this inequality is known in either direction.
3. **Tate, Milne, Kato–Trihan**: BSD (I and II) for \(E/K\) holds **iff** \(\Sha(E/K)\) is finite,
   iff the \(\ell\)-primary part is finite for a *single* prime \(\ell\) (including \(\ell = p\):
   Kato–Trihan 2003). Equivalent (Artin–Tate) to the Tate conjecture for divisors on \(\mathcal{E}\).
4. **Proven high-rank BSD instances exist**: Ulmer (2002) exhibited curves over
   \(\mathbb{F}_p(t)\) of arbitrarily large rank whose surfaces are dominated by Fermat surfaces,
   for which the Tate conjecture is known — so full BSD *holds* with rank as large as you like.
   The "rank ≥ 2 wall" is a number-field phenomenon, not intrinsic to BSD.
5. **Yun–Zhang (2017, 2019)**: higher Gross–Zagier over function fields — the \(r\)-th Taylor
   coefficient of \(L\) equals the self-intersection of the Heegner–Drinfeld cycle on the moduli
   stack of shtukas \(\mathrm{Sht}^r\) with \(r\) legs. **A proved formula for all derivatives.**

**What transfers to \(\mathbb{Q}\)** [SYNTHESIS]: the equivalences "\(\Sha\) finite ⟺ BSD"
(philosophically: Sha-finiteness is the whole conjecture); the heuristics for Sha/Selmer
distributions (Poonen–Rains, Bhargava–Kane–Lenstra–Poonen–Rains) which match function-field data;
visibility and descent techniques.

**What does not transfer, and why — the honest core**: every function-field proof runs through a
cohomology theory (étale cohomology of a surface over \(\mathbb{F}_q\)) in which (a) \(L\) is a
characteristic polynomial of an operator, and (b) rational points contribute cycle classes whose
independence is measured by intersection theory. Over \(\mathbb{Q}\), no cohomology theory is known
in which \(L(E,s)\) is a characteristic polynomial ("the missing Weil cohomology of
\(\overline{\mathrm{Spec}\,\mathbb{Z}}\)"); and \(\mathrm{Sht}^r\) uses \(r\) independent copies of
the Frobenius leg, i.e. implicitly the product \(C \times_{\mathbb{F}_q} C\) — while
\(\mathrm{Spec}\,\mathbb{Z}\) has no known nontrivial self-product (the \(\mathbb{F}_1\)-dream of
Connes–Consani et al. is exactly an attempt to build one). [HEURISTIC but precise as a diagnosis]

---

## 4. Candidate breakthrough

Three candidates were pursued. Assessment in decreasing order of ambition, with honest outcomes.

**C-1. A new Euler system / higher-rank class construction.** [NOT ACHIEVED — OPEN]
The inventory of §3.4 is exhaustive as far as we know; we found no new construction. The most
promising known routes (Darmon–Rotger generalized Kato classes; \(p\)-adic deformation à la
Greenberg–Stevens applied to second derivatives; transferring Yun–Zhang through some
\(\mathbb{F}_1\)-formalism) each stall on an identified unproved lemma — respectively: rationality
of the rank-2 class spaces at the archimedean place; a two-variable family with two independent
deformation directions over \(\mathbb{Q}\) (only one, the cyclotomic/weight direction, exists);
and the nonexistence, to date, of \(\mathrm{Spec}\,\mathbb{Z} \times \mathrm{Spec}\,\mathbb{Z}\).
No fake progress claimed.

**C-2. A verified special-case theorem, restated cleanly.** [DELIVERED — classical content,
complete proof included, novelty not claimed.] A fully self-contained proof of the *algebraic* side
of BSD-rank-0 for the congruent-number curve \(y^2 = x^3 - x\) (Fermat's descent, written out and
checked in §5), paired with the executed analytic side (\(L(E,1) = 0.655514\ldots \ne 0\), and the
exact rational \(L(E,1)/\Omega = 1/4\) known by modular symbols). Together with the session
computations across the family \(y^2 = x^3 - N^2 x\) (§3.9), this is a clean, honest, end-to-end
verification of a Gross–Zagier/Kolyvagin-style rank-0 statement in a restricted family — by
elementary means on the algebraic side.

**C-3. A no-go analysis: why rank ≥ 2 is the wall.** [DELIVERED — SYNTHESIS; the strongest
deliverable of this legion.] Formulated as the **One-Class Barrier** below (§5, Claim B), with a
precise checklist of what any successful rank-2 attack must construct. Its evidential base is
threefold and each leg is a proved theorem or executed computation: (i) every known Euler system
has core rank 1, and its output provably self-destructs when analytic rank ≥ 2 (Gross–Zagier forces
the leading class to vanish); (ii) Iwasawa main conjectures control lengths, and conversion to
ranks requires open nondegeneracy of \(p\)-adic heights; (iii) the certification asymmetry — even
*numerically*, no curve can currently be proven to have analytic rank ≥ 4, because the toolkit for
certified vanishing (modular-symbol rationality, parity, Gross–Zagier) stops exactly at first
derivatives. The wall is one wall, seen three times.

**Verdict:** C-3 is the candidate breakthrough of this report, with C-2 as its fully-verified
companion. C-1 remains open, as it does for the mathematical community.

---

## 5. Strongest new claim with argument

### Claim A (fully proved here; classical, novelty explicitly disclaimed)

**Theorem (Fermat).** *There are no positive integers \(x, y, z\) with \(x^4 - y^4 = z^2\).
Consequently the elliptic curve \(E: y^2 = x^3 - x\) has
\(E(\mathbb{Q}) = \{O, (0,0), (1,0), (-1,0)\} \cong (\mathbb{Z}/2)^2\), i.e. rank 0; and since
\(L(E,1) \neq 0\)* [COMPUTED this session: \(0.655514388573\); exact value \(\Omega/4\) by modular
symbols, PROVED–CITED], *BSD I holds for this curve:*
\(\operatorname{ord}_{s=1}L(E,s) = 0 = \operatorname{rank} E(\mathbb{Q})\).

**Proof of the Diophantine statement** (infinite descent; checked line by line). [PROVED–CLASSICAL]

Suppose a solution in positive integers exists; choose one with \(x\) minimal.

*Reduction.* If a prime \(p\) divides \(\gcd(x,y)\), then \(p^4 \mid z^2\), so \(p^2 \mid z\), and
\((x/p, y/p, z/p^2)\) is a smaller solution. So \(\gcd(x,y) = 1\). If \(x\) were even, then \(y, z\)
are odd and \(y^4 + z^2 = x^4 \equiv 0 \pmod{16}\); but \(y^4 \equiv 1 \pmod{16}\) and squares mod 16
lie in \(\{0,1,4,9\}\), so \(z^2 \equiv 15 \pmod{16}\) is impossible. So \(x\) is odd.

From \(y^4 + z^2 = x^4\): \((y^2, z, x^2)\) is a Pythagorean triple; it is primitive since a common
prime of \(y^2\) and \(z\) would divide \(x^4\), contradicting \(\gcd(x,y)=1\). As \(x^2\) is odd,
exactly one of \(y^2, z\) is even. Two cases.

*Case A: \(y\) odd, \(z\) even.* The primitive parametrization gives coprime \(m > n \ge 1\) of
opposite parity with

\[
y^2 = m^2 - n^2, \qquad z = 2mn, \qquad x^2 = m^2 + n^2 .
\]

Multiplying the outer two equations: \((xy)^2 = m^4 - n^4\). Since \(x^2 = m^2 + n^2\) with
\(n \ge 1\), we get \(m < x\). And \(xy \ge 1\). So \((m, n, xy)\) is a solution in positive
integers with strictly smaller first coordinate — contradiction with minimality.

*Case B: \(y\) even, \(z\) odd.* The parametrization gives coprime \(m > n \ge 1\) of opposite
parity with

\[
y^2 = 2mn, \qquad z = m^2 - n^2, \qquad x^2 = m^2 + n^2 .
\]

Now \((m, n, x)\) is itself a primitive Pythagorean triple (with \(x\) odd), so there are coprime
\(p > q \ge 1\) of opposite parity with \(\{m, n\} = \{p^2 - q^2,\; 2pq\}\) and \(x = p^2 + q^2\).
In either assignment, \(y^2 = 2mn = 4pq(p^2 - q^2)\), so

\[
\left(\frac{y}{2}\right)^2 = p\,q\,(p-q)\,(p+q).
\]

The four factors are pairwise coprime: \(\gcd(p,q) = 1\) handles \(\gcd(p,q)\), \(\gcd(p, p \pm q)\),
\(\gcd(q, p \pm q)\); and \(p \pm q\) are both odd (opposite parity) with
\(\gcd(p-q, p+q) \mid 2\), hence \(= 1\). A product of pairwise coprime positive integers that is a
perfect square makes each factor a square:

\[
p = a^2, \quad q = b^2, \quad p + q = c^2, \quad p - q = d^2, \qquad a,b,c,d \ge 1
\ \ (d \ge 1 \text{ since } p \neq q).
\]

Then \(a^4 - b^4 = p^2 - q^2 = (p+q)(p-q) = (cd)^2\): a new solution in positive integers. Its
first coordinate satisfies \(a^2 = p < p^2 + q^2 = x\), so \(a < x\) (as \(a \le a^2 < x\)) —
contradiction with minimality. \(\blacksquare\)

**From the Diophantine statement to the curve.** Let \((x_0, y_0) \in E(\mathbb{Q})\) with
\(y_0 \neq 0\). Set

\[
a = \frac{x_0^2 - 1}{y_0}, \qquad b = \frac{2x_0}{y_0}, \qquad c = \frac{x_0^2 + 1}{y_0}.
\]

Direct check: \(a^2 + b^2 = \dfrac{(x_0^2-1)^2 + 4x_0^2}{y_0^2} = \dfrac{(x_0^2+1)^2}{y_0^2} = c^2\)
and \(\tfrac{1}{2}ab = \dfrac{x_0(x_0^2 - 1)}{y_0^2} = \dfrac{x_0^3 - x_0}{y_0^2} = 1\): a rational
right triangle of area 1. Scale by a common denominator \(D\) to integer legs \(A, B\), hypotenuse
\(C\): then \(A^2 + B^2 = C^2\) with area \(AB/2 = D^2\), a perfect square. Dividing by
\(g = \gcd(A,B,C)\) keeps the area a perfect square (\(g^2\) divides \(D^2\), and \(g \mid D\)), so
assume the triple primitive: \(A = m^2 - n^2\), \(B = 2mn\) (say), area \(= mn(m-n)(m+n) = \square\)
with the four factors pairwise coprime as before; hence \(m = a^2, n = b^2, m+n = c^2, m-n = d^2\)
and \(a^4 - b^4 = (cd)^2\) — contradicting the Theorem. Therefore every rational point on \(E\) has
\(y = 0\) or is \(O\): \(E(\mathbb{Q}) = \{O, (0,0), (\pm 1, 0)\}\), rank 0. \(\blacksquare\)

**Analytic side and full formula for this curve** [COMPUTED + PROVED–CITED]: session computation
gives \(L(E,1) = 0.655514388573 \neq 0\) and implied \(\#\Sha = 1.000000000000\) with
\(\#E(\mathbb{Q})_{\mathrm{tors}} = 4\), \(\prod c_p = 2\) — consistent with the exact rational
\(L(E,1)/\Omega = 1/4\). Full strong BSD for this curve is a *theorem* by combining Rubin's CM
results with explicit small-prime computations (see GJPST 2009 and references therein). The same
elementary method extends to \(N = 2, 3\) (Fermat/Genocchi descents), matching our computed table
(§3.9).

*Honesty statement: Claim A is classical mathematics (Fermat, 17th century; the curve-triangle
dictionary is standard). Its value here is that the proof is complete, checked, and pairs with
executed analytics — a genuine, if modest, verified special case as the mission defines it. It is
also the historical seed: this is the \(N=1\) case of the congruent number problem, the oldest
open-ended consumer of BSD (via Tunnell's theorem, whose converse direction awaits BSD I for the
family \(y^2 = x^3 - N^2x\)).*

### Claim B (the One-Class Barrier — strongest claim of this report)

[SYNTHESIS — a precise organization of proved facts; substance known to experts, no priority
claimed. The *argument* below is complete given the cited theorems.]

**Claim.** Every currently known unconditional method that transfers analytic information
(\(L\)-values and first derivatives) into rank or Sha control over number fields factors through
**exactly one global cohomology class**, and this is a structural, not accidental, limit:

1. *Euler-system leg.* All constructed Euler systems have core rank 1 (§3.4 inventory). The
   Kolyvagin machine applied to a core-rank-1 system either (a) has nonzero leading class, and then
   *its own output bounds Selmer corank by 1* — it can never certify corank 2 — or (b) has
   vanishing leading class, which the Gross–Zagier formula *forces* whenever
   \(\operatorname{ord}_{s=1}L(E/K,s) \geq 2\) (the class's height *is* the first derivative), and
   then the machine returns the empty bound. So in the rank ≥ 2 regime the method is not merely
   weak: it is provably silent.
2. *Iwasawa leg.* Main conjectures (Kato ⊆, Skinner–Urban ⊇) are equalities of characteristic
   ideals: they measure the **size** (length) of Selmer modules, not their **rank** over
   \(\mathbb{Z}_p\), at the point of specialization. The passage from "order of vanishing of
   \(L_p\) ≥ 2" to "corank ≥ 2" requires nondegeneracy of the \(p\)-adic height pairing
   (Schneider's conjecture) — open; the reverse passage requires nonvanishing of \(p\)-adic
   regulators — open. Both open statements are again statements that a certain *pairing built
   from one-variable derivatives* is nondegenerate.
3. *Certification leg (independent evidence).* The complete toolkit for **certified vanishing** of
   analytic data is: exact rationality of \(L(E,1)/\Omega\) (modular symbols), the functional
   equation (parity), and Gross–Zagier (certified vanishing of \(L'\) via a torsion Heegner point).
   These certify analytic ranks 0, 1, 2, 3 for individual curves and **nothing beyond**: there is no
   known way to certify \(L''(E,1) = 0\), and consequently (to our knowledge) no elliptic curve
   over \(\mathbb{Q}\) is proven to have analytic rank ≥ 4. The verification frontier and the
   theorem frontier break at the same derivative because they use the same and only exact formulas
   in existence — all of which are formulas for values and first derivatives.

**Consequence (checklist for any genuine rank-2 attack).** Any proof of BSD I for a family
containing rank-2 curves must construct at least one of:

- (i) a global object whose *proved* archimedean height formula computes \(L''(E,1)\) — a rank-2
  Gross–Zagier: e.g. Beilinson–Bloch heights of codimension-2 cycles on \(X_0(N)^3\)/Kuga–Sato,
  currently lacking even a proved nondegeneracy theory of the relevant height;
- (ii) an Euler system of core rank 2 with a proved link to the L-function (Mazur–Rubin/Perrin-Riou
  formalism is waiting for it; no construction exists);
- (iii) a proved nondegeneracy theorem for \(p\)-adic heights (turning the existing Main
  Conjectures into rank statements); or
- (iv) a number-field avatar of \(\mathrm{Sht}^2\) — a second "leg" for
  \(\mathrm{Spec}\,\mathbb{Z}\), i.e. the \(\mathbb{F}_1\)-product, in which the Yun–Zhang proof
  could be replayed.

Each of (i)–(iv) is a known open problem; the claim's content is that this list is **exhaustive for
all methods currently in existence**, i.e. the wall is one wall. The function-field world (§3.10),
where legs can be multiplied and \(L\) is a characteristic polynomial, proves the wall is an
artifact of our missing cohomology over \(\mathbb{Z}\), not of BSD itself: there, BSD with rank 17
is a theorem (Ulmer). Over \(\mathbb{Q}\), rank 2 is not "slightly harder" than rank 1 — it is the
first case that requires an exact formula for a second derivative, and *no exact formula for a
second derivative of any motivic L-function over a number field has ever been proved, except the
forced-exceptional-zero cases of §3.6.*

*Honesty statement: Claim B is an organizing no-go analysis, not a theorem — it does not prove that
no rank-1-flavored trick can ever reach rank 2, only that every existing method provably cannot,
each for the identified reason. Its accuracy is falsifiable against the literature; we know of no
counterexample to the inventory in §3.4.*

---

## 6. Why this is not full BSD

Explicit accounting of the gap between this report's content and the conjecture:

1. **No new theorem.** Claims A is classical; the numerical verifications are consistency checks at
   finite precision on finitely many curves; Claim B is an analysis of methods, not mathematics
   that moves the frontier. Nothing here proves any new case of BSD I or BSD II.
2. **Rank ≥ 2 is fully open as a general statement.** For *individual* rank-2 and rank-3 curves
   (389a1, 5077a1) analytic rank = algebraic rank is provable and proved; but no theorem covers any
   infinite class of curves of rank ≥ 2, and the mission's target — a Gross–Zagier/Kolyvagin
   analogue — does not exist at rank 2 (Claim B says why).
3. **Sha is the deeper conjecture.** Not a single elliptic curve over \(\mathbb{Q}\) of rank ≥ 2 is
   known to have finite \(\Sha\); consequently BSD II is not proved for even one rank ≥ 2 curve.
   Our "implied #Sha = 1.000000000000" for 389a1/5077a1 is numerology of the highest quality, but
   numerology.
4. **Even rank ≤ 1 is not 100% closed.** The full strong-BSD formula at *every* prime (including
   \(p = 2\) and additive/Eisenstein primes) for *all* rank ≤ 1 curves remains a program
   (Skinner–Urban, Jetchev–Skinner–Wan, W. Zhang, plus curve-by-curve computation), not a finished
   theorem, though it is close and is a plausible near-term completion by the community.
5. **The analytic side cannot even be certified beyond order 3.** Until someone can prove a single
   curve has \(L''(E,1) = 0\) with \(L\) vanishing to order 4, "analytic rank" itself is
   computationally undefined territory at high rank — an underappreciated symptom of the same
   missing mathematics.

---

## 7. References

All references are real publications/preprints to the best of our knowledge; volume/page data are
given only where we have high confidence, and omitted otherwise rather than guessed. Items marked
(*preprint*) were, to our knowledge, not (yet) journal-published in that form.

**Foundational statements**
- B. Birch, H. P. F. Swinnerton-Dyer, *Notes on elliptic curves. II*, J. reine angew. Math. 218 (1965).
- J. Tate, *On the conjectures of Birch and Swinnerton-Dyer and a geometric analog*, Séminaire Bourbaki, exp. 306 (1966).
- A. Wiles, *The Birch and Swinnerton-Dyer conjecture*, Clay Mathematics Institute Millennium Prize problem description.
- D. Goldfeld, *Sur les produits partiels eulériens attachés aux courbes elliptiques*, C. R. Acad. Sci. Paris 294 (1982).
- K. Conrad, *Partial Euler products on the critical line*, Canad. J. Math. 57 (2005).

**Rank ≤ 1 theorems**
- J. Coates, A. Wiles, *On the conjecture of Birch and Swinnerton-Dyer*, Invent. Math. 39 (1977).
- B. Gross, D. Zagier, *Heegner points and derivatives of L-series*, Invent. Math. 84 (1986).
- V. A. Kolyvagin, *Finiteness of E(Q) and Ш(E,Q) for a subclass of Weil curves*, Izv. Akad. Nauk SSSR Ser. Mat. 52 (1988); *Euler systems*, in The Grothendieck Festschrift II, Birkhäuser (1990).
- D. Bump, S. Friedberg, J. Hoffstein, *Nonvanishing theorems for L-functions of modular forms and their derivatives*, Invent. Math. 102 (1990).
- M. R. Murty, V. K. Murty, *Mean values of derivatives of modular L-series*, Ann. of Math. 133 (1991).
- K. Rubin, *Tate–Shafarevich groups and L-functions of elliptic curves with complex multiplication*, Invent. Math. 89 (1987); *The "main conjectures" of Iwasawa theory for imaginary quadratic fields*, Invent. Math. 103 (1991); *Euler Systems*, Annals of Math. Studies 147, Princeton (2000).
- C. Skinner, *A converse to a theorem of Gross, Zagier, and Kolyvagin*, Ann. of Math. 191 (2020).
- W. Zhang, *Selmer groups and the indivisibility of Heegner points*, Camb. J. Math. 2 (2014).
- D. Jetchev, C. Skinner, X. Wan, *The Birch and Swinnerton-Dyer formula for elliptic curves of analytic rank one*, Camb. J. Math. 5 (2017).

**Modularity**
- A. Wiles, *Modular elliptic curves and Fermat's Last Theorem*, Ann. of Math. 141 (1995); R. Taylor, A. Wiles, *Ring-theoretic properties of certain Hecke algebras*, Ann. of Math. 141 (1995).
- C. Breuil, B. Conrad, F. Diamond, R. Taylor, *On the modularity of elliptic curves over Q: wild 3-adic exercises*, J. Amer. Math. Soc. 14 (2001).

**Euler systems and Iwasawa theory**
- K. Kato, *p-adic Hodge theory and values of zeta functions of modular forms*, Astérisque 295 (2004).
- B. Mazur, *Rational points of abelian varieties with values in towers of number fields*, Invent. Math. 18 (1972).
- B. Mazur, H. P. F. Swinnerton-Dyer, *Arithmetic of Weil curves*, Invent. Math. 25 (1974).
- B. Mazur, K. Rubin, *Kolyvagin systems*, Mem. Amer. Math. Soc. 168, no. 799 (2004).
- B. Perrin-Riou, *Systèmes d'Euler p-adiques et théorie d'Iwasawa*, Ann. Inst. Fourier 48 (1998).
- C. Skinner, E. Urban, *The Iwasawa main conjectures for GL(2)*, Invent. Math. 195 (2014).
- S. Kobayashi, *Iwasawa theory for elliptic curves at supersingular primes*, Invent. Math. 152 (2003).
- R. Pollack, *On the p-adic L-function of a modular form at a supersingular prime*, Duke Math. J. 118 (2003).
- (Supersingular main conjectures: work of F. Sprung and of X. Wan — cited by author and topic; precise bibliographic data intentionally omitted.)
- M. Bertolini, H. Darmon, *Iwasawa's main conjecture for elliptic curves over anticyclotomic Z_p-extensions*, Ann. of Math. 162 (2005).
- A. Lei, D. Loeffler, S. Zerbes; G. Kings, D. Loeffler, S. Zerbes — Beilinson–Flach Euler systems (series of papers, 2014–2017; cited by author and topic).
- H. Darmon, V. Rotger, *Diagonal cycles and Euler systems* I, II (Ann. Sci. ÉNS 2014; J. Amer. Math. Soc. 2017).

**p-adic BSD**
- B. Mazur, J. Tate, J. Teitelbaum, *On p-adic analogues of the conjectures of Birch and Swinnerton-Dyer*, Invent. Math. 84 (1986).
- R. Greenberg, G. Stevens, *p-adic L-functions and p-adic periods of modular forms*, Invent. Math. 111 (1993).
- K. Barré-Sirieix, G. Diaz, F. Gramain, G. Philibert, *Une preuve de la conjecture de Mahler–Manin*, Invent. Math. 124 (1996).
- P. Schneider, *p-adic height pairings* I, II, Invent. Math. (1982, 1985).
- H. Darmon, *Integration on H_p × H and arithmetic applications*, Ann. of Math. 154 (2001).

**Sha and parity**
- J. W. S. Cassels, *Arithmetic on curves of genus 1. IV. Proof of the Hauptvermutung*, J. reine angew. Math. 211 (1962); *Arithmetic on curves of genus 1. VI/VIII* (unboundedness of Ш[3], 1964).
- B. Poonen, M. Stoll, *The Cassels–Tate pairing on polarized abelian varieties*, Ann. of Math. 150 (1999).
- T. Fisher, *Some examples of 5 and 7 descent for elliptic curves over Q*, J. Eur. Math. Soc. 3 (2001).
- T. Dokchitser, V. Dokchitser, *On the Birch–Swinnerton-Dyer quotients modulo squares*, Ann. of Math. 172 (2010).
- B. Poonen, E. Rains, *Random maximal isotropic subspaces and Selmer groups*, J. Amer. Math. Soc. 25 (2012).

**Statistics**
- M. Bhargava, A. Shankar, *Binary quartic forms having bounded invariants, and the boundedness of the average rank of elliptic curves*, Ann. of Math. 181 (2015).
- M. Bhargava, C. Skinner, W. Zhang, *A majority of elliptic curves over Q satisfy the Birch and Swinnerton-Dyer conjecture*, arXiv:1407.1826 (*preprint*, 2014).
- A. Smith, *2^∞-Selmer groups, 2^∞-class groups, and Goldfeld's conjecture*, arXiv:1702.02325 (*preprint*, 2017; since revised/split).

**Computation**
- J. Cremona, *Algorithms for Modular Elliptic Curves*, 2nd ed., Cambridge Univ. Press (1997); Cremona database (all conductors ≤ 500000).
- The LMFDB Collaboration, *The L-functions and Modular Forms Database*, https://www.lmfdb.org.
- G. Grigorov, A. Jorza, S. Patrikis, W. Stein, C. Tarniţă, *Computational verification of the Birch and Swinnerton-Dyer conjecture for individual elliptic curves*, Math. Comp. 78 (2009).
- J. Tunnell, *A classical Diophantine problem and modular forms of weight 3/2*, Invent. Math. 72 (1983).
- N. Elkies, rank ≥ 28 curve, NMBRTHRY announcement (2006); N. Elkies, Z. Klagsbrun, rank ≥ 29 curve (announcement, 2024). (*announcements, not refereed papers*)
- PARI/GP version 2.15.4, The PARI Group, Univ. Bordeaux — used for all session computations (`verification.gp`).

**Function fields**
- J. Milne, *On a conjecture of Artin and Tate*, Ann. of Math. 102 (1975).
- K. Kato, F. Trihan, *On the conjectures of Birch and Swinnerton-Dyer in characteristic p > 0*, Invent. Math. 153 (2003).
- D. Ulmer, *Elliptic curves with large rank over function fields*, Ann. of Math. 155 (2002).
- Z. Yun, W. Zhang, *Shtukas and the Taylor expansion of L-functions*, Ann. of Math. 186 (2017); *…(II)*, Ann. of Math. 189 (2019).

---

*Legion 03, end of report. Files: `REPORT.md` (this file), `verification.gp` (executed session
script). No website files were touched.*
