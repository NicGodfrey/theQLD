# P vs NP — Wave-2 Breakthrough

**Scope.** One lemma, fully proved, strictly stronger than Theorems A/B of
`REPORT.md` (Section 5) within their shared model. Everything below is
self-contained: all definitions are restated, all constants are explicit, and no
step appeals to an unproved claim. This document does not modify `REPORT.md`.

---

## Theorem (one statement)

**Model (identical to REPORT.md §5, restated for self-containment).** Fix n.
Circuits are over {∧, ∨, ¬} with fan-in 2; inputs are the variables x₁, …, xₙ and
the constants 0, 1; size = number of gates; SIZE(s) is the set of functions
f : {0,1}ⁿ → {0,1} computed by circuits with ≤ s gates. A *deterministic q-query
hardness test* Tₙ is a decision tree of depth ≤ q over the 2ⁿ coordinates of the
truth table of f: it adaptively selects points x₁, x₂, … (each depending on the
answers so far), reads f(x₁), f(x₂), …, and outputs accept/reject; no computational
bound is placed on the selection or the decision. Tₙ is *useful against SIZE(s)* if
every accepted f has circuit size > s; it is *nontrivial* if it accepts at least one
function. A test is *nonadaptive* if the set of queried points is fixed in advance.
All logarithms are base 2.

> **Theorem (deterministic probe complexity of hardness certification, determined
> to within a Θ(n) factor).** Let n ≥ 4 and let s satisfy 100n² ≤ s and
> 3s·log s + 1 ≤ 2ⁿ. Let D_n(s) denote the least q for which there exists a
> nontrivial deterministic q-query hardness test useful against SIZE(s). Then
>
> **(s·log s)/(20n)  <  D_n(s)  ≤  3s·log s + 1,**
>
> and the upper bound is witnessed by a *nonadaptive* test. In particular the
> deterministic probe complexity of certifying SIZE(s)-hardness equals s·log s up to
> a multiplicative factor of at most 60n + 1.

Both inequalities are unconditional. The lower bound strictly subsumes Theorem A of
`REPORT.md` throughout the stated range (Corollary 1 below quantifies the gain: a
factor Θ(n) in the regime s = 2^{εn}); the upper bound is new — `REPORT.md` proved
no deterministic upper bound below the trivial 2ⁿ.

---

## Proof (complete)

### Lemma 1 (decoder). For every b ≥ 1, all 2ᵇ minterms on b variables can be computed simultaneously by a single circuit with at most 2^{b+1} gates.

(A *minterm* on variables y₁, …, y_b is a conjunction ℓ₁ ∧ … ∧ ℓ_b with
ℓᵢ ∈ {yᵢ, ¬yᵢ}.)

**Proof.** Let D(b) be the minimum number of gates needed. Base cases:

- b = 1: the two minterms are y₁ and ¬y₁; one ¬ gate. D(1) = 1 ≤ 4.
- b = 2: 2 negations plus 4 ∧ gates: D(2) ≤ 6 ≤ 8.
- b = 3: compute all 4 minterms on {y₁, y₂} (≤ 6 gates), the pair y₃, ¬y₃
  (1 gate), and the 8 products (8 gates): D(3) ≤ 15 ≤ 16.
- b = 4: two halves of size 2 (≤ 6 gates each) and 16 products:
  D(4) ≤ 28 ≤ 32.

Inductive step, b ≥ 5: split the variables into halves of sizes ⌈b/2⌉ and ⌊b/2⌋;
every minterm on b variables is the ∧ of one minterm from each half, so

D(b) ≤ D(⌈b/2⌉) + D(⌊b/2⌋) + 2ᵇ ≤ 2^{⌈b/2⌉+1} + 2^{⌊b/2⌋+1} + 2ᵇ ≤ 2^{⌈b/2⌉+2} + 2ᵇ.

Since b ≥ 5 gives ⌈b/2⌉ + 2 ≤ b, the first term is ≤ 2ᵇ, so D(b) ≤ 2^{b+1}. ∎

### Lemma 2 (sparse indicators are easy, with explicit constant). Let A ⊆ {0,1}ⁿ with |A| = m. Then the indicator function 1_A has circuit size ≤ 2 if m = 0; ≤ 2n − 1 if m = 1; and ≤ 10mn / log m if 2 ≤ m ≤ 2ⁿ.

