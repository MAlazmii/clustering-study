# Validation status

The current local build has 57 passing pytest cases. This includes regression
checks for all issues identified by an independent source/evidence review:
full source fingerprint equality, replay of iteration/convergence/history and
reference results, numerical underflow limits, and final completion written only
after evidence validation succeeds.

| Requirement | Status | Evidence / boundary |
|---|---|---|
| Original coursework protected | PASS | Independent new repository; no copied assessment source/data |
| Hand-computed numerical cases | PASS locally | Known means, labels and SSE; one/all clusters |
| Library reference agreement | PASS locally | Identical starting centers, explicit single start and zero tolerance |
| Input and resource contract | PASS locally | Invalid values, k, limits, seed, shape and magnitude tests |
| Duplicate/empty cluster behavior | PASS locally | Relocation, row preservation and final mean/assignment checks |
| Iteration exhaustion | PASS locally | Explicit non-convergence and nearest-label contract |
| Evidence integrity | PASS locally | Tampering, exact source map, replay, hashes and no overwrite |
| Complete 225-fit study | PASS locally | 225/225 converged, 150/150 reference partitions agree; measured commit `19ea04f` |
| Second-run numerical reproduction | PASS locally | All 225 fits exactly reproduced in the same environment; `results/published/reproduction.json` |
| Figures | PASS locally | Actual evidence plots, fixed-seed gallery, visual inspection |
| GitHub Linux workflow | NOT RUN | Prepared bounded CPU workflow; no remote created yet |
| Public release | NOT RUN | Requires GitHub validation and publication review |

The full record includes exact source fingerprints and commit, generated arrays,
all memberships/centroids, scores, initialization, convergence/iteration metadata,
library reference outputs and fit timings. Verification recomputes records with
the current matching source and dependencies, including custom and reference fits.
It is a consistency check, not a cryptographic authenticity or timing certificate.

A test pass certifies the exercised contract only. It does not establish optimal
partitions, generalization to real data, production-scale performance or universal
bitwise portability across libraries/platforms. Same-environment numerical replay
and actual remote Linux results must be labelled separately.

## Recorded run and scope

Both complete measurement runs used clean commit
`19ea04fbf9828d7d1a66830339a38a2049a40a6f` (see `results/published/study.json` for the full SHA).
Later additions package results, add the comparison utility and adjust plot limits;
the algorithm/runner fingerprints still match the measured source.
The independent review also stress-tested 1,200 seeded discrete-data fits without
finding an increasing objective or converged centroid/occupancy violation. This
supplements the committed tests; it is not a formal proof over every valid input.

A separate clean checkout passed the documented quick-start tests and a nine-fit
CI-sized run plus figure generation, using an offline venv with the installed
pinned packages inherited. This was a Mac check, not a clean Linux installation.
The primary record and all 15 generated arrays are included. The second raw run
remains local; its SHA and an exact numerical comparison digest are preserved in
the reproduction record. A future reader can generate their own second run and
compare using `scripts/compare_runs.py`.
