# LEGION 10 — The abc Conjecture: Research Dossier

**Program:** TOP-10 Unsolved Conjectures Research Program
**Legion:** 10 (abc conjecture / Oesterlé–Masser conjecture)
**Workspace:** `/workspace/research/conjectures/10-abc/`
**Date compiled:** 2026-08-15

**Mission compliance statement.** This dossier does **not** claim a proof of the abc
conjecture, and it does **not** treat Mochizuki's inter-universal Teichmüller theory (IUT)
as an accepted proof. As of the compilation date the abc conjecture must be regarded as
**open**. The IUT papers exist, were published in 2021, and are **not accepted by the
mathematical community at large as a proof**; the detailed status account is in §5.4.

**Orchestration note.** The mission specified ten nested specialist subagents (10-01 …
10-10). The execution environment available to this commander does not expose a
subagent-spawning tool, so the ten angles were executed by the commander directly, in
full, and consolidated here. The angle-to-section map is given below; no angle was
dropped.

| Angle | Topic | Where treated |
|-------|-------|---------------|
| 10-01 | Precise abc statement, quality q(a,b,c), equivalent forms (Szpiro, generalized Szpiro) | §2.1–§2.4 |
| 10-02 | Proven weakenings: Stewart–Tijdeman, Stewart–Yu, Baker-method bounds, actual exponents | §3.1 |
| 10-03 | Consequences of abc and their unconditional status | §3.4 |
| 10-04 | Mochizuki IUT: claimed structure, Scholze–Stix, acceptance status | §5.4 |
| 10-05 | Radical, conductors, arithmetic of rad(abc) | §2.5, §3.3 |
| 10-06 | Function-field abc (Mason–Stothers) and why number fields are harder | §3.2, §4.1, §6.1 |
| 10-07 | Elkies / Bombieri / Vojta dictionary: abc as a Diophantine-hyperbolic statement | §5.3 |
| 10-08 | Computational abc hits and what they constrain | §3.3, §5.5 |
| 10-09 | Effective vs ineffective abc; Baker linear forms in logs as the engine | §3.1, §4.2 |
| 10-10 | What a conventional (non-IUT) proof would need | §5.1, §5.2, §7.2 |

**Honesty labels used throughout:**

- `[KNOWN]` — established theorem in the literature; citation given.
- `[KNOWN — PROOF INCLUDED]` — classical result, reproved in full in this dossier for transparency.
- `[DERIVED HERE]` — routine corollary of cited theorems, proved in full here; **no novelty claimed** (such statements are almost certainly folklore).
- `[CONDITIONAL]` — follows from an explicitly stated unproved hypothesis.
- `[CONJECTURE]` — open statement.
- `[DISPUTED]` — a claimed result not accepted by the mathematical community.
- `[HEURISTIC]` — plausibility argument, not a proof.
- `[STATUS]` — verification/acceptance reporting, with sources.
- `(*)` after a citation — bibliographic details reproduced from the commander's training memory and not independently re-verified today; the mathematical statement attributed to it was cross-checked against secondary sources where possible.

---

## 1. Executive Summary

1. **The abc conjecture is open.** No proof accepted by the community exists. The best
   *proved* inequalities in the direction of abc are exponentially weaker than the
   conjecture: Stewart–Yu (2001) gives `c < exp(K · rad(abc)^(1/3) · (log rad(abc))^3)`,
   whereas abc demands `c < K_eps · rad(abc)^(1+eps)`. Closing this gap — from
   *exponential in a power of the radical* to *polynomial (essentially linear) in the
   radical* — is the entire problem. `[KNOWN]`

2. **The epsilon is necessary.** There are infinitely many triples with
   `c > R · exp(k · sqrt(log R / log log R))` for `k < 6.068` (Stewart–Tijdeman 1986;
   van Frankenhuysen 2000), so `c < K · rad(abc)` is false for every constant K. This
   dossier includes a fully elementary proof of a slightly weaker version of this
   failure (§6.2). `[KNOWN — PROOF INCLUDED]`

3. **IUT status (as of August 2026), in one paragraph.** Mochizuki's four IUT papers
   (preprints 2012, published in Publ. RIMS 2021) claim a proof of a Szpiro-type
   inequality and hence abc. Scholze and Stix (2018) identified what they regard as an
   irreparable gap at the step deriving the key height inequality (IUT-III, Corollary
   3.12) from the multiradial representation (IUT-III, Theorem 3.11); Mochizuki rejects
   their simplification as logically unrelated to his actual argument. Eight years
   later there is still no community consensus that the step is correct, and two
   formalization efforts launched in 2026 — one by Mochizuki's own group at RIMS, one by
   the independent Project LANA at ZEN University — both currently locate the unresolved
   question at exactly that step. Project LANA's July 2026 interim report explicitly
   *suspends judgment* on whether abc has been proved. The majority expert view,
   as reported in the scientific press, is that a serious gap remains. **Therefore this
   dossier treats abc as unproved.** Details and sources: §5.4. `[STATUS]`

4. **Legion output.** No breakthrough is claimed. The concrete deliverables are:
   (a) transparent, self-contained proofs of the two classical pillars — Mason–Stothers
   for polynomials (§6.1) and the infinitude of high-quality "hits" showing epsilon is
   necessary (§6.2); (b) fully derived, effective corollaries of the proved
   Stewart–Yu inequality — a lower bound `rad(abc) >> (log c)^3 / (log log c)^9` for
   every abc triple (§6.3), an effective exponent bound for hypothetical Fermat
   counterexamples (§6.4), and an effective finiteness statement for fixed-base
   generalized Fermat equations (§6.5); (c) a threshold analysis showing exactly which
   polynomial exponent in a bound `c < R^theta` would unlock which famous consequence
   (§6.7); and (d) the precise technical account of where IUT is not yet checkable
   (§5.4). All items are labeled; none of the corollaries is claimed to be new.

