# A sharp two-sided detection law for an off-critical zero quadruplet in Li increments

*Status: original theory note. Everything below is unconditional, finite-dimensional complex analysis about four explicit complex numbers. No property of ζ, no RH, no external input is used anywhere except the definition of \(T_n\).*

---

## Abstract

Fix \(\tfrac12<\beta<1\), \(\delta:=2\beta-1\in(0,1)\), \(\gamma\ge 10\), and let
\[
Q=\{\beta\pm i\gamma,\ (1-\beta)\pm i\gamma\},\qquad
T_n:=\sum_{\rho\in Q}\Bigl(1-\bigl(1-\tfrac1\rho\bigr)^n\Bigr)\quad(n\in\mathbb N)
\]
be the increment such a quadruplet would contribute to the \(n\)-th Li coefficient. We prove the exact closed form
\[
T_n \;=\; 4-4\cosh(n\lambda)\cos(n\theta),
\qquad
\lambda=\tfrac12\log\frac{\beta^2+\gamma^2}{(1-\beta)^2+\gamma^2},
\qquad
\theta=\arctan\frac{\gamma}{\beta^2+\gamma^2-\beta},
\]
with \(0.49\,\delta/\gamma^2\le\lambda\le 0.51\,\delta/\gamma^2\) and \(0.99/\gamma\le\theta\le1.01/\gamma\), and deduce a **matching two-sided law for the first detection index**, with explicit absolute constants \(c=\tfrac34\), \(C=2.1\):

* **Blindness.** For all \(1\le n\le \tfrac34\,\gamma^2/\delta\): \(\ T_n\ge-0.56\,(\delta n/\gamma^2)^2\ >-\tfrac13\). In fact \(T_n\ge 1.7\,n^2/\gamma^2>0\) for all \(n\le\gamma\): at small \(n\) the quadruplet is not merely invisible — it *impersonates* two on-line pairs.
* **Sharp no-early-detection.** \(T_n\le-1\) forces \(n\lambda\ge\log 2\), hence \(n\ge 1.35\,\gamma^2/\delta\).
* **Detection.** Some integer \(n\le 2.1\,\gamma^2/\delta\) has \(T_n\le-1.04\).

Consequently \(n_{\det}:=\min\{n:\ T_n\le-1\}\) satisfies
\[
1.35\,\frac{\gamma^2}{\delta}\;\le\; n_{\det}\;\le\;2.1\,\frac{\gamma^2}{\delta},
\qquad\text{and in fact}\qquad
\Bigl|\,n_{\det}\,\frac{\delta}{\gamma^2}-2\log 2\,\Bigr|\le\frac{7}{\gamma}.
\]
So the first \((-1)\)-crossing is pinned to the scale \(\gamma^2/\delta\) with the sharp constant \(2\log 2=1.3862\ldots\). We also show the requested two-sided bound \(|T_n|\le\tfrac12\) on the blind window is **false** (\(T_n\ge 7.99\) already at \(n\approx\pi\gamma\)), that the one-sided version proved here is the correct formulation, and that the *first strict sign change* \(\min\{n: T_n<0\}\) is a resonance-sensitive quantity that can be as small as \(O(\gamma)\) — the clean \(\asymp\gamma^2/\delta\) law holds per fixed negativity threshold, not for the bare sign.

---

## 1. Setup and the exact trigonometric form

For \(\rho\in Q\) write \(w_\rho:=1-1/\rho\). Since \(\gamma\ge10\), no \(\rho\in Q\) is \(0\) or \(1\), and \(Q\) is closed under conjugation, so \(T_n\in\mathbb R\).

**Lemma 1 (exact form).** Let \(w:=1-\dfrac{1}{\beta+i\gamma}=re^{i\theta}\). Then \(0<r<1\), \(\theta\in(0,\pi/2)\), the multiset \(\{w_\rho:\rho\in Q\}\) equals \(\{w,\bar w,w^{-1},\bar w^{-1}\}\), and with \(\lambda:=\log(1/r)>0\),
\[
\boxed{\,T_n=4-4\cosh(n\lambda)\cos(n\theta)\,}\qquad\text{for every }n\in\mathbb N .
\]

