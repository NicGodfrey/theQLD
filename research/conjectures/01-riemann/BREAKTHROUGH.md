# Riemann — Wave-2 Breakthrough

**Legion:** Wave-2 Legion 01 (Riemann Hypothesis)
**Date:** 2026-08-15
**Builds on:** `REPORT.md` (this directory), specifically Proposition B (§5) and specialist angle 01-01.
**Code:** `code/li_coefficients.py`, `code/verify_theorem.py` (both executed in this run; logs `code/full_run.log`, `code/verify_run.log`; data `code/li_lambda.csv`).

Throughout, \(\xi(s)=\tfrac12 s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s)\) is the completed zeta function, entire of order 1, real on \(\mathbb{R}\), with \(\xi(s)=\xi(1-s)\), \(\xi(1)=\tfrac12\), and zero set equal to the non-trivial zeros of \(\zeta\) (**Known**, Titchmarsh Ch. 2). For an entire function \(f\) of this type with zero multiset \(Z(f)\subset\{0<\mathrm{Re}\,s<1\}\), its **Li coefficients** are

\[
\lambda_n(f)\;=\;\sum_{\rho\in Z(f)}\Bigl(1-\bigl(1-\tfrac1\rho\bigr)^{n}\Bigr),
\qquad n\ge 1,
\]

summed with multiplicity in the symmetric order \(\lim_{T\to\infty}\sum_{|\mathrm{Im}\,\rho|\le T}\) (conjugate pairs grouped; convergence is proved in Step 4 below and is part of the claim). Write \(\lambda_n=\lambda_n(\xi)\). Li's criterion (**Known**, Li 1997): RH \(\iff \lambda_n\ge 0\) for **all** \(n\ge 1\).

---

## Theorem (one statement only)

**Theorem (blindness of finite Li positivity, with explicit constants).**
Assume the computational input
\[
(V):\qquad \lambda_n \;\ge\; 0.0230\,n \qquad\text{for all } 1\le n\le 2000,
\]
verified in this run at 40-digit working precision with two independent cross-checks (see *Computational input* below; the minimum of \(\lambda_n/n\) on this range is \(\lambda_1 = 1+\tfrac\gamma2-\tfrac12\log 4\pi = 0.0230957\ldots\), attained at \(n=1\)). Then for every \(\beta_0\in(\tfrac12,1)\) and every \(\gamma_0\ge 8\), the function
\[
\xi^{*}(s)\;=\;\xi(s)\prod_{\rho'\in Q}\Bigl(1-\frac{s}{\rho'}\Bigr),
\qquad
Q=\{\beta_0\pm i\gamma_0,\;1-\beta_0\pm i\gamma_0\},
\]
has the following properties:

1. \(\xi^{*}\) is entire of order 1, satisfies \(\xi^{*}(s)=\xi^{*}(1-s)\) and \(\overline{\xi^{*}(\bar s)}=\xi^{*}(s)\), is real on the real axis and on the critical line, and its zero multiset is exactly \(Z(\xi)\uplus Q\), all zeros lying in the open strip \(0<\mathrm{Re}\,s<1\); in particular \(\xi^{*}\) has **four zeros off the critical line at height \(\gamma_0\)**;
2. its Li coefficients are \(\lambda_n(\xi^{*})=\lambda_n+T_n\) with \(T_n=\sum_{\rho'\in Q}\bigl(1-(1-1/\rho')^{n}\bigr)\), and for all \(1\le n\le\gamma_0^{2}\),
\[
T_n\;\ge\;-\,2(\sqrt e-1)\,\frac{n}{\gamma_0^{2}}\;>\;-\,1.29745\,\frac{n}{\gamma_0^{2}},
\qquad
|T_n|\;\le\;\min\Bigl(4\sqrt e\,\frac{n}{\gamma_0},\;\frac{4n+3.3\,n^{2}}{\gamma_0^{2}}\Bigr);
\]
3. consequently \(\lambda_n(\xi^{*})>0\) for every \(1\le n\le\min(2000,\lfloor\gamma_0^{2}\rfloor)\).

