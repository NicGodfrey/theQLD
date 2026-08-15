# Theory 10 — Explicit infinite families of abc triples of quality > 1: a Pell family with q_k > 1 + 1/(11k) for every k, the exact conditional liminf for (2ⁿ, 3ⁿ, 2ⁿ+3ⁿ), and the fixed-δ barrier

**Scope.** Elementary number theory only; every proof below is self-contained
(Pell recurrences, the binomial theorem, and a lifting-the-exponent lemma proved
from scratch). For coprime positive integers a + b = c, the *quality* is

    q(a, b, c) = log c / log rad(abc),

where rad(m) = ∏_{p | m} p is the radical (product of the distinct prime
divisors) and log is the natural logarithm (q is independent of the base). We
prove three theorems.

- **Theorem A (unconditional).** An explicit infinite family of pairwise-coprime
  triples a_k + b_k = c_k with q(a_k, b_k, c_k) > 1 + log 2 / (2 log c_k)
  ≥ 1 + 1/(11k) > 1 for **every** k ≥ 1 (so k₀ = 1). The radical bound is proved,
  not cited: rad(a_k b_k c_k) < c_k/√2 for all k.
- **Theorem B (unconditional + one conditional sentence).** For the target family
  (2ⁿ, 3ⁿ, 2ⁿ+3ⁿ), n odd: the triple is already pairwise coprime (no reduction
  is needed — this is proved, not assumed), v₅(2ⁿ+3ⁿ) = 1 + v₅(n) exactly,
  q > 1 for every odd n divisible by 25 (an infinite set, with an explicit lower
  bound), liminf q ≥ 1 unconditionally, and liminf q = 1 exactly under the abc
  conjecture. The guessed closed form log 3 / log 6 ≈ 0.6131 is **not** the
  liminf; §3.5 computes where that wrong guess comes from.
- **Theorem C (conditional).** An explicit family with q ≥ 1.1: if infinitely
  many n satisfy a clean, currently undecided hypothesis about the powerful part
  of 2ⁿ − 1, then the triples (1, 2ⁿ−1, 2ⁿ) for those n ≥ 110 all have
  q ≥ 10n/(9n+10) ≥ 1.1.

**Honesty line (read first).** An unconditional infinite family with
q ≥ 1 + δ for a *fixed* δ > 0 — the headline target — is not proved here, and
§5 proves why no honest note can currently contain one: such a family is
*logically equivalent* to a disproof of the abc conjecture (Proposition 5.1).
The strongest unconditional shape achievable today is q > 1 infinitely often
with an explicit rate q − 1 ≥ δ_k → 0, which Theorem A delivers with
δ_k = 1/(11k); the fixed-δ statement is delivered conditionally (Theorem C),
under a hypothesis that is open in both directions but that the abc conjecture
predicts is false. Every numerical value quoted below was recomputed from
scratch and is a proved bound unless explicitly labelled "observed value".

---

## 1. Definitions and two one-line facts

For a positive integer m, v_p(m) is the exponent of the prime p in m, and
rad(m) = ∏_{p | m} p (rad(1) = 1). An **abc triple** is (a, b, c) with
a, b, c ≥ 1, a + b = c, gcd(a, b) = 1.

**Fact 1.1 (pairwise coprimality is automatic).** If a + b = c and
gcd(a, b) = 1, then a, b, c are pairwise coprime.
*Proof.* If p | a and p | c then p | c − a = b, contradicting gcd(a, b) = 1;
symmetrically for p | b, p | c. ∎

**Fact 1.2 (radical is multiplicative on coprimes, and rad(mⁿ) = rad(m)).**
If gcd(u, v) = 1 then rad(uv) = rad(u)·rad(v); for any n ≥ 1,
rad(uⁿ) = rad(u) ≤ u.
*Proof.* Both sides are the product of the same set of primes. ∎

In particular, for any abc triple, rad(abc) = rad(a)·rad(b)·rad(c).

---

## 2. Theorem A: an unconditional infinite family with q > 1 and an explicit rate, valid from k = 1

### 2.1 The family (write the formulas)

