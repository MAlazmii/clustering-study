"""Independent float64 Lloyd and bisecting algorithms; no global RNG mutation."""
from dataclasses import dataclass
import numpy as np


@dataclass
class Result:
    centers: np.ndarray
    labels: np.ndarray
    inertia: float
    n_iter: int
    converged: bool
    history: list
    initial_centers: np.ndarray | None
    relocations: int = 0


def _integer(value, name, low, high):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in [{low}, {high}]')
    return int(value)


def _data(x):
    a = np.asarray(x)
    if a.dtype.kind not in 'fiu' or a.ndim != 2 or not 1 <= a.shape[0] <= 10000 or not 1 <= a.shape[1] <= 64:
        raise ValueError('X must be a real numeric matrix: 1..10000 rows, 1..64 columns')
    a = np.array(a, dtype=np.float64, copy=True)
    if not np.isfinite(a).all() or np.abs(a).max() > 1e6:
        raise ValueError('X must be finite with absolute coordinates <= 1e6')
    return a


def _check(x, k, seed):
    a = _data(x)
    k = _integer(k, 'k', 1, min(64, len(np.unique(a, axis=0))))
    seed = _integer(seed, 'seed', 0, 2**32-1)
    return a, k, np.random.default_rng(seed)


def _distances(x, centers):
    # One n*d temporary per centroid, rather than an n*k*d tensor.
    return np.column_stack([np.einsum('ij,ij->i', x-c, x-c) for c in centers])


def _initialize(x, k, rng, method):
    if method == 'random':
        unique = np.unique(x, axis=0)
        return unique[rng.choice(len(unique), k, replace=False)].copy()
    if method != 'plus':
        raise ValueError("init must be 'random' or 'plus'")
    centers = [x[rng.integers(len(x))].copy()]
    closest = _distances(x, centers)[:, 0]
    for _ in range(1, k):
        total = closest.sum()
        if total <= 0:
            raise ValueError('No positive-distance candidate for initialization')
        index = rng.choice(len(x), p=closest / total)
        centers.append(x[index].copy())
        closest = np.minimum(closest, _distances(x, [x[index]])[:, 0])
    return np.asarray(centers)


def initialize(x, k, seed=0, method='plus'):
    """Random unique-value sampling or vanilla single-draw D-squared seeding."""
    x, k, rng = _check(x, k, seed)
    return _initialize(x, k, rng, method)


def kmeans(x, k, seed=0, init='plus', initial=None, max_iter=300):
    """Lloyd updates; fixed assignments establish convergence, never a small delta."""
    x, k, rng = _check(x, k, seed)
    max_iter = _integer(max_iter, 'max_iter', 1, 10000)
    if init not in ('random', 'plus'):
        raise ValueError("init must be 'random' or 'plus'")
    centers = _initialize(x, k, rng, init) if initial is None else _data(initial)
    if centers.shape != (k, x.shape[1]):
        raise ValueError('initial centers must have shape (k, n_features)')
    initial_centers = centers.copy()
    previous = None
    history = []
    relocations = 0
    converged = False
    for iteration in range(1, max_iter + 1):
        distances = _distances(x, centers)
        labels = distances.argmin(axis=1)
        counts = np.bincount(labels, minlength=k)
        for empty in np.flatnonzero(counts == 0):
            eligible = counts[labels] > 1
            scores = np.where(eligible, distances[np.arange(len(x)), labels], -np.inf)
            moved = int(scores.argmax())
            counts[labels[moved]] -= 1
            labels[moved] = empty
            counts[empty] += 1
            relocations += 1
        centers = np.array([x[labels == j].mean(axis=0) for j in range(k)])
        residual = x - centers[labels]
        history.append(float(np.einsum('ij,ij->', residual, residual)))
        nearest = _distances(x, centers).argmin(axis=1)
        if previous is not None and np.array_equal(previous, labels) and np.array_equal(nearest, labels):
            converged = True
            break
        previous = labels.copy()
    # Even on exhaustion, labels describe the returned centers' Voronoi assignment.
    labels = _distances(x, centers).argmin(axis=1)
    residual = x - centers[labels]
    return Result(centers, labels, float(np.einsum('ij,ij->', residual, residual)),
                  iteration, converged, history, initial_centers, relocations)


def bisect(x, k, seed=0, max_iter=300):
    """Split the highest-SSE splittable leaf. No final global Lloyd refinement."""
    x, k, rng = _check(x, k, seed)
    max_iter = _integer(max_iter, 'max_iter', 1, 10000)
    leaves = [np.arange(len(x))]
    history = []
    iterations = relocations = 0
    converged = True
    def sse(indices):
        residual = x[indices] - x[indices].mean(axis=0)
        return float(np.einsum('ij,ij->', residual, residual))
    while len(leaves) < k:
        candidates = [(sse(idx), j) for j, idx in enumerate(leaves) if len(np.unique(x[idx], axis=0)) >= 2]
        # Stable leaf order resolves equal SSE.
        chosen = max(candidates, key=lambda item: (item[0], -item[1]))[1]
        indices = leaves[chosen]
        split = kmeans(x[indices], 2, seed=int(rng.integers(2**32)), max_iter=max_iter)
        if len(np.unique(split.labels)) != 2:
            raise RuntimeError('Two-way split did not produce two occupied leaves')
        leaves[chosen] = indices[split.labels == 0]
        leaves.append(indices[split.labels == 1])
        iterations += split.n_iter
        relocations += split.relocations
        converged &= split.converged
        history.append(sum(sse(idx) for idx in leaves))
    labels = np.empty(len(x), dtype=int)
    centers = []
    for j, idx in enumerate(leaves):
        labels[idx] = j
        centers.append(x[idx].mean(axis=0))
    return Result(np.asarray(centers), labels, sum(sse(idx) for idx in leaves),
                  iterations, bool(converged), history, None, relocations)
