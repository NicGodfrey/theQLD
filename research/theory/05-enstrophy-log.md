# 05 — Enstrophy excursions: a quantitative window-counting theorem for 3D Navier–Stokes

**Wave 3, original theory.** One new statement (Theorem 1), a complete proof with every constant explicit, and corollaries. **Honesty tag:** `[NEW QUANTITATIVE FORM — ingredients classical, assembly and explicit constants ours, statement possibly folklore; no global regularity claimed]`.

**One-paragraph statement.** *Let $u^0\in H^1(\mathbb{R}^3)$ be divergence-free and let $u$ be the maximal strong solution of 3D incompressible Navier–Stokes (viscosity $\nu>0$, zero force) on $[0,T_*)$, $\omega=\nabla\times u$. Fix any threshold $M>0$ and let $E_M:=\{t\in[0,T_*):\|\nabla u(t)\|_{L^2}>M\}$; call a connected component of $E_M$ an* almost-blow-up window *if $\|\nabla u\|_{L^2}$ reaches $2^{1/4}M$ inside it. Then: (i) $|E_M|\le\|u^0\|_{L^2}^2/(2\nu M^2)$; (ii) every window not containing $t=0$ lasts at least $\nu^3/(2M^4)$, this being already the time needed inside the window for $\|\nabla u\|_{L^2}$ to climb from $M$ to $2^{1/4}M$; (iii) consequently the number $N(M)$ of windows is finite, $N(M)\le M^2\|u^0\|_{L^2}^2/\nu^4+1$ (the $+1$ removable when $\|\nabla u^0\|_{L^2}\le M$); (iv) the total length of all windows is $\le\|u^0\|_{L^2}^2/(2\nu M^2)$ and outside their union $\|\nabla u(t)\|_{L^2}<2^{1/4}M$; (v) if $T_*<\infty$ then the terminal segment of length $\min(T_*,\nu^3/M^4)$ lies inside a single window — blow-up is "announced" at every threshold $M$ by an uninterrupted excursion of at least that duration. All constants are absolute and explicit; the count in (iii) is dimensionless and scale-invariant. A corollary with the same constants: if $T_*<\infty$ then $T_*\le\|u^0\|_{L^2}^4/(16\nu^5)$.*

---

## 0. Scope; relation to the Wave-2 BKM note and to `REPORT.md`

This note proves something **absent** from `conjectures/05-navier-stokes/BREAKTHROUGH.md` (the Wave-2 BKM note) and from `conjectures/05-navier-stokes/REPORT.md` §5:

- The bound $\int_s^t\|\omega(\sigma)\|_{L^\infty}\,d\sigma\ \ge\ \log\big(\|\omega(t)\|_{L^2}/\|\omega(s)\|_{L^2}\big)$ (with constant $c=1$, better than the target $c=\tfrac12$, and with **no** hypothesis $\|\omega\|_{L^\infty}\ge1$) is the logarithm of Wave-2's Grönwall estimate $(\star)$. It is Wave-2 content and is **not claimed here**.
- `REPORT.md` §5.2 proves the enstrophy ODE and the Leray rate with *unnamed* absolute constants $K_0$, $c=(2K_0)^{-1/4}$. Here every constant is computed: $K_0=\tfrac12$ (Proposition 3.1) and $c=1$ (Proposition 4.1). These explicit values feed the main theorem; the mechanism is Leray's and no novelty is claimed for it.
- `REPORT.md` §5.3 proves Leray's structure theorem ($\dim_{\mathcal H}\Sigma\le\tfrac12$ for singular times, via a Vitali cover). Theorem 1 below is **not** a rewrite of that: it is a *threshold-explicit* statement at every finite level $M$, it is nontrivial also for globally regular solutions (where $\Sigma=\varnothing$ and §5.3 says nothing quantitative), it counts excursions rather than measuring a limit set, and its covering argument is by first-hitting subintervals, not Vitali.

No claim on the Millennium problem is made (see §8).

## 1. Setting, notation, cited ingredients