Define integer sequences (x_k), (y_k) by

    x₁ = 3,  y₁ = 1,   x_{k+1} = 3x_k + 8y_k,   y_{k+1} = x_k + 3y_k,

equivalently, in closed form (proved in Lemma 2.3),

    x_k = ( (3+2√2)^k + (3−2√2)^k ) / 2,      y_k = ( (3+2√2)^k − (3−2√2)^k ) / (4√2).

The family of triples is

    a_k = 1,     b_k = 8·y_k²,     c_k = x_k²        (k = 1, 2, 3, …).

First members: (1, 8, 9), (1, 288, 289), (1, 9800, 9801), (1, 332928, 332929), …

### 2.2 Theorem A

**Theorem A.** For every k ≥ 1:

1. a_k + b_k = c_k, the three entries are pairwise coprime, and c_{k+1} > c_k
   (so the triples are pairwise distinct and the family is infinite);
2. rad(a_k b_k c_k) ≤ 2·x_k·y_k < c_k / √2  — the proved radical bound;
3. consequently

       q(a_k, b_k, c_k)  >  1 + (log 2) / (2 log c_k)  >  1 + (log 2) / (4k·log(3+2√2))  >  1 + 1/(11k)  >  1.

So this is an explicit infinite family of pairwise-coprime abc triples of
quality strictly greater than 1, with an explicit, proved lower bound
1 + δ_k, δ_k = 1/(11k), valid for **all** k ≥ 1 (k₀ = 1). Numerically
(log 2)/(4 log(3+2√2)) = 0.098304…, so δ_k may also be taken as 0.0983/k.

### 2.3 Proof

**Lemma 2.1 (Pell identity).** x_k² − 8y_k² = 1 for all k ≥ 1.
*Proof.* Induction. k = 1: 9 − 8 = 1. Step: with x = x_k, y = y_k,

    (3x + 8y)² − 8(x + 3y)² = 9x² + 48xy + 64y² − 8x² − 48xy − 72y² = x² − 8y². ∎

Hence a_k + b_k = 1 + 8y_k² = x_k² = c_k: the triples sum correctly.

**Lemma 2.2 (coprimality and growth).** gcd(b_k, c_k) = 1; x_k is odd;
x_{k+1} > x_k ≥ 3 and y_{k+1} > y_k ≥ 1.
*Proof.* Any common divisor of c_k = x_k² and b_k = 8y_k² divides
c_k − b_k = 1. Since a_k = 1, all three pairwise gcds are 1 (or use Fact 1.1).
x_k² = 8y_k² + 1 is odd, hence x_k is odd. Growth: x_{k+1} = 3x_k + 8y_k > x_k
and y_{k+1} = x_k + 3y_k > y_k since x_k, y_k ≥ 1. ∎

**Lemma 2.3 (closed form and size).** The closed forms in §2.1 hold, and
3 ≤ x_k < (3+2√2)^k for all k ≥ 1.
*Proof.* Let α = 3+2√2, β = 3−2√2, so αβ = 1 and 0 < β < 1. Define
X_k = (α^k+β^k)/2, Y_k = (α^k−β^k)/(4√2). Then X₁ = 3, Y₁ = 1, and (X_k, Y_k)
satisfies the same recurrence as (x_k, y_k):

    X_{k+1} = (α·α^k + β·β^k)/2 = 3·(α^k+β^k)/2 + 2√2·(α^k−β^k)/2 = 3X_k + 8Y_k,
    Y_{k+1} = (α·α^k − β·β^k)/(4√2) = 3·(α^k−β^k)/(4√2) + 2√2·(α^k+β^k)/(4√2) = 3Y_k + X_k,

expanding α = 3 + 2√2, β = 3 − 2√2 in the numerators. By induction x_k = X_k,
y_k = Y_k (equivalently, x_k + 2√2·y_k = α^k). Finally
x_k = (α^k + β^k)/2 < (α^k + 1)/2 < α^k since α^k > 1 > β^k. ∎

