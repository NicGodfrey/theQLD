# Theory 02 — Probe adaptivity collapses exactly: D_n^{na}(s) = D_n(s), and both equal the smallest non-shattered set

**Scope.** One new theorem, fully proved, in the model of the Wave-2 note
`../conjectures/02-p-vs-np/BREAKTHROUGH.md` (henceforth *Wave-2*). Wave-2 proved
(s·log s)/(20n) < D_n(s) ≤ 3s·log s + 1 for the deterministic probe complexity of
SIZE(s)-hardness certification, bounded the adaptive-over-nonadaptive advantage
only by a factor 60n + 1 (its Corollary 2), and listed the power of adaptive
querying as open in its honesty label. The theorem below settles the
adaptive-vs-nonadaptive question **exactly**: the advantage is 1. Among the three
alternatives posed for this note — D_n^{na}(s) ≤ Cn·D_n(s) for explicit C, equality
up to (1+o(1)), or a factor-2 separation — the true and strongest one is *exact
equality for all parameters*, and we prove it, together with an exact
combinatorial characterization of the common value. Everything needed is
restated; the proof of the theorem is self-contained and imports nothing.
All logarithms are base 2.

---

## Model (identical to Wave-2, restated for self-containment)

Fix n ≥ 1 and write F_n for the set of all functions f : {0,1}ⁿ → {0,1}. Circuits
are over {∧, ∨, ¬} with fan-in 2; inputs are the variables x₁, …, xₙ and the
constants 0, 1; size = number of gates; SIZE(s) ⊆ F_n is the set of functions
computed by circuits with ≤ s gates. (SIZE(s) is never empty: the constants and
the variables need 0 gates.)

An **adaptive deterministic q-query test** T is a decision tree of depth ≤ q over
the 2ⁿ coordinates of the truth table: each internal node is labeled by a point of
{0,1}ⁿ, has two children indexed by the answer bit, and each leaf is labeled
accept or reject. Running T on f follows the path determined by the answers
f(x₁), f(x₂), …; T accepts f iff the run ends at an accepting leaf. No
computational bound is placed on the tree.

A **nonadaptive q-query test** is a pair (Q, Φ) with Q ⊆ {0,1}ⁿ, |Q| ≤ q, and
Φ : {0,1}^Q → {accept, reject}; it accepts f iff Φ(f|_Q) = accept. Querying the
points of Q in a fixed order realizes (Q, Φ) as a decision tree of depth |Q|, so
nonadaptive tests are a special case of adaptive ones.

Fix a class C ⊆ F_n (the intended instantiation is C = SIZE(s)). A test is
**useful against C** if its accepted set is disjoint from C (every accepted f lies
outside C); it is **nontrivial** if it accepts at least one function. Let

- **D(C)** := the least q for which a nontrivial adaptive deterministic q-query
  test useful against C exists;
- **D^{na}(C)** := the same with "nonadaptive" in place of "adaptive";
- **D_n(s)** := D(SIZE(s)) and **D_n^{na}(s)** := D^{na}(SIZE(s)), matching Wave-2.

Both quantities are well defined (finite) iff C ≠ F_n: if C = F_n every accepted
function would violate usefulness, so no nontrivial useful test exists at any q;
if C ≠ F_n, pick h ∉ C, query all 2ⁿ points and accept iff f = h.

**Patterns and shattering.** A *pattern* is a pair (Q, π) with Q ⊆ {0,1}ⁿ and
π : Q → {0,1}. The pattern is *realized in C* if some g ∈ C has g|_Q = π, and
*C-avoided* otherwise. A set Q is *shattered by C* if all 2^{|Q|} patterns on Q
are realized in C. Define the **certification number**

> **u(C) := min{ |Q| : Q ⊆ {0,1}ⁿ is not shattered by C }**
> = the minimum size of the support of a C-avoided pattern.

If ∅ ≠ C ⊊ F_n then 1 ≤ u(C) ≤ 2ⁿ: the empty set is shattered (its unique, empty
pattern is realized by any member of C ≠ ∅), and the full domain is not shattered
(the pattern equal to any h ∉ C on all of {0,1}ⁿ is C-avoided).

---

## Theorem (probe-adaptivity collapse and exact characterization)

> **Theorem.** Let n ≥ 1 and let C be any class with ∅ ≠ C ⊊ F_n. Then
>
> **D(C) = D^{na}(C) = u(C),**
>
> and the optimum is attained by a *single-pattern* nonadaptive test: fix a
> C-avoided pattern (Q, π) with |Q| = u(C), query Q, and accept iff f|_Q = π.
> In particular, with C = SIZE(s): for every n and every s with SIZE(s) ≠ F_n,
>
> **D_n^{na}(s) = D_n(s) = u(SIZE(s))** — exactly, with no parameter
> restrictions. Adaptive query selection has **zero** advantage for hardness
> certification: no pair (n, s) exhibits a separation by a factor 2, nor by
> 1 + o(1), nor by any factor exceeding 1. Equivalently, D_n(s) equals the
> smallest cardinality of a set of inputs not shattered by size-s circuits.