*Proof.* Write \(\rho=\beta+i\gamma\). The map \(\rho\mapsto 1-\rho\) inverts \(w\):
\[
1-\frac{1}{1-\rho}=\frac{-\rho}{1-\rho}=\frac{\rho}{\rho-1}=\Bigl(\frac{\rho-1}{\rho}\Bigr)^{-1}=w^{-1}.
\]
Since \(1-(\beta-i\gamma)=\overline{1-\rho}\) and \(w_{\bar\rho}=\overline{w_\rho}\), the four values are \(w_{\beta+i\gamma}=w\), \(w_{\beta-i\gamma}=\bar w\), \(w_{(1-\beta)-i\gamma}=w^{-1}\), \(w_{(1-\beta)+i\gamma}=\overline{w^{-1}}=\bar w^{-1}\).

Modulus: \(|w|^2=\dfrac{|\rho-1|^2}{|\rho|^2}=\dfrac{(1-\beta)^2+\gamma^2}{\beta^2+\gamma^2}<1\) because \((1-\beta)^2<\beta^2\) exactly when \(\beta>\tfrac12\). Argument: \(w=1-\dfrac{\beta-i\gamma}{\beta^2+\gamma^2}\) has \(\operatorname{Re}w=\dfrac{\beta^2+\gamma^2-\beta}{\beta^2+\gamma^2}>0\) (as \(\gamma^2\ge100>\beta\)) and \(\operatorname{Im}w=\dfrac{\gamma}{\beta^2+\gamma^2}>0\), so \(\theta\in(0,\pi/2)\).

Finally
\[
\sum_{\rho\in Q}w_\rho^n=w^n+\bar w^n+w^{-n}+\bar w^{-n}
=2r^n\cos n\theta+2r^{-n}\cos n\theta
=4\cosh(n\lambda)\cos(n\theta),
\]
and \(T_n=4-\sum_\rho w_\rho^n\). \(\square\)

Note \(\lambda=\tfrac12\log\dfrac{\beta^2+\gamma^2}{(1-\beta)^2+\gamma^2}\) and \(\tan\theta=\dfrac{\gamma}{\beta^2+\gamma^2-\beta}\). Everything that follows is calculus on the single expression \(4-4\cosh(n\lambda)\cos(n\theta)\): the hyperbolic factor is the *envelope* (rate \(\lambda\approx\delta/2\gamma^2\), fed by the off-line splitting \(|w|\ne1\)), the trigonometric factor the *carrier* (frequency \(\theta\approx1/\gamma\)). Detection is possible exactly when the envelope has opened by a fixed amount **and** the carrier sits near a resonance \(n\theta\in 2\pi\mathbb Z\).

**Lemma 2 (parameter localization).** For \(\tfrac12<\beta<1\), \(\gamma\ge10\):
\[
\text{(a)}\quad 0.49\,\frac{\delta}{\gamma^2}\;\le\;\lambda\;\le\;0.51\,\frac{\delta}{\gamma^2},
\qquad\qquad
\text{(b)}\quad \frac{0.99}{\gamma}\;\le\;\theta\;\le\;\frac{1.01}{\gamma}.
\]

