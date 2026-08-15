# Navier–Stokes — Wave-2 Breakthrough

**Legion 05, Wave 2.** Deliverable: one fully proved analytic lemma not already proved in `REPORT.md`. Per the wave-2 menu, we take the first target: a **self-contained proof of the Beale–Kato–Majda (BKM) continuation criterion for 3D Navier–Stokes**, at the enstrophy level, with every inequality written and every constant explicit. Two constant-explicit corollaries follow by combining the new Grönwall estimate with the Leray rate already proved in `REPORT.md` §5.2. **No claim of progress on the Millennium problem is made** (see the last two sections).

Notation matches `REPORT.md`: $\nu>0$, $\mathbb{P}$ the Leray projector, $\omega=\nabla\times u$, and Plancherel normalized so that $\|f\|_{L^2}=\|\hat f\|_{L^2}$. "Strong solution on $[0,T_*)$ with $u^0\in H^1$" means $u\in C([0,T_*);H^1)\cap L^2_{loc}([0,T_*);H^2)$, divergence-free, solving NS (zero force) with $u(0)=u^0$; by the standard local theory such $u$ is smooth on $\mathbb{R}^3\times(0,T_*)$ with $u\in C((0,T_*);H^k)$ for every $k$.

**Cited ingredients (the only external inputs; same citation standard as `REPORT.md` §5).**

- **(I1)** = `REPORT.md` Lemma 5.2.1: for divergence-free $u^0\in H^1(\mathbb{R}^3)$ there is a unique strong solution on a maximal interval $[0,T_{\max})$; it is smooth for $t>0$ with $u\in C((0,T_{\max});H^k)$ for all $k$; and if $T_{\max}<\infty$ then $\|\nabla u(t)\|_{L^2}\to\infty$ as $t\uparrow T_{\max}$. `[KNOWN — FK64, RRS16 Ch. 6–9, LR16]`
- **(I2)** = `REPORT.md` Theorem 5.2 (fully proved there): if $T_{\max}<\infty$ then $\|\nabla u(t)\|_{L^2}\ge c\,\nu^{3/4}(T_{\max}-t)^{-1/4}$ for all $t\in[0,T_{\max})$, with $c=(2K_0)^{-1/4}$ absolute. *(Used only for the corollaries, not for the theorem.)*

Everything else below is proved from scratch.

---

## Theorem

**Theorem W2 (BKM criterion for 3D Navier–Stokes, with explicit Grönwall constant).**
Let $u^0\in H^1(\mathbb{R}^3)$ be divergence-free and let $u$ be the unique strong solution on its maximal interval $[0,T_*)$. Then:

**(a) Quantitative vorticity Grönwall estimate.** For all $0<s\le t<T_*$,
$$
\|\omega(t)\|_{L^2}^2\ \le\ \|\omega(s)\|_{L^2}^2\,
\exp\!\Big(2\int_s^t\|\omega(\sigma)\|_{L^\infty}\,d\sigma\Big),
\tag{$\star$}
$$
with the **absolute constant $2$** in the exponent — no Sobolev or interpolation constants enter. Moreover the same computation yields, with the dissipation retained, for $0<s\le t<T_*$:
$$
\|\omega(t)\|_{L^2}^2+2\nu\int_s^t\|\nabla\omega(\sigma)\|_{L^2}^2\,d\sigma
\ \le\ \|\omega(s)\|_{L^2}^2\,\exp\!\Big(2\int_s^t\|\omega(\sigma)\|_{L^\infty}\,d\sigma\Big).
\tag{$\star\star$}
$$

**(b) Continuation criterion.** If $T_*<\infty$, then
$$
\int_{t_0}^{T_*}\|\omega(t)\|_{L^\infty}\,dt\ =\ \infty
\qquad\text{for every } t_0\in(0,T_*).
$$
Equivalently: if for some $T<\infty$ and some $t_0\in(0,T)$ one has $\int_{t_0}^{T}\|\omega(t)\|_{L^\infty}\,dt<\infty$, then $T_*>T$, i.e. **the smooth solution extends past $T$**. In particular the classical BKM hypothesis $\int_0^T\|\omega\|_{L^\infty}\,dt<\infty$ suffices.

