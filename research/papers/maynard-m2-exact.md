# The Maynard constant $M_2$ equals $\dfrac{1}{1-W(1/e)}$: a complete proof, with the explicit optimizer

**Abstract.** Let $M_2$ be the $k=2$ case of Maynard's variational constant: the supremum of $(J_1(F)+J_2(F))/I(F)$ over nonzero square-integrable $F$ on the simplex $\mathcal R_2=\{t_1,t_2\ge 0,\ t_1+t_2\le 1\}$. We prove that the supremum is attained, that every maximizer has the additive form $F(t_1,t_2)=a(t_1)+a(t_2)$, and that
$$M_2 \;=\; \frac{1}{1-W(1/e)} \;=\; 1.38593327599819425386\ldots,$$
where $W$ is the principal branch of the Lambert function; equivalently, $M_2$ is the unique $x>1$ with $2-\tfrac1x+\log\!\big(1-\tfrac1x\big)=0$. The optimizer is written in closed form (a logarithmic–rational profile $a=m$, unique up to scalars), and the proof is self-contained: existence via a compactness-modulo-multiplication analysis of the essential spectrum, the Euler–Lagrange system, its exact ODE solution, and the eigenvalue classification. As a corollary we obtain the exact "multidimensional gain" at $k=2$ over the radial (one-dimensional) subclass:
$$M_2-M_2^{\mathrm{rad}}\;=\;\frac{1}{1-W(1/e)}-\frac{8}{j_{0,1}^2}\;=\;0.00261272375303483851\ldots\;>\;0.00165,$$
with every inequality certified by explicit rational/series bounds. The numerical value of $M_2$ (and its Lambert form) is recorded on the Polymath8 wiki; the contribution of this note is a complete, referee-checkable proof and the explicit extremizer. No claim about primes is made.

---

## 1. Setup and statement of results

### 1.1 The variational problem

For $k=2$, Maynard's variational problem [1, §3; 2, §6] is posed on the simplex
$$\mathcal R_2 \;=\; \{(t_1,t_2)\in[0,1]^2:\ t_1,t_2\ge 0,\ t_1+t_2\le 1\}.$$
For measurable $F:\mathcal R_2\to\mathbb R$ set
$$I(F)\;=\;\iint_{\mathcal R_2}F(t_1,t_2)^2\,dt_1\,dt_2,$$
$$J_1(F)\;=\;\int_0^1\Big(\int_0^{1-t_2}F(t_1,t_2)\,dt_1\Big)^{\!2}dt_2,
\qquad
J_2(F)\;=\;\int_0^1\Big(\int_0^{1-t_1}F(t_1,t_2)\,dt_2\Big)^{\!2}dt_1,$$
and define
$$M_2\;=\;\sup\Big\{\ \frac{J_1(F)+J_2(F)}{I(F)}\ :\ F\in L^2(\mathcal R_2),\ I(F)>0\ \Big\}. \tag{1.1}$$
(Maynard [1] takes the supremum over piecewise-differentiable $F$; by Remark 2.2 below the two suprema coincide, and our maximizer is real-analytic on $\mathcal R_2$, so it lies in every reasonable competitor class.)

### 1.2 Main results

Throughout, $W$ denotes the principal branch of the Lambert function ($W(z)e^{W(z)}=z$, $W\ge -1$; see [5]), and
$$\psi(\lambda)\;:=\;2-\frac1\lambda+\log\Big(1-\frac1\lambda\Big),\qquad \lambda>1. \tag{1.2}$$

**Theorem A (exact value and optimizer).**
The supremum $(1.1)$ is attained, and
$$M_2\;=\;\lambda^*\;:=\;\frac{1}{1-W(1/e)}\;=\;1.38593327599819425386\ldots,$$
where $\lambda^*$ is also characterized as the unique root of $\psi(\lambda)=0$ in $(1,\infty)$. Moreover:

1. **(Additive form.)** Every maximizer of $(1.1)$ equals, up to a nonzero scalar and a null set, $F^*(t_1,t_2)=m(t_1)+m(t_2)$, where, with $c:=\lambda^*-1=0.38593327599819\ldots$,
$$\boxed{\;m(t)\;=\;1-\frac{c(c+1)}{(2c+1)^2}\,\log\!\frac{(c+t)(c+1)}{c\,(c+1-t)}\;-\;\frac{(c+1)\,t}{(2c+1)(c+t)}\;}\tag{1.3}$$
for $t\in[0,1]$. Equivalently, with $y:=W(1/e)=0.27846454276107379511\ldots$,
$$m(t)\;=\;1-\frac{y}{(1+y)^2}\,\log\!\frac{y+(1-y)t}{y\,\big(1-(1-y)t\big)}\;-\;\frac{(1-y)\,t}{(1+y)\,\big(y+(1-y)t\big)}. \tag{1.4}$$
2. **(Properties of the profile.)** $m$ is real-analytic on $[0,1]$, strictly decreasing, with $m(0)=1$, $m(1)=0$, $m'(0)=-1/c$, $m'(1)=-1/\lambda^*$; consequently $F^*>0$ on all of $\mathcal R_2$.
3. **(Spectral rigidity.)** The associated self-adjoint operator $T$ of Section 3 satisfies $\sigma(T)\cap(1,\infty)=\{\lambda^*\}$, and $\lambda^*$ is a simple eigenvalue. In particular the maximizer is unique up to scalars, and it is symmetric.