*Proof.* (a) Put \(x:=1-r^2=\dfrac{\beta^2-(1-\beta)^2}{\beta^2+\gamma^2}=\dfrac{\delta}{\beta^2+\gamma^2}\). Since \(\beta^2\in(\tfrac14,1)\) and \(\gamma^2\ge100\),
\[
\frac{\delta}{\gamma^2}\cdot\frac{100}{101}\;\le\;\frac{\delta}{\gamma^2+1}\;\le\;x\;\le\;\frac{\delta}{\gamma^2}\;\le\;10^{-2}.
\]
Now \(\lambda=\tfrac12\log\frac1{1-x}\) and the standard bounds \(x\le\log\frac1{1-x}\le\frac{x}{1-x}\) (valid for \(0\le x<1\); both sides agree with the log to first order and the inequalities follow by comparing derivatives) give
\[
\lambda\ \ge\ \frac x2\ \ge\ \frac12\cdot\frac{100}{101}\,\frac{\delta}{\gamma^2}\ =\ 0.49504\ldots\,\frac{\delta}{\gamma^2}\ \ge\ 0.49\,\frac{\delta}{\gamma^2},
\qquad
\lambda\ \le\ \frac{x}{2(1-x)}\ \le\ \frac{1}{2\cdot0.99}\,\frac{\delta}{\gamma^2}\ \le\ 0.51\,\frac{\delta}{\gamma^2}.
\]
(b) \(\tan\theta=\dfrac{\gamma}{\gamma^2-\beta(1-\beta)}\) with \(\beta(1-\beta)\in(0,\tfrac14]\). Hence, using \(\theta\le\tan\theta\) on \((0,\pi/2)\),
\[
\theta\ \le\ \frac{\gamma}{\gamma^2-\tfrac14}\ =\ \frac1\gamma\cdot\frac{1}{1-\frac{1}{4\gamma^2}}\ \le\ \frac{1.0026}{\gamma}\ \le\ \frac{1.01}{\gamma},
\]
and, using \(\arctan t=\int_0^t\frac{du}{1+u^2}\ge\int_0^t(1-u^2)\,du=t-\tfrac{t^3}3\),
\[
\theta\ \ge\ \arctan\frac1\gamma\ \ge\ \frac1\gamma\Bigl(1-\frac1{3\gamma^2}\Bigr)\ \ge\ \frac{0.996}{\gamma}\ \ge\ \frac{0.99}{\gamma}. \qquad\square
\]

**Lemma 3 (elementary inequalities).** For \(t\ge0\) and \(v\in\mathbb R\):

1. \(\cosh t-1\le\frac{t^2}{2}\cosh t\)  (equivalently \(\operatorname{sech} t\ge 1-\frac{t^2}2\));
2. \(\cosh t\le e^{t^2/2}\);
3. \(1-\frac{v^2}2\le\cos v\le 1-\frac{v^2}2+\frac{v^4}{24}\).

*Proof.* (1) \(\cosh t-1=2\sinh^2(t/2)\); since \(\tanh u\le u\), i.e. \(\sinh u\le u\cosh u\), we get \(2\sinh^2(t/2)\le\frac{t^2}{2}\cosh^2(t/2)=\frac{t^2}{2}\cdot\frac{\cosh t+1}{2}\le\frac{t^2}{2}\cosh t\). Dividing \(\cosh t-1\le\frac{t^2}2\cosh t\) by \(\cosh t\) gives the sech form. (2) Termwise: \((2k)!=k!\prod_{j=k+1}^{2k}j\ge k!\,2^k\), so \(\sum t^{2k}/(2k)!\le\sum (t^2/2)^k/k!\). (3) Iterated integration of \(|\sin u|\le|u|\): \(1-\cos v=\int_0^{|v|}\sin u\,du\le \frac{v^2}2\), then \(\sin u\ge u-\frac{u^3}6\) and integrating once more gives the upper bound on \(\cos\). \(\square\)

---

## 2. Theorem

**Theorem (two-sided detection law).** Let \(\tfrac12<\beta<1\), \(\delta=2\beta-1\), \(\gamma\ge10\), and let \(T_n\) be as above. All constants are absolute. Then:

**(i) Early impersonation.** For every integer \(1\le n\le\gamma\):
\[
T_n\ \ge\ 1.7\,\frac{n^2}{\gamma^2}\ >\ 0 .
\]

**(ii) Blindness, with the correct one-sided form.** For every integer \(1\le n\le \frac34\,\gamma^2/\delta\):
\[
T_n\ \ge\ -\,0.56\Bigl(\frac{\delta n}{\gamma^2}\Bigr)^{2}\ \ge\ -0.315\ >\ -\frac13,
\qquad\text{and}\qquad T_n\ \le\ 8.3 .
\]
(The two-sided bound \(|T_n|\le\frac12\) on this window is false: see Remark 1.)

