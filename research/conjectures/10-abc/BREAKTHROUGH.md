# abc — Wave-2 Breakthrough

**Legion:** WAVE-2 LEGION 10 (abc conjecture)
**Workspace:** `/workspace/research/conjectures/10-abc/`
**Date:** 2026-08-15
**Depends on:** `REPORT.md` (Wave-1 dossier), same directory.

**Scope statement.** This file delivers exactly what the Wave-2 mission asked for:
one fully proved Diophantine lemma that is a consequence of a *weaker-than-abc*
inequality, where the weaker inequality is (i) proved completely here in the
function-field case (Mason–Stothers, Theorem A, proof ≤ 2 pages), and (ii) taken as
the cited Stewart–Yu 2001 theorem in the integer case (input (SY) below, not
reproved). Everything else in this file is proved in full, line by line. **The abc
conjecture is not claimed to be proved, and nothing here depends on IUT.**

---

## Theorem

### Input taken from the literature (the weaker-than-abc inequality over Z)

**(SY) [KNOWN — Stewart–Yu 2001, taken as input, not reproved here].**
There is an effectively computable absolute constant `K >= 1` such that every triple
of coprime positive integers `a + b = c` with `c >= 3` satisfies

```
log c  <=  K · R^(1/3) · (log R)^3 ,        R := rad(abc) >= 2 .
```

(C. L. Stewart, K. Yu, "On the abc conjecture, II", Duke Math. J. 108 (2001),
169–181. This is exponentially weaker than abc, which asserts
`log c <= (1+eps) log R + O_eps(1)`. Note `R >= 2` holds automatically: `abc >= 2`
for `c >= 2`, so `abc` has a prime factor.)

Everything below (SY) is proved completely in this file, including the two
auxiliary results (Theorem A and Lemma P) that other derivations often cite
without proof.

### Theorem A (function-field abc; Mason–Stothers) — proved in full below

*Let K be a field and let `a, b, c ∈ K[t]` be pairwise coprime polynomials with
`a + b = c`, not all constant, and such that not all of `a', b', c'` are zero
(automatic in characteristic 0). Then*

```
max( deg a, deg b, deg c )  <=  deg rad(abc) − 1 ,
```

*where `rad(f)` is the product of the distinct monic irreducible factors of f.*

This is the exact abc statement over `K[t]`, with `eps = 0` and constant `−1`. It is
strictly stronger, in its own world, than what is known over Z — and its proof is
elementary and complete below. It is the "weaker-than-abc inequality we prove"
(weaker in the sense that it lives in the model case, not over Z).

### Corollary A.1 (polynomial Fermat — a fully proved Diophantine lemma from Theorem A)

*Let K be a field of characteristic 0 and `n >= 3`. There are no pairwise coprime
polynomials `x, y, z ∈ K[t]`, not all constant, with `xyz ≠ 0` and*

```
x^n + y^n = z^n .
```

### Theorem B (radical lower bound over Z, derived from (SY))

*With K the effective constant of (SY), set `kappa := min( 1, (27K)^(−3) ) > 0`
(effectively computable). Then every triple of coprime positive integers
`a + b = c` with `c >= 16` satisfies*

```
rad(abc)  >=  kappa · (log c)^3 / (log log c)^9 .
```

**The exponents, written and justified.** In the target shape
`rad(abc) >> (log c)^a / (log log c)^b`:

- `a = 3`. Reason: (SY) has the shape `log c <= K R^θ (log R)^m` with `θ = 1/3`,
  and inverting any such bound yields `R >> (log c)^(1/θ)` up to log factors; here
  `1/θ = 3`. No exponent `a > 3` is a formal consequence of (SY) alone: the
  hypothesis (SY) is consistent with a triple having `R` of order
  `(log c)^3 / (log log c)^9`, so the inversion is sharp as a deduction. Improving
  `a` requires improving Stewart–Yu's `1/3` itself (see REPORT.md §4.2, §7.2).
- `b = 9`. Reason: `b = m/θ = 3 / (1/3) = 9` — the factor `(log R)^3` of (SY),
  raised to the power `1/θ = 3` during the inversion.

### Lemma B.2 — THE new Diophantine lemma of this wave (derived from Theorem B)

*Let `P(abc)` denote the greatest prime factor of `abc`. With `kappa` as in Theorem
B, every triple of coprime positive integers `a + b = c` with `c >= 16` satisfies*

```
P(abc)  >  ( 3 · log log c  −  9 · log log log c  +  log kappa ) / log 4 .
```

