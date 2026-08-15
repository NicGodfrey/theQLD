# 08 — The Cycle-Congruence Theorem: Forbidden Residue Classes for Syracuse Cycles

**Status: original theory. Every claim below is proved in full, by elementary number theory, in this file.**

**Honesty line.** Nothing here assumes or uses the numerical verification of the Collatz
conjecture up to 2⁶⁸/2⁷¹, and nothing here proves that nontrivial cycles do not exist. What is
proved is a set of *exact identities* that every cycle must satisfy, and a set of *forbidden
residue classes*: explicit congruence classes modulo 4 and modulo 3 that no nontrivial cycle can
live inside. The only arithmetic "computations" used are single evaluations such as S(1) = 1,
S(3) = 5, S(5) = 1, which are one-line calculations, not machine verification. What remains open
is stated explicitly in §7. This note does not repeat the Wave-2 predecessor-tree result
(the exponent c\* ≈ 0.30); it is logically independent of it.

---

## 1. Setup and notation

For an odd positive integer n, let v₂(m) denote the 2-adic valuation of m (the exponent of the
largest power of 2 dividing m), and define the **Syracuse map**

  S(n) = (3n + 1) / 2^{v₂(3n+1)} ,

which is again an odd positive integer. (S is the odd-to-odd acceleration of the map
T(n) = n/2 for even n, (3n+1)/2 for odd n: one application of S equals one T-odd-step followed by
all subsequent T-halving-steps.)

A **cycle** of length L is a tuple C = (n₁, …, n_L) of odd positive integers with
n_{i+1} = S(n_i) for 1 ≤ i ≤ L, indices read modulo L (so n_{L+1} = n₁), and with the n_i
pairwise distinct as a cyclic orbit. Write

  k_i = v₂(3n_i + 1) ≥ 1,  K = k₁ + k₂ + ⋯ + k_L,
  σ₀ = 0, σ_j = k₁ + ⋯ + k_j (so σ_L = K).

The **trivial cycle** is C = (1): indeed 3·1 + 1 = 4 = 2², so S(1) = 1 with k = 2. A cycle is
**nontrivial** if it is not the trivial cycle. K is the total number of halvings ("total doubling")
around the cycle; L is the number of odd terms.

Two elementary observations used repeatedly:

**Observation A (cycles are S-images).** Every element of a cycle is in the image of S, since
n_{i+1} = S(n_i) and the indexing wraps around.

**Observation B (a cycle containing 1, 3, or 5 is trivial).** If 1 ∈ C, then since S(1) = 1 the
successor of 1 inside C is 1 itself, and iterating, every element of C equals 1; so C = (1).
If 5 ∈ C then S(5) = 16/16 = 1 ∈ C, so C = (1), contradicting 5 ∈ C. If 3 ∈ C then
S(3) = 10/2 = 5 ∈ C, contradiction again. Hence every element of a nontrivial cycle is ≥ 7.

---

## 2. Lemma 1: the local step data mod 4 and mod 3

**Lemma 1.** Let n be odd, k = v₂(3n+1), and n′ = S(n). Then:

1. **(mod 4 controls k.)** k = 1 ⟺ n ≡ 3 (mod 4), and k ≥ 2 ⟺ n ≡ 1 (mod 4).
2. **(k controls the image mod 3.)** n′ ≡ (−1)^k (mod 3). In particular n′ ≡ 1 (mod 3) iff k is
   even, n′ ≡ 2 (mod 3) iff k is odd, and **never** n′ ≡ 0 (mod 3).

*Proof.* (1) 3n + 1 ≡ 2 (mod 4) ⟺ 3n ≡ 1 (mod 4) ⟺ n ≡ 3 (mod 4), because 3·3 = 9 ≡ 1 (mod 4).
For odd n, 3n+1 is even, so k = 1 exactly when 3n+1 ≡ 2 (mod 4), i.e. n ≡ 3 (mod 4); otherwise
4 ∣ 3n+1, i.e. k ≥ 2, which happens exactly when n ≡ 1 (mod 4).

(2) By definition 2^k · n′ = 3n + 1 ≡ 1 (mod 3). Since 2 ≡ −1 (mod 3), this reads
(−1)^k n′ ≡ 1 (mod 3), i.e. n′ ≡ (−1)^k (mod 3). As (−1)^k ∈ {1, −1}, n′ is never ≡ 0 (mod 3). ∎