**Corollary B (exact multidimensional gain at $k=2$).**
Let $M_2^{\mathrm{rad}}$ be the supremum in $(1.1)$ restricted to radial cutoffs $F(t_1,t_2)=g(t_1+t_2)$. By [4] (see also the one-dimensional analysis in [2]), $M_2^{\mathrm{rad}}=8/j_{0,1}^2$, where $j_{0,1}=2.40482555769577276862\ldots$ is the first positive zero of the Bessel function $J_0$; this instantiates the known one-dimensional value $4k(k-1)/j_{k-2,1}^2$ at $k=2$ and is **not** claimed as new here. Then
$$M_2-M_2^{\mathrm{rad}}
\;=\;\frac{1}{1-W(1/e)}-\frac{8}{j_{0,1}^2}
\;=\;0.00261272375303483851\ldots
\;>\;0.00165\;>\;0,$$
where the strict inequality (with the explicit floor $0.00165$) is proved by certified elementary bounds in Section 7. Thus the optimal $k=2$ Maynard cutoff is genuinely non-radial: dependence on $t_1-t_2$ contributes an exact gain of $0.00261\ldots$, about $0.19\%$ of the radial ceiling.

### 1.3 Provenance and honesty

The numerical value $M_2=1.38593\ldots$ and the closed form $1/(1-W(1/e))$ are recorded on the Polymath8 wiki [3]; we make **no claim of priority for the value or for its Lambert form**. The one-dimensional/radial value $8/j_{0,1}^2$ is likewise known ([2]; a complete proof is in the companion note [4]) and is quoted, not re-proved. What we have not located in the published literature — neither in Maynard's paper [1], which introduces the problem and treats $k\ge 5$ numerically, nor in the Polymath8b paper [2], which develops general upper and lower bounds for $M_k$ (including the $2\log 2$ ceiling at $k=2$ and the one-dimensional Bessel analysis) — is a complete proof of the exact evaluation of $M_2$: existence of a maximizer (nontrivial, since the underlying operator is **not** compact), the classification of all Euler–Lagrange solutions, and the closed-form extremizer. Solving the Euler–Lagrange equation itself is the kind of computation an expert could reproduce, and sketches circulated in the Polymath8b discussions; this note should therefore be read as a **complete published-quality write-up of a possibly-folklore result**, with the existence and rigidity steps supplied. If a full proof surfaces in the literature, Theorem A should be relabeled a rediscovery; the corollary's certified gap and the explicit formulas (1.3)–(1.4) we have not seen stated anywhere.

### 1.4 Plan of the proof

Section 2 fixes notation and proves the elementary two-sided bound $\tfrac43\le M_2\le 2\log 2$. Section 3 recasts $(1.1)$ as the norm of a bounded self-adjoint operator $T=S_1^*S_1+S_2^*S_2$ and proves $\sigma_{\mathrm{ess}}(T)\subseteq[0,1]$ — the key existence input, obtained from the operator inequality $T^2\le T+(\text{compact})$. Since $M_2\ge\tfrac43>1$, the top of the spectrum is an isolated eigenvalue: **a maximizer exists**. Section 4 derives the Euler–Lagrange system: any eigenfunction with eigenvalue $\lambda>1$ has the form $\lambda F=f(t_1)+g(t_2)$, and $u=f+g$, $w=f-g$ satisfy decoupled one-dimensional integral equations. Section 5 solves both: the equation forces the second-order ODE $(c+t)(c+1-t)v''+(c+2-3t)v'=0$, whose solutions are explicit; the antisymmetric part $w$ must vanish, and the symmetric part exists **iff** $\psi(\lambda)=0$. Section 6 analyzes $\psi$, produces the Lambert form, and assembles Theorem A. Section 7 proves Corollary B with certified constants. Appendix A reports independent numerical verification.

---

## 2. Preliminaries and the elementary ceiling $2\log 2$

We work in the real Hilbert space $H=L^2(\mathcal R_2)$ with Lebesgue measure, norm $\|F\|^2=I(F)$. All functions are real-valued.

**Lemma 2.1 (elementary bounds).** $\dfrac43\;\le\;M_2\;\le\;2\log 2\;=\;1.38629436111989\ldots$

*Proof.* **Lower bound.** Take $F\equiv 1$: $I(F)=\operatorname{area}(\mathcal R_2)=\tfrac12$, and $J_1(F)=\int_0^1(1-t_2)^2dt_2=\tfrac13=J_2(F)$, so the ratio is $\tfrac{2/3}{1/2}=\tfrac43$.

**Upper bound.** Fix $t_2\in[0,1)$ and put $u=1-t_2$. By the Cauchy–Schwarz inequality with the weight $u+t_1$,
$$\Big(\int_0^{u}F(t_1,t_2)\,dt_1\Big)^2
\;\le\;\Big(\int_0^{u}\frac{dt_1}{u+t_1}\Big)\Big(\int_0^{u}(u+t_1)\,F(t_1,t_2)^2\,dt_1\Big)
\;=\;(\log 2)\int_0^{u}(u+t_1)F^2\,dt_1,$$
because $\int_0^u\frac{dt_1}{u+t_1}=\log\frac{2u}{u}=\log 2$ for every $u>0$. Integrating in $t_2$,
$$J_1(F)\;\le\;(\log 2)\iint_{\mathcal R_2}(1-t_2+t_1)\,F^2,\qquad
J_2(F)\;\le\;(\log 2)\iint_{\mathcal R_2}(1-t_1+t_2)\,F^2 ,$$
and adding, since $(1-t_2+t_1)+(1-t_1+t_2)=2$,
$$J_1(F)+J_2(F)\;\le\;2\log 2\; I(F). \qquad\blacksquare$$

This is the $k=2$ case of the known bound $M_k\le\frac{k}{k-1}\log k$ [2]; Theorem A will show that the truth undercuts this ceiling by only $2\log 2-\lambda^*=3.6109\ldots\times10^{-4}$.

**Remark 2.2 (competitor class).** The Rayleigh quotient $F\mapsto(J_1+J_2)(F)/I(F)$ is continuous on $H\setminus\{0\}$ (each $J_i$ is a bounded quadratic form by Lemma 3.1 below), and smooth functions are dense in $H$; hence the supremum over $L^2$, over continuous, or over piecewise-differentiable $F$ is the same number $M_2$.

---

## 3. Operator formulation and existence of a maximizer

### 3.1 The operator

