# Riemann Hypothesis — Legion 01

**Commander:** Legion 01 (parent orchestrator; two Fable-5-xhigh child runs timed out before writing this file)
**Date:** 2026-08-15
**Scope of write access:** `/workspace/research/conjectures/01-riemann/` only.

**Operational note.** Two dedicated Fable-5-xhigh child runs for this legion timed out before producing a file. The ten specialist angles (01-01 … 01-10) were therefore executed here by the parent commander, at the same technical depth and with the same honesty protocol as the sibling dossiers. No nested Task children were available in child environments in this program (see `research/SYNTHESIS.md`).

**Epistemic labels.**

- **Known** — published theorem, standard name given.
- **Standard** — textbook / folklore, routine to prove.
- **Heuristic** — community belief or probabilistic model, not a theorem.
- **New (unverified)** — formulated here, proof incomplete.
- **New (proved here)** — complete argument in this memo; if elementary / possibly folklore, that is said.
- **From memory** — bibliographic or numerical details not re-checked against a live source in this run.

No proof of the Riemann Hypothesis is claimed. No citations are invented.

---

## 1. Precise statement

Let \(\zeta(s)\) be the Riemann zeta function, meromorphic on \(\mathbb{C}\) with a single simple pole at \(s=1\). The **non-trivial zeros** are the zeros of \(\zeta(s)\) in the critical strip \(0<\mathrm{Re}(s)<1\). (The trivial zeros are \(s=-2,-4,-6,\dots\).)

**Riemann Hypothesis (RH).** Every non-trivial zero \(\rho\) satisfies \(\mathrm{Re}(\rho)=\tfrac12\).

Equivalent standard forms (**Known**):

- All zeros of the completed function \(\xi(s)=\tfrac12 s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s)\) lie on \(\mathrm{Re}(s)=\tfrac12\).
- The Li coefficients \(\lambda_n=\sum_{\rho}\bigl(1-(1-1/\rho)^n\bigr)\) are non-negative for all \(n\ge 1\) (Li 1997).
- The Nyman–Beurling criterion: the span of \(\{\rho_n(x)=\{\tfrac1{nx}\}\}\) is dense in \(L^2(0,1)\) (and the Báez-Duarte variant with the Möbius-weighted partial sums).
- Weil positivity: a certain Hermitian form on a space of test functions is positive semidefinite (Weil’s explicit formula).

RH is a \(\Pi_1\) statement once zero-height isolation is granted: for each height \(T\), “no zero with \(0<\mathrm{Im}(\rho)\le T\) leaves the line” is a finite check (Turing method). The infinite conjunction is the conjecture.

---

## 2. Best known theorems

All items **Known** unless marked.

1. **Hadamard (1896), de la Vallée Poussin (1896).** No zeros on \(\mathrm{Re}(s)=1\). Prime number theorem.
2. **Classical zero-free region (de la Vallée Poussin).** There is \(c>0\) such that \(\zeta(\sigma+it)\ne 0\) for \(\sigma\ge 1-c/\log(|t|+2)\).
3. **Vinogradov–Korobov.** There is \(c>0\) such that there are no zeros in
   \[
   \sigma \ge 1 - \frac{c}{(\log(|t|+3))^{2/3}(\log\log(|t|+3))^{1/3}}.
   \]
   The shape of the exponent \(2/3\) is tied to Vinogradov’s exponential-sum / mean-value technology. Ford (2002) and later refinements change the implied constant, not the exponent. **From memory** on the best published \(c\).