$\nu>0$; $u^0\in H^1(\mathbb{R}^3)$ divergence-free; $u$ the unique **maximal strong solution** on $[0,T_*)$, $T_*\le\infty$: $u\in C([0,T_*);H^1)\cap L^2_{loc}([0,T_*);H^2)$, divergence-free, smooth on $\mathbb{R}^3\times(0,T_*)$ with $u\in C((0,T_*);H^k)$ for all $k$. Vorticity $\omega=\nabla\times u$; $|\nabla\omega|$, $|\nabla u|$ denote Frobenius norms. Throughout
$$
y(t)\ :=\ \|\omega(t)\|_{L^2}^2\ \overset{\text{(I3a)}}{=}\ \|\nabla u(t)\|_{L^2}^2 ,
\qquad
D\ :=\ \frac{\|u^0\|_{L^2}^2}{2\nu}\quad(\text{the total dissipation budget}).
$$
$y$ is continuous on $[0,T_*)$ (since $u\in C([0,T_*);H^1)$) and $C^1$ on $(0,T_*)$ (Wave-2, Step 2).

**Cited ingredients** (the only external inputs; everything else is proved here):

- **(I1)** `REPORT.md` Lemma 5.2.1: existence/uniqueness of the maximal strong solution as above; if $T_*<\infty$ then $\|\nabla u(t)\|_{L^2}\to\infty$ as $t\uparrow T_*$. `[KNOWN — FK64, RRS16, LR16]`
- **(I2)** Energy equality for strong solutions: $\tfrac12\|u(t)\|_{L^2}^2+\nu\int_0^t\|\nabla u\|_{L^2}^2\,d\sigma=\tfrac12\|u^0\|_{L^2}^2$ on $[0,T_*)$; in particular
$$
\int_0^{T_*}y(\sigma)\,d\sigma\ \le\ D .
\tag{1.1}
$$
`[KNOWN — standard; e.g. RRS16]` (Only the inequality (1.1) is used, so Leray–Hopf's energy *inequality* would also suffice.)
- **(I3)** Wave-2 note, Steps 1–3 and Lemmas A–B (all fully proved there):
  - **(I3a)** $\|\nabla v\|_{L^2}=\|\nabla\times v\|_{L^2}$ for divergence-free $v\in H^1$ (Wave-2 Lemma A);
  - **(I3b)** the pointwise stretching bound $|((\omega\cdot\nabla)u)\cdot\omega|\le|\omega|^2|\nabla u|$ (Wave-2 Lemma B);
  - **(I3c)** the enstrophy identity, valid on $(0,T_*)$:
$$
\tfrac12\,y'(t)+\nu\|\nabla\omega(t)\|_{L^2}^2\ =\ \big\langle(\omega\cdot\nabla)u,\ \omega\big\rangle_{L^2} .
\tag{1.2}
$$

## 2. Elementary inequalities with explicit constants (proved from scratch)

### Lemma 2.1 (one-dimensional bound)
For $g\in C_c^1(\mathbb{R}^3)$ and each $i\in\{1,2,3\}$,
$$
|g(x)|\ \le\ \tfrac12\int_{\mathbb{R}}|\partial_i g|\,dx_i
\qquad\text{for every }x .
$$
*Proof.* $g(x)=\int_{-\infty}^{x_i}\partial_i g$ and $g(x)=-\int_{x_i}^{\infty}\partial_i g$ along the $x_i$-line; take absolute values and add: $2|g(x)|\le\int_{\mathbb{R}}|\partial_i g|\,dx_i$. $\square$

### Lemma 2.2 (Loomis–Whitney, $n=3$, exponent $\tfrac12$)
For measurable $F_1(x_2,x_3),F_2(x_1,x_3),F_3(x_1,x_2)\ge0$,
$$
\int_{\mathbb{R}^3}F_1^{1/2}F_2^{1/2}F_3^{1/2}\,dx\ \le\ \Big(\iint F_1\Big)^{1/2}\Big(\iint F_2\Big)^{1/2}\Big(\iint F_3\Big)^{1/2}.
$$
*Proof.* Three applications of Cauchy–Schwarz. First in $x_1$ (with $x_2,x_3$ fixed; $F_1^{1/2}$ is constant):
$$
\int F_1^{1/2}F_2^{1/2}F_3^{1/2}dx_1\ \le\ F_1(x_2,x_3)^{1/2}\,G_2(x_3)^{1/2}\,G_3(x_2)^{1/2},
$$
where $G_2(x_3):=\int F_2\,dx_1$, $G_3(x_2):=\int F_3\,dx_1$. Next in $x_2$ ($x_3$ fixed):
$$
\int F_1(x_2,x_3)^{1/2}G_3(x_2)^{1/2}dx_2\ \le\ \Big(\int F_1\,dx_2\Big)^{1/2}\Big(\int G_3\,dx_2\Big)^{1/2},
$$
so the running bound is $G_2(x_3)^{1/2}\big(\int F_1dx_2\big)^{1/2}\big(\iint F_3\big)^{1/2}$. Finally Cauchy–Schwarz in $x_3$ on $G_2^{1/2}\cdot\big(\int F_1dx_2\big)^{1/2}$ gives the claim. $\square$

### Proposition 2.3 (Sobolev $L^6$ inequality with constant $2/\sqrt3$)
For every $f\in H^1(\mathbb{R}^3)$,
$$
\|f\|_{L^6}\ \le\ \frac{2}{\sqrt3}\,\|\nabla f\|_{L^2}.
\tag{2.1}
$$
*Proof.* Let first $f\in C_c^\infty$, $f\not\equiv0$, and set $g:=f^4\in C_c^1$. By Lemma 2.1, $|g(x)|^{3/2}=\prod_{i=1}^3|g(x)|^{1/2}\le\prod_{i=1}^3\big(\tfrac12\int|\partial_i g|\,dx_i\big)^{1/2}$. Integrating over $\mathbb{R}^3$ and applying Lemma 2.2 with $F_i:=\tfrac12\int|\partial_i g|dx_i$ (a function of the two remaining variables):
$$
\int|g|^{3/2}\ \le\ \prod_{i=1}^3\Big(\tfrac12\|\partial_i g\|_{L^1}\Big)^{1/2}
\quad\Longrightarrow\quad
\|g\|_{L^{3/2}}\ \le\ \tfrac12\prod_{i=1}^3\|\partial_i g\|_{L^1}^{1/3}.
$$
Now $\|g\|_{L^{3/2}}=\big(\int|f|^6\big)^{2/3}=\|f\|_{L^6}^4$ and, by Cauchy–Schwarz, $\|\partial_i g\|_{L^1}\le4\int|f|^3|\partial_i f|\le4\|f\|_{L^6}^3\|\partial_i f\|_{L^2}$. Hence
$$
\|f\|_{L^6}^4\ \le\ \tfrac12\cdot4\,\|f\|_{L^6}^3\prod_{i=1}^3\|\partial_i f\|_{L^2}^{1/3}
\quad\Longrightarrow\quad
\|f\|_{L^6}\ \le\ 2\prod_{i=1}^3\|\partial_i f\|_{L^2}^{1/3}.
$$
By AM–GM, $\prod_i a_i^{1/3}=\big(\prod_i a_i^2\big)^{1/6}\le\big(\tfrac13\sum_i a_i^2\big)^{1/2}$ with $a_i=\|\partial_i f\|_{L^2}$, giving (2.1) on $C_c^\infty$. For general $f\in H^1$: take $f_n\in C_c^\infty$ with $f_n\to f$ in $H^1$ and a.e.; Fatou on the left and $\|\nabla f_n\|_{L^2}\to\|\nabla f\|_{L^2}$ on the right give (2.1). $\square$

*(The sharp constant is Talenti's $\approx0.4783$; the elementary $2/\sqrt3\approx1.1547$ is all we need, and any smaller admissible constant would only improve every constant below.)*

### Lemma 2.4 (interpolation $L^4$ between $L^2$ and $L^6$)
For $f\in L^2\cap L^6$: $\ \|f\|_{L^4}\le\|f\|_{L^2}^{1/4}\|f\|_{L^6}^{3/4}$.

*Proof.* One Cauchy–Schwarz: $\int|f|^4=\int|f|\cdot|f|^3\le\big(\int|f|^2\big)^{1/2}\big(\int|f|^6\big)^{1/2}=\|f\|_{L^2}\|f\|_{L^6}^3$. Take fourth roots. $\square$

### Lemma 2.5 (vector-field Gagliardo–Nirenberg, lossless via regularization)
For a smooth vector field $\omega\in H^1(\mathbb{R}^3;\mathbb{R}^3)$ with $\nabla\omega\in L^2$,
$$
\|\omega\|_{L^4}^2\ \le\ \Big(\frac{2}{\sqrt3}\Big)^{3/2}\|\omega\|_{L^2}^{1/2}\,\|\nabla\omega\|_{L^2}^{3/2}.
\tag{2.2}
$$
*Proof.* For $\delta>0$ set $f_\delta:=(|\omega|^2+\delta^2)^{1/2}-\delta$, a smooth **scalar** function with $0\le f_\delta\le|\omega|$ (since $(|\omega|^2+\delta^2)^{1/2}\le|\omega|+\delta$) and
$$
\partial_i f_\delta=\frac{\sum_j\omega_j\,\partial_i\omega_j}{(|\omega|^2+\delta^2)^{1/2}}
\ \Longrightarrow\
|\partial_i f_\delta|\le\frac{|\omega|\,|\partial_i\omega|}{(|\omega|^2+\delta^2)^{1/2}}\le|\partial_i\omega|
\ \Longrightarrow\
|\nabla f_\delta|\le|\nabla\omega| \text{ pointwise.}
$$
So $f_\delta\in H^1$ and Lemma 2.4 + Proposition 2.3 give
$\|f_\delta\|_{L^4}\le(2/\sqrt3)^{3/4}\|f_\delta\|_{L^2}^{1/4}\|\nabla f_\delta\|_{L^2}^{3/4}\le(2/\sqrt3)^{3/4}\|\omega\|_{L^2}^{1/4}\|\nabla\omega\|_{L^2}^{3/4}$.
Since $\tfrac{d}{d\delta}f_\delta=\delta(|\omega|^2+\delta^2)^{-1/2}-1\le0$, $f_\delta\uparrow|\omega|$ pointwise as $\delta\downarrow0$; monotone convergence gives $\|f_\delta\|_{L^4}\to\|\omega\|_{L^4}$. Square. $\square$

## 3. The enstrophy ODE with the explicit constant $\tfrac12$

### Proposition 3.1
On $(0,T_*)$,
$$
y'(t)\ \le\ \frac{1}{2\nu^3}\,y(t)^3 .
\tag{3.1}
$$
*(This makes `REPORT.md` Lemma 5.2.2 explicit: $K_0=\tfrac12$, obtained at the vorticity level.)*

*Proof.* Fix $t\in(0,T_*)$; all fields lie in every $H^k$ (I1). Chain of inequalities on the stretching term of (1.2), each constant displayed:
$$
\big\langle(\omega\cdot\nabla)u,\omega\big\rangle
\ \overset{\text{(I3b)}}{\le}\ \int|\nabla u|\,|\omega|^2
\ \overset{\text{Hölder }(2,2)}{\le}\ \|\nabla u\|_{L^2}\,\|\omega\|_{L^4}^2
\ \overset{\text{(I3a)}}{=}\ \|\omega\|_{L^2}\,\|\omega\|_{L^4}^2
\ \overset{(2.2)}{\le}\ \Big(\tfrac{2}{\sqrt3}\Big)^{3/2} y^{3/4}\,\|\nabla\omega\|_{L^2}^{3/2}.
$$
Young's inequality $ab\le\tfrac34a^{4/3}+\tfrac14b^4$ with $a=\varepsilon\|\nabla\omega\|_{L^2}^{3/2}$, $b=\varepsilon^{-1}(2/\sqrt3)^{3/2}y^{3/4}$ and $\tfrac34\varepsilon^{4/3}=\nu$ (so $\varepsilon^{-4}=\tfrac{27}{64\nu^3}$, and $(2/\sqrt3)^6=\tfrac{64}{27}$):
$$
\big\langle(\omega\cdot\nabla)u,\omega\big\rangle
\ \le\ \nu\,\|\nabla\omega\|_{L^2}^2+\frac14\cdot\frac{27}{64\nu^3}\cdot\frac{64}{27}\,y^3
\ =\ \nu\,\|\nabla\omega\|_{L^2}^2+\frac{y^3}{4\nu^3}.
$$
Insert into (1.2): $\tfrac12y'+\nu\|\nabla\omega\|_{L^2}^2\le\nu\|\nabla\omega\|_{L^2}^2+\tfrac{1}{4\nu^3}y^3$, i.e. (3.1). $\square$

## 4. The Leray rate with constant exactly $1$, and the safe window

### Proposition 4.1 (constant-one blow-up rate)
If $T_*<\infty$, then
$$
\|\nabla u(t)\|_{L^2}^2\ =\ y(t)\ \ge\ \frac{\nu^{3/2}}{\sqrt{T_*-t}}
\qquad\text{for all }t\in[0,T_*),
\tag{4.1}
$$
and consequently $T_*\ge\nu^3/\|\nabla u^0\|_{L^2}^4$.

*Proof.* Set $K:=\tfrac{1}{2\nu^3}$, so $y'\le Ky^3$ on $(0,T_*)$ by (3.1). First, $T_*<\infty$ forces $y(t)>0$ for every $t\in[0,T_*)$: if $y(t_1)=0$ for some $t_1$, then $\nabla u(t_1)=0$ in $L^2$ by (I3a), and an $L^2$ function with vanishing distributional gradient is $0$, so $u(t_1)=0$; by uniqueness (I1) the solution restarted from the datum $0$ is $u\equiv0$ for $t\ge t_1$, which is global — contradicting $T_*<\infty$. So $y^{-2}$ is $C^1$ on $(0,T_*)$ with $\tfrac{d}{dt}(y^{-2})=-2y^{-3}y'\ge-2K$. Integrating on $[t,s]\subset(0,T_*)$:
$$
y(s)^{-2}\ \ge\ y(t)^{-2}-2K(s-t).
$$
By (I1), $y(s)\to\infty$ as $s\uparrow T_*$, so letting $s\uparrow T_*$: $0\ge y(t)^{-2}-2K(T_*-t)$, i.e. $y(t)^2\ge\tfrac{1}{2K(T_*-t)}=\tfrac{\nu^3}{T_*-t}$ for $t\in(0,T_*)$; at $t=0$ by continuity of $y$. Taking $t=0$ and rearranging: $T_*\ge\nu^3/y(0)^2$. $\square$

### Lemma 4.2 (growth needs time: from level $M^2$ to level $\sqrt2\,M^2$)
Let $0\le a<\tau<T_*$ with $y(a)\le M^2$ and $y(\tau)\ge\sqrt2\,M^2$, and $y>0$ on $[a,\tau]$. Then
$$
\tau-a\ \ge\ \frac{\nu^3}{2M^4}.
\tag{4.2}
$$
*Proof.* As in Proposition 4.1, $y(\tau)^{-2}\ge y(a)^{-2}-2K(\tau-a)$ (integrate on $(a,\tau]$ and use continuity at $a$ if $a=0$). Hence
$$
\frac{1}{2M^4}\ \ge\ \frac{1}{y(\tau)^{2}}\ \ge\ \frac{1}{y(a)^{2}}-\frac{\tau-a}{\nu^{3}}\ \ge\ \frac{1}{M^{4}}-\frac{\tau-a}{\nu^{3}},
$$
so $(\tau-a)/\nu^3\ge\tfrac{1}{M^4}-\tfrac{1}{2M^4}=\tfrac{1}{2M^4}$. $\square$

## 5. Main theorem: quantitative excursion counting

### Definitions
Fix $M>0$. The **bad set** is
$$
E_M\ :=\ \{t\in[0,T_*):\ \|\nabla u(t)\|_{L^2}>M\}\ =\ \{t:\ y(t)>M^2\},
$$
relatively open in $[0,T_*)$ by continuity of $y$, hence a disjoint union of at most countably many relatively open intervals (**components**), each of the form $(a,b)$ with $0\le a<b\le T_*$, or $[0,b)$ if $0\in E_M$. A component $W$ is an **almost-blow-up window** if
$$
\exists\,t\in W:\quad \|\nabla u(t)\|_{L^2}\ \ge\ 2^{1/4}M\qquad(\text{i.e. } y(t)\ge\sqrt2\,M^2),
$$
and **shallow** otherwise. ($2^{1/4}\approx1.19$: a window is an excursion above $M$ during which the gradient norm climbs a further factor $2^{1/4}$.)

### Theorem 1 (finiteness, duration, and total length of almost-blow-up windows)
Let $u$ be the maximal strong solution as in §1, $D=\|u^0\|_{L^2}^2/(2\nu)$, and fix $M>0$. Then:

**(i) (Measure of the bad set.)**
$$
|E_M|\ \le\ \frac{D}{M^2}\ =\ \frac{\|u^0\|_{L^2}^2}{2\nu M^2}.
$$

**(ii) (Minimum duration; explicit ramp-up time.)** Every almost-blow-up window $W$ with $0\notin W$ satisfies
$$
|W|\ \ge\ \frac{\nu^3}{2M^4},
$$
and more precisely: writing $a=\inf W$ and $\tau=$ the first time in $W$ with $y(\tau)=\sqrt2M^2$, one has $\tau-a\ge\nu^3/(2M^4)$ — the solution must spend at least $\nu^3/(2M^4)$ inside the window before first reaching level $2^{1/4}M$.

**(iii) (Counting.)** The number $N(M)$ of almost-blow-up windows is finite, with the dimensionless, scale-invariant bound
$$
N(M)\ \le\ \frac{M^2\,\|u^0\|_{L^2}^2}{\nu^4}\ +\ 1,
$$
and the $+1$ can be dropped when $\|\nabla u^0\|_{L^2}\le M$ (then $0\notin E_M$).

**(iv) (Total length; control off the windows.)** The union $B_M$ of all almost-blow-up windows satisfies $|B_M|\le|E_M|\le\|u^0\|_{L^2}^2/(2\nu M^2)$, and
$$
\|\nabla u(t)\|_{L^2}\ <\ 2^{1/4}M\qquad\text{for every }t\in[0,T_*)\setminus B_M .
$$

**(v) (Terminal window: blow-up is announced.)** If $T_*<\infty$, then the terminal segment
$$
\big(T_*-\min(T_*,\ \nu^3/M^4),\ T_*\big)
$$
is contained in a **single** almost-blow-up window. In particular, at every threshold $M$, blow-up is preceded by one uninterrupted excursion with $\|\nabla u\|_{L^2}>M$ of length at least $\min(T_*,\nu^3/M^4)$.

### Proof

**(i).** $E_M$ is measurable (open). Chebyshev against the dissipation budget (1.1):
$$
M^2\,|E_M|\ \le\ \int_{E_M}y(\sigma)\,d\sigma\ \le\ \int_0^{T_*}y(\sigma)\,d\sigma\ \le\ D .
$$

**(ii).** Let $W$ be an almost-blow-up window with $0\notin W$, so $W=(a,b)$ with $a=\inf W\notin W$ and $a\ge0$. Since $a\in[0,T_*)\setminus E_M$, $y(a)\le M^2$; since $y>M^2$ on $(a,b)$ and $y$ is continuous, $y(a)=M^2$. The set $S:=\{t\in(a,b):y(t)\ge\sqrt2M^2\}$ is nonempty (definition of window) and closed in $(a,b)$; since $y(a)=M^2<\sqrt2M^2$ and $y$ is continuous, $y<\sqrt2M^2$ on a right-neighbourhood of $a$, so $\tau:=\inf S\in(a,b)$, $\tau\in S$ (closedness), and by minimality plus continuity $y(\tau)=\sqrt2M^2$ while $y<\sqrt2M^2$ on $[a,\tau)$. On $[a,\tau]$ we have $y\ge M^2>0$, so Lemma 4.2 applies: $\tau-a\ge\nu^3/(2M^4)$. Finally $|W|=b-a\ge\tau-a$.

**(iii).** Let $W_1,W_2,\dots$ be the almost-blow-up windows not containing $0$, with $a_j=\inf W_j$ and first-hitting times $\tau_j$ as in (ii). The intervals $(a_j,\tau_j]$ are pairwise disjoint (each is a subset of its own component $W_j$, and distinct components are disjoint), each is contained in $E_M$ (because $(a_j,\tau_j]\subset W_j$), and each has length $\ge\nu^3/(2M^4)$ by (ii). Hence if $N'$ of them exist,
$$
N'\cdot\frac{\nu^3}{2M^4}\ \le\ |E_M|\ \overset{\text{(i)}}{\le}\ \frac{\|u^0\|_{L^2}^2}{2\nu M^2}
\quad\Longrightarrow\quad
N'\ \le\ \frac{M^2\,\|u^0\|_{L^2}^2}{\nu^4}.
$$
At most one component of $E_M$ contains $0$ (and exists only if $y(0)>M^2$, i.e. $\|\nabla u^0\|_{L^2}>M$), contributing the $+1$. So $N(M)\le N'+1\le M^2\|u^0\|_{L^2}^2/\nu^4+1$, finite; and $N(M)=N'$ when $\|\nabla u^0\|_{L^2}\le M$.

**(iv).** $B_M\subset E_M$ gives the length bound via (i). If $t\notin B_M$, then either $t\notin E_M$, whence $y(t)\le M^2<\sqrt2M^2$; or $t$ lies in a shallow component, where $y<\sqrt2M^2$ by the definition of shallow. Either way $\|\nabla u(t)\|_{L^2}<2^{1/4}M$.

**(v).** Let $T_*<\infty$ and set $\ell:=\min(T_*,\nu^3/M^4)$. For $t\in(T_*-\ell,\ T_*)$ we have $T_*-t<\nu^3/M^4$, so Proposition 4.1 gives
$$
y(t)\ \ge\ \frac{\nu^{3/2}}{\sqrt{T_*-t}}\ >\ \nu^{3/2}\Big(\frac{M^4}{\nu^3}\Big)^{1/2}\ =\ M^2 ,
$$
hence $(T_*-\ell,T_*)\subset E_M$. Being an interval, it lies in a single component $W_{\rm last}$; by (I1) $y(t)\to\infty$ as $t\uparrow T_*$, so $W_{\rm last}$ contains times with $y\ge\sqrt2M^2$ and is an almost-blow-up window; and $|W_{\rm last}|\ge\ell$. $\blacksquare$

## 6. Corollary: the explicit Leray deadline

### Corollary 6.1
If $T_*<\infty$, then
$$
T_*\ \le\ \frac{\|u^0\|_{L^2}^4}{16\,\nu^5}.
$$
Equivalently: **if the strong solution still exists at time $\|u^0\|_{L^2}^4/(16\nu^5)$, it is global** ($T_*=\infty$).

*Proof.* Integrate the constant-one rate (4.1) against the dissipation budget (1.1):
$$
\frac{\|u^0\|_{L^2}^2}{2\nu}\ \ge\ \int_0^{T_*}y(\sigma)\,d\sigma
\ \ge\ \nu^{3/2}\int_0^{T_*}\frac{d\sigma}{\sqrt{T_*-\sigma}}
\ =\ 2\,\nu^{3/2}\sqrt{T_*}\ ,
$$
so $\sqrt{T_*}\le\|u^0\|_{L^2}^2/(4\nu^{5/2})$ and $T_*\le\|u^0\|_{L^2}^4/(16\nu^5)$. $\blacksquare$

*Remark.* Qualitative eventual regularity is Leray 1934 and appears (without constants, via §5.1-smallness) in `REPORT.md` §5.3; the explicit deadline with constant $16$ — a two-line splice of (4.1) and (1.1), both now free of unnamed factors — is recorded here because Theorem 1(v) and Corollary 6.1 together give a fully explicit picture: blow-up, if it ever happens, happens before $\|u^0\|_{L^2}^4/(16\nu^5)$ and is announced at every threshold $M$ by a terminal window of length $\ge\min(T_*,\nu^3/M^4)$.

## 7. Scaling and dimensional audit

Dimensions: $[\nu]=L^2T^{-1}$, $[\|u^0\|_{L^2}^2]=L^5T^{-2}$, $[y]=[M^2]=L^3T^{-2}$.

- $|E_M|$-bound: $\dfrac{\|u^0\|_{L^2}^2}{2\nu M^2}\sim\dfrac{L^5T^{-2}}{L^2T^{-1}\cdot L^3T^{-2}}=T$. ✓
- Window duration: $\dfrac{\nu^3}{2M^4}\sim\dfrac{L^6T^{-3}}{L^6T^{-4}}=T$. ✓
- Count: $\dfrac{M^2\|u^0\|_{L^2}^2}{\nu^4}\sim\dfrac{L^3T^{-2}\cdot L^5T^{-2}}{L^8T^{-4}}=1$ — dimensionless, as a count must be. ✓
- Deadline: $\dfrac{\|u^0\|_{L^2}^4}{\nu^5}\sim\dfrac{L^{10}T^{-4}}{L^{10}T^{-5}}=T$. ✓

Under the Navier–Stokes scaling $u_\lambda(x,t)=\lambda u(\lambda x,\lambda^2t)$: $y_\lambda(t)=\lambda\,y(\lambda^2t)$, so thresholds transform as $M_\lambda^2=\lambda M^2$, while $\|u^0_\lambda\|_{L^2}^2=\lambda^{-1}\|u^0\|_{L^2}^2$ and $\nu$ is fixed. Then $M_\lambda^2\|u^0_\lambda\|_{L^2}^2/\nu^4=M^2\|u^0\|_{L^2}^2/\nu^4$: **the window count is scale-invariant**, and all time quantities (the $|E_M|$-bound, $\nu^3/(2M^4)$, $\nu^3/M^4$, the deadline) scale as $\lambda^{-2}$, exactly as times must. ✓ Consistency under $M\to\infty$: the count bound grows like $M^2$ while each window shortens like $M^{-4}$ and the total bad measure decays like $M^{-2}$ — the product $N_{\max}\cdot(\text{min duration})=\tfrac{\nu^3}{2M^4}\cdot\tfrac{M^2\|u^0\|^2}{\nu^4}=\tfrac{\|u^0\|^2}{2\nu M^2}$ reproduces (i) exactly, so the chain of estimates is tight against itself (no constant is wasted between (i), (ii), (iii)).

The constant chain, fully traced: $\tfrac12$ (Lemma 2.1) $\to$ $1$ (Lemma 2.2, three Cauchy–Schwarz) $\to$ $2/\sqrt3$ (Proposition 2.3, after the chain-rule factor $4$ and AM–GM $3^{-1/2}$) $\to$ $(2/\sqrt3)^{6}=\tfrac{64}{27}$ meets Young's $\tfrac14\cdot\tfrac{27}{64\nu^3}$ $\to$ $K_0=\tfrac12$ (Proposition 3.1) $\to$ Leray constant $(2K_0)^{-1/4}=1$ (Proposition 4.1) $\to$ window time $\tfrac{\nu^3}{2M^4}$, count $\tfrac{M^2\|u^0\|^2}{\nu^4}$, deadline constant $16$.

## 8. Honesty and novelty

- **Theorem 1:** `[NEW QUANTITATIVE FORM — possibly folklore]`. The three ingredients (energy budget, enstrophy ODE, local growth bound) are classical, and the qualitative moral ("dissipation limits how often the gradient can be large; local theory limits how fast it can grow") is folklore. We are not aware of this excursion-counting statement — finiteness of the set of $M$-threshold windows with the explicit bound $N(M)\le M^2\|u^0\|_{L^2}^2/\nu^4+1$, the explicit ramp-up time $\nu^3/(2M^4)$, and the terminal-window announcement (v) — appearing in the literature in this form; we make no strong originality claim beyond "not located, constants ours". It is **not** in `REPORT.md` (whose §5.3 is the measure/dimension theory of the singular set — a statement about a limit object, empty for regular solutions) and **not** in the Wave-2 BKM note (whose content is the $L^\infty$-vorticity Grönwall estimate and its two corollaries).
- **Propositions 3.1 and 4.1:** `[KNOWN mechanism (Leray 1934); explicit constants $K_0=\tfrac12$, $c=1$ computed here]`. `REPORT.md` §5.2 proves both with unnamed absolute constants; the vorticity-level route through the elementary Sobolev constant $2/\sqrt3$ making every constant explicit (and the Leray constant exactly $1$) is this note's bookkeeping contribution. Not claimed as new mathematics.
- **Corollary 6.1:** `[KNOWN — essentially Leray's eventual-regularity; explicit constant $16$ assembled here]`.
- **§2 toolbox:** `[KNOWN — Gagliardo–Nirenberg 1958/59 mechanism; constants standard folklore; complete proofs included for self-containment]`.
- **First target of the wave brief** ($\int_s^t\|\omega\|_{L^\infty}\ge c\log(\|\omega(t)\|_2/\|\omega(s)\|_2)$): holds with $c=1$ and no auxiliary hypothesis, but it is the logarithm of Wave-2's estimate $(\star)$ and is therefore **not claimed by this note**; the deliverable here is Theorem 1, which Wave-2 does not contain.
- **What this does not say.** Theorem 1 constrains the *time statistics* of large gradients with explicit constants; it neither proves global regularity (the windows are allowed to exist, and inside a window nothing caps $y$) nor constructs blow-up. As $M\to\infty$ the permitted number of windows grows like $M^2$: the estimates never contradict a finite-time singularity — consistent with the supercriticality obstruction (`REPORT.md` §3.10) and the energy-method no-go (`REPORT.md` §5.4, noting that everything used here is energy-abstract in Tao's sense, so by that very no-go it *could not* have proved regularity). **The Millennium problem remains untouched.**
