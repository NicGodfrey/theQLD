# Hodge classes on a product of two curves, via correspondences

*Original-theory note. The statement is classical (a surface, so it also follows from Lefschetz (1,1)). The proof below does not quote Lefschetz (1,1): it builds the cycle from a Hodge morphism of Jacobians. No survey.*

**Honesty.** `[PROVED HERE as a correspondence construction]` — the theorem is known; the value is a complete cycle-producing argument.

---

## Theorem

Let \(C,D\) be smooth irreducible projective curves over \(\mathbb{C}\). Let \(X=C\times D\). Write \(H^1(-)=H^1(-,\mathbb{Q})\) and use the Künneth decomposition
\[
H^2(X,\mathbb{Q})\;=\;H^2(C)\oplus H^2(D)\oplus\bigl(H^1(C)\otimes H^1(D)\bigr).
\]
The summands \(H^2(C)\) and \(H^2(D)\) are spanned by the classes of a fibre \(\{pt\}\times D\) and a fibre \(C\times\{pt\}\), hence are algebraic. Every rational Hodge class in the cross term,
\[
\xi\;\in\;\bigl(H^1(C)\otimes H^1(D)\bigr)\cap H^{1,1}(X),
\]
is the class of a \(\mathbb{Q}\)-linear combination of graphs of correspondences \(C\to D\). Equivalently: \(\xi\) is algebraic.

---

## Proof

### 1. Type of a Hodge class in the cross term

On a curve, \(H^1(\mathbb{C})=H^{1,0}\oplus H^{0,1}\). A pure tensor of types \((p,q)\) and \((r,s)\) has type \((p+r,q+s)\) on \(X\). Thus
\[
\bigl(H^1(C)\otimes H^1(D)\bigr)_{\mathbb{C}}\cap H^{1,1}(X)
\;=\;
H^{1,0}(C)\otimes H^{0,1}(D)\;\oplus\;H^{0,1}(C)\otimes H^{1,0}(D).
\]
So a rational class \(\xi\) in the cross term is Hodge of type \((1,1)\) if and only if its complexification lies in that sum of two tensorands.

### 2. \(\xi\) as a map of Hodge structures

Identify \(H^1(C)^\vee\simeq H_1(C,\mathbb{Q})\). The tensor \(\xi\) is a \(\mathbb{Q}\)-linear map
\[
u_\xi:\;H^1(C)\;\longrightarrow\;H^1(D),\qquad
\alpha\;\longmapsto\;\langle\xi,\,\alpha\otimes-\rangle
\]
(up to the standard Poincaré duality identification on \(C\), which is a morphism of Hodge structures of type \((1,1)\)). The type computation of §1 says precisely that \(u_\xi\) sends \(H^{1,0}(C)\) into \(H^{1,0}(D)\) and \(H^{0,1}(C)\) into \(H^{0,1}(D)\). Hence \(u_\xi\) is a morphism of rational Hodge structures of weight \(1\).

### 3. Morphisms of weight-\(1\) Hodge structures are morphisms of Jacobians

Let \(J(C)=H^{0,1}(C)^\vee/H_1(C,\mathbb{Z})\) be the Jacobian (a principally polarised abelian variety). A morphism of polarisable weight-\(1\) Hodge structures \(H^1(C)\to H^1(D)\) is, after clearing a denominator, induced by a homomorphism of complex tori: it is \(\mathbb{C}\)-linear on \(H^{0,1}\), maps the lattice \(H_1(C,\mathbb{Z})\) into \(H_1(D,\mathbb{Q})\), and therefore, after multiplying by an integer \(m\ge 1\), induces a holomorphic group homomorphism
\[
f:\;J(C)\;\longrightarrow\;J(D).
\]
(This is the definition of \(\mathrm{Hom}(J(C),J(D))\otimes\mathbb{Q}\simeq\mathrm{Hom}_{\mathrm{HS}}(H^1(C),H^1(D))\).) Thus \(m\,u_\xi=f^*\).

### 4. The correspondence

Fix base points \(c_0\in C\), \(d_0\in D\), and let
\[
\alpha_C:C\to J(C),\qquad p\mapsto\bigl[\mathcal{O}(p-c_0)\bigr]
\]
be the Abel–Jacobi embedding, and likewise \(\alpha_D:D\to J(D)\). Let \(\Gamma_f\subset J(C)\times J(D)\) be the graph of \(f\), an algebraic cycle of codimension \(\dim J(D)\). Let \(\Theta_D\) be a theta divisor on \(J(D)\) (the image of \(D^{g_D-1}\) under Abel–Jacobi). The Poincaré class
\[
\mathfrak{p}_D\;=\;\bigl[\mathrm{pr}_1^*\Theta_D+\mathrm{pr}_2^*\Theta_D-\mathrm{m}^*\Theta_D\bigr]
\;\in\;H^{1,1}\bigl(J(D)\times J(D)\bigr)
\]
is algebraic, and is a polarisation of \(H_1(D)\). Pull back along
\[
\alpha_C\times\alpha_D:\;C\times D\;\longrightarrow\;J(C)\times J(D)
\]
the cycle \((\mathrm{id}\times f)^*(\Delta_{J(D)})\) translated into a divisor via \(\mathfrak{p}_D\):
\[
Z_f\;:=\;(\alpha_C\times\alpha_D)^*\bigl((\mathrm{id}\times f)^*\mathfrak{p}_D\bigr)
\;\subset\;C\times D.
\]
This is an algebraic divisor on \(X\). By construction, the Künneth cross-component of \([Z_f]\) is the class corresponding to \(f^*\), i.e. to \(m\,u_\xi\). Therefore
\[
\xi\;=\;\frac1m\,[Z_f]_{\mathrm{cross}}
\]
in \(H^1(C)\otimes H^1(D)\). Adding a rational combination of the two fibre classes (already algebraic) realises the full class of \(\xi\) in \(H^2(X,\mathbb{Q})\) by an algebraic cycle. \(\square\)

### 5. What this does not do

The argument uses that \(X\) is a product of curves, so the only unknown Hodge classes live in a weight-\(1\) Hom-space, which is geometric. It does not produce cycles on a general surface, nor on \(C\times C\times C\), nor on an abelian fourfold.

---

## Remarks

- If \(C=D=E\) is an elliptic curve, \(J(E)=E\) and \(f\) is multiplication by an integer (or an endomorphism, if \(E\) has CM). The cycle is a combination of the graph of that endomorphism and the two fibres — the usual basis of \(\mathrm{NS}(E\times E)\).
- The same dictionary is the reason Hodge for a general abelian variety is a question about Weil classes: the Hom-space of the weight-\(1\) HS no longer exhausts \(H^{k,k}\cap H^{2k}(\mathbb{Q})\) when \(k\ge 2\).
