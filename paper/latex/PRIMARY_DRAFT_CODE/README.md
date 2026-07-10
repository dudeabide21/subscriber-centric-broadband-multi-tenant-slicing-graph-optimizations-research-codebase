# Modular Q1 Proposal LaTeX Project

Compile from this folder:

```bash
pdflatex main.tex
pdflatex main.tex
```

## Structure

- `main.tex` - project entry point
- `config/preamble.tex` - packages and formatting
- `config/macros.tex` - shared notation and macros
- `frontmatter/` - title page and abstract
- `chapters/` - one file per chapter
- `figures/architecture_clean.tex` - clean TikZ architecture diagram
- `backmatter/references.tex` - embedded bibliography

## Major mathematical corrections included

1. Finite queue implementation model separated from auxiliary infinite-buffer LDT model.
2. Diffusion coefficient defined as a variance rate.
3. Effective bandwidth root uses supremum definition; unique root only when crossing conditions hold.
4. LDT no longer claims to guarantee cross-slice isolation.
5. CMDP uses cost minimisation consistently.
6. Safe actions are state-dependent: `U_safe(x)`.
7. Bellman equation uses expectation over continuous/high-dimensional graph states.
8. LEO backoff is normalised and clipped.
9. HMAC CPU claims are empirical acceptance criteria, not guarantees.
10. Wi-Fi PINN validation uses RSSI/floor-plan data, not terrain-grid data.


## v1.1 thesis-level patch status

This package includes the thesis-level v1.1 fixes for undefined symbols, coefficient
normalisation, LEO/telemetry coefficient disambiguation, CMDP cost operationalisation,
empty-safe-action fallback, PPO function-approximation caveat, multiple-comparison
correction, algorithmic overhead, and threat/adversary model. Code-level mirrors for
cost/fallback/telemetry functions should be added in the implementation repository as
separate source-code tasks.
