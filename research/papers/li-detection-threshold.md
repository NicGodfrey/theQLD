# A two-sided \(T^2\log T\) law for the Li detection index of a single off-critical zero

*Status: original research paper, referee-style. Companion to the note `research/theory/01-li-detection.md` [N1], whose quadruplet analysis is re-proved here in the sharpened form needed (Section 4). All external inputs are cited published results; all constants are explicit and were machine-checked. No claim about the truth or falsity of the Riemann Hypothesis is made anywhere in this paper.*

---

## Abstract

Let \(\xi(s)=\tfrac12 s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s)\) and let \(\lambda_n\) be its Li coefficients, so that the Riemann Hypothesis (RH) is equivalent to \(\lambda_n\ge0\) for all \(n\ge1\) (Li [Li]; Keiper [Ke]; Bombieri–Lagarias [BL]). Suppose \(\xi\) has a zero \(\rho_0=\beta+i\gamma\) with \(\tfrac12<\beta<1\), \(\gamma\ge 10\), and set \(\delta:=2\beta-1\), \(\nu:=\gamma^2/\delta\), \(L:=\log\nu\). Assume **(H1)**: every zero of \(\xi\) outside the reflected quadruplet \(Q=\{\beta\pm i\gamma,\,1-\beta\pm i\gamma\}\) lies on the critical line. Using only two unconditional published inputs — Rosser's explicit form of the Riemann–von Mangoldt formula [Ro] and the Platt–Trudgian verification of RH up to height \(3\cdot10^{12}\) [PT] — we prove:

* **(i)** \(\lambda_n>0\) for every \(1\le n\le 1.99\,\nu L\) (in particular for all \(n\le 114\,\gamma^2/\delta\));
* **(ii)** \(\lambda_m<-\,m\log m\) for some integer \(m\in[2.4\,\nu L,\;2.41\,\nu L]\);
* **(iii)** hence \(n_1:=\min\{n\ge1:\lambda_n<0\}\) exists and \(1.99\,\nu L<n_1\le 2.41\,\nu L\), and asymptotically \(n_1=(2+O(L^{-1}\log L))\,\nu L\).

In the normalization of Brown [Br], the quadruplet lies on the boundary of his region \(D_r\) with \(T=(r^2-1)^{-1/2}\) and \(T^2=\nu\,(1+O(\gamma^{-2}))\). Brown proved that if **all** zeros of a \(\xi\)-type function lie in \(D_r\) then the Li positivity statements \(P_n\) hold for \(1\le n\le 2T^2\log T\) [Br, Theorem 2], that some \(P_m\) fails with \(m=O(T^3\log^2T)\) [Br, Theorem 3 and Remark 1], and he remarked that "it would be interesting to see if it is possible to narrow the gap between these two bounds". For the single-quadruplet configuration we close that gap to the constant factor \(2.41/1.99<1.22\): positivity holds up to \(\approx 3.98\,T^2\log T\) and fails by \(\approx 4.82\,T^2\log T\). A configuration version (Theorem 1) replaces (H1) by an explicit counting hypothesis and applies — if RH is true — to the genuine \(\xi\)-type functions \(\xi(s)\prod_{\rho\in Q}(1-s/\rho)\), so the two-sided law is attained by actual entire functions and is not a statement about the empty set. The contrapositive is an explicit detection threshold: verified Li positivity up to \(N\) excludes every (H1)-compatible off-line zero with \(\gamma^2/\delta\le N/(2.41\log N)\), an exponent-\(\tfrac12\) zero-free statement compared with the exponent-\(\tfrac13\) region in [Br, Theorem 3].

---

## 1. Introduction

### 1.1 Li's criterion and Brown's gap

For the completed zeta function \(\xi(s)=\tfrac12 s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s)\), Li [Li] introduced the coefficients
\[
\lambda_n=\frac{1}{(n-1)!}\,\frac{d^n}{ds^n}\Bigl[s^{n-1}\log\xi(s)\Bigr]_{s=1},
\qquad n\ge1,
\]
and proved that RH holds if and only if \(\lambda_n\ge0\) for all \(n\); the sequence had been studied numerically by Keiper [Ke]. Bombieri and Lagarias [BL] showed, unconditionally, that
\[
\lambda_n\;=\;\sum_{\rho}\Bigl(1-\Bigl(1-\frac1\rho\Bigr)^{\!n}\Bigr),
\tag{1.1}
\]
the sum running over the non-trivial zeros \(\rho\) of \(\zeta\) with multiplicity, in the symmetric order \(\lim_{T\to\infty}\sum_{|\operatorname{Im}\rho|\le T}\), and they placed the criterion in a general framework for multisets of zeros. Under RH the asymptotics \(\lambda_n=\tfrac n2\log n+C_1n+O(\sqrt n\log n)\) are known (Lagarias [La]; see also Coffey [Co] and Voros [V]).