The statement is unconditional. It is not in Wave-2: that file's Corollary 2
bounds the adaptivity advantage only by 60n + 1, and its honesty label leaves the
role of adaptivity open.

---

## Proof (complete)

### Lemma (frozen path). Let T be an adaptive deterministic test and let f be a function accepted by T. Let Q_f ⊆ {0,1}ⁿ be the set of (distinct) points queried during the run of T on f. Then every g ∈ F_n with g|_{Q_f} = f|_{Q_f} is accepted by T, and |Q_f| ≤ depth(T).

**Proof.** Let the run of T on f query the points x₁, …, x_r in this order
(r ≤ depth(T); a point may in principle repeat, in which case f supplies the same
answer each time, and |Q_f| ≤ r). We show by induction on i that the run of T on g
queries the same point xᵢ at step i and receives the same answer. Base: the first
query is the label of the root, fixed before any answer, hence equal to x₁; since
x₁ ∈ Q_f and g agrees with f on Q_f, the answer g(x₁) = f(x₁). Step: if the first
i queries and answers coincide for f and g, then both runs sit at the same node of
the tree, so the (i+1)-st query is the same point x_{i+1} ∈ Q_f, and
g(x_{i+1}) = f(x_{i+1}) by agreement on Q_f. Hence the two runs traverse the same
root-to-leaf path and end at the same accepting leaf: T accepts g. ∎

(The induction is the same mechanism as Wave-2's Proposition 1; the difference is
in what is extracted from it. Wave-2 replaces the off-path values by 0 to obtain
one sparse accepted function; here we keep **all** completions, obtaining an
entire accepted subcube — and this is what kills adaptivity.)

### Step 1: u(C) ≤ D(C).

Let T be a nontrivial adaptive test of depth q = D(C), useful against C. By
nontriviality some f is accepted; let Q := Q_f and π := f|_{Q_f} as in the Lemma,
so |Q| ≤ q. By the Lemma, every g with g|_Q = π is accepted by T; by usefulness,
every such g lies outside C. Hence no member of C agrees with π on Q: the pattern
(Q, π) is C-avoided, Q is not shattered, and u(C) ≤ |Q| ≤ D(C). ∎

### Step 2: D^{na}(C) ≤ u(C).

Let (Q, π) be a C-avoided pattern with |Q| = u(C). Define the nonadaptive test
T*: query exactly the points of Q and accept iff f|_Q = π (this is (Q, Φ) with Φ
the indicator of the single answer string π).

- *Nontrivial:* the function g₀ equal to π on Q and 0 elsewhere satisfies
  g₀|_Q = π, so T* accepts g₀.
- *Useful against C:* if T* accepts f then f|_Q = π; since (Q, π) is C-avoided,
  f ∉ C.

T* makes |Q| = u(C) queries, so D^{na}(C) ≤ u(C). ∎

### Step 3: D(C) ≤ D^{na}(C).

A nonadaptive q-query test is an adaptive test of depth ≤ q (query the fixed set
in a fixed order, ignore the answers when choosing queries, decide by Φ). Any
nontrivial useful nonadaptive test is therefore also a nontrivial useful adaptive
test of the same query complexity. ∎

### Conclusion.

Chaining Steps 1–3: u(C) ≤ D(C) ≤ D^{na}(C) ≤ u(C), so all three are equal, and
Step 2 exhibits an optimal test in single-pattern form. For C = SIZE(s) (nonempty
always; a proper subclass of F_n whenever s is below the maximum circuit
complexity of n-bit functions, in particular throughout Wave-2's parameter range —
see Corollary 1), this gives D_n^{na}(s) = D_n(s) = u(SIZE(s)). If SIZE(s) = F_n,
neither quantity is defined (no nontrivial useful test exists, adaptive or not),
so equality holds in every case in which either side means anything.
**This proves the Theorem.** ∎

---

## Corollaries

### Corollary 1 (the trichotomy resolved; Wave-2's window transfers verbatim to nonadaptive tests).