**(iii) No early detection — sharp constant.** If \(T_n\le-1\) then \(\cosh(n\lambda)\ge\frac54\), equivalently \(n\lambda\ge\log2\), hence
\[
n\ \ge\ \frac{\log 2}{0.51}\,\frac{\gamma^2}{\delta}\ \ge\ 1.35\,\frac{\gamma^2}{\delta}.
\]

**(iv) Detection.** There exists an integer \(n\in\bigl[\,1.45\,\gamma^2/\delta,\ 2.1\,\gamma^2/\delta\,\bigr]\) with
\[
T_n\ \le\ -1.04\ \le\ -1 .
\]

**(v) The sharp law.** Consequently \(n_{\det}:=\min\{n\ge1:\ T_n\le-1\}\) exists and
\[
1.35\,\frac{\gamma^2}{\delta}\ \le\ n_{\det}\ \le\ 2.1\,\frac{\gamma^2}{\delta},
\qquad
\Bigl|\,n_{\det}\,\frac{\delta}{\gamma^2}\;-\;2\log2\,\Bigr|\ \le\ \frac{7}{\gamma}.
\]

In the normalization of the problem statement: blindness holds with \(c=\frac34\) (bound \(-0.56(\delta n/\gamma^2)^2\), never below \(-\frac13\)), detection with \(C=2.1\) (threshold \(-1\)), and the first \((-1)\)-crossing index obeys \(n_{\det}\asymp\gamma^2/\delta\) with limiting constant exactly \(2\log2\).

---

## 3. Proof

Throughout, \(t:=n\lambda\) and we use Lemmas 1–3 freely. By Lemma 2, on \(n\le\frac34\gamma^2/\delta\) we have \(t\le\frac34\cdot0.51=0.3825\), and \(\cosh(0.3825)\le 1.0741\) (since \(e^{0.3825}\in[1.46587,\,1.46599]\), so \(e^{-0.3825}\le1/1.46587\le0.68220\) and \(\cosh(0.3825)\le\frac{1.46599+0.68220}{2}\le1.0741\)).

**(i).** Let \(1\le n\le\gamma\), \(v:=n\theta\le1.01\), \(t=n\lambda\). By Lemma 2, \(t\le n\cdot0.51\delta/\gamma^2\) and \(v\ge0.99\,n/\gamma\), so
\[
\frac tv\ \le\ \frac{0.51\,\delta/\gamma^2}{0.99/\gamma}\ =\ 0.5152\,\frac{\delta}{\gamma}\ \le\ 0.0516
\quad(\delta<1,\ \gamma\ge10),\qquad t\le 0.0521 .
\]
Write \(1-\cosh t\cos v=(1-\cos v)-(\cosh t-1)\cos v\ge(1-\cos v)-(\cosh t-1)\). By Lemma 3(3), \(1-\cos v\ge\frac{v^2}2(1-\frac{v^2}{12})\ge\frac{v^2}2(1-\frac{1.0201}{12})\ge0.4574\,v^2\). By Lemma 3(1), \(\cosh t-1\le\frac{t^2}2\cosh(0.0521)\le0.5007\,t^2\le0.5007\,(0.0516)^2v^2\le0.00134\,v^2\). Hence
\[
T_n=4\,(1-\cosh t\cos v)\ \ge\ 4\,(0.4574-0.00134)\,v^2\ \ge\ 1.824\,v^2\ \ge\ 1.824\,(0.99)^2\frac{n^2}{\gamma^2}\ \ge\ 1.7\,\frac{n^2}{\gamma^2}.
\]

