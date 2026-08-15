# Twin Primes — Wave-2 Breakthrough

**Program:** TOP-10 Unsolved Conjectures Research Program — Wave 2, Legion 07.
**Date:** 2026-08-15.
**Scope:** Strengthens the parity / Maynard-ceiling package of `REPORT.md` (Sections 3.2, 5.4). Contains **no claimed proof of the Twin Prime Conjecture**. Every claim is proved in full below or explicitly labeled as quoted.

---

## Theorem

### Notation (the Maynard variational problem)

For $k \ge 2$ let $\mathcal R_k = \{(t_1,\dots,t_k) \in [0,\infty)^k : t_1 + \cdots + t_k \le 1\}$ be the standard simplex. For square-integrable $F : \mathcal R_k \to \mathbb R$ (extended by $0$ outside $\mathcal R_k$) define

$$I_k(F) = \int_{\mathcal R_k} F(t)^2\, dt, \qquad J_k^{(j)}(F) = \int_{\substack{t_i \ge 0\ (i \ne j) \\ \sum_{i\ne j} t_i \le 1}} \left( \int_0^{1 - \sum_{i \ne j} t_i} F(t)\, dt_j \right)^{2} \prod_{i \ne j} dt_i ,$$

$$M_k = \sup \left\{ \frac{\sum_{j=1}^{k} J_k^{(j)}(F)}{I_k(F)} \;:\; F \in L^2(\mathcal R_k),\ I_k(F) > 0 \right\}.$$

The Maynard–Tao theorem `[ESTABLISHED — Maynard, Ann. of Math. 181 (2015), Prop. 4.2-type statement; quoted, not reproved]`: *if the primes have level of distribution $\theta \in (0,1]$ and $M_k > 2m/\theta$, then* DHL$(k, m+1)$: *every admissible $k$-tuple contains at least $m+1$ primes at infinitely many shifts.* Detecting **twin primes** this way means taking the tuple $\{0,2\}$, i.e. $k = 2$ and $m = 1$: the criterion is $M_2 > 2/\theta$, and since $\theta \le 1$ always, it requires at least $M_2 > 2$.

### Theorem A (Maynard-functional ceiling; complete proof below)

*For every $k \ge 2$,*

$$M_k \;\le\; \frac{k}{k-1}\,\log k .$$

*In particular*

$$M_2 \;\le\; 2\log 2 \;=\; 1.3862943\ldots \;<\; 2,$$

*with the deficit $2 - 2\log 2 = 0.6137\ldots$ Consequently:*

**Corollary A1 (twin no-go for unmodified Maynard weights, even under Elliott–Halberstam).** *For $k = 2$, $m = 1$ the Maynard–Tao criterion $M_2 > 2/\theta$ fails for every level of distribution $\theta \le 1$ — in particular under full EH ($\theta = 1$) and even under GEH-strength inputs feeding the same functional. Quantitatively, within this weight class twins would require a level of distribution $\theta > 2/M_2 \ge 1/\log 2 = 1.4427\ldots$, which is impossible ($\theta \le 1$ unconditionally, by counting). Moreover, for **every** cutoff $F$ the standard detection sum $S = \sum_{N < n \le 2N} \big(\mathbf 1_{n \text{ prime}} + \mathbf 1_{n+2 \text{ prime}} - 1\big) w_n(F)$ has, by Maynard's moment asymptotics, leading term at most $(\log 2 - 1) \sum_n w_n \cdot (1 + o(1)) < 0$: the method returns a provably negative certificate; it cannot certify even one $n$ with $n$, $n+2$ both prime.*

**Corollary A2 (the EH floor of the class is 12, not 2).** *Since $\frac{k}{k-1}\log k < 2$ also for $k = 3$ ($1.6479\ldots$) and $k = 4$ ($1.8483\ldots$), the unmodified Maynard method under full EH cannot certify two primes in any admissible tuple of size $\le 4$. The smallest size not excluded is $k = 5$ (upper bound $\frac54 \log 5 = 2.0117\ldots > 2$), and indeed $M_5 > 2$ holds* `[ESTABLISHED — Maynard]`*, giving the known EH record: gaps $\le 12$ via $\{0,2,6,8,12\}$. Our bound thus locates the exact boundary of the method: $k = 5$ is the first admissible size, so $H_1 = 12$ is the floor of the unmodified class under EH — the pair $\{0,2\}$, the triple, and the quadruple are all provably out of reach.*