**Corollary W2.1 (explicit logarithmic divergence rate).** If $T_*<\infty$, then for all $0<s\le t<T_*$,
$$
\int_s^t\|\omega(\sigma)\|_{L^\infty}\,d\sigma\ \ge\
\frac14\,\log\frac{1}{T_*-t}\ +\ \log\frac{c\,\nu^{3/4}}{\|\nabla u(s)\|_{L^2}},
$$
with $c$ the absolute constant of (I2). So the BKM integral diverges at least logarithmically, with the explicit leading coefficient $\tfrac14$.

**Corollary W2.2 (vorticity blow-up rate with explicit constant).** If $T_*<\infty$, then
$$
\limsup_{t\uparrow T_*}\;(T_*-t)\,\|\omega(t)\|_{L^\infty}\ \ge\ \frac14 .
$$
The constant $\tfrac14$ is absolute — independent of $\nu$, of the datum, and of all constants in the local theory.

*Remark (torus).* All three statements hold verbatim on $\mathbb{T}^3$ for mean-zero data, with Fourier series replacing the Fourier transform in Lemma A below and no cutoff needed in Step 3.

---

## Proof (complete, with inequalities)

### Step 0: two elementary lemmas, proved from scratch

**Lemma A (curl–gradient Plancherel identity).** For every divergence-free $v\in H^1(\mathbb{R}^3;\mathbb{R}^3)$,
$$
\|\nabla v\|_{L^2}\ =\ \|\nabla\times v\|_{L^2}.
$$

*Proof.* By Plancherel, $\|\nabla v\|_{L^2}^2=\sum_{i,j}\|\partial_j v_i\|_{L^2}^2=\int_{\mathbb{R}^3}|\xi|^2|\hat v(\xi)|^2\,d\xi$ and $\|\nabla\times v\|_{L^2}^2=\int|\xi\times\hat v(\xi)|^2\,d\xi$ (here $\widehat{\nabla\times v}=i\,\xi\times\hat v$). For a real vector $a\in\mathbb{R}^3$ and a complex vector $b=p+iq\in\mathbb{C}^3$ ($p,q$ real), bilinearity gives $a\times b=a\times p+i\,a\times q$, hence by the real Lagrange identity $|a\times p|^2=|a|^2|p|^2-(a\cdot p)^2$ (and likewise for $q$):
$$
|a\times b|^2=|a\times p|^2+|a\times q|^2
=|a|^2(|p|^2+|q|^2)-\big((a\cdot p)^2+(a\cdot q)^2\big)
=|a|^2|b|^2-|a\cdot b|^2 .
$$
Divergence-freeness means $\xi\cdot\hat v(\xi)=0$ for a.e. $\xi$, so $|\xi\times\hat v|^2=|\xi|^2|\hat v|^2$ pointwise a.e. Integrate. $\square$

**Lemma B (pointwise stretching bound).** For vectors $\omega\in\mathbb{R}^3$ and matrices $\nabla u\in\mathbb{R}^{3\times3}$ (Frobenius norm $|\nabla u|$),
$$
\big|\big((\omega\cdot\nabla)u\big)\cdot\omega\big|\ \le\ |\omega|^2\,|\nabla u| .
$$

*Proof.* For each fixed $i$, Cauchy–Schwarz in $j$ gives $|(\omega\cdot\nabla)u_i|=|\sum_j\omega_j\partial_ju_i|\le|\omega|\,\big(\sum_j|\partial_ju_i|^2\big)^{1/2}$. Squaring and summing over $i$: $|(\omega\cdot\nabla)u|^2\le|\omega|^2\sum_{i,j}|\partial_ju_i|^2=|\omega|^2|\nabla u|^2$. Then Cauchy–Schwarz in $i$ once more: $|((\omega\cdot\nabla)u)\cdot\omega|\le|(\omega\cdot\nabla)u|\,|\omega|\le|\omega|^2|\nabla u|$. $\square$

### Step 1: the vorticity equation