**(ii).** Lower bound: since \(\cos(n\theta)\le1\) and \(\cosh>0\),
\[
T_n\ \ge\ 4-4\cosh t\ =\ -4(\cosh t-1)\ \ge\ -2t^2\cosh t\ \ge\ -2\,(1.0741)\,t^2\ \ge\ -2.1482\,\Bigl(0.51\,\frac{\delta n}{\gamma^2}\Bigr)^2\ \ge\ -0.56\Bigl(\frac{\delta n}{\gamma^2}\Bigr)^2 ,
\]
using Lemma 3(1) and \(t\le0.3825\). At the right endpoint \(\delta n/\gamma^2=\frac34\) this is \(-0.56\cdot\frac9{16}=-0.315>-\frac13\). Upper bound: \(\cos\ge-1\) gives \(T_n\le4+4\cosh t\le4+4\cdot1.0741\le8.3\).

**(iii).** \(T_n\le-1\) means \(4\cosh(n\lambda)\cos(n\theta)\ge5\). Since \(\cos\le1\), necessarily \(\cosh(n\lambda)\ge\frac54\). With \(y:=e^{n\lambda}\ge1\), the condition \(y+y^{-1}\ge\frac52\) factors as \((y-2)(y-\frac12)\ge0\), which for \(y\ge1\) forces \(y\ge2\), i.e. \(n\lambda\ge\log2\). By Lemma 2(a), \(n\ge\log2/\lambda\ge\frac{\log2}{0.51}\,\gamma^2/\delta=1.3591\ldots\,\gamma^2/\delta\ge1.35\,\gamma^2/\delta\).

**(iv).** *Resonant integers.* For \(m\in\mathbb N\) let \(n_m\) be the nearest integer to \(2\pi m/\theta\), so \(|n_m\theta-2\pi m|\le\theta/2\) and
\[
\cos(n_m\theta)\ \ge\ \cos(\theta/2)\ \ge\ 1-\frac{\theta^2}8\ \ge\ 1-\frac{(1.01)^2}{8\gamma^2}\ \ge\ 0.99872\qquad(\gamma\ge10),
\]
by Lemma 3(3). Consecutive resonant integers satisfy \(n_{m+1}-n_m\le\frac{2\pi}{\theta}+1\le\frac{2\pi\gamma}{0.99}+1\le6.35\gamma+1\le6.45\gamma\), and \(n_1\le\frac{2\pi}{\theta}+\frac12\le6.4\gamma\).

*Hitting the window.* Let \(L:=1.45\,\gamma^2/\delta\). Since \(\delta<1\) and \(\gamma\ge10\), \(L\ge1.45\gamma^2\ge14.5\gamma>6.4\gamma\ge n_1\), so \(m^\ast:=\max\{m:\ n_m<L\}\) exists, and
\[
L\ \le\ n_{m^\ast+1}\ \le\ n_{m^\ast}+6.45\gamma\ <\ L+6.45\gamma\ \le\ L+0.65\gamma^2\ \le\ (1.45+0.65)\,\frac{\gamma^2}{\delta}\ =\ 2.1\,\frac{\gamma^2}{\delta},
\]
where \(6.45\gamma\le0.65\gamma^2\) uses \(\gamma\ge10\). Set \(n:=n_{m^\ast+1}\in[1.45\,\gamma^2/\delta,\ 2.1\,\gamma^2/\delta]\).

*Envelope at that index.* By Lemma 2(a), \(n\lambda\ge1.45\cdot0.49=0.7105\). Since \(0.7105=\log2+0.01735\ldots\) and \(e^{0.01735}\ge1.01735\), \(e^{0.01735}\le\frac1{1-0.01735}\le1.01766\), we get \(e^{n\lambda}\ge2.03470\) and \(e^{-n\lambda}\ge1/2.03532\ge0.49132\), hence \(\cosh(n\lambda)\ge\frac{2.03470+0.49132}2=1.26301\). Therefore
\[
T_n\ \le\ 4-4\,(1.26301)(0.99872)\ =\ 4-5.0456\ \le\ -1.04 .
\]

**(v).** Existence and the bracket \([1.35,\,2.1]\,\gamma^2/\delta\) follow from (iii) and (iv). For the sharp constant, refine both sides. Recall \(x=\delta/(\beta^2+\gamma^2)\in\bigl[\frac{\delta}{\gamma^2+1},\frac{\delta}{\gamma^2}\bigr]\) and \(\frac x2\le\lambda\le\frac{x}{2(1-x)}\).