**Proof.** m = 0: 1_A ≡ 0 = x₁ ∧ ¬x₁, two gates. m = 1: a single minterm on n
variables: at most n negations and n − 1 conjunctions, total ≤ 2n − 1.

For m ≥ 2, set b := ⌈log m⌉; since m ≤ 2ⁿ, b ≤ n. Partition the n variables into
k := ⌈n/b⌉ blocks, each of size ≤ b. For each block, compute all minterms of that
block (Lemma 1): cost ≤ 2^{b+1} per block, and 2^{b+1} ≤ 2^{log m + 2} = 4m. For
each a ∈ A, the minterm of a is the ∧ of its k block-minterms, already available on
wires: ≤ k − 1 gates per point. Finally 1_A is the ∨ of the m point-minterms:
≤ m − 1 gates. Total:

size(1_A) ≤ k·2^{b+1} + m(k − 1) + (m − 1) ≤ k·4m + mk = 5mk.

Now k = ⌈n/b⌉ ≤ n/b + 1, and b ≥ log m, so
5mk ≤ 5mn/log m + 5m ≤ 5mn/log m + 5mn/log m = 10mn/log m, where the last step
uses 5m ≤ 5mn/log m, i.e. log m ≤ n, which holds since m ≤ 2ⁿ. ∎

### Lemma 3 (explicit Shannon counting). Let B(s) := |{f : {0,1}ⁿ → {0,1} computable by a circuit with ≤ s gates}|. For all n, s ≥ 1, B(s) ≤ (n + 2) + s·(3(n + s + 1)²)^s; consequently, if n ≤ s and s ≥ 2¹⁰ then B(s) ≤ 2^{3s·log s}.

**Proof.** A circuit with exactly t ≥ 1 gates can be listed in topological order
with the output at gate t. Gate i is described by its type (3 choices) and its two
input wires, each drawn from {0, 1, x₁, …, xₙ, gate₁, …, gate_{i−1}}, i.e. at most
(n + 2 + i − 1) ≤ (n + t + 1) choices per wire. Hence there are at most
(3(n + t + 1)²)^t circuits with t gates, and each computes one function. Circuits
with 0 gates compute the n + 2 functions {0, 1, x₁, …, xₙ}. Summing t = 1, …, s and
bounding every term by the largest gives
B(s) ≤ (n + 2) + s·(3(n + s + 1)²)^s.

Now let n ≤ s and s ≥ 2¹⁰. Then n + 2 ≤ 3s ≤ s·(3(n+s+1)²)^s, so
B(s) ≤ 2s·(3(n + s + 1)²)^s and

log B(s) ≤ 1 + log s + s·(log 3 + 2·log(n + s + 1)).

Since n ≤ s, n + s + 1 ≤ 2s + 1 ≤ 3s, hence 2·log(n+s+1) ≤ 2·log 3 + 2·log s, and
log 3 + 2·log 3 ≤ 4.755. For s ≥ 2¹⁰ we have 4.755 ≤ 0.48·log s (because
log s ≥ 10), so

log B(s) ≤ 1 + log s + s(0.48·log s + 2·log s) = 1 + log s + 2.48·s·log s
≤ 3s·log s,

where the last inequality uses 1 + log s ≤ 0.52·s·log s (clear for s ≥ 2¹⁰). ∎

### Proposition 1 (transcript sparsification — the adversary step). Let Tₙ be a deterministic q-query test that accepts at least one function f. Then Tₙ also accepts the function g := 1_A, where A = {queried points x with f(x) = 1}; in particular |A| =: m satisfies m ≤ min(q, 2ⁿ), and g is a sparse indicator as in Lemma 2.

**Proof.** Run Tₙ with oracle f. Determinism yields a fixed transcript: queried
points x₁, …, x_r (r ≤ q, all in {0,1}ⁿ) with answers f(x₁), …, f(x_r), ending in
acceptance. Define g(x) = f(x) for x ∈ {x₁, …, x_r} and g(x) = 0 otherwise; then
g = 1_A with A as stated and m ≤ r ≤ q, m ≤ 2ⁿ.