On $(0,T_*)$, $u$ is smooth with $u(t)\in H^k$ for all $k$ (I1), so all manipulations below are classical. Start from the vector identity
$$
(u\cdot\nabla)u=\nabla\tfrac{|u|^2}{2}-u\times\omega ,
$$
which is the componentwise identity $u_j\partial_ju_i=\partial_i\tfrac{|u|^2}{2}-\big(u\times(\nabla\times u)\big)_i$ (expand $\big(u\times(\nabla\times u)\big)_i=u_j\partial_iu_j-u_j\partial_ju_i$). Taking curl and using $\nabla\times\nabla=0$ together with the identity
$$
\nabla\times(a\times b)=a\,(\nabla\cdot b)-b\,(\nabla\cdot a)+(b\cdot\nabla)a-(a\cdot\nabla)b
$$
applied with $a=u$, $b=\omega$ (and $\nabla\cdot u=0$, $\nabla\cdot\omega=\nabla\cdot(\nabla\times u)=0$):
$$
\nabla\times\big((u\cdot\nabla)u\big)=-\nabla\times(u\times\omega)
=(u\cdot\nabla)\omega-(\omega\cdot\nabla)u .
$$
Since $\nabla\times\nabla p=0$, the curl of the Navier–Stokes equation is
$$
\partial_t\omega+(u\cdot\nabla)\omega=\nu\Delta\omega+(\omega\cdot\nabla)u
\qquad\text{on }\mathbb{R}^3\times(0,T_*).
\tag{V}
$$

### Step 2: the enstrophy identity is classical on $(0,T_*)$

By (I1), $u\in C((0,T_*);H^k)$ for all $k$; via the equation, $\partial_tu\in C((0,T_*);H^k)$ as well, so $\omega\in C^1((0,T_*);L^2)$ and $t\mapsto\tfrac12\|\omega(t)\|_{L^2}^2$ is $C^1$ on $(0,T_*)$ with
$$
\frac{d}{dt}\,\frac12\|\omega\|_{L^2}^2
=\big\langle\partial_t\omega,\omega\big\rangle_{L^2}
=\nu\langle\Delta\omega,\omega\rangle-\big\langle(u\cdot\nabla)\omega,\omega\big\rangle+\big\langle(\omega\cdot\nabla)u,\omega\big\rangle .
\tag{E}
$$

### Step 3: integration by parts, justified with cutoffs

Fix $t\in(0,T_*)$; all fields are evaluated at time $t$ and lie in every $H^k$, hence (Sobolev, $H^2(\mathbb{R}^3)\hookrightarrow L^\infty$) $u,\omega,\nabla u,\nabla\omega\in L^2\cap L^\infty$. Let $\chi\in C_c^\infty(\mathbb{R}^3)$ with $0\le\chi\le1$, $\chi\equiv1$ on $B_1$, $\operatorname{supp}\chi\subset B_2$, $|\nabla\chi|\le2$; set $\chi_R(x):=\chi(x/R)$, so $|\nabla\chi_R|\le2/R$.

**(i) Dissipation term.** Integrating by parts on the compactly supported integrand,
$$
\int\chi_R\,\Delta\omega\cdot\omega\,dx
=-\int\chi_R|\nabla\omega|^2\,dx-\int(\nabla\chi_R\cdot\nabla)\omega\cdot\omega\,dx,
$$
and
$$
\Big|\int(\nabla\chi_R\cdot\nabla)\omega\cdot\omega\,dx\Big|
\le\frac2R\,\|\nabla\omega\|_{L^2}\|\omega\|_{L^2}\ \xrightarrow[R\to\infty]{}\ 0 .
$$
Since $\Delta\omega\cdot\omega\in L^1$ and $|\nabla\omega|^2\in L^1$, dominated (resp. monotone) convergence gives
$$
\langle\Delta\omega,\omega\rangle=-\|\nabla\omega\|_{L^2}^2 .
$$

**(ii) Transport term.** Using $(u\cdot\nabla)\omega\cdot\omega=u\cdot\nabla\tfrac{|\omega|^2}{2}$ and $\nabla\cdot u=0$,
$$
\int\chi_R\,u\cdot\nabla\tfrac{|\omega|^2}{2}\,dx
=-\int\tfrac{|\omega|^2}{2}\,u\cdot\nabla\chi_R\,dx,
\qquad
\Big|\int\tfrac{|\omega|^2}{2}\,u\cdot\nabla\chi_R\,dx\Big|
\le\frac1R\,\|u\|_{L^\infty}\|\omega\|_{L^2}^2\ \xrightarrow[R\to\infty]{}\ 0 .
$$
The left side converges to $\big\langle(u\cdot\nabla)\omega,\omega\big\rangle$ (integrand in $L^1$), hence
$$
\big\langle(u\cdot\nabla)\omega,\omega\big\rangle=0 .
$$