*Consequently `P(abc) >= (3/log 4 − o(1)) · log log c` with `3/log 4 = 2.164...`,
and there is an effectively computable `C1` such that*

```
P(abc)  >  2 · log log c        for all triples with  c >= C1 .
```

*In particular, the greatest prime factor of `abc` tends to infinity with c,
effectively, over all abc triples.*

(Auxiliary Lemma P, proved in full below: `∏_{p <= n} p < 4^n` for every integer
`n >= 1`, product over primes.)

**Honesty note on Lemma B.2:** this is new relative to REPORT.md, not relative to
the literature — stronger lower bounds on the greatest prime factor of `ab(a+b)`
are known via Baker's method (Győry, Stewart, Tijdeman and others). What is
delivered here is a complete, self-contained derivation whose only unproved input
is (SY).

---

## Proof (complete)

### Part 1. Proof of Theorem A (Mason–Stothers) — target: ≤ 2 pages

Throughout, `'` is the formal derivative `d/dt` on `K[t]`, `deg 0 := −∞`, and for
nonzero `f`, `rad(f)` is the product of the distinct monic irreducible divisors of
`f` (so `rad(u) = 1` for a nonzero constant `u`). Two elementary facts:

**Fact 1.** *If `f` is nonzero then `deg f' <= deg f − 1` (in particular `f' = 0`
when `f` is constant; in characteristic p, `f' = 0` can also occur for nonconstant
`f`, e.g. `f = t^p`).* Immediate from differentiating term by term.

**Fact 2.** *If `p` is irreducible, `e >= 1`, and `p^e || f` (i.e. `p^e | f`,
`p^(e+1) ∤ f`), then `p^(e−1) | f'`.* Write `f = p^e u` with `p ∤ u`; then

```
f' = e p^(e−1) p' u + p^e u' = p^(e−1) · ( e p' u + p u' ) .
```

This holds in every characteristic (if the characteristic divides `e`, even
`p^e | f'`). ∎

**Step 0: none of a, b, c is zero.** If `a = 0`, then `gcd(a, b) = b` up to units,
so pairwise coprimality forces `b` to be a nonzero constant, and then `c = a + b`
is the same constant — all three constant, contradicting the hypothesis. The cases
`b = 0` and `c = 0` (the latter giving `a = −b`, so `gcd(a,b) = a` up to units) are
identical. So `a, b, c ≠ 0` and `deg a, deg b, deg c >= 0`.

**Step 1: one Wronskian, three ways.** For `f, g ∈ K[t]` put
`W(f, g) := f g' − f' g`. `W` is K-bilinear and `W(f, f) = 0`. Since `c = a + b`:

```
W(a, c) = W(a, a) + W(a, b) = W(a, b) ,
W(b, c) = W(b, a) + W(b, b) = −W(a, b) .
```

Set `W := W(a, b) = W(a, c) = −W(b, c)`.

**Step 2: W ≠ 0.** Suppose `W = 0`, i.e. `a b' = a' b`. Then `a | a' b`, and
`gcd(a, b) = 1` gives `a | a'`. If `a' ≠ 0` then `deg a' >= deg a`, contradicting
Fact 1; hence `a' = 0`. Symmetrically `b | b' a` forces `b' = 0`. Then
`c' = a' + b' = 0`, so all three derivatives vanish — excluded by hypothesis.
Therefore `W ≠ 0`.

**Step 3: repeated factors divide W.** Claim: `a / rad(a)` divides `W`. Let `p` be
irreducible with `p^e || a`. If `e = 1` there is nothing to prove for `p`. If
`e >= 2`: `p^(e−1)` divides `a` (trivially) and divides `a'` (Fact 2), hence
divides both terms of `W = a b' − a' b`, hence divides `W`. The prime powers
`p^(e−1)` over distinct `p` are pairwise coprime, and their product is
`a / rad(a)`; so `a / rad(a) | W`.

The same argument applied to the *other two expressions* for `W` handles `b` and
`c`:

- `W = a b' − a' b` also shows `b / rad(b) | W` (if `p^e || b` then `p^(e−1)`
  divides `b'` and `b`, hence both terms);
- `W = W(a, c) = a c' − a' c` shows `c / rad(c) | W` (if `p^e || c` then `p^(e−1)`
  divides `c'` and `c`, hence both terms).

Since `a, b, c` are pairwise coprime, so are `a/rad(a)`, `b/rad(b)`, `c/rad(c)`,
and moreover `rad(abc) = rad(a) rad(b) rad(c)`. Therefore

