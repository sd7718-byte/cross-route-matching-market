# Cheap Attention, Costly Commitment

[![CI](https://github.com/sd7718-byte/cross-route-matching-market/actions/workflows/ci.yml/badge.svg)](https://github.com/sd7718-byte/cross-route-matching-market/actions/workflows/ci.yml)

This folder contains an anonymous theory paper on cross-route inference in a
two-period matching market with endogenous short-term offers and two-sided
long-term participation.

Files:

- `main.tex` — anonymous manuscript, equilibrium results, predictions, and proofs.
- `references.bib` — verified bibliographic metadata and DOI fields.
- `replicate.py` — dependency-free reproduction plus numerical residual tests.
- `formal/ProofAudit.lean` — Lean/Mathlib audit of the algebraic proof core.
- `proof_audit.md` — verification coverage and external-review sign-off fields.
- `literature_matrix.md` — closest-literature novelty boundary.
- `submission/` — cover letter, title page, declarations, highlights, checklist.
- `output/pdf/cheap-attention-costly-commitment.pdf` — compiled submission-style
  manuscript.

To reproduce the numerical table:

```bash
python3 replicate.py
```

To compile after installing a TeX distribution:

```bash
tectonic main.tex
```

or:

```bash
latexmk -pdf main.tex
```

To run the machine-checked proof audit from the repository root:

```bash
lake env lean formal/ProofAudit.lean
```

The current author field is anonymized for review. Replace `Anonymous` only in
a non-blinded submission copy. The bracketed fields in `submission/` require
the author's identity, affiliation, funding, conflict, and acknowledgment
information. A human theory reader should still independently review the full
proofs before journal submission.
