__author__ = 'brianoneill'

def test_deco_sklearn_cluster_KMeans_class():
    """
    Code from "Demonstration of k-means assumptions",
    http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_assumptions.html#example-cluster-plot-kmeans-assumptions-py

    This test demonstrates
        * decorating an "external" class and its subclasses --
          KMeans from sklearn.cluster and its subclasses,
          amongst which is MiniBatchKMeans
        * using the `override` keyword with one of the `log_calls.decorate_*`
          functions to make a change to the settings of (all the methods of)
          an already-decorated class

    >>> from log_calls import log_calls
    >>> from sklearn.cluster import KMeans, MiniBatchKMeans
    >>> from sklearn.datasets import make_blobs
    >>> n_samples = 1500
    >>> random_state = 170
    >>> X, y = make_blobs(n_samples=n_samples, random_state=random_state)

First, let's see the call hierarchy:

    >>> log_calls.decorate_hierarchy(KMeans, log_args=False, override=True)

    >>> kmo = KMeans(n_clusters=2, random_state=random_state,
    ...              n_init=10)
    KMeans.__init__ <== called by <module>
    KMeans.__init__ ==> returning to <module>
    >>> y_pred = kmo.fit_predict(X)
    KMeans.fit_predict <== called by <module>
        KMeans.fit <== called by KMeans.fit_predict
            KMeans._check_fit_data <== called by KMeans.fit
            KMeans._check_fit_data ==> returning to KMeans.fit
        KMeans.fit ==> returning to KMeans.fit_predict
    KMeans.fit_predict ==> returning to <module>

`MiniBatchKMeans` is a subclass of `KMeans`, so that class is decorated too.

    >>> mbk = MiniBatchKMeans(init='k-means++', n_clusters=2, batch_size=45,
    ...                       n_init=10, max_no_improvement=10)
    MiniBatchKMeans.__init__ <== called by <module>
        KMeans.__init__ <== called by MiniBatchKMeans.__init__
        KMeans.__init__ ==> returning to MiniBatchKMeans.__init__
    MiniBatchKMeans.__init__ ==> returning to <module>

    >>> mbk.fit(X)           # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    MiniBatchKMeans.fit <== called by <module>
        MiniBatchKMeans._labels_inertia_minibatch <== called by MiniBatchKMeans.fit
        MiniBatchKMeans._labels_inertia_minibatch ==> returning to MiniBatchKMeans.fit
    MiniBatchKMeans.fit ==> returning to <module>
    MiniBatchKMeans(batch_size=45, compute_labels=True, init='k-means++',
            init_size=None, max_iter=100, max_no_improvement=10, n_clusters=2,
            n_init=10, random_state=None, reassignment_ratio=0.01, tol=0.0,
            verbose=0)

Now let's view arguments too:
    >>> log_calls.decorate_class(KMeans, decorate_subclasses=True,
    ...                          log_args=True, args_sep='\\n',
    ...                          override=True)
    >>> # Incorrect number of clusters
    >>> mbk.fit(X)           # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    MiniBatchKMeans.fit <== called by <module>
        arguments:
            self=MiniBatchKMeans(batch_size=45, compute_labels=True, init='k-means++',
            init_size=None, max_iter=100, max_no_improvement=10, n_clusters=2,
            n_init=10, random_state=None, reassignment_ratio=0.01, tol=0.0,
            verbose=0)
            X=array([[ -5.19811282e+00,   6.41869316e-01],
           [ -5.75229538e+00,   4.18627111e-01],
           [ -1.08448984e+01,  -7.55352273e+00],
           ...,
           [  1.36105255e+00,  -9.07491863e-01],
           [ -3.54141108e-01,   7.12241630e-01],
           [  1.88577252e+00,   1.41185693e-03]])
        defaults:
            y=None
        MiniBatchKMeans._labels_inertia_minibatch <== called by MiniBatchKMeans.fit
            arguments:
                self=MiniBatchKMeans(batch_size=45, compute_labels=True, init='k-means++',
                init_size=None, max_iter=100, max_no_improvement=10, n_clusters=2,
                n_init=10, random_state=None, reassignment_ratio=0.01, tol=0.0,
                verbose=0)
                X=array([[ -5.19811282e+00,   6.41869316e-01],
               [ -5.75229538e+00,   4.18627111e-01],
               [ -1.08448984e+01,  -7.55352273e+00],
               ...,
               [  1.36105255e+00,  -9.07491863e-01],
               [ -3.54141108e-01,   7.12241630e-01],
               [  1.88577252e+00,   1.41185693e-03]])
        MiniBatchKMeans._labels_inertia_minibatch ==> returning to MiniBatchKMeans.fit
    MiniBatchKMeans.fit ==> returning to <module>
    MiniBatchKMeans(batch_size=45, compute_labels=True, init='k-means++',
            init_size=None, max_iter=100, max_no_improvement=10, n_clusters=2,
            n_init=10, random_state=None, reassignment_ratio=0.01, tol=0.0,
            verbose=0)

    Note: the ellipses in the values of array `X` are produced by the `repr` of `numpy`.
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