In particular, for every \(N\le 2000\): no criterion that certifies absence of off-critical-line zeros using only the properties in (1) together with the positivity \(\lambda_1\ge0,\dots,\lambda_N\ge 0\) can exclude off-line zeros at any height \(\ge\max(8,\sqrt N)\) — the detection height of finite Li positivity is at most of order \(\sqrt N\), not \(N\).

---

## Proof (complete, elementary or standard analysis)

**Facts imported.** (i) The structural facts about \(\xi\) stated in the preamble (**Known**). (ii) The classical fact that \(\zeta\) has no non-trivial zero with \(0<|\mathrm{Im}\,\rho|\le 14\) (**Known**; Gram–Backlund era, used *only* in the error analysis of the numerics, never in the theorem's logic). (iii) Li's lemma that the zero-sum \(\lambda_n\) equals the Taylor coefficient \(\frac{d}{dz}\log\xi\bigl(\tfrac1{1-z}\bigr)=\sum_{n\ge0}\lambda_{n+1}z^{n}\) (**Known**, Li 1997; Bombieri–Lagarias 1999 — used only to interpret the numerical computation of \((V)\)). (iv) The computational input \((V)\) (**Computational**, this run).

Throughout, for \(\rho'\in Q\) write \(w=w(\rho')=1-1/\rho'\) and note
\[
|w|^{2}\;=\;\frac{|\rho'-1|^{2}}{|\rho'|^{2}}\;=\;1-\frac{2\,\mathrm{Re}\,\rho'-1}{|\rho'|^{2}} .
\tag{1}
\]

### Step 1 — Structure of \(\xi^{*}\) (part 1 of the Theorem)

Let \(q(s)=\prod_{\rho'\in Q}(1-s/\rho')\), a polynomial of degree 4. Since \(Q\) is closed under conjugation, grouping conjugate pairs gives
\[
q(s)=\Bigl(1+\frac{s^{2}-2\beta_0 s}{\beta_0^{2}+\gamma_0^{2}}\Bigr)
\Bigl(1+\frac{s^{2}-2(1-\beta_0)s}{(1-\beta_0)^{2}+\gamma_0^{2}}\Bigr),
\tag{2}
\]
which has real coefficients; hence \(\overline{q(\bar s)}=q(s)\). Since \(Q\) is closed under \(\rho'\mapsto 1-\rho'\), pairing each root with its reflection gives, factor by factor,
\[
\Bigl(1-\frac{1-s}{\rho'}\Bigr)\Bigl(1-\frac{1-s}{1-\rho'}\Bigr)
=\frac{(s+\rho'-1)(s-\rho')}{\rho'(1-\rho')}
=\Bigl(1-\frac{s}{\rho'}\Bigr)\Bigl(1-\frac{s}{1-\rho'}\Bigr),
\]
so \(q(1-s)=q(s)\). Multiplying by \(\xi\): \(\xi^{*}\) is entire (entire × polynomial) of order 1 (order is unchanged by a polynomial factor), inherits \(\xi^{*}(s)=\xi^{*}(1-s)\) and \(\overline{\xi^{*}(\bar s)}=\xi^{*}(s)\), and is real on \(\mathbb{R}\). On the critical line, \(s=\tfrac12+it\) gives \(1-s=\bar s\), so \(\xi^{*}(s)=\xi^{*}(1-s)=\xi^{*}(\bar s)=\overline{\xi^{*}(s)}\), i.e. \(\xi^{*}\) is real there. The zero multiset of a product is the union of the zero multisets, so \(Z(\xi^{*})=Z(\xi)\uplus Q\); the four points of \(Q\) have real parts \(\beta_0\ne\tfrac12\) and \(1-\beta_0\ne\tfrac12\) inside \((0,1)\) and imaginary parts \(\pm\gamma_0\). This proves part 1. ∎

### Step 2 — Additivity of Li coefficients, in both senses

In the zero-sum sense the additivity \(\lambda_n(\xi^{*})=\lambda_n+T_n\) is immediate: \(Q\) is a finite multiset, so adjoining it adds the finite sum \(T_n\), which is real because the terms for \(\rho'\) and \(\bar\rho'\) are conjugates.

