# LEGION 07 — Twin Prime Conjecture — Research Dossier

**Program:** TOP-10 Unsolved Conjectures Research Program (Legion 07 of 10)
**Date:** 2026-08-15
**Commander note on structure:** The mission ordered ten nested specialist subagents (07-01 … 07-10). Subagent spawning is unavailable in this execution environment, so the commander executed all ten unit briefs in-line, sequentially, at maximum reasoning depth. Unit-by-unit findings and verdicts are logged in Section 4. No website files were touched; all output is confined to this directory.

**Mission compliance statement:** This dossier contains **no claimed proof of the Twin Prime Conjecture**. Everything below is labeled. The deliverables in the "candidate breakthrough" categories permitted by the mission are in Section 5: a formally stated parity no-go proposition with a complete self-contained proof (a rigorous formalization of folklore), a conditional twin-specific no-go, two fully proved admissible-tuple lemmas, and an elementary equivalent reformulation with proof.

## Honesty labels used throughout

| Label | Meaning |
|---|---|
| `[ESTABLISHED]` | Published, peer-reviewed, standard mathematics. |
| `[ESTABLISHED — from memory]` | Real published result; bibliographic or numerical details quoted from memory and not re-verified during this run. |
| `[COMPUTATIONAL]` | Machine-verified numerical fact (rigorous as computation, not as theorem about infinity). |
| `[VERIFIED-WEB 2026-08-15]` | Checked against live sources during this run. |
| `[HEURISTIC]` | Believed on probabilistic/analytic grounds; not a theorem. |
| `[CONJECTURE]` | Open conjecture. |
| `[FOLKLORE — FORMALIZED HERE]` | Known to experts in informal form; the precise statement/proof written out for this dossier. |
| `[PROVED HERE]` | Complete proof included in this dossier (elementary or classical techniques; no novelty of substance claimed unless stated). |
| `[CONDITIONAL]` | Rigorous implication whose hypothesis is open. |
| `[ORIGINAL SYNTHESIS]` | Expository framing or construction assembled for this dossier; no new theorem claimed. |
| `[SPECULATIVE]` | Research direction, not a result. |
| `[FAILED ATTACK]` | Attempted and abandoned, with reason. |

---

## 1. Problem statement and classical background (unit 07-01)

### 1.1 The conjecture

**Twin Prime Conjecture** `[CONJECTURE]`: there exist infinitely many primes $p$ such that $p+2$ is also prime.

Equivalently: $\liminf_{n\to\infty}(p_{n+1}-p_n) = 2$, where $p_n$ is the $n$-th prime. It is the special case $d=2$ of **de Polignac's conjecture** (1849) `[CONJECTURE]`: every even $d \ge 2$ occurs infinitely often as a difference of consecutive primes.

### 1.2 The Hardy–Littlewood quantitative form

**First Hardy–Littlewood conjecture (prime $k$-tuples, quantitative)** `[CONJECTURE]` (Hardy & Littlewood, *Partitio Numerorum III*, Acta Math. 44, 1923): for an admissible tuple $\mathcal H = \{h_1,\dots,h_k\}$ (Definition 1.1 below),

$$\#\{n \le x : n+h_1,\dots,n+h_k \text{ all prime}\} \sim \mathfrak S(\mathcal H)\, \frac{x}{(\log x)^k}, \qquad \mathfrak S(\mathcal H) = \prod_p \left(1 - \frac{\nu_{\mathcal H}(p)}{p}\right)\left(1-\frac 1p\right)^{-k},$$

where $\nu_{\mathcal H}(p)$ is the number of distinct residues occupied by $\mathcal H$ modulo $p$.

**Definition 1.1 (admissible tuple)** `[ESTABLISHED]`: $\mathcal H$ is *admissible* if $\nu_{\mathcal H}(p) < p$ for every prime $p$, i.e. $\mathcal H$ does not cover all residue classes modulo any prime. Admissibility is exactly the condition $\mathfrak S(\mathcal H) \neq 0$ — the local (congruence) obstructions vanish.

For $\mathcal H = \{0, 2\}$ this specializes to the **twin prime constant** form: with

$$C_2 = \prod_{p \ge 3}\left(1 - \frac{1}{(p-1)^2}\right) = 0.6601618158\ldots \quad \text{[ESTABLISHED numerical constant]},$$

the conjecture predicts $\pi_2(x) := \#\{p \le x : p, p+2 \text{ prime}\} \sim 2C_2 \int_2^x \frac{dt}{(\log t)^2}$ `[CONJECTURE]`. The constant $2C_2 \approx 1.3203$ encodes the fact that $p, p+2$ being coprime to a prime $q\ge 3$ removes **two** residues mod $q$ rather than the "independent" heuristic's squared single-residue removal; the singular series is precisely the correction factor between the naive $x/(\log x)^2$ model and the correct local model. `[ESTABLISHED as heuristic derivation; the asymptotic itself is open]`

### 1.3 Classical unconditional facts