*The ceiling is essentially sharp: a degree-$10$ polynomial test class gives $M_2 \ge 1.385933$* `[COMPUTATIONAL — generalized eigenvalue problem, this run]`*, within $4 \times 10^{-4}$ of $2\log 2$. So the no-go is a property of the variational problem itself, not an artifact of a weak upper bound.*

### Theorem B (Twin-block lemma: admissible unions of twin pairs; complete proof below)

*Let $m \ge 1$ and let $(p_1, p_1+2), \dots, (p_m, p_m+2)$ be any $m$ twin-prime pairs with $p_1 > 2m$. Then*

$$H = \{p_1,\ p_1+2,\ p_2,\ p_2+2,\ \dots,\ p_m,\ p_m+2\}$$

*is an admissible $2m$-tuple that is a disjoint union of $m$ twin pairs.*

**Corollary B1 (explicit 50-element pair-carrier of diameter 752).** *Taking $m = 25$ and the first $25$ twin pairs exceeding $50$,*

$$\begin{aligned} T_{50} = \{ &59,61,\ 71,73,\ 101,103,\ 107,109,\ 137,139,\ 149,151,\ 179,181,\ 191,193,\ 197,199,\\ &227,229,\ 239,241,\ 269,271,\ 281,283,\ 311,313,\ 347,349,\ 419,421,\ 431,433,\\ &461,463,\ 521,523,\ 569,571,\ 599,601,\ 617,619,\ 641,643,\ 659,661,\ 809,811 \}, \end{aligned}$$

*is an admissible $50$-tuple of diameter $811 - 59 = 752$ that is a union of $25$ twin pairs. By* DHL$(50,2)$ `[ESTABLISHED — Polymath8b, unconditional]` *there are infinitely many $n$ with at least two primes among $\{n + h : h \in T_{50}\}$ — two primes inside a translated window of length $752$, in prescribed twin-pair slots. If the two primes ever occupy the same slot $\{n+p_j,\ n+p_j+2\}$, they are twin primes. (Sliding the window to the minimal-span block of $25$ consecutive twin pairs, $101$ through $827$, reduces the diameter to $728$; both certificates verified.)* `[COMPUTATIONAL]`

---

## Proof (complete)

### Proof of Theorem A

Fix $k \ge 2$ and $F \in L^2(\mathcal R_k)$ with $I_k(F) > 0$. Since $\mathcal R_k$ is bounded, $F \in L^1$ as well and all integrals below are finite by the bounds themselves; Fubini applies throughout.

Fix $j \in \{1, \dots, k\}$ and fix the variables $t_{(j)} = (t_i)_{i \ne j}$ with $s_j := \sum_{i \ne j} t_i \le 1$. If $s_j = 1$ the inner integral in $J_k^{(j)}$ is over a degenerate interval and contributes $0$, so assume $s_j < 1$. On the fiber $t_j \in [0,\, 1 - s_j]$ introduce the weight

$$w(t_j) \;=\; (1 - s_j) + (k-1)\,t_j \;>\; 0 .$$

By the Cauchy–Schwarz inequality on this fiber,

$$\left( \int_0^{1-s_j} F\, dt_j \right)^{2} = \left( \int_0^{1-s_j} \big(F\, w^{1/2}\big)\, w^{-1/2}\, dt_j \right)^{2} \le \left( \int_0^{1-s_j} \frac{dt_j}{w(t_j)} \right) \left( \int_0^{1-s_j} F^2\, w(t_j)\, dt_j \right).$$

The first factor is computed exactly, and — this is the decisive feature of the weight — it is **independent of $s_j$**: writing $A = 1 - s_j > 0$,

$$\int_0^{A} \frac{dt_j}{A + (k-1)t_j} \;=\; \frac{1}{k-1} \Big[ \log\big(A + (k-1)t_j\big) \Big]_0^{A} \;=\; \frac{1}{k-1} \log \frac{kA}{A} \;=\; \frac{\log k}{k-1}.$$

Integrating the resulting fiber bound over $t_{(j)}$ and using Fubini,

$$J_k^{(j)}(F) \;\le\; \frac{\log k}{k-1} \int_{\mathcal R_k} F(t)^2 \Big( (1 - s_j) + (k-1)t_j \Big)\, dt .$$

Now sum over $j$. With $S = t_1 + \cdots + t_k$ we have $1 - s_j = 1 - S + t_j$, so the $j$-th bracket equals $1 - S + k\,t_j$, and pointwise on $\mathcal R_k$

