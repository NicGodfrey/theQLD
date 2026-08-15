# TOP-10 Unsolved Conjectures Research Program

Ten parallel research legions (01–10), each running Claude Fable 5 at maximum thinking (`claude-fable-5-thinking-xhigh`), with nested specialist subagents.

This is **not** a claim that any Millennium Prize problem has been solved. Each dossier records:

- the precise statement and known partial results
- the main technical obstructions
- attack vectors pursued by the nested specialists
- any lemmas, reformulations, or special-case results that appear new
- an honest verdict: known / incremental / candidate breakthrough / failed attack

| Legion | Conjecture | Directory |
|--------|------------|-----------|
| 01 | Riemann Hypothesis | `conjectures/01-riemann/` |
| 02 | P vs NP | `conjectures/02-p-vs-np/` |
| 03 | Birch and Swinnerton-Dyer | `conjectures/03-bsd/` |
| 04 | Hodge Conjecture | `conjectures/04-hodge/` |
| 05 | Navier–Stokes existence and smoothness | `conjectures/05-navier-stokes/` |
| 06 | Yang–Mills existence and mass gap | `conjectures/06-yang-mills/` |
| 07 | Twin Prime Conjecture | `conjectures/07-twin-primes/` |
| 08 | Collatz Conjecture | `conjectures/08-collatz/` |
| 09 | Goldbach Conjecture | `conjectures/09-goldbach/` |
| 10 | abc Conjecture | `conjectures/10-abc/` |

See [`SYNTHESIS.md`](SYNTHESIS.md) for the cross-legion briefing.

**Execution note.** Ten Fable-5-max parent agents were launched in parallel. Child environments do not expose a nested Task tool, so each legion ran its ten specialist angles itself. Legion 01 (Riemann) timed out twice as a child; the parent commander wrote that dossier. **None of the ten conjectures is claimed as proved.**