**Lemma 2.4 (radical bound).** rad(a_k b_k c_k) ≤ 2 x_k y_k < c_k/√2.
*Proof.* Drop subscripts. Since a = 1 and gcd(b, c) = 1 (Lemma 2.2),

    rad(abc) = rad(b)·rad(c) = rad(8y²)·rad(x²) = rad(2y)·rad(x) ≤ 2y·x,

by Fact 1.2 (8y² and 2y have the same prime divisors; x² and x likewise).
From the Pell identity, 8y² = x² − 1 < x², so 2√2·y < x, i.e. y < x/(2√2),
hence 2xy < 2x·x/(2√2) = x²/√2 = c/√2. ∎

**Proof of Theorem A.** Parts 1 and 2 are Lemmas 2.1, 2.2, 2.4. For part 3,
write L = log c_k and h = (log 2)/2. Lemma 2.4 gives
log rad(a_k b_k c_k) < L − h; also 2 | b_k and 3 ≤ x_k gives some odd prime
dividing c_k, so rad(a_k b_k c_k) ≥ 6 and the quality is well defined; hence

    q(a_k, b_k, c_k) = L / log rad > L/(L−h) = 1 + h/(L−h) > 1 + h/L = 1 + (log 2)/(2 log c_k).

By Lemma 2.3, L = 2 log x_k < 2k·log(3+2√2), whence
q > 1 + (log 2)/(4k log(3+2√2)) = 1 + 0.098304…/k > 1 + 1/(11k), since
1/11 = 0.0909… < 0.098304…. ∎

### 2.4 Observed values (sanity check — not part of any proof)

All factorizations below were verified by direct computation.

| k | triple (1, b_k, c_k) | b_k, c_k factored | rad(abc) | observed q | proved bound 1 + 0.0983/k |
|---|---|---|---|---|---|
| 1 | (1, 8, 9) | 2³ ; 3² | 6 | 1.22629 | 1.09830 |
| 2 | (1, 288, 289) | 2⁵3² ; 17² | 102 | 1.22518 | 1.04915 |
| 3 | (1, 9800, 9801) | 2³5²7² ; 3⁴11² | 2310 | 1.18660 | 1.03277 |
| 4 | (1, 332928, 332929) | 2⁷3²17² ; 577² | 58854 | 1.15778 | 1.02458 |
| 5 | (1, 11309768, 11309769) | 2³29²41² ; 3²19²59² | 7997214 | 1.02180 | 1.01966 |
| 6 | (1, 384199200, 384199201) | 2⁵3⁴5²7²11² ; 17²1153² | 45278310 | 1.12130 | 1.01638 |

At k = 5 the proved bound 1.01966 sits just below the observed 1.02180: the
bound is essentially sharp when x_k and y_k happen to be squarefree with no
small prime factors. Note k = 3 is the classical triple 1 + 9800 = 9801.

### 2.5 Remarks on Theorem A

- **Mechanism.** b_k and c_k are *consecutive powerful numbers* (every prime in
  8y² and in x² occurs to exponent ≥ 2). Squares and lifted exponents (§3) are
  the only unconditional machines we possess for making rad(m) ≪ m along an
  infinite sequence, and the Pell equation makes two powerful numbers differ
  by 1 infinitely often. The saving here is the constant factor √2, which is
  why δ_k ≍ 1/log c_k ≍ 1/k.
- **Is lim q_k = 1?** Unconditionally unknown: an upper bound on q_k needs a
  *lower* bound on rad(x_k y_k), i.e. that x_k y_k is not extremely powerful,
  and even "x_k is squarefree for infinitely many k" is open. Under the abc
  conjecture, q_k ≤ 1 + ε for all large k, so (with part 3) q_k → 1.
- The construction and its rate are best possible for this engine: any family
  in which the quality gain comes from a bounded multiplicative saving
  rad ≤ c/C has q ≤ 1 + log C/(log c − log C) → 1.

---

## 3. Theorem B: the target family (2ⁿ, 3ⁿ, 2ⁿ + 3ⁿ), with the liminf computed honestly