Define the bounded operators $S_1,S_2:H\to L^2(0,1)$,
$$ (S_1F)(t_2)=\int_0^{1-t_2}F(t_1,t_2)\,dt_1,\qquad
   (S_2F)(t_1)=\int_0^{1-t_1}F(t_1,t_2)\,dt_2, $$
so that $J_1(F)=\|S_1F\|_{L^2(0,1)}^2$ and $J_2(F)=\|S_2F\|_{L^2(0,1)}^2$.

**Lemma 3.1.** $\|S_iF\|^2\le I(F)$ for $i=1,2$; the adjoints are $(S_1^*h)(t_1,t_2)=h(t_2)$ and $(S_2^*h)(t_1,t_2)=h(t_1)$ (restricted to $\mathcal R_2$). Consequently
$$T\;:=\;S_1^*S_1+S_2^*S_2,\qquad (TF)(t_1,t_2)\;=\;(S_2F)(t_1)+(S_1F)(t_2),$$
is a bounded self-adjoint operator on $H$ with $0\le T$ and
$$M_2\;=\;\sup_{\|F\|=1}\langle TF,F\rangle\;=\;\|T\|\;=\;\max\sigma(T). \tag{3.1}$$

*Proof.* By Cauchy–Schwarz, $(S_1F)(t_2)^2\le(1-t_2)\int_0^{1-t_2}F^2\,dt_1\le\int_0^{1-t_2}F^2\,dt_1$; integrating gives $\|S_1F\|^2\le I(F)$, and symmetrically for $S_2$. The adjoint formula follows from Fubini: $\langle S_1F,h\rangle=\iint_{\mathcal R_2}F(t_1,t_2)h(t_2)\,dt_1dt_2$. Then $\langle TF,F\rangle=J_1(F)+J_2(F)\ge 0$, so $(3.1)$ is the standard variational characterization of the norm of a nonnegative bounded self-adjoint operator. $\blacksquare$

Write $A:=S_1^*S_1$ and $B:=S_2^*S_2$; by Lemma 3.1, $0\le A\le \mathbf 1$ and $0\le B\le\mathbf 1$ (as quadratic forms), i.e. $\|A\|,\|B\|\le 1$.

Note that $T$ is **not** compact: $S_1S_1^*$ is multiplication by $(1-t)$ on $L^2(0,1)$, so $A=S_1^*S_1$ has essential spectrum filling $[0,1]$. Existence of a maximizer therefore needs an argument; direct maximizing-sequence methods lose compactness exactly along functions concentrating on one axis of the simplex. The saving grace is that the *interaction* of the two directions is compact:

**Lemma 3.2 (compact interaction).** $S_1S_2^*:L^2(0,1)\to L^2(0,1)$ is the integral operator with kernel $\mathbf 1_{\{t_1+t_2\le1\}}$, i.e. $(S_1S_2^*h)(t_2)=\int_0^{1-t_2}h(t_1)\,dt_1$. It is Hilbert–Schmidt, hence compact; consequently $K:=AB+BA$ is a compact self-adjoint operator on $H$.

*Proof.* $(S_2^*h)(t_1,t_2)=h(t_1)$, so $(S_1S_2^*h)(t_2)=\int_0^{1-t_2}h(t_1)dt_1$, an integral operator whose kernel $\mathbf 1_{\{t_1+t_2\le 1\}}$ is square-integrable on $[0,1]^2$: Hilbert–Schmidt. Then $AB=S_1^*(S_1S_2^*)S_2$ is compact (bounded $\circ$ compact $\circ$ bounded), and $BA=(AB)^*$ likewise; $K=AB+BA$ is self-adjoint. $\blacksquare$

### 3.2 The essential spectrum and existence

**Proposition 3.3.** $\sigma_{\mathrm{ess}}(T)\subseteq[0,1]$.

*Proof.* Since $0\le A\le\mathbf 1$, the operator $A-A^2=A^{1/2}(\mathbf 1-A)A^{1/2}$ is nonnegative, and likewise $B-B^2\ge0$. Hence
$$T^2\;=\;A^2+B^2+AB+BA\;=\;T-(A-A^2)-(B-B^2)+K\;\le\;T+K, \tag{3.2}$$
with $K$ compact self-adjoint (Lemma 3.2). Let $\lambda\in\sigma_{\mathrm{ess}}(T)$; note $\lambda\ge0$ since $T\ge0$. By Weyl's criterion [6, Thm. VII.12 and its essential-spectrum refinement; or 7, Thm. 7.2] there is an orthonormal sequence $(F_n)$ with $\|(T-\lambda)F_n\|\to0$. Orthonormality gives $F_n\rightharpoonup0$, so $KF_n\to0$ in norm and $\langle KF_n,F_n\rangle\to0$. Also
$$\langle TF_n,F_n\rangle=\lambda+\langle(T-\lambda)F_n,F_n\rangle\to\lambda,
\qquad
\langle T^2F_n,F_n\rangle=\|TF_n\|^2=\|\lambda F_n+(T-\lambda)F_n\|^2\to\lambda^2 .$$
Testing $(3.2)$ against $F_n$ and passing to the limit: $\lambda^2\le\lambda$, i.e. $\lambda\in[0,1]$. $\blacksquare$

**Corollary 3.4 (existence and Euler–Lagrange).** $M_2$ is an isolated eigenvalue of $T$ of finite multiplicity. A function $F\in H$ with $\|F\|=1$ attains the supremum $(1.1)$ **iff** $TF=M_2F$; in particular maximizers exist.

*Proof.* By Lemma 2.1 and $(3.1)$, $\max\sigma(T)=M_2\ge\tfrac43>1\ge\sup\sigma_{\mathrm{ess}}(T)$. By the spectral theorem, the part of $\sigma(T)$ above the essential spectrum consists of isolated eigenvalues of finite multiplicity; the maximum of the spectrum is one of them, and any of its unit eigenvectors attains $(1.1)$. Conversely, if $\langle TF,F\rangle=M_2$ with $\|F\|=1$ then $\langle(M_2-T)F,F\rangle=0$ with $M_2-T\ge0$, so $\|(M_2-T)^{1/2}F\|=0$, whence $TF=M_2F$. $\blacksquare$