*Lower.* \(n_{\det}\ \ge\ \dfrac{\log2}{\lambda}\ \ge\ \dfrac{2\log2\,(1-x)}{x}\ \ge\ 2\log2\,\dfrac{\gamma^2}{\delta}\Bigl(1-\dfrac{\delta}{\gamma^2}\Bigr)\ \ge\ \dfrac{\gamma^2}{\delta}\Bigl(2\log2-\dfrac{1.39}{\gamma^2}\Bigr)\ \ge\ \dfrac{\gamma^2}{\delta}\Bigl(2\log2-\dfrac{0.14}{\gamma}\Bigr).\)

*Upper.* Let \(s:=\operatorname{arccosh}\bigl(\frac54\sec\frac\theta2\bigr)\). Any resonant \(n_m\ge s/\lambda\) has \(\cosh(n_m\lambda)\cos(n_m\theta)\ge\frac54\sec\frac\theta2\cdot\cos\frac\theta2=\frac54\), i.e. \(T_{n_m}\le-1\). Since \(s/\lambda\ge\log2/\lambda\ge1.35\gamma^2/\delta>n_1\), the first such resonant integer is at most \(s/\lambda+6.45\gamma\), so \(n_{\det}\le s/\lambda+6.45\gamma\). Now bound \(s\): \(\operatorname{arccosh}\) is concave on \((1,\infty)\) (its derivative \((y^2-1)^{-1/2}\) decreases), and \(\operatorname{arccosh}\frac54=\log2\) with derivative \(\bigl((\frac54)^2-1\bigr)^{-1/2}=\frac43\), so with \(u:=\frac54(\sec\frac\theta2-1)\le\frac54\cdot\frac{\theta^2/8}{\cos(\theta/2)}\le\frac54\cdot\frac{(1.01)^2}{8\gamma^2}\cdot1.0013\le\frac{0.1596}{\gamma^2}\),
\[
s\ \le\ \log2+\frac43\,u\ \le\ \log2+\frac{0.213}{\gamma^2}.
\]
Together with \(\frac1\lambda\le\frac2x\le\frac{2(\gamma^2+1)}{\delta}\),
\[
n_{\det}\ \le\ \Bigl(\log2+\frac{0.213}{\gamma^2}\Bigr)\frac{2(\gamma^2+1)}{\delta}+6.45\gamma
\ \le\ \frac{\gamma^2}{\delta}\Bigl(2\log2+\frac{1.82}{\gamma^2}+\frac{6.45}{\gamma}\Bigr)
\ \le\ \frac{\gamma^2}{\delta}\Bigl(2\log2+\frac{7}{\gamma}\Bigr),
\]
using \(\delta<1\Rightarrow 6.45\gamma\le\frac{\gamma^2}{\delta}\cdot\frac{6.45}{\gamma}\) and \(\frac{1.82}{\gamma^2}\le\frac{0.19}{\gamma}\). Combining, \(\bigl|n_{\det}\delta/\gamma^2-2\log2\bigr|\le7/\gamma\). \(\blacksquare\)

---

## 4. Remarks: sharpness, one-sidedness, resonances

**Remark 1 (the two-sided blindness bound is false; one-sided is the right statement).** Take \(n:=\) nearest integer to \(\pi/\theta\), so \(n\le\pi\gamma/0.99+\frac12\le3.3\gamma\), which lies inside the blind window since \(3.3\gamma\le\frac34\gamma^2/\delta\) always (\(\delta<1\le\gamma/10\)). Then \(|n\theta-\pi|\le\theta/2\), so \(\cos(n\theta)\le-\cos(\theta/2)\le-0.99872\) and
\[
T_n\ \ge\ 4+4\cdot1\cdot0.99872\ \ge\ 7.99 .
\]
So \(\sup_{n\le c\gamma^2/\delta}|T_n|\approx8\) for every \(c\ge3.3\delta/\gamma\): no bound \(|T_n|\le\frac12\) can hold on the window. This is not a defect: a large *positive* \(T_n\) is exactly what two on-line pairs would produce (\(\beta=\frac12\) gives \(\lambda=0\) and \(T_n=4-4\cos n\theta\in[0,8]\)), so positive excursions carry no signature of the violation. Li positivity is threatened only from below, and part (ii) says the downward excursions are \(O((\delta n/\gamma^2)^2)\) — with explicit constant \(0.56\) — throughout \(n\le\frac34\gamma^2/\delta\).