**(iii) Stretching term.** No integration by parts is needed. By Lemma B pointwise, then Hölder with exponents $(\infty,2,2)$, then Lemma A (applicable since $u(t)\in H^1$ is divergence-free):
$$
\big\langle(\omega\cdot\nabla)u,\omega\big\rangle
\le\int|\nabla u|\,|\omega|^2\,dx
\le\|\omega\|_{L^\infty}\!\int|\nabla u|\,|\omega|\,dx
\le\|\omega\|_{L^\infty}\|\nabla u\|_{L^2}\|\omega\|_{L^2}
=\|\omega\|_{L^\infty}\,\|\omega\|_{L^2}^2 .
$$
This last equality — $\|\nabla u\|_{L^2}=\|\omega\|_{L^2}$, the exact cancellation supplied by incompressibility — is the entire mechanism of the proof: the vortex-stretching trilinear term is controlled by $\|\omega\|_{L^\infty}$ times the enstrophy itself, with **constant exactly $1$**.

### Step 4: the differential inequality and Grönwall — proof of (a)

Substituting (i)–(iii) into (E): for all $t\in(0,T_*)$,
$$
\frac{d}{dt}\,\frac12\|\omega(t)\|_{L^2}^2+\nu\|\nabla\omega(t)\|_{L^2}^2
\ \le\ \|\omega(t)\|_{L^\infty}\,\|\omega(t)\|_{L^2}^2 .
\tag{D}
$$
Set $y(t):=\|\omega(t)\|_{L^2}^2$ and $\phi(t):=2\|\omega(t)\|_{L^\infty}$; both are continuous on $(0,T_*)$ ($\omega\in C((0,T_*);H^2)$ and $H^2\hookrightarrow L^\infty$). Dropping the dissipation, $y'\le\phi\,y$; hence $\frac{d}{dt}\big(y(t)e^{-\int_s^t\phi}\big)=\big(y'-\phi y\big)e^{-\int_s^t\phi}\le0$, so for $0<s\le t<T_*$
$$
\|\omega(t)\|_{L^2}^2\ \le\ \|\omega(s)\|_{L^2}^2\,\exp\!\Big(2\int_s^t\|\omega(\sigma)\|_{L^\infty}d\sigma\Big),
$$
which is $(\star)$. Keeping the dissipation: integrate (D) after multiplying by $2$, and bound the Grönwall factor once:
$$
y(t)+2\nu\int_s^t\|\nabla\omega\|_{L^2}^2\,d\sigma
\le y(s)+\int_s^t\phi(\sigma)y(\sigma)\,d\sigma
\le y(s)+y(s)\int_s^t\phi(\sigma)e^{\int_s^\sigma\phi}\,d\sigma
= y(s)\,e^{\int_s^t\phi},
$$
using $(\star)$ inside the integral and $\int_s^t \phi\,e^{\int_s^\sigma\phi}d\sigma=e^{\int_s^t\phi}-1$. This is $(\star\star)$. $\square$(a)

### Step 5: continuation — proof of (b)

Suppose $T_*<\infty$ and, for contradiction, that $M:=\int_{t_0}^{T_*}\|\omega(t)\|_{L^\infty}\,dt<\infty$ for some $t_0\in(0,T_*)$. By $(\star)$ with $s=t_0$, for every $t\in[t_0,T_*)$:
$$
\|\nabla u(t)\|_{L^2}\ \overset{\text{Lem. A}}{=}\ \|\omega(t)\|_{L^2}\ \le\ \|\omega(t_0)\|_{L^2}\,e^{M}\ <\ \infty .
$$
On $[0,t_0]$, $t\mapsto\|\nabla u(t)\|_{L^2}$ is continuous (since $u\in C([0,T_*);H^1)$), hence bounded. So $\sup_{t<T_*}\|\nabla u(t)\|_{L^2}<\infty$, contradicting the continuation criterion of (I1), which forces $\|\nabla u(t)\|_{L^2}\to\infty$ as $t\uparrow T_*$ when $T_*<\infty$. Therefore $T_*<\infty$ implies $\int_{t_0}^{T_*}\|\omega\|_{L^\infty}dt=\infty$ for every $t_0\in(0,T_*)$; the contrapositive is the extension statement. $\square$(b)

