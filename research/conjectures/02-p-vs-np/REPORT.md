# P vs NP — Legion 02

**Commander:** Legion 02 (Claude Fable 5, thinking-xhigh)
**Date:** 2026-08-15
**Scope of write access:** `/workspace/research/conjectures/02-p-vs-np/` only.

**Operational note on the nested specialists.** The mission ordered ten grandchild
specialists (02-01 … 02-10) launched via the Task tool. The Task tool is not present in
this environment (tool inventory checked: no `Task` capability exposed), so the
grandchildren could not be launched. Per the mission fallback clause ("If children cannot
launch, do their work yourself"), the commander executed all ten specialist briefs
directly. Section 3 reports them under their assigned designations.

**Epistemic labels used throughout:**

- **Known** — a published theorem with a citation given in Section 7.
- **Standard** — folklore or textbook material; provable by routine arguments, stated
  in standard references.
- **Heuristic** — an informal argument or community belief; not a theorem.
- **New (unverified)** — a claim formulated here whose proof is not complete.
- **New (proved here)** — a claim formulated here with a complete proof in this memo.
  Where such a claim is elementary and may exist in folklore, this is said explicitly.

No citations are invented. Every item in Section 7 is a real publication or manuscript;
bibliographic details were checked against live sources on 2026-08-15 where feasible.

---

## 1. Precise statement

**Definitions (Standard).** Fix the binary alphabet. A language is a set
L ⊆ {0,1}\*. For a deterministic Turing machine M running in time t(n) on inputs of
length n, write L(M) for the language it decides.

- **P** = the class of languages decidable by a deterministic Turing machine in time
  O(n^k) for some constant k.
- **NP** = the class of languages L for which there exist a polynomial p and a
  polynomial-time decidable relation R ⊆ {0,1}\* × {0,1}\* such that
  x ∈ L ⟺ ∃w, |w| ≤ p(|x|) and R(x, w).
  (Equivalently: nondeterministic polynomial time. The equivalence is Standard.)

**The problem.** Decide whether P = NP.

**Canonical complete problem (Known: Cook 1971; Levin 1973).** SAT — satisfiability of
propositional CNF formulas — is NP-complete under polynomial-time many-one reductions.
Hence P = NP ⟺ SAT ∈ P. Karp (1972) showed 21 natural problems are NP-complete;
thousands are now known.

**Logical form (Standard).** "P ≠ NP" is naturally a Π₂ sentence of arithmetic: for
every polynomial-time machine M and every polynomial bound, there exists an input on
which M errs about SAT. It is well approximated from above by Π₁ sentences such as
"SAT does not have circuits of size n^{log n}" (each such statement is checkable at every
finite length by exhaustive search); this observation is load-bearing in Section 3
(02-09).

**Non-uniform strengthening (Standard).** NP ⊄ P/poly (SAT has no polynomial-size
Boolean circuit family) implies P ≠ NP, since P ⊆ P/poly. Nearly all lower-bound
programs discussed below actually target this stronger, non-uniform statement.

**Millennium formulation.** The Clay Mathematics Institute official problem description
is Cook's "The P versus NP Problem" (2000); the statement above matches it.

---

## 2. Best known theorems

The strongest true theorems that bracket the problem, grouped by direction. All are
**Known** with citations in Section 7.

**Unconditional separations that are provable (and why they don't give P ≠ NP):**

1. **Time hierarchy** (Hartmanis–Stearns 1965): P ⊊ EXP. Combined with NP ⊆ EXP ⊆
   NEXP and the nondeterministic time hierarchy (Cook 1973), at least one of the
   inclusions P ⊆ NP ⊆ PSPACE ⊆ EXP is strict — but we cannot prove which.
2. **Monotone circuits**: CLIQUE requires super-polynomial (indeed exponential)
   monotone circuit size (Razborov 1985; Alon–Boppana 1987). Monotone ≠ general:
   the technique provably does not extend (slice-function argument, Standard).
3. **Bounded depth**: PARITY ∉ AC⁰, with tight exponential bounds
   (Ajtai 1983; Furst–Saxe–Sipser 1984; Håstad 1986). MOD_q ∉ AC⁰[p] for distinct
   primes p, q (Razborov 1987; Smolensky 1987).
4. **ACC⁰ frontier**: NEXP ⊄ ACC⁰ (Williams 2011); improved to NQP ⊄ ACC⁰
   (Murray–Williams 2018), with almost-everywhere and average-case refinements
   (Chen–Lyu–Williams 2020).
5. **General circuits, explicit functions**: the best known size lower bound for an
   explicit function against unrestricted fan-in-2 Boolean circuits is linear, roughly
   3.1n − o(n) (Li–Yang 2022, improving the (3 + 1/86)n bound of
   Find–Golovnev–Hirsch–Kulikov 2016). *This is the true measure of the gap: for
   NP ⊄ P/poly one needs super-polynomial; we have ~3.1n.*
6. **De Morgan formulas**: n^{3−o(1)} for an explicit function
   (Andreev 1987; Håstad 1998; polylog sharpening by Tal 2014), via the shrinkage
   exponent Γ = 2 (Subbotovskaya 1961 initiated this).
7. **Fixed-polynomial non-uniform bounds**: for every k, Σ₂ᵖ ⊄ SIZE(n^k)
   (Kannan 1982); MA/1 ⊄ SIZE(n^k) (Santhanam 2009); MA_EXP ⊄ P/poly
   (Buhrman–Fortnow–Thierauf 1998 — a genuinely non-relativizing separation).
8. **Uniform time–space tradeoffs for SAT**: SAT cannot be solved simultaneously in
   time n^{1.8} and space n^{o(1)} (Fortnow–van Melkebeek 2000; the exponent
   2cos(π/7) ≈ 1.8019 is due to Williams 2008, and Buss–Williams 2012 showed the
   method cannot go beyond it).
9. **Proof complexity separations**: exponential lower bounds for Resolution
   (Haken 1985; Chvátal–Szemerédi 1988), bounded-depth Frege (Ajtai 1988;
   Pitassi–Beame–Impagliazzo 1993; Krajíček–Pudlák–Woods 1995), Cutting Planes
   (Pudlák 1997), Polynomial Calculus (Razborov 1998). Frege, Extended Frege and
   AC⁰[p]-Frege remain without super-polynomial lower bounds.

**Conditional structure theorems (collapses and their contrapositives):**

10. **Karp–Lipton** (1980): NP ⊆ P/poly ⇒ PH = Σ₂ᵖ.
11. **Mahaney** (1982): a sparse NP-complete set (under ≤ₘᵖ) exists ⇒ P = NP.
12. **Ladner** (1975): P ≠ NP ⇒ NP-intermediate problems exist (NP is not a
    dichotomy of P and NP-complete).
13. **Cook–Reckhow** (1979): NP = coNP ⟺ some propositional proof system has
    polynomial-size proofs of all tautologies. Hence super-polynomial lower bounds for
    *every* proof system would give NP ≠ coNP ⇒ P ≠ NP.
14. **Impagliazzo–Wigderson** (1997): E ⊄ SIZE(2^{εn}) i.o. ⇒ P = BPP —
    hardness and randomness are two faces of one question; this is why lower bounds
    and derandomization keep appearing together below.
15. **Williams' algorithmic method** (2010–2013): slightly-faster-than-exhaustive
    Circuit-SAT algorithms for a class C imply NEXP ⊄ C. This converts upper-bound
    progress into lower bounds and produced item 4.

**Barrier theorems (limits on proof techniques):**

16. **Relativization** (Baker–Gill–Solovay 1975): there are oracles A, B with
    Pᴬ = NPᴬ and Pᴮ ≠ NPᴮ.
17. **Natural proofs** (Razborov–Rudich 1997): if pseudorandom functions of
    exponential security exist (as implied by standard cryptographic assumptions),
    then no property of Boolean functions that is *constructive* (poly(2ⁿ)-time in the
    truth table), *large* (accepts a 2^{−O(n)} fraction of functions), and *useful*
    against P/poly exists.
18. **Algebrization** (Aaronson–Wigderson 2009): resolving P vs NP in either
    direction requires techniques that are non-algebrizing (do not persist when oracles
    are replaced by their low-degree extensions); IP = PSPACE-style arithmetization
    algebrizes and hence cannot suffice.
19. **Locality** (Chen–Hirahara–Oliveira–Pich–Rajgopal–Santhanam 2022): the known
    lower-bound techniques relativize with respect to "local" oracles and therefore
    cannot cross the hardness-magnification thresholds that would yield NP ⊄ P/poly.
20. **Metamathematical barriers** (Razborov 1995; Krajíček 1997; Pich–Santhanam 2021;
    Li–Oliveira 2023): strong circuit lower bounds are unprovable in natural fragments
    of bounded arithmetic, unconditionally for some fragments/statements and under
    cryptographic assumptions for others. Details in 02-09.

---

## 3. Nested specialist findings (02-01 … 02-10)

*(All ten briefs executed by the commander; see operational note above.)*

### 02-01 — Relativization (Baker–Gill–Solovay)

**Findings.**

- **Known (BGS 1975), proof sketched here.** (a) Let A be any PSPACE-complete
  language. Then NPᴬ ⊆ NPSPACE = PSPACE ⊆ Pᴬ, so Pᴬ = NPᴬ (= PSPACE).
  (b) For the separation, define L_B = {1ⁿ : ∃x ∈ B with |x| = n} (a unary language).
  Construct B in stages: at stage i, take the i-th polynomial-time oracle machine
  M_i, pick a fresh length n larger than anything queried so far and larger than the
  runtime bound of M_i allows to query exhaustively; run M_i on 1ⁿ answering all new
  queries "no". If M_i accepts, put nothing of length n into B; if it rejects, insert
  some unqueried string of length n (one exists because M_i makes < 2ⁿ queries). Then
  L_B ∈ NPᴮ \ Pᴮ, so Pᴮ ≠ NPᴮ.
- **Consequence (Standard).** Any proof of P = NP or of P ≠ NP must at some point use
  a property of computation that is *not* invariant under attaching an arbitrary
  oracle: pure diagonalization, simulation, and padding all relativize.
- **Known (Arora–Impagliazzo–Vazirani 1992).** Relativizing statements can be
  axiomatized: they are the consequences of "Cobham-style" closure axioms for
  feasible computation. What breaks relativization is *local checkability* — the
  Cook–Levin fact that a computation tableau is verifiable by constant-size local
  windows. Arithmetization (02-03, 02-08) exploits exactly this: it evaluates a
  *specific* low-degree polynomial derived from the transition function, which has no
  meaning for a black-box oracle.
- **Answer to the brief's question ("what must a non-relativizing proof look like?").**
  **Standard synthesis:** it must open the box in at least one of three places:
  (i) the *code* of the machine (local checkability, arithmetization, PCPs);
  (ii) the *completeness structure* of a specific problem (e.g., the
  paddability/self-reducibility of SAT, as in Mahaney-type arguments and in Williams'
  method, which uses tight completeness of specific NEXP problems); or
  (iii) *non-uniform information* (advice, anchored functions as in Section 5).
  Both known post-1990 non-relativizing separations — MA_EXP ⊄ P/poly and
  NEXP ⊄ ACC⁰ — do (i) plus (ii).
- **On the "illusionist" barrier named in the mission brief.** A literature search
  (2026-08-15) finds no complexity-theoretic barrier by this name; the term appears
  only in art history and scenography. **We flag this as non-existent in the
  literature** and treat the fourth-barrier slot as open; Section 4 proposes our own
  candidate formalization (the *certification-access barrier*), which is proved in
  Section 5.

### 02-02 — Natural proofs (Razborov–Rudich) and constructive evasion

**Findings.**

- **Known (Razborov–Rudich 1997).** A property Φ = {Φₙ} of n-variable Boolean
  functions is *natural* if it is constructive (deciding Φₙ(f) from the 2ⁿ-bit truth
  table takes poly(2ⁿ) time) and large (Φₙ holds for ≥ 2^{−O(n)} of all functions);
  it is *useful against P/poly* if Φₙ(f) forces f ∉ SIZE(n^k) for every k (large n).
  Theorem: a natural property useful against P/poly breaks pseudorandom function
  families of exponential security (e.g., the factoring/DDH-based PRFs of
  Goldreich–Goldwasser–Micali 1986 and Naor–Reingold 2004). Since such PRFs are widely
  believed to exist, no natural proof shows NP ⊄ P/poly. Essentially all pre-1994
  lower-bound techniques (random restrictions, approximation by polynomials) are
  naturalizable — this is why they stop at AC⁰[p].
- **Known (Williams 2016).** Dropping *largeness* is not merely permitted but
  forced and sufficient: NEXP ⊄ P/poly holds **iff** there is a constructive (not
  necessarily large) property useful against P/poly. So the barrier is precisely about
  the conjunction largeness ∧ constructivity.
- **Known (Carmosino–Impagliazzo–Kabanets–Kolokolova 2016).** Natural properties can
  be *used positively*: any natural property useful against AC⁰[p] yields quasipolynomial-time
  learning algorithms for AC⁰[p] — the barrier is constructive enough to be an
  algorithm factory. This is the cleanest evidence that "naturalness" is a real
  computational resource, not an artifact.
- **Known (Oliveira–Santhanam 2018; McKay–Murray–Williams 2019; CHOPRS 2022).**
  *Hardness magnification*: for certain meta-computational problems (e.g., MCSP with
  size parameter 2^{√n}), lower bounds barely above trivial (n^{1+ε} formula size)
  already imply NP ⊄ NC¹ or stronger. Magnification theorems themselves are
  non-natural in a formal sense, but the *locality barrier* (CHOPRS 2022) shows the
  currently known techniques for the required weak bounds relativize with respect to
  local oracles and therefore cannot cross the threshold. The frontier is genuinely
  open, not merely psychologically.
- **Assessment (Heuristic).** The constructive evasion the brief asks for exists in
  three known flavors: non-largeness (Williams), meta-problems + magnification
  (OS/MMW), and anti-checkability of the anchor (Section 5, Theorem B, proved here:
  useful properties with O(1) *randomized* truth-table probes exist unconditionally,
  but their anchor function is exactly as non-explicit as the lower bound being
  sought). All three relocate the difficulty to the same place: *explicitness*.

### 02-03 — Algebrization (Aaronson–Wigderson)

**Findings.**

- **Known (Aaronson–Wigderson 2009).** For an oracle A, let Ã denote a low-degree
  polynomial extension of A over a field or ring. An inclusion C ⊆ D *algebrizes* if
  Cᴬ ⊆ D^{Ã} for all A and all extensions Ã; a separation C ⊄ D algebrizes if
  C^{Ã} ⊄ Dᴬ for all A, Ã. Results: (i) IP = PSPACE and MIP = NEXP algebrize —
  arithmetization survives the jump from A to Ã; (ii) **P vs NP does not algebrize in
  either direction**: there exist algebraic oracles making the classes equal and
  algebraic oracles keeping them apart, so any resolution needs non-algebrizing
  techniques. Likewise NP ⊄ P/poly and even NP ⊆ P/poly need non-algebrizing
  techniques.
- **Known (Impagliazzo–Kabanets–Kolokolova 2009).** An axiomatic reformulation:
  algebrizing statements are exactly those provable from the AIV-style axioms plus
  "arithmetic checkability"; this locates arithmetization as one axiom beyond
  relativization, and P vs NP as independent of the extended axiom set.
- **Known (Aydınlıoğlu–Bach 2018).** *Affine relativization* unifies the two barriers
  into a single oracle notion under which exactly the known arithmetization-based
  results relativize; this is the sharpest published formalization of "the
  IP = PSPACE toolkit cannot do it".
- **Assessment (Standard).** Williams' NEXP ⊄ ACC⁰ evades algebrization: its
  ingredients (nondeterministic time hierarchy with advice, tight completeness of
  succinct problems, and a *non-black-box* ACC⁰-SAT algorithm exploiting the
  structure of ACC⁰ circuits) are not available relative to algebraic oracles. The
  lesson for a P vs NP attack: interaction with algebraic oracles shows that
  *algebraic simulation of the verifier* is not enough; one must exploit algebraic
  structure of the *computed function itself* (as GCT attempts, 02-06) or algorithmic
  structure of the *circuit class* (as the algorithmic method does, 02-04).

### 02-04 — Circuit lower bounds: AC⁰ → ACC⁰ → formulas → the gap to NP

**Findings.** (All Known unless marked.)

- **AC⁰**: PARITY requires depth-d circuits of size 2^{Ω(n^{1/(d−1)})} (Håstad 1986,
  after Ajtai; FSS). Tight. Technique: switching lemma = random restrictions;
  naturalizable.
- **AC⁰[p]**: Razborov 1987 / Smolensky 1987 — approximation by low-degree
  polynomials over F_p; exp(Ω(n^{1/2d})) bounds for MOD_q. Naturalizable. AC⁰[m] for
  composite m (i.e., ACC⁰'s base case) has resisted all polynomial-method attacks for
  35+ years.
- **ACC⁰**: NEXP ⊄ ACC⁰ (Williams 2011) via: (a) generic connection — a
  2ⁿ/n^{ω(1)}-time Circuit-SAT algorithm for C implies NEXP ⊄ C (Williams 2010,
  using easy-witness lemmas of Impagliazzo–Kabanets–Wigderson 2002); (b) a
  non-trivial ACC⁰-SAT algorithm via the Yao–Beigel–Tarui transform to SYM⁺ form.
  Improvements: NQP = NTIME(n^{polylog n}) ⊄ ACC⁰ (Murray–Williams 2018);
  almost-everywhere and average-case versions (Chen–Lyu–Williams 2020). This is the
  only known *scalable* route past both natural proofs (it produces non-large
  properties) and relativization/algebrization (it uses completeness + circuit
  structure).
- **General circuits**: ~3.1n − o(n) for an explicit function (Li–Yang 2022;
  previously (3+1/86)n by FGHK 2016). Gate elimination is the only technique and is
  provably stuck at O(n) by known formalizations (Heuristic consensus, partially
  formalized in the "bottleneck" literature).
- **Formulas**: n^{3−o(1)} (Andreev/Håstad/Tal). The Karchmer–Raz–Wigderson
  composition program targets P ⊄ NC¹ via communication complexity of relations;
  partial composition theorems exist (Known: KRW 1995 and successors) but the full
  conjecture is open.
- **The gap to NP, quantified (Standard).** NP ⊄ P/poly requires super-polynomial
  size for SAT. Current record for *any* explicit function: 3.1n. For SAT
  specifically, nothing better than the generic record plus the uniform time–space
  tradeoffs (n^{1.8} time at n^{o(1)} space). The honest summary: after 50 years the
  non-uniform gap is [3.1n, superpoly] and it has moved by ~0.1n since 2016 — except
  in restricted classes, where the algorithmic method keeps producing genuinely new
  separations (NQP vs ACC⁰).

### 02-05 — Proof complexity

**Findings.**

- **Known (Cook–Reckhow 1979).** A proof system is a poly-time surjection from
  strings ("proofs") onto TAUT. NP = coNP iff some system is polynomially bounded.
  Hence the *Cook–Reckhow program*: prove super-polynomial lower bounds for ever
  stronger systems; success for all systems gives NP ≠ coNP ⇒ P ≠ NP.
- **Proposition (Standard; proof included for self-containedness).** If P = NP then
  a polynomially bounded proof system exists. *Proof.* P = NP gives NP = coNP
  (complement both sides: coNP = coP = P = NP). TAUT is coNP-complete, so TAUT ∈ NP:
  there is a poly-time verifier V and polynomial p with φ ∈ TAUT ⟺ ∃w, |w| ≤ p(|φ|),
  V(φ, w) = 1. The map (φ, w) ↦ φ when V accepts (and ↦ some fixed tautology
  otherwise) is a Cook–Reckhow proof system in which every tautology has a
  polynomial-size proof. ∎ (Contrapositive: super-polynomial lower bounds for *all*
  proof systems ⇒ P ≠ NP.)
- **Known lower-bound ladder.** Resolution: exponential (Haken 1985 for PHP;
  Chvátal–Szemerédi 1988 for random k-CNF). Bounded-depth Frege: exponential for PHP
  (Ajtai 1988, quasipolynomial-size unprovability; exponential by
  Pitassi–Beame–Impagliazzo 1993 and Krajíček–Pudlák–Woods 1995). Cutting Planes:
  exponential via feasible interpolation + monotone circuit lower bounds
  (Pudlák 1997). Polynomial Calculus / Nullstellensatz: degree and size lower bounds
  (Razborov 1998; Impagliazzo–Pudlák–Sgall 1999). Sum-of-squares: degree lower bounds
  (Grigoriev 2001; Schoenebeck 2008). Ideal Proof System (IPS,
  Grochow–Pitassi 2018): lower bounds only for restricted subsystems
  (Forbes–Shpilka–Tzameret–Wigderson 2021).
- **Open frontier (Standard).** AC⁰[p]-Frege: no super-polynomial lower bounds — the
  proof-complexity mirror of the ACC⁰ situation. Frege and Extended Frege: nothing
  super-polynomial; EF lower bounds are morally equivalent to circuit lower bounds
  (EF is to P/poly as Frege is to NC¹, Standard analogy made precise in bounded
  arithmetic).
- **Known obstructions inside the program.** Feasible interpolation — the engine of
  the CP lower bound — *fails* for Frege and TC⁰-Frege under cryptographic
  assumptions (Krajíček–Pudlák 1998, RSA; Bonet–Pitassi–Raz 2000, Diffie–Hellman).
  Automating Resolution is NP-hard (Atserias–Müller 2020), and likewise for algebraic
  systems (de Rezende–Göös–Nordström–Pitassi–Robere–Sokolov 2021): even *using* weak
  systems optimally is intractable. Proof-complexity generators (Krajíček 2024
  monograph; Razborov 2015) are the current candidate hard tautologies for Frege/EF.
- **Relation to NP ⊄ P/poly (Standard).** Circuit lower bounds and proof-size lower
  bounds are formally linked through bounded arithmetic (02-09): proving
  "SAT ∉ SIZE(n^k)" *feasibly* would yield EF proofs of the corresponding
  propositional translations; conversely EF lower bounds for those translations
  formalize "circuit lower bounds are hard to prove". The two open problems guard
  each other.

### 02-06 — Geometric complexity theory and permanent vs determinant

**Findings.**

- **Setup (Known: Valiant 1979).** perm_m is VNP-complete; det_n is complete for
  VP_ws (skew circuits / algebraic branching programs). The *determinantal
  complexity* dc(perm_m) is the least n such that perm_m is an affine projection of
  det_n. Valiant's conjecture (VP_ws ≠ VNP): dc(perm_m) grows super-polynomially.
- **Known bounds.** Upper: dc(perm_m) ≤ 2^m − 1 (Grenet 2011). Lower:
  dc(perm_m) ≥ m²/2 (Mignon–Ressayre 2004, char 0) — quadratic, unimproved in
  substance for two decades.
- **Known (Mulmuley–Sohoni 2001, 2008).** GCT strengthens Valiant's conjecture to:
  the padded permanent's GL_{n²}(ℂ)-orbit closure is not contained in the determinant's
  orbit closure; proposes to separate the coordinate rings by representation-theoretic
  *obstructions* — irreducible GL_{n²}-modules occurring in one ring but not the other.
- **Known no-go (Ikenmeyer–Panova 2017; Bürgisser–Ikenmeyer–Panova 2019, JAMS).**
  *Occurrence obstructions cannot work*: for n ≫ m^{25}-type regimes, every irreducible
  occurring in the permanent side also occurs on the determinant side. The proof
  exploits the padding. This kills the simplest version of GCT but **not**
  *multiplicity obstructions* (comparing multiplicities rather than occurrence).
- **Known positive data point (Dörfler–Ikenmeyer–Panova 2019).** There is a natural
  setting (Chow variety vs bounded border Waring rank) where multiplicity obstructions
  provably separate while occurrence obstructions provably cannot — so the surviving
  GCT weapon is not vacuous.
- **Assessment (Heuristic).** GCT is the only program that is *aimed at* non-natural
  properties by design (representation-theoretic positivity is not obviously large or
  constructive), but after 25 years it has produced no lower bound for perm vs det
  beyond quadratic, and its combinatorial core (Kronecker/plethysm positivity) is
  itself #P-hard territory. Status: alive only through multiplicity obstructions;
  padding should be avoided (iterated matrix multiplication variants); no known
  route from VP_ws ≠ VNP to P ≠ NP without further (believed but unproven)
  transfer principles — the algebraic and Boolean worlds are connected only by
  conditional bridges (Bürgisser 2000).

### 02-07 — Fine-grained complexity as miniature P vs NP

**Findings.**

- **Known (Impagliazzo–Paturi 2001; Impagliazzo–Paturi–Zane 2001).** ETH: 3-SAT
  requires 2^{εn} time for some ε > 0. SETH: for every δ < 1 there is k with k-SAT
  ∉ DTIME(2^{δn}). The sparsification lemma makes these robust under reductions.
- **Known reduction web.** SETH ⇒ Orthogonal Vectors requires n^{2−o(1)}
  (Williams 2005); OV ⇒ quadratic hardness for Edit Distance (Backurs–Indyk 2015),
  Fréchet distance (Bringmann 2014), LCS (Abboud–Backurs–Vassilevska Williams 2015).
  APSP-equivalence class (Vassilevska Williams–Williams 2010). 3SUM-hardness in
  computational geometry (Gajentaan–Overmars 1995; Pătraşcu 2010 for offline variants).
- **What transfers to P vs NP (Standard/Known).**
  1. *Trivially*: SETH ⇒ ETH ⇒ P ≠ NP. (For fixed k, a k-CNF on n variables has
     poly(n) size, so SAT ∈ P would give 2^{o(n)} k-SAT.) The converse fails in both
     steps as far as we know; refuting SETH would say nothing about P vs NP.
  2. *The algorithmic method is the real transfer*: fine-grained **upper** bounds
     imply lower bounds. Beyond Williams' Circuit-SAT connection, refuting NSETH
     (its nondeterministic extension) implies E^{NP} circuit lower bounds
     (Carmosino–Gao–Impagliazzo–Mihajlin–Paturi–Schneider 2016) — so even *failed*
     fine-grained conjectures pay off in the P vs NP direction.
  3. *Miniature sociology transfers too* (Heuristic): completeness phenomena,
     intermediate problems, and barrier-like results (e.g., limits of deterministic
     reductions to OV under NSETH) all have small-scale analogues.
- **What does not transfer (Standard).** Fine-grained hardness is calibrated to the
  *hardest known* algorithmic phenomena (k-SAT savings → 0 as k → ∞, 02-10), not to a
  complete problem for a class; there is no NP-completeness-like maximality, so a
  single algorithmic surprise (as happened for APSP-related problems via the
  polynomial method, Williams 2014) can restructure the landscape without any
  class collapse.

### 02-08 — Interactive proofs: IP = PSPACE, MIP\*, and why they don't resolve P vs NP

**Findings.**

- **Known.** coNP ⊆ IP and indeed P^{#P} ⊆ IP via sumcheck
  (Lund–Fortnow–Karloff–Nisan 1992); IP = PSPACE (Shamir 1992). MIP = NEXP
  (Babai–Fortnow–Lund 1991), the parent of the PCP theorem
  (Arora–Safra 1998; Arora–Lund–Motwani–Sudan–Szegedy 1998; Dinur 2007).
  MIP\* = RE (Ji–Natarajan–Vidick–Wright–Yuen 2020): with entangled provers,
  interactive verification captures the halting problem; corollaries refute Connes'
  embedding conjecture and resolve Tsirelson's problem.
- **Known (Fortnow–Sipser 1988).** There is an oracle A with coNPᴬ ⊄ IPᴬ: IP = PSPACE
  is non-relativizing — historically the first hard evidence that BGS is evadable.
- **Known (Aaronson–Wigderson 2009).** But the entire arithmetization toolkit
  *algebrizes*: IP = PSPACE holds relative to (A, Ã) pairs, and P vs NP is
  independent of algebrizing techniques. So the one family of non-relativizing tools
  we fully understand is provably insufficient.
- **Why no resolution follows (Standard).** These theorems characterize *verification
  power with randomness and interaction*, i.e., they move the goalposts of what a
  verifier can check — they never produce a deterministic decision procedure (which
  would need P-side collapses) nor a lower bound against P (which would need
  circuit-style hardness). Their P vs NP dividends are indirect and real:
  MA_EXP ⊄ P/poly (BFT 1998), the PCP-based hardness-of-approximation theory (an
  entire "approximate P vs NP" that is *resolved* modulo P ≠ NP), and the
  derandomization–hardness equivalences.
- **Assessment (Heuristic).** MIP\* = RE is a warning about intuition portability: an
  interactive class jumped from NEXP-scale to undecidable by changing the physical
  model of the provers. Nothing analogous can happen for P vs NP itself (both classes
  are model-robust by the strong Church–Turing thesis for polynomial time), which is
  precisely why it is harder.

### 02-09 — Meta-mathematics: independence and unprovability

**Findings.** This is the area where the mission's "sharpened barrier" request has the
most solid recent theorems.

- **What is NOT known (Standard, important).** P vs NP is *not* known to be
  independent of PA, of ZFC, or even of Buss's S¹₂ / Cook's PV. No unconditional
  independence from any theory containing basic arithmetic of feasible reasoning is
  known for the statement itself.
- **Known (Hartmanis–Hopcroft 1976).** There is a recursive oracle A such that
  "Pᴬ = NPᴬ" (for a fixed formalization) is independent of ZFC. Relativized
  independence only; it says nothing about the unrelativized question.
- **Known (Kurtz–O'Donnell–Royer 1987?; Ben-David–Halevi 1991; exposition
  Aaronson 2003).** P ≠ NP is Π₂ but is squeezed by Π₁ approximations
  ("SAT ∉ SIZE(n^{log n})"). Consequences: (i) a Π₁ strengthening cannot be
  independent of a Σ₁-sound theory unless true; (ii) if P ≠ NP were independent of
  PA + (all true Π₁ sentences) — the setting where all non-Gödelian independence
  techniques live — then NP would have deterministic algorithms of running time
  n^{α(n)} for an extremely slowly growing α: "independence of P vs NP by current
  methods" would itself imply a near-collapse. This is the sharpest classical no-go
  for independence dreams.
- **Known (Razborov 1995).** If PRGs secure against 2^{n^ε}-size circuits exist, then
  S²₂(α) cannot prove super-polynomial circuit lower bounds for explicit Boolean
  functions (and S¹₂(α) under a weaker assumption). The natural-proofs barrier,
  recast as conditional unprovability in bounded arithmetic.
- **Known (Krajíček–Oliveira 2017).** *Unconditional*: PV does not prove
  P ⊆ SIZE(n^k) for any fixed k — i.e., fixed-polynomial circuit *upper* bounds on P
  are unprovable; equivalently, the corresponding lower bounds are consistent with PV.
  (Model-theoretic strengthening: Bydžovský–Müller 2020.)
- **Known (Pich–Santhanam 2021).** *Unconditional*: PV cannot prove strong
  average-case lower bounds for fixed NP machines against co-nondeterministic
  2^{n^{o(1)}}-size circuits. (Via Krajíček's proof-complexity-generator technique.)
- **Known (Li–Oliveira 2023).** *Unconditional* unprovability of strong complexity
  lower bounds in the theories T^i_PV — the strongest sound theories with
  ∀Σᵇ_{i−1} axioms over the PV language cannot strongly separate the corresponding
  levels of PH.
- **Known (Atserias–Buss–Müller 2023).** NEXP ⊆ P/poly is unprovable in V⁰₂;
  equivalently NEXP ⊄ P/poly is consistent with V⁰₂ — a consistency result for a
  *strong* second-order bounded theory, by simulating comprehension rather than
  witnessing.
- **Known (Cook–Krajíček 2007).** Conditional consequences of PV proving
  NP ⊆ P/poly: feasibly provable collapses; the provability of upper bounds is as
  constrained as that of lower bounds.
- **Synthesis (Standard + Heuristic).** The proved pattern is: *feasible theories
  cannot verify strong lower bounds (partly unconditionally), and cannot verify strong
  upper bounds either (unconditionally in key cases)*. This is a genuine two-sided
  barrier for "self-aware" mathematics — complexity theory formalized inside feasible
  reasoning cannot settle its own central question. But none of this touches full PA,
  let alone ZFC: the honest answer to "is P vs NP independent of PA?" is **unknown,
  with structural evidence (Ben-David–Halevi) that independence-by-known-techniques
  would itself have dramatic algorithmic consequences.**

### 02-10 — Upper bounds that "almost" put NP in P, and why they stall

**Findings.** (Numbers verified against the journal literature on 2026-08-15.)

- **Known ladder for 3-SAT** (randomized, 2^{cn} with shrinking c):
  Monien–Speckenmeyer 1985 (first < 2ⁿ branching); PPZ 1997/1999 (2^{n−n/k} for
  k-SAT); Schöning 1999 (random walk, (4/3)ⁿ for 3-SAT); PPSZ 2005 (unique 3-SAT
  O(1.3071ⁿ)); Hertli 2011 (PPSZ bound holds for general 3-SAT, removing the
  unique-solution caveat); biased-PPSZ (Hansen–Kaplan–Zamir–Zwick 2019,
  O(1.306995ⁿ)); Scheder 2021/2024 ("PPSZ is better than you think",
  O(1.306973ⁿ) for Unique-3-SAT via re-analysis of unmodified PPSZ; lifts to general
  3-SAT via the lifting framework of Scheder–Steinberger/Scheder 2024).
  Deterministic: full derandomization of Schöning (Moser–Scheder 2011).
- **Known scaling.** For k-SAT all known algorithms have savings Θ(1/k):
  PPZ saves 1/k, PPSZ saves ~π²/6 · 1/k as k → ∞. SETH is exactly the assertion that
  savings must vanish as k → ∞. "Super Strong ETH" is known to hold *for PPSZ-type
  algorithms*: PPSZ with small resolution width cannot beat 2^{n(1−O(1/k))}
  (Scheder–Talebanfard 2020; PPSZ lower bounds: Chen–Scheder–Talebanfard–Tang 2013).
  For general CNF with m clauses the record savings are 1/O(log(m/n))
  (Schuler 2005; Calabro–Impagliazzo–Paturi 2006).
- **Known (Valiant–Vazirani 1986).** Unique-SAT is not an easier target in the
  decisive sense: a polynomial-time algorithm for Unique-SAT gives NP = RP. And
  Hertli's theorem shows the unique case is not where PPSZ's bottleneck lies anyway.
- **Why they stall (Standard synthesis).**
  1. Every known technique (branching/DPLL, local search, random restriction,
     polynomial method, inclusion–exclusion) extracts advantage from *local
     structure* — short clauses, low density, small width — and the advantage decays
     exactly as locality decays (1/k). No technique engages global structure of the
     solution space; random k-SAT near threshold, where the solution-space geometry
     shatters (Heuristic, from statistical physics), is the empirical hard core.
  2. **The stall is not an accident but a theorem-schema (Known, Williams 2010–13):**
     improving Circuit-SAT beyond exhaustive search by n^{ω(1)} factors *implies*
     NEXP circuit lower bounds. The upper-bound program and the lower-bound program
     are the same program. Every percentage point of savings that generalizes beyond
     CNF is paid for in lower-bound currency — which is why the constants freeze at
     the fourth decimal: 1.306973 is where the locality budget of current mathematics
     currently runs out.

---

## 4. Candidate breakthrough (NEW / REFORMULATION / SPECIAL CASE / NO-GO)

**Classification: REFORMULATION + NO-GO, with two small theorems proved in full
(Section 5). No claim of progress on the truth of P vs NP itself.**

**The certification-access barrier.** The mission brief lists a fourth barrier
("illusionist") alongside relativization, natural proofs, and algebrization. As
established in 02-01, no such barrier exists in the literature under that name. We
therefore propose and *prove* a candidate fourth-slot formalization, at the
information-access level rather than the computational level:

> Model every "lower-bound technique that works through a property of Boolean
> functions" as a **hardness test**: a procedure that probes the truth table of
> f: {0,1}ⁿ → {0,1} at q(n) (adaptively chosen) positions, is otherwise
> computationally unbounded, and must accept only functions of circuit size > s(n)
> (soundness/usefulness), accepting at least one function (nontriviality).

The two theorems of Section 5 then pin down the access complexity of hardness
certification exactly:

- **Theorem A (deterministic no-go, unconditional).** Deterministic hardness tests
  need q > s/(3n) probes. Certifying super-polynomial hardness deterministically
  requires reading super-polynomially many truth-table bits; certifying 2^{Ω(n)}
  hardness requires reading a 1/poly(n) fraction of the entire table. *Hardness is
  maximally non-spot-checkable.*
- **Theorem B (randomized evasion, unconditional).** With randomness, **O(1)** probes
  suffice: there is a (non-explicit, non-large) randomized test with 500 queries that
  is sound against SIZE(2^{n/4}) and accepts a nonempty set.

**Why this is a sharpened barrier statement.** Combining A, B, and Razborov–Rudich
gives a three-tier access/constructivity landscape, each tier with a different
epistemic status:

| access to truth table | computation | verdict | status |
|---|---|---|---|
| deterministic, ≤ s/3n bits | unbounded | impossible | **unconditional (Thm A, proved here)** |
| randomized, O(1) bits | unbounded, non-uniform anchor | possible but inherently non-explicit and non-large | **unconditional (Thm B, proved here)** |
| full table (2ⁿ bits) | poly(2ⁿ), large property | impossible | **conditional on PRFs (Razborov–Rudich, Known)** |

The reformulation content: *the natural-proofs barrier is purely about computation and
largeness, not about information* — information-theoretically, hardness certification
is either impossible (deterministic, sublinear access) or trivially cheap (randomized)
— and the cheap certificates are exactly as non-explicit as the hard functions they
certify. Every viable lower-bound program must therefore live in the remaining cell:
full (or near-full) access, computationally bounded, **non-large or non-constructive**
properties. This is consistent with — and gives an elementary information-level
explanation for — where the surviving programs actually operate: Williams' method
(non-large properties via completeness), GCT (aiming at non-constructive
representation-theoretic properties), magnification (properties of meta-computational
problems), and proof-complexity generators.

**Honest novelty assessment.** Theorems A and B are elementary (transcript + lookup
table; counting + Hoeffding). We searched for the precise statements and did not find
them in print; they are folklore-adjacent, and thematically related to (but much more
elementary than, and incomparable with) the locality barrier of CHOPRS 2022, which
concerns oracle-locality of proofs rather than truth-table access of properties. We
label them **New (proved here; possibly folklore)** and make no priority claim.

**Rejected candidates for this section (recorded for honesty).** (i) A "new conditional
collapse": everything we could actually prove was a composition of Karp–Lipton /
Mahaney / Valiant–Vazirani-type statements — Known, no new content. (ii) A "cleaner
complete problem": MCSP and its variants (Hirahara 2018, 2022) already play this role
in the literature; we found no genuinely cleaner reduction. (iii) Anything claiming to
weaken SETH-to-P≠NP transfer: nothing beyond 02-07's known statements survived
scrutiny.

---

## 5. Strongest new claim with a real argument

**Setting.** Fix n. A *deterministic q-query hardness test* is a decision tree Tₙ of
depth ≤ q over the 2ⁿ coordinates of the truth table of f : {0,1}ⁿ → {0,1}: it
adaptively selects points x₁, x₂, … (each depending on the answers so far), reads
f(x₁), f(x₂), …, and outputs accept/reject. No computational bound is placed on the
selection or the decision. Circuits are over {∧, ∨, ¬} with fan-in 2; SIZE(s) is the
set of functions computed by circuits with ≤ s gates. Tₙ is *useful against SIZE(s)*
if every accepted f has circuit size > s; it is *nontrivial* if it accepts at least
one function.

### Theorem A — deterministic access barrier. **New (proved here; possibly folklore).**

*Let Tₙ be a deterministic q-query hardness test that accepts at least one function
f. Then Tₙ also accepts some function g with circuit size ≤ 3(q+1)n. Consequently, a
nontrivial deterministic test that is useful against SIZE(s) must satisfy
q > s/(3n) − 1.*

**Proof.** Run Tₙ with oracle access to the accepted function f. Since Tₙ is
deterministic, this produces a fixed transcript: queried points x₁, …, x_r (r ≤ q)
and answers f(x₁), …, f(x_r), ending in acceptance.

Define g : {0,1}ⁿ → {0,1} by g(x) = f(x) if x ∈ {x₁, …, x_r}, and g(x) = 0 otherwise.

*Tₙ accepts g.* By induction on the steps of the transcript: the first query x₁ is
determined before any oracle answer, hence identical for f and g, and
g(x₁) = f(x₁) by construction; assuming the first i queries and answers coincide, the
(i+1)-st query is a function of that shared prefix, hence identical, and g agrees with
f on it. So the entire transcript — and therefore the decision — is identical: Tₙ
accepts g.

*g is easy.* Let A = {xᵢ : f(xᵢ) = 1} ⊆ {x₁, …, x_r}, so |A| ≤ q and g is the
indicator of A. If A = ∅ then g ≡ 0, computable with O(1) gates. Otherwise
g(x) = ⋁_{a∈A} ⋀_{i=1}^{n} ℓᵢᵃ(x), where ℓᵢᵃ(x) = xᵢ if aᵢ = 1 and ¬xᵢ if aᵢ = 0.
Each conjunction uses ≤ n − 1 binary ∧ gates and ≤ n negations, i.e. ≤ 2n − 1 gates;
the disjunction adds ≤ |A| − 1 ≤ q − 1 gates. Total: ≤ q(2n − 1) + q − 1 < q(2n+1)
≤ 3(q+1)n gates.

So Tₙ accepts a function in SIZE(3(q+1)n). If Tₙ is useful against SIZE(s) with
s ≥ 3(q+1)n, it can accept nothing — contradicting nontriviality. Rearranging gives
q > s/(3n) − 1. ∎

**Corollary A1 (New, proved here).** Any nontrivial deterministic hardness test useful
against P/poly (i.e., against SIZE(n^k) for every k at large n) must make n^{ω(1)}
queries; any such test useful against SIZE(2^{n/4}) must read ≥ 2^{n/4}/(3n) − 1 bits
of the truth table — within a poly(n) factor of the trivial 2ⁿ. **Deterministically,
hardness cannot be spot-checked at all.** Note that no largeness assumption and no
computational bound appear anywhere: this is an information barrier, not a
computational one.

### Theorem B — randomized evasion with a non-explicit anchor. **New (proved here; possibly folklore).**

*For all sufficiently large n there exist a function h : {0,1}ⁿ → {0,1} and a
randomized nonadaptive 500-query test T such that:*

1. *T accepts h with probability 1;*
2. *every f with Pr[T accepts f] ≥ 2/3 agrees with h on > 0.6 · 2ⁿ inputs;*
3. *no function in SIZE(2^{n/4}) agrees with h on ≥ 0.6 · 2ⁿ inputs.*

*Hence Φ := {f : Pr[T accepts f] ≥ 2/3} is a nonempty property, decidable from O(1)
random truth-table probes, useful against SIZE(2^{n/4}).*

**Proof.** *Existence of h (counting).* The number of distinct functions computed by
circuits with s gates on n inputs is at most (3(s + n + 2)²)^s ≤ 2^{s(2 log₂(s+n+2)+2)}:
each gate is described by its type (≤ 3 choices) and two inputs drawn from earlier
gates, input variables, and constants. For s = 2^{n/4} and large n this is at most
2^{2^{n/2}}. The number of functions agreeing with a *fixed* function on ≥ 0.6 · 2ⁿ
points equals the number of binary strings of length N = 2ⁿ within Hamming distance
0.4N of a fixed string, which is ≤ 2^{H(0.4)N} ≤ 2^{0.972·N} (H = binary entropy;
Standard bound Σ_{i≤αN} C(N,i) ≤ 2^{H(α)N} for α < 1/2). Hence the number of
functions 0.6-agreeing with *some* size-2^{n/4} circuit is at most
2^{2^{n/2}} · 2^{0.972 · 2ⁿ} < 2^{2ⁿ} for large n. Choose h to be any function outside
this set (indeed a 1 − 2^{−Ω(2ⁿ)} fraction of all functions qualifies). This gives
property 3.

*The test.* T samples x₁, …, x₅₀₀ independently and uniformly from {0,1}ⁿ, queries
f(xᵢ), and accepts iff #{i : f(xᵢ) = h(xᵢ)} ≥ 400 (i.e., empirical agreement ≥ 0.8).

*Property 1.* If f = h, all 500 samples agree; T accepts with probability 1.

*Property 2.* Suppose f agrees with h on a fraction α ≤ 0.6 of inputs. The number of
agreeing samples is a sum of 500 i.i.d. Bernoulli(α) variables; by Hoeffding's
inequality, Pr[empirical agreement ≥ 0.8] ≤ exp(−2 · (0.8 − 0.6)² · 500) = e^{−40}
< 1/3. Contrapositive: acceptance probability ≥ 2/3 forces α > 0.6.

*Usefulness.* Let f ∈ Φ. By property 2, f agrees with h on > 0.6 · 2ⁿ inputs. If f
had a circuit of size 2^{n/4}, that circuit would compute a function 0.6-agreeing with
h, contradicting property 3. So Φ ∩ SIZE(2^{n/4}) = ∅, and h ∈ Φ ≠ ∅. ∎

**Corollary B1 — the access dichotomy (New, proved here).** Hardness certification
from truth-table access exhibits an unconditional deterministic/randomized dichotomy:
Ω(s/n) queries are necessary deterministically (Theorem A) and O(1) queries suffice
with randomness (Theorem B). Moreover the randomized certificate constructed is
(i) *non-large* — Φ has measure ≤ 2^{(H(0.4)−1)2ⁿ} = 2^{−Ω(2ⁿ)} among all functions,
and (ii) *anchored non-explicitly* — specifying T requires the 2ⁿ-bit table of h, and
producing any valid anchor h is, by property 3, *precisely the problem of exhibiting a
function that is average-case hard for exponential-size circuits*, i.e., the very
explicitness problem that circuit lower bounds are trying to solve.

**Interpretation (Heuristic, clearly flagged).** Corollary B1 turns the old slogan
"hard functions abound by counting (Shannon 1949); only explicitness is missing" into
a two-sided quantitative statement about *certification*: below full access, soundness
is impossible without randomness, and with randomness the entire difficulty
concentrates in the anchor. Together with Razborov–Rudich (full access + efficiency +
largeness ⇒ PRFs break), this cleanly delimits the only remaining habitat for a
property-based proof of NP ⊄ P/poly: essentially-full access, and either
non-constructivity or non-largeness. We emphasize: this constrains *approaches*, and
proves *nothing* about the truth value of P vs NP.

---

## 6. Why this does not resolve P vs NP

1. **The theorems are about tests, not about SAT.** Theorems A and B constrain
   procedures that interact with a function *only through its truth table*. A proof
   of P ≠ NP is not obliged to be such a procedure: it may exploit the description of
   SAT (self-reducibility, paddability, completeness), uniformity, or proof-theoretic
   structure. The barrier delimits property-based (natural-proof-style) strategies
   only — exactly as Razborov–Rudich delimited theirs.
2. **No new lower bound for any explicit function is produced.** Theorem B's anchor h
   is non-explicit by construction; converting it into an explicit function is the
   open problem, not a step toward it. The memo's proved content moves no explicit
   lower bound past 3.1n, ACC⁰, or n^{3−o(1)}.
3. **Quantitative weakness.** Theorem A's Ω(s/n) query bound is far below the 2ⁿ bits
   a poly(2ⁿ)-time natural property may read; it therefore does not interact with the
   Razborov–Rudich regime at all except as a complementary tier, and it says nothing
   about computationally-bounded full-access tests (that tier remains conditional on
   PRFs, as before).
4. **All four established barrier families still stand.** Any resolution must
   simultaneously be non-relativizing (02-01), non-algebrizing (02-03), non-natural
   (02-02), evade locality at the magnification frontier (02-02/02-04), and — if it is
   to be carried out in feasible mathematics — escape the bounded-arithmetic
   unprovability zone (02-09). Nothing in this memo weakens any of these; Section 4
   adds one more constraint on one family of approaches.
5. **Independence is not established either.** Per 02-09, P vs NP remains not known
   to be independent of PA or ZFC, and the Ben-David–Halevi phenomenon shows that
   independence via all known non-Gödelian techniques would itself imply startling
   algorithmic consequences. This memo takes no position on truth or provability.
6. **The upper-bound wall is intact.** The best 3-SAT constant remains 1.306973
   (02-10), the savings decay like Θ(1/k) exactly as SETH predicts, and any dramatic
   generalization of the upper-bound technology is already known to be equivalent to
   lower-bound progress (Williams). Nothing here changes that exchange rate.

**Verdict (per the program's rubric): incremental.** A clean reformulation
(certification-access barrier) with two small unconditional theorems proved in full,
correctly situated relative to known barriers; no movement on the conjecture itself,
and no claim of such.

---

## 7. References

Bibliographic details verified against live sources on 2026-08-15 where marked (†);
the remainder are standard and given from the literature.

**Foundations and completeness.**
1. S. A. Cook. *The complexity of theorem-proving procedures.* STOC 1971.
2. L. Levin. *Universal search problems.* Problemy Peredachi Informatsii 9(3), 1973.
3. R. M. Karp. *Reducibility among combinatorial problems.* In Complexity of Computer Computations, 1972.
4. J. Hartmanis, R. E. Stearns. *On the computational complexity of algorithms.* Trans. AMS 117, 1965.
5. R. E. Ladner. *On the structure of polynomial time reducibility.* J. ACM 22(1), 1975.
6. S. A. Cook. *The P versus NP problem.* Clay Mathematics Institute problem description, 2000.
7. S. Aaronson. *P =? NP.* In Open Problems in Mathematics, Springer, 2016.

**Barriers.**
8. † T. Baker, J. Gill, R. Solovay. *Relativizations of the P =? NP question.* SIAM J. Comput. 4(4):431–442, 1975.
9. A. Razborov, S. Rudich. *Natural proofs.* J. Comput. Syst. Sci. 55(1):24–35, 1997.
10. † S. Aaronson, A. Wigderson. *Algebrization: a new barrier in complexity theory.* ACM Trans. Comput. Theory 1(1), 2009.
11. S. Arora, R. Impagliazzo, U. Vazirani. *Relativizing versus nonrelativizing techniques: the role of local checkability.* Manuscript, 1992.
12. R. Impagliazzo, V. Kabanets, A. Kolokolova. *An axiomatic approach to algebrization.* STOC 2009.
13. B. Aydınlıoğlu, E. Bach. *Affine relativization: unifying the algebrization and relativization barriers.* ACM Trans. Comput. Theory, 2018.
14. † L. Chen, S. Hirahara, I. C. Oliveira, J. Pich, N. Rajgopal, R. Santhanam. *Beyond natural proofs: hardness magnification and locality.* J. ACM 69(4), 2022.
15. L. Fortnow, M. Sipser. *Are there interactive protocols for co-NP languages?* Inf. Process. Lett. 28(5), 1988.

**Circuit lower bounds.**
16. M. Ajtai. *Σ¹₁-formulae on finite structures.* Ann. Pure Appl. Logic 24, 1983.
17. M. Furst, J. Saxe, M. Sipser. *Parity, circuits, and the polynomial-time hierarchy.* Math. Systems Theory 17, 1984.
18. J. Håstad. *Almost optimal lower bounds for small depth circuits.* STOC 1986.
19. A. Razborov. *Lower bounds on the size of bounded depth circuits over a complete basis with logical addition.* Mat. Zametki 41(4), 1987.
20. R. Smolensky. *Algebraic methods in the theory of lower bounds for Boolean circuit complexity.* STOC 1987.
21. A. Razborov. *Lower bounds on the monotone complexity of some Boolean functions.* Dokl. Akad. Nauk SSSR 281, 1985.
22. N. Alon, R. Boppana. *The monotone circuit complexity of Boolean functions.* Combinatorica 7(1), 1987.
23. R. Williams. *Improving exhaustive search implies superpolynomial lower bounds.* STOC 2010; SIAM J. Comput. 42(3), 2013.
24. R. Williams. *Nonuniform ACC circuit lower bounds.* J. ACM 61(1), 2014 (announced 2011).
25. C. Murray, R. Williams. *Circuit lower bounds for nondeterministic quasi-polytime: an easy witness lemma for NP and NQP.* STOC 2018.
26. L. Chen, X. Lyu, R. Williams. *Almost-everywhere circuit lower bounds from non-trivial derandomization.* FOCS 2020.
27. M. G. Find, A. Golovnev, E. A. Hirsch, A. S. Kulikov. *A better-than-3n lower bound for the circuit complexity of an affine disperser.* FOCS 2016.
28. J. Li, T. Yang. *3.1n − o(n) circuit lower bounds for explicit functions.* STOC 2022.
29. B. A. Subbotovskaya. *Realizations of linear functions by formulas using +, ·, −.* Dokl. Akad. Nauk SSSR 136, 1961.
30. A. E. Andreev. *On a method for obtaining more than quadratic effective lower bounds for the complexity of π-schemes.* Moscow Univ. Math. Bull. 42, 1987.
31. J. Håstad. *The shrinkage exponent of De Morgan formulas is 2.* SIAM J. Comput. 27(1), 1998.
32. A. Tal. *Shrinkage of De Morgan formulae by spectral techniques.* FOCS 2014.
33. M. Karchmer, R. Raz, A. Wigderson. *Super-logarithmic depth lower bounds via the direct sum in communication complexity.* Comput. Complexity 5, 1995.
34. † R. Kannan. *Circuit-size lower bounds and non-reducibility to sparse sets.* Information and Control 55, 1982.
35. R. Santhanam. *Circuit lower bounds for Merlin–Arthur classes.* SIAM J. Comput. 39(3), 2009.
36. H. Buhrman, L. Fortnow, T. Thierauf. *Nonrelativizing separations.* IEEE Conf. Computational Complexity 1998.
37. C. E. Shannon. *The synthesis of two-terminal switching circuits.* Bell Syst. Tech. J. 28, 1949.
38. R. Impagliazzo, V. Kabanets, A. Wigderson. *In search of an easy witness: exponential time vs. probabilistic polynomial time.* J. Comput. Syst. Sci. 65(4), 2002.

**Structural / conditional results.**
39. R. Karp, R. Lipton. *Some connections between nonuniform and uniform complexity classes.* STOC 1980.
40. S. Mahaney. *Sparse complete sets for NP: solution of a conjecture of Berman and Hartmanis.* J. Comput. Syst. Sci. 25(2), 1982.
41. R. Impagliazzo, A. Wigderson. *P = BPP if E requires exponential circuits.* STOC 1997.
42. L. Valiant, V. Vazirani. *NP is as easy as detecting unique solutions.* Theor. Comput. Sci. 47, 1986.
43. O. Goldreich, S. Goldwasser, S. Micali. *How to construct random functions.* J. ACM 33(4), 1986.
44. M. Naor, O. Reingold. *Number-theoretic constructions of efficient pseudo-random functions.* J. ACM 51(2), 2004.
45. R. Williams. *Natural proofs versus derandomization.* SIAM J. Comput. 45(2), 2016.
46. M. Carmosino, R. Impagliazzo, V. Kabanets, A. Kolokolova. *Learning algorithms from natural proofs.* CCC 2016.
47. I. C. Oliveira, R. Santhanam. *Hardness magnification for natural problems.* FOCS 2018.
48. D. McKay, C. Murray, R. Williams. *Weak lower bounds on resource-bounded compression imply strong separations of complexity classes.* STOC 2019.
49. S. Hirahara. *Non-black-box worst-case to average-case reductions within NP.* FOCS 2018.
50. S. Hirahara. *NP-hardness of learning programs and partial MCSP.* FOCS 2022.

**Proof complexity.**
51. S. Cook, R. Reckhow. *The relative efficiency of propositional proof systems.* J. Symbolic Logic 44(1), 1979.
52. A. Haken. *The intractability of resolution.* Theor. Comput. Sci. 39, 1985.
53. V. Chvátal, E. Szemerédi. *Many hard examples for resolution.* J. ACM 35(4), 1988.
54. M. Ajtai. *The complexity of the pigeonhole principle.* FOCS 1988; Combinatorica 14, 1994.
55. T. Pitassi, P. Beame, R. Impagliazzo. *Exponential lower bounds for the pigeonhole principle.* Comput. Complexity 3, 1993.
56. J. Krajíček, P. Pudlák, A. Woods. *An exponential lower bound to the size of bounded depth Frege proofs of the pigeonhole principle.* Random Struct. Algorithms 7(1), 1995.
57. P. Pudlák. *Lower bounds for resolution and cutting plane proofs and monotone computations.* J. Symbolic Logic 62(3), 1997.
58. A. Razborov. *Lower bounds for the polynomial calculus.* Comput. Complexity 7, 1998.
59. R. Impagliazzo, P. Pudlák, J. Sgall. *Lower bounds for the polynomial calculus and the Gröbner basis algorithm.* Comput. Complexity 8, 1999.
60. D. Grigoriev. *Linear lower bound on degrees of Positivstellensatz calculus proofs for the parity.* Theor. Comput. Sci. 259, 2001.
61. G. Schoenebeck. *Linear level Lasserre lower bounds for certain k-CSPs.* FOCS 2008.
62. J. Grochow, T. Pitassi. *Circuit complexity, proof complexity, and polynomial identity testing: the ideal proof system.* J. ACM 65(6), 2018.
63. M. Forbes, A. Shpilka, I. Tzameret, A. Wigderson. *Proof complexity lower bounds from algebraic circuit complexity.* Theory of Computing 17, 2021 (CCC 2016).
64. J. Krajíček, P. Pudlák. *Some consequences of cryptographical conjectures for S¹₂ and EF.* Inf. Comput. 140(1), 1998.
65. M. L. Bonet, T. Pitassi, R. Raz. *On interpolation and automatization for Frege systems.* SIAM J. Comput. 29(6), 2000.
66. † A. Atserias, M. Müller. *Automating resolution is NP-hard.* J. ACM 67(5), 2020.
67. † S. F. de Rezende, M. Göös, J. Nordström, T. Pitassi, R. Robere, D. Sokolov. *Automating algebraic proof systems is NP-hard.* STOC 2021.
68. † J. Krajíček. *Proof Complexity Generators.* Monograph, 2024.
69. A. Razborov. *Pseudorandom generators hard for k-DNF resolution and polynomial calculus resolution.* Ann. of Math. 181(2), 2015.

**Geometric complexity theory / algebraic complexity.**
70. L. Valiant. *Completeness classes in algebra.* STOC 1979.
71. K. Mulmuley, M. Sohoni. *Geometric complexity theory I: an approach to the P vs. NP and related problems.* SIAM J. Comput. 31(2), 2001.
72. K. Mulmuley, M. Sohoni. *Geometric complexity theory II: towards explicit obstructions for embeddings among class varieties.* SIAM J. Comput. 38(3), 2008.
73. T. Mignon, N. Ressayre. *A quadratic bound for the determinant and permanent problem.* Int. Math. Res. Not. 2004(79), 2004.
74. B. Grenet. *An upper bound for the permanent versus determinant problem.* Manuscript, 2011.
75. C. Ikenmeyer, G. Panova. *Rectangular Kronecker coefficients and plethysms in geometric complexity theory.* Adv. Math. 319, 2017 (FOCS 2016).
76. † P. Bürgisser, C. Ikenmeyer, G. Panova. *No occurrence obstructions in geometric complexity theory.* J. Amer. Math. Soc. 32:163–193, 2019 (FOCS 2016).
77. † J. Dörfler, C. Ikenmeyer, G. Panova. *On geometric complexity theory: multiplicity obstructions are stronger than occurrence obstructions.* arXiv:1901.04576, 2019 (ICALP 2019).
78. P. Bürgisser. *Completeness and Reduction in Algebraic Complexity Theory.* Springer, 2000.

**Fine-grained complexity.**
79. R. Impagliazzo, R. Paturi. *On the complexity of k-SAT.* J. Comput. Syst. Sci. 62(2), 2001.
80. R. Impagliazzo, R. Paturi, F. Zane. *Which problems have strongly exponential complexity?* J. Comput. Syst. Sci. 63(4), 2001.
81. R. Williams. *A new algorithm for optimal 2-constraint satisfaction and its implications.* Theor. Comput. Sci. 348(2–3), 2005.
82. A. Backurs, P. Indyk. *Edit distance cannot be computed in strongly subquadratic time (unless SETH is false).* STOC 2015.
83. K. Bringmann. *Why walking the dog takes time: Fréchet distance has no strongly subquadratic algorithms unless SETH fails.* FOCS 2014.
84. A. Abboud, A. Backurs, V. Vassilevska Williams. *Tight hardness results for LCS and other sequence similarity measures.* FOCS 2015.
85. V. Vassilevska Williams, R. Williams. *Subcubic equivalences between path, matrix and triangle problems.* FOCS 2010; J. ACM 65(5), 2018.
86. A. Gajentaan, M. Overmars. *On a class of O(n²) problems in computational geometry.* Comput. Geom. 5(3), 1995.
87. M. Pătraşcu. *Towards polynomial lower bounds for dynamic problems.* STOC 2010.
88. M. Carmosino, J. Gao, R. Impagliazzo, I. Mihajlin, R. Paturi, S. Schneider. *Nondeterministic extensions of the strong exponential time hypothesis and consequences for non-reducibility.* ITCS 2016.
89. R. Williams. *Faster all-pairs shortest paths via circuit complexity.* STOC 2014; SIAM J. Comput. 47(5), 2018.

**Interactive proofs.**
90. C. Lund, L. Fortnow, H. Karloff, N. Nisan. *Algebraic methods for interactive proof systems.* J. ACM 39(4), 1992.
91. A. Shamir. *IP = PSPACE.* J. ACM 39(4), 1992.
92. L. Babai, L. Fortnow, C. Lund. *Non-deterministic exponential time has two-prover interactive protocols.* Comput. Complexity 1(1), 1991.
93. S. Arora, S. Safra. *Probabilistic checking of proofs: a new characterization of NP.* J. ACM 45(1), 1998.
94. S. Arora, C. Lund, R. Motwani, M. Sudan, M. Szegedy. *Proof verification and the hardness of approximation problems.* J. ACM 45(3), 1998.
95. I. Dinur. *The PCP theorem by gap amplification.* J. ACM 54(3), 2007.
96. Z. Ji, A. Natarajan, T. Vidick, J. Wright, H. Yuen. *MIP\* = RE.* arXiv:2001.04383, 2020; Commun. ACM 64(11), 2021.

**Meta-mathematics / bounded arithmetic.**
97. J. Hartmanis, J. Hopcroft. *Independence results in computer science.* SIGACT News 8(4), 1976.
98. † S. Ben-David, S. Halevi. *On the independence of P versus NP.* Technical Report 699, Technion, 1991.
99. † S. Aaronson. *Is P versus NP formally independent?* Bulletin of the EATCS 81, 2003. (Also expounds Kurtz–O'Donnell–Royer.)
100. † A. Razborov. *Unprovability of lower bounds on circuit size in certain fragments of bounded arithmetic.* Izvestiya RAN 59(1), 1995.
101. A. Razborov. *Bounded arithmetic and lower bounds in Boolean complexity.* In Feasible Mathematics II, 1995.
102. J. Krajíček. *Interpolation theorems, lower bounds for proof systems, and independence results for bounded arithmetic.* J. Symbolic Logic 62(2), 1997.
103. † S. Cook, J. Krajíček. *Consequences of the provability of NP ⊆ P/poly.* J. Symbolic Logic 72(4), 2007.
104. † J. Krajíček, I. C. Oliveira. *Unprovability of circuit upper bounds in Cook's theory PV.* Logical Methods in Computer Science 13(1), 2017.
105. † J. Bydžovský, M. Müller. *Polynomial time ultrapowers and the consistency of circuit lower bounds.* Arch. Math. Logic 59, 2020.
106. † J. Pich, R. Santhanam. *Strong co-nondeterministic lower bounds for NP cannot be proved feasibly.* STOC 2021.
107. † J. Li, I. C. Oliveira. *Unprovability of strong complexity lower bounds in bounded arithmetic.* STOC 2023.
108. † A. Atserias, S. Buss, M. Müller. *On the consistency of circuit lower bounds for non-deterministic time.* STOC 2023.
109. † I. C. Oliveira. *Meta-mathematics of computational complexity theory* (SIGACT News Complexity Theory Column 124). arXiv:2504.04416, 2025.
110. E. Jeřábek. *Approximate counting in bounded arithmetic.* J. Symbolic Logic 72(3), 2007.
111. S. Buss. *Bounded Arithmetic.* Bibliopolis, 1986.

**Moderately exponential SAT algorithms.**
112. B. Monien, E. Speckenmeyer. *Solving satisfiability in less than 2ⁿ steps.* Discrete Appl. Math. 10(3), 1985.
113. R. Paturi, P. Pudlák, F. Zane. *Satisfiability coding lemma.* Chicago J. Theor. Comput. Sci., 1999 (FOCS 1997).
114. U. Schöning. *A probabilistic algorithm for k-SAT and constraint satisfaction problems.* FOCS 1999.
115. R. Paturi, P. Pudlák, M. Saks, F. Zane. *An improved exponential-time algorithm for k-SAT.* J. ACM 52(3), 2005.
116. † T. Hertli. *3-SAT faster and simpler — unique-SAT bounds for PPSZ hold in general.* FOCS 2011; SIAM J. Comput. 43(2), 2014.
117. † T. D. Hansen, H. Kaplan, O. Zamir, U. Zwick. *Faster k-SAT algorithms using biased-PPSZ.* STOC 2019.
118. † D. Scheder. *PPSZ is better than you think.* FOCS 2021; TheoretiCS 3, 2024.
119. † D. Scheder. *PPSZ for general k-SAT and CSP — making Hertli's analysis simpler and 3-SAT faster.* Comput. Complexity, 2024.
120. R. A. Moser, D. Scheder. *A full derandomization of Schöning's k-SAT algorithm.* STOC 2011.
121. † D. Scheder, N. Talebanfard. *Super strong ETH is true for PPSZ with small resolution width.* CCC 2020.
122. † S. Chen, D. Scheder, N. Talebanfard, B. Tang. *Exponential lower bounds for the PPSZ k-SAT algorithm.* SODA 2013.
123. R. Schuler. *An algorithm for the satisfiability problem of formulas in conjunctive normal form.* J. Algorithms 54(1), 2005.
124. C. Calabro, R. Impagliazzo, R. Paturi. *A duality between clause width and clause density for SAT.* CCC 2006.
125. L. Fortnow, D. van Melkebeek. *Time-space tradeoffs for nondeterministic computation.* CCC 2000.
126. R. Williams. *Time-space tradeoffs for counting NP solutions modulo integers.* Comput. Complexity 17(2), 2008.
127. S. Buss, R. Williams. *Limits on alternation-trading proofs for time-space lower bounds.* CCC 2012.
128. D. van Melkebeek. *A survey of lower bounds for satisfiability and related problems.* Found. Trends Theor. Comput. Sci. 2(3), 2007.

*End of report. Legion 02 makes no claim to have resolved, or materially advanced the
truth value of, P vs NP.*