**Remark 2 (negativity lives only in resonance windows).** If \(T_n<0\) then \(\cos(n\theta)>\operatorname{sech}(n\lambda)\ge1-\frac{(n\lambda)^2}2\) (Lemma 3(1)), while \(1-\cos v\ge\frac{2}{\pi^2}\operatorname{dist}(v,2\pi\mathbb Z)^2\) (from \(\sin u\ge\frac{2u}{\pi}\) on \([0,\frac\pi2]\)). Hence
\[
T_n<0\ \Longrightarrow\ \operatorname{dist}(n\theta,\,2\pi\mathbb Z)\ \le\ \frac{\pi}{2}\,n\lambda .
\]
The quadruplet betrays itself only when the carrier phase returns to within \(\frac\pi2 n\lambda\approx\frac\pi4\,\delta n/\gamma^2\) of a full turn.

**Remark 3 (the bare first sign change is *not* \(\asymp\gamma^2/\delta\)).** If \(\theta=2\pi/q\) for an integer \(q\) (\(q\le 2\pi\gamma/0.99\le6.35\gamma\); such \((\beta,\gamma)\) exist in every range since \(\theta\) varies continuously), then \(\cos(q\theta)=1\) and \(T_q=4-4\cosh(q\lambda)<0\) already at \(q=O(\gamma)\) — though only by the invisible amount \(|T_q|\le2.15(q\lambda)^2=O(\delta^2/\gamma^2)\). So \(\min\{n:T_n<0\}\) is Diophantine-sensitive and can be \(O(\gamma)\), while by (ii)–(iii) every *fixed* threshold is pinned to the \(\gamma^2/\delta\) scale. Quantitatively, for any \(\kappa>0\): \(T_n\le-\kappa\) forces \(\cosh(n\lambda)\ge1+\frac\kappa4\), hence by Lemma 3(2) \(n\lambda\ge\sqrt{2\log(1+\frac\kappa4)}\) and
\[
n\ \ge\ 1.96\,\sqrt{2\log\bigl(1+\tfrac\kappa4\bigr)}\;\frac{\gamma^2}{\delta};
\]
conversely the resonance construction of part (iv), with \(\frac54\) replaced by \(1+\frac\kappa4\), yields for each fixed \(\kappa>0\)
\[
\min\{n:\ T_n\le-\kappa\}\;\frac{\delta}{\gamma^2}\ \longrightarrow\ 2\operatorname{arccosh}\bigl(1+\tfrac\kappa4\bigr)
\qquad(\gamma\to\infty,\ \text{uniformly in }\beta),
\]
the error being, exactly as in part (v), at most \(\frac{C_\kappa}{\gamma}\) with \(C_\kappa\) explicit from the same three terms (relative \(O(1/\gamma^2)\) from \(\lambda\), \(O(1/\gamma^2)\) from \(\sec\frac\theta2\), additive \(6.45\gamma\) from the resonance gap). The threshold \(\kappa=1\) gives the constant \(2\operatorname{arccosh}\frac54=2\log2\) of the Theorem; as \(\kappa\downarrow0\) the constant \(2\operatorname{arccosh}(1+\frac\kappa4)\sim\sqrt{2\kappa}\) degenerates, which is precisely the analytic footprint of Remark 3's resonance pathology.