*Remark (quantitative alternative to the "$\to\infty$" criterion).* One can avoid the qualitative continuation criterion: (I2)'s by-product $T_{\max}\ge c^4\nu^3\|\nabla v^0\|_{L^2}^{-4}$ (proved in `REPORT.md` from Lemma 5.2.2), applied at initial time $t$ with datum $u(t)$ and combined with uniqueness, gives $T_*-t\ge c^4\nu^3\,\|\omega(t_0)\|_{L^2}^{-4}e^{-4M}=:\delta>0$ for **every** $t\in[t_0,T_*)$; choosing $t>T_*-\delta$ is a contradiction. Both routes rest on the same cited local theory.

### Step 6: proof of Corollary W2.1

Let $T_*<\infty$ and $0<s\le t<T_*$. By (I2), $\|\omega(t)\|_{L^2}^2=\|\nabla u(t)\|_{L^2}^2\ge c^2\nu^{3/2}(T_*-t)^{-1/2}$. Feeding this into $(\star)$:
$$
\exp\!\Big(2\int_s^t\|\omega\|_{L^\infty}d\sigma\Big)
\ \ge\ \frac{\|\omega(t)\|_{L^2}^2}{\|\omega(s)\|_{L^2}^2}
\ \ge\ \frac{c^2\nu^{3/2}}{\|\omega(s)\|_{L^2}^2}\,(T_*-t)^{-1/2}.
$$
Taking logarithms and dividing by $2$:
$$
\int_s^t\|\omega(\sigma)\|_{L^\infty}\,d\sigma
\ \ge\ \frac14\log\frac{1}{T_*-t}+\log\frac{c\,\nu^{3/4}}{\|\omega(s)\|_{L^2}} ,
$$
and $\|\omega(s)\|_{L^2}=\|\nabla u(s)\|_{L^2}$ by Lemma A. $\square$

### Step 7: proof of Corollary W2.2

Suppose, for contradiction, $\limsup_{t\uparrow T_*}(T_*-t)\|\omega(t)\|_{L^\infty}=a<\tfrac14$, and fix $a'\in(a,\tfrac14)$. Then there is $s\in(0,T_*)$ with $\|\omega(\sigma)\|_{L^\infty}\le a'(T_*-\sigma)^{-1}$ for all $\sigma\in[s,T_*)$, whence for $t\in(s,T_*)$
$$
\int_s^t\|\omega(\sigma)\|_{L^\infty}d\sigma\ \le\ a'\log\frac{T_*-s}{T_*-t}
\ =\ a'\log\frac{1}{T_*-t}+a'\log(T_*-s).
$$
Corollary W2.1 gives the lower bound $\tfrac14\log\frac{1}{T_*-t}-C(s)$ with $C(s):=\log\big(\|\nabla u(s)\|_{L^2}/(c\nu^{3/4})\big)$ finite. Combining and dividing by $\log\frac{1}{T_*-t}\to+\infty$ as $t\uparrow T_*$:
$$
a'\ \ge\ \frac14 ,
$$
contradicting $a'<\tfrac14$. Hence $\limsup_{t\uparrow T_*}(T_*-t)\|\omega(t)\|_{L^\infty}\ge\tfrac14$. $\blacksquare$

### Scaling check (consistency)

Under $u_\lambda(x,t)=\lambda u(\lambda x,\lambda^2t)$ one has $\omega_\lambda(x,t)=\lambda^2\omega(\lambda x,\lambda^2 t)$, so
$$
\int_0^{T/\lambda^2}\|\omega_\lambda(t)\|_{L^\infty}\,dt
=\int_0^{T/\lambda^2}\lambda^2\|\omega(\lambda^2t)\|_{L^\infty}\,dt
=\int_0^{T}\|\omega(\tau)\|_{L^\infty}\,d\tau .
$$
The BKM integral is **exactly scale-invariant** (and dimensionless: $[\omega]=\text{time}^{-1}$), i.e. the criterion sits precisely on the critical line — consistent with `REPORT.md` §3.2's observation that the entire criterion industry lives at criticality. Likewise $(T_*-t)\|\omega(t)\|_{L^\infty}$ in Corollary W2.2 is scale-invariant, which is why its threshold $\tfrac14$ can be absolute.

---

## What is new vs REPORT.md