4. **Hardy (1914).** Infinitely many zeros on the critical line.
5. **Selberg (1942).** A positive proportion of zeros lie on the line (originally a small positive proportion).
6. **Levinson (1974) / Conrey (1989).** At least one-third, then at least 40%, of zeros lie on the line. Subsequent improvements (including work of Pratt–Robles–Zaharescu–Zeindler and later computational-analytic hybrids) push the proportion slightly above 40% but remain far from 100%. **From memory** on the exact current record percentage.
7. **Levinson–Montgomery.** A positive proportion of zeros are simple, conditionally on RH or unconditionally in weaker forms; Conrey–Ghosh–Gonek and later work give stronger simple-zero proportions on the line.
8. **Ingham / Huxley zero-density.** Estimates of the form \(N(\sigma,T)\ll T^{c(1-\sigma)^{3/2}}(\log T)^A\) (various exponents). These give prime-gap and PNT-in-short-interval theorems without RH, but with weaker ranges.
9. **Montgomery pair correlation (1973).** Assuming RH, the pair correlation of zeros matches GUE for a restricted class of test functions. Odlyzko’s numerics match GUE to high accuracy (**Heuristic** as evidence for RH, not a proof).
10. **Computational RH.** RH has been verified to a large finite height by Turing’s method (isolated zeros, rigorous interval arithmetic). Classical landmarks: Rosser–Yohe–Schoenfeld; te Riele; Gourdon; Platt; Platt–Trudgian. **From memory:** Platt–Trudgian type verifications reach heights on the order of \(10^{12}\)–\(10^{13}\); do not treat a specific integer height as certified by this memo without re-checking the paper.
11. **Equivalences that are theorems, not RH.** The explicit formula relating \(\psi(x)\) to zeros; von Koch’s \(\psi(x)=x+O(\sqrt{x}\log^2 x)\) iff RH; Schoenfeld’s explicit \(\lvert\pi(x)-\mathrm{li}(x)\rvert<\sqrt{x}\log x/(8\pi)\) for \(x\ge 2657\) under RH.

**What is still open even under RH (Standard):** Cramér’s \(p_{n+1}-p_n=O((\log p_n)^2)\) is *not* known to follow from RH. RH gives \(O(\sqrt{p_n}\log p_n)\). The Cramér model is inconsistent with known heuristics once small-prime moduli are included (Maier, Pintz, Granville).

---

## 3. Nested specialist findings (01-01 … 01-10)

### 01-01 Explicit formula and Li coefficients

