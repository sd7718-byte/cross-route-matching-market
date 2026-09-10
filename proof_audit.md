# Proof and computation audit

## Machine-checked scope

`formal/ProofAudit.lean` was accepted without warnings by Lean 4.29.0 using
Mathlib v4.29.0. The kernel-checked lemmas cover:

1. the dynamic choice-gap factorization;
2. positivity of the material loss below the calibrated conversion cutoff;
3. the paired contraction inequality used for two-sided uniqueness; and
4. strict match-volume monotonicity when acceptance falls.

Re-run from the repository root:

```bash
lake env lean cross-route-matching-paper/formal/ProofAudit.lean
```

## Numerical scope

`replicate.py` uses bracketed bisection and assertions to check every reported
cutoff and numerical value. It also verifies all fixed-point residuals, the
stability classification of each equilibrium, and the four fold conditions in
the numerical illustration.

```bash
python3 cross-route-matching-paper/replicate.py
```

## Analytic scope not formalized

Brouwer existence, the implicit-function comparative statics, and the local
saddle-node theorem are proved conventionally in the manuscript. The numerical
instance of the fold is checked, but the full implicit-function theorem is not
formalized in Lean.

Kernel checking is stronger than an internal algebra review, but it is not an
independent economist's assessment of assumptions, novelty, interpretation, or
journal fit. Before submission, a theorist who did not draft the paper should
still read the full proofs and record any objections here.

External reader: `[NAME]`  
Date reviewed: `[DATE]`  
Disposition: `[PASS / REVISE]`  
Notes: `[NOTES]`