```
(abc) / rad(abc)  =  (a/rad(a)) · (b/rad(b)) · (c/rad(c))   divides   W .
```

**Step 4: degree count.** Since `W ≠ 0` and `(abc)/rad(abc) | W`:

```
deg a + deg b + deg c − deg rad(abc)  <=  deg W .                    (1)
```

Bound `deg W` from each of the three expressions. From `W = a b' − a' b`: the term
`a b'` is either 0 (if `b' = 0`) or has degree `deg a + deg b' <= deg a + deg b − 1`
(Fact 1); likewise `a' b`; hence

```
deg W  <=  deg a + deg b − 1 .                                       (2)
```

Combining (1) and (2) and cancelling `deg a + deg b`:

```
deg c  <=  deg rad(abc) − 1 .
```

Repeating with `W = a c' − a' c` gives `deg W <= deg a + deg c − 1`, hence
`deg b <= deg rad(abc) − 1`; and with `W = −(b c' − b' c)` gives
`deg W <= deg b + deg c − 1`, hence `deg a <= deg rad(abc) − 1`. Taking the maximum
of the three bounds:

```
max( deg a, deg b, deg c )  <=  deg rad(abc) − 1 .   ∎
```

**Sharpness of the hypotheses.** (i) The derivative hypothesis cannot be dropped in
characteristic p: `t^p + 1 = (t+1)^p` is a coprime triple with
`max deg = p` and `deg rad = 2`; all three derivatives vanish. (ii) The bound is
attained: `t + 1 = (t+1)` is degenerate, but e.g. `t^2 + (2t + 1) = (t+1)^2` over Q
has `max deg = 2` and `rad = t(2t+1)(t+1)` of degree 3, so equality holds in
`2 <= 3 − 1`.

*(End of Mason–Stothers proof — under two pages.)*

### Part 2. Proof of Corollary A.1 (polynomial Fermat, n ≥ 3)

Suppose `x, y, z ∈ K[t]` are pairwise coprime, not all constant, `xyz ≠ 0`,
`char K = 0`, `n >= 3`, and `x^n + y^n = z^n`. Let
`d := max(deg x, deg y, deg z) >= 1`.

Apply Theorem A to the triple `(a, b, c) = (x^n, y^n, z^n)`: it is pairwise coprime
(coprimality is preserved by powers), satisfies `a + b = c`, is not all constant
(as `d >= 1`), and in characteristic 0 the nonconstant entry has nonzero
derivative. Also `rad(x^n y^n z^n) = rad(xyz)` — *powers do not change the radical*,
which is the entire point. Theorem A gives

```
n·d = max( deg x^n, deg y^n, deg z^n )
    <=  deg rad(xyz) − 1
    <=  deg x + deg y + deg z − 1
    <=  3d − 1 .
```

So `(n − 3) d <= −1`, impossible for `n >= 3` and `d >= 1`. ∎

### Part 3. Proof of Theorem B (radical lower bound from (SY))

Let `a + b = c` be coprime positive integers with `c >= 16`, and write
`L := log c`, so `L >= log 16 = 2.772...` and `log L >= log log 16 = 1.019... >= 1`.
Let `R := rad(abc) >= 2`.

**Case 1: `R >= L^3`.** Since `log L >= 1` we have `(log L)^9 >= 1`, hence

```
R  >=  L^3  >=  L^3 / (log L)^9  >=  kappa · L^3 / (log L)^9
```

(using `kappa <= 1`). Done.

**Case 2: `R < L^3`.** Then `log R < 3 log L` (both sides positive since `R >= 2`,
`L > e`). Substituting into (SY):

```
L  <=  K · R^(1/3) · (log R)^3  <  K · R^(1/3) · 27 (log L)^3 ,
```

hence

```
R^(1/3)  >  L / ( 27 K (log L)^3 ) ,
R        >  L^3 / ( (27K)^3 (log L)^9 )  >=  kappa · L^3 / (log L)^9 .
```

In both cases `rad(abc) >= kappa (log c)^3 / (log log c)^9` with
`kappa = min(1, (27K)^(−3))`, effectively computable because K is. ∎

**Why `a = 3` cannot be improved from (SY) alone.** Theorem B is a purely logical
inversion of the inequality (SY); (SY) as a hypothesis permits `R` as small as the
solution of `L = K R^(1/3)(log R)^3`, which is of order `L^3 / (log L)^9`. So any
lemma of the shape `R >> (log c)^a` with `a > 3` would need information beyond
(SY) — i.e. an improvement of the Stewart–Yu exponent `1/3`, which is exactly the
open frontier described in REPORT.md §4.2 and §7.2. (The abc conjecture itself
predicts the incomparably stronger `R > c^(1−eps)` for `c` large.)

