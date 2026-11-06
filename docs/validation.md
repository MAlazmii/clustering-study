# Validation status

The current local build has 56 passing pytest cases. This includes regression
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
| Complete 225-fit study | Pending final reviewed-source rerun | Earlier development run retained locally |
| Second-run numerical reproduction | Pending final reviewed-source rerun | Timings excluded from equality claim |
| Figures | Prepared | Actual evidence plots, fixed-seed gallery, visual inspection |
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
