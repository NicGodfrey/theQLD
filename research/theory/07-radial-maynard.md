# 07 — The radial Maynard functional is a drum: $M_2^{\mathrm{rad}} = 8/j_{0,1}^2$, exactly

**One new statement.** The Maynard variational functional for the twin configuration ($k=2$), restricted to *radial* cutoffs $F(t_1,t_2)=g(t_1+t_2)$, has exact value
$$M_2^{\mathrm{rad}} \;=\; \frac{8}{j_{0,1}^{2}} \;=\; 1.3833205522\ldots,$$
where $j_{0,1}=2.4048255576\ldots$ is the first positive zero of the Bessel function $J_0$. The supremum is attained, uniquely up to scalars, at $g^*(s) = \frac{j_{0,1}}{2\sqrt s}\,J_1\!\big(j_{0,1}\sqrt s\big)$, a strictly positive analytic profile. In particular $M_2^{\mathrm{rad}} < 2\log 2 < 2$: even the best radial Maynard weight falls short of detecting twin primes by the definite margin $2 - 8/j_{0,1}^2 = 0.6166\ldots$, at every level of distribution up to full Elliott–Halberstam.

**One-line honesty tag.** `[PROVED HERE]` — new exact evaluation of a *restricted* functional (Wave 2 had only the upper bound $M_2 \le 2\log 2$ for the unrestricted $M_2$, by a different argument not repeated here); the identification of the extremizer via Bessel's equation is classical Sturm–Liouville theory, claimed as applied, not invented.

---

## 1. Setup and statement

Notation follows the Wave-2 twin-prime dossier (`conjectures/07-twin-primes/BREAKTHROUGH.md`). Let
$$\mathcal R_2 = \{(t_1,t_2)\in[0,1]^2 : t_1,t_2\ge 0,\ t_1+t_2\le 1\},$$
and for measurable $F$ on $\mathcal R_2$ set
$$I(F)=\iint_{\mathcal R_2} F(t_1,t_2)^2\,dt_1\,dt_2,\qquad
J_1(F)=\int_0^1\!\Big(\int_0^{1-t_2}F(t_1,t_2)\,dt_1\Big)^{\!2}dt_2,$$
with $J_2(F)$ defined symmetrically (inner integration in $t_2$). Maynard's constant is $M_2=\sup\,(J_1+J_2)/I$ over $F\in L^2(\mathcal R_2)$ with $I(F)>0$.

**Definition (radial class).** $F$ is *radial* if $F(t_1,t_2)=g(t_1+t_2)$ for some $g\in L^2([0,1],\,s\,ds)$, $g \ne 0$. (Section 2 shows this weighted space is exactly the condition $F \in L^2(\mathcal R_2)$, $I(F)>0$.) Put
$$M_2^{\mathrm{rad}} \;=\; \sup\Big\{ \frac{J_1(F)+J_2(F)}{I(F)} \;:\; F(t_1,t_2)=g(t_1+t_2),\ g\in L^2([0,1],s\,ds),\ g\neq 0 \Big\}.$$
Radial cutoffs are the natural symmetric one-parameter reduction of the Maynard problem — they depend only on the "total budget" $t_1+t_2$ of the divisor supports, which is the quantity the simplex constraint actually restricts.

**Theorem 1.** With $j = j_{0,1}$ the first positive zero of $J_0$,
$$M_2^{\mathrm{rad}} \;=\; \frac{8}{j_{0,1}^{2}} \;=\; 1.3833205522451594\ldots\;,$$
and the supremum is attained precisely at the scalar multiples of $F^*(t_1,t_2)=g^*(t_1+t_2)$, where
$$g^*(s) \;=\; \frac{j}{2\sqrt s}\,J_1\!\big(j\sqrt s\big) \;=\; -\frac{d}{ds}\,J_0\!\big(j\sqrt s\big) \;=\; \sum_{m\ge 1} \frac{(-1)^{m+1}\,m}{(m!)^2}\Big(\frac{j^2}{4}\Big)^{\!m} s^{\,m-1},$$
an entire function of $s$ with $g^*(0)=j^2/4$ and $g^*>0$ on $[0,1]$.

**Corollary 1 (two-sided pinch on the full constant).** $\;\dfrac{8}{j_{0,1}^2} \le M_2 \le 2\log 2$, i.e. $1.38332\ldots \le M_2 \le 1.38629\ldots$ — a closed-form lower bound within $0.215\%$ of the Wave-2 ceiling.