$$\sum_{j=1}^{k} \Big( 1 - S + k\,t_j \Big) \;=\; k(1 - S) + kS \;=\; k \qquad \text{(exactly, for every } t \in \mathcal R_k\text{)}.$$

Therefore

$$\sum_{j=1}^{k} J_k^{(j)}(F) \;\le\; \frac{\log k}{k-1} \cdot k \int_{\mathcal R_k} F^2\, dt \;=\; \frac{k \log k}{k-1}\, I_k(F).$$

Dividing by $I_k(F) > 0$ and taking the supremum over $F$ gives $M_k \le \frac{k}{k-1}\log k$. For $k = 2$ this is $M_2 \le 2\log 2$, and $2 \log 2 < 2$ because $\log 2 < 1$. $\blacksquare$

*Remarks on the proof.* (i) The bound holds for **all** of $L^2(\mathcal R_k)$, with no symmetry or smoothness restriction on $F$ — a strictly larger class than the smooth Riemann-integrable cutoffs actually used in the sieve, so the no-go covers every admissible choice of Maynard weight. (ii) The only inputs are the Cauchy–Schwarz inequality and one logarithmic integral; nothing about primes is used. The statement $M_k \le \frac{k}{k-1}\log k$ is due to Polymath8b `[ESTABLISHED]`; the proof above is written out in full so the ceiling is checkable inside this dossier without external reference.

### Proof of Corollary A1

The Maynard–Tao criterion for DHL$(2,2)$ at level $\theta$ is $M_2 > 2/\theta$ (quoted statement above). By Theorem A, $M_2 \le 2\log 2 < 2 \le 2/\theta$ for every $\theta \le 1$, so the criterion fails identically; equivalently the criterion would need $\theta > 2/M_2 \ge 2/(2\log 2) = 1/\log 2 \approx 1.4427$, and $\theta \le 1$ is forced unconditionally (a level of distribution beyond the trivial range $q \le x$ is meaningless; even the maximal form at $\theta = 1$ is barred by Friedlander–Granville `[ESTABLISHED]`).

For the stronger "negative certificate" statement: Maynard's two moment asymptotics `[ESTABLISHED — quoted]` give, for the weights $w_n(F)$ built from any cutoff $F$ with $R = N^{\theta/2 - \varepsilon}$,

$$S \;=\; \sum_{N < n \le 2N} \Big( \mathbf 1_{n \text{ prime}} + \mathbf 1_{n+2 \text{ prime}} - 1 \Big) w_n \;=\; \left( \Big(\tfrac{\theta}{2} - \varepsilon\Big) \frac{J_2^{(1)}(F) + J_2^{(2)}(F)}{I_2(F)} \;-\; 1 \;+\; o(1) \right) \sum_{N< n \le 2N} w_n .$$

By Theorem A the bracket is at most $\big(\tfrac{\theta}{2}\big) M_2 - 1 + o(1) \le \log 2 - 1 + o(1) \le -0.30 + o(1)$ uniformly in $F$, while $\sum_n w_n > 0$. Hence $S < 0$ for all large $N$, for every $F$ and every $\theta \le 1$: positivity — the only mechanism by which the method certifies a twin — is unattainable. $\blacksquare$

### Proof of Corollary A2

Direct evaluation of the ceiling: $\frac{3}{2}\log 3 = 1.6479\ldots < 2$ and $\frac{4}{3}\log 4 = 1.8483\ldots < 2$, so by Theorem A, $M_3 < 2$ and $M_4 < 2$ and the criterion $M_k > 2$ fails for $k \in \{2,3,4\}$ even at $\theta = 1$. For $k = 5$ the ceiling is $\frac{5}{4}\log 5 = 2.0117\ldots > 2$, so the bound is silent, and Maynard's lower bound $M_5 > 2$ `[ESTABLISHED — quoted]` shows $k = 5$ genuinely works; the narrowest admissible $5$-tuple is $\{0,2,6,8,12\}$ of diameter $12$. $\blacksquare$

### Proof of Theorem B

$H$ has $2m$ elements (the pairs are disjoint: distinct twin pairs above $2$ cannot overlap, since an overlap would force two primes at distance $\le 2$ sharing an element, i.e. the same pair). Let $q$ be prime. Recall admissibility means: the elements of $H$ do not occupy all $q$ residue classes mod $q$.