Throughout §3, n is **odd**, and

    a_n = 2ⁿ,   b_n = 3ⁿ,   c_n = 2ⁿ + 3ⁿ.

### 3.1 The reduced coprime triple, written explicitly

**Lemma 3.1.** For every n ≥ 1: gcd(2ⁿ, 3ⁿ) = 1; c_n is odd; 3 ∤ c_n;
5 ∤ 2ⁿ·3ⁿ. Hence (2ⁿ, 3ⁿ, 2ⁿ+3ⁿ) is *already pairwise coprime*: the reduced
coprime triple **is** (2ⁿ, 3ⁿ, 2ⁿ+3ⁿ) itself, and no gcd needs to be divided
out. Moreover gcd(c_n, 6) = 1, so

    rad(a_n b_n c_n) = 2·3·rad(c_n) = 6·rad(c_n).

*Proof.* gcd(2ⁿ, 3ⁿ) = 1 is clear; pairwise coprimality then follows from
Fact 1.1. c_n = even + odd is odd; if 3 | c_n then 3 | c_n − 3ⁿ = 2ⁿ, false;
5 ∤ 2ⁿ·3ⁿ since 2 and 3 are the only primes dividing it. Oddness and 3 ∤ c_n
give gcd(c_n, 6) = 1, and the radical formula is Fact 1.2 applied to the
pairwise coprime factors 2ⁿ, 3ⁿ, c_n. ∎

(The only "algebraic factor to divide out" one could mean is the factor 5 of
c_n for odd n, coming from 2 + 3 = 5; it divides c only, so it never violates
coprimality. Its exact contribution is computed next.) Explicitly, the triple
in fully reduced form is

    2ⁿ + 3ⁿ = 5^{1+v₅(n)} · m_n,   with 5 ∤ m_n, m_n ∈ ℤ≥1,   triple = (2ⁿ, 3ⁿ, 5^{1+v₅(n)}·m_n),

where the 5-adic valuation is exact by the next lemma.

### 3.2 The lifting-the-exponent lemma, proved in full

**Lemma 3.2 (LTE, sufficient generality).** Let p be an odd prime and A, B
integers with p | A − B and p ∤ AB. Then for every m ≥ 1:

    v_p(A^m − B^m) = v_p(A − B) + v_p(m).

*Proof.* Three steps.

*(i) p ∤ m case.* A^m − B^m = (A − B)·S with S = Σ_{i=0}^{m−1} A^i B^{m−1−i}.
Modulo p, A ≡ B, so S ≡ m·A^{m−1} (mod p), and p ∤ m, p ∤ A give p ∤ S. Hence
v_p(A^m − B^m) = v_p(A − B).

*(ii) exponent p step: v_p(A^p − B^p) = v_p(A − B) + 1.* Write A = B + t·p^α
with α = v_p(A − B) ≥ 1 and p ∤ t. By the binomial theorem,

    A^p − B^p = Σ_{i=1}^{p} C(p, i)·B^{p−i}·t^i·p^{αi}.

The i = 1 term is p^{α+1}·B^{p−1}·t, of exact valuation α + 1 (p ∤ Bt).
The i = 2 term has valuation ≥ v_p(C(p,2)) + 2α = 1 + 2α ≥ α + 2, using that
p | C(p,2) = p(p−1)/2 for odd p, and 2α ≥ α + 1. Every term with i ≥ 3 has
valuation ≥ αi ≥ 3α ≥ α + 2. So the sum has exact valuation α + 1.

*(iii) general m.* Write m = p^j·m′ with p ∤ m′. Iterating (ii) j times gives
v_p(A^{p^j} − B^{p^j}) = v_p(A − B) + j, noting at each stage that the new pair
(A^{p^i}, B^{p^i}) still satisfies the hypotheses (p divides their difference
by construction; p divides neither). Then (i) applied to the pair
(A^{p^j}, B^{p^j}) with exponent m′ finishes:
v_p(A^m − B^m) = v_p(A^{p^j} − B^{p^j}) = v_p(A − B) + j = v_p(A−B) + v_p(m). ∎

