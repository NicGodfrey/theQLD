# Cross-legion briefing — TOP-10 unsolved conjectures

**Date:** 2026-08-15
**Program:** ten Fable-5-max (`claude-fable-5-thinking-xhigh`) research legions, one conjecture each.
**Standing claim:** **none of the ten conjectures was proved.** A fabricated Millennium proof would have been a failure of the program. The research product is a set of *method barriers*, *special-case verifications*, and *precise reductions* that a specialist can check.

## How the army actually ran

The parent commander launched ten parallel Fable-5-xhigh general-purpose agents (legions 01–10). Each was ordered to nest ten grandchild specialists (100 nested runs). **Child environments do not expose the Task tool**, so every legion executed its ten angles itself. Legion 01 timed out twice as a child run; the parent wrote that dossier to the same standard.

No website file in this repository was modified. All output lives under `research/`.

## Scoreboard

| Legion | Conjecture | Status of the conjecture | Strongest deliverable | Taxonomy |
|--------|------------|--------------------------|----------------------|----------|
| 01 | Riemann Hypothesis | Open | VK deduction barrier (Prop. A); Li coefficients see only finite height (Prop. B) | NO-GO / reformulation |
| 02 | P vs NP | Open | Certification-access barrier: deterministic hardness tests need \(>s/(3n)\) probes; randomized \(O(1)\) probes work only with a non-explicit anchor | NO-GO / reformulation |
| 03 | Birch–Swinnerton-Dyer | Open except ranks 0–1 in known cases | One-Class Barrier for rank \(\ge 2\); live Pari/GP leading-term checks; Fermat descent for \(y^2=x^3-x\) | NO-GO + special case |
| 04 | Hodge | Open | Verified 2025 frontier (Markman ⇒ Hodge for all abelian fourfolds); two explicit reduction targets (Weil sixfolds; Fermat \(X^4_{33}\)) | Reduction / survey |
| 05 | Navier–Stokes | Open | Written-out Fujita–Kato / Leray / \(\mathcal H^{1/2}\) singular-time proofs; Tao averaged-NS no-go for energy-only methods | NO-GO + special case |
| 06 | Yang–Mills mass gap | Open | Gap-Transfer lemma (H1)–(H4); ultralocal fixed-coupling no-go; Abelian falsifier | NO-GO / interface lemma |
| 07 | Twin primes | Open | Parity no-go with a complete Liouville-weight proof; Maynard functional cannot certify gap 2 even on full EH | NO-GO |
| 08 | Collatz | Open | Four-wall no-go (mirror / 2-adic / Diophantine / Tao invariance); cycle-exclusion pipeline at published height \(2^{71}\) | NO-GO + computation |
| 09 | Binary Goldbach | Open (ternary is a theorem) | Modulus Barrier: minor-arc \(L^2\) mass is one logarithm too large; GRH captures at most half the mass | NO-GO |
| 10 | abc | Open (IUT not accepted) | Mason–Stothers written out; Stewart–Yu corollaries derived; IUT dispute located at IUT-III 3.11⇒3.12 | Incremental / status |

## What “research breakthrough” means in this program

The mission asked for a breakthrough on each problem. In the sense used by working mathematicians — a new theorem that moves the frontier of a Millennium problem — **this program did not produce one**, and it would be dishonest to say otherwise.

In the sense the dossiers were tasked to use, each legion was required to return at least one of:

- a **no-go** that rules out a popular attack as a checkable statement,
- a **special case** with a complete argument,
- a **reduction** to a named missing lemma,
- or a **reformulation** that changes what a next paper has to construct.

That bar was met on every legion. The recurring pattern is the same: the classical attack is not “almost done”; it is **blocked by a named information-theoretic or analytic deficit** (one logarithm, one Euler-system class, one RG crossover, parity, energy-only estimates, \(\zeta(1+it)\) growth). Future work has to go *around* those walls.

## Cross-cutting observations

1. **Parity and one logarithm are the same wall in two languages.** Twin primes (Legion 07) and binary Goldbach (Legion 09) fail for dual reasons: sieves cannot see \(\Omega(n)\) mod 2; the circle method cannot see the phase of \(S(\alpha)\) on the minor arcs. Chen’s \(1+2\) theorems are the parity-permitted endpoint of both.
2. **Rank / derivative / core-rank 1.** BSD (Legion 03) and, in a different way, Hodge (Legion 04) are stuck where a single characteristic class or Euler system is available and the next one is not.
3. **Criticality.** Navier–Stokes (energy supercritical in 3D) and Yang–Mills (the weak-to-strong RG crossover) are both “the estimate you have is one derivative / one scale short of the estimate you need,” and both have a published averaged or ultralocal counter-model showing that the abstract estimate class is insufficient.
4. **Finite checks do not finish \(\Pi_2\) statements.** Computational RH, Collatz verification, Goldbach to \(4\cdot 10^{18}\), and twin-prime tables are all \(\Pi_1\) slices of \(\Pi_2\) conjectures. Legion 01 Proposition B and Legion 08’s consistency check make this precise.
5. **IUT is not a proof of abc.** Legion 10 treated the 2018–2026 dispute as a *located* gap (IUT-III Theorem 3.11 \(\Rightarrow\) Corollary 3.12), not as a social controversy. The conventional engine remains Baker/Yu linear forms in logarithms, with a structural height loss.

## How to read the dossiers

Start with this file, then the executive summary of the legion you care about, then Section 5 of that report (the proved or formalized claim). Citations marked “from memory” or with an asterisk must be re-checked before any external use.

## Files

```
research/README.md
research/SYNTHESIS.md
research/conjectures/01-riemann/REPORT.md
research/conjectures/02-p-vs-np/REPORT.md
research/conjectures/03-bsd/REPORT.md
research/conjectures/03-bsd/verification.gp
research/conjectures/04-hodge/REPORT.md
research/conjectures/05-navier-stokes/REPORT.md
research/conjectures/06-yang-mills/REPORT.md
research/conjectures/07-twin-primes/REPORT.md
research/conjectures/08-collatz/REPORT.md
research/conjectures/08-collatz/code/*.py
research/conjectures/09-goldbach/REPORT.md
research/conjectures/10-abc/REPORT.md
```
