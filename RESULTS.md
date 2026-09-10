# Reproduction results

Unlike the two trading-research repositories, this project has a complete
deterministic numerical reproduction and a scoped machine-checked proof audit.

## Numerical reference output

`python3 replicate.py` verifies the equilibrium values, root classification,
fixed-point residuals, and fold conditions. The committed reference case gives:

| Quantity | Value |
| --- | ---: |
| Calibrated cutoff, `gamma_star` | 0.3535353535 |
| Subjective cutoff, `pi_star` | 0.7588383838 |
| True threshold | 8 |
| Subjective threshold | 4 |
| Distortion mass | 0.2015049566 |
| Expected loss | 0.0200576429 |

The script terminates with `all_residual_checks=PASS`; assertions fail the run
if a stated numerical condition is violated.

## Machine-checked scope

`lake env lean formal/ProofAudit.lean` checks four algebraic and order-theoretic
lemmas used by the paper: the choice-gap identity, positive inefficient-delay
loss, the two-sided contraction core, and match-volume monotonicity.

The proof audit does not formalize Brouwer existence, the full implicit-function
argument, or the local saddle-node theorem. Those limitations are stated in
`proof_audit.md` and should not be omitted when describing the work.