- **Brun (1919)** `[ESTABLISHED]`: $\sum_{p,\,p+2 \text{ prime}} \left(\frac 1p + \frac 1{p+2}\right)$ converges (Brun's constant $B_2$). Hence twins have density zero among primes; sieve upper bounds give $\pi_2(x) \ll x/(\log x)^2$, the true conjectured order of magnitude. The convergence of $B_2$ means "divergence-style" evidence (as with $\sum 1/p$) is structurally unavailable for twins.
- **Clement's criterion (1949)** `[ESTABLISHED]` (P. A. Clement, Amer. Math. Monthly 56): for $n \ge 2$, the pair $(n, n+2)$ is a twin prime pair iff $4\big((n-1)! + 1\big) + n \equiv 0 \pmod{n(n+2)}$. An exact Wilson-type reformulation; computationally useless (factorial size), but it certifies that twin-ness is a single congruence condition.
- **Hensley–Richards (1974)** `[ESTABLISHED — from memory]` (Acta Arith. 25): the prime $k$-tuples conjecture is *incompatible* with the "second Hardy–Littlewood conjecture" $\pi(x+y) \le \pi(x) + \pi(y)$. Expert consensus discards the second conjecture and keeps the tuples conjecture; relevant here because it shows dense admissible tuples eventually beat the primes' own initial density.

---

## 2. The sieve frontier: known partial results (units 07-02 → 07-05)

### 2.1 Chen's theorem and the 1+2 barrier (unit 07-02)

**Chen's theorem (announced 1966, full proof 1973)** `[ESTABLISHED]` (J.-R. Chen, Sci. Sinica 16): there are infinitely many primes $p$ such that $p + 2 \in \mathcal P_2$, i.e. $p+2$ is prime or a product of two primes. Quantitatively, the count of such $p \le x$ is $\gg x/(\log x)^2$, matching the conjectured order for genuine twins.

Method `[ESTABLISHED]`: linear (dimension-1) sieve upper and lower bounds applied to the shifted sequence $\{p+2 : p \le x\}$, using Bombieri–Vinogradov (Section 2.3) as the level-of-distribution input, plus Chen's decisive **switching principle** (role reversal: bounding the bad count of $p+2 = q_1 q_2 q_3$ by re-sieving with $q_1$ as the "variable prime"). Standard expositions: Halberstam–Richert, *Sieve Methods* (1974); Ross's simplified proof (1975) `[ESTABLISHED — from memory]`.

Why it stops at $\mathcal P_2$: the linear sieve's lower-bound function $f(s)$ has **sifting limit** $\beta = 2$; below it the lower bound goes negative. Selberg's parity example (Section 3.1) shows this is not a defect of the particular sieve but an information-theoretic wall: the axioms used cannot distinguish integers with an odd versus even number of prime factors. Chen's $\mathcal P_2$ is exactly the parity-permitted endpoint. `[ESTABLISHED — see Friedlander–Iwaniec, Opera de Cribro (2010), for the modern treatment]`

The same weighted-sieve machinery gives the analogous approximations for variants: infinitely many $p$ with $2p+1 \in \mathcal P_2$ (Sophie Germain approximation), and every large even $N$ is $p + \mathcal P_2$ (Chen's Goldbach theorem, same paper). `[ESTABLISHED; the $2p+1$ variant is a standard extension of Chen's method — from memory]`

### 2.2 The GPY method, exactly (unit 07-03)

**Goldston–Pintz–Yıldırım, "Primes in tuples I"** (Ann. of Math. 170 (2009), 819–862) `[ESTABLISHED]`.

Setup. Fix an admissible $k$-tuple $\mathcal H = \{h_1,\dots,h_k\}$, let $P(n) = \prod_{i}(n+h_i)$, choose a truncation $R = N^{\theta/2 - \varepsilon}$ where $\theta$ is the available level of distribution, and an extra parameter $\ell \ge 0$. Define the GPY weight (a truncated, $\ell$-smoothed divisor sum mimicking $\Lambda^{\otimes k}$):

$$\Lambda_R(n;\mathcal H,\ell) = \frac{1}{(k+\ell)!}\sum_{\substack{d \mid P(n) \\ d \le R}} \mu(d)\left(\log \frac Rd\right)^{k+\ell}, \qquad w_n = \Lambda_R(n;\mathcal H,\ell)^2 \ \ (\ge 0).$$

Detection functional. With $\vartheta(m) = \log m$ if $m$ prime, else $0$:

$$S := \sum_{N < n \le 2N} \Big(\sum_{i=1}^k \vartheta(n+h_i) - \log 3N\Big)\, w_n.$$

If $S > 0$ then some $n \in (N, 2N]$ has **at least two** primes among $n+h_1,\dots,n+h_k$, so a prime gap $\le \max_i h_i - \min_i h_i$ occurs.

The two moment computations (GPY's core propositions; constants quoted from the paper, structure certain, exact constants `[ESTABLISHED — from memory]`):

$$\sum_{N<n\le 2N} w_n \sim \frac{\binom{2\ell}{\ell}}{(k+2\ell)!}\, \mathfrak S(\mathcal H)\, N (\log R)^{k+2\ell},$$

$$\sum_{N<n\le 2N} w_n\, \vartheta(n+h_j) \sim \frac{\binom{2\ell+2}{\ell+1}}{(k+2\ell+1)!}\, \mathfrak S(\mathcal H)\, N (\log R)^{k+2\ell+1} \quad (1 \le j \le k),$$

the second valid provided the primes have level of distribution $\theta$ (needed to control the error terms $\sum_{d \le R^2} |\Delta(N; d)|$ arising from opening the square — this is where Bombieri–Vinogradov enters with $\theta = 1/2$). Taking ratios:

$$\frac{S}{(\log 3N)\sum w_n} \longrightarrow \frac{\theta}{2}\cdot \frac{2(2\ell+1)}{\ell+1}\cdot\frac{k}{k+2\ell+1} \;-\; 1.$$

Optimizing $\ell \asymp \sqrt k$ makes the middle factors approach $4 \cdot \frac{\theta}{2} = 2\theta$ as $k \to \infty$. Consequences `[ESTABLISHED]`:

1. **Need $\theta > 1/2$:** $2\theta > 1$ iff $\theta > 1/2$. Any level of distribution beyond Bombieri–Vinogradov, however slight, gives **bounded gaps** with explicit $k(\theta)$.
2. **At $\theta = 1/2$ exactly:** the functional just fails ($\to 1 - \epsilon$), but a refinement gives the landmark unconditional result $\liminf_n \frac{p_{n+1}-p_n}{\log p_n} = 0$: gaps infinitely often smaller than any fixed multiple of the average.
3. **Under full Elliott–Halberstam ($\theta = 1$):** $k = 6$, tuple $\{0,4,6,10,12,16\}$, giving gaps $\le 16$ infinitely often (the borderline case $k=6$ needs the paper's finer analysis). `[ESTABLISHED — from memory]`

A technical smoothing of the GPY sieve (Motohashi–Pintz, Bull. LMS 40, 2008) anticipated the reduction to smoothed/flexible moduli that Zhang would exploit. `[ESTABLISHED — from memory]`

### 2.3 Zhang: bounded gaps unconditionally (unit 07-04)

**Bombieri–Vinogradov theorem (1965)** `[ESTABLISHED]`: for every $A>0$ there is $B>0$ with

$$\sum_{q \le x^{1/2}/(\log x)^B} \max_{(a,q)=1}\Big|\psi(x;q,a) - \frac{x}{\varphi(q)}\Big| \ll_A \frac{x}{(\log x)^A}.$$

This is "level of distribution $\theta = 1/2$": GRH-strength on average. The **Elliott–Halberstam conjecture** EH$[\theta]$ (Elliott & Halberstam, 1968) `[CONJECTURE]` asserts the same with moduli up to $x^{\theta}$, for any $\theta < 1$.

**Zhang's theorem (2013; Ann. of Math. 179 (2014), 1121–1174)** `[ESTABLISHED]`: there are infinitely many prime gaps $\le 7\times 10^7$. The engine is a Bombieri–Vinogradov-type estimate **beyond** level $1/2$ — level $\theta = \tfrac12 + 2\varpi$ with $\varpi = 1/1168$ — valid not for all moduli but for $x^{\delta}$-**smooth, squarefree** moduli, and for the specific residue classes (roots of $P$ mod $q$) that the GPY sieve actually needs. That weakened-but-shifted form suffices because the GPY error terms can be arranged to involve only such moduli (this flexibility is the Motohashi–Pintz observation). Ingredients: Heath-Brown's identity, the dispersion method (Linnik; Bombieri–Fouvry–Friedlander–Iwaniec lineage), completion of incomplete exponential sums, and ultimately Weil/Deligne-strength bounds on Kloosterman-type sums over finite fields. Zhang's tuple size $k_0 = 3.5\times 10^6$ gave $H = 7\times 10^7$.

**Polymath8a** ("New equidistribution estimates of Zhang type", Algebra & Number Theory 8, 2014) `[ESTABLISHED]` optimized the exponents ($\varpi, \delta$), the exponential-sum inputs, and the admissible tuples, reaching $H \le 4680$ along the Zhang route.

Key structural point `[ESTABLISHED]`: Zhang did **not** prove EH$[\theta]$ for any $\theta > 1/2$ in the standard maximal form; he proved a smoothed, restricted-residue surrogate. The distinction matters for Section 3.2: Friedlander–Granville (Ann. of Math. 129, 1989) showed EH-type uniformity must fail for moduli up to $x/(\log x)^B$, so all such improvements live strictly inside $q \le x^{1-\varepsilon}$.

### 2.4 Maynard–Tao and the current records (unit 07-05)

**Maynard, "Small gaps between primes"** (Ann. of Math. 181 (2015), 383–413); Tao independently, contributed to Polymath8b `[ESTABLISHED]`.

The multidimensional Selberg sieve replaces the single divisor variable $d \mid P(n)$ by one variable per coordinate:

$$w_n = \Big(\sum_{\substack{d_i \mid n + h_i\ \forall i \\ \prod d_i \le R}} \lambda_{d_1,\dots,d_k}\Big)^2, \qquad \lambda_{d_1,\dots,d_k} \approx \Big(\prod_i \mu(d_i)\Big) F\Big(\frac{\log d_1}{\log R},\dots,\frac{\log d_k}{\log R}\Big),$$

with $F$ smooth on the simplex $\{t_i \ge 0, \sum t_i \le 1\}$. The two moments become explicit functionals of $F$:

$$\sum_n w_n \rightsquigarrow I_k(F) = \int F^2\,dt, \qquad \sum_n w_n \mathbf 1_{n+h_j \text{ prime}} \rightsquigarrow J_k^{(j)}(F) = \int \Big(\int F\, dt_j\Big)^2 \prod_{i\neq j} dt_i,$$

and with level of distribution $\theta$, the conclusion DHL$(k, m{+}1)$ — *every* admissible $k$-tuple contains $\ge m+1$ primes at infinitely many shifts — holds whenever

$$M_k := \sup_F \frac{\sum_{j=1}^k J_k^{(j)}(F)}{I_k(F)} > \frac{2m}{\theta}.$$

Results `[ESTABLISHED]`:

- $M_k \ge \log k - 2\log\log k - 2$ for large $k$, hence $M_k \to \infty$: **any** positive level of distribution yields arbitrarily many primes in tuples ($m+1$ primes for $k \gg e^{cm/\theta}$). This is qualitatively beyond Zhang, and it needs only classical Bombieri–Vinogradov.
- $M_{105} > 4$: with $\theta = 1/2$, DHL$(105, 2)$; the narrowest admissible 105-tuple has diameter 600, so gaps $\le 600$ infinitely often.
- $M_5 > 2$ (barely): under EH ($\theta=1$), DHL$(5,2)$ with $\{0,2,6,8,12\}$: gaps $\le 12$.
- $H_m := \liminf (p_{n+m} - p_n) < \infty$ for every $m$; Maynard's bound $H_m \ll m^3 e^{4m}$; the exponential rate has since been improved (Baker–Irving) `[ESTABLISHED — from memory]`.

**Polymath8b** ("Variants of the Selberg sieve, and bounded intervals containing many primes", Res. Math. Sci. 1, 2014) `[ESTABLISHED]`, `[VERIFIED-WEB 2026-08-15]`:

| $m$ | conjectural $H_m$ | under GEH / EH | unconditional |
|---|---|---|---|
| 1 | 2 (twins) | 6 (GEH); 12 (EH, Maynard) | **246** |
| 2 | 6 | 252 (GEH); 270 (EH) | 395,106 |
| 3 | 8 | 52,116 | 24,462,654 |

Route to 246: pure Maynard functional gives $M_{54} > 4$ hence $H_1 \le H(54) = 270$; an "$\varepsilon$-enlarged simplex" variant of the variational problem gives DHL$(50,2)$, and the narrowest admissible 50-tuple has diameter $H(50) = 246$. `[ESTABLISHED — from memory for the 54/270 intermediate step]`

Two facts verified live `[VERIFIED-WEB 2026-08-15]`: (i) **246 is still the best unconditional bound as of August 2026** (Polymath wiki; no published improvement); (ii) practitioners assess the current variational machinery as essentially saturated near 246 without new equidistribution or a new sieve idea.

Important corollary of the record's structure `[ESTABLISHED]`: the 246 bound uses only Bombieri–Vinogradov — Zhang-type equidistribution and Deligne-dependent estimates are no longer needed for $H_1$ (they still matter for $H_m$, $m \ge 2$). The frontier input for $H_1$ is the sieve functional, not the level of distribution.

---

## 3. Obstructions: parity, the EH ceiling, positional blindness (units 07-06 → 07-08)

### 3.1 The parity problem (unit 07-06)

**Informal statement** `[ESTABLISHED — Selberg]`: sieve methods that use only "type I" information — counts of a sequence in congruence classes $A_d = X g(d) + r_d$ with controlled remainders — cannot distinguish integers with an **odd** number of prime factors from integers with an **even** number. Since primes have one prime factor (odd) and the sieve-accessible almost-primes $\mathcal P_2$ include $p_1p_2$ (even), no such sieve can prove the existence of primes, or of twin primes, in a sifted sequence. Selberg's example dates to his analysis of the linear sieve's optimality (address at the 11th Scandinavian Congress, 1949; elaborated in his Collected Papers, vol. II) `[ESTABLISHED — from memory]`.

The dossier's formal version, with complete proof, is **Proposition 5.1** below. The twin-specific version is **Proposition 5.2** (conditional). Related rigorous landmarks:

- **Bombieri's asymptotic sieve** (1976) `[ESTABLISHED — from memory]`: given type-I information of essentially full level for a sequence, one obtains asymptotics for $\sum a_n \Lambda_j(n)$ (generalized von Mangoldt, detecting $\mathcal P_j$) for **every $j \ge 2$**, while the $j = 1$ (prime) case remains undetermined precisely up to a one-parameter "parity phase". Parity is thus the *only* obstruction at that level of information.
- **Friedlander–Granville** (Ann. of Math. 129, 1989) and **Friedlander–Granville–Hildebrand–Maier** (J. Amer. Math. Soc. 4, 1991) `[ESTABLISHED — from memory]`: oscillation results limiting equidistribution of primes in progressions for very large moduli; these calibrate what level-of-distribution hypotheses can even be true (see 3.2).
- **Breaking parity is possible with *extra* (bilinear / type-II) information** `[ESTABLISHED]`: Friedlander–Iwaniec proved $x^2 + y^4$ captures primes (Ann. of Math. 148, 1998) via their *asymptotic sieve for primes*, whose engine is a bilinear-form estimate that genuinely inputs sign-sensitive information beyond the sieve axioms; Heath-Brown did the same for $x^3 + 2y^3$ (Acta Math. 186, 2001). Helfgott's work on root numbers and parity for cubic forms is in the same spirit `[ESTABLISHED — from memory]`. **No analogous bilinear structure is known for the sequence $n(n+2)$.** This is the precise technological gap.
- A modern quantitative echo `[ESTABLISHED]`: Tao's logarithmically-averaged two-point Chowla theorem (Forum Math. Pi 4, 2016) proves $\sum_{n \le x} \lambda(n)\lambda(n+2)/n = o(\log x)$ — the Liouville sign at $n$ and $n+2$ genuinely decorrelates in log-density. Interpreted through Section 5, this *confirms the internal consistency* of the parity-twist models that block the sieve (it does not, of course, block other methods).

### 3.2 The Elliott–Halberstam ceiling (unit 07-07)

Suppose EH$[\theta]$ for every $\theta < 1$ — the strongest distribution hypothesis that survives Friedlander–Granville's oscillation theorems. What follows for twins?

- GPY: gaps $\le 16$. Maynard: gaps $\le 12$. Polymath8b under **generalized** EH (GEH, level $1-\varepsilon$ for general convolutions, after Bombieri–Friedlander–Iwaniec): gaps $\le 6$, i.e. infinitely many $n$ with two primes in $\{n, n+2, n+6\}$-type configurations. `[ESTABLISHED]`
- **Not twins.** Two independent hard stops:
  1. **Variational stop** `[ESTABLISHED]`: Polymath8b proved the upper bound $M_k \le \frac{k}{k-1}\log k$. For $k = 2$: $M_2 \le 2\log 2 \approx 1.386 < 2 = 2m/\theta|_{m=1,\theta=1}$. So even at the maximal conceivable level $\theta = 1$, the Maynard functional **provably cannot** certify two primes in a 2-tuple. The $\varepsilon$-enlargement and vanishing-marginal refinements move the GEH endpoint to $H_1 = 6$ and, per the Polymath8b analysis, no further — $6$ is the parity-imposed limit of the entire Selberg-weight class under GEH. `[ESTABLISHED — Polymath8b, final-section analysis; section number not re-verified]`
  2. **Parity stop** `[FOLKLORE — FORMALIZED HERE, Section 5]`: EH/GEH are still type-I-style statements about congruence counts. The $\big(1 \pm \lambda\big)$-twisted models of Section 5 satisfy the same statistics the sieve consumes, yet contain no twins; so no argument consuming only EH/GEH-type inputs plus nonnegative weights can reach $H_1 = 2$.

Summary: **level of distribution is no longer the binding constraint for twins; parity is.** Even the full EH hierarchy buys $6$, not $2$.

### 3.3 Bounded gaps ≠ twins: positional blindness (unit 07-08)

What Zhang/Maynard/Polymath prove is DHL$(k,2)$: in every admissible $k$-tuple, *some two* positions are simultaneously prime infinitely often. Pigeonholing over the tuple's difference set yields: **some** even $d \le 246$ is a Polignac number (infinitely many prime pairs at distance exactly... at most 246, and by a finite pigeonhole some fixed $d \le 246$ recurs infinitely often). The method cannot name $d$; naming any *specific* difference (e.g. $d = 2$) is precisely a parity-class problem. Related established refinements: Pintz showed the set of Polignac numbers has positive lower density `[ESTABLISHED — from memory, 2013]`; Maynard's *Dense clusters of primes in subsets* (Compositio Math. 152, 2016) `[ESTABLISHED — from memory]` extends the sieve to general admissible families of linear forms and to thin sets with BV-type equidistribution — always with the same cardinality-not-position conclusion.

The **pair-carrier construction** (Observation 5.4) makes the blindness tactile: one can build an admissible 50-tuple that is a disjoint union of 25 *twin pairs* $\{a_j, a_j+2\}$; DHL$(50,2)$ then guarantees two primes among the 50 entries infinitely often, and the Twin Prime Conjecture would follow if the two primes ever landed in the *same* pair-slot — but the sieve's conclusion is invariant under which two slots fire, and the parity models can route the two primes into distinct slots forever. Nothing in the moment method sees the diagonal.

---

## 4. Attack-vector log of the ten units (07-01 … 07-10)

Each unit: brief, key finding, verdict (*known / incremental / candidate breakthrough / failed attack*).

**07-01 (Statement, HL constant, first HL conjecture).** Assembled Section 1; computed nothing new; confirmed the singular-series formalism and the Hensley–Richards incompatibility. Also produced the elementary $6k\pm1$ reformulation with full proof (Lemma 5.5) as the "equivalent formulation" deliverable. Verdict: **known**, plus one **fully proved elementary reformulation** (folklore, proof included).

**07-02 (Chen / 1+2 barrier).** Section 2.1. Confirmed that Chen's endpoint is the parity endpoint of the linear sieve; the switching principle does not iterate ($\mathcal P_2 \to \mathcal P_1$ would need sign-sensitive input). Attempted variant: apply switching a second time with a bilinear pivot on $n(n+2)$ — no usable bilinear structure found (the sequence has no known "multiplicative surrogate" like Gaussian norms in $x^2+y^4$). Verdict: **failed attack** (documented reason), survey **known**.

**07-03 (GPY exactly).** Section 2.2 with the exact weight, both moment asymptotics, the ratio optimization, and the three consequences. Checked internal consistency of the constants (ratio $\to 2\theta$; borderline $k=6$ under EH). Verdict: **known** (precision pass; no gap found in the standard account).

**07-04 (Zhang, BV/EH).** Section 2.3. Emphasis finding: Zhang's input is *not* EH$[\theta>1/2]$ but a smoothed restricted surrogate, and post-Maynard the $H_1$ record no longer uses it at all. Verdict: **known**.

**07-05 (Maynard–Tao, Polymath8).** Section 2.4; records re-verified live ($246$ unconditional; $12$ EH; $6$ GEH; $H_m$ table) `[VERIFIED-WEB 2026-08-15]`. Verdict: **known**, with fresh verification.

**07-06 (Parity no-go).** Section 3.1 + **Proposition 5.1 proved in full** (rigorous, self-contained, PNT-only ingredients) and **Proposition 5.2** (twin-specific, conditional on a Chowla-type estimate; the needed hypothesis stated exactly). This is the dossier's primary "formally stated no-go" deliverable. Verdict: **candidate contribution of exposition-grade rigor** — folklore formalized with complete proof; no research novelty claimed.

**07-07 (EH ceiling).** Section 3.2. Sharpest formal finding: $M_2 \le 2\log 2 < 2$ (from Polymath8b's $M_k \le \frac{k}{k-1}\log k$) — a one-line *proof* that the unmodified Maynard functional cannot give twins even at $\theta = 1$. Verdict: **known** (assembled into an unusually crisp form).

**07-08 (Bounded gaps vs twins).** Section 3.3 + Observation 5.4 (pair-carrier tuple, admissibility proved). Verdict: **original synthesis** (elementary, verified; clarifies, does not advance).

**07-09 (Computational).** Section 6. Records re-verified live; the Π-complexity point (twin infinitude is $\Pi^0_2$: numerics can neither prove nor refute it) stated formally. Verdict: **known** + verification.

**07-10 (Variants).** Section 7.2. Ranking with reasons; the uniform explanation ("cardinality vs. position") of why all named-pattern variants sit in one difficulty class. Verdict: **known / original synthesis**.

---

## 5. Candidate results proved or formalized in this dossier

> Scope statement `[honesty]`: 5.1 and 5.3 are rigorous with complete proofs from standard ingredients; they are formalizations/instances of known mathematics, written out so the no-go and the constructions are *checkable statements* rather than lore. 5.2 is conditional and labeled so. 5.4 and 5.5 are elementary and fully proved. **Nothing here advances the frontier; everything here is true.**

### Proposition 5.1 (Parity blindness of divisor-level sieve data) `[FOLKLORE — FORMALIZED HERE] [PROVED HERE]`

*Let $\lambda$ be the Liouville function, $x \ge 3$, $0 < \varepsilon < 1$. Define nonnegative weights on $n \le x$:*

$$a_n = 1 - \lambda(n), \qquad b_n = 1 + \lambda(n).$$

*Then, with $L(y) := \sum_{m \le y} \lambda(m)$ and $c_0 > 0$ the absolute constant from the Prime Number Theorem with classical error term:*

1. *(identical type-I data)* For every $d \le x^{1-\varepsilon}$,
$$\sum_{\substack{n \le x \\ d \mid n}} a_n = \frac{x}{d} + O\!\Big(\frac{x}{d}\, e^{-c_0\sqrt{\varepsilon \log x}}\Big) = \sum_{\substack{n \le x \\ d \mid n}} b_n + O\!\Big(\frac{x}{d}\, e^{-c_0\sqrt{\varepsilon \log x}}\Big);$$
*both weightings present the sieve with the same density function $g(d) = 1/d$ and remainders of strength "level $x^{1-\varepsilon}$".*
2. *(maximally different prime content)* $b_p = 0$ for every prime $p$, while $a_p = 2$; hence $\sum_{p \le x} b_p = 0$ and $\sum_{p \le x} a_p = 2\pi(x)$.

*Consequently: there is no functional $\Phi$, consuming only the data $\{\sum_{d \mid n} w_n : d \le x^{1-\varepsilon}\}$ of a nonnegative weight sequence $(w_n)$, with the property that $\Phi(\text{data}) > 0$ forces $\sum_p w_p > 0$. In particular no sieve bound built solely from such data can prove the existence of primes — a fortiori of twin primes — in the sifted range.*

**Proof.** $\lambda$ is completely multiplicative, so for any $d$, $\sum_{n \le x,\, d \mid n} \lambda(n) = \sum_{m \le x/d} \lambda(dm) = \lambda(d) L(x/d)$. The PNT with de la Vallée Poussin error is equivalent to $L(y) \ll y\, e^{-c_0\sqrt{\log y}}$ `[ESTABLISHED]`. For $d \le x^{1-\varepsilon}$ we have $x/d \ge x^{\varepsilon}$, so $\log(x/d) \ge \varepsilon \log x$ and $|L(x/d)| \ll (x/d) e^{-c_0 \sqrt{\varepsilon \log x}}$. Since $\sum_{n \le x, d\mid n} (1 \mp \lambda(n)) = \lfloor x/d \rfloor \mp \lambda(d) L(x/d)$, part 1 follows. Part 2 is $\lambda(p) = -1$. For the consequence: the two sequences $(a_n), (b_n)$ are both admissible inputs with the same data up to the stated error, so any $\Phi$ as described returns (essentially) the same value on both; if that value certified positivity of the weighted prime count, it would be wrong on $(b_n)$. $\blacksquare$

**Remarks.** (i) The same argument runs with arithmetic-progression data $\sum_{n \equiv a (q)} w_n$, since $\lambda$ satisfies Siegel–Walfisz- and Bombieri–Vinogradov-type mean value theorems (established literature on multiplicative functions; details omitted) `[ESTABLISHED — from memory]`. So even "BV-level" or "EH-level" progression statistics are parity-blind in this abstraction. (ii) The weight $b_n = 1+\lambda(n)$ is supported exactly on $\Omega(n)$ even — the "almost-primes of even type" of the mission brief. (iii) What escapes the no-go: any input *not* determined by the listed data — bilinear/type-II sums (Friedlander–Iwaniec), automorphic input, additive-combinatorial transference. The no-go is a map of the wall, not of the territory beyond it.

### Proposition 5.2 (Twin-specific parity no-go) `[CONDITIONAL — hypothesis open]`

*Assume the Chowla-type equidistribution hypothesis* CH: *for some $\delta > 0$, uniformly for $d \le x^{1-\varepsilon}$ and residues $r$,*
$$\sum_{\substack{n \le x \\ n \equiv r \ (d)}} \lambda\big(n(n+2)\big) \ll \frac{x}{d}\, (\log x)^{-\delta \log\log x} \quad (\text{any saving uniform in } d \text{ suffices}).$$
*Define $c^{\pm}_n = 1 \pm \lambda(n(n+2)) \ge 0$. Then $(c^+_n)$ and $(c^-_n)$ present identical type-I data for the twin sieve (divisor data of the polynomial $n(n+2)$) up to the CH error, while $c^-_n = 0$ whenever $n$ and $n+2$ are both prime (since then $\lambda(n(n+2)) = (-1)^2 = 1$). Hence, under CH, no functional of twin-sieve type-I data with nonnegative weights can certify the existence of twin primes.*

**Proof.** Identical to 5.1 with $\lambda(n)$ replaced by $\lambda(n(n+2))$; the vanishing at twin ranks is the displayed sign computation. $\blacksquare$

**Honesty notes.** CH is open — it is a two-point Chowla-type statement *with* uniformity in progressions; unconditionally we know only the logarithmically-averaged decorrelation $\sum_{n\le x} \lambda(n)\lambda(n+2)/n = o(\log x)$ (Tao 2016) `[ESTABLISHED]`, which supports but does not prove CH. The role of 5.2 is to make precise *why experts expect* no purely type-I proof of twins: such a proof would *refute* CH — i.e., detecting twins by sieve alone is at least as hard as disproving a Chowla-type statement everyone believes. Unconditionally, Proposition 5.1 already blocks the abstract one-dimensional route, and Selberg's classical examples block the linear sieve at its $\beta = 2$ limit `[ESTABLISHED]`.

### Lemma 5.3 (Prime-block admissible tuples) `[ESTABLISHED — classical construction; PROVED HERE in full]`

*For $k \ge 2$ let $m = \pi(k)$ and $\mathcal H_k = \{p_{m+1}, p_{m+2}, \dots, p_{m+k}\}$ (the first $k$ primes exceeding $k$). Then $\mathcal H_k$ is an admissible $k$-tuple of diameter $(1 + o(1))\, k \log k$.*

**Proof.** *Admissibility.* Let $q$ be prime. If $q \le k$: every element of $\mathcal H_k$ is a prime $> k \ge q$, hence not divisible by $q$, so residue $0 \pmod q$ is unoccupied. If $q > k$: the tuple has $k < q$ elements, so it occupies at most $k < q$ residues mod $q$. Either way $\nu_{\mathcal H_k}(q) < q$. *Diameter.* By the PNT, $p_n \sim n \log n$ and $m = \pi(k) \sim k/\log k = o(k)$; hence $p_{m+k} \sim (m+k)\log(m+k) \sim k \log k$, while $p_{m+1} \le 2(k+1) = o(k\log k)$ by Bertrand's postulate. $\blacksquare$

**Context** `[ESTABLISHED — from memory]`: this is the Hensley–Richards-type construction; the true minimal diameter $H(k)$ satisfies $H(k) \ge (\tfrac12 - o(1))k\log k$ via the Montgomery–Vaughan large sieve, and exact small values are known by computation ($H(50) = 246$, $H(105) = 600$ — the numbers in the records). So the lemma's construction is within a factor $\sim 2$ of optimal; record tuples come from computational sieving of intervals, not from closed forms.

### Observation 5.4 (Pair-carrier tuples and the missing diagonal) `[ORIGINAL SYNTHESIS — elementary parts PROVED HERE]`

*Let $M = \prod_{p \le 53} p$ and $T = \{ jM + t : 0 \le j \le 24, \ t \in \{0, 2\}\}$, a set of $50$ integers forming $25$ disjoint twin pairs. Then $T$ is admissible.*

**Proof.** Mod $2$: every element is even, residue $1$ unoccupied. Mod odd $p \le 53$: $M \equiv 0$, so elements occupy only $\{0, 2\} \pmod p$, and $p \ge 3$ leaves residue $1$ unoccupied. Mod $p > 53$: at most $50 < p$ residues occupied. $\blacksquare$

*Consequences.* DHL$(50,2)$ (Polymath8b, unconditional) applies: infinitely many $n$ have **two primes** among $\{n + jM,\ n + jM + 2\}_{j\le 24}$. If the two primes ever share a slot $j$, they are twins. The theorem is constitutionally silent on this: its conclusion is a cardinality over 50 symmetric positions, and the parity models (5.1/5.2 style) are consistent with the two primes avoiding the diagonal forever. The construction isolates, in one concrete object, the exact deficit between the strongest proved theorem and the conjecture: **a diagonal-biasing device for sieve weights** — any nonnegative weight system whose moments remain computable but which rewards *same-slot* prime pairs — would convert DHL$(50,2)$-technology into twins, and by 5.2 any such device must consume information beyond type-I data (e.g. bilinear estimates for $n(n+2)$). `[SPECULATIVE as a research direction; the stated mathematics is proved above]` The diameter of $T$ is astronomically large ($24M + 2$, $M \approx 3.3 \times 10^{19}$); $T$ is a structural exhibit, not a competitor to $H(50) = 246$.

### Lemma 5.5 (The $6k \pm 1$ quadratic-exclusion reformulation) `[FOLKLORE; PROVED HERE in full]`

*For $k \ge 1$, the pair $(6k-1,\ 6k+1)$ is a twin prime pair if and only if $k$ is in none of the three families*

$$k = 6ab + a + b, \qquad k = 6ab - a - b, \qquad k = 6ab + a - b \qquad (a, b \ge 1).$$

*Since every twin pair other than $(3,5)$ has the form $(6k-1, 6k+1)$, the Twin Prime Conjecture is equivalent to: the three quadratic families above fail to cover all sufficiently large integers.*

**Proof.** Every divisor of $6k\pm1$ is coprime to $6$, hence $\equiv \pm 1 \pmod 6$. If $6k+1 = uv$ with $u, v > 1$ then $u \equiv v \pmod 6$ (their product is $\equiv 1$): writing $u = 6a+1, v = 6b+1$ gives $6k+1 = 36ab + 6a + 6b + 1$, i.e. $k = 6ab + a + b$; writing $u = 6a - 1, v = 6b - 1$ gives $k = 6ab - a - b$. If $6k - 1 = uv$ then $u \not\equiv v$: $u = 6a - 1, v = 6b+1$ gives $6k - 1 = 36ab + 6a - 6b - 1$, i.e. $k = 6ab + a - b$ (the roles of $a, b$ swapped give the same family). Conversely each representation manufactures the corresponding factorization, and $a, b \ge 1$ forces both factors $> 1$. Finally, twin pairs $(p, p+2)$ with $p > 3$ have $p \equiv 5 \pmod 6$ (as $p \equiv 1$ would force $3 \mid p+2$), i.e. $p = 6k - 1$. $\blacksquare$

**Assessment** `[honesty]`: this repackages the sieve of Eratosthenes on the $k$-line; the exclusion sets have density $\to 1$ and the survivor count is exactly $\pi_2$-sized, so no leverage is gained *for free*. Its value is as the mission's "equivalent formulation suggesting tuple constructions": survivors of the three families are the natural home for structured searches (Beatty/polynomial subsequences of $k$ avoiding all three quadratic families), and the *one-sided* versions (avoid only the $6k+1$ families, or only the $6k-1$ family) are theorems (Dirichlet), which makes the reformulation a clean laboratory for studying the correlation between two individually-infinite survivor sets — precisely the parity-hard step, now in elementary clothing. `[ORIGINAL SYNTHESIS / SPECULATIVE]`

---

## 6. Computational status and the limits of numerics (unit 07-09)

**Records and counts.**

- Largest known twin primes `[COMPUTATIONAL] [VERIFIED-WEB 2026-08-15]`: $2996863034895 \cdot 2^{1290000} \pm 1$ — 388,342 decimal digits; found 14 Sept 2016 by PrimeGrid (discoverer Tom Greer; LLR primality proofs, independently verified). **Still the record as of August 2026.** Each member's primality is a rigorous $N \pm 1$ (Brillhart–Lehmer–Selfridge-type) proof, not probabilistic.
- Counting function `[COMPUTATIONAL] [VERIFIED-WEB 2026-08-15]`: $\pi_2(10^{18}) = 808{,}675{,}888{,}577{,}436$ (computation credited to T. Oliveira e Silva's tabulations). Empirical $\pi_2(x)$ tracks the Hardy–Littlewood prediction $2C_2\int_2^x dt/(\log t)^2$ with small, fluctuation-scale relative error throughout the computed range — strong calibration evidence for the singular-series model. `[COMPUTATIONAL + HEURISTIC interpretation]`
- Brun's constant `[COMPUTATIONAL + HEURISTIC]`: the familiar value $B_2 \approx 1.9021605831\ldots$ (Nicely; Sebah–Demichel) is an **extrapolation** that assumes the Hardy–Littlewood asymptotic for the tail. Rigorously, only convergence (Brun 1919) plus much weaker explicit bounds are known; published rigorous upper bounds sit near $2.1$–$2.3$ (e.g. Klyve's 2007 thesis, partly conditional) `[ESTABLISHED — from memory, not re-verified]`. Honest summary: *we do not rigorously know even the second decimal digit of $B_2$.*
- Cultural footnote `[ESTABLISHED]`: Nicely's 1994 twin-prime computations exposed the Intel Pentium FDIV bug — the sole instance to date of the Twin Prime Conjecture affecting consumer hardware.

**What numerics can and cannot do here** `[ESTABLISHED — elementary logic, stated formally]`:

The statement "there are infinitely many twin primes" is $\Pi^0_2$ ("for every $N$ there exists a twin pair beyond $N$"). Therefore:

1. No finite computation can **prove** it (unlike a $\Sigma^0_1$ statement, it has no finite witness).
2. No finite computation can **refute** it (unlike a $\Pi^0_1$ statement such as Goldbach, it has no finite counterexample). A universe with a largest twin pair at $10^{10^{100}}$ is computationally indistinguishable, forever, from the conjectured one.
3. What numerics *does* deliver: (a) rigorous existence of specific gigantic twins (records), each a proved theorem about a particular pair; (b) rigorous exact counts to $10^{18}$, which calibrate the Hardy–Littlewood constant to high precision and stress-test the underlying pseudo-randomness model; (c) discovery infrastructure — the record 50-tuples behind $H(50) = 246$ came from computational search, so numerics directly powers the *theorem* side of the field via admissible-tuple optimization.

---

## 7. Honest verdict, variant ranking, and recommended next steps

### 7.1 Verdict (program taxonomy: known / incremental / candidate breakthrough / failed attack)

- **Twin Prime Conjecture: open. No progress toward infinitude was made by this legion, and none was expected.** `[honesty]`
- Survey layer (Sections 1–3, 6): **known**, with two live verifications (records; 246 status) `[VERIFIED-WEB 2026-08-15]`.
- Proposition 5.1 (parity no-go, formal statement + complete proof): **candidate deliverable in the mission's "formally stated parity no-go" category** — rigorous, self-contained, and checkable; mathematically it is folklore made precise, not new mathematics. Claiming more would be dishonest.
- Proposition 5.2 (twin-specific, conditional): honest formalization of *why* the obstruction applies to twins specifically; hypothesis (uniform two-point Chowla in progressions) is open and clearly flagged.
- Lemmas 5.3/5.5, Observation 5.4: **fully proved, elementary**; classification **original synthesis / exposition**, in the mission's "equivalent formulation + admissible tuple construction" category.
- Sharpest single sentence the legion can stand behind: *for twin primes, the level-of-distribution axis is exhausted — even full EH/GEH provably caps this method family at gap 6 (variational bound $M_2 \le 2\log 2 < 2$ plus the Polymath8b parity ceiling) — and the binding constraint is parity, breakable only by injecting bilinear/type-II information for which no structure on $n(n+2)$ is currently known.* `[ESTABLISHED components; assembly is this dossier's summary judgment]`

### 7.2 Variant ranking (unit 07-10): which is "easier" and why

Ordered from proved to hardest, with the structural reason:

1. **"Some pattern" statements — PROVED.** $m+1$ primes in every admissible $k$-tuple for $k \gg e^{cm}$ (Maynard–Tao); some Polignac number $\le 246$; positive density of Polignac numbers (Pintz). Reason these fell: the sieve certifies *cardinalities* over symmetric positions, never *positions*.
2. **Chen-type approximations — PROVED.** $p + 2 \in \mathcal P_2$; $2p+1 \in \mathcal P_2$ (Sophie Germain analogue); Goldbach's $\mathcal P_2$ version. Reason: $\mathcal P_2$ is on the permitted side of the parity wall.
3. **Twin primes / any single named Polignac difference $d$ — OPEN, parity class.** Twins are the structurally "easiest" member: translation-invariant, sits natively inside the tuple framework (the pair $\{0,2\}$ is a sub-object of every record construction), and has the GEH-conditional bound 6 breathing on it.
4. **Sophie Germain ($p$, $2p+1$) and Cunningham chains — OPEN, parity class, plus an extra handicap.** The forms $n$ and $2n+1$ have different leading coefficients, so the pattern is not a translate family; mixed-slope Maynard-type families still cannot force a *cross-slope* pair (same positional blindness), and the GEH-style conditional endpoints analogous to "6" are less favorable. Chen-side approximations exist (item 2), but the bounded-gap ladder that helps twins has no true analogue.
5. **Full de Polignac (every even $d$) and full Hardy–Littlewood $k$-tuples/Dickson/Schinzel/Bateman–Horn — strictly harder**; each contains the twin conjecture as a special case.

So among the named open variants, **twins is the easiest and the bellwether**: any parity-breaking mechanism for one member of class 3 is expected to sweep the class. `[assessment; components ESTABLISHED]`

### 7.3 Recommended next steps for a future legion `[SPECULATIVE — research directions, not results]`

1. **Bilinear structure for $n(n+2)$.** The only historically successful parity breaks (Friedlander–Iwaniec $x^2+y^4$; Heath-Brown $x^3+2y^3$; Helfgott's root-number program) ran through genuine type-II/bilinear estimates tied to extra algebraic structure (norm forms, root numbers). Target of record: identify *any* bilinear decomposition adapted to the correlation $\sum \Lambda(n)\Lambda(n+2)$ — e.g. via the pair-carrier framing of Observation 5.4 (what minimal diagonal bias evades Proposition 5.2's model class?).
2. **Chowla/Elliott interface.** Post-Tao (log-averaged two-point) and Matomäki–Radziwiłł-era mean-value technology: quantify exactly which strengthening (removal of log-averaging + progression-uniformity, i.e. hypothesis CH of Proposition 5.2) is needed to *certify* the no-go, and conversely whether any *disproof-of-model* pathway exists — the two questions are complementary and both currently open.
3. **Variational frontier below 246.** Practitioner assessment `[VERIFIED-WEB 2026-08-15]` is that modest improvements (toward $\sim 210$) may be extractable from enlarged/vanishing-marginal variational problems at feasible computational cost; worthwhile as an incremental target, with the explicit understanding (Section 3.2) that this axis terminates at 6, not 2.
4. **Formalization.** Proposition 5.1, Lemmas 5.3/5.5 and Observation 5.4 are mechanizable in Lean/Isabelle with current libraries (PNT is formalized); a machine-checked parity no-go would be a genuinely citable artifact of this program.

---

## Bibliography (all real works; details from memory where marked; no invented citations)

1. V. Brun, *La série $1/5+1/7+1/11+1/13+\cdots$ est convergente ou finie*, Bull. Sci. Math. 43 (1919).
2. G. H. Hardy, J. E. Littlewood, *Some problems of 'Partitio Numerorum' III*, Acta Math. 44 (1923).
3. P. A. Clement, *Congruences for sets of primes*, Amer. Math. Monthly 56 (1949).
4. A. Selberg, address, 11th Scandinavian Congress of Mathematicians (1949); parity examples elaborated in *Collected Papers*, vol. II. `[from memory]`
5. E. Bombieri, *On the large sieve*, Mathematika 12 (1965); A. I. Vinogradov, companion result (1965).
6. P. D. T. A. Elliott, H. Halberstam, *A conjecture in prime number theory* (1968). `[from memory]`
7. J.-R. Chen, *On the representation of a larger even integer as the sum of a prime and the product of at most two primes*, Sci. Sinica 16 (1973).
8. H. Halberstam, H.-E. Richert, *Sieve Methods*, Academic Press (1974).
9. D. Hensley, I. Richards, *Primes in intervals*, Acta Arith. 25 (1974). `[from memory]`
10. E. Bombieri, *The asymptotic sieve*, Rend. Accad. Naz. dei XL (1976). `[from memory]`
11. J. Friedlander, A. Granville, *Limitations to the equi-distribution of primes I*, Ann. of Math. 129 (1989).
12. J. Friedlander, A. Granville, A. Hildebrand, H. Maier, *Oscillation theorems…*, J. Amer. Math. Soc. 4 (1991). `[from memory]`
13. J. Friedlander, H. Iwaniec, *The polynomial $x^2+y^4$ captures its primes* and *Asymptotic sieve for primes*, Ann. of Math. 148 (1998).
14. D. R. Heath-Brown, *Primes represented by $x^3+2y^3$*, Acta Math. 186 (2001).
15. H. Helfgott, *Root numbers and the parity problem* (Princeton PhD thesis, 2003) and subsequent papers on parity for cubic forms. `[from memory]`
16. K. Soundararajan, *Small gaps between prime numbers: the work of Goldston–Pintz–Yıldırım*, Bull. AMS 44 (2007).
17. Y. Motohashi, J. Pintz, *A smoothed GPY sieve*, Bull. London Math. Soc. 40 (2008). `[from memory]`
18. D. Goldston, J. Pintz, C. Yıldırım, *Primes in tuples I*, Ann. of Math. 170 (2009), 819–862.
19. J. Friedlander, H. Iwaniec, *Opera de Cribro*, AMS Colloquium Publ. 57 (2010).
20. Y. Zhang, *Bounded gaps between primes*, Ann. of Math. 179 (2014), 1121–1174.
21. D. H. J. Polymath, *New equidistribution estimates of Zhang type*, Algebra & Number Theory 8 (2014).
22. D. H. J. Polymath, *Variants of the Selberg sieve, and bounded intervals containing many primes*, Res. Math. Sci. 1 (2014).
23. J. Maynard, *Small gaps between primes*, Ann. of Math. 181 (2015), 383–413.
24. J. Maynard, *Dense clusters of primes in subsets*, Compositio Math. 152 (2016). `[from memory]`
25. J. Pintz, positive density of Polignac numbers (2013). `[from memory — precise venue not re-verified]`
26. A. Granville, *Primes in intervals of bounded length*, Bull. AMS 52 (2015).
27. T. Tao, *The logarithmically averaged Chowla and Elliott conjectures for two-point correlations*, Forum Math. Pi 4 (2016).
28. D. Klyve, *Explicit bounds on twin primes and Brun's constant*, PhD thesis, Dartmouth (2007). `[from memory]`
29. Polymath wiki, *Bounded gaps between primes* — records table. `[VERIFIED-WEB 2026-08-15]`
30. PrimeGrid / t5k.org (Prime Pages), twin prime record $2996863034895\cdot 2^{1290000}\pm1$. `[VERIFIED-WEB 2026-08-15]`

*End of LEGION 07 dossier.*
