__author__ = 'brianoneill'

def test():
    """
    Code from "Demonstration of k-means assumptions",
    http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_assumptions.html#example-cluster-plot-kmeans-assumptions-py

    >>> from log_calls import log_calls
    >>> from sklearn.cluster import KMeans
    >>> from sklearn.datasets import make_blobs
    >>> n_samples = 1500
    >>> random_state = 170
    >>> X, y = make_blobs(n_samples=n_samples, random_state=random_state)

# First, let's see the call hierarchy:
#     >>> log_calls.decorate_class(KMeans, log_args=False)
#     >>> y_pred = KMeans(n_clusters=2, random_state=random_state).fit_predict(X)     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
#     KMeans.__init__ <== called by <module>
#     KMeans.__init__ ==> returning to <module>
#     KMeans.fit_predict <== called by <module>
#         KMeans.fit <== called by KMeans.fit_predict
#             KMeans._check_fit_data <== called by KMeans.fit
#             KMeans._check_fit_data ==> returning to KMeans.fit
#         KMeans.fit ==> returning to KMeans.fit_predict
#     KMeans.fit_predict ==> returning to <module>

Now let's view arguments too:
    >>> log_calls.decorate_class(KMeans, log_args=True, args_sep='\\n')
    >>> # Incorrect number of clusters
    >>> y_pred = KMeans(n_clusters=2, random_state=random_state).fit_predict(X)     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    KMeans.__init__ <== called by <module>
        arguments:
            self=<sklearn.cluster.k_means_.KMeans object at ...>
            n_clusters=2
            random_state=170
        defaults:
            init='k-means++'
            n_init=10
            max_iter=300
            tol=0.0001
            precompute_distances='auto'
            verbose=0
            copy_x=True
            n_jobs=1
    KMeans.__init__ ==> returning to <module>
    KMeans.fit_predict <== called by <module>
        arguments:
            self=KMeans(copy_x=True, init='k-means++', max_iter=300, n_clusters=2, n_init=10,
        n_jobs=1, precompute_distances='auto', random_state=170, tol=0.0001,
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
        KMeans.fit <== called by KMeans.fit_predict
            arguments:
                self=KMeans(copy_x=True, init='k-means++', max_iter=300, n_clusters=2, n_init=10,
            n_jobs=1, precompute_distances='auto', random_state=170, tol=0.0001,
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
            KMeans._check_fit_data <== called by KMeans.fit
                arguments:
                    self=KMeans(copy_x=True, init='k-means++', max_iter=300, n_clusters=2, n_init=10,
                n_jobs=1, precompute_distances='auto', random_state=170, tol=0.0001,
                verbose=0)
                    X=array([[ -5.19811282e+00,   6.41869316e-01],
                   [ -5.75229538e+00,   4.18627111e-01],
                   [ -1.08448984e+01,  -7.55352273e+00],
                   ...,
                   [  1.36105255e+00,  -9.07491863e-01],
                   [ -3.54141108e-01,   7.12241630e-01],
                   [  1.88577252e+00,   1.41185693e-03]])
            KMeans._check_fit_data ==> returning to KMeans.fit
        KMeans.fit ==> returning to KMeans.fit_predict
    KMeans.fit_predict ==> returning to <module>

    Note: the ellipses in the values of array `X` are produced by `sklearn`.

    """

if __name__ == '__main__':
    # import doctest
    # doctest.testmod()

    ##########################
    from log_calls import log_calls

    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs
    n_samples = 1500
    random_state = 170
    X, y = make_blobs(n_samples=n_samples, random_state=random_state)

    # First, let's see the call hierarchy:
    log_calls.decorate_class(KMeans, log_args=False)
    y_pred = KMeans(n_clusters=2, random_state=random_state).fit_predict(X)     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    '''
    KMeans.__init__ <== called by <module>
    KMeans.__init__ ==> returning to <module>
    KMeans.fit_predict <== called by <module>
        KMeans.fit <== called by KMeans.fit_predict
            KMeans._check_fit_data <== called by KMeans.fit
            KMeans._check_fit_data ==> returning to KMeans.fit
        KMeans.fit ==> returning to KMeans.fit_predict
    KMeans.fit_predict ==> returning to <module>
    '''

    print("########################################################")

    # Now let's view arguments too:
    log_calls.decorate_class(KMeans, log_args=True, args_sep='\\n')
    # Incorrect number of clusters
    y_pred = KMeans(n_clusters=2, random_state=random_state).fit_predict(X)     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