Tₙ accepts g, by induction on the transcript: the first query is fixed before any
answer, hence identical for f and g, and g agrees with f on it; if the first i
queries and answers coincide, the (i+1)-st query is a function of that shared
prefix, hence identical, and g agrees with f on it by construction. So the entire
transcript, and therefore the decision, is identical: Tₙ accepts g. ∎

### Part (a): the lower bound D_n(s) > (s·log s)/(20n).

Let Tₙ be a nontrivial deterministic q-query test useful against SIZE(s), with
n ≥ 4 and s ≥ 100n². By Proposition 1, Tₙ accepts g = 1_A with |A| = m ≤ min(q, 2ⁿ).
Usefulness forces size(g) > s. We examine m using Lemma 2:

- **m = 0:** size(g) ≤ 2 ≤ s — contradiction.
- **m = 1:** size(g) ≤ 2n − 1 < 100n² ≤ s — contradiction.
- **m ≥ 2:** s < size(g) ≤ 10mn/log m.

So m ≥ 2 and s < 10mn/log m. Let h(m) := m/log m. The real function x/ln x has
derivative (ln x − 1)/(ln x)², positive for x > e, so h is increasing on integers
m ≥ 3; also h(2) = 2 = h(4). Hence for q ≥ 4, max{h(m) : 2 ≤ m ≤ q} = h(q).

*Case q ≤ 3.* Then m ∈ {2, 3} and 10mn/log m ≤ max(20n, 30n/log 3) = 20n < 100n²
≤ s — contradiction. So q ≥ 4.

*Case q ≥ 4.* Then s < 10n·h(m) ≤ 10n·h(q) = 10qn/log q, i.e.

**q > s·log q / (10n).**  (★)

Since q ≥ 4, log q ≥ 2, so (★) gives q > s/(5n) ≥ 100n²/(5n) = 20n, and

log q > log s − log(5n) ≥ log s − ½·log s = ½·log s,

where log(5n) ≤ ½·log s because (5n)² = 25n² ≤ 100n² ≤ s. Substituting back
into (★):

q > s·(½·log s)/(10n) = **(s·log s)/(20n).** ∎

### Part (b): the upper bound D_n(s) ≤ 3s·log s + 1, nonadaptively.

Assume n ≥ 4, 100n² ≤ s, and 3s·log s + 1 ≤ 2ⁿ. Note s ≥ 100n² ≥ 1600 ≥ 2¹⁰ and
s ≥ 100n² ≥ n, so Lemma 3 applies: B(s) ≤ 2^{3s·log s}.

Set q := ⌊3s·log s⌋ + 1 ≤ 2ⁿ and let Q ⊆ {0,1}ⁿ be the first q strings in
lexicographic order. Consider the restriction map f ↦ f|_Q from SIZE(s) to
{0,1}^Q. Its image has at most B(s) ≤ 2^{3s·log s} < 2^q elements, while
|{0,1}^Q| = 2^q. Hence some pattern π : Q → {0,1} is realized by **no** function in
SIZE(s).

Define the nonadaptive q-query test T*: query exactly the points of Q and accept
iff f|_Q = π.

- *Useful against SIZE(s):* if T* accepts f and f had a circuit of size ≤ s, then
  f|_Q = π would be realized by a SIZE(s) function — contradiction. So every
  accepted f has size > s.
- *Nontrivial:* the function equal to π on Q and 0 elsewhere is accepted.

Thus D_n(s) ≤ q ≤ 3s·log s + 1. ∎

Combining (a) and (b): (s·log s)/(20n) < D_n(s) ≤ 3s·log s + 1, and the ratio of
the bounds is (3s·log s + 1)·(20n)/(s·log s) = 60n + 20n/(s·log s) < 60n + 1.
**This proves the Theorem.** ∎

### Corollary 1 (strict improvement over Theorem A of REPORT.md; Θ(n) gain in the exponential regime).

Theorem A gave q > s/(3n) − 1. Part (a) gives q > (s·log s)/(20n), which is larger
whenever log s > 20/3, i.e. s ≥ 102 — true throughout the Theorem's range
(s ≥ 100n² ≥ 1600). Concretely, for s = 2^{n/4} and n ≥ 80 (then 100n² ≤ 2^{n/4}
and 3s·log s + 1 ≤ 2ⁿ, so the Theorem applies):