**Corollary 3.3 (exact 5-adic valuation).** For every odd n ≥ 1:

    v₅(2ⁿ + 3ⁿ) = 1 + v₅(n).

*Proof.* Apply Lemma 3.2 with p = 5, A = 2, B = −3, m = n: A − B = 5, so
v₅(A − B) = 1, and p ∤ AB = −6. Since n is odd, Aⁿ − Bⁿ = 2ⁿ − (−3)ⁿ = 2ⁿ + 3ⁿ. ∎

(Verified by direct computation for all odd n ≤ 401.)

### 3.3 Theorem B

**Theorem B.** For odd n, write q_n = q(2ⁿ, 3ⁿ, 2ⁿ+3ⁿ) and v = v₅(n). Then:

1. **(General radical bound and trivial floor.)**
   rad(a_n b_n c_n) = 6·rad(c_n) ≤ 6·c_n·5^{−v}, and consequently

       q_n ≥ log c_n / log(6 c_n) = 1 − log 6 / log(6 c_n)          (all odd n),
       q_n ≥ log c_n / ( log c_n + log 6 − v·log 5 )                 (all odd n).

2. **(An infinite proved subfamily with q > 1.)** If 25 | n (i.e. v ≥ 2) then
   q_n > 1; explicitly, for odd n with v = v₅(n) ≥ 2,

       q_n  >  1 + ( v·log 5 − log 6 ) / ( n·log 3 + log 12 )  >  1.

   The set {n odd : 25 | n} = {25, 75, 125, 175, …} is infinite, so this is an
   infinite family of pairwise-coprime triples of quality > 1. The smallest
   member, n = 25, has the proved bound q₂₅ ≥ 1.05481 (see §3.4).

3. **(The liminf, computed honestly.)** Unconditionally,

       liminf_{n → ∞, n odd} q_n ≥ 1,

   and no unconditional finite upper bound on this liminf is known. Under the
   abc conjecture, lim_{n → ∞, n odd} q_n = 1; hence, conditionally, the exact
   closed form is

       liminf_{n odd} q_n = 1.

*Proof.*

(1) By Lemma 3.1, rad(a_n b_n c_n) = 6 rad(c_n). By Corollary 3.3,
c_n = 5^{1+v}·m_n with 5 ∤ m_n, so rad(c_n) = 5·rad(m_n) ≤ 5·m_n =
5·c_n/5^{1+v} = c_n·5^{−v} ≤ c_n. Taking logarithms in
rad(a b c) ≤ 6 c_n 5^{−v} ≤ 6c_n and dividing log c_n by them gives the two
displayed lower bounds (the denominators are ≥ log 30 > 0).

(2) From (1), q_n ≥ 1 + (v log 5 − log 6)/(log c_n + log 6 − v log 5). For
v ≥ 2 the numerator is 2 log 5 − log 6 = log(25/6) > 0. The denominator is
positive and, since v log 5 > 0 and c_n < 2·3ⁿ,

    log c_n + log 6 − v log 5 < n log 3 + log 2 + log 6 = n log 3 + log 12,

which yields the displayed bound, strictly greater than 1. Since also
rad(abc) ≤ (6/25)c_n < c_n, indeed q_n > 1.

(3) *Lower half (unconditional).* By (1), q_n ≥ 1 − log 6/log(6 c_n) and
c_n > 3ⁿ → ∞, so for every ε > 0 and all large odd n, q_n ≥ 1 − ε. Hence
liminf ≥ 1. *Why no unconditional upper bound:* an upper bound on q_n needs a
lower bound on rad(c_n); the strongest known unconditional lower bounds on
rad(2ⁿ+3ⁿ) (via primitive prime divisors or linear forms in logarithms — cited
as context only, not used anywhere in this note) are of polynomial size in n,
whereas log c_n ≍ n; a bound rad(c_n) ≥ c_n^θ for infinitely many n with some
fixed θ > 0 is far beyond current techniques. *Upper half (under abc).* The abc
conjecture states: for every ε > 0, only finitely many coprime triples satisfy
c > rad(abc)^{1+ε}. The triples here are pairwise distinct (c_n is strictly
increasing), so for every ε > 0 all but finitely many odd n have
q_n ≤ 1 + ε, i.e. limsup q_n ≤ 1. Combined with liminf ≥ 1, the limit exists
and equals 1, so liminf = 1. ∎

