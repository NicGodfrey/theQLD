# Wave 3 — original notes (not surveys)

Ten short papers under `research/theory/`. Each is a proof. None of the ten conjectures is solved.

## What was actually proved

| Note | Statement | Novelty vs literature |
|------|-----------|------------------------|
| `01-li-detection.md` | Off-line Li increment \(T_n=4-4\cosh(n\lambda)\cos(n\theta)\); first \(T_n\le-1\) at \(n_{\det}\asymp\gamma^2/\delta\) with sharp constant \(2\log 2\) | New closed form + two-sided law (finite-dimensional analysis; no ζ used) |
| `02-probe-adaptivity.md` | Adaptive = nonadaptive probe complexity: \(D=D^{na}=u(C)\) | Elementary; folklore-adjacent; settles a gap Wave 2 left open |
| `03-selmer-family.md` | 2-isogeny descent for \(y^2=x^3+p^2x\), \(p\equiv5\pmod8\): rank 0, \(E(\mathbb{Q})\simeq\mathbb{Z}/2\) | Classical method on a family Wave 2 did not treat |
| `04-product-cycles.md` | Hodge classes on \(C\times D\) are graphs of Jacobian morphisms | Classical theorem; correspondence proof, not Lefschetz (1,1) |
| `05-enstrophy-log.md` | Number of almost-blow-up windows \(\le M^2\|u_0\|_2^2/\nu^4+1\) | Quantitative assembly of classical energy/enstrophy |
| `06-z2-gap.md` | Explicit Ising gap \(m(\beta)=\ln(1/(4\tanh\beta))\) for \(\beta<\mathrm{artanh}(1/4)\); 2D \(\mathbb{Z}_2\) gauge solved | Classical; complete write-up with explicit rate |
| `07-radial-maynard.md` | \(M_2^{\mathrm{rad}}=8/j_{0,1}^2=1.38332\ldots\) exactly | New exact evaluation of a restricted Maynard functional |
| `08-cycle-congruence.md` | No Collatz cycle lives in \(3\pmod4\); a \(1\pmod4\) or \(1\pmod3\) cycle is trivial | Elementary; computation-free modular constraints |
| `09-goldbach-twin-energy.md` | \(\sum R_N(n)^2=\sum T_N(h)^2\) exactly; \(L^2\) equienergetic with twins | Parseval identity made exact + \(L^2\) corollaries |
| `10-quality-family.md` | Pell family \((1,8y_k^2,x_k^2)\) has \(q>1+1/(11k)\) for every \(k\) | Unconditional infinite family with proved quality \(>1\) (not a fixed \(\delta>0\); that would refute abc) |

## Honest rank of originality

These are **pure-theory notes**, not surveys. The statements that are most likely new *as written* are 01 (two-sided Li detection with the cosh-cos formula), 07 (exact radial Maynard value), 08 (the modular collapse for Syracuse cycles), and 10 (explicit Pell quality rate). The others are complete proofs of statements experts would call standard or folklore.

That is what this compute was for: theorems with proofs, not literature maps. It is still not a Clay-scale breakthrough.
