# Clustering study design

Implement the owner's approved next portfolio stage in an independent repository.
Original coursework, PDFs, supplied datasets and existing repositories are read-only.
No paid services or GPU resources. Start locally; prepare a reviewable GitHub-ready
project without assuming authorization to create another remote repository.

## Approach
A new NumPy implementation from the mathematical description gives clear source
ownership. Adapting the old coursework would leave supplied-material rights unclear;
a notebook-only demo would not support repeatable contracts and evidence checks.
Scikit-learn provides evaluation metrics and a reference, not the custom algorithms.

## Scientific question and methods
How do initialization and cluster geometry affect squared-distance clustering?
Compare Lloyd k-means with random distinct-observation initialization, vanilla
single-draw D-squared k-means++ initialization, and a bisecting method which splits
the splittable leaf with largest within-leaf SSE using one k-means++ two-way run.
Bisecting membership stays hierarchical; its iteration count sums the split runs,
and its labels need not be globally nearest to the final leaf centroids.

Use float64, finite real 2D arrays, 1 <= k <= number of distinct observations.
Bound n to 10,000, d to 64 and k to 64, zero or 1e-100 <= |coordinate| <= 1e6 to avoid overflow and
unbounded memory. Reject booleans as integer parameters. Use local NumPy Generator
instances, never reset global random state. Lloyd stops at stable assignments;
max_iter=300 limits updates. On exhaustion return nearest labels and mark not
converged; do not claim centroid-mean consistency for unfinished fits. Empty-cluster
repair moves the farthest point from a donor with >1 member; ties use row order.

## Fixed experiment
Three generated 2D cases: separated isotropic, overlapping isotropic, anisotropic.
600 observations, 3 equal components; fixed k=3 is supplied, not estimated.
Dataset seeds 11,22,33,44,55; initialization seeds 101,202,303,404,505.
3 methods x 3 cases x 5 datasets x 5 initializations = 225 custom fits.
For each flat fit, run scikit-learn Lloyd from the exact same initial centers,
n_init=1, tol=0, max_iter=300. Record reference inertia/ARI; divergence is evidence,
not silently discarded. Reference timing is not a speed comparison.

Generated component labels are used only for ARI evaluation and an explanatory
figure. No supervised training/test split or generalization claim applies.
Record inertia, silhouette (null outside its defined domain), ARI, effective k,
iterations, convergence, elapsed fit time, centers/labels, init centers, input hash.
Limit BLAS/OpenMP threads to one and save library, OS, hardware and thread metadata.
Randomize method order with a separate fixed RNG; timings include initialization
and fitting, exclude data generation, metrics, reference and disk writes.
One untimed warm-up per method. No peak-performance claim.

## Evidence and presentation
Exclusive new output directory, initial status incomplete, incremental records,
final complete only after expected fit count and validation pass. Save generated
arrays and configuration, source fingerprints and Git revision/clean state scoped
to this repo. Reject an enclosing Git repo. Preserve diagnostics on failure.
Verify saved inputs, configurations, numerical outputs and metric summaries before
plotting. Figures: all-seed metric distributions; fixed first-seed geometry gallery
(no best-run selection). Teal/gold/graphite palette, clear axes, captions, legends,
SVG and PNG. Metrics describe synthetic cases only, not real-world accuracy.

## Delivery gates
Independent numerical/edge tests; identical-start library checks; complete actual
local study; repeat reproduction comparison excluding time/platform metadata;
source/secret/privacy scan; fresh review; docs, license, pinned bounded CPU workflow.
GitHub Linux execution and public release are later explicit steps if not authorized.