Combined with Observation A: **no element of any cycle is divisible by 3.**

---

## 3. Theorem 1: the exact cycle identities

**Theorem 1 (exact identities).** Let C = (n₁, …, n_L) be any cycle, with k_i, K, σ_j as above.
Then:

1. **(Multiplicative identity.)**
   ∏_{i=1}^{L} (3 + 1/n_i) = 2^K.
2. **(Integer form.)** For every starting index (stated here for index 1):
   (2^K − 3^L) · n₁ = Σ_{j=1}^{L} 3^{L−j} · 2^{σ_{j−1}} ,
   a sum of L positive integers; consequently 2^K − 3^L is a **positive** integer, i.e.
   2^K > 3^L. The same holds for every n_m with the partial sums σ taken starting at index m; in
   particular, summing over all L rotations,
   (2^K − 3^L) · (n₁ + ⋯ + n_L) is an explicit sum of L² positive terms of the form 3^a 2^b.
3. **(Linear form.)**
   Σ_{i=1}^{L} 2^{k_i} n_{i+1} = 3 (n₁ + ⋯ + n_L) + L.
4. **(Two-sided bound.)** 3^L < 2^K ≤ 4^L, i.e. L·log₂3 < K ≤ 2L, with the right-hand equality
   K = 2L only for the trivial cycle.

*Proof.* (1) From 2^{k_i} n_{i+1} = 3 n_i + 1 = n_i (3 + 1/n_i) we get
n_{i+1} = n_i (3 + 1/n_i) / 2^{k_i}. Multiplying over i = 1, …, L and using that the product
∏ n_{i+1} equals ∏ n_i (both run over the whole cycle) and is nonzero, the n-products cancel and
∏ (3 + 1/n_i) = 2^{Σ k_i} = 2^K.

(2) We prove by induction on j that

  2^{σ_j} n_{j+1} = 3^j n₁ + Σ_{m=1}^{j} 3^{j−m} 2^{σ_{m−1}}  (0 ≤ j ≤ L).

For j = 0 it reads n₁ = n₁ (empty sum). Assume it for j; multiply the step relation
2^{k_{j+1}} n_{j+2} = 3 n_{j+1} + 1 by 2^{σ_j}:

  2^{σ_{j+1}} n_{j+2} = 3·2^{σ_j} n_{j+1} + 2^{σ_j}
   = 3^{j+1} n₁ + Σ_{m=1}^{j} 3^{j+1−m} 2^{σ_{m−1}} + 3^0·2^{σ_j}
   = 3^{j+1} n₁ + Σ_{m=1}^{j+1} 3^{j+1−m} 2^{σ_{m−1}} ,

completing the induction. At j = L, n_{L+1} = n₁ and σ_L = K, giving
2^K n₁ = 3^L n₁ + Σ_{m=1}^{L} 3^{L−m} 2^{σ_{m−1}}, which is the claim. The right side is a sum of
L positive integers, so (2^K − 3^L) n₁ > 0 and hence 2^K − 3^L ≥ 1. Rotating the starting index
and summing gives the L²-term identity.

(3) Sum 2^{k_i} n_{i+1} = 3 n_i + 1 over i = 1, …, L.

(4) Each n_i ≥ 1 is odd, so 3 < 3 + 1/n_i ≤ 4, and (1) gives 3^L < 2^K ≤ 4^L. Equality on the
right forces every factor to equal 4 (a product of L factors, each ≤ 4, can equal 4^L only if
each factor is exactly 4), i.e. every n_i = 1, the trivial cycle. Taking log₂ gives
L·log₂3 < K ≤ 2L. ∎

---

## 4. Lemma 2: the rigidity lemma

This is the engine of the forbidden-class theorem.

**Lemma 2 (rigidity).** If every exponent satisfies k_i ≥ 2, then C is the trivial cycle.

*Proof.* K = Σ k_i ≥ 2L, so 2^K ≥ 4^L. But Theorem 1(1) and n_i ≥ 1 give
2^K = ∏(3 + 1/n_i) ≤ 4^L. Hence 2^K = 4^L exactly, and as in Theorem 1(4), every factor equals 4,
so every n_i = 1 and C = (1). ∎

Note the shape of the argument: a *congruence* hypothesis (all k_i ≥ 2) collides with the *exact
size* identity ∏(3 + 1/n_i) = 2^K, and the only escape hatch is the trivial cycle. No growth
estimates, no probabilistic heuristics, no computer search.

