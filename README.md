# Approval-based committee voting: manipulability, proportionality and the core

Computational checks for a Game Theory course project (Sharif University of Technology, 2026) on **approval-based committee elections**: each voter approves a set of candidates and a rule picks a committee of size *k*. Three rules are studied:
- **AV** (approval voting): the *k* candidates with the most approvals;
- **PAV** (proportional approval voting): maximises Σ H(|Aᵢ ∩ W|), with H the harmonic number;
- **CC** (Chamberlin–Courant): maximises the number of voters with at least one approved winner.

All scores use exact rational arithmetic (`fractions`), and ties are broken lexicographically so every example is reproducible.

## What each script does
| Script | Question | Method |
|---|---|---|
| `src/manipulability.py` | Can a voter gain by misreporting their approval set? | Exhaustive search over small profiles (n ≤ 3 voters, m ≤ 4 candidates) for a profitable deviation under AV, PAV and CC |
| `src/proportionality.py` | Which rules satisfy JR, PJR and EJR? | Exact axiom checkers plus randomised search for violations (e.g. a CC committee violating JR or PJR), and a check that PAV produces no EJR violation in the sampled instances |
| `src/core_stability.py` | Is there always a core-stable committee, and does PAV find it? | Verifies a published counterexample in which a PAV-optimal committee (k = 8) is not core-stable, then exhaustively checks small elections (m ≤ 5) for the existence of a core-stable committee |

```bash
python src/manipulability.py
python src/proportionality.py
python src/core_stability.py     # the m = 5 part takes longer
```

## How to read the results
The searches cover **small instances only**. A counterexample they find is a real counterexample. Not finding one is evidence for the cases tested, not a proof. The general facts used in the report (AV's strategy-proofness for this utility model, PAV satisfying EJR, the open question of whether the core is always non-empty and recent results for few seats) come from the literature cited in `report/report_fa.tex`, not from these scripts.

The report itself (Persian, XeLaTeX with `xepersian`) is in `report/`.

## License
MIT, see [LICENSE](LICENSE).
