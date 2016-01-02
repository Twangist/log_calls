__author__ = 'brianoneill'


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
    # log_calls.decorate_external_function(sklearn.cluster.k_means)
    # ret = sklearn.cluster.k_means(X, n_clusters=45)

### THIS WORKS (import module and call it through module name :| ):
    >>> ## TODO Can this be improved?? It's clunky to require that the module name be known.
    >>> import sklearn.cluster.k_means_
    >>> log_calls.decorate_external_function(sklearn.cluster.k_means_.k_means,
    ...                                      args_sep='\\n',
    ...                                      override=True)
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
    tests.addTests(doctest.DocTestSuite())
    return tests

if __name__ == '__main__':
    doctest.testmod()

    # from sklearn.datasets import make_blobs
    # n_samples = 1500
    # random_state = 170
    # X, y = make_blobs(n_samples=n_samples, random_state=random_state)
    #
    # # import log_calls as log_calls_mod
    # from log_calls import log_calls
    # # print(type(log_calls))  # <class 'type'>

    ## (C)
    ## Now try `_decorate_module`
    ## *  create a `KMeans` obj
    ## *  call `fit_predict` on it
    #### THIS DOESN'T WORK --- blows up one way or the other,
    ####                   --- without 'omit=', and with 'omit='
    #### import sklearn.cluster
    #### # log_calls._decorate_module(sklearn.cluster)
    #### log_calls._decorate_module(sklearn.cluster.k_means_,
    ####                           omit=['get_params']
    ####                          )
    ####
    #### kmeans_obj = sklearn.cluster.k_means_.KMeans(
    ####                         n_clusters=2, random_state=random_state, n_init=10)
    #### y_pred = kmeans_obj.fit_predict(X)

    # ## (-1)
    # import log_calls.tests as pkg
    # log_calls.decorate_package_function(pkg.f, log_retval=True)
    # log_calls.decorate_package_function(pkg.g, log_retval=True)
    # pkg.f(2,3)
    # # Works for (both f and g) now that we replace the fn with its deco'd wrapper
    # # in the dicts of **both** the module and the package.
    # '''
    # f <== called by <module>
    #     arguments: a=2, b=3
    #     g <== called by f
    #         arguments: a=2, b=3
    #         g return value: 6
    #     g ==> returning to f
    #     f return value: 16
    # f ==> returning to <module>
    # '''
    # ## (0)
    # ## Try using log_calls.decorate_package_function with a function specified by module
    # ## TODO  Doesn't work (correctly) -- no output:
    # import log_calls.tests.some_module as mod
    # log_calls.decorate_module_function(mod.f, log_retval=True)
    # log_calls.decorate_module_function(mod.g, log_retval=True)
    # mod.f(2,3)
    # '''
    # f <== called by <module>
    #     arguments: a=2, b=3
    #     g <== called by f
    #         arguments: a=2, b=3
    #         g return value: 6
    #     g ==> returning to f
    #     f return value: 16
    # f ==> returning to <module>
    # '''
