# Thesis-level v1.1 review and completion status

This package applies the remaining thesis-level checks requested after draft_9. It does not implement the separate repository code mirrors for cost/fallback/telemetry functions; those should be handled in the source-code repository as the next code-level task.

## Build status

- `pdflatex -interaction=nonstopmode -halt-on-error main.tex` completed successfully.
- A second `pdflatex` pass completed successfully.
- No unresolved equation references such as `Eq. (??)` remain.
- No multiply-defined labels remain after cleaning auxiliary files and recompiling.
- Remaining build note: one minor LaTeX font substitution warning for small-caps italic Latin Modern; this does not block the thesis-level draft.

## v1.1 thesis-level patch status

| # | Patch item | Status in this package |
|---:|---|---|
| 1 | Define `T_rot` / `T_token` | Closed at thesis level. |
| 2 | Define `Delta_min` and pre-result method | Closed at thesis level. |
| 3 | Uniform coefficient convention for beta, omega, psi, zeta; separate kappa sensitivities | Closed at thesis level. |
| 4 | Bridge SDE `sigma_k` to epoch estimator `sigma_hat^2_{k,tau}` | Closed at thesis level. |
| 5 | Operational definitions for CMDP cost terms | Closed at thesis level via cost-term table. |
| 6 | Define `B_curr`, `B_nominal`, telemetry coefficients | Closed at thesis level; Eq. 5.1 now uses `kappa_B` and `kappa_CPU`. |
| 7 | Fallback when `U_safe(x)=emptyset` | Closed at thesis level; fallback tied to Online/Degraded/Isolated survivability. |
| 8 | Threat/adversary model | Closed at thesis level in Chapter 7. |
| 9 | Complexity/control-overhead paragraph for Algorithms 1-3 | Closed at thesis level in Chapter 6. |
| 10 | PPO/function-approximation caveat | Closed at thesis level in Chapter 4. |
| 11 | Multiple-comparison correction | Closed at thesis level using Holm-Bonferroni; BH reserved for exploratory secondary analysis. |
| 12 | `make check-env` | Not in this LaTeX package; user reported already completed in repository. |
| 13 | LaTeX manuscript under version control | This package is structured for direct placement under the repository's manuscript directory. |

## Important remaining work outside this thesis-level package

1. Add code mirrors for:
   - CMDP cost function operational terms.
   - `U_safe(x)=emptyset` fallback.
   - telemetry throttle coefficients `kappa_B`, `kappa_CPU`.
   - LEO backoff coefficients `kappa_RTT`, `kappa_drop`.
2. Add unit tests for those code mirrors.
3. Begin the minimum vertical prototype only after the thesis-level v1.1 patch is committed.