For completeness we also check additivity in Li's derivative sense, because the two senses attach the exponent \(n\) to different roots. For a single factor \(u(z)=1-\frac{1}{\rho(1-z)}\) (i.e. \(1-s/\rho\) at \(s=1/(1-z)\)), factor
\[
u(z)=\frac{\rho-1}{\rho}\cdot\frac{1-\frac{\rho}{\rho-1}z}{1-z},
\qquad
\frac{d}{dz}\log u(z)=\frac{1}{1-z}-\frac{\frac{\rho}{\rho-1}}{1-\frac{\rho}{\rho-1}z}
=\sum_{n\ge0}\Bigl[1-\Bigl(\frac{\rho}{\rho-1}\Bigr)^{n+1}\Bigr]z^{n},
\]
valid near \(z=0\) (note \(q(1)=\prod(1-1/\rho')\ne0\) since \(1\notin Q\)). Since \(\frac{\rho}{\rho-1}=1-\frac{1}{1-\rho}\), the derivative-sense coefficient of the factor with root \(\rho\) equals the **zero-sum term of the reflected root** \(1-\rho\). Because \(Q\) is invariant under \(\rho\mapsto1-\rho\), summing over \(Q\) gives the same total \(T_{n+1}\) in both senses. (This is why the reflection symmetry of \(Q\) is essential and not cosmetic.) ∎

### Step 3 — The one-sided bound (the heart of the theorem)

Split \(Q\) into the *right pair* \(\beta_0\pm i\gamma_0\) (real part \(>\tfrac12\)) and the *left pair* \((1-\beta_0)\pm i\gamma_0\) (real part \(<\tfrac12\)).

**Right pair.** By (1) with \(\mathrm{Re}\,\rho'=\beta_0>\tfrac12\): \(|w|\le1\). Hence each term
\[
1-\mathrm{Re}(w^{n})\;\ge\;1-|w|^{n}\;\ge\;0 .
\tag{3}
\]

**Left pair.** By (1) with \(\mathrm{Re}\,\rho'=1-\beta_0<\tfrac12\) and \(|\rho'|^{2}\ge\gamma_0^{2}\):
\[
|w|^{2}=1+\frac{2\beta_0-1}{(1-\beta_0)^{2}+\gamma_0^{2}}\;\le\;1+\frac{1}{\gamma_0^{2}},
\qquad\text{so}\qquad
|w|^{n}\le\Bigl(1+\gamma_0^{-2}\Bigr)^{n/2}\le e^{\,n/(2\gamma_0^{2})}.
\tag{4}
\]
Each left term obeys the **hard floor**
\[
1-\mathrm{Re}(w^{n})\;\ge\;1-|w|^{n}\;\ge\;-\bigl(e^{\,n/(2\gamma_0^{2})}-1\bigr).
\tag{5}
\]
Since \(u\mapsto (e^{u}-1)/u\) is increasing, for \(0\le u\le\tfrac12\) (i.e. \(n\le\gamma_0^{2}\), \(u=n/(2\gamma_0^{2})\)) we have \(e^{u}-1\le 2(\sqrt e-1)\,u\). Summing (3) twice and (5) twice:
\[
T_n\;\ge\;-2\bigl(e^{\,n/(2\gamma_0^{2})}-1\bigr)\;\ge\;-2\cdot 2(\sqrt e-1)\cdot\frac{n}{2\gamma_0^{2}}
\;=\;-2(\sqrt e-1)\,\frac{n}{\gamma_0^{2}}\;>\;-1.29745\,\frac{n}{\gamma_0^{2}} .
\tag{6}
\]

*Remark (why \(\sqrt N\), not \(N\)).* The first-order effect of a zero at height \(\gamma_0\) on \(\lambda_n\) is the **phase** rotation \(n\arg w\approx n/\gamma_0\), of size \(O(n/\gamma_0)\) — this is what the folklore estimate (REPORT.md, Prop. B) tracks. But by (3) and (5) the phase can only push a term *up* (towards \(2\)); it can push it *down* only to the floor \(1-|w|^{n}\), and the modulus excess \(|w|-1\) is **second order**, \(O(1/\gamma_0^{2})\), by (1). Downward perturbation is therefore \(O(n/\gamma_0^{2})\), quadratically smaller than the folklore tail \(O(n/\gamma_0)\).

### Step 4 — Two-sided bounds and convergence

For any \(\rho'\in Q\), \(|1-w|=1/|\rho'|\le1/\gamma_0\), and \(\max(1,|w|)^{k}\le e^{k/(2\gamma_0^{2})}\le\sqrt e\) for \(k\le n\le\gamma_0^{2}\) by (4). Telescoping \(w^{n}-1=(w-1)(w^{n-1}+\dots+1)\):
\[
|1-w^{n}|\;\le\;n\,|1-w|\max(1,|w|)^{n-1}\;\le\;\sqrt e\;\frac{n}{\gamma_0},
\qquad\text{so}\qquad
|T_n|\le 4\sqrt e\,\frac{n}{\gamma_0}\;(<6.595\,\tfrac n{\gamma_0}).
\tag{7}
\]
For the sharper bound, use conjugate-pair cancellation. Set \(E(\rho')=(1-w^{n})-n(1-w)=(1-w)\sum_{k=0}^{n-1}(w^{k}-1)\); by the same telescoping, \(|w^{k}-1|\le\sqrt e\,k/\gamma_0\), whence
\[
|E(\rho')|\;\le\;\frac1{\gamma_0}\cdot\sqrt e\,\frac{n^{2}}{2\gamma_0}\;=\;\frac{\sqrt e\,n^{2}}{2\gamma_0^{2}} .
\]
A conjugate pair contributes \(2n\,\mathrm{Re}(1/\rho')+2\,\mathrm{Re}\,E(\rho')\), and \(\mathrm{Re}(1/\rho')=\mathrm{Re}(\rho')/|\rho'|^{2}\le1/\gamma_0^{2}\). Summing the two pairs:
\[
|T_n|\;\le\;\frac{4n}{\gamma_0^{2}}+\frac{2\sqrt e\,n^{2}}{\gamma_0^{2}}
\;\le\;\frac{4n+3.3\,n^{2}}{\gamma_0^{2}}
\qquad(1\le n\le\gamma_0^{2}).
\tag{8}
\]
The same pair estimate applied to the zeros of \(\xi\) itself (for fixed \(n\), all but finitely many zeros satisfy \(|\mathrm{Im}\,\rho|^{2}\ge n\)) shows each pair contributes \(O_n(\gamma^{-2})\); since \(\sum_{\rho}|\mathrm{Im}\,\rho|^{-2}<\infty\) (**Known**, from \(N(T)\ll T\log T\)), the defining zero-sum for \(\lambda_n\) (and for \(\lambda_n(\xi^{*})\)) converges absolutely after pairing. This completes part 2. ∎

### Step 5 — Positivity (part 3)

For \(1\le n\le\min(2000,\lfloor\gamma_0^{2}\rfloor)\), combine \((V)\) with (6):
\[
\lambda_n(\xi^{*})\;=\;\lambda_n+T_n\;\ge\;0.0230\,n-1.29745\,\frac{n}{\gamma_0^{2}}
\;=\;n\Bigl(0.0230-\frac{1.29745}{\gamma_0^{2}}\Bigr)\;>\;0
\]
whenever \(\gamma_0^{2}>1.29745/0.0230=56.41\), which holds for all \(\gamma_0\ge 7.6\), in particular \(\gamma_0\ge8\). ∎

**Proof of the final clause.** Given \(N\le2000\) and any real height \(h\ge\max(8,\sqrt N)\), take \(\gamma_0=h\) and any \(\beta_0\in(\tfrac12,1)\). Then \(N\le\gamma_0^{2}\), so \(\xi^{*}\) satisfies every property listed in part 1 and \(\lambda_n(\xi^{*})>0\) for \(1\le n\le N\), yet has zeros off the line at height exactly \(h\). A criterion of the stated form that certified "no off-line zeros at height \(h\)" would therefore be contradicted by \(\xi^{*}\); since \(h\ge\max(8,\sqrt N)\) was arbitrary, no height \(\ge\max(8,\sqrt N)\) can be certified. ∎

### Corollary — even infinitely many off-line zeros escape finite Li positivity

*For every \(93\le N\le2000\) and any choice \(\beta_j\in(\tfrac12,1)\), the function*
\[
\xi^{**}(s)=\xi(s)\prod_{j=1}^{\infty}q_j(s),
\qquad q_j=\text{the quadruple polynomial (2) at }(\beta_j,\gamma_j),\quad \gamma_j=\lceil\sqrt N\rceil\,j,
\]
*is entire of order 1 with all the structural properties of part 1, has **infinitely many** zeros off the critical line (four at every height \(\gamma_j\), \(j\ge1\); about \(4T/\sqrt N\) of them up to height \(T\)), and satisfies \(\lambda_n(\xi^{**})>0\) for all \(1\le n\le N\).*

**Proof.** Writing \(a_j=(|s|^{2}+2|s|)/\gamma_j^{2}\), (2) gives \(|q_j(s)|\le(1+a_j)^{2}\) and \(|q_j(s)-1|\le2a_j+a_j^{2}\); since \(\sum_j\gamma_j^{-2}=\frac{\pi^{2}}{6\lceil\sqrt N\rceil^{2}}<\infty\), the product converges absolutely and locally uniformly, so \(\xi^{**}\) is entire with zero multiset \(Z(\xi)\uplus\bigcup_j Q_j\) (Weierstrass, **Standard**). Order: for \(|s|=R\ge2\), \(\sum_j\log(1+a_j)\le\sum_{j\le\sqrt c}\log(1+c/j^{2})+\sum_{j>\sqrt c}c/j^{2}=O(\sqrt c\log c)=O(R\log R)\) with \(c=2R^{2}/\lceil\sqrt N\rceil^{2}\), so \(\log M_{\xi^{**}}(R)=\log M_{\xi}(R)+O(R\log R)\) and the order is 1. Symmetries: each \(q_j\) has them (Step 1). Li coefficients: \(\lambda_n(\xi^{**})=\lambda_n+\sum_j T_n^{(j)}\), absolutely convergent by (8) (valid since \(n\le N\le\gamma_1^{2}\le\gamma_j^{2}\)). One-sided bound (6) for each \(j\):
\[
\lambda_n(\xi^{**})\;\ge\;\lambda_n-2(\sqrt e-1)\,n\sum_{j\ge1}\frac{1}{\gamma_j^{2}}
\;\ge\;n\Bigl(0.0230-\frac{1.29745\,\pi^{2}}{6N}\Bigr)\;>\;0
\]
for \(N>1.29745\,\pi^{2}/(6\cdot0.0230)=92.8\). ∎

### Complement — the blindness window is genuinely finite (consistency with Li's criterion)

*For every quadruple \(Q\) as in the Theorem there are infinitely many \(n\) with*
\[
T_n\;\le\;6-e^{\kappa n},
\qquad
\kappa=0.49\,\frac{2\beta_0-1}{(1-\beta_0)^{2}+\gamma_0^{2}}\;>\;0 .
\]

**Proof.** For the left pair, \(x:=(2\beta_0-1)/((1-\beta_0)^{2}+\gamma_0^{2})\le\gamma_0^{-2}\le1/64\), so \(\log|w|=\tfrac12\log(1+x)\ge\tfrac x2(1-\tfrac x2)\ge0.49\,x=\kappa\), i.e. \(|w|^{n}\ge e^{\kappa n}\). Let \(\theta=\arg w\). If \(\theta/2\pi\) is rational with denominator \(q\), every \(n\in q\mathbb{Z}\) has \(\cos n\theta=1\); if irrational, by Weyl equidistribution a positive density of \(n\) has \(n\theta\bmod2\pi\in[-\pi/3,\pi/3]\), i.e. \(\cos n\theta\ge\tfrac12\). For such \(n\) the left pair contributes \(2-2|w|^{n}\cos n\theta\le2-e^{\kappa n}\); each right-pair term is \(1-\mathrm{Re}(w^{n})\le1+|w|^{n}\le2\) since \(|w|\le1\) there, so the right pair contributes at most \(4\). Hence \(T_n\le 6-e^{\kappa n}\to-\infty\). ∎

So \(\lambda_n(\xi^{*})\) does eventually go negative (as Li–Bombieri–Lagarias positivity theory demands for a multiset with \(\mathrm{Re}\,\rho\ne\tfrac12\)); the theorem quantifies exactly *how late* that detection can be forced to occur. Numerically, for \((\beta_0,\gamma_0)=(0.99,8)\) the guaranteed blind window is \(n\le64\) and the first actual negative value of \(\lambda_n+T_n\) occurs at \(n=955\) (value \(\approx-134.8\)); see `code/verify_run.log`.

### Computational input \((V)\) and its verification

`code/li_coefficients.py` computes \(\lambda_1,\dots,\lambda_{2000}\) from Li's generating function
\[
g(z)\;=\;\frac{d}{dz}\log\xi\Bigl(\frac{1}{1-z}\Bigr)\;=\;s^{2}\,\frac{\xi'}{\xi}(s)\Big|_{s=1/(1-z)},
\qquad
\frac{\xi'}{\xi}(s)=\frac1s+\frac1{s-1}-\frac{\log\pi}2+\frac12\psi\Bigl(\frac s2\Bigr)+\frac{\zeta'}{\zeta}(s),
\]
by trapezoidal (= discrete Fourier) coefficient extraction on the circle \(|z|=r\) with \(M=8192\) points, at working precision 40 digits. The method needs **no logarithm of \(\xi\)** (no branch tracking) and **no power-series division** (no catastrophic cancellation). Analyticity of \(g\) on \(|z|\le0.995\) needs only the classical fact (ii): a pole at \(z_\rho=1-1/\rho\) with \(|z_\rho|\le0.995\) would force \(|\rho|^{2}\le1/(1-0.995^{2})<100.3\), i.e. a zero of \(\zeta\) with \(|\mathrm{Im}\,\rho|\le11\), which does not exist; zeros *on* the line sit exactly on \(|z_\rho|=1\) by (1).

Verification performed (all in `code/full_run.log`):
- **closed-form anchor:** \(\lambda_1\) agrees with \(1+\tfrac\gamma2-\tfrac12\log4\pi\) to \(4.8\times10^{-32}\);
- **two independent radii** \(r=0.99\) and \(r=0.985\) agree on all 2000 coefficients to \(4.6\times10^{-27}\);
- **a-priori aliasing bound** (sup of \(|g|\) on \(|z|=0.995\), sampled, \(\approx7\times10^{4}\)): wrap-around error \(\le1.9\times10^{-9}\) at \(n=2000\);
- **known small values reproduced:** \(\lambda_2=0.09234573\ldots\), \(\lambda_3=0.20763892\ldots\), \(\lambda_4=0.36879047\ldots\);
- **result:** \(\min_{n\le2000}\lambda_n/n=\lambda_1=0.0230957\ldots\) at \(n=1\); hence \((V)\) holds with margin (all later \(\lambda_n/n\) are larger; e.g. \(\lambda_{2000}/2000=2.6758\ldots\)).

`code/verify_theorem.py` then re-checks every displayed inequality — (6), (7), (8), Step 5, the Corollary bound, and the Complement — against **exact** complex-arithmetic evaluation of \(T_n\) for the quadruples \((\beta_0,\gamma_0)=(0.75,45),(0.99,8),(0.51,45)\) and for the infinite family \(\gamma_j=45j\): all pass, with minimum slack \(1.6\times10^{-3}\) in (6) and minimum value \(0.024\) of \(\lambda_n+T_n\) (see `code/verify_run.log`). These margins exceed every numerical error bound above by \(>20\) orders of magnitude.

*(Not interval-certified: mpmath high-precision floating point, not ball/interval arithmetic. No new computational height for RH is claimed anywhere; the only zero-location fact imported is the 1903-era height 14.)*

---

## What is new vs REPORT.md

REPORT.md's Proposition B (§5) sketched the folklore first-order estimate \(|1-(1-1/\rho)^{n}|=O(n/|\rho|)\) and concluded, qualitatively, that Li positivity for \(n\le N\) is "compatible with a hypothetical off-line zero at height \(\gg N\)". This dossier goes beyond it in four checkable ways.

1. **A quadratic sharpening of the blindness height, with the mechanism identified.** The new observation (Step 3) is that the *downward* perturbation of \(\lambda_n\) by an off-line zero is governed by the modulus excess \(|1-1/\rho|-1=O(|\rho|^{-2})\) alone — the \(O(n/|\rho|)\) phase effect is blocked by the hard floor \(1-\mathrm{Re}(w^n)\ge1-|w|^n\). Hence blindness up to height \(\sim\sqrt N\), not \(\sim N\): a quadratic improvement over Proposition B, with the explicit constant \(2(\sqrt e-1)<1.29745\).
2. **A construction, not a tail estimate.** The "cannot exclude" slogan is upgraded to a formal no-go theorem: an explicit Pólya-class function \(\xi^{*}\) (and, in the Corollary, \(\xi^{**}\) with *infinitely many* off-line zeros) possessing every structural property of \(\xi\) used by Li's criterion, whose first \(N\) Li coefficients are strictly positive. This pins down exactly which ingredient any finite-Li-based zero-localization must use: the *arithmetic* of \(\zeta\) (Euler product / prime side of the explicit formula), not positivity plus functional-equation structure.
3. **Fully written constants everywhere** — (6), (7), (8), the threshold \(\gamma_0\ge8\) (any \(\gamma_0>7.6\) works), the corollary threshold \(N\ge93\) — each verified numerically against exact evaluation.
4. **Executed, reproducible numerics.** REPORT.md ran no computation. Here \(\lambda_1,\dots,\lambda_{2000}\) are computed by a branch-free FFT/Cauchy method with a closed-form anchor, two-radius cross-validation, and an a-priori aliasing bound; and the finite-window phenomenon is exhibited concretely (blind through \(n=64\), detection at \(n=955\), for a quadruple at height 8).

---

## What this does NOT prove (RH remains open)

- **Nothing about the actual zeros of \(\zeta\).** \(\xi^{*}\) and \(\xi^{**}\) are auxiliary functions; no statement is made that \(\zeta\) has, or has not, off-line zeros anywhere. RH is untouched.
- **Li's criterion is not weakened.** Positivity of **all** \(\lambda_n\) is still equivalent to RH; indeed the Complement proves \(T_n\to-\infty\) along a subsequence, so the constructed functions are eventually detected. The theorem only measures how *slowly* finite positivity acquires information.
- **The no-go binds a specific class of arguments** — those using only entirety, order 1, the functional equation, reality, zeros-in-strip, and \(\lambda_1,\dots,\lambda_N\ge0\). Arguments that use the Euler product, the arithmetic formula for \(\lambda_n\) via Stieltjes constants, or the prime side of the explicit formula are *not* covered (and, by this theorem, any successful finite-Li zero-localization must use them).
- **The computational input \((V)\) is floating-point** (40 digits, cross-validated, error bounds \(\le10^{-8}\) against verified margins \(\ge1.6\times10^{-3}\)), not interval-certified, and covers \(n\le2000\) only; the theorem's range is capped accordingly. No new RH verification height is claimed or used.
- **No new zero-free region, no new proportion of zeros on the line, no operator.** This is a method barrier (in the same taxonomic slot as REPORT.md §5), now with a construction and constants instead of a sketch.

---

## Honesty label: New (proved here) / Folklore formalized / Computational

- **Theorem, Corollary, Complement — New (proved here).** All proofs are complete and elementary (freshman complex analysis plus the standard structural facts about \(\xi\) cited as Known). The underlying *qualitative* phenomenon ("finite Li positivity sees only finite height") is folklore and was sketched as REPORT.md Proposition B; the quadratic \(\sqrt N\) sharpening via the hard-floor/modulus-excess argument, the explicit constants, and the \(\xi^{*}/\xi^{**}\) constructions are, to the best of this run's knowledge, new here — but this run performed **no literature search**, so a prior appearance of some version (e.g. in the Bombieri–Lagarias circle of ideas) cannot be excluded; if it exists, the correct label degrades to *Folklore formalized* with explicit constants.
- **Input \((V)\) and all numerical tables — Computational** (mpmath, 40-digit floating point, two-radius cross-validation, closed-form anchor; not interval arithmetic).
- **Imported facts** — labeled **Known** inline (structure of \(\xi\); Li's lemma; no zeros of \(\zeta\) with \(0<|\mathrm{Im}\,\rho|\le14\), used only in the numerics' error analysis).
- No proof of RH is claimed. No citations are invented. No computational heights are invented.