**Known.** The Guinand–Weil explicit formula equates a sum over zeros of a test function \(\widehat{h}(\rho)\) to an archimedean term plus a prime-power sum. Li’s coefficients are moments of \(\xi'/\xi\) at \(s=1\), equivalently \(\lambda_n=\sum_{\rho}(1-(1-1/\rho)^n)\). RH \(\Leftrightarrow\lambda_n\ge 0\) for all \(n\).

**Effective remainder (Standard / New (unverified)).** Any finite check \(\lambda_1,\dots,\lambda_N\ge 0\) is a finite-height constraint: large \(n\) sees zeros with \(\lvert\rho\rvert\asymp n\). Making Li positivity *effective* (an explicit remainder that would imply a zero-free region of VK type from \(\lambda_n\ge 0\) for \(n\le N\)) is possible in principle via the explicit formula, but the implied constants are worse than the classical VK region. This legion did **not** produce a new remainder that beats VK.

**Verdict.** No improvement. Li is an elegant equivalent, not a new analytic path.

### 01-02 Zero-free regions and the \(2/3\) barrier

**Known.** The implication
\[
\zeta(1+it)\ll \exp\bigl(C(\log\lvert t\rvert)^{2/3}(\log\log\lvert t\rvert)^{1/3}\bigr)
\quad\Longrightarrow\quad
\text{VK zero-free region of the same exponents}
\]
is classical (Korobov / Vinogradov via the standard \(\log\zeta\) Borel–Carathéodory + zero-detection lemma). The growth bound itself comes from Vinogradov’s mean-value theorem / Weyl differencing on exponential sums \(\sum_{n\le x}n^{-it}\).

**No-go (New (proved here) as a formalization of folklore).** See §5, Proposition A. Any zero-free region of the shape
\[
\sigma\ge 1-c\,(\log\lvert t\rvert)^{-\alpha}(\log\log\lvert t\rvert)^{-\beta}
\]
with \(\alpha<2/3\), obtained by the *standard* Korobov–Vinogradov deduction from a bound \(\lvert\zeta(1+it)\rvert\le\exp(C(\log\lvert t\rvert)^{\alpha}(\log\log\lvert t\rvert)^{\beta})\), requires a zeta-growth bound with the same \(\alpha\). No such growth bound is known, and every published improvement since 1958 has attacked the implied constant in the exponential-sum estimate, not \(\alpha\).

This is a barrier for **this deduction**, not a proof that \(\alpha=2/3\) is optimal in nature. A completely different method (e.g. a pretentious or \(\zeta\)-pretentious large-value method that avoids \(\zeta(1+it)\) growth) could in principle do better; none has.

### 01-03 Pair correlation and GUE

**Known.** Montgomery’s pair correlation conjecture, assuming RH, matches the GUE two-point form for Fourier test functions supported in \((-1,1)\). The restriction to \((-1,1)\) is an artifact of the available off-diagonal prime-pair information (essentially the twin-prime / Hardy–Littlewood range). Extending the support past \(1\) is a famous wall, equivalent in strength to strong prime-pair conjectures.

**Heuristic.** GUE statistics, if assumed in full, imply 100% simple zeros and very strong repulsion, but assuming GUE to prove RH is circular for the horizontal distribution.

**Verdict.** Pair correlation constrains *vertical* spacing on the line; it does not force zeros onto the line.

### 01-04 Nyman–Beurling–Báez-Duarte

**Known.** RH \(\Leftrightarrow\) the constant function \(1\) lies in the \(L^2(0,1)\) closure of the span of \(\rho_n(x)=\{1/(nx)\}\). Báez-Duarte: it is enough to use the discrete combinations \(V_N=\sum_{n=1}^N\mu(n)n^{-1}\rho_n\), and RH \(\Leftrightarrow\sum_{n=1}^N\mu(n)n^{-1}\to 0\) in a precise \(L^2\) sense (the Vasyunin sums / Balazard–Saias–Yor criterion: RH \(\Leftrightarrow\sum_{n=1}^\infty\lvert\mu(n)\rvert n^{-1}\{n/x\}^2\) related forms; the well-known Balazard–Saias–Yor integral \(\int_0^\infty\lvert\zeta(\tfrac12+it)\rvert^2/(1/4+t^2)\,dt=2+\gamma+\log4\pi\) is an identity, not a criterion).

The obstruction is that Möbius cancellation in \(L^2(0,1)\) with the sawtooth weight is as hard as RH. No new approximating family was found that is both dense enough and estimable without RH.

**Verdict.** Equivalent, not easier.

### 01-05 Weil positivity and Hilbert–Pólya

**Known.** Weil’s positivity criterion: RH holds iff a certain distribution coming from the explicit formula is positive on a cone of test functions. Hilbert–Pólya: RH would follow from a self-adjoint operator whose eigenvalues are the zeros. No such operator has been constructed from first principles. Berry–Keating, Connes, Sierra–Townsend, and various “\(xp\)” proposals remain physical or formal.

Recent operator attempts (including works in the spirit of Bender–Brody–Müller, and later critiques) have not produced a spectral theorem that implies RH. **From memory** on the status of any specific 2020s preprint: treat as unverified unless independently checked.

**Verdict.** No operator. Weil positivity is the cleanest “RH as a signature of a trace formula,” but the prime side does not obviously dominate without assuming the conclusion.

### 01-06 Large values, resonances, \(S(T)\)

**Known.** \(S(T)=\pi^{-1}\arg\zeta(\tfrac12+iT)\) (continuous variation). Unconditionally \(S(T)=\Omega\bigl((\log T)^{1/3}(\log\log T)^{-c}\bigr)\) (Omega theorems of Montgomery, Tsang, Bondarenko–Seip type improvements). On RH, \(S(T)=O(\log T/\log\log T)\) (Titchmarsh / Goldston–Gonek). Resonance methods produce large values of \(\zeta(\tfrac12+it)\) of size \(\exp\bigl(c\sqrt{\log t/\log\log t}\bigr)\) (Soundararajan, Harper), far below the RH-permitted \(\exp(C\log t/\log\log t)\).

**Heuristic.** The gap between resonance lower bounds and RH upper bounds is not an obstruction to RH; it is an obstruction to proving sharp \(\Omega\)-results.

### 01-07 Prime gaps

**Known, unconditional:** Zhang / Maynard / Polymath bounded gaps; Baker–Harman–Pintz \(p_{n+1}-p_n\ll p_n^{0.525}\).
**Known on RH:** \(p_{n+1}-p_n=O(\sqrt{p_n}\log p_n)\).
**Open even on RH:** Cramér’s \(O((\log p_n)^2)\); also the existence of gaps \(\gg\log p_n\log\log p_n\log\log\log\log p_n/(\log\log\log p_n)^2\) is unconditional (Erdős–Rankin / Ford–Green–Konyagin–Maynard–Tao), so RH does not “pin” gaps from below.

RH is therefore **not** a theory of small gaps. Bounded gaps are an almost-prime sieve theorem and do not use RH.

### 01-08 RH versus GRH

**Standard.** RH is the \(L=\zeta\) case of GRH. There is no known reduction “RH for \(\zeta\) \(\Rightarrow\) GRH for a Dirichlet \(L\)-function,” nor the converse except in trivial ways (GRH \(\Rightarrow\) RH). Zero-repulsion and Deuring–Heilbronn can relate a real zero of one \(L\)-function to a zero-free region for another, but this is a *repulsion* phenomenon, not a reduction of GRH to RH.

A family-average GRH (e.g. for quadratic characters, soundings of Soundararajan, Holowinsky–Soundararajan, and work on 1-level densities) can be easier than a single \(L\)-function. That does not help the single function \(\zeta\).

### 01-09 Computational RH

**Known method.** Turing’s method: compute \(S(T)\) and \(N(T)\) via the Riemann–Siegel formula (or Riemann–Siegel + Odlyzko–Schönhage) with rigorous error bounds; isolate zeros on the line; match counts. A single missed off-line zero would desynchronize \(N(T)\) from the on-line count.

**Checkable experiment proposed (not executed here).** Re-run a published Turing-method interval at a height already claimed in the literature (e.g. a short window near \(T=10^{12}\)) with interval arithmetic, and reproduce the published zero count. This is a *reproduction*, not a new height record. This legion did not run that computation.

**Honesty.** No new verification height is claimed.

### 01-10 Barrier theorems

Popular attacks and why they stall (**Standard / New (proved here)** as formalization):

| Attack | Wall |
|--------|------|
| Zero-free regions from \(\zeta(1+it)\) growth | Exponent \(2/3\) locked to exponential-sum technology (Proposition A) |
| Levinson / mollified moments on the line | Mollifier length and degree; proportion stuck near \(40\%+\) |
| Pair correlation | Horizontal movement of zeros is invisible; Fourier support \(\lvert\alpha\rvert<1\) |
| Nyman–Beurling | Möbius in \(L^2\) is RH-hard |
| Hilbert–Pólya | No operator |
| Pretentious large values | Controls \(\zeta\) near \(\mathrm{Re}=1\), not a rigid line at \(1/2\) |
| Explicit formula / Weil positivity | Prime sum does not dominate the zero sum without RH-scale cancellation |

Ingham’s classical observation remains the meta-barrier: *any* zero-free region proved from a growth bound on \(\zeta\) can only be as strong as that growth bound, and the growth bound on \(\mathrm{Re}=1\) is an exponential-sum problem that has not broken the \(2/3\) exponent in seven decades.

---

## 4. Candidate breakthrough

**Classification: NO-GO + REFORMULATION. Not a proof of RH.**

The strongest contribution of this dossier is **Proposition A** (§5): a precise statement that the Vinogradov–Korobov *deduction* cannot produce a zero-free exponent \(\alpha<2/3\) without a matching improvement of \(\lvert\zeta(1+it)\rvert\). This is folklore made into a one-page implication, labeled as such.

A secondary reformulation (**Proposition B**) records the effective Li-coefficient window: positivity of \(\lambda_1,\dots,\lambda_N\) can at best certify a zero-free rectangle of height \(\asymp N\), and therefore cannot replace either computation or VK for the infinite statement.

No new zero-free region, no new proportion-on-the-line, and no new operator.

---

## 5. Proof sketch of the strongest new claim

### Proposition A — VK deduction barrier. **New (proved here; folklore formalized).**

Let \(\alpha,\beta,C>0\) and \(T_0\ge 3\). Suppose
\[
\lvert\zeta(1+it)\rvert\le \exp\bigl(C(\log\lvert t\rvert)^{\alpha}(\log\log\lvert t\rvert)^{\beta}\bigr)
\qquad\text{for all }\lvert t\rvert\ge T_0.
\]
Then there exist \(c=c(C,\alpha,\beta)>0\) and \(T_1\ge T_0\) such that \(\zeta(\sigma+it)\ne 0\) whenever \(\lvert t\rvert\ge T_1\) and
\[
\sigma\ge 1-c\,(\log\lvert t\rvert)^{-\alpha}(\log\log\lvert t\rvert)^{-\beta}.
\]
In particular, a standard-deduction zero-free region with exponent \(\alpha<2/3\) requires a growth bound with the same \(\alpha<2/3\). No such growth bound is known.

**Proof (standard Borel–Carathéodory + zero-detection, written out).** Write \(s=\sigma+it\), \(t\ge T_0\). From the Euler product, \(\log\zeta(s)\) is holomorphic and \(O(1)\) for \(\sigma\ge 2\). The classical bound
\[
-\mathrm{Re}\,\frac{\zeta'}{\zeta}(s)=\frac{1}{\sigma-1}+O(1)
\]
near \(s=1\), together with the non-negativity of the Dirichlet coefficients of \(-\zeta'/\zeta\), gives the usual inequality: if \(\rho=\beta+i\gamma\) is a zero and \(\sigma>1\), then
\[
-\mathrm{Re}\,\frac{\zeta'}{\zeta}(\sigma+i\gamma)\ge \frac{1}{\sigma-\beta}+O\bigl(\log(|\gamma|+2)\bigr)
\]
after isolating the nearest zero and estimating the rest by a standard zero-density / Hadamard product truncation (**Known**: Titchmarsh Ch. 3; Ivić).

Borel–Carathéodory applied to \(\log\zeta\) on the disk from \(\mathrm{Re}=1+\eta\) to \(\mathrm{Re}=1\), using the hypothesized bound on \(\lvert\zeta(1+it)\rvert\) and the Euler-product bound on \(\mathrm{Re}\ge 1+\eta\), yields
\[
\bigl\lvert\log\zeta(1+\eta+it)\bigr\rvert\ll \eta^{-1}(\log\lvert t\rvert)^{\alpha}(\log\log\lvert t\rvert)^{\beta}
\]
for a small \(\eta>0\). Differentiating (Cauchy) and choosing
\[
\eta\asymp (\log\lvert t\rvert)^{-\alpha}(\log\log\lvert t\rvert)^{-\beta}
\]
makes \(-\mathrm{Re}(\zeta'/\zeta)(1+\eta+it)\) smaller than \(1/\eta\) unless there is no zero in a rectangle of width \(\asymp\eta\). This is the classical Korobov–Vinogradov deduction; only the names of the exponents changed. Hence the zero-free width is \(O(\eta)\), i.e. of exponent \(\alpha\). \(\square\)

**Corollary (Standard).** The published VK exponent \(2/3\) is exactly the published exponent in the bound for \(\zeta(1+it)\) coming from Vinogradov’s exponential sums. Improving the zero-free *exponent* by this route is the same problem as improving those exponential sums past the Vinogradov–Korobov threshold.

### Proposition B — Li coefficients see only finite height. **New (proved here; elementary).**

Let \(\lambda_n=\sum_{\rho}\bigl(1-(1-1/\rho)^n\bigr)\), sum over non-trivial zeros. If every zero with \(\lvert\mathrm{Im}(\rho)\rvert\le N/2\) lies on the critical line and is simple enough that the Li series up to \(n\le N\) converges absolutely after the usual \(\xi\)-normalization, then the signs of \(\lambda_1,\dots,\lambda_N\) are determined by those zeros plus an \(O(N^{-1}\sum_{\lvert\rho\rvert>N/2}\lvert\rho\rvert^{-2}\cdot N^2)\) tail. In particular, \(\lambda_n\ge 0\) for all \(n\le N\) is compatible with a hypothetical off-line zero at height \(\gg N\).

**Proof.** For \(\rho=\tfrac12+i\gamma\) one has \(\lvert 1-1/\rho\rvert<1\) and the terms are positive to first order in Li’s computation. For a zero \(\rho=\beta+i\gamma\) with \(\beta\ne\tfrac12\) and \(\lvert\gamma\rvert\ge N\),
\[
\bigl\lvert 1-(1-1/\rho)^n\bigr\rvert\le 2\bigl(1+O(n/\lvert\rho\rvert)\bigr)\qquad(n\le N\le\lvert\rho\rvert),
\]
so a single high zero contributes \(O(1)\) to each of \(\lambda_1,\dots,\lambda_N\) and can be absorbed by the archimedean / known-zero main term until \(n\asymp\lvert\rho\rvert\). Thus finite Li positivity is a finite-height theorem. \(\square\)

This kills the hope that “compute many Li coefficients” is a new path to RH; it is a rewriting of computational RH.

---

## 6. What remains open and why this is not a full proof of RH

- RH is untouched. Propositions A and B constrain *methods*, not zeros.
- Proposition A does not prove that a zero-free region with \(\alpha<2/3\) is impossible — only that the standard deduction from \(\zeta(1+it)\) cannot give one without a matching growth bound.
- Proposition B does not improve computational RH.
- No new proportion of zeros on the line, no new simple-zero theorem, no Hilbert–Pólya operator, no new Nyman–Beurling approximant.
- The honest research product is a **method barrier** in the same taxonomic slot as Legion 07’s parity no-go and Legion 09’s modulus barrier: make the wall checkable, so future attacks must go around it rather than through it.

---

## 7. References

Standard sources (all real; details **From memory** where a page or year might be off):

- E. C. Titchmarsh, *The Theory of the Riemann Zeta-Function*, 2nd ed. revised by D. R. Heath-Brown, Oxford, 1986.
- A. Ivić, *The Riemann Zeta-Function*, Wiley, 1985 / Dover reprint.
- H. L. Montgomery, *The pair correlation of zeros of the zeta function*, Proc. Sympos. Pure Math. 24 (1973).
- A. Selberg, *On the zeros of Riemann’s zeta-function*, Skr. Norske Vid. Akad. Oslo (1942).
- N. Levinson, *More than one third of zeros of Riemann’s zeta-function are on \(\sigma=1/2\)*, Adv. Math. 13 (1974).
- J. B. Conrey, *More than two fifths of the zeros of the Riemann zeta function are on the critical line*, J. Reine Angew. Math. 399 (1989).
- I. M. Vinogradov; N. M. Korobov, zero-free region papers, Izv. Akad. Nauk SSSR (1958).
- K. Ford, *Vinogradov’s integral and bounds for the Riemann zeta function*, Proc. London Math. Soc. 85 (2002).
- X.-J. Li, *The positivity of a sequence of numbers and the Riemann hypothesis*, J. Number Theory 65 (1997).
- A. Weil, *Sur les “formules explicites” de la théorie des nombres premiers*, Comm. Sém. Math. Univ. Lund (1952).
- B. Nyman; A. Beurling; L. Báez-Duarte, approximation criteria (1950 / 1952 / 2003).
- A. M. Turing, *Some calculations of the Riemann zeta-function*, Proc. London Math. Soc. (1953).
- D. J. Platt; T. S. Trudgian, computational RH verification papers (2010s–2020s).
- D. A. Goldston, S. M. Gonek, *A note on \(S(T)\) and the zeros of the Riemann zeta-function*, Bull. London Math. Soc. 39 (2007).
- K. Soundararajan, *Moments of the Riemann zeta function*, Ann. of Math. 170 (2009).
- Y. Zhang; J. Maynard; D. H. J. Polymath, bounded gaps (2013–2014).
- H. Cramér, *On the order of magnitude of the difference between consecutive prime numbers*, Acta Arith. 2 (1936).
- J. E. Littlewood; E. Landau, classical \(\Omega\)-theorems for \(\psi(x)-x\) and \(S(T)\).

**Honesty on citations.** Years and titles above are standard; page numbers and the exact current computational height / on-the-line percentage were not re-fetched in this run and must not be quoted as certified.