Let n ≥ 4 and 100n² ≤ s and 3s·log s + 1 ≤ 2ⁿ (Wave-2's range). Wave-2's part (b)
exhibits a pattern on ⌊3s·log s⌋ + 1 points realized by no function in SIZE(s); in
particular SIZE(s) ≠ F_n there, so the Theorem applies and, importing Wave-2's
two-sided bound,

**(s·log s)/(20n) < D_n^{na}(s) = D_n(s) = u(SIZE(s)) ≤ 3s·log s + 1.**

Consequences. (i) The inequality D_n^{na}(s) ≤ Cn·D_n(s) holds with the best
possible constant: the factor is exactly 1, not Θ(n); Wave-2's Corollary 2 bound
of 60n + 1 improves to 1. (ii) No pair (n, s) — inside or outside Wave-2's
range — satisfies D_n^{na}(s) ≥ 2·D_n(s), nor even
D_n^{na}(s) ≥ (1 + ε)·D_n(s) for any ε > 0: the separation alternative is false.
(iii) In the flagship regime s = 2^{n/4}, n ≥ 80:
2^{n/4}/80 < D_n^{na}(2^{n/4}) = D_n(2^{n/4}) ≤ (3n/4)·2^{n/4} + 1. ∎

### Corollary 2 (shattering reformulation; counting and VC upper bounds with arbitrary query positions).

Let ∅ ≠ C ⊊ F_n, let B := |C|, and let VC(C) be the VC dimension of C as a set
system on {0,1}ⁿ (the largest cardinality of a shattered subset).

1. *(Uniform shattering below the threshold.)* Every Q ⊆ {0,1}ⁿ with
   |Q| < D(C) is shattered by C. For C = SIZE(s): every pattern on fewer than
   D_n(s) inputs — hence, importing Wave-2's part (a), every pattern on at most
   (s·log s)/(20n) inputs — is realized by a circuit with ≤ s gates.
2. *(Counting bound, any positions.)* D(C) ≤ ⌊log B⌋ + 1, and moreover **every**
   set Q of size ⌊log B⌋ + 1 supports a C-avoided pattern.
3. *(VC bound.)* D(C) ≤ VC(C) + 1.

**Proof.** (1) is the equality D(C) = u(C) read contrapositively: a non-shattered
set of size < D(C) would force u(C) < D(C). The SIZE(s) instantiation combines
this with Wave-2's lower bound D_n(s) > (s·log s)/(20n).
(2) Restriction to Q maps C into {0,1}^Q, so at most B patterns on Q are realized;
if |Q| = ⌊log B⌋ + 1 then 2^{|Q|} > B, so some pattern on Q is C-avoided and Q is
not shattered; hence u(C) ≤ |Q|. Such Q exists: C ⊊ F_n gives B < 2^{2ⁿ}, so
⌊log B⌋ + 1 ≤ 2ⁿ.
(3) Any set of size VC(C) + 1 is non-shattered by maximality of the VC dimension,
so u(C) ≤ VC(C) + 1. Such a set exists: VC(C) = 2ⁿ would mean C shatters the
whole cube, i.e. C = F_n, excluded. ∎

Item (2) applied to C = SIZE(s) with Wave-2's Lemma 3 (B ≤ 2^{3s·log s} for
n ≤ s, s ≥ 2¹⁰) recovers Wave-2's upper bound D_n(s) ≤ 3s·log s + 1, and refines
it in two ways: the exact form D_n(s) ≤ ⌊log |SIZE(s)|⌋ + 1, and the freedom to
place the ⌊3s·log s⌋ + 1 queries at *arbitrary* positions of the truth table, not
just the lexicographically first ones used in Wave-2's part (b).

### Corollary 3 (worst-case-sound randomized tests: R = D exactly).

Define a *randomized q-query test* as a probability distribution R over the
(finite) set of adaptive deterministic decision trees of depth ≤ q. Say R is
**worst-case sound against SIZE(s)** if Pr_{T∼R}[T accepts f] = 0 for every
f ∈ SIZE(s) (it *never* accepts an easy function), and **nontrivial** if some f₀
has Pr_{T∼R}[T accepts f₀] ≥ 2/3. Let R_n^{ws}(s) be the least such q. Then, for
every n, s with SIZE(s) ≠ F_n,

**R_n^{ws}(s) = D_n(s) = D_n^{na}(s) = u(SIZE(s)),**

and the optimum is attained by a deterministic single-pattern nonadaptive test.

**Proof.** (≤) The point mass on an optimal deterministic test T* from Step 2 is
worst-case sound (T* accepts no member of SIZE(s) at all) and nontrivial (T*
accepts g₀ with probability 1 ≥ 2/3), so R_n^{ws}(s) ≤ D_n(s).
(≥) Let R attain R_n^{ws}(s) =: q, and let f₀ satisfy Pr[T accepts f₀] ≥ 2/3.
The set E of depth-≤q trees accepting f₀ is finite and Pr(E) ≥ 2/3 > 0, so some
T₀ ∈ E has Pr[T = T₀] > 0. T₀ is nontrivial (it accepts f₀). T₀ is useful: if T₀
accepted some g ∈ SIZE(s), then Pr_{T∼R}[T accepts g] ≥ Pr[T = T₀] > 0, violating
worst-case soundness. So T₀ witnesses D_n(s) ≤ q. The remaining equalities are
the Theorem. ∎

