.. _decorating_functions_class_hierarchies_modules:

Bulk (Re)Decoration, (Re)Decorating Imports
#########################################################################

This chapter discusses the ``log_calls.decorate_*`` classmethods. These methods allow you to:

* decorate or redecorate functions and classes,
* decorate an entire class hierarchy (a class and all its subclasses), and even
* decorate all classes and/or functions in a module.

These methods are handy in situations where altering source code is impractical (too many things
to decorate) or questionable practice (third-party modules and packages).
They can also help you learn a new codebase, by shedding light on its internal operations.

The ``decorate_*`` methods provide another way to dynamically change the settings
of already-decorated functions and classes.

Like any decorator, `log_calls` is a :ref:`functional <functional-def>` —
a function that takes a function argument and returns a function. The
following typical use::

    @log_calls()
    def f(): pass

is equivalent to::

    f = log_calls()(f)

If ``f`` occurs in your own code, then no doubt you'll prefer the former. The ``log_calls.decorate_*``
methods let you decorate ``f`` when its definition does *not* necessarily appear in your code.

.. note::
   You can't decorate Python builtins. Attempting to do is harmless (anyway, it's supposed to be!),
   and `log_calls` will return the builtin class or callable unchanged. For example,
   the following have no effect::

    log_calls.decorate_class(dict)
    log_calls.decorate_class(dict, only='update')
    log_calls.decorate_function(dict.update)


.. _decorating_classes_programmatically:

Decorating classes programmatically
============================================================


.. _decorate_class-method:

Decorating a class and optionally, all of its subclasses
----------------------------------------------------------

.. py:classmethod:: log_calls.decorate_class(klass: type, decorate_subclasses=False, **setting_kwargs) -> None

   Decorate class ``klass`` and, optionally, all of its descendants recursively.
   If ``decorate_subclasses == True``, and if any subclasses are decorated,
   their explicitly given :ref:`settings <what-is-a-setting>` remain unchanged by those in
   ``setting_kwargs`` *unless* ``override=True`` is in ``setting_kwargs``.

   ``log_calls.decorate_class(C, **kwds)`` is basically a syntactically sweetened version of
   ``log_calls(**kwds)(C)``, with the addition of the flag parameter ``decorate_subclasses``.
   There's another difference, however: ``log_calls.decorate_class(...)`` returns ``None``,
   whereas ``log_calls(**kwds)(C)`` returns ``C``.


.. _decorate_class_hierarchy:

Decorating a class and all of its subclasses
----------------------------------------------------------

.. py:classmethod:: log_calls.decorate_hierarchy(baseclass: type, **setting_kwargs) -> None

   Decorate ``baseclass`` and, recursively, all of its descendants.
   If any subclasses are directly decorated, their explicitly given :ref:`settings <what-is-a-setting>`
   remain unchanged by those in ``setting_kwargs`` *unless* ``override=True`` is in ``setting_kwargs``.

   This is just a shorthand for ``log_calls.decorate_class(baseclass, decorate_subclasses=True, **setting_kwargs)``.


.. _decorating_functions:

Decorating functions programmatically
===========================================

.. --comment--  Some generalization about these three classmethods?

.. _decorate_function-method:

Decorating a function in your namespace
---------------------------------------------------------------------------------

.. py:classmethod:: log_calls.decorate_function(f: 'Callable', **setting_kwargs) -> None

   Decorate ``f`` using ``settings_kwds``, and replace the definition of ``f.__name__``
   with the decorated function (i.e. the wrapper) in the global namespace *of the caller*.

   :param f: a function object, with no package/module qualifier:
    however it would be referred to in code at the point of the call
    to ``decorate_function``. ``f`` itself refers to a function which is
    either defined in or imported into the module of the caller.
   :param setting_kwargs: settings for decorator

   ``log_calls.decorate_function(f, **kwds)`` is basically a syntactically sweetened version of
   ``log_calls(**kwds)(f)``. However, ``log_calls.decorate_function(...)`` returns ``None``,
   whereas ``log_calls(**kwds)(f)`` returns the wrapper of ``f``.


.. _decorate_package_function-method:

Decorating an "external" function in a package
---------------------------------------------------------------------------------

.. py:classmethod:: log_calls.decorate_package_function(f: 'Callable', **setting_kwargs) -> None

   Decorate ``f`` using settings in ``settings_kwds``;
   replace the definition of ``f.__name__`` with the decorated function in the ``__dict__``
   of the *module* of ``f``.

   :param f: a function object, qualified with a package, e.g. ``somepackage.somefunc``,
     however it would be referred to in code at the point of a call to ``decorate_package_function``.
   :param setting_kwargs: settings for decorator

.. --comment-- Example?

.. _decorate_module_function-method:

Decorating an "external" function in a module
---------------------------------------------------------------------------------

.. py:classmethod:: log_calls.decorate_module_function(f: 'Callable', **setting_kwargs) -> None

   Decorate ``f`` using settings in ``settings_kwds``;
   replace the definition of ``f.__name__`` with the decorated function in the ``__dict__``
   of the module of ``f``.

   :param f: a function object, qualified with a module, e.g. ``thatmodule.afunc``,
             however it would be referred to in code at the point of a call to ``decorate_module_function``.
   :param setting_kwargs: settings for decorator