### 3.4 Observed values (sanity check — not part of any proof)

The "proved bound" column is the second bound of Theorem B.1,
log c_n / (log c_n + log 6 − v·log 5), which is fully proved for every odd n
via Corollary 3.3.

| n | v₅(n) | c_n factored | observed q_n | proved lower bound |
|---|---|---|---|---|
| 1 | 0 | 5 | 0.47320 | 0.47320 (attained) |
| 3 | 0 | 5·7 | 0.66491 | 0.66491 (attained) |
| 5 | 1 | 5²·11 | 0.96856 | 0.96856 (attained) |
| 15 | 1 | 5²·7·11·31·241 | 0.98906 | 0.98906 (attained) |
| 25 | 2 | 5³·11·1201·513101 | 1.05481 | **1.05481** (attained; > 1 since v = 2) |
| 75 | 2 | (not factored; not needed) | — | 1.01763 |

For n = 25: c = 847322163875 = 5³·11·1201·513101, so rad(abc) =
6·5·11·1201·513101 = 203357319330 and q = log c/log rad = 1.054808…; the
proved bound log c/(log 6 + log c − 2 log 5) equals the observed value because
c/5³ is squarefree — the inequality of Theorem B.1 is attained (likewise in
the rows marked "attained", where c_n/5^{1+v} happens to be squarefree).

### 3.5 Where the wrong guess log 3 / log 6 comes from

If one erroneously writes rad(2ⁿ·3ⁿ) = 6ⁿ instead of the correct
rad(2ⁿ·3ⁿ) = 6 (Fact 1.2), one gets the fake asymptotics
q_n "≈" log 3ⁿ / log 6ⁿ = log 3/log 6 = 0.613147…. The radical destroys
exponents; that is the entire point of the abc quality. The correct closed
form for the conditional liminf is 1 (Theorem B.3), approached from below
along generic odd n (observed values above) and exceeded infinitely often
(25 | n, part 2). Every statement of Theorem B about this family that can be
made unconditional has been made unconditional; the single conditional
sentence (lim = 1 under abc) is labelled as such.

---

## 4. Theorem C: a conditional infinite family with q ≥ 1.1

### 4.1 Powerful part

For m ≥ 1 write m = κ(m)·s(m) where κ(m) = ∏_{p : v_p(m) ≥ 2} p^{v_p(m)} (the
**powerful part**) and s(m) = ∏_{p : v_p(m) = 1} p (squarefree,
gcd(κ, s) = 1).

**Lemma 4.1.** rad(m) ≤ m / √κ(m).
*Proof.* rad(m) = rad(κ(m))·s(m). Every prime in κ = ∏ p^{e_p} has e_p ≥ 2, so
p ≤ p^{e_p/2} and rad(κ) ≤ κ^{1/2}. Hence rad(m) ≤ κ^{1/2} s = (κ s)/κ^{1/2}
= m/√κ(m). ∎

### 4.2 The hypothesis and the theorem

**Hypothesis H.** There are infinitely many integers n ≥ 1 with
κ(2ⁿ − 1) ≥ 2^{n/5}.

**Theorem C.** Let n satisfy κ(2ⁿ − 1) ≥ 2^{n/5}. Then (1, 2ⁿ−1, 2ⁿ) is a
pairwise-coprime abc triple with

    q(1, 2ⁿ−1, 2ⁿ)  ≥  10n / (9n + 10),

which is increasing in n, equals 1.1 at n = 110, and tends to 10/9 = 1.111….
Hence: **if Hypothesis H holds, there are infinitely many pairwise-coprime abc
triples of quality ≥ 1.1** (all n ≥ 110 in H work; δ = 0.1 is fixed and
explicit). More generally, replacing 2^{n/5} by 2^{θn} (0 < θ ≤ 1) gives
q ≥ n/(n(1 − θ/2) + 1) → 1/(1 − θ/2).