---

## 5. Theorem 2: the Cycle-Congruence Theorem (forbidden residue classes)

**Theorem 2.** Let C = (n₁, …, n_L) be a cycle of the Syracuse map.

1. **(Class 3 mod 4 is forbidden outright.)** It is impossible that every n_i ≡ 3 (mod 4).
   (This holds with no nontriviality assumption.)
2. **(Class 1 mod 4 forces triviality.)** If every n_i ≡ 1 (mod 4), then C = (1). Hence **no
   nontrivial cycle lies inside a single residue class mod 4.**
3. **(Class 0 mod 3 is forbidden outright.)** No element of any cycle is ≡ 0 (mod 3).
4. **(Class 1 mod 3 forces triviality.)** If every n_i ≡ 1 (mod 3), then C = (1). Hence no
   nontrivial cycle lies inside the class 1 (mod 3), and every nontrivial cycle contains a term
   ≡ 2 (mod 3).

*Proof.*

**(1)** By Lemma 1(1), n_i ≡ 3 (mod 4) means k_i = 1 for every i, so K = L. Theorem 1(4) gives
3^L < 2^K = 2^L, i.e. (3/2)^L < 1, impossible for L ≥ 1.
(Equivalently and even more simply: k_i = 1 means n_{i+1} = (3n_i + 1)/2 > n_i, so the terms
strictly increase around a closed loop — absurd.)

**(2)** By Lemma 1(1), n_i ≡ 1 (mod 4) for all i means k_i ≥ 2 for all i, and Lemma 2 gives
C = (1). (The statement is sharp: the trivial cycle does lie in the class 1 (mod 4).)

**(3)** Observation A plus Lemma 1(2): every cycle element is an S-image, and S-images are never
divisible by 3.

**(4)** Suppose every n_i ≡ 1 (mod 3). Each n_{i+1} is the S-image of n_i, and by Lemma 1(2),
n_{i+1} ≡ (−1)^{k_i} (mod 3). So n_{i+1} ≡ 1 (mod 3) forces k_i even; in particular k_i ≥ 2 for
every i. Lemma 2 gives C = (1). (Again sharp: 1 ≡ 1 (mod 3), and the trivial cycle has k = 2,
even, consistent throughout.) Since class 0 (mod 3) is empty on cycles by (3), a nontrivial cycle
must contain a term ≡ 2 (mod 3). ∎

Thus **m = 4 is an explicit modulus > 2 such that no nontrivial cycle lies in any single residue
class mod m**, and mod 3 the classes 0 and 1 are likewise forbidden for nontrivial cycles.
Note the pleasant asymmetry of the two mod-4 cases: class 3 (mod 4) dies because the cycle would
be *too big* (2^L < 3^L — pure growth), class 1 (mod 4) dies because the cycle would be *too
small* (2^K ≥ 4^L — rigidity). A cycle must balance on the knife edge between them, which is
exactly the content of the corollaries below.

---

## 6. Corollaries: structure forced on every nontrivial cycle

**Corollary 1 (mixed residues and the exponent vector).** Every nontrivial cycle contains at
least one term ≡ 1 (mod 4) **and** at least one term ≡ 3 (mod 4) **and** at least one term
≡ 2 (mod 3). Equivalently (via Lemma 1), its exponent vector (k₁, …, k_L) contains at least one
entry equal to 1 and at least one entry ≥ 2. In particular L ≥ 2, and K satisfies the **strict**
two-sided bound

  L·log₂3 < K ≤ 2L − 1.

*Proof.* The mod-4 statements are Theorem 2(1),(2); the mod-3 statement is Theorem 2(4). By
Lemma 1(1) these translate to: some k_i = 1, some k_j ≥ 2 — so L ≥ 2 (one exponent cannot be both).
K = 2L is excluded by Theorem 1(4), so K ≤ 2L − 1. ∎

(As a cross-check on L ≥ 2: a fixed point satisfies n(2^k − 3) = 1, forcing n = 1, k = 2 — the
trivial cycle.)

**Corollary 2 (quantitative closeness of K/L to log₂3).** Let n\* = min_i n_i. Then

  0 < K/L − log₂3 < 1 / (3 n\* ln 2).

*Proof.* Divide the multiplicative identity by 3^L: 2^K / 3^L = ∏(1 + 1/(3 n_i)) ≤
(1 + 1/(3n\*))^L. Take natural logs and use ln(1+x) < x:
K ln 2 − L ln 3 ≤ L·ln(1 + 1/(3n\*)) < L/(3n\*). Divide by L ln 2. The left inequality is
2^K > 3^L from Theorem 1(2). ∎

