# BSD — Wave-2 Breakthrough

**Legion 03, Wave 2.** Wave 1 ([`REPORT.md`](./REPORT.md)) delivered a complete proof of BSD I for the
*single* curve \(y^2 = x^3 - x\) (Fermat's descent), floating-point verification of the leading-term
formula on six Cremona curves and seven congruent-number curves, and the "One-Class Barrier"
no-go analysis. Wave 2 delivers what the mission's option (1) asks for — **a fully proved
elementary theorem about rank-0 congruent-number curves for a clean infinite family** — and, on
top of it, option (2): a **370-fold extension of the machine verification** (2,214 Cremona curves,
a 19-prime family table exact to 38 digits, and a 19,653-prime counting scan with zero violations).

The headline: **BSD I is proved here, end to end and by elementary means (plus one cited classical
theorem of Tunnell), for the infinite family \(E_p : y^2 = x^3 - p^2x\), \(p\) prime,
\(p \equiv 3 \pmod 8\)** — with the strictly stronger algebraic statement
\(\operatorname{Sel}_2(E_p) \cong (\mathbb{Z}/2)^2\) (so also \(\Sha(E_p)[2] = 0\)), an *effective*
analytic lower bound \(L(E_p,1) \ge \beta/\sqrt{p}\), and the 2-part of the strong BSD formula.
The content is classical (Genocchi 1855 ancestry; see Honesty label) — the contribution is a
complete, self-contained, machine-cross-checked proof, not a claim of priority.

---

## Theorem or Computational Theorem

Throughout, \(p\) is a prime with \(p \equiv 3 \pmod 8\), and

\[
E_p:\; y^2 = x^3 - p^2 x = x(x-p)(x+p),
\qquad \Delta = 2^6 p^6,\quad N = 2^5 p^2 .
\]

This is the congruent-number curve: \(p\) is a congruent number iff \(E_p(\mathbb{Q})\) has a point
with \(y \neq 0\) beyond 2-torsion, iff (as we show) \(\operatorname{rank} E_p(\mathbb{Q}) \ge 1\).
There are infinitely many such \(p\) (Dirichlet). Let
\(\beta = \int_1^\infty \frac{dx}{\sqrt{x^3-x}} = 2.6220575542\ldots\)

**Theorem A (complete 2-descent; algebraic side).** *For every prime \(p \equiv 3 \pmod 8\):*

\[
\operatorname{Sel}_2(E_p/\mathbb{Q}) \;\cong\; (\mathbb{Z}/2)^2 .
\]

*Consequently:*
1. \(\operatorname{rank} E_p(\mathbb{Q}) = 0\);
2. \(E_p(\mathbb{Q}) = \{O, (0,0), (p,0), (-p,0)\} \cong (\mathbb{Z}/2)^2\);
3. \(\Sha(E_p/\mathbb{Q})[2] = 0\) — in particular, if \(\Sha(E_p)\) is finite, its order is odd;
4. \(p\) is not a congruent number (Genocchi's theorem, 1855).

**Theorem B (Tunnell-number congruence; analytic side).** *For every prime
\(p \equiv 3 \pmod 8\), the Tunnell number*

\[
a_p \;=\; \#\{(x,y,z)\in\mathbb{Z}^3 : p = 2x^2+y^2+32z^2\} \;-\; \tfrac12\,\#\{(x,y,z)\in\mathbb{Z}^3 : p = 2x^2+y^2+8z^2\}
\]

*satisfies*

\[
a_p \equiv 2 \pmod 4 .
\]

*In particular \(a_p \neq 0\), and by Tunnell's theorem* [PROVED–CITED: Tunnell 1983]
*\(L(E_p,1) = \beta a_p^2 / (4\sqrt p)\), so*

\[
L(E_p,1) \;\ge\; \frac{\beta}{\sqrt p} \;>\; 0,
\qquad\text{hence}\qquad
\operatorname{ord}_{s=1} L(E_p,s) = 0 .
\]

**Corollary C.** *For every prime \(p \equiv 3 \pmod 8\) — an infinite family:*

1. **BSD I holds for \(E_p\):**
   \(\operatorname{ord}_{s=1}L(E_p,s) = 0 = \operatorname{rank} E_p(\mathbb{Q})\), with *both* sides
   determined unconditionally and effectively (no floating point in the statement or proof).
2. **The analytic Sha is the odd perfect square \((a_p/2)^2\):** with
   \(\Omega_{E_p} = 2\beta/\sqrt p\), \(\prod_\ell c_\ell = c_2 c_p = 2\cdot 4 = 8\),
   \(\#E_p(\mathbb{Q})_{\mathrm{tors}}^2 = 16\), \(\mathrm{Reg} = 1\), strong BSD for \(E_p\) is
   *equivalent* to the exact identity \(\#\Sha(E_p) = (a_p/2)^2\).
3. **The 2-part of strong BSD holds for \(E_p\):** \(\Sha(E_p)\) is finite (Rubin's CM theorem
   applies since \(E_p\) has CM by \(\mathbb{Z}[i]\) and \(L(E_p,1)\ne 0\) [PROVED–CITED]), and
   \(v_2(\#\Sha) = 0 = v_2\bigl((a_p/2)^2\bigr)\): the 2-adic valuations of the two sides of the
   BSD formula agree, by Theorem A(3) + Theorem B.

**Computational Theorem D (machine-verified, PARI/GP 2.15.4; script
[`breakthrough.gp`](./breakthrough.gp), transcript [`breakthrough.out`](./breakthrough.out)).**

1. \(a_p \equiv 2 \pmod 4\) and \(\#\{(x,y): 2x^2+y^2=p\} = 4\) hold for **all 19,653 primes**
   \(p \equiv 3 \pmod 8\), \(p \le 10^6\) (exact integer arithmetic; zero violations).
2. `ellrank` (2-descent + Cassels pairing) certifies rank exactly 0 for **all 311 primes**
   \(p \equiv 3 \pmod 8\), \(p \le 10^4\) (zero failures).
3. For the 19 primes \(p \in \{3,\dots,283\} \cup \{307, 467, 907\}\): \(L(E_p,1)\) agrees with
   \(\beta a_p^2/(4\sqrt p)\) and implied \(\#\Sha\) agrees with \((a_p/2)^2\) to \(\le 5\cdot10^{-38}\),
   with the predicted values \(\#\Sha_{\mathrm{an}} = 1, 9, 25, 49, 81\) all occurring; local data
   uniformly \(c_2 = 2\) (Kodaira III), \(c_p = 4\) (I\(_0^*\)), \(\Omega = 2\beta/\sqrt p\).
4. Strong-BSD leading-term verification for **all 2,214 Cremona curves of conductor \(\le 500\)**
   (Wave 1: 6 curves): worst deviation of implied \(\#\Sha\) from an integer \(3\cdot 10^{-35}\);
   every rounded value a perfect square (34 curves with \(\Sha_{\mathrm{an}} \in \{4,9,16,25\}\));
   analytic rank always inside the descent rank window; the only 2 curves where
   2-descent + Cassels pairing cannot close the rank (210e7, 210e8) are exactly the two with
   \(\Sha[4] \ne 0\) (\(\#\Sha = 16\)), as theory demands.

---

## Proof or machine transcript (commands + outputs)

### 0. Elementary facts used

For \(p \equiv 3 \pmod 8\):

- (QR1) \(\bigl(\tfrac{-1}{p}\bigr) = -1\) (since \(p \equiv 3 \bmod 4\)); hence
  \(u^2 + v^2 \equiv 0 \pmod p \Rightarrow p \mid u,\, p \mid v\).
- (QR2) \(\bigl(\tfrac{2}{p}\bigr) = -1\) (since \(p \equiv 3 \bmod 8\)).
- (QR3) \(\bigl(\tfrac{-2}{p}\bigr) = +1\); hence \(p\) is represented by the form \(y^2 + 2x^2\):
  since \(\mathbb{Z}[\sqrt{-2}]\) is norm-Euclidean, \(p\) splits as \(\pi\bar\pi\) and the
  representation \(p = y^2 + 2x^2\) is unique up to the four sign choices \((\pm x, \pm y)\)
  (units of \(\mathbb{Z}[\sqrt{-2}]\) are \(\pm 1\)); both \(x, y \ne 0\). Thus
  **\(\#\{(x,y) \in \mathbb{Z}^2 : 2x^2 + y^2 = p\} = 4\) exactly.** [PROVED–CLASSICAL]
- The model \(y^2 = x^3 - p^2x\) is globally minimal (\(v_2(\Delta) = 6 < 12\),
  \(v_p(\Delta) = 6 < 12\)).

**Lemma 0 (torsion).** \(E_p(\mathbb{Q})_{\mathrm{tors}} = \{O,(0,0),(\pm p,0)\} \cong (\mathbb{Z}/2)^2\).

*Proof.* For any good odd prime \(\ell \equiv 3 \pmod 4\), the cubic \(f(x) = x^3 - p^2x\) is an odd
function, and \(\chi(-1) = -1\) for the quadratic character \(\chi\) of \(\mathbb{F}_\ell\); pairing
\(x \leftrightarrow -x\) gives \(\sum_{x \in \mathbb{F}_\ell} \chi(f(x)) = 0\), so
\(\#E_p(\mathbb{F}_\ell) = \ell + 1\) (supersingular count). Reduction mod good \(\ell\) is injective
on prime-to-\(\ell\) torsion [PROVED–CITED: Silverman AEC VII.3.1]. If an odd prime \(q\) divided
\(\#E_p(\mathbb{Q})_{\mathrm{tors}}\), choose (Dirichlet) a good prime \(\ell \equiv 3 \pmod 4\) with
\(\ell \equiv 1 \pmod q\); then \(q \mid \ell + 1 \equiv 2 \pmod q\), absurd. For the 2-part, choose
a good prime \(\ell \equiv 3 \pmod 8\); then \(\ell + 1 \equiv 4 \pmod 8\), so the 2-primary torsion
divides 4; it contains the full 2-torsion \((\mathbb{Z}/2)^2\), hence equals it. \(\blacksquare\)

### 1. Proof of Theorem A

**Setup (complete 2-descent; formalism cited, all content executed here).** \(E_p\) has full
rational 2-torsion with \(e_1 = 0\), \(e_2 = p\), \(e_3 = -p\). The complete 2-descent map

\[
\varphi:\; E_p(\mathbb{Q})/2E_p(\mathbb{Q}) \;\hookrightarrow\; \frac{\mathbb{Q}^*}{(\mathbb{Q}^*)^2} \times \frac{\mathbb{Q}^*}{(\mathbb{Q}^*)^2},
\qquad
(x,y) \mapsto (x,\; x-p) \quad (y \ne 0),
\]

with the standard convention at 2-torsion points, is an **injective group homomorphism**
[PROVED–CITED: Silverman AEC, Prop. X.1.4]. The images of the 2-torsion points are computed
directly from the convention:

\[
T \;=\; \varphi(E_p(\mathbb{Q})_{\mathrm{tors}}) \;=\; \{(1,1),\; (-1,-p),\; (p,2),\; (-p,-2p)\} \pmod{\text{squares}} .
\]

For a class \((b_1, b_2)\) with \(b_1, b_2\) squarefree, membership in the everywhere-locally-solvable
group is read off the **homogeneous space** (projective, coordinates \((Z_1{:}Z_2{:}Z_3{:}D)\)):

\[
C_{b_1,b_2}:\qquad
b_1Z_1^2 - b_2Z_2^2 = p\,D^2,
\qquad
b_1Z_1^2 - b_3Z_3^2 = -p\,D^2,
\]

where \(b_3\) is the squarefree part of \(b_1b_2\). The 2-Selmer group is identified with the set of
classes \((b_1,b_2)\) for which \(C_{b_1,b_2}\) has points in \(\mathbb{R}\) and in every
\(\mathbb{Q}_q\); it contains \(\varphi(E_p(\mathbb{Q})/2E_p(\mathbb{Q}))\), and the quotient is
\(\Sha(E_p)[2]\) [PROVED–CITED: standard complete 2-descent, Silverman AEC §X.4; Stoll,
*Descent on elliptic curves*]. If \(P = (x,y)\), \(y \neq 0\), has \(\varphi(P) = (b_1,b_2)\), then
writing \(x = b_1z_1^2\), \(x - p = b_2z_2^2\) and \(x + p = y^2/(x(x-p)) = b_1b_2\,z_3^2\) exhibits a
rational point on \(C_{b_1,b_2}\) with \(D = 1\); this is the only direction of the dictionary we
use for global points, and it is proved by this one line.

**Step 1 (support).** *If \(C_{b_1,b_2}(\mathbb{Q}_q) \neq \emptyset\) for a prime \(q \nmid 2p\),
then \(q \nmid b_1b_2b_3\).* Consequently every Selmer class satisfies
\(b_1 \in \{\pm1, \pm2, \pm p, \pm 2p\}\), \(b_2 \in \{\pm1,\pm2,\pm p,\pm 2p\}\).

*Proof.* Since \(b_3 \sim b_1 b_2\) modulo squares, \(q\) divides exactly zero or two of
\(b_1, b_2, b_3\). Suppose two, and take a primitive solution
\((Z_1,Z_2,Z_3,D) \in \mathbb{Z}_q^4\) (not all in \(q\mathbb{Z}_q\)). Subtracting the two defining
equations gives the third relation \(b_3Z_3^2 - b_2Z_2^2 = 2pD^2\).

- *Case \(q \mid b_1, b_3\) (so \(q \nmid b_2\)):* equation 2 gives
  \(0 \equiv -pD^2 \pmod q\), so \(q \mid D\); equation 1 mod \(q\) gives \(q \mid b_2Z_2^2\), so
  \(q \mid Z_2\); then equation 1 mod \(q^2\) gives \(v_q(b_1Z_1^2) = 1 + 2v_q(Z_1) \ge 2\), so
  \(q \mid Z_1\); then equation 2 mod \(q^2\) gives \(1 + 2v_q(Z_3) \ge 2\), so \(q \mid Z_3\) —
  contradicting primitivity.
- *Case \(q \mid b_2, b_3\) (so \(q \nmid b_1\)):* the third relation gives \(0 \equiv 2pD^2\), so
  \(q \mid D\); equation 1 mod \(q\) gives \(q \mid b_1 Z_1^2\), so \(q \mid Z_1\); equations 1 and 2
  mod \(q^2\) then force \(q \mid Z_2\) and \(q \mid Z_3\) as above — contradiction.
- *Case \(q \mid b_1, b_2\) (so \(q \nmid b_3\)):* equation 1 gives \(0 \equiv pD^2\), so
  \(q \mid D\); equation 2 mod \(q\) gives \(q \mid b_3Z_3^2\), so \(q \mid Z_3\); equation 2 mod
  \(q^2\) gives \(q \mid Z_1\); equation 1 mod \(q^2\) gives \(q \mid Z_2\) — contradiction.
  \(\blacksquare\)

**Step 2 (coset reduction).** Let \(G\) be the group of classes allowed by Step 1
(\(|G| = 4 \times 8 = 32\)). \(T \le G\) has index 8, and since the only element of \(T\) with
trivial first coordinate is \((1,1)\), **the eight classes \((1, b)\), \(b \in \{\pm1,\pm2,\pm p,\pm2p\},\)
are a complete set of coset representatives of \(T\) in \(G\)**. Both
\(\varphi(E_p(\mathbb{Q})/2E_p(\mathbb{Q}))\) and \(\operatorname{Sel}_2\) are subgroups of \(G\)
containing \(T\); hence if either is strictly larger than \(T\), it contains \((1,b)\) for some
\(b \neq 1\), whose homogeneous space

\[
C_b:\qquad Z_1^2 - b\,Z_2^2 = p\,D^2, \qquad Z_1^2 - b\,Z_3^2 = -p\,D^2
\]

is then solvable in every completion of \(\mathbb{Q}\) (for \(\operatorname{Sel}_2\)), respectively
in \(\mathbb{Q}\) itself (for a global point, by the one-line dictionary above). It therefore
suffices to eliminate the **seven** spaces \(C_b\), \(b \in \{-1, \pm2, \pm p, \pm 2p\}\), each at a
single place.

**Step 3 (elimination at \(\infty\)): \(b \in \{-1,-2,-p,-2p\}\).** The second equation reads
\(Z_1^2 + |b|Z_3^2 + pD^2 = 0\) over \(\mathbb{R}\), forcing \(Z_1 = Z_3 = D = 0\); the first
equation then forces \(Z_2 = 0\). No real projective point. \(\square\)

**Step 4 (elimination at \(p\)): \(b \in \{2, p, 2p\}\).** Take a primitive
\(\mathbb{Z}_p\)-solution.

- **\(b = 2\):** mod \(p\): \(Z_1^2 \equiv 2Z_2^2\) and \(Z_1^2 \equiv 2Z_3^2\). If
  \(p \nmid Z_1\) then \(2\) is a QR mod \(p\), contradicting (QR2). So \(p \mid Z_1\), whence
  \(p \mid Z_2, Z_3\), whence \(p^2 \mid Z_1^2 - 2Z_2^2 = pD^2\), so \(p \mid D\) —
  contradiction with primitivity. \(\square\)
- **\(b = p\):** \(p \mid Z_1^2\), write \(Z_1 = pW\): the system becomes
  \(pW^2 - Z_2^2 = D^2\), \(pW^2 - Z_3^2 = -D^2\). The first gives
  \(Z_2^2 + D^2 \equiv 0 \pmod p\), so \(p \mid Z_2, D\) by (QR1); then
  \(pW^2 = Z_2^2 + D^2 \equiv 0 \pmod{p^2}\) forces \(p \mid W\); then
  \(Z_3^2 = pW^2 + D^2 \equiv 0 \pmod{p^2}\) forces \(p \mid Z_3\). All of
  \(Z_1, Z_2, Z_3, D\) divisible by \(p\) — contradiction. \(\square\)
- **\(b = 2p\):** \(p \mid Z_1\), write \(Z_1 = pW\): \(pW^2 - 2Z_2^2 = D^2\),
  \(pW^2 - 2Z_3^2 = -D^2\). The second gives \(D^2 \equiv 2Z_3^2 \pmod p\); if \(p \nmid Z_3\),
  \(2\) is a QR mod \(p\), contradicting (QR2). So \(p \mid Z_3\), then \(p \mid D\), then (first
  equation) \(p \mid Z_2\), then \(pW^2 = D^2 + 2Z_2^2 \equiv 0 \pmod {p^2}\) gives \(p \mid W\) —
  contradiction. \(\square\)

**Step 5 (conclusion).** No \(C_b\) has points everywhere locally, so
\(\operatorname{Sel}_2(E_p) = T \cong (\mathbb{Z}/2)^2\). Since
\(\varphi\) is injective, \(2^{\operatorname{rank}} \cdot \#E_p(\mathbb{Q})[2] =
\#\bigl(E_p(\mathbb{Q})/2E_p(\mathbb{Q})\bigr) \le \#\operatorname{Sel}_2 = 4\) with
\(\#E_p(\mathbb{Q})[2] = 4\), forcing \(\operatorname{rank} = 0\); with Lemma 0,
\(E_p(\mathbb{Q}) \cong (\mathbb{Z}/2)^2\) exactly. The exact sequence
\(0 \to E_p(\mathbb{Q})/2E_p(\mathbb{Q}) \to \operatorname{Sel}_2 \to \Sha[2] \to 0\) gives
\(\#\Sha[2] = 4/4 = 1\). If \(\Sha\) is finite and had even order it would contain an element of
order 2; hence \(\#\Sha\) is odd. Finally, a rational right triangle of area \(p\) yields a point
of \(E_p(\mathbb{Q})\) with \(y \ne 0\) (the classical dictionary, written out in REPORT.md §5),
and all four points of \(E_p(\mathbb{Q})\) have \(y = 0\) or are \(O\); so \(p\) is not congruent.
\(\blacksquare\)

*Remark.* All seven eliminations happen at the two bad places \(\infty\) and \(p\); the machine
cross-check (`ellrank` \(= [0,0,0,[\,]]\) for 311 primes) confirms rank exactly 0 independently.

### 2. Proof of Theorem B

Write \(B = \#\{(x,y,z): p = 2x^2 + y^2 + 8z^2\}\), \(A = \#\{(x,y,z): p = 2x^2+y^2+32z^2\}\), so
\(a_p = A - B/2\).

**Step 1 (no zero coordinates except \(z\)).** In any solution of \(p = 2x^2+y^2+8z^2\): \(y\) is
odd (parity), and \(x \neq 0\) — else \(p = y^2 + 8z^2 \equiv 1 \pmod 8\), contradicting
\(p \equiv 3 \pmod 8\). (Same for the form with \(32z^2\).)

**Step 2 (orbit counting mod 8).** The sign group \(\{\pm1\}^3\) acts on solutions. By Step 1,
every solution with \(z \ne 0\) has all coordinates nonzero, so its orbit has size exactly 8:

\[
B_{z\,\mathrm{odd}} \equiv 0 \pmod 8, \qquad B_{z\,\mathrm{even},\, z\neq0} \equiv 0 \pmod 8 .
\]

The \(z = 0\) stratum is \(B_0 = \#\{(x,y): 2x^2+y^2 = p\} = 4\) by (QR3). Hence
\(B_{z\,\mathrm{even}} = B_0 + B_{z\,\mathrm{even}, z\ne0} \equiv 4 \pmod 8\).

**Step 3 (the 32-form counts the even-\(z\) stratum).** \((x,y,w) \mapsto (x,y,2w)\) is a bijection
from solutions of \(p = 2x^2+y^2+32w^2\) onto solutions of \(p = 2x^2+y^2+8z^2\) with \(z\) even.
So \(A = B_{z\,\mathrm{even}}\) and

\[
a_p \;=\; A - \tfrac{B}{2}
\;=\; \frac{B_{z\,\mathrm{even}} - B_{z\,\mathrm{odd}}}{2}
\;\equiv\; \frac{4 - 0}{2} \;=\; 2 \pmod 4 . \qquad\blacksquare
\]

**Step 4 (analytic consequences).** Tunnell's theorem [PROVED–CITED: Tunnell 1983; exposition in
Koblitz GTM 97] states, for odd squarefree \(n\):
\(L(E_n,1) = \beta\, a_n^2/(4\sqrt n)\). With \(|a_p| \ge 2\) from \(a_p \equiv 2 \pmod 4\):

\[
L(E_p,1) \;=\; \frac{\beta\,a_p^2}{4\sqrt p} \;\ge\; \frac{\beta}{\sqrt p} \;>\; 0 .
\qquad\blacksquare
\]

(The identity, including the constant \(\beta\), is verified below to 38 decimal digits at 19
primes with \(a_p \in \{\pm2, \pm6, 10, -14, 18\}\) — strong protection against misquotation.)

### 3. Proof of Corollary C

(1) is Theorem A(1) + Theorem B. (2): the BSD-normalized quantities of \(E_p\) are:
\(\Omega_{E_p} = 2\beta/\sqrt p\) — substituting \(x = pu\), \(y = p^{3/2}v\) into the minimal model
maps \(E_p\) to \(v^2 = u^3 - u\) and scales \(dx/2y\) by \(p^{-1/2}\); each of the two real
components contributes \(\beta/\sqrt p\); \(c_p = 4\) — Tate's algorithm: \(v_p(c_4) = 2\),
\(v_p(\Delta) = 6\) give Kodaira type I\(_0^*\), and the residual cubic \(x^3 - x\) splits over
\(\mathbb{F}_p\), so all four components are rational [PROVED–CITED: Tate's algorithm; certified by
`elllocalred`]; \(c_2 = 2\), type III with conductor exponent 5 — computed exactly by
`elllocalred` for \(p = 3\), and valid for every \(p \equiv 3 \pmod 8\) because \(p/3 \equiv 1
\pmod 8\) is a square in \(\mathbb{Z}_2^\times\), making \(E_p\) and \(E_3\) isomorphic over
\(\mathbb{Q}_2\) (a quadratic twist by a 2-adic square), and Tamagawa numbers are local invariants;
torsion order 4 (Lemma 0); \(\mathrm{Reg} = 1\) (rank 0). So the BSD II right-hand side equals
\(\#\Sha \cdot (2\beta/\sqrt p)\cdot 8/16 = \#\Sha\,\beta/\sqrt p\), while Tunnell gives
\(L = (a_p/2)^2 \beta/\sqrt p\): BSD II \(\Leftrightarrow \#\Sha = (a_p/2)^2\), an odd perfect
square by Theorem B. (3): Rubin's theorem (CM curves with \(L(E,1) \neq 0\) have finite \(\Sha\))
applies to \(E_p\) (CM by \(\mathbb{Z}[i]\)) [PROVED–CITED: Rubin 1987]; Theorem A(3) gives
\(\Sha[2^\infty] = \Sha[2] = 0\), so \(v_2(\#\Sha) = 0 = v_2((a_p/2)^2)\): the 2-adic valuations of
the two sides of the strong BSD formula agree. \(\blacksquare\)

### 4. Machine transcript

Environment: PARI/GP 2.15.4 (`pari-gp`, `pari-elldata` Debian packages, already installed;
`elldata` = Cremona database). Commands executed in this session:

```bash
cd /workspace/research/conjectures/03-bsd
gp -q -s 2000000000 breakthrough.gp | tee breakthrough.out
```

Full output (verbatim; total computation time just under 10 seconds):

```text
beta = Int_1^oo dx/sqrt(x^3-x) = 2.622057554292119810464839590

PART 1: Tunnell scan to X = 1000000   (qfrep: 2467 ms)
  primes p = 3 (mod 8), p <= 10^6 : 19653
  violations of  a_p = 2 (mod 4)  : 0
  violations of  #{2x^2+y^2=p}=4  : 0
  BSD-predicted #Sha = (a_p/2)^2, first occurrences:
    #Sha = 1  count 2343  first p = 3
    #Sha = 9  count 2365  first p = 43
    #Sha = 25  count 2090  first p = 307
    #Sha = 49  count 1953  first p = 467
    #Sha = 81  count 1742  first p = 907
    #Sha = 121  count 1356  first p = 4547
    #Sha = 169  count 1239  first p = 2707
    #Sha = 225  count 1155  first p = 8147
  (scan: 22 ms)

PART 2: ellrank(E_p) = [0,0,0,[]] (rank exactly 0) for all 311 primes p = 3 (mod 8), p <= 10^4;  failures: 0   (252 ms)

PART 3: family table (E_p : y^2 = x^3 - p^2 x)
    p    a_p   L(E_p,1)        beta*a_p^2/(4 sqrt p)   implied #Sha   (a_p/2)^2  c_2  c_p  kod_2 kod_p
      3     2   1.51384563480   1.51384563480    1.00000000000      1      2    4    3    -1
     11    -2   0.790580098755   0.790580098755    1.00000000000      1      2    4    3    -1
     19    -2   0.601541258069   0.601541258069    1.00000000000      1      2    4    3    -1
     43     6   3.59874025523   3.59874025523    9.00000000000      9      2    4    3    -1
     59     2   0.341362817522   0.341362817522    1.00000000000      1      2    4    3    -1
     67    -2   0.320335314478   0.320335314478    1.00000000000      1      2    4    3    -1
     83     2   0.287808207097   0.287808207097    1.00000000000      1      2    4    3    -1
    107    -6   2.28135484270   2.28135484270    9.00000000000      9      2    4    3    -1
    131     6   2.06181208979   2.06181208979    9.00000000000      9      2    4    3    -1
    139     2   0.222400019053   0.222400019053    1.00000000000      1      2    4    3    -1
    163     6   1.84837858188   1.84837858188    9.00000000000      9      2    4    3    -1
    179    -2   0.195981783129   0.195981783129    1.00000000000      1      2    4    3    -1
    211     2   0.180509886274   0.180509886274    1.00000000000      1      2    4    3    -1
    227    -2   0.174032072314   0.174032072314    1.00000000000      1      2    4    3    -1
    251    -6   1.48952524758   1.48952524758    9.00000000000      9      2    4    3    -1
    283    -6   1.40278628750   1.40278628750    9.00000000000      9      2    4    3    -1
    307    10   3.74121822391   3.74121822391    25.0000000000     25      2    4    3    -1
    467   -14   5.94538331483   5.94538331483    49.0000000000     49      2    4    3    -1
    907    18   7.05218335940   7.05218335940    81.0000000000     81      2    4    3    -1
  max |L - Tunnell|             = 2.350988701644575016 E-38
  max |impliedSha - (a_p/2)^2|  = 4.701977403289150032 E-38
  max |omega1*sqrt(p)/beta - 1| = 5.877471754111437540 E-39
  (kod codes: 3 = III at 2;  -1 = I0* at p)      (65 ms)

PART 4: Cremona sweep, all curves 11 <= N <= 500      (7148 ms)
  curves checked                    : 2214
  worst |impliedSha - integer|      : 3.043942621454313502 E-35
  non-square rounded Sha            : 0
  analytic rank outside descent box : 0
  curves where 2-descent + Cassels pairing cannot close the rank: 2  ["210e7", "210e8"]
  curves with implied #Sha > 1      : 34
    66b3  rank_an=0  #Sha_an=4
    102b5  rank_an=0  #Sha_an=4
    114c3  rank_an=0  #Sha_an=4
    120a5  rank_an=0  #Sha_an=4
    130b3  rank_an=0  #Sha_an=4
    182b3  rank_an=0  #Sha_an=9
    195a7  rank_an=0  #Sha_an=4
    210c5  rank_an=0  #Sha_an=4
    210e5  rank_an=0  #Sha_an=4
    210e7  rank_an=0  #Sha_an=16
    210e8  rank_an=0  #Sha_an=16
    240d3  rank_an=0  #Sha_an=4
    258d3  rank_an=0  #Sha_an=4
    275b3  rank_an=0  #Sha_an=25
    294c3  rank_an=0  #Sha_an=4
    300b2  rank_an=0  #Sha_an=9
    312c3  rank_an=0  #Sha_an=4
    330b6  rank_an=0  #Sha_an=4
    330c6  rank_an=0  #Sha_an=4
    330d3  rank_an=0  #Sha_an=4
    336d3  rank_an=0  #Sha_an=4
    378a3  rank_an=0  #Sha_an=9
    390b5  rank_an=0  #Sha_an=4
    410b3  rank_an=0  #Sha_an=4
    435d3  rank_an=0  #Sha_an=4
    438e2  rank_an=0  #Sha_an=4
    442a2  rank_an=0  #Sha_an=4
    442d2  rank_an=0  #Sha_an=4
    448c5  rank_an=0  #Sha_an=9
    448c6  rank_an=0  #Sha_an=9
    462f3  rank_an=0  #Sha_an=4
    475a3  rank_an=0  #Sha_an=9
    480b2  rank_an=0  #Sha_an=4
    480h2  rank_an=0  #Sha_an=4

TOTAL computation time: 9954 ms
```

Reading notes on the transcript:

- **Part 1 is exact integer arithmetic** (`qfrep` lattice-point counts): the two congruences of
  Theorem B's proof (\(a_p \equiv 2 \bmod 4\) and \(B_0 = 4\)) hold with zero exceptions over all
  19,653 primes to \(10^6\). The observed \((a_p/2)^2\) values are all odd perfect squares — the
  family's "Sha-meter": Tunnell counting predicts \(\#\Sha(E_{43}) = 9\), \(\#\Sha(E_{307}) = 25\),
  \(\#\Sha(E_{467}) = 49\), \(\#\Sha(E_{907}) = 81\), each confirmed against the L-value in Part 3
  to 38 digits. These are falsifiable predictions of strong BSD, and they pass.
- **Part 2** uses PARI's `ellrank` (2-descent plus the 2-part of the Cassels pairing); the output
  \([0,0,0,[\,]]\) certifies rank exactly 0 — an independent machine re-derivation of Theorem A's
  conclusion for 311 primes.
- **Part 3** confirms the full constellation of Corollary C: the Tunnell constant, the period
  \(\Omega = 2\beta/\sqrt p\) (via \(\omega_1\sqrt p/\beta = 1\) to 39 digits), and the uniform
  local data \(c_2 = 2\) (type III), \(c_p = 4\) (type I\(_0^*\)).
- **Part 4** extends Wave 1's six-curve table to all 2,214 Cremona curves of conductor \(\le 500\):
  implied \(\#\Sha\) is an integer to 35 digits and a perfect square in every single case, and the
  analytic rank always lies in the descent window. The only two curves where the machine's
  2-descent cannot close the rank gap (210e7, 210e8, both \(\#\Sha_{\mathrm{an}} = 16\)) are
  exactly those with 4-torsion in \(\Sha\) — the documented intrinsic limit of the method, and a
  micro-illustration of the report's One-Class Barrier: even computationally, nontrivial \(\Sha\)
  is what blocks descent.

Wave-1's script ([`verification.gp`](./verification.gp)) remains reproducible; this session's new
files are [`breakthrough.gp`](./breakthrough.gp) and [`breakthrough.out`](./breakthrough.out).

---

## What is new vs REPORT.md

| Item | Wave 1 (REPORT.md) | Wave 2 (this file) |
|---|---|---|
| Rank-0 theorem, algebraic side | One curve: \(y^2 = x^3 - x\) (Fermat descent, \(N=1\)) | **Infinite family** \(p \equiv 3 \pmod 8\): full \(\operatorname{Sel}_2 \cong (\mathbb{Z}/2)^2\) via seven homogeneous-space eliminations, all written out |
| \(\Sha\) control | None proved (cited only) | **\(\Sha(E_p)[2] = 0\) proved** for the whole family; hence \(\#\Sha\) odd (given finiteness, cited) |
| Analytic side | Floating-point: \(L(E,1) = 0.6555\ldots \neq 0\) for single curves | **Theorem:** \(a_p \equiv 2 \pmod 4\) (elementary counting), hence \(L(E_p,1) \ge \beta/\sqrt p > 0\) for the family — nonvanishing with an **effective lower bound**, no numerics in the proof |
| BSD I status delivered | One curve (plus cited results) | **Proved for an infinite family**, both sides unconditional; equivalently, an elementary reproof of Genocchi's theorem upgraded to full BSD I |
| BSD II | Consistency numerics | **2-part of BSD II proved** for the family (\(v_2\) of both sides \(= 0\), using Rubin's finiteness); exact reduction of BSD II to \(\#\Sha = (a_p/2)^2\) |
| Verification scale | 6 Cremona curves + 7 congruent-number curves | **2,214 Cremona curves** (\(N \le 500\)), 19-prime family table exact to \(10^{-38}\), **19,653-prime** integer scan; new confirmed \(\Sha\) predictions 9, 25, 49, 81 from pure lattice-point counting |
| New structural observation | One-Class Barrier (methods analysis) | The Tunnell count as a **Sha-meter** for the family (\(|a_p| = 2\sqrt{\#\Sha_{\mathrm{an}}}\)), verified; descent obstruction at \(\Sha[4] \neq 0\) exhibited concretely (210e7/210e8) |

Nothing in Wave 1 is retracted; the One-Class Barrier analysis (REPORT §4–6) stands and is
illustrated, not breached, by these results.

## Why full BSD remains open

Everything proved here lives strictly inside the rank-0 regime, on the "easy" side of the wall
mapped in REPORT.md:

1. **The family has analytic rank 0 by construction.** Theorems A and B together prove
   0 = 0. The methods — 2-descent with quadratic-residue eliminations, and theta-series counting
   through Tunnell/Waldspurger — are exactly the "one distinguished class / one special value"
   toolkit. Neither can see a first derivative, let alone a second. No statement about any curve
   of analytic rank \(\ge 1\) follows, and the rank \(\ge 2\) wall (no exact archimedean formula
   for \(L''\), no core-rank-2 Euler system, no unconditional \(\Sha\) finiteness) is untouched.
2. **\(\Sha[2] = 0\) is not \(\Sha = 0\).** Our descent kills only the 2-part. The full finiteness
   of \(\Sha(E_p)\) used in Corollary C(3) is Rubin's deep CM theorem, not elementary; and the full
   BSD II for the family — \(\#\Sha = (a_p/2)^2\) exactly, at every prime — would require the CM
   Iwasawa-theoretic machinery (Rubin's main conjecture and its refinements) at all odd primes,
   including the delicate ones. The transcript's 38-digit agreements are consistency at finite
   precision, not proof.
3. **Congruent-number BSD is only half-done even as a family statement.** For \(p \equiv 5, 7
   \pmod 8\) the sign is \(-1\), the rank is conjectured (and in part proved — Monsky's rank-1
   results, Tian's induction, Smith's \(2^\infty\)-Selmer work) to be 1, and the full "every
   \(n \equiv 5,6,7 \pmod 8\) is congruent" remains open precisely because it needs BSD-type
   input at rank 1 across a family — already at the boundary of the Gross–Zagier–Kolyvagin regime.
4. **The general conjecture requires what no method provides:** rank equality plus \(\Sha\)
   finiteness for *all* curves, including analytic rank \(\ge 2\), where every existing engine is
   provably silent (REPORT §4, Claim B). This file adds evidence and a clean solved province; it
   does not move that frontier.

## Honesty label

Using the label system of REPORT.md:

- **Theorem A** — [PROVED–HERE; CLASSICAL CONTENT]. Complete proof above; the only cited inputs
  are the standard complete-2-descent formalism (Silverman AEC X.1.4, §X.4; Stoll's descent notes)
  and reduction-injectivity of torsion (Silverman VII.3.1). The result itself is classical:
  the non-congruence of \(p \equiv 3 \pmod 8\) is Genocchi (1855); 2-Selmer computations for
  congruent-number curves of this shape appear (in stronger and more general forms) in work of
  Heath-Brown, Monsky, Serf, Feng, and others. **No priority is claimed.**
- **Theorem B** — [PROVED–HERE modulo one citation; CLASSICAL CONTENT]. The mod-4 counting
  argument (Steps 1–3) is complete and elementary; the bridge to \(L(E_p,1)\) is Tunnell's theorem
  [PROVED–CITED: Tunnell, Invent. Math. 72 (1983); exposition Koblitz GTM 97]. Nonvanishing of
  \(L(E_p,1)\) for \(p \equiv 3 \pmod 8\) is likewise known to experts (it also follows from
  Genocchi + the Coates–Wiles/Rubin CM equivalences, and 2-adic valuation refinements exist in
  the literature, e.g. C. Zhao's and later work); the value of this section is a self-contained
  elementary proof. **No priority is claimed.**
- **Corollary C** — parts (1), (2): follow from A + B with local computations proved or certified
  above [PROVED–HERE given the cited descent formalism and Tunnell]. Part (3): uses Rubin (1987)
  for finiteness of \(\Sha\) [PROVED–CITED]; given that, the 2-part statement is proved here.
  For this CM family, substantially stronger BSD II results (full \(p\)-parts at odd primes, and
  recently more) are known via CM Iwasawa theory (Rubin; Burungale–Tian and successors) — our
  contribution is elementary method and complete auditability, not strength.
- **Computational Theorem D** — [COMPUTED]. Part 1 is exact integer arithmetic (a finite theorem,
  machine-proved). Parts 2–4 are certified descent (Part 2) and high-precision floating point with
  PARI's rigorous error management (Parts 3–4): consistency checks, not proofs, except where
  integrality/nonvanishing at the stated precision is the only thing used. PARI's `ellrank` class-
  and unit-group steps may assume GRH internally; our hand proof of Theorem A is unconditional and
  independent of this.
- **No fake full BSD.** Nothing here proves BSD for any curve of analytic rank \(\ge 1\), proves
  finiteness of \(\Sha\) for any new curve, or weakens the rank-2 wall. The claim is exactly:
  *BSD I, plus \(\Sha[2] = 0\), plus the 2-part of BSD II, proved for the infinite family
  \(E_p,\ p \equiv 3 \pmod 8\), by elementary and fully checkable means, with large-scale machine
  corroboration.*

**Additional references (delta to REPORT.md §7).**
- A. Genocchi, *Note analitiche sopra tre scritti inediti di Leonardo Pisano*, Ann. Sci. Mat. Fis. 6 (1855) — non-congruence of primes \(p \equiv 3 \pmod 8\).
- J. Tunnell, *A classical Diophantine problem and modular forms of weight 3/2*, Invent. Math. 72 (1983).
- N. Koblitz, *Introduction to Elliptic Curves and Modular Forms*, 2nd ed., Springer GTM 97 (1993).
- J. Silverman, *The Arithmetic of Elliptic Curves*, 2nd ed., Springer GTM 106 (2009), Prop. X.1.4, §X.4, Prop. VII.3.1.
- M. Stoll, *Descent on elliptic curves*, lecture notes (arXiv:math/0611694).
- D. R. Heath-Brown, *The size of Selmer groups for the congruent number problem* I, II, Invent. Math. 111 (1993), 118 (1994).
- P. Monsky, *Mock Heegner points and congruent numbers*, Math. Z. 204 (1990).
- K. Feng, *Non-congruent numbers, odd graphs and the Birch–Swinnerton-Dyer conjecture*, Acta Arith. 75 (1996).
- C. Zhao, *A criterion for elliptic curves with lowest 2-power in L(1)*, Math. Proc. Cambridge Philos. Soc. 121 (1997).
- Y. Tian, *Congruent numbers and Heegner points*, Camb. J. Math. 2 (2014).
- A. Burungale, Y. Tian, *p-converse to a theorem of Gross–Zagier, Kolyvagin and Rubin*, Invent. Math. 220 (2020).
- K. Rubin, *Tate–Shafarevich groups and L-functions of elliptic curves with complex multiplication*, Invent. Math. 89 (1987).

---

*Legion 03, Wave 2, end of file. Files written this wave: `BREAKTHROUGH.md` (this file),
`breakthrough.gp` (executed script), `breakthrough.out` (verbatim transcript). No website files
touched; no git operations performed.*
