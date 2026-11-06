# Mathematical and experimental specification

## Objective and updates
For X in R^(n×d), minimize sum_i ||x_i − c_(label_i)||². Arithmetic uses float64.
Lloyd assigns points to their nearest centroid (lowest index on exact ties), then
replaces each centroid by the arithmetic mean of its members. Each empty cluster
receives the currently farthest assigned observation from a donor with >1 members;
row order breaks distance ties. Convergence requires stable assignments and exact
agreement with a fresh nearest-centroid assignment. No small-objective-change
shortcut is used. On iteration exhaustion, convergence is false and returned
labels are nearest to the returned centres; those centres may not be means of
the final labels. Such outcomes remain in the evidence.

Random initialization samples distinct coordinate values uniformly without
replacement. With duplicate observations this differs from row-weighted sampling.
Vanilla k-means++ picks the first observation uniformly among rows, then draws
one new observation with probability proportional to squared distance from its
nearest chosen centre. It does not use scikit-learn's greedy multi-trial seeding.
The experiment compares Lloyd implementations using exactly the same initial
centres, n_init=1, algorithm='lloyd', tol=0 and max_iter=300. Identical seeds alone
would not ensure identical initialization across libraries.

Bisecting chooses the splittable leaf with largest within-leaf SSE, breaking ties
by leaf order. A two-way k-means++ fit partitions its row indices; one child
replaces the leaf and the other is appended. Child seeds come from the fit's
local generator. There is one start per split and no global refinement. Final
centres are leaf means, even when a child split exhausted its budget; convergence
is true only if all child fits converged. Its iteration count sums child updates,
so it is not directly comparable to flat Lloyd iteration counts. Its objective
is evaluated on hierarchical memberships, not global nearest-centroid labels.

## Generated cases
For each dataset seed, generate 200 observations from each centre (-4,-1), (0,4),
(4,-1), using independent standard normal noise. Multiply noise by 0.65 for
separated data, 2.1 for overlapping data, and 1.15 for the stretched case. For
stretched data multiply the whole row-vector array by [[1,0.8],[0,0.13]]. Then
shuffle rows with the same local generator. All array values and group labels
are stored, along with byte hashes. No feature standardization is applied: the
geometry transformation is the object of study.

The fixed design is `configs/study.json`: dataset seeds 11,22,33,44,55;
initialization seeds 101,202,303,404,505; three methods; k=3; n=600; max_iter=300.
No outcomes are used to alter k, seeds, case parameters or stopping criteria.
Generating group labels are evaluation-only. This is not supervised learning,
and there is no claim of held-out generalization or real-world dataset performance.

## Evaluation and measurement
- Inertia: within-assigned-cluster squared distance; lower is the fitted objective.
- Adjusted Rand index (ARI): agreement with generating component labels, adjusted
  for chance and invariant to cluster ID permutation. It is not classification accuracy.
- Silhouette: cohesion versus nearest alternative-cluster separation; undefined
  outside 2…n−1 occupied clusters, represented as null rather than a fake score.
- Effective cluster count, iterations, convergence, empty-cluster relocations and
  objective history are retained for every fit.

Fit time uses perf_counter around input validation, initialization and fitting;
it excludes generation, metric computation, reference runs and disk writes.
One untimed 60-point warm-up per method precedes a fixed, shuffled schedule
(order seed90210). BLAS/OpenMP pools are limited to one thread and recorded.
CPU models/clocks/thermal state are not controlled; times are diagnostic observations,
not a speed leaderboard. No library speed comparison is reported.

The five initializations within each generated dataset are dependent observations.
The plots show all 25 values per method/case, median, IQR and min–max; these are
not confidence intervals. No statistical significance or universal ranking is claimed.
The geometry gallery uses seeds11/101 as declared before measurements.

## Sources
Algorithm implementation is independent; these primary references document the
comparison tool and metric definitions:
- [scikit-learn KMeans](https://scikit-learn.org/1.8/modules/generated/sklearn.cluster.KMeans.html)
- [scikit-learn clustering evaluation](https://scikit-learn.org/1.8/modules/clustering.html#clustering-performance-evaluation)
- [k-means++ original paper](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf)

The code does not claim scikit-learn source ownership or implement its greedy
initialization variant. NumPy/scikit-learn/Matplotlib and their dependencies retain
independent licenses.