This sharpens Wave-2's Corollary 3 — which proved only the one-sided bound
q > (s·log s)/(20n) for perfectly sound randomized tests — to an exact identity
R = D = D^{na} = u, by the same one-tree extraction plus the new collapse. It also
re-confirms Wave-2's diagnosis with no slack left: the O(1)-query randomized
evasion (Wave-2 REPORT Theorem B) is purchased *entirely* by soundness error.
Once a test is forbidden to ever accept an easy function, randomness **and**
adaptivity are both exactly worthless.

---

## Remarks

1. **Why this does not contradict known adaptivity gaps.** In property testing,
   adaptive tests can be much cheaper than nonadaptive ones (for arbitrary
   properties the generic conversion costs 2^q). Those models demand
   *completeness over the whole property*: every function with the property must
   be accepted (with good probability). Here completeness is existential —
   accept at least one function — and the frozen-path Lemma converts one
   accepted function into an accepted subcube; passing to a single leaf preserves
   existential completeness but would destroy universal completeness. The
   collapse is thus a feature of certification-type acceptance conditions
   (nontrivial + one-sided sound), and we claim nothing for models with
   universal completeness.
2. **Where the open problem now lives.** Wave-2's honesty label asked whether
   adaptive tests can beat s·log s by a Θ(n) factor. The Theorem removes
   adaptivity from the question entirely: the residual Θ(n) window
   (s·log s)/(20n) < u(SIZE(s)) ≤ 3s·log s + 1 is now a *purely combinatorial*
   question about circuits — what is the smallest set of inputs not shattered by
   SIZE(s)? Equivalently: how many gates suffice to realize an arbitrary pattern
   on q inputs (with the completion free)? The Theorem does not narrow that
   window; it shows the window is about partial-function circuit complexity and
   nothing else.
3. **Monotonicity, for the record.** u(SIZE(s)) is nondecreasing in s: a larger
   class realizes more patterns, so shattered sets only accumulate. Via the
   Theorem this is also immediate for D_n(s), as usefulness against a larger
   class is a stronger constraint.

---

## What is new vs Wave-2

1. **Exact adaptivity collapse.** Wave-2's Corollary 2: adaptivity helps by at
   most 60n + 1. Here: it helps by exactly 1, for all n, s, with no parameter
   restrictions — settling the trichotomy posed for this note (equality holds;
   the Cn-factor bound is true with factor 1; the factor-2 separation is false).
2. **Exact characterization.** D_n(s) = D_n^{na}(s) = u(SIZE(s)), the smallest
   non-shattered set of inputs; plus the canonical single-pattern form of an
   optimal test. Neither the identity nor the quantity u appears in Wave-2.
3. **Refined upper bound.** D_n(s) ≤ ⌊log |SIZE(s)|⌋ + 1 with arbitrary query
   positions (Corollary 2), a formally sharper and structurally stronger version
   of Wave-2's part (b).
4. **Exact randomized identity.** R_n^{ws}(s) = D_n(s) for worst-case-sound
   randomized tests (Corollary 3), upgrading Wave-2's Corollary 3 from a lower
   bound to an equality.

What is *not* new: the frozen-path induction is the same standard decision-tree
argument as Wave-2's Proposition 1 (used there to sparsify, here to keep the whole
subcube); the counting in Corollary 2 is Shannon-style; Corollary 3's extraction
of a deterministic tree from the support is the mechanism of Wave-2's
Corollary 3.

---

## Why P vs NP remains open

1. The theorem is about truth-table-probe certification, not about SAT or any
   explicit function; it constrains a family of approaches, not the truth value
   of P vs NP.
2. It proves no new circuit lower bound: the avoided patterns exist by counting
   and are non-explicit, exactly as in Wave-2.
3. If anything it strengthens the negative message of Wave-2: below the
   information-theoretic threshold u(SIZE(s)), no amount of adaptivity, and no
   randomness without soundness error, certifies hardness — the only escape
   (Wave-2 REPORT Theorem B) is to accept easy functions with positive
   probability.
4. The Razborov–Rudich, relativization, and algebrization barriers are untouched;
   D_n(s) and u(SIZE(s)) are non-uniform, per-length quantities with no bearing on
   uniform separations.

---

## Honesty line

**New relative to Wave-2 (proved here in full; elementary; folklore-adjacent — the
frozen-path argument is standard decision-tree reasoning and u(C) resembles
exclusion-dimension/non-membership-certificate quantities in learning theory; no
priority claim). Unconditional. Resolves the adaptive-vs-nonadaptive question of
Wave-2's honesty label exactly (advantage = 1); does NOT narrow Wave-2's Θ(n)
window for the value of D_n(s), which persists as the open combinatorial problem
of determining u(SIZE(s)); not progress on the truth value of P vs NP.**
