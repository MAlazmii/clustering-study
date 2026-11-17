# Validation status

The test suite checks source fingerprints, replay of iteration and convergence
metadata and reference results, numerical underflow limits, and final completion
written only after evidence validation succeeds. It also covers replay of the
unchanged archived study after verification and test dependencies are updated.

| Requirement | Status | Evidence / boundary |
|---|---|---|
| Original coursework protected | PASS | Independent new repository; no copied assessment source/data |
| Hand-computed numerical cases | PASS locally | Known means, labels and SSE; one/all clusters |
| Library reference agreement | PASS locally | Identical starting centers, explicit single start and zero tolerance |
| Input and resource contract | PASS locally | Invalid values, k, limits, seed, shape and magnitude tests |
| Duplicate/empty cluster behavior | PASS locally | Relocation, row preservation and final mean/assignment checks |
| Iteration exhaustion | PASS locally | Explicit non-convergence and nearest-label contract |
| Evidence integrity | PASS locally | Tampering, source fingerprints, replay, hashes and no overwrite |
| Complete 225-fit study | PASS locally | 225/225 converged, 150/150 reference partitions agree; measured commit `19ea04f` |
| Second-run numerical reproduction | PASS locally | All 225 fits exactly reproduced in the same environment; `results/published/reproduction.json` |
| Figures | PASS locally | Actual evidence plots, fixed-seed gallery, visual inspection |
| GitHub Linux workflow | PASS | [Recorded run at `5aebaf8`](https://github.com/MAlazmii/clustering-study/actions/runs/42270230598): 57 tests, two full 225-fit studies, exact numerical comparison and figures |
| Release checks | Commit-specific | See [workflow results](https://github.com/MAlazmii/clustering-study/actions/workflows/checks.yml) for the exact revision being used |

The full record includes exact source fingerprints and commit, generated arrays,
all memberships/centroids, scores, initialization, convergence/iteration metadata,
library reference outputs and fit timings. Verification requires new records
to match the current source fingerprints. For the archived study it checks the
exact published record digest, original algorithm source, and recorded numerical
dependency versions. Both paths replay generated data, custom fits and reference
fits. Verification establishes numerical consistency. Fit timings remain the
original recorded measurements.

A test pass certifies the exercised contract only. It does not establish optimal
partitions, generalization to real data, production-scale performance or universal
bitwise portability across libraries/platforms. Same-environment numerical replay
and actual remote Linux results must be labelled separately.

## Recorded run and scope

Both complete measurement runs used clean commit
`19ea04fbf9828d7d1a66830339a38a2049a40a6f` (see `results/published/study.json` for the full SHA).
Later revisions package results, add the comparison utility, update plotting and
test dependencies, and preserve the archived measurements as recorded. The
archived record digest is
`939afc1bcacfd102d9bcc7c4cdd53caccce24a4c3a216a120658bb396856b4c3`.
Its original source fingerprints remain in `results/published/study.json`.
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

## GitHub Linux validation

The first private GitHub validation completed successfully on 6 November 2026
at commit `5aebaf8aa51f49a5d8ceefcb6a42972dd5692f35`. All 57 tests passed;
each of two complete studies had 225 converged fits and 150 matching reference
partitions. Their inputs and numerical outputs reproduced exactly, excluding
timing. Both figures and the downloadable evidence artifact were generated.

The workflow has read-only permissions, pinned Actions and one
Ubuntu 24.04 job with a ten-minute limit. It uses Python 3.11 and pinned dependencies;
no GPU, premium runner, self-hosted access or paid service is enabled.

Each run saves both 225-fit records, generated arrays, numerical comparison and
figures as a commit-labelled artifact retained for 14 days. The run's conclusion and
step logs establish what actually passed; this page does not substitute for them.
The saved Mac record and the new Linux record have distinct environmental metadata.
No cross-platform timing equality or performance ranking is claimed.

## Dependency review on 17 November 2026

The project pins Pillow 13.0.0, pytest 9.0.3 and Pygments 2.20.0 to incorporate
published security fixes. The numerical library pins remain those used for the
archived study. An OSV exact-version query of all 20 resolved runtime and test
packages in a fresh Python 3.11 environment returned zero matching advisories
on this date. Installer packages were outside this query.

The fresh environment passed all 60 tests and replayed all 225 archived fits.
Two new 225-fit studies also reproduced exactly, with all fits converged. Their
numerical digest matched the archived reproduction digest
`c0a3acf9d83fe5b223a4d99f192eccc1f1478283988b282de97b22095f0c3214`.
The archived record, arrays, and algorithm source remained byte-for-byte intact.
These checks ran locally on macOS with Python 3.11.

The dependency fixes are documented by the maintainers and advisory database.
[Pytest advisory](https://github.com/advisories/GHSA-6w46-j5rx-g56g),
[Pygments advisory](https://github.com/advisories/GHSA-5239-wwwm-4pmq) and
[Pillow security advisories](https://github.com/python-pillow/Pillow/security/advisories).
The workflow uses a read-only repository token and disables checkout credential
persistence.
