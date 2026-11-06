import numpy as np
import pytest
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from threadpoolctl import threadpool_limits
from clustering_study.core import initialize, kmeans, bisect


def test_hand_computed_means_and_sse():
    x = np.array([[0.], [2.], [8.], [10.]])
    r = kmeans(x, 2, initial=np.array([[0.], [10.]]))
    np.testing.assert_allclose(r.centers, [[1.], [9.]], atol=1e-14)
    assert r.labels.tolist() == [0, 0, 1, 1]
    assert r.inertia == 4.0 and r.converged


def test_one_cluster_and_all_distinct_clusters():
    x = np.array([[1.], [2.], [6.]])
    r = kmeans(x, 1)
    assert r.inertia == 14.0
    np.testing.assert_allclose(r.centers, [[3.]])
    assert kmeans(x, 3).inertia == 0.0


@pytest.mark.parametrize('method', ['random', 'plus'])
def test_initializer_distinct_reproducible_and_local_rng(method):
    x = np.array([[0., 1.], [0., 1.], [2., 3.], [4., 5.]])
    np.random.seed(78)
    state = np.random.get_state()
    a = initialize(x, 3, 91, method)
    np.testing.assert_array_equal(a, initialize(x, 3, 91, method))
    assert len(np.unique(a, axis=0)) == 3
    assert all(any(np.array_equal(row, obs) for obs in x) for row in a)
    after = np.random.get_state()
    assert state[0] == after[0] and state[2:] == after[2:]
    np.testing.assert_array_equal(state[1], after[1])


def test_empty_cluster_repair_duplicates_and_nonmutation():
    x = np.array([[0.], [0.], [10.], [10.]])
    original = x.copy()
    init = np.array([[0.], [0.]])
    r = kmeans(x, 2, initial=init)
    assert r.relocations > 0 and r.converged and r.inertia == 0
    assert len(np.unique(r.labels)) == 2
    np.testing.assert_array_equal(x, original)
    np.testing.assert_array_equal(init, [[0.], [0.]])


def test_exhausted_iteration_budget_is_not_convergence():
    x = np.array([[0.], [2.], [3.], [10.]])
    r = kmeans(x, 2, initial=np.array([[0.], [2.]]), max_iter=1)
    assert not r.converged and r.n_iter == 1
    expected = np.argmin(((x[:, None] - r.centers)**2).sum(axis=2), axis=1)
    np.testing.assert_array_equal(r.labels, expected)


@pytest.mark.parametrize('seed', [0, 3, 15])
def test_identical_start_matches_library_and_objective_descends(seed):
    x = np.random.default_rng(seed).normal(size=(90, 3))
    init = initialize(x, 4, seed, 'plus')
    r = kmeans(x, 4, initial=init)
    with threadpool_limits(limits=1):
        ref = KMeans(n_clusters=4, init=init, n_init=1, tol=0, max_iter=300, algorithm='lloyd').fit(x)
    assert r.converged
    assert np.all(np.diff(r.history) <= 1e-9)
    assert r.inertia == pytest.approx(ref.inertia_, rel=1e-10, abs=1e-10)
    assert adjusted_rand_score(r.labels, ref.labels_) == 1.0


@pytest.mark.parametrize('bad', [[], [[np.nan]], [[np.inf]], [1, 2], [[1+2j]], [[1e7]], [[True]], [['1']]])
def test_reject_invalid_arrays(bad):
    with pytest.raises(ValueError): kmeans(bad, 1)


@pytest.mark.parametrize('k', [0, -1, True, 1.5, 3])
def test_reject_infeasible_k(k):
    with pytest.raises(ValueError): kmeans([[0.], [1.], [1.]], k)


@pytest.mark.parametrize('value', [0, -1, True, 1.5])
def test_reject_invalid_iteration_budget(value):
    with pytest.raises(ValueError): kmeans([[0.], [1.]], 1, max_iter=value)


def test_reject_bad_seed_initializer_and_centers():
    for kwargs in [{'seed': -1}, {'seed': True}, {'init': 'unknown'}, {'initial': [[np.nan]]}, {'initial': [[0., 1.]]}]:
        with pytest.raises(ValueError): kmeans([[0.], [1.]], 1, **kwargs)


def test_bisect_preserves_duplicate_rows_and_means():
    x = np.array([[0.], [0.], [2.], [8.], [10.], [10.]])
    r = bisect(x, 3, seed=17)
    assert r.converged and len(r.labels) == len(x)
    assert set(r.labels) == {0, 1, 2}
    for j in range(3): np.testing.assert_allclose(r.centers[j], x[r.labels == j].mean(axis=0))
    assert r.inertia == pytest.approx(sum(float(np.dot(x[i]-r.centers[c], x[i]-r.centers[c])) for i,c in enumerate(r.labels)))
    np.testing.assert_array_equal(r.labels, bisect(x, 3, seed=17).labels)
    assert bisect(x, 1).inertia == pytest.approx(((x-x.mean(axis=0))**2).sum())