### Part 4. Proof of Lemma P (primorial bound) and Lemma B.2

**Lemma P.** *For every integer `n >= 1`,* `∏_{p <= n} p < 4^n` *(product over
primes; empty product = 1).*

**Proof** (Erdős; strong induction on n).

- `n = 1`: `1 < 4`. `n = 2`: `2 < 16`.
- `n >= 4` even: `n` is not prime, so `∏_{p <= n} p = ∏_{p <= n−1} p < 4^(n−1) < 4^n`
  by the induction hypothesis.
- `n = 2m + 1 >= 3` odd (`m >= 1`): split the primes at `m + 1`:

```
∏_{p <= 2m+1} p  =  ( ∏_{p <= m+1} p ) · ( ∏_{m+1 < p <= 2m+1} p ) .
```

Every prime `p` with `m + 1 < p <= 2m + 1` divides the binomial coefficient
`C(2m+1, m) = (2m+1)! / ( m! (m+1)! )`: it divides the numerator `(2m+1)!`, and,
being a prime `> m+1`, it divides neither `m!` nor `(m+1)!`. Hence the product of
these primes divides `C(2m+1, m)`, so it is `<= C(2m+1, m)`. Moreover

```
2 · C(2m+1, m) = C(2m+1, m) + C(2m+1, m+1) <= (1+1)^(2m+1) = 2^(2m+1) ,
```

so `C(2m+1, m) <= 2^(2m) = 4^m`. By the induction hypothesis (applied to
`m + 1 <= 2m < n`), `∏_{p <= m+1} p < 4^(m+1)`. Multiplying:

```
∏_{p <= 2m+1} p  <  4^(m+1) · 4^m  =  4^(2m+1)  =  4^n .   ∎
```

**Proof of Lemma B.2.** Let `a + b = c` be coprime positive integers with
`c >= 16`, and let `P := P(abc)` be the greatest prime factor of `abc` (well
defined: `abc >= 2`). Every prime dividing `abc` is `<= P`, so by Lemma P

```
rad(abc)  <=  ∏_{p <= P} p  <  4^P .
```

Combining with Theorem B:

```
4^P  >  kappa · (log c)^3 / (log log c)^9 .
```

For `c >= 16` we have `log log c > 1`, so `log log log c` is defined and positive.
Taking logarithms of both sides:

```
P · log 4  >  log kappa + 3 log log c − 9 log log log c ,
```

which is the displayed inequality of Lemma B.2. Since
`log log log c = o(log log c)` and `log kappa` is an (effective) constant, we get
`P >= (3/log 4 − o(1)) log log c`, and because `3 / log 4 = 2.1640... > 2`, there
is an effectively computable `C1` (computable from K: it suffices that
`(3/log 4 − 2) log log c > (9/log 4) log log log c − (log kappa)/log 4`) beyond
which `P(abc) > 2 log log c`. All constants trace back to the effective K of (SY),
so the statement is fully effective. ∎

**Sanity check on a real triple.** Reyssat's triple `2 + 3^10·109 = 23^5`:
`c = 6436343`, `log log c = 2.75...`, and the bound (in its asymptotic form) asks
for a prime factor of size a few units; indeed `P(abc) = 109`. The lemma is weak —
as it must be, being an honest consequence of an exponentially-weaker-than-abc
input — but it is nonvacuous, effective, and completely proved.

---

## What is new vs REPORT.md

Relative to the Wave-1 dossier (`REPORT.md`), item by item:

1. **Theorem A (Mason–Stothers).** REPORT.md §6.1 already contains a proof. The
   proof here is a rewrite with every gap closed so this file stands alone: the
   nonvanishing of a, b, c (Step 0, absent in REPORT.md), the case analysis for
   vanishing derivatives inside the degree estimate (2), the explicit three-way
   symmetric degree count, Fact 2 stated and proved in all characteristics, and
   the sharpness examples for both the derivative hypothesis and the `−1`.
2. **Corollary A.1 (polynomial Fermat, n ≥ 3).** REPORT.md §3.2 *asserted* this
   consequence without proof. It is proved here in full (Part 2) — a fully proved
   Diophantine lemma derived from an abc-type inequality that this file proves.
