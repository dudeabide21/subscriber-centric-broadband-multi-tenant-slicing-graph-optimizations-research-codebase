# Two-machine workflow

## Roles
- Fedora PC/server: coding, experiments, data processing, and test execution.
- Laptop: LaTeX, diagrams, proposal editing, and review.

## Git branches
- `main`
- `dev`
- `paper`
- `experiments`

## Operating rules
- Clone the repository on both machines.
- Use Git as the sync point.
- Keep raw data out of Git.
- Use `data/raw/` only locally.
- Use `paper/latex/` for the manuscript.
- Use `docs/` for protocols and formulas.
- Commit code and paper work separately.

## Suggested workflow
1. Code on Fedora.
2. Run tests on Fedora.
3. Commit code.
4. Pull on the laptop.
5. Edit paper and diagrams.
6. Commit paper changes on the paper branch.
7. Merge after review.