Brown [Br] quantified the relation between *finite* Li positivity and zero-free regions. For \(r>1\) let \(D_r\) be the closed region
\[
D_r=\Bigl\{z\in\mathbb C:\ \Bigl|\tfrac{z}{z-1}\Bigr|\le r\ \text{and}\ \Bigl|\tfrac{z-1}{z}\Bigr|\le r\Bigr\},
\tag{1.2}
\]
a lens around the critical line whose intersection over all \(r>1\) is the critical line itself, and set \(T=(r^2-1)^{-1/2}\). For a general class of \(\xi\)-type functions (including completed Artin \(L\)-functions under Artin's conjecture) Brown proved: if all zeros lie in \(D_r\) then the positivity statements \(P_n\) hold for all \(1\le n\le 2T^2\log T\), provided \(T\ge T_0\) [Br, Theorem 2]; and conversely \(P_1,\dots,P_n\) force the zeros into \(D_r\) with \(T\asymp(n/\log^2n)^{1/3}\) [Br, Theorem 3] — equivalently, a zero on the boundary of \(D_r\) forces some \(P_m\) to fail with \(m=O(T^3\log^2T)\). Brown remarked [Br, Remark 1] that it would be interesting to narrow the gap between \(T^2\log T\) and \(T^3\log^2T\).

### 1.2 What this paper proves

We close Brown's gap **to a constant factor smaller than \(1.22\)** in the extremal single-violation scenario: one reflected quadruplet
\[
Q=\{\beta\pm i\gamma,\ (1-\beta)\pm i\gamma\},\qquad \tfrac12<\beta<1,\quad \delta:=2\beta-1,
\]
off the line, all other zeros on the line. The natural scale is
\[
\nu:=\frac{\gamma^2}{\delta},\qquad L:=\log\nu ,
\]
and \(\nu\) *is* Brown's \(T^2\) for this configuration: the quadruplet lies on \(\partial D_r\) with \(r=e^{\kappa}\), \(\kappa=\tfrac12\log\frac{\beta^2+\gamma^2}{(1-\beta)^2+\gamma^2}\), and \(T^2=(r^2-1)^{-1}=\nu(1+O(\gamma^{-2}))\) (Section 7.1). Our main results (Theorems 1 and 2, Section 3) give, for the full Li coefficients \(\lambda_n=\lambda_n^{\mathrm{rest}}+T_n\) (on-line background plus quadruplet increment):

* positivity of **every** \(\lambda_n\) up to \(1.99\,\nu L\);
* a violent sign failure \(\lambda_m<-m\log m\) at some explicit resonant index \(m\le 2.41\,\nu L\);
* hence the first sign change is pinned in the window \((1.99\,\nu L,\ 2.41\,\nu L]\), and equals \((2+O(L^{-1}\log L))\,\nu L\).

In Brown's normalization the window is \(\approx[3.98,\,4.82]\cdot T^2\log T\): the upper bound \(T^3\log^2T\) is replaced by a near-matching \(T^2\log T\), which is what the shape of his Theorem 2 predicts to be optimal. Everything is explicit; the only imported facts are Rosser's explicit zero-counting bound [Ro] and the Platt–Trudgian verification [PT], both unconditional. The exact increment formula \(T_n=4-4\cosh(n\kappa)\cos(n\theta)\) is proved in Section 4 (Lemma 4.1), following and sharpening the companion note [N1].

We emphasize the logical status honestly (Section 8): hypothesis (H1) of Theorem 2 is believed to be vacuous — RH asserts precisely that no such \(\rho_0\) exists — and nothing here is evidence for or against RH. The mathematical content is a *detection threshold*: exactly how many Li coefficients must be inspected before a given off-line zero is visible, with matching upper and lower bounds. The configuration form (Theorem 1) is non-vacuous: under RH it applies verbatim to the \(\xi\)-type functions \(\xi(s)\prod_{\rho\in Q}(1-s/\rho)\) for every admissible \((\beta,\gamma)\) (Section 7.4).

---

## 2. Definitions and imported results

### 2.1 Li coefficients of a configuration

Throughout, \(\tfrac12<\beta<1\), \(\delta=2\beta-1\in(0,1)\), \(\gamma>0\), and
\[
Q=\{\beta+i\gamma,\ \beta-i\gamma,\ 1-\beta+i\gamma,\ 1-\beta-i\gamma\}
\]
(four distinct points since \(\beta\neq\tfrac12\), \(\gamma\neq0\)). Its **Li increment** is the finite sum
\[
T_n:=\sum_{\rho\in Q}\Bigl(1-\Bigl(1-\frac1\rho\Bigr)^{\!n}\Bigr),\qquad n\ge1 .
\tag{2.1}
\]

A **critical-line multiset** is a multiset \(Z'=\biguplus_{j\ge1}\{\tfrac12+it_j,\ \tfrac12-it_j\}\) with ordinates \(0<t_1\le t_2\le\cdots\to\infty\), with counting function \(N'(T):=\#\{j:t_j\le T\}\). For \(\rho=\tfrac12+it\) one has \(|1-1/\rho|=|\rho-1|/|\rho|=1\), so \(1-1/\rho=e^{i\varphi_t}\) for a unique \(\varphi_t\in(0,\pi)\) when \(t>0\) (computed in Lemma 4.2), and the conjugate pair contributes
\[
p_t(n):=\Bigl(1-e^{in\varphi_t}\Bigr)+\Bigl(1-e^{-in\varphi_t}\Bigr)=2\bigl(1-\cos(n\varphi_t)\bigr)\in[0,4].
\tag{2.2}
\]
We define the **background** and the **Li coefficients of the configuration** \(\mathcal C=(\beta,\gamma;Z')\) by
\[
\lambda_n^{\mathrm{rest}}:=\sum_{j\ge1}p_{t_j}(n),
\qquad
\lambda_n(\mathcal C):=T_n+\lambda_n^{\mathrm{rest}} .
\tag{2.3}
\]
Since \(p_t(n)\le\min(4,(n\varphi_t)^2)\) and \(\varphi_t\le 2/t\) for \(t\ge10\) (Lemma 4.2), the series (2.3) converges absolutely whenever \(N'(T)=O(T\log T)\), which our hypothesis (H2) below guarantees; in particular no summation-order subtleties arise.

**Hypothesis (H2) (explicit counting of the background).** With
\[
F(T):=\frac{T}{2\pi}\log\frac{T}{2\pi e}+\frac78,
\qquad
\widetilde Q(T):=0.137\log T+0.443\log\log T+3.6,
\]
the multiset \(Z'\) satisfies \(\;\bigl|N'(T)-F(T)\bigr|\le \widetilde Q(T)\) for all \(T\ge 10^6\).

### 2.2 Imported results (all unconditional, all published)

**(K1) (Rosser [Ro, Theorem 19]).** Let \(N(T)\) denote the number of zeros \(\rho\) of \(\zeta\) with \(0<\operatorname{Im}\rho\le T\), counted with multiplicity (all zeros in the strip, on or off the critical line). Then
\[
\bigl|N(T)-F(T)\bigr|\;\le\;R(T):=0.137\log T+0.443\log\log T+1.588
\qquad(T\ge 1467).
\]
(We apply this only for \(T\ge10^6\). Trudgian's improvement [Tr] would sharpen our constants marginally; we do not use it.)

**(K2) (Platt–Trudgian [PT, Theorem 1]).** Every zero \(\rho=\beta+i\gamma\) of \(\zeta\) with \(0<\gamma\le 3\cdot10^{12}\) has \(\beta=\tfrac12\).

**(K3) (classical).** \(\zeta(\sigma)\neq0\) for \(0<\sigma<1\): indeed \((1-2^{1-\sigma})\zeta(\sigma)=\sum_{k\ge1}(-1)^{k-1}k^{-\sigma}>0\) (alternating series with decreasing terms) while \(1-2^{1-\sigma}<0\), so \(\zeta(\sigma)<0\). Together with \(\xi(0)=\xi(1)=\tfrac12\neq0\) [Ti, Ch. II], the non-trivial zeros of \(\zeta\) have non-zero imaginary part and come in conjugate pairs. Consequently, if all zeros of \(\xi\) outside \(Q\) lie on the critical line, those zeros form a critical-line multiset \(Z'\) in the sense of Section 2.1, and by (1.1) — regrouping the absolutely convergent tail by conjugate pairs, which the symmetric order permits —
\[
\lambda_n(\xi)\;=\;T_n+\lambda_n^{\mathrm{rest}}\;=\;\lambda_n(\mathcal C),
\qquad
N'(T)=N(T)-2\cdot\mathbf 1_{\{T\ge\gamma\}} .
\tag{2.4}
\]
(The quadruplet contributes the two zeros \(\beta+i\gamma\), \(1-\beta+i\gamma\) to \(N(T)\).)

---

## 3. Statements

**Theorem 1 (configuration version).**
Let \(\tfrac12<\beta<1\), \(\delta=2\beta-1\), \(\gamma\ge 10^6\), and let \(Z'\) be a critical-line multiset satisfying (H2). Put \(\nu=\gamma^2/\delta\) and \(L=\log\nu\) (so \(\nu>10^{12}\), \(L>27.63\)). Then the Li coefficients \(\lambda_n=\lambda_n(\mathcal C)\) of (2.3) satisfy:

1. \(\lambda_n>0\) for every integer \(1\le n\le 1.9\,\nu L\);
2. there is an integer \(m\in[\,2.6\,\nu L,\ 2.61\,\nu L\,]\) with \(\lambda_m<-\,m\log m\);
3. hence \(n_1:=\min\{n\ge1:\lambda_n<0\}\) exists and \(1.9\,\nu L<n_1\le 2.61\,\nu L\).

**Theorem 2 (the Riemann \(\xi\)-function).**
Suppose \(\xi\) has a zero \(\rho_0=\beta+i\gamma\) with \(\tfrac12<\beta<1\) and \(\gamma\ge10\), and assume

* **(H1)** the zero multiset of \(\xi\) is \(Q\uplus Z'\) with \(Z'\subset\{\operatorname{Re}s=\tfrac12\}\).

Then automatically \(\gamma>3\cdot10^{12}\) (by (K2)), \(Z'\) satisfies (H2) (by (K1)), \(L>57.45\), and the Li coefficients \(\lambda_n=\lambda_n(\xi)\) satisfy:

1. \(\lambda_n>0\) for every integer \(1\le n\le 1.99\,\nu L\); in particular for all \(n\le 114\,\gamma^2/\delta\);
2. \(\lambda_m<-\,m\log m\) for some integer \(m\in[\,2.4\,\nu L,\ 2.41\,\nu L\,]\); in particular \(\lambda_m<0\) for some
\[
m\;\le\;2.41\,\frac{\gamma^2}{\delta}\,\log\frac{\gamma^2}{\delta}\;\le\;4.82\,\frac{\gamma^2}{\delta}\,\log\frac{\gamma}{\delta};
\]
3. \(n_1=\min\{n\ge1:\lambda_n<0\}\) satisfies \(1.99\,\nu L<n_1\le 2.41\,\nu L\).

**Corollary 3 (detection threshold).**
Let \(N\ge3\) and suppose \(\lambda_n(\xi)\ge0\) for all \(n\le N\). Then \(\xi\) has no zero \(\beta+i\gamma\) \((\beta>\tfrac12,\ \gamma>0)\) satisfying (H1) with
\[
\frac{\gamma^2}{2\beta-1}\;\le\;\frac{N}{2.41\,\log N}.
\]

**Remark 3.1 (asymptotically sharp constant \(2\)).** For every \(\varepsilon\in(0,\tfrac12)\) there is an explicit \(L_0(\varepsilon)=O(\varepsilon^{-1}\log\varepsilon^{-1})\) such that for \(L\ge L_0(\varepsilon)\) the proof below gives \(\lambda_n>0\) for all \(n\le(2-\varepsilon)\nu L\) and \(\lambda_m<0\) for some \(m\le(2+\varepsilon)\nu L\): part 1 needs only \(2e^{-\varepsilon L/2}\le 0.032\,L\), and part 2 only \(\tfrac\varepsilon2 L\ge\log\bigl((2+\varepsilon)L\bigr)+\log\bigl(L+\log((2+\varepsilon)L)\bigr)\), up to the same \(1\%\) slack for the resonance shift \(6.29\gamma\) that the proofs already carry. Hence
\[
n_1=\bigl(2+O(L^{-1}\log L)\bigr)\,\nu L
\qquad(\gamma\to\infty,\ \text{uniformly in }\beta).
\]
The limiting constant \(2\) is *insensitive* to the constants \(0.032\) and \(0.98\) in Proposition 5.1: they enter only through additive \(O(1)\) terms inside a logarithm that is compared with \(L\). It is the exact reciprocal of the envelope rate \(\kappa\nu\to\tfrac12\) (Lemma 4.2).

**Remark 3.2 (higher multiplicity).** Theorem 2's hypothesis (H1) forces the four zeros of \(Q\) to be simple. If instead \(Z(\xi)=kQ\uplus Z'\) with \(k\ge2\), part 2 holds verbatim (at the chosen \(m\) the increment \(T_m\) is negative, and \(kT_m\le T_m\)); part 1 would need its endpoint reduced by \(O(\nu\log k)\), which we do not carry out.

---

## 4. The quadruplet increment \(T_n\)

Write \(\rho=\beta+i\gamma\) and \(w:=1-1/\rho\).

**Lemma 4.1 (exact closed form).** Let \(w=e^{-\kappa}e^{i\theta}\) with \(\kappa>0\), \(\theta\in(0,\pi/2)\). Then the multiset \(\{1-1/\rho':\rho'\in Q\}\) equals \(\{w,\bar w,w^{-1},\bar w^{-1}\}\) and, for every \(n\ge1\),
\[
\boxed{\;T_n\;=\;4-4\cosh(n\kappa)\cos(n\theta)\;}
\qquad
\kappa=\tfrac12\log\frac{\beta^2+\gamma^2}{(1-\beta)^2+\gamma^2},
\qquad
\tan\theta=\frac{\gamma}{\beta^2+\gamma^2-\beta}.
\]

*Proof.* The reflection \(\rho\mapsto1-\rho\) inverts \(w\):
\[
1-\frac1{1-\rho}=\frac{-\rho}{1-\rho}=\Bigl(\frac{\rho-1}{\rho}\Bigr)^{-1}=w^{-1},
\]
and conjugation of \(\rho\) conjugates \(w\); so the four values are \(w,\bar w,w^{-1},\bar w^{-1}\). Since
\[
|w|^2=\frac{(1-\beta)^2+\gamma^2}{\beta^2+\gamma^2}<1
\iff\beta>\tfrac12,
\]
we may write \(|w|=e^{-\kappa}\), \(\kappa>0\) as displayed. Moreover \(w=1-\frac{\beta-i\gamma}{\beta^2+\gamma^2}\) has \(\operatorname{Re}w=\frac{\beta^2+\gamma^2-\beta}{\beta^2+\gamma^2}>0\) (as \(\gamma^2>\beta\)) and \(\operatorname{Im}w=\frac{\gamma}{\beta^2+\gamma^2}>0\), so \(\theta\in(0,\pi/2)\) with the stated tangent. Finally
\[
\sum_{\rho'\in Q}\bigl(1-1/\rho'\bigr)^n
=w^n+\bar w^n+w^{-n}+\bar w^{-n}
=2e^{-n\kappa}\cos n\theta+2e^{n\kappa}\cos n\theta
=4\cosh(n\kappa)\cos(n\theta),
\]
and \(T_n=4-\sum_{\rho'}(1-1/\rho')^n\). In particular \(T_n\in\mathbb R\). \(\square\)

**Lemma 4.2 (angles and rate).** For \(\sigma\in[0,1]\) and \(t\ge10\), the angle \(\psi=\arg\bigl(1-\frac1{\sigma+it}\bigr)\in(0,\pi/2)\) satisfies
\[
\bigl|\,t\psi-1\,\bigr|\;\le\;\frac1{t^{2}} .
\tag{4.1}
\]
In particular the background angles obey \(|\,t\varphi_t-1\,|\le t^{-2}\) (case \(\sigma=\tfrac12\)) and the quadruplet angle obeys \(|\,\gamma\theta-1\,|\le\gamma^{-2}\) (case \(\sigma=\beta\)). Moreover, for \(\gamma\ge10\),
\[
\frac{\delta}{2\gamma^2}\Bigl(1-\frac1{\gamma^2}\Bigr)\;\le\;\kappa\;\le\;\frac{\delta}{2\gamma^2},
\qquad\text{i.e.}\qquad
\frac{1}{2\nu}\Bigl(1-\frac1{\gamma^2}\Bigr)\le\kappa\le\frac1{2\nu}.
\tag{4.2}
\]

*Proof.* As in Lemma 4.1, \(1-\frac1{\sigma+it}=\frac{t^2+\sigma^2-\sigma+it}{\sigma^2+t^2}\) with \(\sigma^2-\sigma\in[-\tfrac14,0]\), so
\[
\tan\psi=\frac{t}{t^2+\sigma^2-\sigma}\in\Bigl[\frac1t,\ \frac{t}{t^2-\tfrac14}\Bigr].
\]
Upper bound: \(\psi\le\tan\psi\le\frac1t\bigl(1-\tfrac1{4t^2}\bigr)^{-1}=\frac1t\bigl(1+\tfrac{1}{4t^2-1}\bigr)\le\frac1t(1+t^{-2})\) for \(t\ge10\). Lower bound: \(\psi\ge\arctan\frac1t\ge\frac1t-\frac1{3t^3}\ge\frac1t(1-t^{-2})\). This is (4.1).

For (4.2): \(\dfrac{\beta^2+\gamma^2}{(1-\beta)^2+\gamma^2}=1+x\) with \(x=\dfrac{\beta^2-(1-\beta)^2}{(1-\beta)^2+\gamma^2}=\dfrac{\delta}{(1-\beta)^2+\gamma^2}\in\Bigl[\dfrac{\delta}{\gamma^2+\tfrac14},\ \dfrac{\delta}{\gamma^2}\Bigr]\). Then \(\kappa=\tfrac12\log(1+x)\le\tfrac x2\le\frac{\delta}{2\gamma^2}\), while \(\log(1+x)\ge x-\tfrac{x^2}2\) gives
\[
\kappa\ \ge\ \frac{x}{2}\Bigl(1-\frac x2\Bigr)\ \ge\ \frac{\delta}{2\gamma^2}\Bigl(1+\frac1{4\gamma^2}\Bigr)^{-1}\Bigl(1-\frac{\delta}{2\gamma^2}\Bigr)
\ \ge\ \frac{\delta}{2\gamma^2}\Bigl(1-\frac1{4\gamma^2}-\frac1{2\gamma^2}\Bigr)
\ \ge\ \frac{\delta}{2\gamma^2}\Bigl(1-\frac1{\gamma^2}\Bigr). \qquad\square
\]

**Lemma 4.3 (envelope, impersonation, resonance).** Let \(\gamma\ge10^6\). Then:

**(a)** For every \(n\ge1\):\(\quad T_n\ \ge\ 4-4\cosh(n\kappa)\ \ge\ 2-2e^{n\kappa}\), i.e. \(-T_n\le 2e^{n\kappa}-2\).

**(b)** For every \(1\le n\le\gamma\):\(\quad T_n\ \ge\ 1.8\,\dfrac{n^2}{\gamma^2}\ >\ 0\)  (the quadruplet *impersonates* two on-line pairs).

**(c)** For every real \(X\ge 6.29\,\gamma\) there is an integer \(m\in[X,\ X+6.29\,\gamma]\) with \(\cos(m\theta)\ge1-10^{-12}\); for that \(m\),
\[
T_m\ \le\ 4-1.999\,e^{m\kappa}.
\]

*Proof.* **(a)** \(\cos\le1\) gives the first bound; \(4\cosh x-4=2e^{x}+2e^{-x}-4\le 2e^{x}-2\) since \(e^{-x}\le1\).

**(b)** Put \(v:=n\theta\) and \(u:=n\kappa\). By (4.1)–(4.2) with \(n\le\gamma\): \(v\le\gamma\theta\le1+\gamma^{-2}\le1.001\), and
\[
\frac uv=\frac\kappa\theta\le\frac{\delta/(2\gamma^2)}{(1-\gamma^{-2})/\gamma}\le\frac{1}{2\gamma}\bigl(1+2\gamma^{-2}\bigr)\le\frac{0.51}{\gamma},
\qquad\text{so } u\le\frac{0.51}{\gamma}\,v\le10^{-6}v .
\]
For all real \(v\), \(\cos v\le1-\tfrac{v^2}2+\tfrac{v^4}{24}\le1-v^2\bigl(\tfrac12-\tfrac{(1.001)^2}{24}\bigr)\le1-0.458\,v^2\) on \(v\le1.001\); and \(\cosh u\le1+u^2\) for \(u\le1\) (since \(\sum_{k\ge1}u^{2k}/(2k)!\le u^2(e-2)\le u^2\)). Hence
\[
\cosh u\,\cos v\le(1+u^2)(1-0.458v^2)\le1-0.458v^2+u^2\le1-0.457\,v^2,
\]
so \(T_n=4(1-\cosh u\cos v)\ge1.828\,v^2\ge1.828\,(1-\gamma^{-2})^2\,\dfrac{n^2}{\gamma^2}\ge1.8\,\dfrac{n^2}{\gamma^2}\).

**(c)** Let \(P:=2\pi/\theta\); by (4.1), \(6\gamma\le P\le 2\pi\gamma(1+2\gamma^{-2})\le6.284\gamma\). For \(k\ge1\) let \(m_k\) be the nearest integer to \(kP\), so \(|m_k\theta-2\pi k|\le\theta/2\) and
\[
\cos(m_k\theta)\ \ge\ \cos(\theta/2)\ \ge\ 1-\frac{\theta^2}{8}\ \ge\ 1-\frac{(1+\gamma^{-2})^2}{8\gamma^2}\ \ge\ 1-10^{-12}
\qquad(\gamma\ge10^6).
\]
Consecutive \(m_k\) differ by at most \(P+1\le6.29\gamma\), and \(m_1\le P+\tfrac12\le6.29\gamma\le X\). Hence \(k^*=\max\{k:m_k<X\}\) exists and \(m:=m_{k^*+1}\in[X,\,X+6.29\gamma]\). Finally
\[
T_m=4-4\cosh(m\kappa)\cos(m\theta)\le4-4\cosh(m\kappa)\,(1-10^{-12})\le4-2e^{m\kappa}(1-10^{-12})\le4-1.999\,e^{m\kappa}. \qquad\square
\]

---

## 5. The on-line background

**Proposition 5.1 (two-sided bracket for \(\lambda_n^{\mathrm{rest}}\)).** Let \(Z'\) satisfy (H2). Then \(\lambda_n^{\mathrm{rest}}\ge0\) for all \(n\ge1\), and for every \(n\ge10^6\):
\[
0.032\; n\log n\;\le\;\lambda_n^{\mathrm{rest}}\;\le\;0.98\; n\log n .
\]

*Proof.* Non-negativity is clear from (2.2). Fix \(n\ge10^6\).

**Lower bound.** Keep only ordinates \(t_j\in(n,2n]\). For such \(t\), by (4.1), \(v:=n\varphi_t\) satisfies
\[
v\le\frac nt(1+t^{-2})\le1+10^{-12}\le1.001,
\qquad
v\ge\frac nt(1-t^{-2})\ge0.999\,\frac nt\ \ (\ge0.499).
\]
Since \(1-\cos v\ge\frac{v^2}2-\frac{v^4}{24}=\frac{v^2}2\bigl(1-\frac{v^2}{12}\bigr)\ge\frac{v^2}2\bigl(1-\frac{(1.001)^2}{12}\bigr)\ge0.458\,v^2\),
\[
p_t(n)=2(1-\cos v)\ \ge\ 0.916\,(0.999)^2\Bigl(\frac nt\Bigr)^2\ \ge\ 0.914\,\Bigl(\frac nt\Bigr)^2\ \ge\ 0.2285
\qquad(t\le2n).
\tag{5.1}
\]
Count the ordinates using (H2) twice: since \(F(2n)-F(n)=\frac n{2\pi}\log\frac{2n}{\pi e}\) and \(\log\frac{2n}{\pi e}=\log n-1.4516\ge0.8949\log n\) for \(\log n\ge13.815\),
\[
N'(2n)-N'(n)\ \ge\ \frac n{2\pi}\log\frac{2n}{\pi e}-\widetilde Q(2n)-\widetilde Q(n)
\ \ge\ \bigl(0.8949-0.0001\bigr)\frac{n}{2\pi}\log n
\ =\ 0.8948\,\frac{n}{2\pi}\log n ,
\tag{5.2}
\]
where we used \(\widetilde Q(2n)+\widetilde Q(n)\le2\widetilde Q(2n)\le0.0001\cdot\frac n{2\pi}\log n\) for all \(n\ge10^6\): at \(n=10^6\) the two sides are \(13.55\) and \(219.9\), and the left side grows logarithmically while the right side grows superlinearly. Combining (5.1)–(5.2):
\[
\lambda_n^{\mathrm{rest}}\ \ge\ 0.2285\cdot0.8948\cdot\frac{n\log n}{2\pi}\ \ge\ 0.032\,n\log n .
\]

**Upper bound.** Use \(p_t(n)\le\min\bigl(4,(n\varphi_t)^2\bigr)\) (from \(1-\cos v\le\min(2,v^2/2)\)) and split at \(t=n\).

*Head.* By (H2), \(N'(n)\le F(n)+\widetilde Q(n)\le\frac n{2\pi}\log n-\frac{2.8379\,n}{2\pi}+\tfrac78+\widetilde Q(n)\le\frac n{2\pi}\log n\) for \(n\ge10^6\) (indeed \(\frac{2.8379\,n}{2\pi}\ge4.5\cdot10^5\ge\tfrac78+\widetilde Q(n)\)); the same argument gives \(N'(t)\le\frac t{2\pi}\log t\) for every \(t\ge n\). Hence \(\sum_{t_j\le n}p_{t_j}(n)\le4N'(n)\le\frac2\pi\,n\log n\).

*Tail.* By partial summation, for \(T>n\),
\[
\sum_{n<t_j\le T}t_j^{-2}
=\frac{N'(T)}{T^2}-\frac{N'(n)}{n^2}+2\int_n^{T}\frac{N'(t)}{t^3}\,dt ,
\]
and \(N'(T)/T^2\le\frac{\log T}{2\pi T}\to0\), so
\[
\sum_{t_j>n}t_j^{-2}\ \le\ 2\int_n^{\infty}\frac{t\log t}{2\pi}\,\frac{dt}{t^3}\ =\ \frac1\pi\,\frac{\log n+1}{n} .
\]
With \(\varphi_t\le\frac1t(1+t^{-2})\) for \(t>n\),
\[
\sum_{t_j>n}(n\varphi_{t_j})^2\ \le\ (1+10^{-12})^2\,n^2\sum_{t_j>n}t_j^{-2}\ \le\ \frac{1.001}{\pi}\,n\,(\log n+1).
\]
Adding head and tail, for \(n\ge10^6\) (so \(\log n\ge13.815\)):
\[
\lambda_n^{\mathrm{rest}}\ \le\ n\log n\Bigl[\frac2\pi+\frac{1.001}{\pi}\Bigl(1+\frac1{13.815}\Bigr)\Bigr]
\ \le\ n\log n\,\bigl[0.6367+0.3417\bigr]\ \le\ 0.98\,n\log n. \qquad\square
\]

*Remark.* For comparison: for the zeros of \(\zeta\) under RH one has \(\lambda_n=\tfrac12 n\log n+C_1n+O(\sqrt n\log n)\) [La], so a background of Riemann–von Mangoldt density truly grows like \(\tfrac12\,n\log n\). The bracket \([0.032,\,0.98]\) straddles \(\tfrac12\), and by Remark 3.1 its width affects the final answer only at relative order \(1/L\).

---

## 6. Proofs of the theorems

### 6.1 Proof of Theorem 1

Recall \(\kappa\le\frac1{2\nu}\) and \(\kappa\ge\frac{1-\gamma^{-2}}{2\nu}\) from (4.2), and \(\lambda_n=T_n+\lambda_n^{\mathrm{rest}}\).

**Part 1 (positivity for \(n\le1.9\,\nu L\)).** Split into three ranges; note \(\gamma<\gamma^2\le\nu<1.9\,\nu L\).

*Range 1: \(1\le n\le\gamma\).* By Lemma 4.3(b), \(T_n\ge1.8\,n^2/\gamma^2>0\), and \(\lambda_n^{\mathrm{rest}}\ge0\); so \(\lambda_n>0\).

*Range 2: \(\gamma<n\le\nu\).* Here \(n>\gamma\ge10^6\), so Proposition 5.1 applies; and \(n\kappa\le\nu\cdot\frac1{2\nu}=\frac12\), so by Lemma 4.3(a),
\[
-T_n\ \le\ 4\cosh\tfrac12-4\ <\ 0.511\ <\ 0.032\cdot10^6\cdot13.8\ \le\ 0.032\,n\log n\ \le\ \lambda_n^{\mathrm{rest}} .
\]

*Range 3: \(\nu<n\le1.9\,\nu L\).* Here \(n\kappa\le1.9\,\nu L\cdot\frac{1}{2\nu}=0.95\,L\) and \(\log n>\log\nu=L\), so by Lemma 4.3(a) and Proposition 5.1,
\[
-T_n\ \le\ 2e^{0.95L}-2,
\qquad
\lambda_n^{\mathrm{rest}}\ \ge\ 0.032\,n\log n\ \ge\ 0.032\,\nu L\ =\ 0.032\,L\,e^{L}.
\]
It therefore suffices that \(2e^{0.95L}\le0.032\,L\,e^{L}\), i.e. \(2\le0.032\,L\,e^{0.05L}\). At \(L=27.63\) the right side is \(0.032\cdot27.63\cdot e^{1.3815}=3.52>2\), and it is increasing in \(L\). Hence \(\lambda_n\ge0.032\,Le^{L}-2e^{0.95L}+2>0\).

**Part 2 (violent negativity at a resonant \(m\le2.61\,\nu L\)).** Apply Lemma 4.3(c) with \(X=2.6\,\nu L\) (note \(X\ge6.29\gamma\) since \(\nu L/\gamma=\gamma L/\delta\ge10^6\cdot27\)): there is an integer
\[
m\in[\,2.6\,\nu L,\ 2.6\,\nu L+6.29\gamma\,]\subseteq[\,2.6\,\nu L,\ 2.61\,\nu L\,]
\]
(using \(6.29\gamma\le0.01\,\nu L\), i.e. \(629\le\gamma L/\delta\)) with \(T_m\le4-1.999\,e^{m\kappa}\). By (4.2),
\[
m\kappa\ \ge\ 2.6\,\nu L\cdot\frac{1-\gamma^{-2}}{2\nu}\ \ge\ 1.2999\,L .
\]
We claim \(m\kappa\ge\log m+\log\log m\), i.e. \(e^{m\kappa}\ge m\log m\). Since \(m\le2.61\,\nu L\),
\[
\log m\le L+\log(2.61L),
\qquad
\log\log m\le\log\bigl(L+\log(2.61L)\bigr),
\]
so it suffices that \(g(L):=0.2999\,L-\log(2.61L)-\log\bigl(L+\log(2.61L)\bigr)\ge0\) for \(L\ge27.63\). Numerically \(g(27.63)=8.286-4.278-3.463=0.545>0\), and
\[
g'(L)=0.2999-\frac1L-\frac{1+1/L}{L+\log(2.61L)}\ \ge\ 0.2999-0.0362-0.0325\ >\ 0
\qquad(L\ge27.63),
\]
so \(g>0\) throughout. Hence \(e^{m\kappa}\ge m\log m\) and, with Proposition 5.1 (applicable since \(m\ge2.6\,\nu L\ge10^6\)),
\[
\lambda_m\ \le\ \bigl(4-1.999\,e^{m\kappa}\bigr)+0.98\,m\log m
\ \le\ 4-1.999\,m\log m+0.98\,m\log m
\ =\ 4-1.019\,m\log m\ <\ -\,m\log m,
\]
the last step because \(0.019\,m\log m\ge0.019\cdot(2.6\cdot10^{12}\cdot27.6)\cdot\log(10^6)\gg4\).

**Part 3.** Immediate from Parts 1 and 2. \(\blacksquare\)

### 6.2 Proof of Theorem 2

*Step 1 (the quadruplet sits inside \(Z(\xi)\)).* We may take \(\gamma>0\) (conjugating \(\rho_0\) if necessary). \(\xi\) is real on \(\mathbb R\), so its zero multiset is closed under conjugation; \(\xi(s)=\xi(1-s)\), so it is closed under \(s\mapsto1-s\) [Ti, Ch. II]. Hence \(Q\subseteq Z(\xi)\), and \(Q\) consists of four distinct points.

*Step 2 (height).* By (K2), every zero with \(0<\operatorname{Im}\rho\le3\cdot10^{12}\) has real part \(\tfrac12\); since \(\beta\ne\tfrac12\), necessarily \(\gamma>3\cdot10^{12}\). Thus \(\nu\ge\gamma^2>9\cdot10^{24}\) and \(L>57.45\); in particular \(\gamma\ge10^6\).

*Step 3 ((H2) holds for \(Z'\)).* By (K3), \(Z'\) is a critical-line multiset and \(N'(T)=N(T)-2\cdot\mathbf 1_{\{T\ge\gamma\}}\). By (K1), for \(T\ge10^6\ (\ge1467)\),
\[
\bigl|N'(T)-F(T)\bigr|\ \le\ R(T)+2\ =\ 0.137\log T+0.443\log\log T+3.588\ \le\ \widetilde Q(T).
\]
Moreover \(\lambda_n(\xi)=\lambda_n(\mathcal C)\) by (2.4).

*Step 4 (run the proof of Theorem 1 with \(L>57.45\)).* Theorem 1 already gives the conclusions with \((1.9,\ 2.61)\). The two numerical checks improve as follows.

*Part 1 with endpoint \(1.99\,\nu L\):* in Range 3 now \(n\kappa\le0.995\,L\), and the required inequality \(2\le0.032\,L\,e^{0.005L}\) holds at \(L=57.45\) (right side \(=0.032\cdot57.45\cdot e^{0.2873}=2.45\)) and is increasing in \(L\). Ranges 1–2 are unchanged.

*Part 2 with window \([2.4\,\nu L,\ 2.41\,\nu L]\):* take \(X=2.4\,\nu L\); then \(m\le2.4\,\nu L+6.29\gamma\le2.41\,\nu L\), and \(m\kappa\ge1.2\,L(1-\gamma^{-2})\ge1.1999\,L\), so it suffices that
\[
g_2(L):=0.1999\,L-\log(2.41L)-\log\bigl(L+\log(2.41L)\bigr)\ \ge\ 0
\qquad(L\ge57.45).
\]
Numerically \(g_2(57.45)=11.484-4.931-4.134=2.42>0\) and \(g_2'(L)\ge0.1999-\frac1{57.45}-\frac{1.02}{62.4}>0\). The rest of Part 2 is verbatim.

*Step 5 (the "in particular" statements).* \(1.99\,L>1.99\cdot57.45>114\), giving the range \(n\le114\,\gamma^2/\delta\) in part 1. For part 2, \(\log\frac{\gamma^2}{\delta}=2\log\gamma+\log\frac1\delta\le2\bigl(\log\gamma+\log\frac1\delta\bigr)=2\log\frac\gamma\delta\) since \(\log\frac1\delta\ge0\). \(\blacksquare\)

### 6.3 Proof of Corollary 3

Suppose, for contradiction, that \(\xi\) has a zero \(\beta+i\gamma\) with \(\beta>\tfrac12\), satisfying (H1), and with \(\nu=\gamma^2/(2\beta-1)\le N/(2.41\log N)\). Theorem 2 applies (its hypothesis \(\gamma\ge10\) holds by (K2), as any off-line zero has \(\gamma>3\cdot10^{12}\)). Since \(\nu\le N\), we get \(L=\log\nu\le\log N\), so Theorem 2, part 2, produces an \(m\le2.41\,\nu L\le2.41\cdot\frac{N}{2.41\log N}\cdot\log N=N\) with \(\lambda_m<0\) — contradicting \(\lambda_n\ge0\) for all \(n\le N\). \(\blacksquare\)

---

## 7. Discussion

### 7.1 Dictionary with Brown's normalization

For our configuration, \(\max_{\rho'\in Q}\bigl|\rho'/(\rho'-1)\bigr|=e^{\kappa}\), so the quadruplet lies on the boundary of Brown's region \(D_r\) (see (1.2)) with \(r=e^{\kappa}\) and inside no smaller \(D_{r'}\). With \(T=(r^2-1)^{-1/2}\),
\[
T^2=\frac1{e^{2\kappa}-1},
\qquad
2\kappa\in\Bigl[\frac{1-\gamma^{-2}}{\nu},\ \frac1\nu\Bigr]
\ \Longrightarrow\
\Bigl|\frac{T^2}{\nu}-1\Bigr|\le\frac2{\gamma^2},
\]
so \(\nu\) is Brown's \(T^2\) up to relative error \(2\gamma^{-2}\le10^{-12}\), and \(L=\log\nu=2\log T+O(\gamma^{-2})\). In this normalization Theorem 2 reads: Li positivity holds through \(\approx3.98\,T^2\log T\) and fails by \(\approx4.82\,T^2\log T\). Brown's Theorem 2 (positivity for \(n\le2T^2\log T\) when *all* zeros are in \(D_r\)) thus has the optimal shape: for the boundary configuration studied here the true detection index is \(\Theta(T^2\log T)\), with matching constants \(3.98\) and \(4.82\) (both \(\to4\) as \(T\to\infty\) by Remark 3.1). This answers the question of [Br, Remark 1] within the single-quadruplet class: the gap \(T^2\log T\) versus \(T^3\log^2T\) closes to a factor \(<1.22\). We emphasize that we do **not** improve Brown's \(O(T^3\log^2T)\) bound in his full generality (arbitrarily many zeros in \(D_r\)); see Section 8.

Corollary 3, read as a zero-free region, gives: verified positivity \(P_1,\dots,P_N\) excludes (H1)-compatible quadruplets with \(T^2\lesssim N/(2.41\log N)\), i.e. a region of Brown \(D_r\)-type with \(T\asymp(N/\log N)^{1/2}\), against \(T\asymp(N/\log^2N)^{1/3}\) from [Br, Theorem 3] — again, on the narrower configuration class.

### 7.2 Why the \(\log\) factor appears

The companion note [N1] analyses the increment \(T_n\) alone and finds that its first crossing of a *fixed* threshold (\(T_n\le-1\)) occurs at \((2\log2+O(\gamma^{-1}))\,\nu\), with no logarithm. For the full \(\lambda_n\), the quadruplet must overtake the growing background \(\lambda_n^{\mathrm{rest}}\asymp n\log n\) (Proposition 5.1) rather than a constant: the envelope \(2e^{n\kappa}\) exceeds \(n\log n\) precisely when \(n\kappa\gtrsim\log n\), i.e. \(n\gtrsim2\nu L\). The threshold \(-1\) of [N1] is thus replaced by the moving target \(-\Theta(n\log n)\), which converts the scale \(\nu\) into \(\nu\log\nu\) and the constant \(2\log2\) into \(2\). Both constants are sharp for their respective questions.

### 7.3 Numerical illustration (not used in any proof)

For synthetic configurations whose background ordinates are defined by \(F(t_j)=j\) (so that (H2) holds by construction, apart from heights far below the theorem's range), a direct computation of \(\lambda_n=T_n+\sum_j p_{t_j}(n)\) over resonant indices locates the first negative Li coefficient at
\[
(\beta,\gamma)=(0.75,30):\ n_1/(\nu L)=3.03;\quad
(0.6,50):\ 2.91;\quad
(0.9,60):\ 2.97;\quad
(0.8,100):\ 2.89,
\]
with \(L\in[7.5,\,9.7]\). The ratios exceed \(2\) by \(\approx2\log(cL)/L\), exactly the finite-\(L\) correction predicted by Remark 3.1 (e.g. at \((0.75,30)\): predicted crossover \(2\nu(\log m+\log\log m-\log4)\approx41{,}700\) versus observed \(40{,}910\)). This is an illustration of the mechanism at small heights, outside the range \(\gamma\ge10^6\) of the theorems, and is used nowhere in the proofs.

### 7.4 Non-vacuity: genuine \(\xi\)-type functions attaining the law

For any admissible \((\beta,\gamma)\) let \(q(s)=\prod_{\rho'\in Q}(1-s/\rho')\) and \(\xi^*:=\xi\,q\). Then \(q\) has real coefficients and satisfies \(q(1-s)=q(s)\) (pair each root with its reflection: \((1-\frac{1-s}{\rho'})(1-\frac{1-s}{1-\rho'})=(1-\frac s{\rho'})(1-\frac s{1-\rho'})\)), so \(\xi^*\) is entire of order \(1\), real on \(\mathbb R\), satisfies \(\xi^*(s)=\xi^*(1-s)\), and has zero multiset \(Z(\xi)\uplus Q\). If RH is true, then for every \(\tfrac12<\beta<1\) and \(\gamma\ge10^6\) the function \(\xi^*\) satisfies the hypotheses of Theorem 1 with \(Z'=Z(\xi)\) (its counting function is \(N\) itself, and (K1) gives (H2) with room to spare). Theorem 1 then pins the first Li sign change of \(\xi^*\) inside \((1.9\,\nu L,\ 2.61\,\nu L]\). Thus the two-sided law of this paper is realized by concrete entire functions of \(\xi\)-type — conditionally on RH for the background, unconditionally as a statement about configurations.

---

## 8. What is new, and honesty

**Proved here.** Theorems 1 and 2, Corollary 3, Remarks 3.1–3.2, Proposition 5.1 and Lemmas 4.1–4.3, with all constants explicit and machine-verified. The only external inputs are [Ro, Theorem 19], [PT, Theorem 1], the zero-sum representation (1.1) from [BL] (with [Li]), and classical structural facts about \(\xi\) [Ti]. Nothing conditional on RH is used in Theorems 1–2; hypothesis (H1) (resp. (H2)) is stated in the theorems themselves.

**New versus Brown [Br].** (a) The negativity bound at scale \(T^2\log T\) with explicit constant (\(2.41\,\nu L\approx4.82\,T^2\log T\)), against his \(O(T^3\log^2T)\), and the resulting two-sided pinning of the detection index within a factor \(1.22\) (asymptotically \(1\)) — but **only** for the single-quadruplet-plus-line configuration, a much narrower class than Brown's (his bounds must cover arbitrarily many zeros crowding \(\partial D_r\), where the background can conspire; we prove nothing about that general case, and Brown's \(T^3\log^2T\) record there stands). (b) The identification of the sharp asymptotic constant: \(n_1\sim2\,\nu\log\nu=4\,T^2\log T\). (c) An exponent-\(\tfrac12\) contrapositive (Corollary 3) versus the exponent-\(\tfrac13\) of [Br, Theorem 3], again on the narrower class. Within its class, our positivity part 1 is of the same \(T^2\log T\) shape as [Br, Theorem 2] (constant \(\approx3.98\) versus his \(2\), on our special configuration), so the genuinely new content is the matching upper bound and the two-sided law.

**New versus the companion note [N1].** [N1] concerns the four-term increment \(T_n\) only: its exact form, the blind window, and the first crossing of fixed thresholds at scale \((2\log2)\nu\). Here the actual Li coefficients \(\lambda_n=T_n+\lambda_n^{\mathrm{rest}}\) are treated: the unconditional-counting bracket for \(\lambda_n^{\mathrm{rest}}\) (Proposition 5.1), the passage from the \(\nu\)-scale to the \(\nu\log\nu\)-scale, the two-sided law with constants \((1.99,2.41)\), the limiting constant \(2\), and the detection-threshold corollary are all new. Lemma 4.1 restates [N1, Lemma 1]; Lemma 4.2 sharpens [N1, Lemma 2] (exact \(\kappa\le\delta/2\gamma^2\), unified angle bound (4.1)).

**Hypotheses, honestly.** (H1) is expected to be vacuous: RH predicts no \(\rho_0\) exists, and Theorem 2 asserts nothing about whether it does. We do not prove RH, do not disprove it, and do not claim evidence either way; the theorems calibrate the Li criterion as a detector. Without (H1), one would need a pointwise-in-\(n\) upper bound on the contribution of *other* hypothetical off-line zeros; classical zero-density estimates control their number but not, without further work, the exponentially growing terms \(|1-1/\rho|^{-n}\) they contribute, and we leave an unconditional version (e.g. "at most one quadruplet below height \(H\)" replaced by a density hypothesis) as an open problem. (H2) is unconditional for \(\xi\) via [Ro] because the Riemann–von Mangoldt count is insensitive to whether zeros are on or off the line. The hypothesis \(\gamma\ge10\) in Theorem 2 is stated for form's sake; (K2) upgrades it to \(\gamma>3\cdot10^{12}\), and this upgrade (not any numerics of ours) is what makes the small-\(n\) ranges clean. Corollary 3 has content beyond (K2) only when \(N/(2.41\log N)>9\cdot10^{24}\), i.e. \(N\gtrsim1.4\cdot10^{27}\) — far beyond present verifications of Li positivity; it quantifies what future verifications would buy.

**Constants.** None of \(1.9,\ 1.99,\ 2.4,\ 2.41,\ 2.6,\ 2.61,\ 0.032,\ 0.98\) is optimal; the proof was tuned for checkability, not extremal constants. The bracket ratio \(2.41/1.99\) (for \(\xi\)) tends to \(1\) as \(\gamma\to\infty\) (Remark 3.1). Using [Tr] in place of [Ro] would improve only lower-order terms.

---

## References

* **[BL]** E. Bombieri and J. C. Lagarias, *Complements to Li's criterion for the Riemann hypothesis*, J. Number Theory **77** (1999), no. 2, 274–287.
* **[Br]** F. C. S. Brown, *Li's criterion and zero-free regions of \(L\)-functions*, J. Number Theory **111** (2005), no. 1, 1–32.
* **[Co]** M. W. Coffey, *Toward verification of the Riemann hypothesis: application of the Li criterion*, Math. Phys. Anal. Geom. **8** (2005), no. 3, 211–255.
* **[Ke]** J. B. Keiper, *Power series expansions of Riemann's \(\xi\) function*, Math. Comp. **58** (1992), 765–773.
* **[La]** J. C. Lagarias, *Li coefficients for automorphic \(L\)-functions*, Ann. Inst. Fourier (Grenoble) **57** (2007), no. 5, 1689–1740.
* **[Li]** X.-J. Li, *The positivity of a sequence of numbers and the Riemann hypothesis*, J. Number Theory **65** (1997), no. 2, 325–333.
* **[N1]** *A sharp two-sided detection law for an off-critical zero quadruplet in Li increments*, companion note, `research/theory/01-li-detection.md` (this repository).
* **[PT]** D. J. Platt and T. S. Trudgian, *The Riemann hypothesis is true up to \(3\cdot10^{12}\)*, Bull. Lond. Math. Soc. **53** (2021), no. 3, 792–797.
* **[Ro]** J. B. Rosser, *Explicit bounds for some functions of prime numbers*, Amer. J. Math. **63** (1941), 211–232.
* **[Ti]** E. C. Titchmarsh, *The Theory of the Riemann Zeta-Function*, 2nd ed., revised by D. R. Heath-Brown, Oxford Univ. Press, 1986.
* **[Tr]** T. S. Trudgian, *An improved upper bound for the argument of the Riemann zeta-function on the critical line II*, J. Number Theory **134** (2014), 280–292.
* **[V]** A. Voros, *Sharpenings of Li's criterion for the Riemann hypothesis*, Math. Phys. Anal. Geom. **9** (2006), no. 1, 53–63.