3. **Theorem B.** REPORT.md §6.3 derived the same bound
   `rad(abc) >= kappa (log c)^3/(log log c)^9`. New here: the explicit
   justification of the exponents — `a = 1/θ = 3` and `b = m/θ = 9` from the
   Stewart–Yu shape `log c <= K R^θ (log R)^m`, `θ = 1/3`, `m = 3` — together with
   the sharpness observation that no `a > 3` is a formal consequence of (SY)
   alone, which pins the exact frontier.
4. **Lemma B.2 (greatest prime factor of abc triples) — the genuinely new item.**
   Not present anywhere in REPORT.md: an effective bound
   `P(abc) > (3/log 4) log log c − (9/log 4) log log log c − C0`, hence
   `P(abc) > 2 log log c` for `c` effectively large, over *all* abc triples. Its
   proof chain is complete inside this file modulo only (SY): Theorem B (proved
   here from (SY)) + Lemma P (proved here from scratch, Erdős's induction).
5. **Novelty disclaimer.** "New" in this section means *new relative to
   REPORT.md*. None of Theorems A, B, Corollary A.1, Lemma P, Lemma B.2 is claimed
   to be new to mathematics; Lemma B.2-type results (in much stronger form) exist
   in the Baker-method literature on `P(ab(a+b))`. The deliverable is the complete,
   auditable derivation, per the mission's transparency standard.

---

## Why abc remains open; IUT is not endorsed

**Why open.** The best proved upper bound in the direction of abc is the input
(SY): `log c <= K rad(abc)^(1/3) (log rad(abc))^3`. The conjecture demands
`log c <= (1+eps) log rad(abc) + O_eps(1)`. The gap is between *exponential in a
power of the radical* and *linear in the logarithm of the radical* — a gap of kind,
not of degree. The structural obstruction is documented in REPORT.md §4: the
Baker/Yu linear-forms machinery that produces (SY) carries a multiplicative loss
(`∏ log A_i` over the primes of the radical) that no known technique removes; the
function-field proof (Theorem A above) runs on the derivative `d/dt`, and `Spec Z`
has no derivation — the Wronskian `W`, which does all the work in Part 1, has no
known integer analogue of provably small height. Theorem B's exponent `a = 3` is
exactly the shadow of this: it is `1/θ` for the Stewart–Yu `θ = 1/3`, and it
improves if and only if transcendence theory improves.

**IUT not endorsed.** Mochizuki's IUT papers (published in Publ. RIMS 57 (2021))
claim abc via a Szpiro-type inequality, but the derivation of the key inequality —
IUT-III Corollary 3.12 from Theorem 3.11 — has not been independently verified in
13+ years; Scholze–Stix maintain the step fails, Mochizuki maintains their
simplification is not his argument, and as of 2026 both the RIMS formalization
roadmap and the independent Project LANA (Lean formalization, ZEN University)
locate the unresolved question at precisely that step, with LANA's July 2026
interim report explicitly *suspending judgment* on whether abc has been proved.
Full sourced account: REPORT.md §5.4. Accordingly: **nothing in this file uses,
endorses, or depends on IUT, and this file does not claim — and its results do not
imply — that the abc conjecture is proved.** The strongest inequality used over Z
is the community-accepted Stewart–Yu theorem, which is exponentially weaker than
abc.

---

## Honesty label

Per the label taxonomy of REPORT.md:

| Item | Label |
|------|-------|
| Input (SY) (Stewart–Yu 2001) | `[KNOWN]` — cited, taken as input, not reproved |
| Theorem A (Mason–Stothers) | `[KNOWN — PROOF INCLUDED]` — classical; complete proof in Part 1 |
| Corollary A.1 (polynomial Fermat, n ≥ 3) | `[KNOWN — PROOF INCLUDED]` — classical; complete proof in Part 2 |
| Theorem B (radical lower bound, a = 3, b = 9) | `[DERIVED HERE]` — routine effective inversion of (SY); complete proof in Part 3; no novelty claimed |
| Lemma P (primorial bound < 4^n) | `[KNOWN — PROOF INCLUDED]` — Erdős; complete proof in Part 4 |
| Lemma B.2 (P(abc) ≫ log log c, effective) | `[DERIVED HERE]` — complete proof in Part 4; new relative to REPORT.md only; stronger results exist in the literature |
| Status of abc | `[CONJECTURE]` — **open; not proved here or elsewhere by community standards** |
| Status of IUT | `[DISPUTED]` / `[STATUS]` — not endorsed; not used |

No claim that abc is proved. No use of IUT. Every unproved statement used is the
single cited theorem (SY), flagged as such at its point of use.

---

*End of Wave-2 breakthrough file for LEGION 10.*