**Corollary 3 (a positive density of terms ≡ 3 mod 4).** Let A = #{ i : n_i ≡ 3 (mod 4) }
= #{ i : k_i = 1 }. Then in any nontrivial cycle

  A ≥ 2L − K > L · ( 2 − log₂3 − 1/(3 n\* ln 2) ).

Since a nontrivial cycle has n\* ≥ 7 (Observation B), the bracket exceeds
2 − log₂3 − 1/(21 ln 2) > 0.415 − 0.069 > 1/3. **More than one third of the terms of any
nontrivial cycle are ≡ 3 (mod 4)** — and asymptotically (as n\* → ∞) more than a fraction
2 − log₂3 ≈ 0.41504 of them.

*Proof.* K = Σ k_i ≥ A·1 + (L − A)·2 = 2L − A, so A ≥ 2L − K. By Corollary 2,
K < L·log₂3 + L/(3 n\* ln 2), hence A > L(2 − log₂3) − L/(3 n\* ln 2). The numerical bound uses
n\* ≥ 7 and 1/(21 ln 2) = 0.0687…, 2 − log₂3 = 0.41503… ∎

---

## 7. What is *not* proved here (open edges of this result)

- **Class 2 (mod 3) is not excluded.** All terms ≡ 2 (mod 3) is equivalent (by Lemma 1(2)) to all
  k_i odd; the identity only forces 3^L < 2^K ≤ (3 + 1/7)^L then, i.e. K/L ∈ (log₂3, log₂(22/7)],
  which is a nonempty window (≈ (1.585, 1.652]). Whether a nontrivial cycle can lie entirely in
  2 (mod 3) remains open; we make no claim.
- **The continued-fraction refinement is not claimed.** Corollary 2 shows K/L approximates log₂3
  to within 1/(3 n\* ln 2), but concluding that K/L must be a convergent or intermediate fraction
  of log₂3 requires an inequality of the shape K/L − log₂3 < 1/(2L²), i.e. a lower bound on n\*
  *in terms of L*, which this note does not establish. We state only what Corollary 2 proves.
- **Existence.** None of the above rules out nontrivial cycles; it constrains where they can live
  (mixed mod 4, avoiding 0 and 1 mod 3 as a whole class, with a ≥ 1/3 density of terms ≡ 3 mod 4
  and K pinned in (L·log₂3, 2L−1]).

---

## 8. The theorem in one paragraph

**Cycle-Congruence Theorem.** Let C = (n₁, …, n_L) be any cycle of the Syracuse map
S(n) = (3n+1)/2^{v₂(3n+1)} on odd positive integers, let k_i = v₂(3n_i+1) and K = Σ k_i. Then the
exact identity ∏_{i=1}^{L}(3 + 1/n_i) = 2^K holds, with integer form
(2^K − 3^L)·n₁ = Σ_{j=1}^{L} 3^{L−j} 2^{k₁+⋯+k_{j−1}} > 0 and linear form
Σ 2^{k_i} n_{i+1} = 3Σn_i + L; consequently 3^L < 2^K ≤ 4^L with equality on the right only for
the trivial cycle (1). Moreover no cycle whatsoever has all terms ≡ 3 (mod 4) (else K = L and
2^L > 3^L, absurd), any cycle with all terms ≡ 1 (mod 4) is trivial (all k_i ≥ 2 forces
2^K ≥ 4^L ≥ ∏(3+1/n_i) = 2^K, so every factor equals 4 and every term equals 1), no cycle element
is divisible by 3 (S-images are ≡ ±1 mod 3), and any cycle with all terms ≡ 1 (mod 3) is trivial
(the image congruence n_{i+1} ≡ (−1)^{k_i} mod 3 forces all k_i even, reducing to the previous
case); hence every nontrivial cycle mixes both odd classes mod 4, contains a term ≡ 2 (mod 3),
has an exponent vector containing both a 1 and an entry ≥ 2, satisfies the strict bound
L·log₂3 < K ≤ 2L − 1 with 0 < K/L − log₂3 < 1/(3·min(n_i)·ln 2), and has more than one third of
its terms ≡ 3 (mod 4). All proofs are elementary and computation-free; nothing here decides
whether nontrivial cycles exist.
