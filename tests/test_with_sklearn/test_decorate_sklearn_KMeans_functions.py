__author__ = 'brianoneill'


###############################################################################

def test_deco_sklearn_cluster_kmeans_function():
    """
    Dunno how to decorate `sklearn.cluster.kmeans` so that the decorated funciton
    is called via `sklearn.cluster.kmeans(...)`. What gets decorated is the function
    qualified by the *module* name,
        `sklearn.cluster.kmeans_.kmeans`
    because sklearn.cluster.kmeans_ is the module of the function `sklearn.cluster.kmeans`
    as per inspect.getmodule

    >>> from sklearn.datasets import make_blobs
    >>> n_samples = 1500
    >>> random_state = 170
    >>> X, y = make_blobs(n_samples=n_samples, random_state=random_state)

    >>> from log_calls import log_calls

THIS Doesn't work:
    # import sklearn
    # import sklearn.cluster
    # log_calls.decorate_module_function(sklearn.cluster.k_means)
    # ret = sklearn.cluster.k_means(X, n_clusters=45)

### THIS WORKS (import module and call it through module name :| ):
    >>> ## TODO Can this be improved?? It's clunky to require that the module name be known.
    >>> import sklearn.cluster.k_means_
    >>> log_calls.decorate_module_function(sklearn.cluster.k_means_.k_means,
    ...                                    args_sep='\\n',
    ...                                    override=True)
    >>> ret = sklearn.cluster.k_means_.k_means(X, n_clusters=3, random_state=2)     # doctest: +NORMALIZE_WHITESPACE
    k_means <== called by <module>
        arguments:
            X=array([[ -5.19811282e+00,   6.41869316e-01],
           [ -5.75229538e+00,   4.18627111e-01],
           [ -1.08448984e+01,  -7.55352273e+00],
           ...,
           [  1.36105255e+00,  -9.07491863e-01],
           [ -3.54141108e-01,   7.12241630e-01],
           [  1.88577252e+00,   1.41185693e-03]])
            n_clusters=3
            random_state=2
        defaults:
            init='k-means++'
            precompute_distances='auto'
            n_init=10
            max_iter=300
            verbose=False
            tol=0.0001
            copy_x=True
            n_jobs=1
            return_n_iter=False
    k_means ==> returning to <module>

    >>> ret
    (array([[ 1.91176144,  0.40634045],
           [-8.94137566, -5.48137132],
           [-4.55490993,  0.02920864]]), array([2, 2, 1, ..., 0, 0, 0], dtype=int32), 2862.7319140789582)
    """
    pass

def test__decorate_functions():
    """
    >>> from sklearn.datasets import make_blobs
    >>> n_samples = 1500
    >>> random_state = 170
    >>> X, y = make_blobs(n_samples=n_samples, random_state=random_state)
    >>> from log_calls import log_calls

(B)
import the module, deco the fn as a module function, and call the fn via the module
==> OUTPUT:

    >>> import sklearn.cluster.k_means_
    >>> log_calls.decorate_module_function(sklearn.cluster.k_means_.k_means,
    ...                                    override=True)

    >>> ret_B = sklearn.cluster.k_means_.k_means(X, n_clusters=3, random_state=2)     # doctest: +NORMALIZE_WHITESPACE
    k_means <== called by <module>
        arguments: X=array([[ -5.19811282e+00,   6.41869316e-01],
           [ -5.75229538e+00,   4.18627111e-01],
           [ -1.08448984e+01,  -7.55352273e+00],
           ...,
           [  1.36105255e+00,  -9.07491863e-01],
           [ -3.54141108e-01,   7.12241630e-01],
           [  1.88577252e+00,   1.41185693e-03]]), n_clusters=3, random_state=2
        defaults:  init='k-means++', precompute_distances='auto', n_init=10, max_iter=300, verbose=False, tol=0.0001, copy_x=True, n_jobs=1, return_n_iter=False
    k_means ==> returning to <module>
    >>> ret_B
    (array([[ 1.91176144,  0.40634045],
           [-8.94137566, -5.48137132],
           [-4.55490993,  0.02920864]]), array([2, 2, 1, ..., 0, 0, 0], dtype=int32), 2862.7319140789582)

(A)
import the package, deco the fn as a package function;
    >>> import sklearn.cluster
    >>> log_calls.decorate_package_function(sklearn.cluster.k_means,
    ...                                     override=True)

Call the fn via the package ==> OUTPUT, and
Call the fn via the module ==> OUTPUT.

Call via package -- OUTPUT:
    >>> ret = sklearn.cluster.k_means(X, n_clusters=3, random_state=2)     # doctest: +NORMALIZE_WHITESPACE
    k_means <== called by <module>
        arguments: X=array([[ -5.19811282e+00,   6.41869316e-01],
           [ -5.75229538e+00,   4.18627111e-01],
           [ -1.08448984e+01,  -7.55352273e+00],
           ...,
           [  1.36105255e+00,  -9.07491863e-01],
           [ -3.54141108e-01,   7.12241630e-01],
           [  1.88577252e+00,   1.41185693e-03]]), n_clusters=3, random_state=2
        defaults:  init='k-means++', precompute_distances='auto', n_init=10, max_iter=300, verbose=False, tol=0.0001, copy_x=True, n_jobs=1, return_n_iter=False
    k_means ==> returning to <module>
    >>> ret
    (array([[ 1.91176144,  0.40634045],
           [-8.94137566, -5.48137132],
           [-4.55490993,  0.02920864]]), array([2, 2, 1, ..., 0, 0, 0], dtype=int32), 2862.7319140789582)

Call via module -- OUTPUT TOO now :D:D:D :
    >>> ret = sklearn.cluster.k_means_.k_means(X, n_clusters=3, random_state=2)     # doctest: +NORMALIZE_WHITESPACE
    k_means <== called by <module>
        arguments: X=array([[ -5.19811282e+00,   6.41869316e-01],
           [ -5.75229538e+00,   4.18627111e-01],
           [ -1.08448984e+01,  -7.55352273e+00],
           ...,
           [  1.36105255e+00,  -9.07491863e-01],
           [ -3.54141108e-01,   7.12241630e-01],
           [  1.88577252e+00,   1.41185693e-03]]), n_clusters=3, random_state=2
        defaults:  init='k-means++', precompute_distances='auto', n_init=10, max_iter=300, verbose=False, tol=0.0001, copy_x=True, n_jobs=1, return_n_iter=False
    k_means ==> returning to <module>
    >>> ret
    (array([[ 1.91176144,  0.40634045],
           [-8.94137566, -5.48137132],
           [-4.55490993,  0.02920864]]), array([2, 2, 1, ..., 0, 0, 0], dtype=int32), 2862.7319140789582)

    """
    pass


##############################################################################
# end of tests.
##############################################################################
import doctest

# For unittest integration
def load_tests(loader, tests, ignore):
    try:
        import sklearn
    except ImportError:
        pass
    else:
        tests.addTests(doctest.DocTestSuite())
    return tests

if __name__ == '__main__':
    doctest.testmod()