.. --comment--  More? example?


.. _decorate_module-method:

Decorating all functions and/or classes in a module
==========================================================================

``decorate_module`` lets you decorate the functions and/or classes of an imported module:

.. py:classmethod:: log_calls.decorate_module(cls, mod: 'module', functions: bool=True, classes: bool=True, **setting_kwargs) -> None

    :param mod: module whose members are to be decorated
    :param functions: decorate all functions in ``mod`` if true
    :param classes: decorate all classes in ``mod`` if true
    :param setting_kwargs: keyword parameters for decorator
    :raises: TypeError


.. _decorate-methods-examples:

Examples
======================

These modules in the ``tests/`` subdirectory contain several examples:

* ``test_decorate_module.py``
  The docstring of the function ``test_decorate_module()``
  contains simple tests of decorating the module ``tests/some_module.py``.

A few examples/tests use the `Skikit-Learn` package if it's installed.
(The following subsection reproduces one of them.)
Those in these two modules are run by ``run_tests.py``:

* ``test_decorate_sklearn_KMeans.py``
* ``test_decorate_sklearn_KMeans_functions.py``

The test in the following module decorates an entire module of `Skikit-Learn`:

* ``_test_decorate_module_of_sklearn.py``

As the settings it imposes mess up the other ``sklearn`` tests, it is **not**
run by ``run_tests.py``. It can be run separately.


.. _decorate-methods-sklearn-example:

Example — decorating a class in `scikit-learn`
------------------------------------------------

This example demonstrates:

* decorating a class that's not part of your project (unless you're working on scikit-learn:), and
* using the ``override`` parameter with one of the ``log_calls.decorate_*`` functions to dynamically
  change the settings of (all the callables of) an already-decorated class.

Except for the ``log_calls.decorate_*`` calls, the following code is excerpted
from the *sklearn* site, e.g. `Demonstration of k-means assumptions <http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_assumptions.html#example-cluster-plot-kmeans-assumptions-py>`_.
The double backslashes in the two added lines accommodate `doctest`.

    >>> from log_calls import log_calls
    >>> from sklearn.cluster import KMeans
    >>> from sklearn.datasets import make_blobs
    >>> n_samples = 1500
    >>> random_state = 170
    >>> X, y = make_blobs(n_samples=n_samples, random_state=random_state)

First, let's decorate the class hierarchy, with settings that show just the call tree:

    >>> log_calls.decorate_hierarchy(KMeans, log_args=False)        ### THIS LINE ADDED

Now let's call ``KMeans.fit_predict``:

    >>> y_pred = KMeans(n_clusters=2, random_state=random_state).fit_predict(X)
    KMeans.__init__ <== called by <module>
    KMeans.__init__ ==> returning to <module>
    KMeans.fit_predict <== called by <module>
        KMeans.fit <== called by KMeans.fit_predict
            KMeans._check_fit_data <== called by KMeans.fit
            KMeans._check_fit_data ==> returning to KMeans.fit
        KMeans.fit ==> returning to KMeans.fit_predict
    KMeans.fit_predict ==> returning to <module>

``MiniBatchKMeans`` is a subclass of ``KMeans`` so that class is decorated too:

    >>> mbk = MiniBatchKMeans(init='k-means++', n_clusters=2, batch_size=45,
    ...                       n_init=10, max_no_improvement=10)
    MiniBatchKMeans.__init__ <== called by <module>
        KMeans.__init__ <== called by MiniBatchKMeans.__init__
        KMeans.__init__ ==> returning to MiniBatchKMeans.__init__
    MiniBatchKMeans.__init__ ==> returning to <module>

Now let's call ``MiniBatchKMeans.fit``:

    >>> mbk.fit(X)           # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    MiniBatchKMeans.fit <== called by <module>
        MiniBatchKMeans._labels_inertia_minibatch <== called by MiniBatchKMeans.fit
        MiniBatchKMeans._labels_inertia_minibatch ==> returning to MiniBatchKMeans.fit
    MiniBatchKMeans.fit ==> returning to <module>
    MiniBatchKMeans(batch_size=45, compute_labels=True, init='k-means++',
            init_size=None, max_iter=100, max_no_improvement=10, n_clusters=2,
            n_init=10, random_state=None, reassignment_ratio=0.01, tol=0.0,
            verbose=0)


To view arguments as well (and trigger more output), change setting to ``log_args=True``
and use ``override=True``. Here, we call ``log_calls.decorate_class`` for class ``KMeans``
with the parameter ``decorate_subclasses=True``, which is equivalent to calling
``log_calls.decorate_hierarchy``:

    >>> log_calls.decorate_class(KMeans, decorate_subclasses=True,
    ...                          log_args=True, args_sep='\\n',
    ...                          override=True)
    >>> mbk.fit(X)                              # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
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

Note: the ellipses in the values of the ``numpy`` array ``X`` are produced by its ``repr``.
