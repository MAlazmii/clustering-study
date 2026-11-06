# Clustering Study Implementation Plan

> Execute with superpowers:executing-plans, then one fresh final code review.

**Goal:** A locally verified, GitHub-ready clustering study with actual experiments and figures.
**Architecture:** Independent NumPy algorithms, generated inputs, recorded experiment, evidence-driven plots.
**Tech Stack:** Python 3.11, NumPy, scikit-learn, Matplotlib, pytest, threadpoolctl.
**Spec:** ../specs/2026-11-06-clustering-design.md

## Global constraints
Original coursework stays untouched. No paid services. Bounds and seeds from the
spec are mandatory. No real-world or universal speed claims. New results never overwrite.

## Review focus
Duplicate points/empty clusters; max-iteration exhaustion; mutated input/result
records; global RNG contamination; interrupted runs mislabelled complete.

## Task 1 — Numerical algorithms
Files: clustering_study/core.py, tests/test_core.py.
Interfaces: initialize(X,k,seed,method); kmeans(X,k,seed=0,init='plus',initial=None,max_iter=300);
bisect(X,k,seed=0,max_iter=300). Result holds centers, labels, inertia, n_iter,
converged, history, initial_centers, relocations.
- [ ] Write failing tests: hand-computed 1D means/SSE, same-init sklearn, duplicates/repair,
invalid data/counts, non-convergence, no input/global-RNG mutation, bisect partition/inertia.
- [ ] Implement and run full suite; commit independent algorithms.

## Task 2 — Experiment and evidence
Files: clustering_study/experiment.py, tests/test_experiment.py, configs/study.json.
Interfaces: generate(case,seed,n); run_study(config,output); verify_run(output).
- [ ] Failing tests for deterministic generation, exclusive output, malformed config,
complete small run, tampered array/metrics, incomplete record, ancestor Git rejection.
- [ ] Implement input/output hashes and raw evidence; run all tests; commit.
- [ ] Run full predeclared225-fit experiment and a second repeat; compare all numerical fields.

## Task 3 — Figures, documentation, release preparation
Files: scripts/plot_results.py, README.md, docs/methods.md, docs/validation.md,
docs/provenance.md, CONTRIBUTING.md, LICENSE, requirements.txt, .github/workflows/checks.yml.
- [ ] Generate PNG/SVG from verified records, inspect both figures.
- [ ] Explain real measured findings and limitations, reproduce commands in clean checkout.
- [ ] Fresh whole-project review, fix blocking issues with regression tests, final full-suite run.
- [ ] Save a local checkpoint with exact commit, evidence and remaining Linux/GitHub status.
