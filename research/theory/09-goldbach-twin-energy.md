# 09 — The Goldbach–Twin Energy Identity: Goldbach Energy Equals Prime-Pair Energy, Exactly

**Status: original theory. Every unconditional claim below is proved in full in this file.
Conditional claims are labelled as such, with the hypothesis displayed.**

**Honesty line.** This note proves an *exact finite identity* — the ℓ² energy of the (weighted,
truncated) Goldbach representation function equals the ℓ² energy of the (weighted, truncated)
prime-pair correlation function — together with an exact variance identity, an unconditional
evaluation of both Hardy–Littlewood main-term energies to a common constant (c₂/3)N³ with
c₂ = 4∏_{p>2}(1 + (p−1)⁻³) = 4.60192…, and a two-way L² transfer between Goldbach regularity and
twin-pair statistics with explicit constants. **No claim of binary Goldbach is made.** The precise
reason L² information cannot yield binary Goldbach is itself proved below (Lemma 7: the 3/c₂
support barrier). This note does **not** rewrite the Wave-2 modulus barrier
(`research/conjectures/09-goldbach/REPORT.md`: minor-arc L² mass (1+o(1))·N log N versus main term
𝔖(n)n ≍ n); it is logically independent of it and sits on the *other* side of Parseval: instead of
bounding minor-arc mass, it equates two physical-side energies exactly.

---

## 1. Setup: exact definitions and truncations

Throughout, p, q denote primes, e(x) = e^{2πix}, and log is natural. Fix an integer N ≥ 2
(N need not be even; "even N" is never assumed).

**Prime weight.** θ(n) = log n if n is prime, θ(n) = 0 otherwise. Write Θ(N) = Σ_{m≤N} θ(m)
(Chebyshev's function; by the Prime Number Theorem Θ(N) = (1+o(1))N, and by Chebyshev's elementary
estimate Θ(N) ≤ C₀N with an absolute constant, valid for all N ≥ 2).

**The exponential sum.** S(α) = Σ_{m=1}^{N} θ(m) e(mα), a trigonometric polynomial of degree N.

**Truncated Goldbach function.** For 2 ≤ n ≤ 2N,

  R_N(n) = Σ_{m: 1≤m≤N, 1≤n−m≤N} θ(m) θ(n−m) = Σ_{m=max(1,n−N)}^{min(N,n−1)} θ(m) θ(n−m).

This is the precise truncation required for exactness: *both* summands are restricted to [1, N].
For 2 ≤ n ≤ N+1 the constraints m ≤ N and n−m ≤ N are automatic, so R_N(n) coincides exactly with
the untruncated R(n) = Σ_{m=1}^{n−1} θ(m)θ(n−m); for N+1 < n ≤ 2N it is a genuine truncation.
R_N(n) > 0 if and only if n = p + q with primes p, q ≤ N.

**Truncated prime-pair (twin) function.** For 0 ≤ h ≤ N−1,

  T_N(h) = Σ_{m=1}^{N−h} θ(m) θ(m+h),  and T_N(−h) = T_N(h).

Again the truncation is that *both* members of the pair lie in [1, N]; T_N(h) is defined for
|h| ≤ N−1 and vanishes identically beyond. T_N(0) = Σ_{p≤N} log²p. For even h ≥ 2, T_N(h) is the
weighted count of prime pairs at distance h ("generalized twins"); h = 2 is the twin case.

**Slot counts (these matter).** R_N lives on {2, 3, …, 2N}: exactly **2N − 1** slots.
T_N lives on {−(N−1), …, N−1}: exactly **2N − 1** slots. The two index sets have the same
cardinality. This is not decorative; it is what makes Corollary 1.2 exact.

**Main terms.** Let C₂ = ∏_{p>2}(1 − (p−1)⁻²) = 0.66016… (twin prime constant) and, for even
m ≥ 2,

  𝔖(m) = 2C₂ ∏_{p|m, p>2} (p−1)/(p−2),  𝔖(m) = 0 for odd m.

The interval-length function ℓ_N(n) = #{m : 1 ≤ m ≤ N, 1 ≤ n−m ≤ N} = min(n−1, 2N+1−n) (a tent
peaking at n = N+1 with ℓ_N(N+1) = N). The Hardy–Littlewood predictions adapted to our truncations
are

  M_G(n) = 𝔖(n) ℓ_N(n)  (even n, 2 ≤ n ≤ 2N),  M_T(h) = 𝔖(|h|)(N − |h|)  (even h, 0 < |h| < N).

These are hypotheses' reference points, never assumed true; every use is displayed.

---

## 2. The exact identity