This settles global optimality structurally: no second-variation analysis is needed, because *every* maximizer is characterized as a top eigenfunction, and Sections 4–5 will show the eigenvalue problem above $1$ has exactly one solution.

---

## 4. The Euler–Lagrange system and the additive form

Fix $\lambda>1$ and write $c:=\lambda-1>0$.

**Proposition 4.1 (structure of eigenfunctions).** Suppose $F\in H$, $F\ne0$, $TF=\lambda F$. Define $f:=S_2F$, $g:=S_1F\in L^2(0,1)$. Then:

1. $\lambda F(t_1,t_2)=f(t_1)+g(t_2)$ for a.e. $(t_1,t_2)\in\mathcal R_2$;
2. $f$ and $g$ (after modification on null sets) belong to $C^\infty([0,1])$ and satisfy the coupled system
$$(c+t)\,f(t)=G(1-t),\qquad (c+t)\,g(t)=\mathcal F(1-t)\qquad(0\le t\le1), \tag{4.1}$$
where $\mathcal F(x)=\int_0^x f(s)\,ds$ and $G(x)=\int_0^x g(s)\,ds$;
3. $u:=f+g$ and $w:=f-g$ satisfy the decoupled equations
$$(c+t)\,u(t)=+U(1-t),\qquad (c+t)\,w(t)=-\mathcal W(1-t), \tag{4.2}$$
with $U(x)=\int_0^x u$, $\mathcal W(x)=\int_0^x w$.

*Proof.* (1) is the eigenvalue equation $TF=\lambda F$ read pointwise. For (2), substitute (1) into the definition of $f$ and use Fubini: for a.e. $t_1$,
$$f(t_1)=(S_2F)(t_1)=\frac1\lambda\int_0^{1-t_1}\big(f(t_1)+g(t_2)\big)dt_2
=\frac{(1-t_1)f(t_1)+G(1-t_1)}{\lambda},$$
i.e. $(\lambda-1+t_1)f(t_1)=G(1-t_1)$, which is the first equation of $(4.1)$; the second is symmetric. Since $f,g\in L^2(0,1)\subset L^1(0,1)$, the primitives $\mathcal F,G$ are continuous; as $c+t\ge c>0$, the identities $(4.1)$ show $f,g$ agree a.e. with continuous functions, and then, bootstrapping ($\mathcal F,G\in C^1\Rightarrow f,g\in C^1\Rightarrow\mathcal F,G\in C^2\Rightarrow\cdots$), $f,g\in C^\infty([0,1])$ and $(4.1)$ holds everywhere. (3) follows by adding and subtracting the two equations in $(4.1)$: $G+\mathcal F=\int(f+g)=U$ and $G-\mathcal F=-\mathcal W$. $\blacksquare$

The two equations $(4.2)$ are the $\sigma=+1$ and $\sigma=-1$ cases of the one-parameter family analyzed next. This is the promised **reduction to one dimension**.

---

## 5. The one-dimensional problem solved exactly

Fix $c>0$ and $\sigma\in\{+1,-1\}$, and consider, for $v\in L^2(0,1)$, $V(x):=\int_0^x v(s)\,ds$, the integral equation
$$(c+t)\,v(t)\;=\;\sigma\,V(1-t)\qquad(0\le t\le 1). \tag{5.1}$$

**Lemma 5.1 (forced ODE).** Any solution of $(5.1)$ is (a.e. equal to) a $C^\infty$ function satisfying
$$(c+t)(c+1-t)\,v''(t)+(c+2-3t)\,v'(t)=0\qquad(0\le t\le1). \tag{5.2}$$
The solution space of $(5.2)$ on $[0,1]$ is $\{\alpha+\beta\varphi:\alpha,\beta\in\mathbb R\}$, where
$$\varphi(t):=\int_0^t\frac{ds}{(c+s)^2(c+1-s)}
=\frac{1}{(2c+1)^2}\log\frac{c+t}{c}
+\frac{t}{(2c+1)\,c\,(c+t)}
+\frac{1}{(2c+1)^2}\log\frac{c+1}{c+1-t}. \tag{5.3}$$