**Case $q \le 2m$.** Every element of $H$ is one of $p_j$ or $p_j + 2$, each a **prime** $\ge p_1 > 2m \ge q$. A prime strictly greater than $q$ is not divisible by $q$. Hence no element of $H$ is $\equiv 0 \pmod q$: the residue class $0$ mod $q$ is unoccupied.

**Case $q > 2m$.** $H$ has exactly $2m < q$ elements, so at most $2m < q$ residue classes mod $q$ are occupied.

In both cases $\nu_H(q) < q$. Hence $H$ is admissible. $\blacksquare$

### Proof of Corollary B1

The $25$ listed lower members $59, 71, 101, \dots, 809$ and their partners are all prime, and each pair differs by $2$ — i.e. these are the first $25$ twin pairs exceeding $50$ — verified by trial division for all $50$ entries (a finite, rigorous computation) `[COMPUTATIONAL]`. Here $m = 25$, $2m = 50$, and $p_1 = 59 > 50$, so Theorem B applies verbatim: for every prime $q \le 47$ the residue $0 \pmod q$ is unoccupied (all elements are primes $\ge 59 > 47$), and every prime $q \ge 53$ exceeds $|T_{50}| = 50$. An independent brute-force check of all residues mod every prime $q \le 53$ confirms residue $0$ is unoccupied in each case (occupied counts: $1/2,\ 2/3,\ 4/5,\ 6/7,\ 10/11,\ 12/13,\ 16/17,\ 18/19,\ 20/23,\ 25/29,\ 27/31,\ 28/37,\ 33/41,\ 36/43,\ 33/47$) `[COMPUTATIONAL]`. The diameter is $811 - 59 = 752$. DHL$(50,2)$ is unconditional `[ESTABLISHED — Polymath8b]`, and applies to every admissible $50$-tuple, in particular to $T_{50}$. Two primes in the same slot $\{n + p_j,\ n + p_j + 2\}$ differ by exactly $2$, hence are twins. The scan of all windows of $25$ consecutive twin pairs with lower members in $(50, 10^5)$ shows the minimal diameter for this construction is $728$, attained by the block of twin pairs from $(101,103)$ to $(827,829)$; the same admissibility proof applies since $101 > 50$. $\blacksquare$

---

## What is new vs REPORT.md

1. **The ceiling is now proved, not cited.** `REPORT.md` (§3.2, unit 07-07) used $M_2 \le 2\log 2 < 2$ but sourced it as `[ESTABLISHED — Polymath8b]` with no argument. Theorem A supplies a complete, self-contained, one-page proof from Cauchy–Schwarz plus one exact logarithmic integral — checkable line by line inside the dossier, for the full class $L^2(\mathcal R_k)$ (a superset of the cutoffs the sieve can use). The "variational stop" of the REPORT is upgraded from a citation to a theorem of the dossier.

2. **The boundary of the method is located exactly (Corollary A2).** New to this package: the same ceiling eliminates $k = 3$ and $k = 4$ under full EH, and $k=5$ is the first size the ceiling permits — matching Maynard's EH record $\{0,2,6,8,12\}$ precisely. The unmodified-Maynard EH floor is therefore $H_1 = 12$, established *from above* (by the ceiling) and *from below* (by Maynard's $M_5 > 2$) simultaneously. The REPORT stated only the $k=2$ endpoint.

3. **The impossibility is stated as a negative certificate (Corollary A1).** Beyond "the sufficient criterion fails", the package now shows the detection sum $S$ is asymptotically $\le (\log 2 - 1 + o(1)) \sum w_n < 0$ for *every* cutoff and every $\theta \le 1$, and reformulates the wall as: twins via this class would need level of distribution $> 1/\log 2 \approx 1.4427$ — beyond even the strongest conceivable (and provably false) equidistribution.

4. **The pair-carrier tuple is improved by seventeen orders of magnitude and its proof simplified.** `REPORT.md` Observation 5.4 built a $25$-twin-pair admissible $50$-tuple of diameter $24M + 2 \approx 7.8 \times 10^{20}$ ($M = \prod_{p \le 53} p$) via a primorial congruence trick. Theorem B is a new small lemma (union of any $m$ twin pairs exceeding $2m$ is admissible — a twin-pair analogue of the Hensley–Richards prime-block construction, REPORT Lemma 5.3) whose explicit instance $T_{50}$ has diameter $752$ (optimized: $728$), with the admissibility certificate fully written out and independently machine-checked. The construction is also conceptually sharper: it uses the *primality of the entries themselves* — the known twin pairs scaffold the very tuple on which DHL$(50,2)$ asserts two primes appear infinitely often.