*Proof.* Coprimality: gcd(2ⁿ−1, 2ⁿ) = 1 and Fact 1.1. Radical: with
b = 2ⁿ − 1 odd,

    rad(1·b·2ⁿ) = 2·rad(b) ≤ 2·b/√κ(b) ≤ 2·2ⁿ·2^{−n/10} = 2^{9n/10 + 1}

by Lemma 4.1 and κ(b) ≥ 2^{n/5}. Hence

    q = log 2ⁿ / log rad(abc) ≥ (n log 2) / ((9n/10 + 1) log 2) = 10n/(9n+10).

Monotonicity: d/dn [10n/(9n+10)] = 100/(9n+10)² > 0; at n = 110 the value is
1100/1000 = 1.1. The θ-version is the same computation with 2^{−θn/2} in place
of 2^{−n/10}. ∎

### 4.3 Status of Hypothesis H — stated with full honesty

- **H is open in both directions.** Nobody can prove there are infinitely many
  such n, and nobody can prove there are finitely many. Even the far weaker
  question "is 2ⁿ − 1 squarefree for infinitely many n?" is open. What *is*
  known: κ(2ⁿ − 1) > 1 for infinitely many n (e.g. 1093² | 2ⁿ − 1 whenever
  364 | n, from the Wieferich prime 1093), but such constructions give only
  bounded powerful parts, nowhere near 2^{n/5}.
- **Small cases meeting the inequality (observed, not asymptotic evidence):**
  n = 6 (2⁶−1 = 63 = 3²·7, κ = 9 ≥ 2^{1.2} = 2.30), n = 20 (κ = 5² = 25 ≥ 2⁴),
  n = 21 (κ = 7² = 49 ≥ 2^{4.2}). These lie below the threshold n ≥ 110, so
  they certify only the mechanism, not the conclusion q ≥ 1.1 (observed
  qualities: 1.1127, 1.0708, 1.0942 respectively — the first exceeds 1.1 by
  luck of small numbers).
- **Why a powerful-part hypothesis and not a primality hypothesis.** Assuming
  some cofactor is *prime* makes the radical large and the quality small, and
  Wieferich-type square conditions (p² | 2^{p−1} − 1) save only O(log p)
  against log c ≍ p — both dead ends for fixed δ. A fixed δ needs a powerful
  part of size c^{Ω(1)}, so the hypothesis must say exactly that; H is the
  cleanest such statement for this family.
- **The abc conjecture implies H is false**: under abc, only finitely many
  triples have q ≥ 1.1 = 1 + 0.1, while H would produce infinitely many
  (Theorem C). So Theorem C is expected to be vacuously true. §5 shows this
  vacuity is *forced*: every correct theorem of the requested fixed-δ form
  must have an abc-refuting hypothesis.

---

## 5. The fixed-δ barrier: why Theorems A and C are the honest maximum

**Proposition 5.1.** The following are equivalent.
(i) There exists δ > 0 and an infinite set of pairwise-coprime abc triples
with q(a, b, c) ≥ 1 + δ.
(ii) The abc conjecture (∀ε > 0, only finitely many coprime triples have
c > rad(abc)^{1+ε}) is false.

*Proof.* (i) ⇒ (ii): every triple in the family has c ≥ rad^{1+δ} >
rad^{1+δ/2} (strict since rad(abc) ≥ 2 whenever c ≥ 2: some prime divides bc).
Infinitely many distinct triples violate the abc bound at ε = δ/2, so abc
fails. (ii) ⇒ (i): if abc fails at some ε₀ > 0, the infinitely many triples
with c > rad^{1+ε₀} all have q > 1 + ε₀; take δ = ε₀. ∎

Consequently, a proof of the headline target "explicit infinite family with
q ≥ 1 + δ, fixed explicit δ > 0" *is* a disproof of the abc conjecture. No
such proof is claimed here. Quantitatively, the engines used above cannot even
approach it:

- **LTE / cyclotomic repetition (Theorem B)** manufactures a prime power
  p^{1+v_p(n)} inside c_n; the radical saving is v_p(n)·log p = O(log n),
  against log c_n ≍ n. Gain: q − 1 = O(log n / n) → 0.
- **Pell squares (Theorem A)** manufacture *all* primes of bc squared; the
  saving is the constant log √2. Gain: q − 1 ≍ 1/log c → 0.
- Fixed δ needs a saving of size δ·log c, i.e. a powerful part of bc of size
  c^{Ω(1)} along an infinite family — exactly what Hypothesis H postulates and
  what no unconditional method produces. (For context only: the best known
  unconditional savings, by Stewart–Tijdeman-type constructions, are of size
  exp(C√(log c/log log c)), still giving q → 1. They are not used, and not
  needed, anywhere above.)

Algebraic factorizations by themselves (e.g. 8ⁿ + 1 = (2ⁿ+1)(4ⁿ−2ⁿ+1), or
Aurifeuillian factors) can never help: they split c into coprime factors whose
radicals multiply back (Fact 1.2), leaving log rad unchanged unless a factor
is repeated. Only *multiplicity* — squares and lifted exponents — reduces a
radical, which is why Theorems A–C are built exclusively from multiplicity.

---

## 6. The theorem, in one paragraph

**Theorem (quality family; unconditional except the two clauses flagged).**
Define x₁ = 3, y₁ = 1, x_{k+1} = 3x_k + 8y_k, y_{k+1} = x_k + 3y_k — equivalently
x_k + 2√2·y_k = (3+2√2)^k — and set (a_k, b_k, c_k) = (1, 8y_k², x_k²). Then for
every k ≥ 1: a_k + b_k = c_k, the entries are pairwise coprime, x_k² − 8y_k² = 1,
rad(a_k b_k c_k) = rad(2y_k)·rad(x_k) ≤ 2x_k y_k < c_k/√2, and therefore
q(a_k, b_k, c_k) > 1 + (log 2)/(2 log c_k) > 1 + 1/(11k) > 1, so the pairwise-coprime
abc triples (1, 8y_k², x_k²), k = 1, 2, 3, …, form an explicit infinite family of
quality strictly exceeding 1 with the explicit proved rate δ_k = 1/(11k) valid from
k₀ = 1 (first members (1,8,9), (1,288,289), (1,9800,9801), of qualities 1.2263,
1.2252, 1.1866). For the target family (2ⁿ, 3ⁿ, 2ⁿ+3ⁿ) with n odd — which is
already pairwise coprime, so it is its own reduced triple — the lifting-the-exponent
lemma gives exactly v₅(2ⁿ+3ⁿ) = 1 + v₅(n), hence rad(2ⁿ·3ⁿ·(2ⁿ+3ⁿ)) ≤
6·(2ⁿ+3ⁿ)·5^{−v₅(n)}, so q_n > 1 + (v₅(n)·log 5 − log 6)/(n log 3 + log 12) > 1 for
every odd n divisible by 25 (an infinite set; at n = 25 the proved bound is
q ≥ 1.05481, attained), while unconditionally liminf_{n odd} q_n ≥ 1 with no
unconditional upper bound known, and — flagged conditional clause one — under the
abc conjecture lim q_n = 1, so the liminf is exactly 1 and not log 3/log 6, which
arises only from the false identity rad(2ⁿ3ⁿ) = 6ⁿ. Finally — flagged conditional
clause two — if infinitely many n satisfy κ(2ⁿ−1) ≥ 2^{n/5} (κ = powerful part;
a hypothesis open in both directions), then rad(2ⁿ(2ⁿ−1)) ≤ 2^{9n/10+1} for those n
and the coprime triples (1, 2ⁿ−1, 2ⁿ) with n ≥ 110 all satisfy
q ≥ 10n/(9n+10) ≥ 1.1, an infinite family with fixed δ = 0.1; no unconditional
theorem of this fixed-δ form can be given by anyone at present, because such a
family is logically equivalent (Proposition 5.1) to a disproof of the abc
conjecture — and that equivalence, not a defect of the method, is the honest
boundary of this note.