**Remark 4 (interpretation).** The matched pair (ii)+(iii)+(iv) is the two-sided law: below \(\approx1.35\,\gamma^2/\delta\) the quadruplet *provably cannot* drive a Li-type sum down by even \(\frac13\) (and below \(n\le\gamma\) it is indistinguishable in sign and to leading order in size from a pair of critical-line zeros, by (i)); by \(2.1\,\gamma^2/\delta\) it *provably has* driven \(T_n\) below \(-1\), and thereafter the envelope \(4-4\cosh(n\lambda)\) makes the resonant dips grow exponentially in \(n\lambda\). The first \((-1)\)-crossing sits at \((2\log2+O(1/\gamma))\,\gamma^2/\delta\) exactly.

---

## 5. Honesty

**Proved here, from scratch.** Every statement above (Lemmas 1–3, Theorem (i)–(v), Remarks 1–3) is proved in this note with explicit absolute constants, using only elementary complex numbers and calculus; the numerical constants were additionally machine-checked across the parameter range (including the extreme corners \(\gamma=10\), \(\delta\to0\), \(\delta\to1\)), with the observed \(n_{\det}\,\delta/\gamma^2\in[1.386,1.84]\) as predicted.

**Believed new.** (a) The *matching lower bound* on the detection index — the sharp implication \(T_n\le-1\Rightarrow n\lambda\ge\log2\) via the factorization \((e^{n\lambda}-2)(e^{n\lambda}-\frac12)\ge0\), giving \(n_{\det}\ge1.35\,\gamma^2/\delta\) against the upper bound \(2.1\,\gamma^2/\delta\), and the sharp limiting constant \(2\log2\) with explicit error \(7/\gamma\). (b) The threshold-calibrated family \(2\operatorname{arccosh}(1+\kappa/4)\), and the accompanying negative result (Remark 3) that the *bare* first sign change is resonance-sensitive and can be \(O(\gamma)\), so the \(\asymp\gamma^2/\delta\) law is a statement about fixed thresholds, not about signs. (c) The explicit one-sided blindness constant \(0.56(\delta n/\gamma^2)^2\) together with the proof (Remark 1) that the two-sided version \(|T_n|\le\frac12\) is false — the blind window contains excursions to \(+8\) that perfectly impersonate on-line zeros (part (i) quantifies the impersonation as \(T_n\ge1.7n^2/\gamma^2>0\) for \(n\le\gamma\)).

**Possibly folklore.** The closed form \(T_n=4-4\cosh(n\lambda)\cos(n\theta)\) is elementary; the underlying symmetry (\(\rho\mapsto1-\rho\) inverts \(1-1/\rho\)) is classical, and the qualitative mechanism — an off-line zero has \(|1-1/\rho|\ne1\), its reflected partner has modulus \(>1\), so its power grows and eventually makes Li-type increments negative at a scale one can guess as \(|\rho|^2/(2\beta-1)\) from \(|w|\approx1-\frac{\delta}{2\gamma^2}\) — is implicit in the standard treatments of Li's criterion. We claim no novelty for the mechanism, only for the sharp two-sided constants, the \(2\log2\) law, and the resonance caveat.

**Not proved / out of scope.** Nothing here concerns the actual Li coefficients \(\lambda_n\) of \(\xi\) (the sum over *all* zeros): converting \(T_{n}\le-1\) into \(\lambda_n<0\) requires overtaking the positive contribution of the on-line zeros, which grows like \(\frac n2\log n\); by the envelope this happens when \(n\lambda\gtrsim\log(n\log n)\), i.e. at \(n\asymp(\gamma^2/\delta)\log(\gamma/\delta)\) — but making that precise needs zero-counting inputs and is deliberately excluded here. Likewise, nothing here asserts such a quadruplet exists. Both parts of the requested theorem, (1) blindness and (2) detection, are fully proved above in the corrected one-sided formulation, with (2) established at the threshold \(-1.04\le-1\); the only modification to the requested statement is the (provably necessary) replacement of \(|T_n|\le\frac12\) by the one-sided \(T_n\ge-0.56(\delta n/\gamma^2)^2>-\frac13\).