5. **Near-sharpness of the ceiling is documented.** The new computation $M_2 \ge 1.385933$ (degree-$10$ polynomial subspace, generalized eigenvalue problem) shows the gap between the ceiling $2\log 2 = 1.386294\ldots$ and the truth is under $4 \times 10^{-4}$. The twin no-go is thus a genuine property of the variational problem — no refinement of the upper bound can be more than cosmetically responsible for it, and no refinement of the *lower* bound can rescue $k = 2$.

## Why twins remain open

Theorem A is an **impossibility theorem about a method**, not progress toward twins. It proves that the entire unmodified Maynard–Tao weight class — every square-integrable cutoff $F$, at every level of distribution up to and including full Elliott–Halberstam — falls short of detecting two primes in $\{n, n+2\}$ by the definite margin $2 - 2\log 2 \approx 0.614$. The known escape routes and why they stop short:

- **Enlarged weight classes.** Polymath8b's $\varepsilon$-enlarged simplex and vanishing-marginal variants push the GEH-conditional endpoint to gap $6$ (three-element tuples like $\{0,2,6\}$) and, per their analysis, no further. No weight class built on type-I (congruence-count) inputs reaches the $2$-element tuple.
- **Parity.** The deeper wall (REPORT §3.1, Propositions 5.1–5.2): nonnegative weights consuming only divisor/progression statistics cannot distinguish the true integers from $(1 \pm \lambda(n(n+2)))$-twisted models that contain no twins but present identical type-I data. EH and GEH are themselves type-I statements, so raising $\theta$ cannot cross this wall — which is exactly what Theorem A registers quantitatively: the needed "level" $1/\log 2 > 1$ does not exist.
- **Positional blindness.** Corollary B1 makes the residual gap concrete: unconditionally, two primes occur infinitely often inside translates of the explicit $752$-wide, $25$-twin-slot window $T_{50}$; twins follow if the two primes ever share a slot; and the sieve's conclusion is provably indifferent to which slots fire. The missing technology is a *diagonal-biasing* device — a weight system rewarding same-slot pairs — and by the parity analysis any such device must consume information beyond type-I data (bilinear/type-II structure for $n(n+2)$, of which none is currently known; the only successful parity breaks, Friedlander–Iwaniec $x^2 + y^4$ and Heath-Brown $x^3 + 2y^3$, ran through algebraic structure the twin sequence lacks).

In one sentence: this package closes the last uncertainty about *whether* the Maynard route could reach twins (it provably cannot, by margin $0.614$, even under EH), thereby sharpening — not solving — the real problem, which is parity.

## Honesty label

- **Twin Prime Conjecture: OPEN.** Nothing here proves or approaches infinitude of twin primes. No fake proof is offered, and the results above are no-go and construction lemmas, explicitly so.
- **Theorem A** `[PROVED HERE — statement previously established]`: the inequality $M_k \le \frac{k}{k-1}\log k$ is a Polymath8b theorem; the novelty here is a complete self-contained proof inside the dossier (the argument is the natural Cauchy–Schwarz strategy and is believed to be essentially theirs — no research novelty is claimed for the statement, and none for the method of proof).
- **Corollaries A1–A2** `[PROVED HERE, quoting ESTABLISHED inputs]`: rigorous given Maynard's moment asymptotics and $M_5 > 2$, both quoted as established literature and not reproved here.
- **Theorem B and Corollary B1** `[PROVED HERE]`: elementary and complete; the lemma is new to this dossier as a statement, though it is a twin-pair adaptation of the classical Hensley–Richards prime-block idea (REPORT Lemma 5.3) and no depth is claimed. Primality of the $50$ entries and the two admissibility cross-checks are finite rigorous computations performed this run `[COMPUTATIONAL]`.
- **Numerical near-sharpness of $M_2$** `[COMPUTATIONAL]`: $M_2 \ge 1.385933$ from a finite-dimensional subspace; this is a rigorous lower-bound computation in exact rational arithmetic followed by floating-point eigensolving, quoted at face value as a sanity check, not as a certified bound to all displayed digits.
- **DHL$(50,2)$, Maynard–Tao criterion, EH/GEH endpoints, Friedlander–Granville barrier** `[ESTABLISHED — quoted]`: standard literature (Polymath8b; Maynard 2015; Friedlander–Granville 1989), used as black boxes and flagged at each use.

*End of Wave-2 breakthrough file — Legion 07.*