**Corollary 2 (radial twin no-go).** $M_2^{\mathrm{rad}} < 2$. Since the Maynard–Tao criterion for two primes in $\{n,n+2\}$ at level of distribution $\theta$ requires $M_2 > 2/\theta \ge 2$ `[ESTABLISHED — Maynard, quoted as in the Wave-2 dossier]`, no radial cutoff detects twins, even under full Elliott–Halberstam; the shortfall is exactly $2 - 8/j_{0,1}^2 = 0.61667\ldots$.

The proof occupies Sections 2–6: (1) exact reduction of the three integrals to a one-dimensional weighted Rayleigh quotient; (2) the Euler–Lagrange equation with its two boundary conditions, both justified; (3) the transformation to Bessel's equation of order $0$; (4) the sharp inequality (first eigenvalue $= j_{0,1}^2/4$) proved by a Picone-type identity, with the equality case; (5) numerics with a self-contained certified enclosure of $j_{0,1}$, so every strict inequality above is proved inside this note.

---

## 2. Step 1 — Exact reduction to a one-dimensional Rayleigh quotient

**Lemma 1 (reduction).** Let $g\in L^2([0,1],s\,ds)$, $g \ne 0$, and $F(t_1,t_2)=g(t_1+t_2)$. Define
$$G(x) \;=\; \int_x^1 g(u)\,du \qquad (0<x\le 1).$$
Then $G$ is locally absolutely continuous on $(0,1]$ with $G(1)=0$ and $G'=-g$ a.e., and
$$I(F) \;=\; \int_0^1 s\,g(s)^2\,ds \;=\; \int_0^1 s\,G'(s)^2\,ds, \qquad
J_1(F)+J_2(F) \;=\; 2\int_0^1 G(s)^2\,ds .$$
Conversely, every $G$ in the class
$$\mathcal V \;=\; \Big\{ G:(0,1]\to\mathbb R \ \text{locally absolutely continuous},\ G(1)=0,\ 0<\int_0^1 s\,G'(s)^2\,ds<\infty \Big\}$$
arises this way from $g:=-G'$. Consequently
$$M_2^{\mathrm{rad}} \;=\; \sup_{G\in\mathcal V}\ \frac{2\int_0^1 G(s)^2\,ds}{\int_0^1 s\,G'(s)^2\,ds} \;=\; \frac{2}{\lambda_*}, \qquad
\lambda_* \;:=\; \inf_{G\in\mathcal V}\ Q(G),\quad Q(G):=\frac{\int_0^1 s\,(G')^2}{\int_0^1 G^2}. \tag{2.1}$$

*Proof.* **The integral $I$.** All integrands are nonnegative, so Tonelli applies throughout. Writing the simplex as $0\le t_2\le 1$, $0\le t_1\le 1-t_2$ and substituting $u=t_1+t_2$ in the inner integral,
$$I(F)=\int_0^1\!\!\int_0^{1-t_2} g(t_1+t_2)^2\,dt_1\,dt_2
=\int_0^1\!\!\int_{t_2}^{1} g(u)^2\,du\,dt_2
=\int_0^1 g(u)^2\Big(\int_0^{u} dt_2\Big) du
=\int_0^1 u\,g(u)^2\,du,$$
where the third equality swaps the order over $\{0\le t_2\le u\le 1\}$. The weight $s\,ds$ is thus forced: $F\in L^2(\mathcal R_2)$ **iff** $g\in L^2([0,1],s\,ds)$, and $I(F)>0$ iff $g\neq 0$ there.

**The integrals $J_1,J_2$.** First, $g$ is integrable away from $0$: for $x\in(0,1]$, by Cauchy–Schwarz with weight $u$,
$$\int_x^1 |g(u)|\,du \;=\; \int_x^1 |g(u)|\sqrt u\cdot\frac{du}{\sqrt u}
\;\le\; \Big(\int_x^1 u\,g^2\,du\Big)^{1/2}\Big(\log\tfrac1x\Big)^{1/2} \;<\;\infty. \tag{2.2}$$
So $G(x)=\int_x^1 g$ is well defined and locally absolutely continuous on $(0,1]$, $G(1)=0$, $G'=-g$ a.e. (Lebesgue differentiation). For $t_2\in(0,1]$, the same substitution gives the inner integral of $J_1$ exactly:
$$\int_0^{1-t_2} g(t_1+t_2)\,dt_1 \;=\; \int_{t_2}^{1} g(u)\,du \;=\; G(t_2),$$
absolutely convergent by (2.2). Hence $J_1(F)=\int_0^1 G(t_2)^2\,dt_2$ and, symmetrically, $J_2(F)=\int_0^1 G(t_1)^2\,dt_1$; the endpoint $t=0$ is a null set. Therefore $J_1+J_2=2\int_0^1 G^2$, finite by Lemma 2(b) below. Since $G'=-g$, also $I(F)=\int_0^1 s(G')^2\,ds$.

**Converse.** Given $G\in\mathcal V$, put $g:=-G'\in L^2(s\,ds)$, $g \ne 0$; then for $x\in(0,1]$, $\int_x^1 g = -\int_x^1 G' = G(x)-G(1)=G(x)$ by absolute continuity on $[x,1]$. So the map $g\mapsto G$ is a bijection onto $\mathcal V$, and (2.1) follows by taking suprema. $\blacksquare$

**Lemma 2 (a priori estimates; soft bound $M_2^{\mathrm{rad}}\le 2$).** Let $G\in\mathcal V$ and $D:=\int_0^1 s(G')^2\,ds$. Then:

**(a)** for every $s\in(0,1]$, $\;G(s)^2 \le \varepsilon(s)\,\log\tfrac1s\;$ where $\varepsilon(s):=\int_s^1 u\,G'(u)^2\,du \le D$;

**(b)** $\int_0^1 G^2\,ds \;\le\; D\int_0^1 \log\tfrac1s\,ds \;=\; D$, hence $Q(G)\ge 1$ and $M_2^{\mathrm{rad}}\le 2$.

*Proof.* (a) is (2.2) applied to $g=-G'$, squared. (b) integrates (a), using $\int_0^1\log\frac1s\,ds=1$; then $Q\ge1$, and $M_2^{\mathrm{rad}} = 2/\lambda_* \le 2$ by (2.1). $\blacksquare$

Lemma 2 already recovers, for the radial class, the qualitative Wave-2 conclusion $M_2^{\mathrm{rad}} \le 2$ in three lines. The rest of the note replaces the constant $1$ in $Q \ge 1$ by the sharp $j_{0,1}^2/4 = 1.4457\ldots$ and identifies the optimizer.

---

## 3. Step 2 — Euler–Lagrange equation and both boundary conditions

The quotient $Q$ in (2.1) is a Rayleigh quotient for a singular Sturm–Liouville problem on $(0,1)$ with weight $p(s)=s$ degenerating at the left endpoint. This section derives the equation and boundary conditions satisfied by any minimizer; Section 5 will prove a minimizer exists (by exhibiting it), making the analysis here unconditional.

**Proposition 3.** Suppose $G_*\in\mathcal V$ attains $\lambda_* = Q(G_*)$. Then $G_*\in C^\infty\big((0,1)\big)$ and
$$\big(s\,G_*'(s)\big)' + \lambda_*\,G_*(s) = 0 \quad\text{on } (0,1), \qquad
G_*(1)=0, \qquad \lim_{s\to 0^+} s\,G_*'(s) = 0. \tag{3.1}$$

*Proof.* **First variation.** Fix $\eta\in C_c^\infty\big((0,1)\big)$; then $G_*+t\eta\in\mathcal V$ for all small $t$. Both $N(t)=\int_0^1 s(G_*'+t\eta')^2$ and $D(t)=\int_0^1 (G_*+t\eta)^2$ are quadratic polynomials in $t$ with $D(0)>0$, so $t\mapsto N(t)/D(t)$ is differentiable near $0$ and minimized at $t=0$. Setting the derivative to zero and using $N(0)=\lambda_* D(0)$:
$$\int_0^1 s\,G_*'\,\eta'\,ds \;=\; \lambda_* \int_0^1 G_*\,\eta\,ds \qquad \text{for all } \eta\in C_c^\infty\big((0,1)\big). \tag{3.2}$$

**Regularity.** (3.2) says the locally integrable function $u(s):=s\,G_*'(s)$ has distributional derivative $-\lambda_* G_*$ on $(0,1)$; since $G_*$ is continuous, $u$ has an absolutely continuous representative with $u'=-\lambda_* G_*$ pointwise. Then $G_*'=u/s$ is continuous on $(0,1)$, so $G_*\in C^1(0,1)$; then $u\in C^1$ and $G_*''=(u'-G_*')/s=(-\lambda_* G_*-G_*')/s$ is continuous, so $G_*\in C^2(0,1)$; iterating, $G_*\in C^\infty(0,1)$ and the ODE in (3.1) holds classically.

**Boundary condition at $s=1$** is membership in $\mathcal V$: $G_*(1)=0$ (with $G_*$ continuous up to $1$).

**Natural boundary condition at $s=0$.** By Lemma 2(a), $|G_*(s)|\le\big(D\log\frac1s\big)^{1/2}$, so $G_*\in L^1(0,\tfrac12)$. Fix $s_0\in(0,1)$; integrating $u'=-\lambda_* G_*$,
$$u(s) \;=\; u(s_0) + \lambda_*\int_s^{s_0} G_*(v)\,dv \;\xrightarrow[s\to0^+]{}\; c \;:=\; u(s_0)+\lambda_*\int_0^{s_0}G_*(v)\,dv \in\mathbb R .$$
If $c\neq 0$, then $|G_*'(s)| = |u(s)|/s \ge |c|/(2s)$ for all small $s$, whence $\int_0 s\,(G_*')^2\,ds \ge \frac{c^2}{4}\int_0 \frac{ds}{s} = \infty$, contradicting $G_*\in\mathcal V$. Hence $c=0$: $\lim_{s\to0^+} sG_*'(s)=0$. $\blacksquare$

The condition at $s=0$ is *not imposed* on the class $\mathcal V$; it is *forced* by finiteness of the weighted Dirichlet energy — the variational ("natural") boundary condition of the degenerate weight $p(s)=s$. This is the mechanism that will kill the second Bessel solution $Y_0$ in the next step.

---

## 4. Step 3 — Transformation to Bessel's equation of order zero, and the spectrum

**Proposition 4.** Let $\lambda>0$. Under the substitution
$$x \;=\; 2\sqrt{\lambda s}, \qquad H(x) \;=\; G\big(x^2/(4\lambda)\big),$$
the equation $(sG')'+\lambda G=0$ on $(0,1)$ is equivalent to Bessel's equation of order $0$,
$$H''(x) + \frac1x H'(x) + H(x) = 0 \qquad \big(0<x<2\sqrt\lambda\,\big), \tag{4.1}$$
and moreover $\;s\,G'(s) = \tfrac{x}{2}\,H'(x)$. Consequently, the boundary-value problem (3.1) with parameter $\lambda>0$ has a nonzero solution in $\mathcal V$ **iff**
$$\lambda \;=\; \lambda_n \;:=\; \frac{j_{0,n}^{\,2}}{4}, \qquad n=1,2,\ldots,$$
where $0<j_{0,1}<j_{0,2}<\cdots$ are the positive zeros of $J_0$; the solution is then $G=A\,\varphi_n$, $\varphi_n(s):=J_0\big(j_{0,n}\sqrt s\big)$.

*Proof.* **The substitution.** From $x=2\sqrt{\lambda s}$: $\frac{dx}{ds}=\sqrt{\lambda/s}=2\lambda/x$ and $s=x^2/(4\lambda)$. Then
$$G'(s) = H'(x)\,\frac{2\lambda}{x}, \qquad
G''(s) = \frac{2\lambda}{x}\,\frac{d}{dx}\Big(H'(x)\frac{2\lambda}{x}\Big) = \frac{4\lambda^2}{x^2}H''(x) - \frac{4\lambda^2}{x^3}H'(x),$$
so
$$sG''+G'+\lambda G = \frac{x^2}{4\lambda}\Big(\frac{4\lambda^2}{x^2}H''-\frac{4\lambda^2}{x^3}H'\Big) + \frac{2\lambda}{x}H' + \lambda H
= \lambda\Big(H'' + \frac1x H' + H\Big),$$
which vanishes iff (4.1) holds. Also $sG'(s) = \frac{x^2}{4\lambda}\cdot H'(x)\frac{2\lambda}{x} = \frac{x}{2}H'(x)$, as claimed.

**Solving the BVP.** The solution space of (4.1) is two-dimensional, spanned by $J_0$ and $Y_0$ `[ESTABLISHED — classical; e.g. Watson, ch. III]`, so $G(s)=A\,J_0(x)+B\,Y_0(x)$ with $x=2\sqrt{\lambda s}$. Test the natural boundary condition through $sG'=\frac x2 H'$:
- $J_0$-part: $\frac x2 J_0'(x) = -\frac x2 J_1(x) \to 0$ as $x\to0^+$ (indeed $J_1(x)=\frac x2+O(x^3)$);
- $Y_0$-part: from the classical expansion $Y_0(x)=\frac2\pi\big(\log\frac x2+\gamma\big)J_0(x)+O(x^2)$ one has $Y_0'(x)=\frac{2}{\pi x}+O(x\log x)$, so $\frac x2 Y_0'(x)\to \frac1\pi \neq 0$.

Hence $\lim_{s\to0^+}sG'(s)=B/\pi$, and the condition $sG'\to0$ of (3.1) forces $B=0$. (Equivalently: for $B\ne0$, $G'(s)\sim B/(\pi s)$ and the energy $\int_0 s(G')^2\,ds$ diverges — the $Y_0$ branch is not even in $\mathcal V$.) Then $G=A\,J_0\big(2\sqrt{\lambda s}\big)$ with $A\neq0$, and the Dirichlet condition $G(1)=0$ reads $J_0\big(2\sqrt\lambda\big)=0$, i.e. $2\sqrt\lambda=j_{0,n}$ for some $n\ge1$. Conversely each $\varphi_n(s)=J_0(j_{0,n}\sqrt s)$ lies in $\mathcal V$: by the power series of $J_0$,
$$\varphi_n(s) \;=\; \sum_{m\ge0}\frac{(-1)^m}{(m!)^2}\Big(\frac{j_{0,n}^2}{4}\Big)^{\!m} s^m \tag{4.2}$$
is *entire in $s$* (the $\sqrt s$ disappears because $J_0$ is even), so $\varphi_n\in C^\infty[0,1]$, $\varphi_n(1)=J_0(j_{0,n})=0$, and the energy is finite. $\blacksquare$

The candidate minimizer is thus the ground state
$$\varphi(s) \;:=\; \varphi_1(s) \;=\; J_0\big(j\sqrt s\big), \qquad j:=j_{0,1},$$
with $\varphi(0)=1$, $\varphi(1)=0$, $\varphi'(0)=-j^2/4$, and — two facts used repeatedly below —
$$\varphi>0 \text{ on } [0,1), \qquad -\varphi'(s)=\frac{j}{2\sqrt s}J_1\big(j\sqrt s\big) = g^*(s) >0 \text{ on } (0,1]. \tag{4.3}$$
The first holds because $j\sqrt s<j$ and $j$ is the *first* zero of $J_0$ (with $J_0(0)=1$). The second reduces to $J_1>0$ on $(0,j\,]$, which is elementary from the alternating series of $J_1$: its terms $t_m=(x/2)^{2m+1}/\big(m!(m+1)!\big)$ satisfy $t_{m+1}/t_m=(x/2)^2/\big((m+1)(m+2)\big)<1$ for $x\le 2.8$, so
$$J_1(x) \;\ge\; t_0-t_1 \;=\; \frac x2\Big(1-\frac{x^2}{8}\Big) \;>\;0 \qquad (0<x\le 2.405), \tag{4.4}$$
and $j<2.405$ by Lemma 6 below. So the optimal radial profile $g^*=-\varphi'$ is a genuine (strictly positive) sieve cutoff.

Proposition 4 identifies the *only possible* minimizers; it does not by itself prove $\lambda_*=\lambda_1$, because the infimum in (2.1) could a priori fail to be attained. The next step closes this gap with a direct sharp inequality, valid for every $G\in\mathcal V$, whose equality case is exactly $G \in \mathbb{R}\varphi$.

---

## 5. Step 4 — The sharp inequality, by a Picone identity at the ground state

**Theorem 5 (sharp weighted Poincaré inequality on the triangle's radial slice).** For every $G\in\mathcal V$,
$$\int_0^1 s\,G'(s)^2\,ds \;\ge\; \frac{j_{0,1}^{\,2}}{4}\int_0^1 G(s)^2\,ds, \tag{5.1}$$
with equality **iff** $G=c\,\varphi$ for some $c\neq0$. Consequently $\lambda_*=\lambda_1=j_{0,1}^2/4$, the infimum in (2.1) is attained exactly on $\mathbb R^\times\varphi$, and
$$M_2^{\mathrm{rad}} \;=\; \frac{2}{\lambda_1} \;=\; \frac{8}{j_{0,1}^{\,2}} .$$

*Proof.* Write $\lambda_1=j^2/4$ and $\psi:=\varphi'/\varphi$ on $(0,1)$, which is well defined and smooth by (4.3). Fix $[a,b]\subset(0,1)$.

**The identity.** Pointwise on $(0,1)$, expanding the square,
$$s\,(G')^2 - s\,(G'-\psi G)^2 \;=\; 2s\,\psi\,G\,G' - s\,\psi^2G^2
\;=\; \frac{d}{ds}\big[\,s\,\psi\,G^2\,\big] - (s\psi)'\,G^2 - s\,\psi^2G^2 .$$
Since $\varphi$ solves $(s\varphi')'=-\lambda_1\varphi$,
$$(s\psi)' \;=\; \frac{(s\varphi')'}{\varphi} - s\,\frac{(\varphi')^2}{\varphi^2} \;=\; -\lambda_1 - s\,\psi^2,$$
so the last two terms combine to $+\lambda_1 G^2$. $G$ is locally absolutely continuous and $\psi\in C^\infty(0,1)$, so $s\psi G^2$ is absolutely continuous on $[a,b]$ and we may integrate:
$$\int_a^b s(G')^2\,ds \;-\; \lambda_1\int_a^b G^2\,ds
\;=\; \int_a^b s\,\big(G'-\psi G\big)^2\,ds \;+\; \Big[\, \frac{s\,\varphi'(s)}{\varphi(s)}\,G(s)^2 \,\Big]_{s=a}^{s=b}. \tag{5.2}$$

**Boundary term at $b\to1^-$.** Let $\varepsilon(s)=\int_s^1 u\,G'(u)^2du\to0$ as $s\to1^-$ (absolute continuity of the integral). By Lemma 2(a) and $\log\frac1b\le\frac{1-b}{b}\le 2(1-b)$ for $b\ge\frac12$,
$$G(b)^2 \;\le\; 2\,\varepsilon(b)\,(1-b).$$
By (4.3), $-\varphi'$ is continuous and strictly positive on $[\tfrac12,1]$; let $\kappa=\min_{[1/2,1]}(-\varphi')>0$ and $M=\max_{[1/2,1]}|\varphi'|$. Then $\varphi(b)=\int_b^1(-\varphi')\ge\kappa(1-b)$, so
$$\Big|\frac{b\,\varphi'(b)}{\varphi(b)}\,G(b)^2\Big| \;\le\; \frac{M\cdot 2\varepsilon(b)(1-b)}{\kappa\,(1-b)} \;=\; \frac{2M}{\kappa}\,\varepsilon(b) \;\xrightarrow[b\to1^-]{}\; 0 .$$

**Boundary term at $a\to0^+$.** Here $\varphi(a)\to\varphi(0)=1$ and $\varphi'$ is bounded near $0$ (it is continuous on $[0,1]$ by (4.2)), while $G(a)^2\le D\log\frac1a$ by Lemma 2(a). Hence
$$\Big|\frac{a\,\varphi'(a)}{\varphi(a)}\,G(a)^2\Big| \;\le\; C\,a\log\tfrac1a \;\xrightarrow[a\to0^+]{}\; 0 .$$

**Passing to the limit.** As $a\downarrow0$, $b\uparrow1$: the left side of (5.2) converges to $\int_0^1 s(G')^2 - \lambda_1\int_0^1G^2$ (monotone convergence; both integrals finite by Lemma 2(b)), the boundary terms vanish, and $\int_a^b s(G'-\psi G)^2$ increases to $\int_0^1 s(G'-\psi G)^2$ (monotone convergence), which is therefore finite and equals the left side:
$$\int_0^1 s(G')^2\,ds \;-\; \lambda_1\int_0^1 G^2\,ds \;=\; \int_0^1 s\,\big(G'-\psi G\big)^2\,ds \;\ge\; 0 .$$
This is (5.1).

**Equality case.** Equality forces $G'=\psi G$ a.e. on $(0,1)$. On any $[a,b]\subset(0,1)$ the function $G/\varphi$ is absolutely continuous (quotient of an AC function by a $C^1$ function bounded away from zero) with $(G/\varphi)'=(G'-\psi G)/\varphi=0$ a.e., hence $G=c\varphi$ on $(0,1)$, and on $(0,1]$ by continuity; $c\neq0$ since $G\ne0$ in $\mathcal V$.

**Attainment and the value.** $\varphi\in\mathcal V$ (Proposition 4), and integrating by parts on $[a,b]$ and letting $a\to0$, $b\to1$ — the boundary term $s\varphi'\varphi$ vanishes at both ends since $\varphi(1)=0$ with $\varphi'$ bounded, and $s\varphi'(s)\to0$ with $\varphi(0)=1$ —
$$\int_0^1 s(\varphi')^2\,ds \;=\; \big[\,s\varphi'\varphi\,\big]_0^1 - \int_0^1 (s\varphi')'\varphi\,ds \;=\; \lambda_1\int_0^1\varphi^2\,ds,$$
so $Q(\varphi)=\lambda_1$ and the infimum is attained. By (2.1), $M_2^{\mathrm{rad}}=2/\lambda_1=8/j^2$. $\blacksquare$

*Explicit check of the attained value* (Fourier–Bessel norms, classical `[ESTABLISHED]`, included as verification, not needed for the proof): with $u=\sqrt s$,
$$\int_0^1 \varphi^2\,ds = 2\int_0^1 J_0(ju)^2\,u\,du = J_1(j)^2 = 0.2695141239\ldots,\qquad
\int_0^1 s(\varphi')^2\,ds = \frac{j^2}{4}\,J_1(j)^2 = 0.3896625746\ldots,$$
(using $\int_0^1 J_0(ju)^2u\,du=\tfrac12 J_1(j)^2$ and $\int_0^1 J_1(ju)^2u\,du=\tfrac12 J_1(j)^2$ at $J_0(j)=0$), whose ratio is $4/j^2$ as required, and a direct two-dimensional numerical quadrature of $(J_1+J_2)/I$ on the simplex for $F^*=g^*(t_1+t_2)$ reproduces $8/j^2=1.38332055224515941\ldots$ to all computed digits.

This proves Theorem 1: the reduction (Lemma 1), the sharp inequality with its equality case (Theorem 5), and $g^*=-\varphi'$ with the series and positivity (4.2)–(4.4).

**Remark (why a drum).** The substitution $u=\sqrt s$, $H(u)=G(u^2)$ gives $\int_0^1 G^2\,ds=2\int_0^1H^2u\,du$ and $\int_0^1 s(G')^2ds=\frac12\int_0^1 (H')^2u\,du$, so $\lambda_*=\frac14\,\mu_1$ where $\mu_1=\inf \int_0^1 (H')^2u\,du/\int_0^1H^2u\,du$ over $H(1)=0$ — the *radial first Dirichlet eigenvalue of the unit disk*, $\mu_1=j_{0,1}^2$ `[ESTABLISHED — classical]`. The radial Maynard problem for the twin configuration is, up to this change of variables, the fundamental tone of a circular drum; the optimal sieve cutoff is the drum's ground-state mode read along the diagonal of the simplex. This equivalence is an independent confirmation of $\lambda_*=j^2/4$, but the proof above is self-contained and does not use it.

---

## 6. Step 5 — Certified numerics and the twin-prime conclusion

**Lemma 6 (self-contained enclosure of $j_{0,1}$).** $\;2.403 \;<\; j_{0,1} \;<\; 2.405$.

*Proof.* All series values below are partial sums of $J_0(x)=\sum_{m\ge0}(-1)^m t_m$, $t_m=(x^2/4)^m/(m!)^2$, computed in **exact rational arithmetic** at rational $x$ and rounded here to nine places; for $x\le 2.405$ the terms satisfy $t_{m+1}/t_m=(x^2/4)/(m+1)^2<1$ for $m\ge1$, so the alternating-series bound applies from $m=1$ on: the true value lies between consecutive partial sums.

At $x=2.403$ ($x^2/4 = 1.44360225$ exactly): the partial sums through $m=7$ and $m=8$ bracket the value,
$$0.0009480 \;<\; S_7 \;\le\; J_0(2.403) \;\le\; S_8 \;<\; 0.0009481,$$
so $J_0(2.403) > 9.4\times10^{-4} > 0$. At $x=2.405$ ($x^2/4=1.44600625$ exactly):
$$-0.0000906 \;<\; S_7 \;\le\; J_0(2.405) \;\le\; S_8 \;<\; -0.0000905,$$
so $J_0(2.405) < -9.0\times10^{-5} < 0$.

By (4.4), $J_1>0$ on $(0,2.405]$, hence $J_0'=-J_1<0$ there: $J_0$ is *strictly decreasing* on $[0,2.405]$. Since $J_0(0)=1>0$ and $J_0(2.403)>0$, monotonicity gives $J_0>0$ on all of $[0,2.403]$, so the first zero satisfies $j_{0,1}>2.403$. Since $J_0(2.405)<0$, the intermediate value theorem places a zero in $(2.403,2.405)$, so $j_{0,1}<2.405$. $\blacksquare$

**Corollary 6.1 (certified value and strict inequalities).**
$$1.3831198\ldots \;=\; \frac{8}{2.405^2} \;<\; M_2^{\mathrm{rad}} \;=\; \frac{8}{j_{0,1}^2} \;<\; \frac{8}{2.403^2} \;=\; 1.3854231\ldots \;<\; 2\log2 \;=\; 1.3862943\ldots \;<\; 2 .$$
Every inequality here is proved within this note: $2\log2<2$ is $\log2<1$, i.e. $2<e$; and $\frac{8}{2.403^2}<2\log2$ amounts to $2.403^2 > 4/\log 2$, which holds with room to spare from the all-positive series $\log 2=\sum_{k\ge1}\frac{1}{k\,2^k} > \sum_{k=1}^{10}\frac{1}{k\,2^k}=\frac{44711}{64512}=0.6930648\ldots$, giving $4/\log 2 < 4\cdot\frac{64512}{44711} = 5.7714656\ldots < 5.774409 = 2.403^2$. With the classical high-precision value $j_{0,1}=2.404825557695772768\ldots$ `[ESTABLISHED — Watson; standard tables]`,
$$M_2^{\mathrm{rad}} \;=\; \frac{8}{j_{0,1}^2} \;=\; \frac{8}{5.7831859629467845\ldots} \;=\; 1.3833205522451594\ldots,$$
which sits $0.0029738\ldots$ below the Wave-2 ceiling $2\log2$ — the radial class realizes $99.785\%$ of the ceiling but cannot cross it.

**Corollary 2, proof (radial twin no-go).** The Maynard–Tao criterion `[ESTABLISHED — quoted, exactly as in the Wave-2 dossier]` detects $m+1=2$ primes in the admissible pair $\{0,2\}$ only if $M_2 > 2/\theta$, where $\theta\le1$ is the level of distribution; thus at best (full Elliott–Halberstam, $\theta=1$) it needs $M_2>2$, and a radial cutoff can only contribute its own Rayleigh quotient, at most $M_2^{\mathrm{rad}}$. By Theorem 1 and Corollary 6.1, $M_2^{\mathrm{rad}}=8/j_{0,1}^2<1.3855<2$. So no radial Maynard weight — including the *optimal* one $F^*$, now known exactly — certifies twin primes, even under EH; the deficit is exactly $2-8/j_{0,1}^2=0.6166794\ldots$. $\blacksquare$

**Corollary 1, proof (pinch on $M_2$).** The radial class is a subclass of $L^2(\mathcal R_2)$ with $I>0$, so $M_2\ge M_2^{\mathrm{rad}}=8/j_{0,1}^2$; the upper bound $M_2\le 2\log2$ is Wave-2 Theorem A (quoted, not reproved). $\blacksquare$

**Remark (the optimizer of the full $M_2$ is not radial).** The Wave-2 dossier records the computational bound $M_2\ge1.385933$ (degree-$10$ polynomial subspace) `[COMPUTATIONAL — quoted]`. Since $1.385933>1.3854232>8/j_{0,1}^2$ by Corollary 6.1, *modulo that computation* the true extremizer of $M_2$ is strictly non-radial: dependence on $t_1-t_2$ genuinely helps, though by less than $0.003$. Unconditionally, this note proves only the lower bound of Corollary 1 — which is, however, exact and in closed form, versus a floating-point eigenvalue.

---

## 7. Honesty

- **Theorem 1 ($M_2^{\mathrm{rad}}=8/j_{0,1}^2$, with unique optimizer $g^*$)** `[PROVED HERE]` — the new statement of this note. Wave 2 proved only the *upper bound* $M_2\le\frac{k}{k-1}\log k$ for the unrestricted functional (Cauchy–Schwarz on fibers, not repeated or used anywhere above). An exact evaluation of any natural sub-supremum of $M_2$ appears in neither the dossier nor, to the author's knowledge, the standard sources (Maynard 2015; Polymath8b); it is the kind of statement an expert could produce as an exercise, and the tag should degrade to `[REDISCOVERED]` if a reference surfaces.
- **Method** — the reduction (Lemma 1), the a priori bound (Lemma 2), the natural-boundary-condition argument (Proposition 3), the Picone identity at the ground state (Theorem 5), and the certified enclosure (Lemma 6) are written out in full and are self-contained. The *ingredients* are classical: Sturm–Liouville/Rayleigh theory, Bessel's equation of order zero and the pair $(J_0,Y_0)$ with its $x\to0$ asymptotics `[ESTABLISHED — Watson]`, the Picone/ground-state-substitution trick, and Fourier–Bessel norm identities (used only in a verification remark). No novelty is claimed for any of these techniques.
- **Quoted inputs** — the Maynard–Tao detection criterion $M_2>2/\theta$ and Wave-2 Theorem A ($M_2\le2\log2$) are used only in the Corollaries, as black boxes, flagged at each use; the high-precision decimal of $j_{0,1}$ is quoted, but every *inequality* in the conclusions is covered by the self-contained enclosure of Lemma 6.
- **What this is not** — no claim about twin primes themselves is made. Theorem 1 is a sharpened impossibility statement *inside* the Maynard weight class: the most natural symmetric one-dimensional family of cutoffs has an exactly computable ceiling, $8/j_{0,1}^2\approx1.3833$, and that ceiling — the fundamental tone of a circular drum — lies below the detection threshold $2$ by a fixed margin. The conjecture remains open.