5. **Verdict (README taxonomy): known / incremental.** No candidate breakthrough. The
   honest frontier for a conventional proof is identified in §7.2: any sub-polynomial
   improvement in (p-adic) linear forms in logarithms of "additive" rather than
   "multiplicative" dependence on the heights (Baker's 1998 refinement program), or a
   proof of the modular degree conjecture, or an arithmetic analogue of the
   derivative/Wronskian — each of which is itself a famous open problem.

---

## 2. Problem Statement and Equivalent Formulations (Angles 10-01, 10-05)

### 2.1 The radical and the conjecture

For a positive integer n, the **radical** `rad(n)` is the product of the distinct primes
dividing n. Examples: `rad(16) = 2`, `rad(18) = 6`, `rad(1000000) = 10`.

An **abc triple** in the wide sense is a triple of coprime positive integers (a, b, c)
with `a + b = c` (coprimality of any one pair implies coprimality of all pairs, since
any prime dividing two of them divides the third). Throughout, `R := rad(abc)`.

**abc conjecture (Masser 1985, Oesterlé; `[CONJECTURE]`).** For every `eps > 0` there
are only finitely many coprime triples `a + b = c` with

```
c > rad(abc)^(1+eps).
```

Equivalently: for every `eps > 0` there exists an (unspecified) constant `K_eps` such
that every coprime triple satisfies `c < K_eps · rad(abc)^(1+eps)`.

The two forms are equivalent by a standard compactness argument: finitely many
exceptions can be absorbed into a constant, and conversely a uniform constant forces
finiteness of triples exceeding the bound with a slightly larger epsilon. `[KNOWN]`

A symmetric variant: for coprime integers with `A + B + C = 0`,
`max(|A|, |B|, |C|) < K_eps · rad(|ABC|)^(1+eps)`. This is equivalent to the above.

### 2.2 Quality

The **quality** of a triple is

```
q(a, b, c) := log c / log rad(abc).
```

A triple is a **hit** if `q > 1`, i.e. `c > rad(abc)`. The abc conjecture is exactly
the statement `limsup q(a,b,c) = 1` over all coprime triples — more precisely:

- hits exist, and in fact infinitely many exist (proved in full in §6.2); so `limsup q >= 1` unconditionally;
- abc asserts that for every `eps > 0` only finitely many triples have `q > 1 + eps`.

The highest quality ever found is `q = 1.62991...`, for Reyssat's 1987 triple

```
2 + 3^10 · 109 = 23^5      (2 + 6436341 = 6436343,  rad = 2·3·23·109 = 15042).
```

No triple with `q >= 2` has ever been found (see §3.3, §5.5). `[KNOWN]`

### 2.3 Equivalent forms: Szpiro and generalized (modified) Szpiro

Let `E/Q` be an elliptic curve with minimal discriminant `Delta_min` and conductor `N`.

- **Szpiro's conjecture** `[CONJECTURE]`: for every `eps > 0`,
  `|Delta_min| < C_eps · N^(6+eps)`.
- **Modified (generalized) Szpiro conjecture** `[CONJECTURE]`: for every `eps > 0`,
  `max(|c4|^3, |c6|^2) < C_eps · N^(6+eps)`, where c4, c6 are the standard invariants
  of a minimal Weierstrass model.

**Relationship `[KNOWN]`:** the abc conjecture is *equivalent* to the modified Szpiro
conjecture, and Szpiro-type inequalities imply abc-type inequalities, via the **Frey
curve**: to a coprime triple `a + b = c` one attaches

```
E_{a,b} :  y^2 = x (x - a) (x + b),
```

which has discriminant `16 (abc)^2` and is semistable away from 2, with conductor equal
to `rad(abc)` up to a bounded power of 2. The dictionary "additive relation among
integers ↔ elliptic curve whose discriminant sees the product and whose conductor sees
the radical" is the single most important structural reformulation of abc. (See
Oesterlé's Bourbaki exposé [Oes88] and Frey [Fre97].)

Transparent sample computation `[DERIVED HERE]` (standard): plain Szpiro applied to the
Frey curve gives `(abc)^2 << rad(abc)^(6+eps)`; since for a triple with `a <= b < c` we
have `abc > b·c > c^2 / 2`, this yields `c << rad(abc)^(3/2 + eps)`. An amplification
trick (applying Szpiro to auxiliary triples manufactured from (a,b,c)) improves the
exponent to `6/5 + eps`; the exponent 6/5 from plain Szpiro is standard in the survey
literature ([Oes88], [Nit96]) `(*)`. Modified Szpiro yields the full `1 + eps`, because
for the Frey curve `|c4|` is comparable to `c^2`, so `|c4|^3 << N^(6+eps)` reads
`c^6 << rad(abc)^(6+eps)`.

### 2.4 Other equivalent formulations `[KNOWN]`

- **Granville–Langevin form:** if f is a squarefree binary form of degree `n >= 3`, then
  for every `beta > 2` there is `C(f, beta)` with
  `rad(f(x, y)) > C · max(|x|, |y|)^(n - beta)` for all coprime integers x, y. This is
  equivalent to abc (Langevin [Lan93]).
- **Vojta's conjecture in dimension 1** (with truncated counting functions) is
  equivalent to abc; abc also implies Vojta's height inequality for algebraic points on
  curves (van Frankenhuijsen [vF02]). See §5.3.
- **S-unit reformulation:** abc is equivalent to a uniform bound on the heights of
  solutions of `u + v = 1` in S-units, of the shape "height of u is at most
  `(1+eps) · (sum of log p over p in S) + O_eps(1)`". This form makes visible why
  linear forms in logarithms enter: solutions of the S-unit equation are precisely
  where the known machinery bites (§3.1, §4.2).

### 2.5 The arithmetic of rad(abc) (Angle 10-05)

Facts used repeatedly in this dossier, all elementary `[KNOWN]`:

1. `rad` is multiplicative on coprime arguments: `rad(abc) = rad(a) rad(b) rad(c)` for a
   coprime triple.
2. `rad(n) <= n`, with equality iff n is squarefree; `rad(n) <= sqrt(n)` iff n is
   **powerful** (every prime exponent >= 2). High-quality triples are exactly those
   whose three entries are simultaneously "radical-deficient", e.g. divisible by high
   prime powers.
3. For the Frey curve, the conductor N satisfies `N | 2^s · rad(abc)` and
   `rad(abc) | 2^t · N` for small absolute s, t: **conductor = radical up to 2-adic
   bookkeeping.** This is why Szpiro-type statements about conductors translate into
   radical statements. (Sketch level; the precise 2-adic exponent requires Tate's
   algorithm.) `[KNOWN]`
4. Distribution: integers with small radical ("smooth-kernel" integers) are rare; the
   counting function of `{n <= x : rad(n) <= y}` is studied by Robert–Tenenbaum [RT13],
   and that analysis underlies the refined conjecture of Robert–Stewart–Tenenbaum
   [RST14] quoted in §3.3. The heuristic that abc should be true is, at bottom, the
   statement that the three events "a has small radical", "b has small radical",
   "a + b has small radical" behave quasi-independently; the RST refinement quantifies
   exactly how much correlation the additive structure can produce. `[HEURISTIC]`,
   made precise as a conjecture in [RST14].
5. What makes `rad` hard: it is neither monotone nor continuous in any archimedean
   sense, it is invisible to linear algebra, and — decisively — there is no operator on
   Z that detects repeated prime factors the way `d/dt` detects repeated roots of a
   polynomial (`p^e || n` forces `p^(e-1) | n'` has no meaning for integers). This is
   the exact point where the function-field proof (§6.1) fails to transfer (§4.1).

---

## 3. Known Results and Prior Art (Angles 10-02, 10-03, 10-06, 10-08, 10-09)

### 3.1 Proved weakenings of abc — the actual exponents (Angle 10-02)

All three bounds below are **unconditional, fully effective theorems**; the constants
are effectively computable. They are proved by Baker's method: archimedean linear forms
in logarithms plus, crucially, Yu Kunrui's p-adic linear forms in logarithms. `[KNOWN]`

| Result | Bound (R = rad(abc)) | Reference |
|--------|----------------------|-----------|
| Stewart–Tijdeman 1986 | `c < exp( K1 · R^15 )` | [ST86] |
| Stewart–Yu 1991 | `c < exp( K2(eps) · R^(2/3 + eps) )` | [SY91] |
| **Stewart–Yu 2001 (best known)** | `c < exp( K · R^(1/3) · (log R)^3 )` | [SY01] |

The 2001 bound is the current world record. Note the shape: the conjecture asserts
`log c <= (1+eps) log R + O_eps(1)`; the theorem gives `log c << R^(1/3) (log R)^3`. The
proved bound is thus **exponentially** far from the conjecture — the gap is not one of
degree but of kind. Every application listed in §3.4 that "follows from abc" needs
`log c << (const) · log R`, and no known technique produces any bound of that shape.

Mechanism sketch `[KNOWN, sketch]`: for a prime p dividing (say) a, the valuation
`v_p(a) = v_p(c - b)` is the p-adic size of the "linear form" `(c/b) - 1`, where b and c
are built from the primes of R. Yu's p-adic analogue of Baker's theorem bounds this
valuation by an expression that contains the **product** `prod_{q | R} log q` over the
primes involved. Since R can have `~ log R / log log R` prime factors, this product can
be of size `exp(c · log R) = R^c`; balancing the three terms of the triple against each
other is what produces the exponent 1/3. The multiplicative dependence on the heights
of the individual logarithms is the structural source of the exponential loss — see
§4.2 and §7.2.

### 3.2 The proved model case: function fields (Angle 10-06)

**Mason–Stothers theorem `[KNOWN — PROOF INCLUDED in §6.1]`** (Stothers 1981 `(*)`,
Mason 1984): if a(t), b(t), c(t) are coprime polynomials over a field, not all constant,
with `a + b = c`, and not all of a', b', c' vanish, then

```
max(deg a, deg b, deg c) <= deg rad(abc) - 1,
```

where `rad(abc)` is the product of the distinct irreducible factors (over an
algebraically closed field: `n0(abc) - 1`, with n0 the number of distinct roots).

This is the *exact* function-field analogue of abc — with `eps = 0` and constant
absorbed into "-1" — and its proof is one page (Wronskian; reproduced in §6.1; there is
an even shorter proof due to Snyder [Sny00] `(*)`). Consequences in the polynomial
world include Davenport's inequality `deg(f^3 - g^2) >= (1/2) deg f + 1` for
non-degenerate polynomials and immediate "polynomial FLT" for degree >= 3. The
characteristic-p caveat is genuine: in characteristic p, `t^p + 1 = (t + 1)^p` gives
triples of unbounded degree with radical of degree 2, and the hypothesis on derivatives
excludes exactly such Frobenius-twisted examples. `[KNOWN]`

Why this does not transfer to Z is treated as Obstruction 1 in §4.1.

### 3.3 Lower bounds: how strong can abc possibly be? (Angles 10-02, 10-05, 10-08)

- **Epsilon is necessary `[KNOWN]`:** Stewart–Tijdeman [ST86] proved there are
  infinitely many coprime triples with
  `c > R · exp( k · sqrt(log R / log log R) )` for every `k < 4`; van Frankenhuysen
  [vF00] improved the constant to `k = 6.068`. Hence `c < K · R` is false for every K,
  and even `c < R · (log R)^A` is false for every A. A fully elementary proof of a
  qualitative version (`c > 0.60 · R · log c` infinitely often) is given in §6.2.
- **Refined conjecture `[CONJECTURE]`:** Robert–Stewart–Tenenbaum [RST14] conjecture
  that with `k = rad(abc)`,
  `c < k · exp( 4 · sqrt(3 log k / log log k) · (1 + o(1)) )`,
  and that the constant `4 sqrt(3)` is optimal. Defining the **merit** of a triple as
  `(q - 1)^2 · log R · log log R`, a two-line computation `[DERIVED HERE]` (substitute
  `log c - log R = 4 sqrt(3 log k / log log k)` into the definition) shows the RST
  conjecture predicts `limsup merit = 48`. This gives the computational program (§5.5)
  a sharp falsifiable target.
- **Computational record `[KNOWN]`:** the ABC@Home distributed project (Leiden;
  de Smit's tables [dS]) completed in 2011 the exhaustive enumeration of **all**
  14,482,065 abc hits with `c < 10^18`. Among numbers of at most 20 digits there are
  exactly 236 triples of quality >= 1.4 (per de Smit's list, as reported in the survey
  [arXiv:1409.2974]). Top of the all-time list:

| a | b | c | quality q | found by |
|---|---|---|-----------|----------|
| 2 | 3^10 · 109 | 23^5 | 1.6299 | Reyssat |
| 11^2 | 3^2 · 5^6 · 7^3 | 2^21 · 23 | 1.6260 | de Weger |
| 19 · 1307 | 7 · 29^2 · 31^8 | 2^8 · 3^22 · 5^4 | 1.6235 | Browkin–Brzezinski |

  No known triple has `q >= 1.63`, let alone 2. What this does and does not constrain
  is analyzed in §5.5.

### 3.4 Consequences of abc and their unconditional status (Angle 10-03)

The table records: what abc (or an effective/weak form) would give, and what is known
unconditionally today. This is the core of Angle 10-03. All rows `[KNOWN]` as
implications; the "unconditional status" column is the honest scoreboard.

| Consequence | What abc gives | Unconditional status today |
|-------------|----------------|----------------------------|
| Fermat's Last Theorem, large n | Weak-abc with exponent 2 (`c < R^2`, unproved) gives FLT for all `n >= 6` in five lines (§6.6); effective abc gives an explicit n0 | **Proved for all n >= 3** (Wiles 1995, Taylor–Wiles 1995) by modularity — not by abc |
| Mordell conjecture (finiteness of rational points on curves of genus >= 2) | Elkies [Elk91]: abc (over number fields) implies Mordell, **effectively** (via Belyi maps) | **Proved** (Faltings 1983), but **ineffectively**: no algorithm provably lists all rational points. Effective Mordell is open |
| Infinitude of non-Wieferich primes | Silverman [Sil88]: abc implies >> log x non-Wieferich primes up to x (any base) | **Open.** It is not even known unconditionally that infinitely many non-Wieferich primes exist; only 2 Wieferich primes (1093, 3511) are known despite searches beyond 10^17 `(*)` |
| Catalan's conjecture (`x^p - y^q = 1`) | Finiteness/effectivity follows from abc | **Proved** (Mihăilescu 2004); earlier Tijdeman 1976 `(*)` gave effective finiteness by Baker's method |
| Fermat–Catalan / Beal finiteness (`x^p + y^q = z^r`, `1/p + 1/q + 1/r < 1`) | abc implies only finitely many solutions (with coprime bases), uniformly in the exponents | **Open** in general. For each *fixed* exponent triple, finiteness is proved (Darmon–Granville 1995, via Faltings — ineffective) |
| Pillai's conjecture (`|x^p - y^q| -> infinity`; generalized Tijdeman) | Follows from abc | **Open** except the Catalan case |
| Hall's conjecture, weak form (`|x^3 - y^2| >> x^(1/2 - eps)`) | Follows from abc | **Open**; best known unconditional lower bounds are logarithmic-exponent improvements on Baker's method, far from x^(1/2-eps) |
| Erdős–Woods conjecture (radical-determines-neighborhood), finitely many exceptions | Follows from abc (Langevin [Lan93]) | **Open** |
| Only finitely many n with n-1, n, n+1 all powerful | Follows from abc (see §6.7 for the exact exponent threshold: any proved `c < R^theta` with `theta < 4/3` suffices) | **Open**; no triple of consecutive powerful numbers is known |
| Squarefree values of polynomials (density) | Granville [Gr98]: abc gives the expected density of squarefree values of any separable f | **Open** for degree >= 4; degree 3 is Hooley's theorem `(*)` |
| Siegel zeros | Granville–Stark [GS00]: *uniform abc over number fields* implies no Siegel zeros for L-functions of odd real characters | **Open** (this is one of the most striking conditional implications: abc touches L-functions) |
| Lang's height conjecture (lower bound for canonical height of non-torsion points) | Follows from Szpiro/abc (Hindry–Silverman) `(*)` | **Open** in general |
| Roth's theorem refinements | Bombieri (unpublished manuscript, 1990s) `(*)`: abc implies strengthened approximation exponents | Roth's theorem itself is **proved** (1955) but **ineffective** |
| Erdős–Ulam problem (no dense rational-distance set in the plane) | Negative answer follows from abc | **Open** |
| Effective Siegel theorem (integral points on curves) | Follows from effective abc | Siegel's theorem is proved; full effectivity **open** (known cases via Baker) |

Two honest morals `[STATUS]`:

1. Every *proved* row was proved by methods other than abc (modularity, Faltings,
   cyclotomic fields, Baker). abc would *unify and effectivize* them; it has so far
   *predicted* rather than produced.
2. The rows that remain open are open precisely because they need `log c << log R`
   strength; the proved Stewart–Yu bound (`log c << R^(1/3+o(1))`) is useless for every
   single row of this table except in "fixed radical" regimes (§6.5 exploits exactly
   that regime, which is the one place the proved bounds have real Diophantine content).

---

## 4. Main Technical Obstructions

### 4.1 Obstruction 1: no derivative on Spec Z (why Mason–Stothers does not transfer)

The one-page function-field proof (§6.1) uses the derivation `d/dt` in two essential
ways: (i) the Wronskian `W = a b' - a' b` is a *nonzero* object of *small degree*
(degree drops by at least 1); (ii) repeated factors are detected: `p^e || a` implies
`p^(e-1) | gcd(a, a')`. Over Z there is no map with the Leibniz property compatible
with addition — "carrying" in integer addition destroys any naive arithmetic
derivative. In geometric language: over a function field one has the Kodaira–Spencer
map / a nontrivial derivation of the base; `Spec Z` has no base to differentiate along
(the "absolute point" or "field with one element" is not available as mathematics).
Attempts to build substitutes (Buium's arithmetic differential characters via p-adic
Fermat quotients; Borger's lambda-ring point of view) produce genuine theories but, so
far, no small-height Wronskian-like invariant attached to an abc triple. `[HEURISTIC]`
as an explanation; the non-existence of a naive arithmetic derivative is elementary.

### 4.2 Obstruction 2: the multiplicative loss in linear forms in logarithms (Angle 10-09)

Baker-method lower bounds have the shape

```
|b1 log alpha1 + ... + bn log alphan| > exp( -C(n, d) · log A1 · log A2 · ... · log An · log B )
```

(archimedean; Baker–Wüstholz 1993 `(*)`, Matveev 2000 `(*)`), and Yu Kunrui's p-adic
versions have the same **product** `prod_i log Ai` (with an extra factor p). Applied to
an abc triple, the alphas run over the primes of R, so n ~ omega(R) can be as large as
`log R / log log R` and the product of the `log Ai` is genuinely exponential in a power
of log R. **This is not sloppiness; it is the known structural limit of the method.**
Stewart–Yu's exponent 1/3 is the result of optimizing against it. Baker himself
[Bak98] formulated the precise conjectural repair: a linear-forms bound in which the
product over the heights is replaced by an essentially additive/summed dependence would
yield an inequality of near-abc strength (radical to a bounded power, up to log
factors). No progress of that shape exists. `[KNOWN]` for the shape of the bounds and
for Baker's program; see §7.2.

### 4.3 Obstruction 3: ineffectivity of the geometric route

The geometric finiteness theorems that "morally" surround abc (Roth, Siegel via Roth,
Faltings) are ineffective: their proofs bound the *number* of solutions but provably
give no bound on their *height*, because they argue by contradiction from two
hypothetical large solutions. abc sits on the effective side of this divide (it *is* a
height bound). Any route to abc through Diophantine approximation must first crack
effectivity in Roth-type theorems — itself a famous open problem. `[KNOWN]`

### 4.4 Obstruction 4: the verification obstruction (specific to the IUT claim)

Distinct from the mathematical obstructions above: the only *claimed* proof of abc is
written in a formalism (IUT) whose crucial step has resisted independent verification
for 13+ years, with expert disagreement about whether the step is even well-posed as
written. Whatever the truth value of Corollary 3.12, the *checkability* failure is
itself now a recognized object of study (two Lean-formalization projects, §5.4.5). A
proof that cannot be transmitted is, operationally, not yet a proof for the
community. `[STATUS]`

---

## 5. Attack Vectors and Specialist Findings

### 5.1 Vector A — sharpen linear forms in logarithms (Angles 10-09, 10-10)

**State.** The entire proved upper-bound frontier (§3.1) is downstream of Baker/Yu
estimates. The known dependencies are multiplicative in the heights (§4.2).

**What would suffice `[KNOWN]`:** Baker [Bak98] shows that a refinement of the
linear-forms lower bound — of Lang–Waldschmidt type `(*)`, i.e. with the product
`prod log Ai` replaced by additive dependence — implies an explicit abc-type inequality
with the radical to a fixed power (up to logarithms). This is the single most concrete
conventional path: it converts abc into a problem *internal to transcendence theory*.

**Finding.** No new estimate is proved here. The legion's analysis (§6.7) quantifies
the payoff ladder: even `c < exp((log R)^A)` for some fixed A (still far weaker than
abc) would already break out of the current regime, and any proved polynomial bound
`c < K · R^theta` would immediately settle famous problems (theta < 4/3: consecutive
powerful numbers; theta = 2: FLT for n >= 6 reproved in five lines; any theta:
effective Mordell machinery via Elkies becomes quantitative). `[DERIVED HERE]`
(threshold arithmetic; routine).

### 5.2 Vector B — the modular route: Szpiro via modularity (Angle 10-10)

Since every elliptic curve over Q is modular, the Frey curve of a triple admits a
modular parametrization `phi: X0(N) -> E`. The **degree conjecture** — that
`deg phi << N^(2+eps)` — implies Szpiro's conjecture, hence abc-type inequalities
(Frey; see Goldfeld's survey [Gol02]). The modular degree is computable from the
symmetric-square L-function, so this route converts abc into growth estimates for
automorphic L-values — analytic number theory, not anabelian geometry. Unconditional
results bound `deg phi` polynomially in N only with exponents too large, and lower
bounds show the exponent 2 would be sharp. **Status: open, but fully conventional and
checkable; arguably the most "community-legible" known route to abc.** `[KNOWN]`

### 5.3 Vector C — the Vojta/Nevanlinna dictionary (Angle 10-07)

Vojta's analogy [Voj87] translates Nevanlinna value-distribution theory into
Diophantine statements: the Second Main Theorem *with truncated counting functions* for
maps to `P^1` relative to the divisor `{0, 1, infinity}` corresponds exactly to abc.
Interpretation `[KNOWN]`:

- An abc triple is an integral/rational point on the **three-punctured line**
  `P^1 - {0, 1, infinity}` (set `u = a/c`, `v = b/c`, `u + v = 1`, u and v S-units);
  the radical is the truncated counting function ("count each prime once").
- The three-punctured line is hyperbolic (its universal cover is the disk; its complex
  points admit no nonconstant entire curve — Picard's theorem). abc is the arithmetic
  shadow of Picard/Nevanlinna for this one hyperbolic curve. In Nevanlinna theory the
  truncated SMT for `P^1 - {0,1,infty}` **is a theorem**; abc asks for its arithmetic
  twin.
- **Elkies [Elk91]:** via Belyi maps (every curve over a number field maps to `P^1`
  ramified only over {0, 1, infinity} — Belyi 1979), abc *pulls back* to give the
  Mordell conjecture effectively, and van Frankenhuijsen [vF02] extended this to
  Vojta's height inequality for curves. So abc is not an isolated curiosity: it is the
  minimal case of the general Vojta conjectures, and it already carries the full
  strength of one-dimensional Diophantine geometry.
- Bombieri's unpublished manuscript "Roth's theorem and the abc-conjecture" `(*)`
  develops the approximation-theoretic side of the same dictionary.

**Finding.** This dictionary explains *why* abc is hard (it encodes hyperbolicity,
which archimedean analysis sees but arithmetic does not yet), and it certifies that any
proved abc-weakening automatically has geometric consequences. No new theorem here.

### 5.4 Vector D — the IUT program: precise status account (Angle 10-04) `[STATUS]`

This subsection is deliberately detailed; an accurate status account is one of the
mission's accepted deliverables. Nothing here endorses IUT as established, and nothing
here asserts that Corollary 3.12 is false — the verified fact is the absence of
community acceptance and the persistence of an unresolved, precisely-located dispute.

#### 5.4.1 Timeline of record

- **Aug 2012.** Mochizuki posts four preprints, *Inter-universal Teichmüller Theory
  I–IV* (~600 pages, on top of ~1000 pages of prerequisites from his earlier anabelian
  program), claiming a proof of the modified Szpiro conjecture, hence abc.
- **2015–2016.** Study workshops (Oxford, Kyoto). Outcome: a small group (largely
  around RIMS, plus e.g. Fesenko) asserts understanding and correctness; the broader
  expert community reports inability to extract the proof.
- **Mar 2018.** Scholze and Stix spend a week in Kyoto with Mochizuki and Hoshi; they
  then release the manuscript **"Why abc is still a conjecture"** (two versions, May and
  August 2018), asserting a gap: in their assessment, the derivation of **IUT-III
  Corollary 3.12** contains a step that cannot be correct as stated, and their
  simplified model of the log-theta-lattice yields no nontrivial inequality. Mochizuki
  publishes point-by-point rebuttals asserting the simplification destroys the content.
- **Apr 2020 / Mar 2021.** The four papers are accepted and published in
  *Publications of the RIMS* **57** (2021) — the journal of Mochizuki's own institute,
  where he is editor-in-chief (the journal stated he recused himself from the
  refereeing). Publication did **not** produce acceptance: leading number theorists
  publicly reiterated that the gap objection stands (Scholze restated it in a
  post-publication zbMATH review `(*)`).
- **2022.** Mochizuki–Fesenko–Hoshi–Minamide–Porowski publish "explicit estimates"
  ([ExpEst] `(*)`, Kodai Math. J.), claiming effective numerical versions of the
  inequalities (with applications announced to effective FLT-type statements). These
  inherit the disputed core: they are contingent on Corollary 3.12.
- **2023–2024.** Kirti Joshi posts an independent arXiv series ("Construction of
  Arithmetic Teichmüller Spaces", including a part titled as a proof of the
  abc-conjecture), proposing a reconstruction of the disputed mechanism. **Neither
  side accepts it**: Mochizuki published detailed objections, and Scholze also regards
  it as incorrect. In his own November 2025 status document [Jos25], Joshi describes
  his position on whether Mochizuki proved abc as "still open"/"currently neutral"
  while his preprints remain under consideration. `[DISPUTED]` on all sides.
- **Oct 2025.** Mochizuki posts a 90+ page "Report on the current situation
  surrounding IUT" [Moc25], reiterating: Scholze–Stix do not contest Theorem 3.11 (the
  multiradial algorithm); their assertion (his labels (SSA1)/(SSA2)) is that no
  nontrivial Diophantine consequence follows; and — in his view — their
  simplification has "no logical relationship" to the actual argument of Corollary
  3.12.
- **Mar 31, 2026.** **Project LANA** launches at ZEN University (Japan): a funded,
  semi-independent project to examine IUT with the Lean proof assistant, with domestic
  and international members.
- **Apr 2026.** Mochizuki's group (with Hoshi, Yamashita, Yang and others) posts its
  own formalization roadmap [MocForm26]: five stages, of which **Stage 1 is precisely
  "Theorem 3.11 implies Corollary 3.12"** — chosen, in the document's own words,
  because "this has received the most public attention". The document states the work
  is in the "early skeletal portion of Stage 1".
- **Jul 2026.** Project LANA's interim report [LANA26]: members were **"unable to reach
  complete consensus"**; "there are points that remain unclear in the process of
  deriving Corollary 3.12 from Theorem 3.11 in the third IUT paper"; the project
  **"continues to suspend judgment on whether a proof of the abc conjecture has been
  obtained through IUT theory"** and does not exclude the possibility that a
  mathematical gap exists. Press coverage [NS26] reports the majority expert view that
  a serious gap remains (with named dissent, e.g. Fesenko, who maintains the proof is
  complete and Scholze's assessment wrong).

#### 5.4.2 The claimed proof structure, neutrally described

1. **Reduction (prior work, [GenEll] `(*)`).** abc/Szpiro is reduced to a height
   inequality for elliptic curves in "initial theta-data" — one may work with a single
   suitable Frey-type curve and bound the height of its q-parameters.
2. **Hodge theaters (IUT-I).** Large categorical/anabelian scaffolds encoding the
   arithmetic of the fixed number field and curve, built via mono-anabelian
   reconstruction from étale fundamental groups (this part builds on Mochizuki's
   published and accepted anabelian geometry).
3. **Links (IUT-II, III).** Two non-scheme-theoretic "gluings" between Hodge theaters:
   the **log-link** (p-adic logarithms) and the **theta-link** (multiplying by theta
   values / rescaling one multiplicative monoid against another). The lattice of
   theaters connected by these links is the **log-theta-lattice**. The links
   deliberately do not respect the ring structures; only certain shared "cores"
   (realified Frobenioids, etc.) are transported.
4. **Multiradial representation (IUT-III, Theorem 3.11).** An algorithm asserted to
   describe the image of the "theta-pilot" object simultaneously up to three explicit
   indeterminacies (Ind1, Ind2, Ind3), in a container common to both sides of the
   theta-link.
5. **The key inequality (IUT-III, Corollary 3.12).** From the multiradial
   representation, a log-volume comparison is asserted: the degree of the theta-pilot
   is bounded by the log-volume of a certain hull, yielding `-deg <= bound`, i.e. the
   height inequality. **This is the step in dispute.**
6. **Numerics (IUT-IV).** The inequality is converted into Szpiro/abc-type inequalities
   with explicit constants.

#### 5.4.3 The dispute, stated precisely

- **Scholze–Stix position.** After unwinding the identifications made along the theta-
  and log-links (in their simplification: identifying the multiple "copies" of real
  numbers / of the relevant monoids that the formalism keeps distinct), the resulting
  inequality trivializes — the argument, they contend, cannot produce a nontrivial
  bound, so Corollary 3.12 is unproved; they locate the failure in the final pages of
  IUT-III. They explicitly do **not** dispute Theorem 3.11 as a construction
  ([Moc25] confirms this characterization from the other side).
- **Mochizuki position.** The identifications performed by Scholze–Stix are exactly
  what the theory prohibits; the distinct labels (his (n, m)-indexed theaters) are
  ordinary set-theoretic distinctness, and collapsing them changes the mathematics, so
  the Scholze–Stix simplification has, in his words, "no logical relationship" to the
  actual proof [Moc25].
- **The meta-problem.** Each side maintains the other has not engaged the actual
  argument. There is no agreed formal common ground on which the disagreement can be
  scored — which is precisely why both sides have now (2026) turned to machine
  formalization, where "what exactly is the statement of 3.12's proof obligation"
  must be made explicit.

#### 5.4.4 Where IUT is not yet checkable (the deliverable)

The checkability frontier, as of August 2026, is exactly this:

> **No third party has been able to expand the published proof of IUT-III Corollary
> 3.12 into a chain of statements each of which an independent expert (or a proof
> assistant) accepts.** The published text's proof of 3.12 is short (a few pages)
> and appeals to the multiradial representation of Theorem 3.11; the disputed content
> is whether the asserted simultaneous comparison across the theta-link survives the
> indeterminacies without collapsing. Everything upstream (anabelian reconstruction
> results, Frobenioids, the constructions of IUT-I/II, Theorem 3.11 as an algorithm)
> is regarded — even by critics — as either verifiable or at least conventional; the
> LANA report and the RIMS formalization plan both concentrate the open question in
> the single step 3.11 ⇒ 3.12. That both proponents and neutral verifiers now agree
> *on the location* of the contested step is the only genuine convergence of the last
> eight years.

Operational conclusion `[STATUS]`: until Stage 1 of either formalization effort (or an
equivalent human document) succeeds and is independently audited, **IUT does not
constitute a community proof of abc, and abc is open.** This dossier's mandate to "not
declare abc proved" is thus not merely policy; it is the factual state of the field.

### 5.5 Vector E — the computational program (Angle 10-08)

**What exists `[KNOWN]`:** the complete enumeration below 10^18 (14,482,065 hits,
[dS]), the all-time quality table (§3.3), and merit statistics.

**What the data constrains:**

1. **Explicit conjectures are falsifiable and survive.** Baker's explicit abc
   conjecture [Bak04] — `c < (6/5) · R · (log R)^omega / omega!` with omega the number
   of distinct primes of abc — survives the full corpus. So does the exponent-2 weak
   form (`c < R^2`): the maximum quality ever observed is 1.63. A single triple with
   `q >= 2` would refute weak-abc-2 and, with it, the five-line FLT argument of §6.6;
   none has been found.
2. **Lower-bound families are realized.** The elementary family of §6.2 and the
   Stewart–Tijdeman/van Frankenhuysen families are visible in the data as the
   persistent trickle of hits with merit bounded away from 0; the RST prediction
   `limsup merit = 48` (§3.3) is consistent with the observed record merits (upper
   thirties) while remaining unrefuted. `(*)` for the numerical value of the record
   merit.
3. **What the data cannot do.** abc is a statement about all sufficiently large
   triples; no finite computation can prove it, and the observed `q <= 1.63` is weak
   evidence about the limsup (quality converges extremely slowly; the RST secondary
   term `exp(4 sqrt(3 log k / log log k))` is enormous in the computable range).
   Computation's real roles: refuting explicit strengthened forms, calibrating the
   constants in conjectures like [RST14]/[Bak04], and supplying certified minimal
   counterexample thresholds for conditional theorems (as in FLT-style applications of
   explicit inequalities).

---

## 6. New Work of This Legion: Proofs, Derivations, Failed Attacks

**Honesty preamble.** Nothing in this section is claimed as a research novelty. Items
6.1–6.2 are classical theorems reproved in full (transparency deliverable). Items
6.3–6.5 are corollaries of the cited Stewart–Yu theorem, derived here completely; they
are routine and presumably folklore, but the derivations are self-contained and
checkable line by line, which is what the mission's "transparent argument" standard
requires. Item 6.6 is a classical conditional observation with full proof. Item 6.7
documents failed attacks and thresholds.

### 6.1 Proposition (Mason–Stothers) `[KNOWN — PROOF INCLUDED]`

*Let K be a field and let a, b, c in K[t] be pairwise coprime with `a + b = c`, not all
constant, and not all of a', b', c' zero. Then*

```
max(deg a, deg b, deg c) <= deg rad(abc) - 1.
```

**Proof.** For polynomials f, g write `W(f, g) = f g' - f' g`. Using `c = a + b`:

```
W(a, c) = a c' - a' c = a(a' + b') - a'(a + b) = a b' - a' b = W(a, b),
W(b, c) = b c' - b' c = b(a' + b') - b'(a + b) = -(a b' - a' b) = -W(a, b).
```

Set `W := W(a, b) = W(a, c) = -W(b, c)`.

*W is nonzero.* If W = 0 then `a b' = a' b`; since gcd(a, b) = 1, a divides a' ; as
deg a' < deg a this forces a' = 0, and symmetrically b' = 0, hence c' = a' + b' = 0,
contradicting the hypothesis.

*Repeated factors divide W.* Let p be an irreducible factor of a with `p^e || a`
(e >= 1). Then `p^(e-1) | a'` (differentiate `a = p^e u`), so `p^(e-1)` divides both
terms of `W = a b' - a' b`. Hence `a / rad(a)` divides W; similarly `b / rad(b)`
divides `W = W(a,b)` and `c / rad(c)` divides `W(b, c) = -W`. The three quantities are
pairwise coprime (a, b, c are), so

```
(abc) / rad(abc)  divides  W.
```

*Degree count.* W ≠ 0, so
`deg a + deg b + deg c - deg rad(abc) <= deg W <= deg a + deg b - 1`, giving
`deg c <= deg rad(abc) - 1`. The identities `W = W(a,c) = -W(b,c)` make the argument
symmetric in a, b, c (repeat the count with the other two pairings), so the same bound
holds for deg a and deg b. ∎

*Characteristic-p caveat (sharpness of the derivative hypothesis).* In characteristic
p, `t^p + 1 = (t+1)^p` is a coprime triple with max degree p and `deg rad = 2`; here
all derivatives vanish. This is why the hypothesis cannot be dropped, and it is the
first hint that the "derivative" is doing irreplaceable work — see §4.1.

### 6.2 Proposition (epsilon is necessary; infinitely many hits) `[KNOWN — PROOF INCLUDED]`

*For every integer k >= 1 the triple*

```
a = 1,   b = 3^(2^k) - 1,   c = 3^(2^k)
```

*is a coprime triple with* `rad(abc) < 3c / 2^(k+1)`. *Consequently there are
infinitely many abc hits, and*

```
c  >  (2 / (3 log 3)) · rad(abc) · log c      for all these triples,
```

*so no inequality of the form `c <= K · rad(abc)` holds with any constant K.*

**Proof.** Coprimality is clear (b = c - 1; also 3 does not divide b since
`b ≡ -1 mod 3`).

*Claim:* `v_2(3^(2^k) - 1) = k + 2` for k >= 1, where v_2 is the 2-adic valuation.
Base case k = 1: `3^2 - 1 = 8`, valuation 3 = 1 + 2. Induction step: factor

```
3^(2^(k+1)) - 1 = (3^(2^k) - 1) · (3^(2^k) + 1).
```

For k >= 1, `3^(2^k) ≡ 1 (mod 8)` (since 3^2 = 9 ≡ 1 mod 8 and squaring preserves
this), so `3^(2^k) + 1 ≡ 2 (mod 8)` has valuation exactly 1. Hence the valuation
increments by exactly 1, proving the claim.

Write `b = 2^(k+2) · m` with m odd. Then `rad(b) <= 2m = b / 2^(k+1)`, so

```
rad(abc) = rad(3 b) = 3 · rad(b) <= 3 b / 2^(k+1) < 3 c / 2^(k+1).
```

Since `log c = 2^k · log 3`, we have `2^(k+1) = 2 log c / log 3`, hence
`rad(abc) < (3 log 3 / (2 log c)) · c`, which rearranges to the display. As
`(2 / (3 log 3)) ≈ 0.6068`, each such triple with k >= 3 is a hit (indeed
`q(1, 80, 81) = log 81 / log 30 = 1.2920...` already at k = 2), and quality exceeding
1 occurs infinitely often. ∎

*Context.* The much stronger `c > R exp(6.068 sqrt(log R / log log R))` infinitely
often is [ST86]+[vF00]; the point of including this weaker but fully elementary
version is that it is verifiable by hand and already kills `eps = 0`.

### 6.3 Corollary (radical lower bound for abc triples) `[DERIVED HERE]`

*There is an effectively computable constant `kappa > 0` such that every coprime triple
`a + b = c` with `c >= 16` satisfies*

```
rad(abc)  >=  kappa · (log c)^3 / (log log c)^9 .
```

**Derivation** (from Stewart–Yu [SY01]: `log c <= K · R^(1/3) (log R)^3` with K
effective, `R = rad(abc) >= 2`).

Case 1: `R >= (log c)^3`. The claim holds with kappa = 1 since
`(log log c)^9 >= 1` for `c >= 16`.

Case 2: `R < (log c)^3`. Then `log R < 3 log log c`, so the Stewart–Yu bound gives
`log c <= 27 K · R^(1/3) (log log c)^3`, i.e.
`R >= (log c)^3 / ((27K)^3 (log log c)^9)`.

Take `kappa = min(1, (27K)^(-3))`. ∎

*Label check:* routine inversion of a cited effective theorem; effective; certainly
folklore; included because it is the sharpest *proved* "radical-bound lemma" this
legion can offer with a transparent argument, and it is the exact currency the mission
requested (a lower bound on the radical in terms of c).

### 6.4 Corollary (effective exponent bound for Fermat counterexamples) `[DERIVED HERE]`

*With K the effective Stewart–Yu constant: if `x^n + y^n = z^n` with pairwise coprime
positive integers and `n >= 3`, then*

```
n  <=  27 K · z · (log z)^2 .
```

**Derivation.** Apply [SY01] to the coprime triple `(x^n, y^n, z^n)`:
`n log z = log(z^n) <= K R^(1/3) (log R)^3` with
`R = rad(x^n y^n z^n) = rad(xyz) <= xyz < z^3` (as x, y < z). So `R^(1/3) < z` and
`log R < 3 log z`, giving `n log z <= 27 K z (log z)^3`; divide by log z (z >= 2). ∎

*Honesty:* FLT is a theorem (Wiles), so this adds nothing to knowledge of Fermat; the
value is illustrative — it shows the *proved* abc-weakenings bound a counterexample's
exponent polynomially in the size of its base, i.e. they have genuine (if weak)
Diophantine content, and similar Baker-method exponent bounds long predate this
dossier.

### 6.5 Corollary (fixed-base generalized Fermat: effective finiteness) `[DERIVED HERE]`

*Fix pairwise coprime integers `x, y, z >= 2`. Then every solution in exponents
`p, q, r >= 1` of*

```
x^p + y^q = z^r
```

*satisfies `max(p, q, r) <= K (xyz)^(1/3) (log(xyz))^3 / log 2`. In particular the set
of exponent triples is finite and effectively bounded — a proved, strictly weaker
abc-type statement with a genuine Diophantine consequence.*

**Derivation.** The triple `(x^p, y^q, z^r)` is coprime, with radical
`rad(x^p y^q z^r) = rad(xyz) <= xyz` — the exponents do not enter the radical, which is
the whole point. By [SY01], `log(z^r) <= K (xyz)^(1/3) (log(xyz))^3`, and the two
smaller terms are bounded by c = z^r, so also
`p log x, q log y <= K (xyz)^(1/3) (log(xyz))^3`. Divide by `log 2 <= log x, log y,
log z`. ∎

*Why this is the honest showcase:* in the "fixed radical, growing exponents" regime the
exponential-in-R^(1/3) bound is not a weakness — R is constant — and Stewart–Yu delivers
an unconditional, fully effective finiteness theorem that a naive reader would have
guessed requires abc. This is the mission's "Diophantine consequence following from a
strictly weaker abc-type inequality" — with the inequality being the *cited proved*
Stewart–Yu theorem rather than a new one; no new inequality is claimed.

### 6.6 Proposition (weak abc with exponent 2 implies FLT for n >= 6) `[CONDITIONAL — hypothesis unproved; argument classical]`

*Hypothesis (unproved "weak abc-2"): every coprime triple satisfies `c < rad(abc)^2`.
(Consistent with all 14.5 million known hits; max known quality 1.63.)*

*Claim: under the hypothesis, `x^n + y^n = z^n` has no solution in coprime positive
integers for any `n >= 6`.*

**Proof.** Given a solution, apply the hypothesis to `(x^n, y^n, z^n)`:

```
z^n < rad(x^n y^n z^n)^2 = rad(xyz)^2 <= (xyz)^2 < z^6 <= z^n,
```

using x, y < z and z >= 2. Contradiction. ∎

This classical observation (see Granville–Tucker [GT02]) calibrates how little of abc
is needed for spectacular consequences — and equally, that even this "little" is
unproved: the best proved exponent on R is not 2 but *exponential* (§3.1).

### 6.7 Failed attacks and the threshold ladder `[ANALYSIS — DERIVED HERE]`

Documented so the next legion does not repeat them:

1. **Consecutive powerful numbers via Stewart–Yu: fails.** If n-1, n, n+1 are all
   powerful, apply abc-type bounds to `(1, n^2 - 1, n^2)`; the radical satisfies
   `R <= rad(n^2-1) rad(n) <= sqrt(n^2-1) · sqrt(n) < n^(3/2)` (powerful m has
   `rad(m) <= sqrt(m)`). An inequality `c < K R^theta` gives `n^2 < K n^(3 theta/2)`,
   a contradiction for large n iff `theta < 4/3`. Stewart–Yu instead gives
   `2 log n <= K n^(1/2) (log n)^3` — vacuous. **Threshold: the first proved
   polynomial bound with exponent < 4/3 settles Erdős's consecutive-powerful problem
   (finiteness).**
2. **Improving the exponent 1/3 by re-balancing:** examined and abandoned. The 1/3 in
   [SY01] is already the optimum of the three-way balance against the multiplicative
   height-loss in Yu's p-adic estimates (§4.2); a fourth balancing object does not
   exist in a triple. Any improvement must come from inside transcendence theory
   (Baker's refinement program, §5.1), not from repackaging.
3. **Elementary radical-bound lemmas beyond §6.3:** attempts to prove any bound of the
   form `c <= F(R)` for an elementary explicit F *without* Baker's method fail at the
   first step: even the finiteness of triples with a fixed radical is the S-unit
   theorem, whose only known proofs are ineffective (Mahler-type) or Baker-based.
   There appears to be **no elementary route to any upper bound** — a fact worth
   recording as a boundary of the search space.
4. **Threshold ladder for a hypothetical proved bound `c < K · R^theta`:**
   - any fixed theta (however large): effective S-unit and Mordell machinery
     (via [Elk91]) becomes explicit with polynomial dependence; already revolutionary;
   - theta = 2: FLT for n >= 6 in five lines (§6.6); Beal-type finiteness for exponent
     triples with `1/p + 1/q + 1/r < 1/theta + something` regimes;
   - theta < 4/3: consecutive powerful numbers (item 1);
   - theta -> 1 + eps: full abc and the entire table of §3.4.
   This ladder is the legion's recommended metric for judging any future claimed
   partial result: *state the theta (or the shape of F) and read the payoff off the
   ladder.*

---

## 7. Honest Verdict, Open Directions, References

### 7.1 Verdict (per program taxonomy: known / incremental / candidate breakthrough / failed attack)

**Verdict: known / incremental.**

- The abc conjecture is **open**. `[STATUS]`
- No new inequality beyond the literature was proved by this legion. The new-to-this-
  dossier items (§6.3–6.5, §6.7) are transparent, effective, checkable derivations
  from Stewart–Yu 2001 and threshold analyses — useful bookkeeping, not breakthroughs,
  and explicitly not claimed as novel.
- The mission-critical deliverables that *are* fully met: an accurate statement corpus
  (§2), the exact proved exponents (§3.1), the consequence scoreboard (§3.4), a
  self-contained proof of the function-field theorem and of the necessity of epsilon
  (§6.1–6.2), a current and sourced account of exactly where the IUT claim is not yet
  checkable (§5.4), and the identification of the conventional-proof frontier (§7.2).
- **IUT is not endorsed as a proof; abc is not declared proved.** The 2026 state of
  affairs — both the proponents' own formalization roadmap and the independent LANA
  project concentrating on the single step 3.11 ⇒ 3.12, with LANA suspending judgment
  — is documented with primary sources.

### 7.2 What a conventional (non-IUT) proof would need (Angle 10-10)

Ranked by concreteness:

1. **Additive-height linear forms in logarithms.** Prove Baker-type lower bounds (and
   Yu-type p-adic ones) in which the product `prod_i log Ai` is replaced by additive
   dependence on the heights (Lang–Waldschmidt-type strength). Baker [Bak98] showed
   such bounds imply explicit near-abc inequalities. This keeps the entire proof
   inside classical transcendence theory. Nothing beyond the multiplicative regime
   has been proved in 50+ years — but partial de-multiplicativization (e.g. removing
   one log factor per prime) would already improve the Stewart–Yu exponent and would
   be a publishable breakthrough with a transparent statement.
2. **The modular degree conjecture** `deg(phi: X0(N) -> E) << N^(2+eps)` implies
   Szpiro, hence abc-type bounds ([Gol02], Frey). Equivalent to growth bounds for
   symmetric-square L-values; fully "checkable mathematics" and connected to standard
   analytic-number-theory technology (subconvexity culture). This is the route this
   legion recommends watching.
3. **An arithmetic Kodaira–Spencer / Wronskian.** Construct, for a coprime triple, an
   integer invariant W(a, b, c) that is provably nonzero and provably small (polynomial
   in R), with divisibility by `abc / rad(abc)` — the exact skeleton of §6.1. All
   known candidates (Buium's arithmetic derivatives, lambda-ring geometry) fail the
   "small height" requirement. Even a W with `|W| < exp((log R)^A)` would beat
   Stewart–Yu.
4. **Effectivize Roth/Faltings.** Any effective Roth-type theorem restructures the
   ineffectivity landscape (§4.3) and would open the Vojta-dictionary route (§5.3).
5. **For the IUT route specifically:** a self-contained, independently auditable
   derivation of the Corollary 3.12 inequality — now concretely instantiated as
   "complete Stage 1 of the Lean formalization and have it audited outside RIMS".
   Until then the claim remains unusable by the community, regardless of its ultimate
   truth value.

### 7.3 Concrete next steps for follow-on legions

1. Track and audit the two formalization efforts ([MocForm26], [LANA26]); any Lean
   artifact for "3.11 ⇒ 3.12" should be checked for *statement fidelity* (does the
   formalized statement actually express the height inequality?) before celebrating.
2. Run the RST merit statistic over de Smit's complete corpus [dS] and publish the
   empirical limsup trajectory against the predicted 48 (§3.3); this is a
   low-risk, genuinely useful data contribution.
3. Attempt the "one-log removal" sub-goal in Yu's p-adic estimates (item 1 of §7.2) as
   a bounded, well-posed transcendence-theory project; even a conditional statement
   ("additive linear forms imply abc with explicit constants", sharpening [Bak98])
   with modern constants would be a citable increment.
4. Formalize §6.1 (Mason–Stothers) and §6.6 in Lean as a warm-up corpus for abc-adjacent
   formalization — cheap, useful, and pedagogically valuable.

### 7.4 References

Peer-reviewed / classical (statements used are standard; `(*)` = bibliographic details
from memory, flagged in text where relied upon):

- [ST86] C. L. Stewart, R. Tijdeman, "On the Oesterlé–Masser conjecture", Monatshefte für Mathematik 102 (1986), 251–257.
- [SY91] C. L. Stewart, K. Yu, "On the abc conjecture", Mathematische Annalen 291 (1991), 225–230.
- [SY01] C. L. Stewart, K. Yu, "On the abc conjecture, II", Duke Mathematical Journal 108 (2001), 169–181.
- [vF00] M. van Frankenhuysen, "A lower bound in the abc conjecture", Journal of Number Theory 82 (2000), 91–95.
- [vF02] M. van Frankenhuijsen, "The ABC conjecture implies Vojta's height inequality for curves", Journal of Number Theory 95 (2002), 289–302.
- [Elk91] N. D. Elkies, "ABC implies Mordell", International Mathematics Research Notices 1991, no. 7, 99–109.
- [Sil88] J. H. Silverman, "Wieferich's criterion and the abc-conjecture", Journal of Number Theory 30 (1988), 226–237.
- [Gr98] A. Granville, "ABC allows us to count squarefrees", International Mathematics Research Notices 1998, no. 19, 991–1009.
- [GS00] A. Granville, H. Stark, "ABC implies no 'Siegel zeros' for L-functions of characters with negative discriminant", Inventiones Mathematicae 139 (2000), 509–523.
- [GT02] A. Granville, T. Tucker, "It's as easy as abc", Notices of the AMS 49 (2002), no. 10, 1224–1231.
- [RST14] O. Robert, C. L. Stewart, G. Tenenbaum, "A refinement of the abc conjecture", Bulletin of the London Mathematical Society 46 (2014), 1156–1166.
- [RT13] O. Robert, G. Tenenbaum, "Sur la répartition du noyau d'un entier", Indagationes Mathematicae 24 (2013), 802–914.
- [Bak98] A. Baker, "Logarithmic forms and the abc-conjecture", in: Number Theory (Eger, 1996), de Gruyter, 1998, 37–44.
- [Bak04] A. Baker, "Experiments on the abc-conjecture", Publicationes Mathematicae Debrecen 65 (2004), 253–260.
- [Gol02] D. Goldfeld, "Modular forms, elliptic curves and the abc-conjecture", in: A Panorama in Number Theory (Baker 60th birthday volume), Cambridge University Press, 2002, 128–147.
- [Oes88] J. Oesterlé, "Nouvelles approches du 'théorème' de Fermat", Séminaire Bourbaki exp. 694, Astérisque 161–162 (1988), 165–186.
- [Mas85] D. W. Masser, "Open problems", in: Proceedings of the Symposium on Analytic Number Theory, Imperial College London, 1985.
- [Lan93] M. Langevin, "Cas d'égalité pour le théorème de Mason et applications de la conjecture abc", C. R. Acad. Sci. Paris 317 (1993), 441–444.
- [Nit96] A. Nitaj, "La conjecture abc", L'Enseignement Mathématique 42 (1996), 3–24.
- [Fre97] G. Frey, "On ternary equations of Fermat type and relations with elliptic curves", in: Modular Forms and Fermat's Last Theorem, Springer, 1997, 527–548.
- [Voj87] P. Vojta, "Diophantine Approximations and Value Distribution Theory", Lecture Notes in Mathematics 1239, Springer, 1987.
- Mason 1984: R. C. Mason, "Diophantine Equations over Function Fields", LMS Lecture Note Series 96, Cambridge University Press, 1984.
- Stothers 1981: W. W. Stothers, "Polynomial identities and hauptmoduln", Quarterly Journal of Mathematics (Oxford) 32 (1981). `(*)`
- [Sny00] N. Snyder, "An alternate proof of Mason's theorem", Elemente der Mathematik 55 (2000), 93–94. `(*)`
- Belyi 1979: G. V. Belyi, "On Galois extensions of a maximal cyclotomic field", Izv. Akad. Nauk SSSR 43 (1979). `(*)`
- Wiles 1995 / Taylor–Wiles 1995: Annals of Mathematics 141 (1995), 443–551 and 553–572.
- Faltings 1983: "Endlichkeitssätze für abelsche Varietäten über Zahlkörpern", Inventiones Mathematicae 73 (1983), 349–366.
- Mihăilescu 2004: "Primary cyclotomic units and a proof of Catalan's conjecture", J. reine angew. Math. 572 (2004), 167–195.
- Darmon–Granville 1995: "On the equations z^m = F(x, y) and Ax^p + By^q = Cz^r", Bulletin of the LMS 27 (1995), 513–543.
- Baker–Wüstholz 1993: "Logarithmic forms and group varieties", J. reine angew. Math. 442 (1993), 19–62. `(*)`
- Matveev 2000: "An explicit lower bound for a homogeneous rational linear form in logarithms of algebraic numbers II", Izvestiya: Mathematics 64 (2000). `(*)`
- K. Yu, series on p-adic logarithmic forms and group varieties (1998–2007). `(*)`
- Tijdeman 1976: "On the equation of Catalan", Acta Arithmetica 29 (1976). `(*)`
- E. Bombieri, "Roth's theorem and the abc-conjecture", unpublished manuscript (1990s); cited here secondhand. `(*)`
- Lang 1990: S. Lang, "Old and new conjectured Diophantine inequalities", Bulletin of the AMS 23 (1990), 37–75. `(*)`

IUT-related primary and status sources (URLs live as of 2026-08-15):

- Mochizuki, "Inter-universal Teichmüller Theory I–IV", Publications of the RIMS 57 (2021).
- P. Scholze, J. Stix, "Why abc is still a conjecture", manuscript (May/August 2018), publicly available from the authors' webpages.
- [Moc25] S. Mochizuki, "Report on the current situation surrounding inter-universal Teichmüller theory (IUT)", October 2025. https://www.kurims.kyoto-u.ac.jp/~motizuki/IUT-report-2025-10.pdf
- [MocForm26] S. Mochizuki et al., "On the formalization of IUT: a preliminary progress report" (joint work in progress with Y. Hoshi, G. Yamashita, Y. Yang, et al.), April 2026. https://www.kurims.kyoto-u.ac.jp/~motizuki/Formalization%20of%20IUT%20(2026-04).pdf
- [LANA26] ZEN University, "Project LANA Interim Report on IUT Theory" (announcement and summary), July 2026. https://zen.ac.jp/news/zmcpostevent0717e
- [NS26] New Scientist, "Effort to solve biggest controversy in mathematics has made no progress" (2026). https://www.newscientist.com/article/2580313-effort-to-solve-biggest-controversy-in-mathematics-has-made-no-progress/
- [Jos25] K. Joshi, "Report on the Scholze–Stix–Mochizuki controversy" (status document, November 2025). https://sites.arizona.edu/kirti-joshi/files/2025/11/report-on-scholze-stix-mochizuki-controversy.pdf ; and the arXiv series "Construction of Arithmetic Teichmüller Spaces" (2023–2024). `[DISPUTED]`
- [ExpEst] S. Mochizuki, I. Fesenko, Y. Hoshi, A. Minamide, W. Porowski, "Explicit estimates in inter-universal Teichmüller theory", Kodai Mathematical Journal 45 (2022). `(*)` `[DISPUTED — contingent on IUT-III Cor. 3.12]`

Data:

- [dS] B. de Smit, ABC triples tables and the completed ABC@Home enumeration (14,482,065 triples with c < 10^18, completed 2011). https://pub.math.leidenuniv.nl/~smitbde/abc/
- [arXiv:1409.2974] "abc triples" (survey; source for the 236 high-quality-triple count and the Reyssat record). https://arxiv.org/abs/1409.2974

---

*End of LEGION 10 dossier. abc remains a conjecture.*