2^{n/4}/80 < D_n(2^{n/4}) ≤ (3n/4)·2^{n/4} + 1.

Theorem A gave only q > 2^{n/4}/(3n) − 1; the new lower bound is stronger by a
factor 3n/80 = Θ(n). ∎ (Both conditions at n = 80: 100·80² = 640000 ≤ 2²⁰ =
1048576 ✓, and 3·2²⁰·20 + 1 < 2⁸⁰ ✓.)

### Corollary 2 (adaptivity is nearly useless here).

The upper bound in (b) is achieved by a nonadaptive test, and the lower bound in
(a) holds for adaptive tests. Hence in the Theorem's range, adaptive query
selection can reduce the probe complexity of hardness certification by a factor of
at most 60n + 1. ∎

### Corollary 3 (zero-error randomness certifies nothing: the exact location of Theorem B's power).

Define a *randomized q-query test* as a probability distribution R over
deterministic q-query tests, *perfectly sound against SIZE(s)* if every test in the
support of R accepts only functions of size > s, and *nontrivial* if some f is
accepted with probability > 0.

*Claim:* under the Theorem's hypotheses, every nontrivial perfectly sound
randomized q-query test satisfies q > (s·log s)/(20n).

*Proof:* pick f with Pr_{T∼R}[T accepts f] > 0 and a test T₀ in the support of R
accepting f. T₀ is a deterministic, nontrivial, useful q-query test; apply
part (a). ∎

*Consequence:* any nontrivial randomized test with q ≤ (s·log s)/(20n) queries
must accept some function of circuit size ≤ s with positive probability. Theorem B
of `REPORT.md` (500 queries, useful in the two-sided-error sense against
SIZE(2^{n/4})) is therefore possible **only** because a fixed seed of its test
accepts easy functions with small but positive probability. The randomized
evasion of Theorem B is purchased entirely by soundness error — not by randomness
in query selection, which Corollary 2 shows is nearly worthless, and not by any
other resource.

### Consistency check (recorded for scrupulousness).

The function accepted by T* in part (b) is itself a sparse indicator of ≤ q points;
by Lemma 2 its size is ≤ 10qn/log q ≈ 30sn·(1 + o(1)), which indeed exceeds s, so
parts (a) and (b) are compatible. Also, the property {f : f|_Q = π} accepted by T*
has density 2^{−q} = 2^{−Θ(s log s)} among all functions — far below the
2^{−O(n)} largeness threshold of Razborov–Rudich, consistent with the natural-proofs
barrier (which is untouched; see below).

---

## What is new vs REPORT.md

1. **The lower bound is strictly sharper than Theorem A, by a factor Θ(log s).**
   Theorem A: q > s/(3n) − 1, proved via a plain DNF of the transcript
   (size ≤ 3(q+1)n). Here the block-decoder construction (Lemmas 1–2) compresses
   the transcript indicator to 10qn/log q gates, which converts, through the same
   adversary step, into q > (s·log s)/(20n). In the flagship regime s = 2^{n/4}
   this is a Θ(n) improvement: 2^{n/4}/80 versus 2^{n/4}/(3n) (Corollary 1). All
   constants are explicit and every inequality is verified in the proof.
2. **The first upper bound.** `REPORT.md` proved no deterministic test with fewer
   than the trivial 2ⁿ queries exists; part (b) constructs a nonadaptive test with
   3s·log s + 1 queries via an explicit counting argument (Lemma 3, which also
   supplies the "clean Shannon counting with explicit numbers" requested as a
   candidate direction: B(s) ≤ 2^{3s·log s} for n ≤ s, s ≥ 2¹⁰, plus the existence
   of a pattern on ⌊3s·log s⌋ + 1 fixed truth-table positions avoided by all
   size-s circuits).