1. **BKM is proved here; in `REPORT.md` it is only cited.** §3.2 of the report states BKM as `[KNOWN — BKM84]` with no proof anywhere in the dossier. The four proved items in `REPORT.md` §5 are Fujita–Kato (§5.1), the Leray enstrophy rate (§5.2), the dimension of singular times (§5.3), and the formalized Tao no-go (§5.4). None contains, implies, or resembles the proof above.
2. **The mechanism is disjoint from Fujita–Kato (§5.1).** No mild formulation, no fixed point, no critical spaces, no Littlewood–Paley/paraproduct machinery, no smallness. The proof runs entirely at the vorticity level: the curl of the equation (V), the exact incompressibility cancellation $\|\nabla u\|_{L^2}=\|\omega\|_{L^2}$ (Lemma A), the transport cancellation $\langle(u\cdot\nabla)\omega,\omega\rangle=0$, and a linear Grönwall. This is not a rewrite of anything in the report.
3. **It is also not a rewrite of the report's enstrophy inequality (Lemma 5.2.2).** That inequality is at the velocity level, cubic in enstrophy ($X'\le K_0\nu^{-3}X^3$), and its constant $K_0$ absorbs unnamed Sobolev/interpolation constants. Inequality (D) here is *linear* in enstrophy with the critical coefficient $\|\omega\|_{L^\infty}$, is dissipation-retaining ($\star\star$), and carries the **absolute constant $2$** with no embedding constants at all — this is target #2 of the wave-2 menu ("explicit enstrophy differential inequality with constants written") delivered as a by-product of target #1.
4. **The corollaries are new to the dossier.** Corollary W2.1 (logarithmic lower bound with explicit leading coefficient $\tfrac14$) and Corollary W2.2 ($\limsup(T_*-t)\|\omega(t)\|_{L^\infty}\ge\tfrac14$, absolute constant) are obtained by splicing the new estimate $(\star)$ with the report's own Theorem 5.2; neither statement (nor any quantitative vorticity-rate statement) appears in `REPORT.md`.

## Why Millennium NS remains open

- **The theorem is conditional, and its hypothesis is critical.** By the scaling check above, $\int_0^T\|\omega\|_{L^\infty}dt$ is scale-invariant. The only quantities controlled a priori for large data — energy and dissipation — are *supercritical* (`REPORT.md` §2.3, §3.10, obstruction O1). No known argument bounds a critical quantity a priori for large data; producing such a bound is essentially the Millennium problem itself. Theorem W2 converts one unbounded critical quantity ($\int\|\omega\|_{L^\infty}$) into regularity; it does not bound it.
- **Consistency with the no-go (§5.4).** Nothing here contradicts Proposition 5.4 of the report: the proof does exploit exact structure (the curl cancellations of Lemmas A and Step 3(ii) are properties of the true nonlinearity, not of Tao's averaged class), but the output is a *conditional criterion*, not an unconditional bound — exactly the pattern §3.2 of the report describes for the entire criterion industry. Breaking energy-abstraction is necessary but visibly not sufficient.
- **The corollaries constrain, but do not construct or exclude, blow-up.** W2.1–W2.2 say any hypothetical singularity must accumulate at least $\tfrac14\log\frac{1}{T_*-t}$ of integrated vorticity and attain the rate $(T_*-t)^{-1}$ along a sequence of times. This narrows the phenomenology (cf. obstruction O5) by explicit constants; it decides neither Clay (A)/(B) nor (C)/(D).

## Honesty label

- **Theorem W2:** `[KNOWN — proof written out here]`. The BKM criterion originates with Beale–Kato–Majda 1984 [BKM84] (for Euler; the log-Sobolev route). The Navier–Stokes enstrophy-level version proved here is standard textbook material (cf. Majda–Bertozzi; Robinson–Rodrigo–Sadowski [RRS16]). No novelty is claimed at the level of the statement. The value delivered is a complete, self-contained, constant-explicit proof **absent from `REPORT.md`**, by a mechanism absent from `REPORT.md`, with only the local-theory package (I1) cited — the same citation standard the report itself uses in §5.2–5.3.
- **Corollaries W2.1–W2.2:** `[SYNTHESIS]`. Qualitative content (log divergence of the BKM integral; $(T_*-t)^{-1}$ vorticity rate at blow-up) is known folklore; the specific explicit constants ($\tfrac14$ in both, inherited from the constant $2$ in $(\star)$ and the report's fully proved Theorem 5.2) are assembled here and, to our knowledge, this exact constant-explicit form does not appear verbatim in the literature. No new mathematics beyond assembly is claimed.
- **Millennium status:** untouched. No global regularity is claimed, no blow-up is claimed, and no unconditional supercritical bound is claimed. Per the wave-2 mandate: **no fake global regularity.**