*Proof.* Smoothness follows by the same bootstrap as in Proposition 4.1 (the right side of $(5.1)$ is continuous, and $c+t\ge c>0$). Differentiate $(5.1)$:
$$(c+t)v'(t)+v(t)=-\sigma\,v(1-t). \tag{5.4}$$
Replace $t\mapsto1-t$ in $(5.1)$: $(c+1-t)v(1-t)=\sigma V(t)$, i.e. $v(1-t)=\sigma V(t)/(c+1-t)$. Substituting into $(5.4)$ and using $\sigma^2=1$:
$$(c+1-t)\big[(c+t)v'(t)+v(t)\big]=-V(t).$$
Differentiating once more,
$$-\big[(c+t)v'+v\big]+(c+1-t)\big[(c+t)v''+2v'\big]=-v,$$
which simplifies to $(c+t)(c+1-t)v''+\big[2(c+1-t)-(c+t)\big]v'=0$, i.e. $(5.2)$, since $2(c+1-t)-(c+t)=c+2-3t$. Note the reflection has been eliminated: $(5.2)$ is a genuine ODE, the same for both $\sigma$.

For the solution space: on $[0,1]$ the leading coefficient $(c+t)(c+1-t)\ge c\min(c,1)>0$, so $(5.2)$ is a regular linear ODE with two-dimensional solution space. Since $\frac{c+2-3t}{(c+t)(c+1-t)}=\frac{2}{c+t}-\frac{1}{c+1-t}$ (check by clearing denominators), an integrating factor is $(c+t)^2(c+1-t)$, giving $v'(t)=\beta\big/\big[(c+t)^2(c+1-t)\big]$ and $v=\alpha+\beta\varphi$. The closed form $(5.3)$ follows from the partial fractions
$$\frac{1}{(c+s)^2(c+1-s)}
=\frac{1}{(2c+1)^2}\cdot\frac{1}{c+s}
+\frac{1}{2c+1}\cdot\frac{1}{(c+s)^2}
+\frac{1}{(2c+1)^2}\cdot\frac{1}{c+1-s},$$
verified by multiplying out and comparing values at $s=-c$, $s=c+1$, and the coefficient of $s^2$. $\blacksquare$

**Lemma 5.2 (defect function).** Let $v=\alpha+\beta\varphi$ solve $(5.2)$ and set $D_\sigma(t):=(c+t)v(t)-\sigma V(1-t)$. Then
$$D_\sigma''(t)\;=\;(1-\sigma)\,\frac{\beta}{(c+t)(c+1-t)^2}\qquad(0\le t\le1). \tag{5.5}$$

*Proof.* $D_\sigma'(t)=v(t)+(c+t)v'(t)+\sigma v(1-t)$ and $D_\sigma''(t)=2v'(t)+(c+t)v''(t)-\sigma v'(1-t)$. By $(5.2)$,
$$2v'+(c+t)v''=v'\cdot\frac{2(c+1-t)-(c+2-3t)}{c+1-t}=v'(t)\,\frac{c+t}{c+1-t},$$
and since $v'(t)=\beta/\big[(c+t)^2(c+1-t)\big]$,
$$v'(t)\,\frac{c+t}{c+1-t}=\frac{\beta}{(c+t)(c+1-t)^2},
\qquad
v'(1-t)=\frac{\beta}{(c+1-t)^2(c+t)} .$$
Subtracting $\sigma$ times the second from the first gives $(5.5)$. $\blacksquare$

Equation $(5.1)$ says precisely $D_\sigma\equiv0$. The two signs now behave completely differently.

**Proposition 5.3 (antisymmetric part vanishes).** For $\sigma=-1$ the only solution of $(5.1)$ is $v\equiv0$. Consequently, in Proposition 4.1 one has $w=f-g\equiv0$: **every eigenfunction of $T$ with eigenvalue $\lambda>1$ is symmetric and of the additive form**
$$F(t_1,t_2)\;=\;a(t_1)+a(t_2),\qquad a:=f/\lambda=g/\lambda .$$

*Proof.* If $v$ solves $(5.1)$ with $\sigma=-1$, then $v=\alpha+\beta\varphi$ (Lemma 5.1) and $D_{-1}\equiv0$, so $D_{-1}''\equiv0$; by $(5.5)$ with $1-\sigma=2$, $\beta=0$. Then $v\equiv\alpha$ and $(5.1)$ reads $(c+t)\alpha=-\alpha(1-t)$ for all $t$, i.e. $\alpha(c+1)=0$, so $\alpha=0$. The consequence is immediate from Proposition 4.1(3), and $a=f/\lambda$ gives $F=(f(t_1)+g(t_2))/\lambda=a(t_1)+a(t_2)$. $\blacksquare$

**Proposition 5.4 (symmetric part: the eigenvalue condition).** For $\sigma=+1$, equation $(5.1)$ has a nonzero solution **iff**
$$\varphi(1)=\frac{1}{c(c+1)}
\qquad\Longleftrightarrow\qquad
\log\frac{c+1}{c}=\frac{2c+1}{c+1}
\qquad\Longleftrightarrow\qquad
\psi(c+1)=0, \tag{5.6}$$
with $\psi$ as in $(1.2)$. In that case the solutions form the one-dimensional space $\mathbb R\,m$, where $m:=1-c(c+1)\varphi$ is given explicitly by $(1.3)$ and satisfies
$$m(0)=1,\quad m(1)=0,\quad m'(t)=\frac{-c(c+1)}{(c+t)^2(c+1-t)}<0,\quad m'(0)=-\frac1c,\quad m'(1)=-\frac1{c+1},$$
so $m$ is real-analytic, strictly decreasing from $1$ to $0$, and positive on $[0,1)$.

*Proof.* By Lemma 5.1 any solution is $v=\alpha+\beta\varphi$, and by Lemma 5.2 with $\sigma=+1$, $D:=D_{+1}$ satisfies $D''\equiv0$ for **every** such $v$; hence $D(t)=D(0)+D'(0)\,t$ is affine, and
$$(5.1)\iff D\equiv 0\iff D(1)=0 \text{ and } D'(0)=0 .$$
Compute, using $V(0)=0$, $\varphi(0)=0$, $\varphi'(0)=1/\big(c^2(c+1)\big)$:
$$D(1)=(c+1)\,v(1)=(c+1)\big(\alpha+\beta\varphi(1)\big),$$
$$D'(0)=v(0)+c\,v'(0)+v(1)
=2\alpha+\beta\Big(\frac{1}{c(c+1)}+\varphi(1)\Big).$$
$D(1)=0$ forces $\alpha=-\beta\varphi(1)$; substituting, $D'(0)=\beta\big(\tfrac1{c(c+1)}-\varphi(1)\big)$. A nonzero solution ($\beta\ne0$; if $\beta=0$ then $\alpha=0$) exists iff $\varphi(1)=\tfrac1{c(c+1)}$, and then the solution space is spanned by the choice $\beta=-c(c+1)$, $\alpha=c(c+1)\varphi(1)=1$, i.e. by $m=1-c(c+1)\varphi$, which is $(1.3)$ upon inserting $(5.3)$.

*Simplification of the condition.* By $(5.3)$, $\varphi(1)=\dfrac{2}{(2c+1)^2}\log\dfrac{c+1}{c}+\dfrac{1}{(2c+1)\,c(c+1)}$, so
$$\varphi(1)=\frac1{c(c+1)}
\iff
\frac{2}{(2c+1)^2}\log\frac{c+1}{c}=\frac{1}{c(c+1)}\cdot\frac{2c}{2c+1}
\iff
\log\frac{c+1}{c}=\frac{2c+1}{c+1}.$$
Writing $\lambda=c+1$: $\log\frac{\lambda}{\lambda-1}=2-\frac1\lambda$, i.e. $2-\frac1\lambda+\log\big(1-\frac1\lambda\big)=0$, which is $\psi(\lambda)=0$.

*Properties of $m$.* $m'=-c(c+1)\varphi'<0$ strictly; $m(0)=1$; $m(1)=1-c(c+1)\varphi(1)=0$ by $(5.6)$; the endpoint slopes follow from $\varphi'(0)=1/(c^2(c+1))$ and $\varphi'(1)=1/((c+1)^2c)$. Positivity on $[0,1)$ follows from strict decrease and $m(1)=0$. Real-analyticity is clear from $(1.3)$ (denominators nonvanishing on $[0,1]$ since $c>0$). $\blacksquare$

**Proposition 5.5 (converse: the eigenfunction exists).** Suppose $\psi(\lambda)=0$, $\lambda>1$, $c=\lambda-1$, and let $m$ be as above. Then $F^*(t_1,t_2):=m(t_1)+m(t_2)$ satisfies $TF^*=\lambda F^*$, and hence $\dfrac{J_1(F^*)+J_2(F^*)}{I(F^*)}=\lambda$.

*Proof.* Write $\mathfrak M(x)=\int_0^x m$. By construction $m$ solves $(5.1)$ with $\sigma=+1$: $(c+t)m(t)=\mathfrak M(1-t)$. Then
$$(S_2F^*)(t_1)=\int_0^{1-t_1}\big(m(t_1)+m(t_2)\big)dt_2=(1-t_1)\,m(t_1)+\mathfrak M(1-t_1)
=(1-t_1)\,m(t_1)+(c+t_1)\,m(t_1)=\lambda\,m(t_1),$$
since $(1-t_1)+(c+t_1)=c+1=\lambda$; symmetrically $(S_1F^*)(t_2)=\lambda m(t_2)$. Hence
$$(TF^*)(t_1,t_2)=(S_2F^*)(t_1)+(S_1F^*)(t_2)=\lambda\big(m(t_1)+m(t_2)\big)=\lambda F^*,$$
and the Rayleigh quotient of an eigenfunction equals its eigenvalue. $\blacksquare$

---

## 6. The transcendental equation, Lambert's function, and the proof of Theorem A

**Lemma 6.1.** $\psi(\lambda)=2-\frac1\lambda+\log(1-\frac1\lambda)$ is continuous and strictly increasing on $(1,\infty)$, with $\psi(1^+)=-\infty$ and $\psi(\lambda)\to2$ as $\lambda\to\infty$. Hence $\psi$ has a unique zero $\lambda^*\in(1,\infty)$, and
$$\lambda^*=\frac{1}{1-W(1/e)}=1.38593327599819425386\ldots$$

*Proof.* $\psi'(\lambda)=\dfrac{1}{\lambda^2}+\dfrac{1}{\lambda(\lambda-1)}>0$, and the limits are clear, so a unique zero exists. Substitute $y:=1-\tfrac1\lambda$, a strictly increasing bijection $(1,\infty)\to(0,1)$ with $\lambda=\tfrac1{1-y}$:
$$\psi(\lambda)=0
\iff 2-(1-y)+\log y=0
\iff 1+y+\log y=0
\iff y\,e^{y}=e^{-1}. \tag{6.1}$$
Since $x\mapsto xe^x$ is strictly increasing on $(0,\infty)$, $(6.1)$ has the unique positive solution $y=W(1/e)$ (principal branch [5]); numerically $y=0.27846454276107379511\ldots$, giving the stated $\lambda^*=1/(1-y)$. The displayed digits are obtained by Newton's method on $(6.1)$ in 40-digit arithmetic (Appendix A). $\blacksquare$

**Proof of Theorem A.** By Corollary 3.4 a maximizer $F_0$ exists and satisfies $TF_0=M_2F_0$ with $M_2\ge\tfrac43>1$. By Proposition 4.1 (applied with $\lambda=M_2$), $M_2\,F_0=f(t_1)+g(t_2)$ with $(f,g)$ smooth solving $(4.1)$; by Proposition 5.3, $f=g$ (so $F_0$ is symmetric and additive: item 1's form, with $a=f/M_2$), and $u=2f$ is a **nonzero** solution of $(5.1)$ with $\sigma=+1$ ($u=0$ would force $F_0=0$). By Proposition 5.4 this is possible only if $\psi(M_2)=0$; by Lemma 6.1, $M_2=\lambda^*=1/(1-W(1/e))$.

Conversely, at $\lambda=\lambda^*$ Proposition 5.5 exhibits the eigenfunction $F^*=m(t_1)+m(t_2)$; by Proposition 5.4 the solution space of the $\sigma=+1$ equation is one-dimensional and the $\sigma=-1$ equation has only the trivial solution, so the eigenspace of $T$ at $\lambda^*$ is exactly $\mathbb R F^*$ — and, by the same classification applied at an arbitrary $\lambda>1$, $\sigma(T)\cap(1,\infty)=\{\lambda^*\}$ with $\lambda^*$ simple (item 3). Every maximizer is a unit eigenvector at $M_2=\lambda^*$ (Corollary 3.4), hence a scalar multiple of $F^*$: items 1 and 2 follow from Proposition 5.4, and formula $(1.4)$ follows from $(1.3)$ by the substitutions $c=\tfrac{y}{1-y}$, $c+1=\tfrac1{1-y}$, $2c+1=\tfrac{1+y}{1-y}$, $c+t=\tfrac{y+(1-y)t}{1-y}$, $c+1-t=\tfrac{1-(1-y)t}{1-y}$, under which $\tfrac{c(c+1)}{(2c+1)^2}=\tfrac{y}{(1+y)^2}$. $\blacksquare$

**Remark 6.2 (global optimality and the $2\log2$ ceiling).** Global optimality required no second-variation argument: it is built into the spectral identity $M_2=\max\sigma(T)$ together with the rigidity $\sigma(T)\cap(1,\infty)=\{\lambda^*\}$. As a consistency check against Lemma 2.1:
$$\lambda^*=1.3859332760\ldots\;<\;1.3862944\ldots=2\log2,$$
the Cauchy–Schwarz ceiling exceeding the true value by only $2\log2-\lambda^*=3.61085\times10^{-4}$ — the $k=2$ Maynard problem saturates $99.974\%$ of its elementary upper bound.

**Remark 6.3 (shape of the optimizer).** The extremal profile is neither rational ($a=c_0/(1-\alpha t)$) nor exponential: it is the specific logarithmic–rational combination $(1.3)$. Near the "empty" corner it starts at $m(0)=1$ with slope $-1/c\approx-2.5911$ and hits zero at $t=1$ with slope $-1/\lambda^*\approx-0.72154$; monotone positivity confirms it is an admissible sieve-type cutoff.

---

## 7. The gap over the radial class: proof of Corollary B

Recall from [4, Thm. 1] (see also the one-dimensional analysis in [2]) that the radial restriction $F(t_1,t_2)=g(t_1+t_2)$ of $(1.1)$ has exact value
$$M_2^{\mathrm{rad}}=\frac{8}{j_{0,1}^2}=1.38332055224515941535\ldots,$$
attained at the Bessel profile $g^*(s)=\tfrac{j_{0,1}}{2\sqrt s}J_1(j_{0,1}\sqrt s)$; this is the $k=2$ instance of the known one-dimensional value $4k(k-1)/j_{k-2,1}^2$ and is used here as a black box. Corollary B asserts
$$M_2-M_2^{\mathrm{rad}}=\frac{1}{1-W(1/e)}-\frac{8}{j_{0,1}^2}>0 ,$$
with the certified floor $0.00165$. Since Theorem A gives $M_2=\lambda^*$, it suffices to prove the two lemmas below (their constants were chosen to make every step verifiable in exact integer arithmetic plus one truncated Taylor series).

**Lemma 7.1.** $\lambda^*>1.385$.

*Proof.* Since $\psi$ is strictly increasing (Lemma 6.1) and $\psi(\lambda^*)=0$, it suffices to show $\psi(1.385)<0$.

*(i)* $722021\times1385=999\,999\,085<10^9$, so $0.722021\times1.385<1$, i.e. $\dfrac1{1.385}>0.722021$ and $1-\dfrac1{1.385}<0.277979$.

*(ii)* $e^{0.2801}<1.3232622$: the partial sum of $\sum_{k\ge0}\tfrac{0.2801^k}{k!}$ through $k=6$ is $<1.32326211$ (exact rational arithmetic), and for $k\ge7$ the term ratio is $\le\tfrac{0.2801}{8}$, so the tail is at most $\tfrac{0.2801^7}{7!}\cdot\big(1-\tfrac{0.2801}{8}\big)^{-1}<2.8\times10^{-8}$.

*(iii)* With $e<2.7182819$: $e^{1.2801}<2.7182819\times1.3232622<3.5971$ (exact multiplication: $2.7182819\times1.3232622=3.59699968\ldots$).

*(iv)* $277979\times35973=9\,999\,738\,567<10^{10}$, so $0.277979\times3.5973<1$, i.e. $\dfrac1{0.277979}>3.5973>3.5971>e^{1.2801}$. By monotonicity of $\log$, $\ \log(0.277979)<-1.2801$.

*(v)* Combining (i), (iv) and monotonicity of $\log$:
$$\psi(1.385)=2-\frac1{1.385}+\log\Big(1-\frac1{1.385}\Big)
<2-0.722021+\log(0.277979)
<2-0.722021-1.2801=-0.002121<0. \qquad\blacksquare$$

**Lemma 7.2.** $j_{0,1}>2.4048$, and hence $M_2^{\mathrm{rad}}=\dfrac{8}{j_{0,1}^2}<\dfrac{8}{2.4048^2}<1.38335$.

*Proof.* $J_0$ is strictly decreasing on $[0,2.405]$: $J_0'=-J_1$, and $J_1>0$ on $(0,2.405]$ because its alternating series has terms $t_m=\tfrac{(x/2)^{2m+1}}{m!\,(m+1)!}$ with ratio $t_{m+1}/t_m=\tfrac{(x/2)^2}{(m+1)(m+2)}<1$ for $x\le2.8$, so $J_1(x)\ge t_0-t_1=\tfrac x2\big(1-\tfrac{x^2}8\big)>0$ for $0<x\le2.405$ (as in [4, (4.4)]).

Positivity at $2.4048$: with $q=\tfrac{2.4048^2}{4}=1.44576576$ exactly ($2.4048=\tfrac{1503}{625}$), the terms $t_m=\tfrac{q^m}{(m!)^2}$ of $J_0(2.4048)=\sum_{m\ge0}(-1)^mt_m$ decrease for $m\ge1$ (ratio $q/(m+1)^2<1$), so consecutive partial sums bracket the value; in exact rational arithmetic,
$$1.3256\times10^{-5}<S_7\le J_0(2.4048)\le S_8<1.3269\times10^{-5},$$
so $J_0(2.4048)>0$. Since $J_0$ is strictly decreasing on $[0,2.405]$ with $J_0(0)=1$ and $J_0(2.4048)>0$, its first zero satisfies $j_{0,1}>2.4048$. (The same brackets at $x=2.4049$ give $J_0(2.4049)<-3.86\times10^{-5}<0$, so in fact $2.4048<j_{0,1}<2.4049$; only the lower bound is needed.)

Finally $2.4048^2=\tfrac{2259009}{390625}$, and $\tfrac{8}{2.4048^2}<1.38335$ is the exact integer inequality
$$8\times390625\times10^5=312\,500\,000\,000\;<\;138335\times2259009=312\,500\,010\,015. \qquad\blacksquare$$

**Proof of Corollary B.** By Theorem A, Lemma 7.1, and Lemma 7.2,
$$M_2-M_2^{\mathrm{rad}}=\lambda^*-\frac{8}{j_{0,1}^2}>1.385-1.38335=0.00165>0 .$$
With the high-precision values $\lambda^*=1.38593327599819425386\ldots$ and $8/j_{0,1}^2=1.38332055224515941535\ldots$ (using $j_{0,1}=2.40482555769577276862\ldots$ [8, §10.21]), the gap is
$$M_2-M_2^{\mathrm{rad}}=0.00261272375303483851\ldots \qquad\blacksquare$$

**Remark 7.3 (interpretation).** The gap is the exact "multidimensional gain" at $k=2$: the optimal cutoff $(1.3)$ genuinely exploits the difference variable $t_1-t_2$, but only to the tune of $0.19\%$ of the radial value. This makes unconditional the observation of [4, Rem. §6] (there contingent on a floating-point computation) that the extremizer of the full $M_2$ is strictly non-radial. Both optima, radial and full, fall well short of the twin-prime detection threshold $M_2>2$ at every level of distribution $\theta\le1$; consistently with Lemma 2.1, **no arithmetic consequence is claimed in this note**.

---

## Appendix A. Independent numerical verification

All checks were run in 40-digit arithmetic (mpmath 1.4.1) and, for the discretizations, in IEEE double precision (numpy 2.4.4); none is used in the proofs.

1. **Closed form.** Newton's method on $\psi(\lambda)=0$ gives $\lambda^*=1.385933275998194253860622\ldots$, agreeing with $1/(1-W(1/e))$ to all $40$ digits; $1+y+\log y=0$ at $y=W(1/e)$ to $40$ digits.
2. **Integral equation.** With $c=\lambda^*-1$ and $m$ from $(1.3)$: $\max_{t\in[0,1]}\big|(c+t)m(t)-\int_0^{1-t}m\big|<10^{-40}$ on a $21$-point grid (adaptive quadrature); the forms $(1.3)$ and $(1.4)$ agree to $10^{-40}$; $m(0)=1$, $m(1)=0$, $m'(0)=-1/c$ exactly to precision.
3. **Rayleigh quotient.** Two-dimensional adaptive quadrature of $J_1+J_2$ and $I$ at $F^*=m(t_1)+m(t_2)$ gives $(J_1+J_2)/I=1.3859332759981942539$, matching $\lambda^*$ to $2\times10^{-20}$.
4. **Global search.** Power iteration on the discretized operator $T$ (piecewise-constant elements on the simplex, $n\times n$ grids) yields discrete maxima $1.3789900235$ ($n=100$), $1.3836218826$ ($n=300$), $1.3847779558$ ($n=600$), increasing toward $\lambda^*$ from below — consistent with attainment at $\lambda^*$ and with no larger supremum.
5. **Gap.** $j_{0,1}=2.404825557695772768621632\ldots$, $8/j_{0,1}^2=1.383320552245159415350935\ldots$, $\lambda^*-8/j_{0,1}^2=0.002612723753034838509687\ldots$, $2\log2-\lambda^*=3.61085121697\times10^{-4}$.
6. **Certified constants of §7.** $722021\times1385=999\,999\,085$; $277979\times35973=9\,999\,738\,567$; $138335\times2259009=312\,500\,010\,015$; $e^{0.2801}=1.32326213193\ldots$; $2.7182819\times1.3232622=3.596999687\ldots$; $J_0(2.4048)=1.3268\times10^{-5}$, $J_0(2.4049)=-3.8646\times10^{-5}$; all as asserted.

---

## References

[1] J. Maynard, *Small gaps between primes*, Ann. of Math. (2) **181** (2015), no. 1, 383–413.

[2] D. H. J. Polymath, *Variants of the Selberg sieve, and bounded intervals containing many primes*, Res. Math. Sci. **1** (2014), Art. 12.

[3] Polymath8 wiki, *Selberg sieve variational problem*, https://asone.ai/polymath/index.php?title=Selberg_sieve_variational_problem (mirror of michaelnielsen.org/polymath1). Records $M_2=1.38593\ldots$ and the form $1/(1-W(1/e))$; no complete proof is given there.

[4] *The radial Maynard functional is a drum: $M_2^{\mathrm{rad}}=8/j_{0,1}^2$, exactly*, companion note, `research/theory/07-radial-maynard.md` (this repository). Complete proof of the radial value, its Bessel extremizer, and a self-contained enclosure of $j_{0,1}$.

[5] R. M. Corless, G. H. Gonnet, D. E. G. Hare, D. J. Jeffrey, D. E. Knuth, *On the Lambert W function*, Adv. Comput. Math. **5** (1996), 329–359.

[6] M. Reed, B. Simon, *Methods of Modern Mathematical Physics*, Vol. I (Functional Analysis) and Vol. IV (Analysis of Operators), Academic Press. (Weyl criterion for the essential spectrum; stability under compact perturbation.)

[7] P. D. Hislop, I. M. Sigal, *Introduction to Spectral Theory*, Springer, 1996. (Weyl sequences, Thm. 7.2.)

[8] NIST Digital Library of Mathematical Functions, §10.21 (zeros of Bessel functions), https://dlmf.nist.gov/10.21. ($j_{0,1}=2.40482555769577276862\ldots$)

[9] D. A. Goldston, J. Pintz, C. Y. Yıldırım, *Primes in tuples I*, Ann. of Math. (2) **170** (2009), 819–862. (Context: one-dimensional cutoffs and the Bessel-optimal weight.)