3. **Together: a two-sided determination.** The deterministic probe complexity of
   hardness certification is pinned to the window [(s·log s)/(20n), 3s·log s + 1] —
   i.e. it *equals* s·log s up to a factor ≤ 60n + 1. Theorem A was a one-sided
   impossibility; this is a (near-)characterization. The first row of the
   three-tier table in `REPORT.md` §4 upgrades from "deterministic, ≤ s/3n bits:
   impossible" to "deterministic: Θ̃(s) bits, necessary and sufficient up to Θ(n)".
4. **Two structural corollaries with complete proofs.** Adaptivity helps by at most
   a factor 60n + 1 (Corollary 2), and randomness with zero soundness error helps
   not at all (Corollary 3). Corollary 3 locates the entire power of Theorem B's
   O(1)-query evasion in its soundness error: below (s·log s)/(20n) queries, any
   test that accepts anything must accept an easy function with positive
   probability. Neither statement appears in `REPORT.md`.

What is *not* new: the transcript/adversary step (Proposition 1) is the same
mechanism as Theorem A's; the sparse-indicator upper bound is a standard
Lupanov-style decoder argument; the counting is Shannon's. The new content is the
sharpened combination, the explicit constants, the matching upper bound, and the
two corollaries.

---

## Why P vs NP remains open

1. **The theorem is about truth-table-probe tests, not about SAT.** It constrains
   procedures that interact with a Boolean function only through oracle access to
   its truth table. A proof of P ≠ NP is under no obligation to be such a
   procedure: it may exploit the description of SAT (self-reducibility,
   paddability, completeness), uniformity, or proof-theoretic structure. Like
   Theorems A/B and like Razborov–Rudich, this delimits a *family of approaches*;
   it says nothing about the truth value of P vs NP.
2. **No explicit lower bound moves.** The hard objects here are non-explicit
   twice over: the unrealized pattern π of part (b) is found by exhaustive
   enumeration of all 2^{O(s log s)} size-s circuits, and the accepted functions
   are indicators produced by counting, not constructions. The best explicit
   general-circuit lower bound remains ~3.1n (Li–Yang 2022, per `REPORT.md` §2),
   and nothing here changes that.
3. **The Razborov–Rudich tier is untouched.** The natural-proofs barrier concerns
   full-access, poly(2ⁿ)-time, *large* properties and remains conditional on
   pseudorandom functions exactly as before. The present theorem lives in the
   information-access tier (computationally unbounded, query-bounded) and only
   sharpens that tier from a one-sided bound to a two-sided determination.
4. **All established barriers stand.** Relativization, algebrization, natural
   proofs, locality/magnification, and the bounded-arithmetic unprovability
   results catalogued in `REPORT.md` §§2–3 are unaffected. If anything, the
   theorem reinforces the report's synthesis: hardness certification below full
   access is information-theoretically expensive (now with matching bounds), and
   the cheap randomized certificates concentrate all difficulty in a non-explicit
   anchor with unavoidable soundness error (Corollary 3).
5. **No uniform consequence.** D_n(s) is a purely non-uniform, per-length
   quantity. Bounds on it imply nothing about deterministic time classes, NP, or
   any uniform separation.

---

## Honesty label

**New (proved here; elementary; possibly folklore-adjacent — no priority claim).
Unconditional. Not progress on the truth value of P vs NP.**

- Every lemma, the theorem, and all three corollaries are proved in full above
  with explicit constants; nothing is conditional and nothing is deferred.
- The ingredients are classical (decision-tree adversary/transcript, Lupanov-style
  block decoder, Shannon counting). The specific two-sided statement about the
  model of `REPORT.md` §5 — lower bound (s·log s)/(20n), nonadaptive upper bound
  3s·log s + 1, adaptivity gap ≤ 60n + 1, zero-error-randomness collapse — is not
  in `REPORT.md` and was not found by us in print, but the "hardness test" model
  is the report's own; the result is internal to that model and we make no claim
  of novelty beyond it.
- Known gap, stated openly: the window between the bounds is a factor Θ(n)
  (essentially "log of the truth-table length"). Closing it — i.e. determining
  whether adaptive tests can beat s·log s by a Θ(n) factor — is open even in this
  toy model.
- This is a barrier-sharpening meta-theorem about hardness-certification
  procedures. It is **not** a circuit lower bound for any explicit function, not
  a statement about SAT, and not a step toward resolving P vs NP, which remains
  open for the reasons given above.