**Theorem 1 (Goldbach–twin energy identity; exact, all N ≥ 2).**

  Σ_{n=2}^{2N} R_N(n)² = Σ_{h=−(N−1)}^{N−1} T_N(h)² = T_N(0)² + 2 Σ_{h=1}^{N−1} T_N(h)².

Moreover the first moments agree exactly:

  Σ_{n=2}^{2N} R_N(n) = Σ_{|h|≤N−1} T_N(h) = Θ(N)².

*Proof 1 (Fourier/Parseval).* S(α)² = Σ_{m,m'∈[1,N]} θ(m)θ(m')e((m+m')α) = Σ_{n=2}^{2N} R_N(n)e(nα),
and |S(α)|² = S(α)·conj(S(α)) = Σ_{m,m'∈[1,N]} θ(m)θ(m')e((m−m')α) = Σ_{|h|≤N−1} T_N(h)e(hα).
Both are trigonometric polynomials; by orthogonality of the characters e(kα) on [0,1] (Parseval),

  Σ_n R_N(n)² = ∫₀¹ |S(α)²|² dα = ∫₀¹ |S(α)|⁴ dα = ∫₀¹ |(|S(α)|²)|² dα = Σ_h T_N(h)².

The middle step is the tautology |S²| = |S|². The first-moment identity is α = 0:
S(0)² = Θ(N)² equals both Σ_n R_N(n) and Σ_h T_N(h). ∎

*Proof 2 (double counting, no analysis).* Both sides count weighted quadruples
(a, b, c, d) ∈ [1,N]⁴ with weight θ(a)θ(b)θ(c)θ(d). The left side, expanded, runs over quadruples
(m₁, m₂, m₃, m₄) with m₁+m₂ = m₃+m₄ = n, summed over n: the constraint is m₁+m₂ = m₃+m₄. The right
side, expanded, runs over pairs of pairs at common gap h: quadruples (a, a+h, c, c+h), i.e., the
constraint (a+h) − a = (c+h) − c reads b − a = d − c with b = a+h, d = c+h; and b − a = d − c is
equivalent to a + d = b + c. The bijection (m₁, m₂, m₃, m₄) = (a, d, b, c) matches the two
constraint sets and the weights. Same-sum quadruples are same-gap quadruples. ∎

**Interpretation.** "Goldbach energy equals twin-pair energy" is exact, for every N, with no error
term, because both are the fourth moment of the same prime exponential sum — read once on the
*sum* side (convolution) and once on the *difference* side (autocorrelation).

**Corollary 1.2 (exact variance identity).** For **every** constant c ∈ ℝ,

  Σ_{n=2}^{2N} (R_N(n) − c)² = Σ_{|h|≤N−1} (T_N(h) − c)².

In particular, with the common mean μ = Θ(N)²/(2N−1), the empirical variance of the Goldbach
profile over its 2N−1 slots equals the empirical variance of the twin profile over its 2N−1 slots,
exactly.

*Proof.* Expand: Σ(X − c)² = ΣX² − 2cΣX + c²·(#slots). By Theorem 1 the second moments agree and
the first moments agree; the slot counts are both 2N−1 (Section 1). All three ingredients match
term by term, for every c. ∎

**Remark 1.3 (the identity is quadratic and only quadratic).** Third moments do *not* match:
numerically at N = 101, Σ R_N³ / Σ T_N³ = 0.9419 (and 0.9532 at N = 50). Parseval pairs |S²|²
with (|S|²)²; there is no analogous identity for cubes, and none is claimed. Any attempt to
extract *pointwise* (L∞) Goldbach information from Theorem 1 must pass through L², where roots and
signs are invisible; this is quantified honestly in Lemma 7.

---

## 3. Unconditional size of the common energy

Write E(N) = Σ_{n=2}^{2N} R_N(n)² = Σ_{|h|<N} T_N(h)² = ∫₀¹|S|⁴.

**Proposition 2.** Unconditionally,

  (1/2 − o(1)) N³ ≤ E(N) ≤ (1 + o(1)) N³ log N.

*Proof.* Lower: by Cauchy–Schwarz over the 2N−1 slots and Theorem 1's first-moment identity,
E(N) ≥ (Σ_n R_N(n))²/(2N−1) = Θ(N)⁴/(2N−1) = (1/2 − o(1))N³, using Θ(N) = (1+o(1))N (PNT).
Upper: E(N) = ∫₀¹|S|⁴ ≤ (sup_α |S(α)|²)·∫₀¹|S|² = Θ(N)² · Σ_{m≤N}θ(m)², and
Σ_{m≤N}θ(m)² = Σ_{p≤N}log²p ≤ (log N)·Θ(N), so E(N) ≤ Θ(N)³ log N = (1+o(1))N³ log N. ∎

**Remark 3.1 (what is classical here).** With a Selberg-sieve upper bound
T_N(h) ≪ 𝔖(h)N (h ≠ 0) and Lemma 3(ii) below, the upper bound improves to E(N) ≍ N³; this is the
classical "additive energy of the primes is ≍ N³" and we do not reproduce the sieve proof.
Proposition 2 is included because it is fully self-contained (PNT only) and already pins E(N) to
within one logarithm.

**Remark 3.2 (unconditional twin-energy lower bound, for free).** Since
T_N(0)² ≤ (Θ(N)log N)² ≪ N²log²N, Theorem 1 + Proposition 2 give, unconditionally,
Σ_{0<|h|<N} T_N(h)² ≥ (1/2 − o(1))N³ — at least 32.6% of the Hardy–Littlewood prediction
(c₂/3)N³ = 1.53397…N³ computed in Section 5. The derivation is one line, and we make no novelty
claim for it; it is recorded because it is the honest unconditional floor under everything below.

---

## 4. Singular series moments (proved in full)

**Lemma 3.** As K → ∞:

  (i) Σ_{k≤K} 𝔖(2k) = 2K + O(log K);
  (ii) Σ_{k≤K} 𝔖(2k)² = c₂K + O(log²K),  where c₂ = 4 ∏_{p>2} (1 + (p−1)⁻³) = 4.6019230….

*Proof.* Let g be the multiplicative function supported on odd squarefree integers with
g(p) = 1/(p−2) for p > 2, g(1) = 1. Since p | 2k with p > 2 iff p | k, the Euler product gives
𝔖(2k) = 2C₂ ∏_{p|k, p>2}(1 + 1/(p−2)) = 2C₂ Σ_{d|k} g(d), the sum over odd squarefree divisors.

(i) Σ_{k≤K}𝔖(2k) = 2C₂ Σ_d g(d)⌊K/d⌋. Terms with d > K vanish. Write ⌊K/d⌋ = K/d − {K/d}:

  Σ_{k≤K}𝔖(2k) = 2C₂[ K·Σ_{d} g(d)/d − K·Σ_{d>K} g(d)/d − Σ_{d≤K} g(d){K/d} ].

Main term: Σ_d g(d)/d = ∏_{p>2}(1 + 1/(p(p−2))), and per prime
(1 + 1/(p(p−2)))(1 − 1/(p−1)²) = [(p(p−2)+1)/(p(p−2))]·[p(p−2)/(p−1)²] = (p−1)²/(p−1)² = 1,
using p(p−2)+1 = (p−1)². Hence Σ_d g(d)/d = 1/C₂ and the main term is 2K.
Errors: G₁(x) := Σ_{d≤x} g(d) ≤ ∏_{p≤x}(1 + 1/(p−2)) ≤ exp(Σ_{p≤x} 1/(p−2)) ≪ log x by Mertens;
so the fractional-part sum is O(log K), and by partial summation
Σ_{d>K} g(d)/d = G₁(t)/t |_{t=K}^{∞} + ∫_K^∞ G₁(t)t⁻²dt ≪ (log K)/K, so the tail term is O(log K).

(ii) 𝔖(2k)² = 4C₂² Σ_{d₁,d₂} g(d₁)g(d₂)[lcm(d₁,d₂) | k]. Grouping by L = lcm(d₁,d₂) defines the
multiplicative function h(L) = Σ_{lcm(d₁,d₂)=L} g(d₁)g(d₂), supported on odd squarefree L, with
h(p) = 2g(p) + g(p)² = (2p−3)/(p−2)². Then

  Σ_{k≤K}𝔖(2k)² = 4C₂² Σ_L h(L)⌊K/L⌋ = 4C₂²[ K·Σ_L h(L)/L + O(Σ_{L≤K}h(L)) + O(K·Σ_{L>K}h(L)/L) ].

Main term: Σ_L h(L)/L = ∏_{p>2}(1 + (2p−3)/(p(p−2)²)), so c₂ = 4 ∏_{p>2} A_p with
A_p = (1 − 1/(p−1)²)²·(1 + (2p−3)/(p(p−2)²)). We claim A_p = 1 + 1/(p−1)³. Indeed
(1 − 1/(p−1)²)² = p²(p−2)²/(p−1)⁴, so A_p = p·[p(p−2)² + 2p − 3]/(p−1)⁴, and
p(p−2)² + 2p − 3 = p³ − 4p² + 6p − 3 = (p−1)(p² − 3p + 3), while
(p−1)⁴·(1 + 1/(p−1)³) = (p−1)⁴ + (p−1) = (p−1)(p³ − 3p² + 3p) = (p−1)·p·(p² − 3p + 3).
The two agree, proving the closed form. Errors: h(p) = 2/p + O(1/p²), so
H(x) := Σ_{L≤x}h(L) ≤ ∏_{p≤x}(1 + h(p)) ≪ exp(2 log log x + O(1)) ≪ log²x, giving the middle error
O(log²K); partial summation gives Σ_{L>K}h(L)/L ≪ (log²K)/K, giving the last error O(log²K). ∎

Numerical check (2·10⁵ terms): empirical mean of 𝔖(2k) is 1.999965; empirical mean of 𝔖(2k)² is
4.601569, versus c₂ = 4.6019230894 (the deficit is the proven O(log²K/K)).

**Remark 4.1.** c₂ > 4 = (mean of 𝔖(2k))², strictly: the singular series has genuine variance, and
c₂/3 = 1.533974…, 3/c₂ = 0.651901…, √(3/c₂) = 0.807404… are the constants used below.

---

## 5. The main terms conserve the identity (unconditional consistency)

**Theorem 4 (main-term energy consistency).** Unconditionally,

  Σ_{even n, 2≤n≤2N} M_G(n)² = (c₂/3)N³ + O(N²log²N),
  Σ_{even h, 0<|h|<N} M_T(h)² = (c₂/3)N³ + O(N²log²N),

so the Hardy–Littlewood predictions for the two sides of Theorem 1 carry *identical* leading
energy (c₂/3)N³ = (1.533974…)N³. The tent profile ℓ_N(n) (Goldbach) and the triangle profile
N−|h| (twins) are exactly energy-balanced against each other.

*Proof.* Summation by parts. If A(k) = Σ_{j≤k}a_j = ck + r(k) with |r(k)| ≤ ρ for k ≤ K, and
w₁,…,w_K ≥ 0, then Σ_{k≤K} a_k w_k = c Σ_{k≤K} w_k + O(ρ·(w_K + Σ_{k<K}|w_k − w_{k+1}|)).

Goldbach side: a_k = 𝔖(2k)², K = N, w_k = ℓ_N(2k)². By Lemma 3(ii), ρ ≪ log²N. Here w_N = 1 and
|w_k − w_{k+1}| ≤ (ℓ_N(2k) + ℓ_N(2k+2))·|ℓ_N(2k) − ℓ_N(2k+2)| ≤ 2N·2, so the variation term is
O(N²log²N). The pure tent sum is elementary: ℓ_N(2k) = min(2k−1, 2N+1−2k) runs over odd values up
and back down, and Σ_{k=1}^{N} ℓ_N(2k)² = N³/3 + O(N²) (for even N it is exactly N(N²−1)/3).
Multiplying by c₂ gives (c₂/3)N³ + O(N²log²N).

Twin side: Σ_{even h, 0<|h|<N} M_T(h)² = 2 Σ_{1≤j≤⌈N/2⌉−1} 𝔖(2j)²(N−2j)². Same partial summation
with w_j = (N−2j)²: w has total variation O(N²), and 2 Σ_j (N−2j)² = 2·(N³/12 + O(N²))·4/2 —
explicitly, Σ_{1≤j≤⌈N/2⌉−1}(N−2j)² = 4Σ_{t≤N/2−1+O(1)} t² + O(N²) = N³/6 + O(N²) — so the doubled
sum is N³/3 + O(N²), and with the c₂ density: (c₂/3)N³ + O(N²log²N). ∎

Numerical check at N = 20000: ‖M_G‖²/((c₂/3)N³) = 0.999826, ‖M_T‖²/((c₂/3)N³) = 0.997501.

**Remark 5.1.** Theorem 4 is a nontrivial *consistency theorem*: the exact identity of Theorem 1
forces any pair of correct main terms to be equienergetic, and the Hardy–Littlewood pair passes
this test with the same constant c₂/3 emerging from two different integrals
(∫ tent² against the 𝔖²-density, ∫ triangle² against the same density). Had these disagreed, at
least one of the two Hardy–Littlewood predictions would be false. They agree.

---

## 6. Transfer I: Goldbach flatness pins and shapes the twin profile

Define the Goldbach L² deviation over the exactly N even slots n ∈ {2, 4, …, 2N}:

  D(N)² = Σ_{even n, 2≤n≤2N} ( R_N(n) − 𝔖(n)ℓ_N(n) )².

Hypotheses (never asserted, always displayed):

  (GF₂):  D(N)² = o(N³).
  (GF∞):  max_{even n ≤ 2N} |R_N(n) − 𝔖(n)ℓ_N(n)| = o(N).

Since there are N even slots, (GF∞) ⟹ D(N)² ≤ N·o(N²) = o(N³) ⟹ (GF₂). (This is the *only* free
direction between L∞ and L²; see Lemma 7 for the converse's failure.)

Two unconditional bookkeeping bounds, proved now and reused silently:

**Lemma 5.0 (parity bookkeeping).** Unconditionally,
(a) Σ_{odd n ≤ 2N} R_N(n)² ≪ N log N and Σ_{odd n} R_N(n) ≪ N;
(b) Σ_{odd h, |h|<N} T_N(h)² ≪ N log N and Σ_{odd h} T_N(h) ≪ N;
(c) T_N(0)² ≪ N² log²N.

*Proof.* (a) If n is odd and n = m + m' with θ(m)θ(m') ≠ 0, one of m, m' is the only even prime 2;
so R_N(n) = 2θ(2)θ(n−2) ≤ (2 log 2)log 2N, nonzero only when n−2 is prime, i.e., for
O(N/log N) values of n. Hence Σ R_N² ≪ (N/log N)·log²(2N) ≪ N log N and Σ R_N ≪ N. (b) Same
argument: odd gap forces m = 2, T_N(h) = θ(2)θ(2+|h|) for odd h. (c) T_N(0) = Σ_{p≤N} log²p ≤
Θ(N)log N ≪ N log N by Chebyshev. ∎

**Theorem 5 (flatness transfer with explicit constants).**

**(a) Energy pinning.** Assume (GF₂). Then

  Σ_{0<|h|<N} T_N(h)² = (c₂/3)N³ + o(N³),  and Σ_{even h, 0<h<N} T_N(h)² = (c₂/6)N³ + o(N³).

**(b) Explicit contrapositive (the requested inequality).** For any fixed ε ∈ (0, 2c₂], if

  | Σ_{0<|h|<N} T_N(h)² − (c₂/3)N³ | ≥ εN³

for some N ≥ N₀(ε), then

  max_{even n ≤ 2N} | R_N(n) − 𝔖(n)ℓ_N(n) | ≥ (√(3/c₂)/6)·εN·(1−o(1)) ≥ 0.134·εN.

In words: the weighted Goldbach counts cannot stay within o(N) — a fortiori within
o(N/polylog N) — of the Hardy–Littlewood prediction unless the twin-pair energy equals the
Hardy–Littlewood value (c₂/3)N³ exactly to leading order. The deviation forced is of order N,
i.e., of the order of the main term divided by a constant, not merely N/polylog.

**(c) Twin non-uniformity.** Assume (GF₂). Let 𝓗 = {even h : 0 < h < N}, M = |𝓗| = ⌊(N−1)/2⌋,
and let T̄ = M⁻¹Σ_{h∈𝓗} T_N(h) be the empirical mean. Then T̄ = (1+o(1))N and

  Σ_{h∈𝓗} (T_N(h) − T̄)² ≥ (c₂/6 − 1/2 − o(1)) N³ ≥ 0.2669 N³,

so the coefficient of variation of the twin-pair counts across even shifts satisfies
CV ≥ √(c₂/3 − 1) − o(1) ≥ 0.7307 − o(1): under Goldbach flatness, prime pairs are provably *not*
equidistributed in the shift h; the counts fluctuate by at least 73% of their mean in RMS. Also,
for any λ > 0, #{h ∈ 𝓗 : T_N(h) ≥ λN} ≤ (c₂/6 + o(1))N/λ² (no super-popular glut).

**(d) What "twin flatness" then means — and what remains open.** Assume (GF₂). With
Γ(N) = Σ_{even h, 0<|h|<N} 𝔖(|h|)(N−|h|) T_N(h) (the correlation of the twin counts with the
Hardy–Littlewood profile),

  Σ_{even h, 0<|h|<N} ( T_N(h) − 𝔖(|h|)(N−|h|) )² = (2c₂/3)N³ − 2Γ(N) + o(N³).

Hence, under (GF₂), pointwise-in-L² twin flatness is *equivalent* to the single scalar statement
Γ(N) = (c₂/3 − o(1))N³. We cannot evaluate Γ(N) unconditionally, and we say so: energy pinning
(part (a)) fixes the *norm* of the twin profile; it cannot fix its *direction*. That is the honest
content of "unless T is correspondingly flat": flat means Γ maximal, and (a) supplies exactly the
norm constraint that makes Γ maximal ⟺ flat.

*Proof of Theorem 5.*

(a) Split Σ_{n=2}^{2N} R_N(n)² into even and odd n. Odd n contribute O(N log N) (Lemma 5.0(a)).
For even n write R_N = M_G + E, so Σ_{even} R_N² = ‖M_G‖² + 2⟨M_G, E⟩ + D(N)². By Cauchy–Schwarz
|⟨M_G, E⟩| ≤ ‖M_G‖·D(N) ≤ (√(c₂/3)+o(1))N^{3/2}·o(N^{3/2}) = o(N³), using Theorem 4 and (GF₂).
Hence Σ_n R_N(n)² = (c₂/3)N³ + o(N³). By Theorem 1, Σ_{|h|<N} T_N(h)² has the same value; subtract
T_N(0)² ≪ N²log²N (Lemma 5.0(c)) to get the first claim, and subtract the odd-h contribution
O(N log N) (Lemma 5.0(b)) and halve by symmetry T_N(−h) = T_N(h) to get the second.

(b) Run (a) quantitatively. The chain in (a) gives, unconditionally,

  | Σ_{0<|h|<N} T_N(h)² − (c₂/3)N³ | ≤ 2‖M_G‖D(N) + D(N)² + O(N²log²N),

with ‖M_G‖ ≤ (√(c₂/3)+o(1))N^{3/2} (Theorem 4). If the left side is ≥ εN³, then for N large
2‖M_G‖D + D² ≥ (ε/2)N³. If D ≥ ‖M_G‖, then 3D² ≥ (ε/2)N³ and D ≥ √(ε/6)·N^{3/2}. Otherwise
3‖M_G‖D ≥ (ε/2)N³, so D ≥ εN³/(6‖M_G‖) ≥ (ε/6)√(3/c₂)·N^{3/2}(1−o(1)). For ε ≤ 2c₂ the second
bound is the smaller, so in all cases D(N) ≥ (ε/6)√(3/c₂)·N^{3/2}(1−o(1)). Finally D² is a sum of
exactly N squares, so max ≥ D/√N ≥ (ε/6)√(3/c₂)·N(1−o(1)), and √(3/c₂)/6 = 0.13456… .

(c) First moment over 𝓗: by Theorem 1's mass identity and Lemma 5.0,
Σ_{h∈𝓗} T_N(h) = ½(Θ(N)² − T_N(0)) − Σ_{odd h>0} T_N(h) = (½+o(1))N² (PNT), so T̄ = (1+o(1))N.
Second moment over 𝓗 is (c₂/6)N³ + o(N³) by (a). Hence the empirical variance is

  Σ_{𝓗} T² − (Σ_{𝓗} T)²/M = (c₂/6)N³ − (¼N⁴(1+o(1)))/((N/2)(1+O(1/N))) + o(N³)
                            = (c₂/6 − 1/2)N³ + o(N³),

and c₂/6 − 1/2 = 0.266987… > 0. The CV claim is this variance divided by M·T̄² = (½+o(1))N³:
CV² = (c₂/3 − 1) + o(1) = 0.533974… + o(1). The level-set bound is Chebyshev's inequality on the
second moment: λ²N²·#{h ∈ 𝓗 : T_N(h) ≥ λN} ≤ Σ_{𝓗} T_N² = (c₂/6 + o(1))N³.

(d) Expand the square: Σ_{even, h≠0}(T − M_T)² = Σ_{even, h≠0} T² − 2Γ(N) + ‖M_T‖². Insert (a) for
the first term and Theorem 4 for the third. ∎

**Remark 6.1 (honesty about the hypothesis).** (GF₂) restricted to n ≤ N is — up to the identical
weighting — the classical unconditional theorem of van der Corput, Chudakov, and Estermann
(1937–38): Σ_{n≤N}(R(n) − 𝔖(n)n)² ≪ N³ log^{−A} N for every A, proved by Vinogradov's minor-arc
bound plus Bessel; recall R_N(n) = R(n) exactly for n ≤ N+1 (Section 1). Our hypothesis
additionally covers the truncated tent range N+1 < n ≤ 2N. The same circle-method proof is
expected to give it (the analysis is of the very same S(α), with e(−nα) frequencies running to
2N), but *we have not carried that out here*, so Theorem 5 is stated as an implication, not
unconditionally. No circularity: nothing above uses (GF₂) except where displayed.

**Remark 6.2 (honesty about novelty of "many popular gaps").** The mere existence of many h with
T_N(h) ≫ N is elementary and unconditional: Σ_{h≠0}T_N(h) = Θ(N)² − T_N(0) = (1−o(1))N² while
max_h T_N(h) ≤ (log 2N)Θ(N) ≪ N log N, so at least ≫ N/log N shifts carry T_N(h) ≥ N/4 by
pigeonhole — first-moment information suffices, and we claim no credit there. What Theorem 5 adds
is *second-moment rigidity*: the exact value (c₂/3)N³ of the energy, the variance floor 0.2669N³,
the CV floor 0.7307, and the λ⁻² ceiling on super-popular shifts — none of which follow from the
first moment.

---

## 7. Transfer II: twin flatness gives a positive proportion of Goldbach evens — and the exact barrier of the method

Hypothesis (displayed, not asserted):

  (TF₂): Σ_{even h, 0<|h|<N} ( T_N(h) − 𝔖(|h|)(N−|h|) )² = o(N³).

**Theorem 6 (reverse transfer).** Assume (TF₂). Then Σ_{n=2}^{2N} R_N(n)² = (c₂/3)N³ + o(N³), and

  #{ even n, 2 ≤ n ≤ 2N : n = p + q for some primes p, q ≤ N } ≥ (3/c₂ − o(1))·N ≥ (0.6519 − o(1))·N.

That is: twin L²-flatness forces at least 65.19% of the even numbers in [2, 2N] to be Goldbach
(with both prime summands ≤ N).

*Proof.* By (TF₂), Cauchy–Schwarz on the cross term (as in Theorem 5(a), with the roles of the two
sides exchanged), and Theorem 4: Σ_{even h≠0} T_N² = ‖M_T‖² + O(‖M_T‖·o(N^{3/2})) + o(N³) =
(c₂/3)N³ + o(N³). Adding T_N(0)² ≪ N²log²N and the odd-h contribution ≪ N log N (Lemma 5.0),
Σ_{|h|<N}T_N² = (c₂/3)N³ + o(N³), and Theorem 1 converts this into Σ_n R_N(n)² = (c₂/3)N³ + o(N³).
Let 𝒜 = {even n ≤ 2N : R_N(n) > 0}. By Lemma 5.0(a) and the mass identity,
Σ_{even n} R_N(n) = Θ(N)² − O(N) = (1−o(1))N². By Cauchy–Schwarz supported on 𝒜:

  (1−o(1))N⁴ = (Σ_{even n} R_N(n))² ≤ |𝒜| · Σ_{even n} R_N(n)² ≤ |𝒜| · ((c₂/3)+o(1))N³,

so |𝒜| ≥ (3/c₂ − o(1))N. Finally R_N(n) > 0 iff n is a sum of two primes ≤ N (Section 1). ∎

**Lemma 7 (the 3/c₂ barrier: L² genuinely cannot see the roots).** There exists a nonnegative
function g on the N even slots {2, 4, …, 2N} with

  Σ g = (1−o(1))N²,  Σ g² = ((c₂/3)+o(1))N³,  and g = 0 on (1 − 3/c₂ − o(1))·N ≈ 0.348N slots.

Consequently, *no* argument whose only inputs are the mass Σ_{even} R_N and the energy
Σ_{even} R_N² — and the entire chain (TF₂) ⟹ Theorem 6 uses only these — can certify more than a
3/c₂ = 0.6519… proportion of Goldbach evens. In particular this method cannot prove binary
Goldbach, even from *perfect* twin flatness, and we do not claim otherwise.

*Proof.* Take g = λ·1_B with λ = (Σg²)/(Σg) = ((c₂/3)+o(1))N and |B| = (Σg)²/(Σg²) =
(3/c₂ + o(1))N (round |B| to an integer and repair the two moments exactly by adjusting the value
of g on a single slot; the adjustment changes each moment by O(N²) = o(N³)). This g is
indistinguishable from R_N by mass and energy, and vanishes on the complement of B. Equality
analysis of Cauchy–Schwarz shows this flat-indicator profile is the *unique* extremal shape, so
the constant 3/c₂ in Theorem 6 is sharp for the method. ∎

**Remark 7.1 (the L²→L∞ ledger, stated once and honestly).** L² lower bounds transfer to L∞ lower
bounds for free (a sum of N squares that is ≥ cN³ has a term ≥ cN²; used in Theorem 5(b)). L²
upper bounds do **not** transfer to L∞ upper bounds, and L² data does **not** bound zero sets
beyond Cauchy–Schwarz (Lemma 7): squaring forgets roots. Every L∞-flavored statement in this note
is therefore either a lower bound on a maximum (Theorem 5(b)) or a support bound with its
sharpness certificate attached (Theorem 6 + Lemma 7). Nothing stronger is claimed because nothing
stronger is true at this level of information.

---

## 8. Honesty ledger

**Classical and not claimed as new.** The Parseval mechanism equating the fourth moment of S with
either side (Theorem 1's proof method) is the standard opening move of the circle method; the
qualitative fact that the additive energy of the primes is ≍ N³ is classical (Remark 3.1); the
unconditional Goldbach L² theorem in the untruncated range is van der Corput–Chudakov–Estermann
(Remark 6.1); popularity of many gaps from the first moment is folklore (Remark 6.2).

**What this note contributes.** (1) The *exact* finite identity with matched truncations, matched
masses, and matched slot counts (Theorem 1), and its consequence that every centered quadratic
statistic of the Goldbach profile equals that of the twin profile exactly (Corollary 1.2) — an
"energy conservation law" between the two most famous prime binary problems. (2) A fully proved
closed form and error term for the second moment of the singular series,
Σ_{k≤K}𝔖(2k)² = 4∏_{p>2}(1+(p−1)⁻³)·K + O(log²K), via the per-prime identity
(1−(p−1)⁻²)²(1+(2p−3)/(p(p−2)²)) = 1+(p−1)⁻³ (Lemma 3). (3) The unconditional main-term
consistency theorem: tent² and triangle² carry the *same* energy (c₂/3)N³ (Theorem 4). (4) A
two-way L² transfer with explicit constants: Goldbach within o(N) of Hardy–Littlewood forces twin
energy = (c₂/3)N³, twin variance ≥ 0.2669N³, twin CV ≥ 0.7307 (Theorem 5); twin flatness forces
≥ 65.19% of evens to be Goldbach (Theorem 6). (5) The sharp 3/c₂ support barrier making the
L²→L∞ obstruction a theorem rather than an apology (Lemma 7).

**Not proved and not claimed.** Binary Goldbach; the twin prime conjecture; hypothesis (GF₂) in
the tent range (Remark 6.1); any pointwise asymptotic for T_N(h); any improvement of the Wave-2
modulus barrier, which concerns minor-arc mass and is untouched here.

**Numerical verification (sanity, not evidence of theorems — the theorems are proved).** At
N = 50 and N = 101: both sides of Theorem 1 agree to relative error 0 in double precision
(84517.546… and 919821.401… respectively); masses equal Θ(N)² exactly; Corollary 1.2 holds for
arbitrary centering c; third-moment ratios 0.9532 and 0.9419 confirm Remark 1.3. Lemma 3 and
Theorem 4 checks are reported in Sections 4–5.

---

## 9. The theorem in one paragraph

Let θ(n) = log n on primes and 0 elsewhere, Θ(N) = Σ_{m≤N}θ(m), and for N ≥ 2 define the
truncated Goldbach and prime-pair functions R_N(n) = Σ_{m, n−m ∈ [1,N]} θ(m)θ(n−m) (2 ≤ n ≤ 2N;
this equals the usual Σ_{m=1}^{n−1}θ(m)θ(n−m) for n ≤ N+1) and T_N(h) = Σ_{m, m+h ∈ [1,N]}
θ(m)θ(m+h) (|h| ≤ N−1). Then, exactly and for every N — by Parseval applied to
S(α) = Σ_{m≤N}θ(m)e(mα), whose square has coefficients R_N and whose modulus-squared has
coefficients T_N, or equivalently because same-sum quadruples of primes are same-gap quadruples —
Σ_{n=2}^{2N} R_N(n)² = Σ_{|h|≤N−1} T_N(h)², and likewise Σ R_N = Σ T_N = Θ(N)² over the equally
many (2N−1) slots, whence Σ(R_N − c)² = Σ(T_N − c)² for every constant c: Goldbach energy,
mass, and variance equal twin-pair energy, mass, and variance. Consequently (all constants
explicit, with c₂ = 4∏_{p>2}(1+(p−1)⁻³) = 4.60192…, proved via Σ_{k≤K}𝔖(2k)² = c₂K + O(log²K)):
the Hardy–Littlewood main terms of the two problems are exactly equienergetic, both of energy
(c₂/3)N³ + O(N²log²N); if the weighted Goldbach counts lie uniformly within o(N) of 𝔖(n)ℓ_N(n)
then the twin-pair energy Σ_{h≠0}T_N(h)² must equal (c₂/3)N³ + o(N³) — indeed any deviation εN³
of the twin energy forces a Goldbach deviation ≥ 0.134εN somewhere — and the twin counts must
then fluctuate across even shifts with coefficient of variation ≥ √(c₂/3 − 1) ≥ 0.73; conversely,
twin L²-flatness forces at least 3/c₂ − o(1) ≥ 65.1% of even n ≤ 2N to be sums of two primes ≤ N,
and the constant 3/c₂ is sharp for any argument using only mass and energy, which is the precise,
proven sense in which L² information conserves Goldbach–twin energy but cannot see the roots.
