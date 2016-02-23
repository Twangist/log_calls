.. log_calls Readme documentation master file, created by
   sphinx-quickstart on Tue Feb  9 05:14:29 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
    :hidden:
    :maxdepth: 1
    :titlesonly:

    Introduction <intro>
    installation
    quickstart
    what_log_calls_can_decorate
    keyword_parameters
    The "Settings" API <settings_api>
    Call History and Statistics <call_history_and_stats>
    indent_aware_fns
    Accessing Method Wrappers <accessing_method_wrappers>
    Retrieving and Changing the Defaults <change_set_reset_defaults>
    decorate_fns
    indirect_values
    final_example

.. role:: raw-html(raw)
   :format: html

.. |br| raw:: html

   <br />

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`log_calls` — A Decorator for Debugging and Profiling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Readme (release |release|)
############################################################

`log_calls` is a Python 3.3+ decorator that can print a lot of useful information
`log_calls` is a Python 3.3+ decorator that can print a lot of useful information
about calls to decorated functions, methods and properties. The decorator can
write to ``stdout``, to another stream or file, or to a logger. `log_calls`
provides methods for writing your own debug messages, and for easily "dumping"
variables and expressions paired with their values. It can decorate individual
functions, methods and properties; but it can also programmatically decorate
callable members of entire classes and class hierarchies, even of entire modules,
with just a single line — which can greatly expedite learning a new codebase.

In short, `log_calls` can save you from writing, rewriting, copying, pasting and
tweaking a lot of *ad hoc*, debug-only, boilerplate code — and it can keep *your*
codebase free of that clutter.

For each call to a decorated function or method, `log_calls` can show you:

* the caller (in fact, the complete call chain back to another `log_calls`-decorated caller,
  so there are no gaps in chains displayed)
* the arguments passed to the function or method, and any default values used
* nesting of calls, using indentation
* the number of the call (whether it's the 1\ :superscript:`st` call, the 2\ :superscript:`nd`,
  the 103\ :superscript:`rd`, ...)
* the return value
* the time it took to execute
* and more!

These and other features are optional and configurable settings, which can be specified
for each decorated callable via keyword parameters, as well as *en masse* for a group of
callables all sharing the same settings. You can examine and change these settings
on the fly using attributes with the same names as the keywords, or using a dict-like
interface whose keys are the keywords.

`log_calls` can also collect profiling data and statistics, accessible at runtime, such as:

* the number of calls to a function
* total time taken by the function
* the function's entire call history (arguments, time elapsed, return values, callers,
  and more), available as text in CSV format and, if `Pandas <http://pandas.pydata.org>`_
  is installed, as a `DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_.

The package contains two other decorators:

* `record_history`, a stripped-down version of `log_calls`,
  only collects call history and statistics, and outputs no messages;
* `used_unused_keywords` lets a function or method easily determine, per-call,
  which of its keyword parameters were actually supplied by the caller,
  and which received their default values.

This document gives an overview of `log_calls` features and their use.
See `the complete documentation  <http://www.pythonhosted.org/log_calls/index.html>`_
for the definitive, detailed account.

The test suites in ``log_calls/tests/``, which provide 96% coverage, contain many additional
examples, with commentary.

--------------------------------------------------------------------

.. _installation:

Installation
##################


The *log_calls* package has no dependencies — it requires no other packages.
All it requires is a standard distribution of Python 3.3 or higher (Python 3.4+ recommended).
The package won't install on earlier versions.

Installing `log_calls` is as simple as running the command

       ``$ pip install log_calls``

to install `log_calls` from PyPI (the Python Package Index). Here and elsewhere,
``$`` at the *beginning* of a line indicates your command prompt, whatever it may be.

Ideally you'll do install `log_calls` in a virtual environment (a *virtualenv*).
In Python 3.3+, it's easy to set up a virtual environment using the
`pyvenv <https://docs.python.org/3/using/scripts.html?highlight=pyvenv#pyvenv-creating-virtual-environments>`_
tool, included in the standard distribution.

..    Running the tests
..    =================
..    Each ``*.py`` file in the ``log_calls/`` directory has at least one corresponding test
..    file ``test_*.py`` in the ``log_calls/tests/`` directory. The tests provide 96+% coverage.
..    All tests have passed on every tested platform + Python version (at least half the releases
..    3.3.x through 3.5.y); however, that's a sparse matrix :) If you encounter any turbulence,
..    do let us know.
..
..    You can run the tests for `log_calls` after installing it, using the following command
..    in the top-level `log_calls` directory:
..
..        ``$ ./run_tests.py -q``
..
..    using the "quiet" (``-q``) switch. Alternately, in the ``log_calls/tests`` directory, run:
..
..        ``$ python -m unittest discover log_calls.tests``
..
..    What to expect
..    --------------
..    Both of the above commands run all tests in the ``tests/`` subdirectory. If you run
..    either of them, the output you see should end like so::
..
..
..        Ran 106 tests in 0.499s
..
..        OK
..
..    indicating that all went well. (Depending upon what packages you have installed,
..    you may see fewer tests reported.) If any test fails, it will tell you.

--------------------------------------------------------------------

.. _quickstart:

Quick Start
###########

Basic usage
==================================================

First, let's import the `log_calls` decorator from the package of the same name:

    >>> from log_calls import log_calls

In code, ``log_calls`` now refers to the decorator, a class (an object of type ``type``),
and not to the module:

    >>> type(log_calls)
    type

The decorator has many options, and thus can take many parameters,
but let's first see the simplest examples possible, using no parameters at all.

.. _quickstart-functions:

Decorating functions
---------------------

If you decorate a function with `log_calls`, each call to the function is generally
preceded and followed by some reportage. The decorator first writes messages announcing
entry to the function and what arguments it has received; the decorator calls the function
with those arguments, and the function executes; upon its return, the decorator finishes up
and announces the return of the function:

    >>> @log_calls()
    ... def f(a, b, c):
    ...     print("--- Hi from f")
    >>> f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3
    --- Hi from f
    f ==> returning to <module>

Adding another decorated function to the call chain presents useful information too. Here,
``g`` calls the decorated ``f`` above. Observe that (by default) the `log_calls` output for the
nested call to ``f`` is indented to align with the inner lines of the `log_calls` output for ``g``:

    >>> @log_calls()
    ... def g(n):
    ...     print("*** Hi from g")
    ...     f(n, 2*n, 3*n)
    ...     print("*** Bye from g")
    >>> g(3)
    g <== called by <module>
        arguments: n=3
    *** Hi from g
        f <== called by g
            arguments: a=3, b=6, c=9
    --- Hi from f
        f ==> returning to g
    *** Bye from g
    g ==> returning to <module>

`log_calls` gives informative output even when call chains include undecorated functions.
In the next example, a decorated function ``h`` calls an undecorated ``g2``, which calls
an undecorated ``g1``, which, finally, calls our original decorated ``f``:

    >>> def g1(n): f(n, 2*n, 3*n)
    >>> def g2(n): g1(n)
    >>> @log_calls()
    ... def h(x, y): g2(x+y)

Now let's call ``h``:

    >>> h(2, 3)
    h <== called by <module>
        arguments: x=2, y=3
        f <== called by g1 <== g2 <== h
            arguments: a=5, b=10, c=15
    --- Hi from f
        f ==> returning to g1 ==> g2 ==> h
    h ==> returning to <module>

Notice that when writing entry and exit messages for ``f``, `log_calls` displays
the entire active call chain *back to the nearest decorated function*, so that there
aren't "gaps" in the chain of functions it reports on. If it didn't do this, we'd
see only ``f <== called by g1`` and then ``f ==> returning to g1`` followed by
``h ==> returning to <module>``, which wouldn't tell us the whole story about how
control reached ``g1`` from ``h``.


.. _quickstart-methods:

Decorating methods
-------------------

Similarly, you can decorate methods (and properties) within a class:

    >>> class A():
    ...     def __init__(self, n):
    ...         self.n = n
    ...
    ...     @log_calls()
    ...     def ntimes(self, m):
    ...         return self.n * m

Only the ``ntimes`` method is decorated:

    >>> a = A(3)            # __init__ called
    >>> a.ntimes(4)                 # doctest: +ELLIPSIS
    A.ntimes <== called by <module>
        arguments: self=<__main__.A object at 0x...>, m=4
    A.ntimes ==> returning to <module>
    12

.. _quickstart-classes:

Decorating classes
------------------------

To decorate all methods of a class, simply decorate the class itself:

    >>> @log_calls()
    ... class C():
    ...     def __init__(self, n):
    ...         self.n = n if n >= 0 else -n
    ...
    ...     @staticmethod
    ...     def revint(x): return int(str(x)[::-1])
    ...
    ...     @property
    ...     def revn(self): return self.revint(self.n)

All methods of ``C`` are now decorated. Creating an instance logs the call to ``__init__``:

    >>> c = C(123)                    # doctest: +ELLIPSIS
    C.__init__ <== called by <module>
        arguments: self=<__main__.C object at 0x...>, n=123
    C.__init__ ==> returning to <module>

Accessing its ``revn`` property calls the staticmethod ``revint``, and both calls are logged:

    >>> c.revn                        # doctest: +ELLIPSIS
    C.revn <== called by <module>
        arguments: self=<__main__.C object at 0x...>
        C.revint <== called by C.revn
            arguments: x=123
        C.revint ==> returning to C.revn
    C.revn ==> returning to <module>
    321

If you want to decorate only some of the methods of a class, you *don't* have to
individually decorate all and only all the ones you want: the ``only`` and ``omit``
keyword parameters to the class decorator let you concisely specify which methods
will and won't be decorated. See the :ref:`keyword_parameters_reference` section
for details.


Decorating *most* methods, overriding the settings of one method
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Suppose you have a class ``D`` that's just like ``C`` but adds a ``double()`` method.
(For the sake of the example, never mind that in practice you might subclass ``C``.)
Suppose you want to decorate all callables in ``D`` *except* ``revint``,
and furthermore, you want `log_calls` to report values returned by the property getter
``revn``. Here's how to do it:

    >>> @log_calls(omit='revint')
    ... class D():
    ...     def __init__(self, n):
    ...         self.n = n if n >= 0 else -n
    ...
    ...     @staticmethod
    ...     def revint(x): return int(str(x)[::-1])
    ...
    ...     def double(self): return self.n + self.n
    ...
    ...     @property
    >>>     @log_calls(log_retval=True)
    ...     def revn(self): return self.revint(self.n)

By default, `log_calls` does *not* display return values, and the outer, class-level
decorator uses that default. The explicit decorator of ``revn`` overrides that,
specifying the desired setting. Note that ``@log_calls`` follows ``@property``:
in general, when decorating a callable in a class, ``@log_calls``
should come *after* any ``@property``, ``@classmethod`` or ``@staticmethod`` decorator.

Let's see this class in action:

    >>> d = D(71)                                           # doctest: +ELLIPSIS
    D.__init__ <== called by <module>
        arguments: self=<__main__.D object at 0x...>, n=71
    D.__init__ ==> returning to <module>

The return value of ``d.double()`` is *not* logged:

    >>> d.double()                                          # doctest: +ELLIPSIS
    D.double <== called by <module>
        arguments: self=<__main__.D object at 0x...>
    D.double ==> returning to <module>

However, the return value of ``revn`` *is* logged, and ``revint`` has *not* been decorated:

    >>> print('~~~\\nMy favorite number plus 3 is', d.revn + 3)   # doctest: +ELLIPSIS
    D.revn <== called by <module>
        arguments: self=<__main__.D object at 0x...>
        D.revn return value: 17
    D.revn ==> returning to <module>
    ~~~
    My favorite number plus 3 is 20

(*A* doctest *quirk: the* doctest *examples in this document use* ``'\\n'``
*where in actual code you'd write* ``'\n'``. *All the examples herein work
(as tests, they pass), but they would fail if* ``'\n'`` *were used.*)

These examples have shown just a few of the features that make `log_calls` powerful, versatile,
yet easy to use. They have also introduced a couple of `log_calls`'s keyword parameters,
the source of much of that versatility. The :ref:`keyword_parameters` section introduces them all;
the :ref:`keyword_parameters_reference` documents each one concisely.


--------------------------------------------------------------------

.. _what-log_calls-can-decorate:

What *log_calls* Can Decorate
###################################

In this document, the phrase "decorated callable" appears frequently. Generally we use
*callable* as a generic term that includes global functions as well as methods and properties
of classes. We use it to emphasize that what is said applies equally to global functions,
methods and properties, and indeed to anything that `log_calls` can decorate.

We use more the specific terms *decorated function*, *decorated method*, and so on, as
appropriate for examples, and when what is said applies to the narrower class of callables
named but perhaps not to all callables.

.. _functional-def:

.. index:: functional

.. sidebar:: "functional"

    A *functional* is a higher-order function, a function of functions.

    * When passed a function *fn*, ``log_calls(**kwds)(``\ *fn*\ ``)`` returns a function;
    * when passed a class *klass*, ``log_calls(**kwds)(``\ *klass*\ ``)`` returns the class *klass*.

Functions defined with ``def``, methods and properties don't exhaust the callables that
`log_calls` can decorate. Lambda expressions are functions, and *can* be decorated by using
``log_calls()`` as a *functional*, without the ``@`` syntactic sugar:

    >>> f = log_calls()(lambda x: 2 * x)
    >>> f(3)
    <lambda> <== called by <module>
        arguments: x=3
    <lambda> ==> returning to <module>
    6

The question arises: what, exactly, *can* `log_calls` decorate? (and thus, what can't it decorate?)
We won't attempt to give necessary and sufficient conditions for that set of callables.
But the following is true:

    Anything that `log_calls` can decorate is a callable, |br|
    but not every callable can be decorated by `log_calls`.


Whatever `log_calls` **cannot** decorate, it simply returns unchanged.

.. index:: callable

.. _what-is-a-callable-label:

What is a "callable"?
==============================================

Loosely, a "callable" is anything that can be called. In Python, the term has a precise meaning,
encompassing not only functions and methods but also classes, as well as instances of classes
that implement a ``__call__`` method. A correct though unsatisfying definition is: an object
is *callable* iff the builtin ``callable`` function returns ``True`` on that object.
The Python documentation for
`callable <https://docs.python.org/3/library/functions.html?highlight=callable#callable>`_
is good as far as it goes, but a bit breezy; greater detail can be found in the stackoverflow Q&A
`What is a “callable” in Python? <http://stackoverflow.com/questions/111234/what-is-a-callable-in-python>`_
and in the articles cited there.

.. _callables-that-log_calls-cannot-decorate:

Examples, mostly negative
==============================================

`log_calls` can't decorate callable builtins, such as ``len`` — it just returns the builtin unchanged:

    >>> len is log_calls()(len)  # No "wrapper" around len -- not deco'd
    True
    >>> dict.update is log_calls(log_elapsed=True)(dict.update)
    True

Similarly, `log_calls` doesn't decorate builtin or extension type classes, returning the class unchanged:

    >>> _ = log_calls()(dict)
    >>> dict(x=1)               # dict.__init__ not decorated, no output

It also doesn't decorate various objects which are callables by virtue of having
a ``__call__`` method, such as ``functools.partial`` objects:

    >>> from functools import partial
    >>> def h(x, y): return x + y
    >>> h2 = partial(h, 2)        # so h2(3) == 5
    >>> h2lc = log_calls()(h2)
    >>> h2lc is h2                # not deco'd
    True

However, `log_calls` *can* decorate *classes*  whose instances are callables
by virtue of implementing a ``__call__`` method:

    >>> @log_calls()
    ... class Rev():
    ...     def __call__(self, s):  return s[::-1]
    >>> rev = Rev()
    >>> callable(rev)
    True
    >>> rev('ABC')                        # doctest: +ELLIPSIS
    Rev.__call__ <== called by <module>
        arguments: self=<Rev object at 0x...>, s='ABC'
    Rev.__call__ ==> returning to <module>
    'CBA'

--------------------------------------------------------------------


.. _keyword_parameters:

The Keyword Parameters
####################################

`log_calls` has many features, and thus many, mostly independent, keyword parameters
(21 in release |release|), all with hopefully sensible default values. We'll
introduce them collectively, in two categories, and then document each one.

Parameters that are "settings", parameters that are not
=============================================================

.. _the-settings:
.. _what-is-a-setting:

Three quarters of the keyword parameters correspond to *settings*, which comprise the *state*
of a decorated callable:

* the destination of `log_calls` output — which stream, or file, or logger
* what that output will look like and how much detail it will contain — customizations
* whether all or part of that output should be muted
* whether to record the history of calls to the callable, and if so, how much of it.

These keyword parameters are settings::

    enabled                    prefix
    args_sep                   file
    log_args                   mute
    log_retval                 logger
    log_exit                   loglevel
    log_call_numbers           record_history
    log_elapsed                max_history
    indent


As explained below, all of a decorated callable's settings can be accessed
dynamically, and almost all can be changed on the fly.

.. _the-non-settings:

The other keyword parameters are (almost all) directives to the decorator
governing what it decorates and how::

    NO_DECO                    override
    settings                   omit
    name                       only

Their initial values aren't available via attributes of the wrapper,
and can't subsequently be changed.



.. _keyword_parameters_reference:


"Settings" Keyword Parameters
--------------------------------------

+---------------------+-------------------+-------------------------------------------------------------+
| Keyword parameter   | Default value     || Description                                                |
+=====================+===================+=============================================================+
| ``enabled``         | ``1`` (``True``)  || An ``int``. If positive (or ``True``), then `log_calls`    |
|                     |                   || will output (or "log") messages. If false ("disabled":     |
|                     |                   || ``0``, alias ``False``), `log_calls` won't output messages |
|                     |                   || or record history but will maintain its count of the       |
|                     |                   || total number of calls to the callable. If negative         |
|                     |                   || ("bypassed"), `log_calls` won't do anything.               |
+---------------------+-------------------+-------------------------------------------------------------+
| ``args_sep``        | ``', '``          || ``str`` used to separate arguments. The default lists      |
|                     |                   || all args on the same line. If ``args_sep`` is (or ends     |
|                     |                   || in) ``'\n'``, then additional spaces are appended to       |
|                     |                   || the separator for a neater display. Other separators       |
|                     |                   || in which ``'\n'`` occurs are left unchanged, and are       |
|                     |                   || untested – experiment/use at your own risk.                |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_args``        | ``True``          || If true, `log_calls` will log arguments passed to          |
|                     |                   || the decorated callable, as well as any default values      |
|                     |                   || used for its keyword parameters.                           |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_retval``      | ``False``         || If true, `log_calls` will log what the decorated           |
|                     |                   || callable returns. At most 77 chars are printed,            |
|                     |                   || with a trailing ellipsis if the value is truncated.        |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_exit``        | ``True``          || If true, `log_calls` will log an exiting message           |
|                     |                   || after the decorated callable returns, and before           |
|                     |                   || returning what the callable returned. The message          |
|                     |                   || is of the form                                             |
|                     |                   ||         ``f returning to ==> caller``                      |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_call_numbers``| ``False``         || If true, `log_calls` displays the (1-based) number         |
|                     |                   || of the call, e.g.                                          |
|                     |                   ||         ``f [3] called by <== <module>``                   |
|                     |                   || and                                                        |
|                     |                   ||         ``f [3] returning to ==> <module>``                |
|                     |                   || for the 3rd logged call. These would correspond to         |
|                     |                   || the 3rd record in the callable's call history,             |
|                     |                   || if ``record_history`` is true.                             |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_elapsed``     | ``False``         || If true, `log_calls` displays how long the callable took   |
|                     |                   || to execute, in seconds (elapsed time and process time).    |
+---------------------+-------------------+-------------------------------------------------------------+
| ``indent``          | ``False``         || When true, each new level of logged messages is            |
|                     |                   || indented by 4 spaces, giving a visualization               |
|                     |                   || of the call hierarchy.                                     |
+---------------------+-------------------+-------------------------------------------------------------+
| ``prefix``          | ``''``            || A ``str`` with which to prefix the callable's name         |
|                     |                   || in logged messages: on entry, in reporting return          |
|                     |                   || values (if ``log_retval`` is true) and on exit (if         |
|                     |                   || ``log_exit`` is true).                                     |
+---------------------+-------------------+-------------------------------------------------------------+
| ``file``            | ``sys.stdout``    || If ``logger`` is ``None``, a stream (an instance of type   |
|                     |                   || ``io.TextIOBase``) to which `log_calls` will print its     |
|                     |                   || messages. This value is supplied to the ``file``           |
|                     |                   || keyword parameter of the ``print`` function.               |
+---------------------+-------------------+-------------------------------------------------------------+
| ``mute``            | ``0`` (``False``) || Three-valued ``int`` that controls the amount of output:   |
|                     |                   ||   ``log_calls.MUTE.NOTHING`` (0) — mute nothing            |
|                     |                   ||   ``log_calls.MUTE.CALLS``   (1) —                         |
|                     |                   ||          mutes `log_calls` own output, but allows          |
|                     |                   ||          output of ``log_message()`` and ``log_exprs()``   |
|                     |                   ||   ``log_calls.MUTE.ALL``     (2) — mute all output         |
+---------------------+-------------------+-------------------------------------------------------------+
| ``logger``          | ``None``          || If not ``None``, either a logger (a ``logging.Logger``     |
|                     |                   || instance), or the name of a logger (a ``str`` that will    |
|                     |                   || be passed to ``logging.getLogger()``); that logger         |
|                     |                   || will be used to write messages, provided it has            |
|                     |                   || handlers; otherwise, ``print`` is used.                    |
+---------------------+-------------------+-------------------------------------------------------------+
| ``loglevel``        | ``logging.DEBUG`` || Logging level, ignored unless a logger is specified.       |
|                     |                   || This should be one of the logging levels defined by        |
|                     |                   || the ``logging`` module, or a custom level.                 |
+---------------------+-------------------+-------------------------------------------------------------+
| ``record_history``  | ``False``         || If true, a list of records will be kept, one for each      |
|                     |                   || logged call to the decorated callable. Each record         |
|                     |                   || holds: call number (1-based), arguments, defaulted         |
|                     |                   || keyword arguments, return value, time elapsed,             |
|                     |                   || time of call, prefixed name, caller (call chain).          |
|                     |                   || The value of this attribute is a ``namedtuple``.           |
+---------------------+-------------------+-------------------------------------------------------------+
| ``max_history``     | ``0``             || An ``int``.                                                |
|                     |                   || If *value* > 0, store at most *value*-many records,        |
|                     |                   || records, oldest records overwritten;                       |
|                     |                   || if *value* ≤ 0, store unboundedly many records.            |
|                     |                   || Ignored unless ``record_history`` is true.                 |
|                     |                   || This setting can be changed only by calling                |
|                     |                   ||  `wrapper`\ ``.stats.clear_history(max_history=0)``        |
|                     |                   || (q.v.) on the `wrapper` of a decorated callable.           |
+---------------------+-------------------+-------------------------------------------------------------+

.. _non-settings-appendix-I:

Non-"Settings" Keyword Parameters
--------------------------------------

+---------------------+-------------------+------------------------------------------------------------------+
| Keyword parameter   | Default value     |   Description                                                    |
+=====================+===================+==================================================================+
| ``settings``        | ``None``          || A dict that maps settings keywords and/or ``NO_DECO``           |
|                     |                   || to values — a *settings dict* — or a string giving              |
|                     |                   || the pathname to a *settings file* containing settings           |
|                     |                   || and values. If the pathname is a directory and not a file,      |
|                     |                   || `log_calls` looks for a file ``.log_calls`` in that directory;  |
|                     |                   || otherwise, it looks for the named file.                         |
|                     |                   || The format of a settings file is: zero or more lines of the     |
|                     |                   || form *setting* = *value*; lines whose first non-whitespace      |
|                     |                   || character is ``'#'`` are comments. These settings are           |
|                     |                   || a baseline; other settings passed to `log_calls` can            |
|                     |                   || override their values.                                          |
+---------------------+-------------------+------------------------------------------------------------------+
| ``name``            | ``''``            || Specifies the display name of a decorated callable, if          |
|                     |                   || nonempty, and then, it must be a ``str``, of the form:          |
|                     |                   || * the preferred name of the callable (a string literal), or     |
|                     |                   || * an old-style format string with one occurrence of ``%s``,     |
|                     |                   ||   which the ``__name__`` of the decorated callable replaces.    |
+---------------------+-------------------+------------------------------------------------------------------+
| ``omit``            | ``tuple()``       || A string or sequence of strings designating callables of        |
|                     |                   || a class. Supplied to a class decorator, ignored in function     |
|                     |                   || decorations. The designated callables will *not* be decorated.  |
|                     |                   || Each of these "designators" can be a name of a method           |
|                     |                   || or property, a name of a property with an appended              |
|                     |                   || qualifier ``.getter``, ``.setter``, or ``.deleter``; it can     |
|                     |                   || have prefixed class names (``Outer.Inner.mymethod``).           |
|                     |                   || It can also contain "glob" wildcards ``*?``, character sets     |
|                     |                   || ``[aqrstUWz_]``, character ranges ``[r-t]``, combinations       |
|                     |                   || of these ``[a2-9f-hX]``, and complements ``[!acr-t]``.          |
|                     |                   || Allowed formats:                                                |
|                     |                   || ``'f'``,   ``'f g h'``,   ``'f, g, h'``, ``[f, g, h]``,         |
|                     |                   | ``(f, g, h)``, or indeed any sequence of designators.            |
+---------------------+-------------------+------------------------------------------------------------------+
| ``only``            | ``tuple()``       || A string or sequence of strings designating callables of        |
|                     |                   || a class. Supplied to a class decorator, ignored in function     |
|                     |                   || decorations. Only the designated callables will be              |
|                     |                   || decorated, excluding any specified by ``omit``. These           |
|                     |                   || "designators" are as described for ``omit``. Allowed formats    |
|                     |                   || of sequences of designators are also as described for ``omit``. |
+---------------------+-------------------+------------------------------------------------------------------+
| ``override``        | ``False``         || `log_calls` respects explicitly given settings of already-      |
|                     |                   || decorated callables and classes. Classes are decorated          |
|                     |                   || from the inside out, so explicitly given settings of any        |
|                     |                   || inner decorators are unchanged by an outer class decorator.     |
|                     |                   || To give the settings of the outer decorator priority,           |
|                     |                   || supply it with ``override=True``.                               |
|                     |                   || ``override`` can be used with the ``log_calls.decorate_*``      |
|                     |                   || classmethods, in order to change existing settings              |
|                     |                   || of decorated callables or classes.                              |
+---------------------+-------------------+------------------------------------------------------------------+
| ``NO_DECO``         | ``False``         || When true, prevents `log_calls` from decorating a callable      |
|                     |                   || or class. Intended for use at program startup, it provides      |
|                     |                   || a single "true bypass" switch when placed in a global           |
|                     |                   || *settings dict* or *settings file*.                             |
+---------------------+-------------------+------------------------------------------------------------------+

.. note::
    Admittedly, ``name`` would make a plausible "setting". In a future version
    of `log_calls`, it probably will be one.

--------------------------------------------------------------------

.. _settings-API:

The "Settings" API: the ``log_calls_settings`` Attribute
#############################################################

.. _wrapper-settings-of-a-callable:

When `log_calls` decorates a callable (a function, method, property, ...), it "wraps" that
callable in a function — the *wrapper* of the callable. Subsequently, calls to the decorated
callable actually call the wrapper, which delegates to the original, in between its own
pre- and post-processing. This is simply what the typical decorator does.


`log_calls` gives the wrapper a few attributes pertaining to the wrapped callable, notably
``log_calls_settings``, a dict-like object that contains the `log_calls` state of the callable.
The keys of ``log_calls_settings`` are just the "settings" keyword parameters listed above.

**The** *settings of a decorated callable* **are the key/value pairs of its**
``log_calls_settings`` **object**, an attribute of the callable's wrapper.
The settings comprise the `log_calls` state of the callable.

Changing the settings of a decorated callable
=================================================

Sometimes, you'll need or want to change a `log_calls` setting for a decorated callable
on the fly. The major impediment to doing so is that the values of the `log_calls`
parameters are set once the definition of the decorated callable is interpreted.
Those values are established once and for all when the Python interpreter
processes the definition.

Even if a variable is used as a parameter value, its value at the time
Python processes the definition is "frozen" for the created callable object.
What gets stored is not the variable, but its value. Subsequently changing
the value of the variable will *not* affect the behavior of the decorator.

For example, suppose ``DEBUG`` is a module-level variable initialized to ``False``:

    >>> DEBUG = False

and you use this code:

    >>> @log_calls(enabled=DEBUG)
    ... def foo(**kwargs): pass
    >>> foo()       # No log_calls output: DEBUG is False

If later you set ``DEBUG = True`` and call ``foo``, that call still won't be logged,
because the ``enabled`` setting of ``foo`` is bound to the original *value*
of ``DEBUG``, established when the definition was processed:

    >>> DEBUG = True
    >>> foo()       # Still no log_calls output

(This is simply how default values of keyword parameters work in Python.)

`log_calls` provides *three* ways to overcome this limitation
and dynamically control the settings of a decorated callable:

* the ``log_calls.decorate_*`` classmethods, described briefly in :ref:`decorate-functions`;
* the ``log_calls_settings`` attribute, described in this chapter, which provides a mapping interface
  and an attribute-based interface to settings;
* *indirect values*, described briefly in :ref:`indirect-values`.


Dict-like and attribute-based access to settings
=====================================================

The ``log_calls_settings`` attribute of a decorated callable is an object that
lets you read and, for almost all settings, change the callable's settings, using a mapping
(``dict``-like) interface, and equivalently, via attributes of the object. The mapping keys
and the attribute names are simply the `log_calls` settings keywords. ``log_calls_settings`` also
implements many of the standard ``dict`` methods for interacting with the settings in familiar ways.

A few simple examples will clarify these concepts. Let's decorate a function
with a couple of non-default settings:

    >>> @log_calls(args_sep=' / ', log_exit=False)
    ... def f(x, y): pass

    >>> f(1, 2)
    f <== called by <module>
        arguments: x=1 / y=2

    >>> f.log_calls_settings['args_sep']
    ' / '
    >>> f.log_calls_settings['log_exit']
    False
    >>> f.log_calls_settings['enabled']
    True

Initially the value of a setting is the value passed to the `log_calls` decorator for
the corresponding keyword parameter, or the default value for that parameter if no
argument was supplied for it. In order to view all the current settings, we use
the ``as_OD()`` method, which returns a copy of the settings as an ``OrderedDict``.
(There's also an ``as_dict()`` method, which returns a ``dict`` and so is less
"doctestable".)

    >>> f.log_calls_settings.as_OD()   # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True),         ('args_sep', ' / '),
                 ('log_args', True),        ('log_retval', False),
                 ('log_elapsed', False),    ('log_exit', False),
                 ('indent', True),          ('log_call_numbers', False),
                 ('prefix', ''),            ('file', None),
                 ('logger', None),          ('loglevel', 10),
                 ('mute', False),           ('record_history', False),
                 ('max_history', 0)])

``log_calls_settings`` can then be used not only to read settings values, as seen above,
but also to write them:

    >>> f.log_calls_settings['args_sep'] = '\\n'
    >>> f(1, 2)                                 # doctest: +NORMALIZE_WHITESPACE
    f <== called by <module>
        arguments:
            x=1
            y=2

You can also use the settings keywords as attributes of ``log_calls_settings``
instead of as keys to the mapping interface; they're completely equivalent:

    >>> f.log_calls_settings.log_args = False
    >>> f.log_calls_settings.log_exit = True
    >>> f(1, 2)                                 # doctest: +NORMALIZE_WHITESPACE
    f <== called by <module>
    f ==> returning to <module>

``log_calls_settings`` has a length ``len(log_calls_settings)``;
its keys and ``items()`` can be iterated through; you can use ``in`` to test
for key membership; and it has an ``update()`` method, described next. As with an
ordinary dictionary, attempting to access a nonexistent setting raises ``KeyError``.
Unlike an ordinary dictionary, you can't add new keys – the ``log_calls_settings``
dictionary is closed to new members, and attempts to add one will also raise ``KeyError``.

The ``update()``, ``as_dict()``, and ``as_OD()`` methods
======================================================================

The ``log_calls_settings.update()`` method lets you update several settings at once:

    >>> f.log_calls_settings.update(
    ...     log_args=True, args_sep=', ', log_call_numbers=True, log_exit=False)
    >>> _ = f(5, 6)
    f [1] <== called by <module>
        arguments: x=5,  y=6

You can retrieve the entire collection of settings as a ``dict`` using ``as_dict()``,
and as an ``OrderedDict`` using the ``as_OD()`` method.
Either can serve as a snapshot of the settings, so that you can change settings
temporarily, use the new settings, and then use ``update()`` to restore settings
from the snapshot. in addition to taking keyword arguments, as shown above,
``update()`` can take one or more dicts – in particular, a dictionary retrieved
from one of the ``as_*`` methods:

.. py:method:: wrapper.log_calls_settings.update(*dicts, **settings_kwargs) -> None
   :noindex:

   Update the settings from all dicts in ``dicts``, in order, and then from ``settings_kwargs``.
   Allow but ignore attempts to write to immutable keys (``max_history``).
   This permits the user to retrieve a copy of the settings with ``as_dict()``
   or ``as_OD()``, obtaining a dictionary which will contain items for
   immutable settings too; make changes to settings and use them;
   then restore the original settings by passing the retrieved dictionary to ``update``.

   :param dicts: a sequence of dicts containing setting keywords and values
   :param settings_kwargs: additional settings and values

--------------------------------------------------------------------

.. _call_history_statistics:

Call History and Statistics: the ``stats`` Attribute
########################################################

Unless it's *bypassed* (``enabled`` setting < 0), `log_calls` always collects
at least a few basic statistics about each call to a decorated callable.
When the ``record_history`` setting is true for a decorated callable,
`log_calls` accumulates a sequence of records holding the details of each
logged call to the callable:

    A *logged call* to a decorated callable is one that occurs when
    the callable's ``enabled`` setting is true.

The statistics and history are accessible via the ``stats`` attribute,
which `log_calls` adds to the wrapper of a decorated callable.

Let's define a function ``f`` and decorate it to record its call history:

    >>> @log_calls(record_history=True, log_call_numbers=True, log_exit=False)
    ... def f(a, *args, x=1, **kwargs): pass

In the next few subsections, we'll call this function, manipulate its settings,
and examine its statistics and history.


.. _stats-attribute:

The ``stats`` attribute and *its* attributes
================================================

The ``stats`` attribute of a decorated callable is an object that provides
read-only statistics and data about the calls to a decorated callable:

* :ref:`stats.num_calls_logged <num_calls_logged>`
* :ref:`stats.num_calls_total <num_calls_total>`
* :ref:`stats.elapsed_secs_logged <elapsed_secs_logged>`
* :ref:`stats.process_secs_logged <process_secs_logged>`
* :ref:`stats.history <history>`
* :ref:`stats.history_as_csv <history_as_csv>`
* :ref:`stats.history_as_DataFrame <history_as_DataFrame>`

The first four of these don't depend on the ``record_history`` setting at all.
The last three values, ``stats.history*``, are empty unless ``record_history``
is or has been true.

The ``stats`` attribute also provides one method, ``stats.clear_history()``.

Let's call the function ``f`` twice:

    >>> f(0)
    f [1] <== called by <module>
        arguments: a=0
        defaults:  x=1
    >>> f(1, 100, 101, x=1000, y=1001)
    f [2] <== called by <module>
        arguments: a=1, *args=(100, 101), x=1000, **kwargs={'y': 1001}

and explore its ``stats``.

.. _num_calls_logged:

The ``num_calls_logged`` attribute
----------------------------------------------

The ``stats.num_calls_logged`` attribute holds the number of the most
recent logged call to a decorated callable. Thus, ``f.stats.num_calls_logged``
will equal 2:

    >>> f.stats.num_calls_logged
    2

This counter is incremented on each logged call to the callable, even if its
`log_call_numbers` setting is false.

.. _num_calls_total:

The ``num_calls_total`` attribute
-----------------------------------------------

The ``stats.num_calls_total`` attribute holds the *total* number of calls
to a decorated callable. This counter is incremented even when logging
is disabled for a callable (its ``enabled`` setting is ``0`` i.e. ``False``),
but *not* when it's "bypassed" (its ``enabled`` setting is less than ``0``).

To illustrate, let's now *disable* logging for ``f`` and call it 3 more times:

    >>> f.log_calls_settings.enabled = False
    >>> for i in range(3): f(i)

Now ``f.stats.num_calls_total`` will equal 5, but ``f.stats.num_calls_logged``
will still equal 2:

    >>> f.stats.num_calls_total
    5
    >>> f.stats.num_calls_logged
    2

Finally, let's re-enable logging for ``f`` and call it again.
The displayed call number will be the number of the *logged* call, 3, the same
value as ``f.stats.num_calls_logged`` after the call:

    >>> f.log_calls_settings.enabled = True
    >>> f(10, 20, z=5000)
    f [3] <== called by <module>
        arguments: a=10, *args=(20,), **kwargs={'z': 5000}
        defaults:  x=1

    >>> f.stats.num_calls_total
    6
    >>> f.stats.num_calls_logged
    3

.. _elapsed_secs_logged:

The ``elapsed_secs_logged`` attribute
------------------------------------------------

The ``stats.elapsed_secs_logged`` attribute holds the sum of the elapsed times of
all logged calls to a decorated callable, in seconds. Here's its value for the three
logged calls to ``f`` above (this doctest is actually ``+SKIP``\ ped):

    >>> f.stats.elapsed_secs_logged   # doctest: +SKIP
    6.67572021484375e-06

.. _process_secs_logged:

The ``process_secs_logged`` attribute
------------------------------------------------

The ``stats.process_secs_logged`` attribute holds the sum of the process times
of all *logged* calls to a decorated callable, in seconds.
Here's its value for the three logged calls to `f` above (this doctest is
actually ``+SKIP``\ ped):

    >>> f.stats.process_secs_logged   # doctest: +SKIP
    1.1000000000038757e-05

.. _history:

The ``history`` attribute
--------------------------------------------

The ``stats.history`` attribute of a decorated callable provides the call history
of logged calls as a tuple of records. Each record is a ``namedtuple``
of type ``CallRecord``, whose fields are these::

    argnames
    argvals
    varargs
    explicit_kwargs
    defaulted_kwargs
    implicit_kwargs
    retval
    elapsed_secs
    process_secs
    timestamp
    prefixed_func_name
    caller_chain

The ``stats.elapsed_secs_logged`` and ``stats.process_secs_logged`` attributes contain
the sums of the ``elapsed_secs`` and ``process_secs`` "columns", respectively.

.. _history_as_csv:

The ``history_as_csv`` attribute
-------------------------------------------------

The value ``stats.history_as_csv`` attribute is a text representation in CSV format
of a decorated callable's call history. You can save this string
and import it into the program or tool of your choice for further analysis.
(If your tool of choice is `Pandas <http://pandas.pydata.org>`_, you can use
:ref:`history_as_DataFrame`, discussed next, to obtain history directly in
the representation you really want.)

The CSV representation breaks out each parameter into its own column, throwing away
information about whether an argument's value was explicitly passed or is a default.

The CSV separator is '|' rather than ',' because some of the fields – ``args``,  ``kwargs``
and ``caller_chain`` – use commas intrinsically. Let's examine ``history_as_csv``
for a function that has all of those fields nontrivially:

    >>> @log_calls(record_history=True, log_call_numbers=True,
    ...            log_exit=False, log_args=False)
    ... def f(a, *extra_args, x=1, **kw_args): pass
    >>> def g(a, *args, **kwargs):
    ...     f(a, *args, **kwargs)
    >>> @log_calls(log_exit=False, log_args=False)
    ... def h(a, *args, **kwargs):
    ...     g(a, *args, **kwargs)
    >>> h(0)
    h <== called by <module>
        f [1] <== called by g <== h
    >>> h(10, 17, 19, z=100)
    h <== called by <module>
        f [2] <== called by g <== h
    >>> h(20, 3, 4, 6, x=5, y='Yarborough', z=100)
    h <== called by <module>
        f [3] <== called by g <== h

Here's the call history of ``f`` in CSV format (ellipses added for the ``elapsed_secs``,
``process_secs`` and ``timestamp`` fields):

    >>> print(f.stats.history_as_csv)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    call_num|a|extra_args|x|kw_args|retval|elapsed_secs|process_secs|timestamp|prefixed_fname|caller_chain
    1|0|()|1|{}|None|...|...|...|'f'|['g', 'h']
    2|10|(17, 19)|1|{'z': 100}|None|...|...|...|'f'|['g', 'h']
    3|20|(3, 4, 6)|5|{'y': 'Yarborough', 'z': 100}|None|...|...|...|'f'|['g', 'h']
    <BLANKLINE>

In tabular form,

+----------+----+------------+---+----------------------+--------+--------------+--------------+-----------+----------------+--------------+
| call_num | a  | extra_args | x | kw_args              | retval | elapsed_secs | process_secs | timestamp | prefixed_fname | caller_chain |
+==========+====+============+===+======================+========+==============+==============+===========+================+==============+
| 1        | 0  | ()         | 1 || {}                  | None   |     ...      |     ...      |    ...    | 'f'            | ['g', 'h']   |
+----------+----+------------+---+----------------------+--------+--------------+--------------+-----------+----------------+--------------+
| 2        | 10 | (17, 19)   | 1 || {'z': 100}          | None   |     ...      |     ...      |    ...    | 'f'            | ['g', 'h']   |
+----------+----+------------+---+----------------------+--------+--------------+--------------+-----------+----------------+--------------+
| 3        | 20 | (3, 4, 6)  | 5 || {'y': 'Yarborough', | None   |     ...      |     ...      |    ...    | 'f'            | ['g', 'h']   |
|          |    |            |   ||  'z': 100}          |        |              |              |           |                |              |
+----------+----+------------+---+----------------------+--------+--------------+--------------+-----------+----------------+--------------+

As usual, `log_calls` will use whatever names you use for *varargs* parameters
(here, ``extra_args`` and ``kw_args``). Whatever the name of the ``kwargs`` parameter,
items within that field are guaranteed to be in sorted order.

.. _history_as_DataFrame:

The ``history_as_DataFrame`` attribute
--------------------------------------------------------

The ``stats.history_as_DataFrame`` attribute returns the history of a decorated
callable as a `Pandas <http://pandas.pydata.org>`_
`DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_,
if the Pandas library is installed. This saves you the intermediate step of
calling ``DataFrame.from_csv`` with the proper arguments (and also saves you from
having to know or care what those are).

If Pandas is not installed, the value of this attribute is ``None``.

.. _clear_history:

The ``clear_history()`` method
------------------------------------------------------------

As you might expect, the ``stats.clear_history(max_history=0)`` method clears
the call history of a decorated callable. In addition, it resets all running sums:

* ``num_calls_total`` and ``num_calls_logged`` are reset to ``0``,
* ``elapsed_secs_logged`` and ``process_secs_logged`` are reset to ``0.0``.

**This method is the only way to *change* the value of the ``max_history`` setting**,
via the optional keyword parameter for which you can supply any (integer) value,
by default ``0``.

The function ``f`` has a nonempty history, as we just saw. Let's clear ``f``'s history,
setting ``max_history`` to ``33``:

    >>> f.stats.clear_history(max_history=33)

and check that settings and ```stats``` tallies are reset:

    >>> f.log_calls_settings.max_history
    33
    >>> f.stats.num_calls_logged
    0
    >>> f.stats.num_calls_total
    0
    >>> f.stats.elapsed_secs_logged
    0.0
    >>> f.stats.process_secs_logged
    0.0

--------------------------------------------------------------------

.. _indent-aware-functions:

Writing Indent-Aware Debug Messages
####################################################################################
.. The Indent-Aware Writing Methods ``log_message()`` and ``log_exprs()``

.. _log_message-method:

``log_message()``
=====================

``log_message()`` is an indent-aware replacement for ``print()`` which decorated
callables can use to write debugging messages aligned within the `log_calls` visual frame,
to the same destination as `log_calls`'s own output.
Even multiline messages are indented properly. ``log_message()`` is called *on
the decorated callable's wrapper*.

    >>> @log_calls()
    ... def f(x):
    ...     f.log_message("Hello.\\nThat's all for now.")
    >>> f(2)
    f <== called by <module>
        arguments: x=2
        Hello.
        That's all for now.
    f ==> returning to <module>

If the `log_calls` output destination for ``f`` were ``sys.stderr``, a file, or a logger,
then ``f.log_message()`` would write to that same destination, in any case respecting the
``indent`` setting of ``f``.

.. py:method:: wrapper.log_message(msg, *msgs, sep=' ', extra_indent_level=1, prefix_with_name=False)
    :noindex:

    (To be called by a decorated callable, on its own wrapper.)
    Join one one or more "messages" (anything you want to see as a string) with ``sep``,
    and write the result to the `log_calls` output destination of the caller.

    :param msg: the first or only message
    :param msgs: optional additional messages
    :param extra_indent_level: a number of 4-column-wide *indent levels* specifying
        where to begin writing that message. This value x 4 is an offset in columns
        from the left margin of the visual frame established by `log_calls` – that is,
        an offset from the column in which the callable's entry and exit messages begin.
        The default of 1 aligns the message with the "arguments: " line of `log_calls`'s output.
    :type extra_indent_level: ``int``
    :param prefix_with_name:  If true, the final message is prefaced with the
        name of the callable, plus possibly its call number in square brackets
        (if the `log_call_numbers` setting is true).
    :type prefix_with_name:  ``bool``

    **Note**: If the `mute` setting of the caller is ``log_calls.MUTE.CALLS``,
    ``log_message()`` forces ``prefix_with_name`` to ``True``, and ``extra_indent_level`` to ``0``.
    A little reflection should reveal that these are sensible adjustments.

.. _log_exprs-method:

The expression-evaluating method ``log_exprs()``
===============================================================

``log_exprs()`` is a convenience method built upon ``log_message()``
which makes it easy to print variables and expressions together their values.

.. py:method:: wrapper.log_exprs(*exprs, sep=', ', extra_indent_level=1, prefix_with_name=False, prefix='')
        :noindex:

        Evaluate each expression in ``exprs`` in the context of the caller, a decorated callable;
        make a string `expr` ``=`` `val` from each, and pass those strings
        to ``log_message()`` as messages to write, separated by ``sep``.

        :param exprs: expressions to evaluate and log with their values
        :type exprs: sequence of ``str``
        :param sep: separator for `expr` ``=`` `val` substrings
        :param extra_indent_level: as for log_message
        :param prefix_with_name: as for log_message
        :param prefix: additional text to prepend to output message.

Here's a small but realistic example:

    >>> @log_calls()
    ... def gcd(a, b):
    ...     while b:
    ...         a, b = b, (a % b)
    ...         gcd.log_exprs('a', 'b', prefix="At bottom of loop: ")
    ...     return a
    >>> gcd(48, 246)
    gcd <== called by <module>
        arguments: a=48, b=246
        At bottom of loop: a = 246, b = 48
        At bottom of loop: a = 48, b = 6
        At bottom of loop: a = 6, b = 0
    gcd ==> returning to <module>
    6

--------------------------------------------------------------------

Accessing Method Wrappers: |br| the ``get_log_calls_wrapper()`` and ``get_own_log_calls_wrapper()`` Classmethods
############################################################################################################################

`log_calls` decorates a callable by "wrapping" it in a function (the *wrapper*) which has
various attributes — not only data containing settings, but also methods. Access to these attributes
requires access to the callable's wrapper. In particular, a decorated callable
must access its *own* wrapper in order to use the :ref:`log_message <log_message-method>` and
:ref:`log_exprs <log_exprs-method>` methods.

It's straightforward to access the wrapper of a decorated global function ``f``: after decoration,
``f`` refers to the wrapper. For methods and properties, however, the various kinds of methods
and the two ways of defining properties require different navigation paths to the wrapper.
`log_calls` hides this complexity, providing uniform access to the wrappers of methods and properties.

.. py:classmethod:: decorated_class.get_log_calls_wrapper(fname: str)
    :noindex:

    Classmethod of a decorated class.
    Call this on a decorated class or an instance thereof to access the wrapper
    of the callable named ``fname``, in order to access the
    `log_calls`-added attributes for ``fname``.

    :param fname: name of a method (instance method, staticmethod or classmethod),
        or the name of a property (treated as denoting the getter),
        or the name of a property concatenated with '`.getter`', '`.setter`' or '`.deleter`'.

    :raises: ``TypeError`` if ``fname`` is not a ``str``; ValueError if ``fname``
            isn't as described above or isn't in the ``__dict__`` of *decorated_class*.

    :return: wrapper of ``fname`` if ``fname`` is decorated, ``None`` otherwise.


.. py:classmethod:: decorated_class.get_own_log_calls_wrapper()
    :noindex:

    Classmethod of a decorated class. Call from *within* a method or property
    of a decorated class. Typically called on ``self`` from within instance methods,
    and called on the enclosing, decorated class ``decorated_class`` from within
    classmethods and staticmethods.

    :raises: ``ValueError`` if caller is not decorated.

    :return: the wrapper of the caller (a function), so that the caller
             can access its own `log_calls` attributes.


--------------------------------------------------------------------

.. _set_reset_defaults:

Retrieving and Changing the Defaults
#############################################################

`log_calls` classmethods ``set_defaults()``, ``reset_defaults()``
======================================================================

The ``settings`` parameter lets you specify an entire collection of
:ref:`settings <what-is-a-setting>` at once. If you find that you're passing the same settings
dict or settings file to most `log_calls` decorators in a program, `log_calls` offers a further economy.
At program startup, you can use the ``log_calls.set_defaults`` classmethod to change the `log_calls`
defaults to the settings you want, and eliminate most of the ``settings`` arguments.

.. py:classmethod:: log_calls.set_defaults(new_default_settings=None, **more_defaults)
   :noindex:

   Change the `log_calls` default values for settings, different from the "factory defaults".

   :param new_default_settings:  a settings dict or settings file: any valid value
    for the ``settings`` parameter.
   :type new_default_settings:   ``dict`` (a settings dict) or ``str`` (pathname for a settings file)
   :param more_defaults: keyword parameters where every key is a :ref:`setting <what-is-a-setting>`.
    These override settings in ``new_defaults``.

   **The new defaults are not retroactive!** (Settings of already-decorated callables remain unchanged.)
   They apply to every decoration that occurs subsequently.

You can easily undo all changes effected by ``set_defaults``:

.. py:classmethod:: log_calls.reset_defaults()
   :noindex:

   Restore the "factory default" defaults.

`log_calls` classmethods ``get_defaults_OD()``, ``get_factory_defaults_OD()``
===================================================================================

For convenience, `log_calls` also provides classmethods for retrieving the current defaults
and the "factory defaults", each as an ``OrderedDict``:

.. py:classmethod:: log_calls.get_defaults_OD()
    :noindex:

    Return an `OrderedDict` of the current `log_calls` defaults.

.. py:classmethod:: log_calls.get_factory_defaults_OD()
    :noindex:

    Return an `OrderedDict` of the `log_calls` "factory defaults".


The returned dictionaries can be compared with those obtained from a callable's
``log_calls_settings.as_OD()`` or ``log_calls_settings.as_dict()`` method to
determine whether, and if so how, the callable's settings differ from the defaults.

If ``log_calls.set_default()`` has not been called, then the current defaults *are*
the factory defaults.

--------------------------------------------------------------------

.. _decorate-functions:

Bulk and External (Re)Decoration
####################################################################
..  (Re)Decorating Classes, Class Hierarchies, Functions, and Modules

This section discusses the ``log_calls.decorate_*`` classmethods. These methods allow you to:

* decorate or redecorate functions and classes,
* decorate an entire class hierarchy (a class and all its subclasses), and even
* decorate all classes and/or functions in a module.

The ``decorate_*`` methods are handy in situations where altering source code is impractical (too many things
to decorate) or questionable practice (third-party modules and packages).
These methods can help you learn a new codebase, by shedding light on its internal operations.

They provide another way to dynamically change the settings of already-decorated functions and classes.

Like any decorator, `log_calls` is a :ref:`functional <functional-def>` —
a function that takes a function argument and returns a function. The
following typical use::

    @log_calls()
    def f(): pass

is equivalent to::

    f = log_calls()(f)

If ``f`` occurs in your own code, then no doubt you'll prefer the former. The ``log_calls.decorate_*``
methods let you decorate ``f`` when its definition does *not* necessarily appear in your code.

The ``log_calls.decorate_*`` classmethods are:

    * ``decorate_class(baseclass, decorate_subclasses=False, **setting_kwds)``
      decorates a class and, optionally, all of its subclasses

    * ``decorate_hierarchy(baseclass, **setting_kwds)``
      decorates a class and all of its subclasses

    * ``decorate_function(f, **setting_kwds)``
      decorates a function defined or imported into the module from which you call this method

    * ``decorate_package_function(f, **setting_kwds)``
      decorates a function in an imported package

    * ``decorate_module_function(f, **setting_kwds)``
      decorates a function in an imported package or module

    * ``decorate_module(mod: 'module', functions=True, classes=True,, **setting_kwds)``
      decorates all functions and classes in a module

.. note::
   You can't decorate Python builtins. Attempting to do is harmless (anyway, it's supposed to be!),
   and `log_calls` will return the builtin class or callable unchanged. For example,
   the following have no effect::

    log_calls.decorate_class(dict)
    log_calls.decorate_class(dict, only='update')
    log_calls.decorate_function(dict.update)


--------------------------------------------------------------------

.. _indirect-values:

Indirect Values
####################################################################

`log_calls` offers a third way to make the settings of a decorated callable dynamic:
*indirect values*.

Using this capability is more intrusive than the approaches already discussed:
it introduces more "debug-only" code which you'll have to ensure doesn't run
in production. As such, it's less appealing. However, it has its place, in
demos and producing documentation.

`log_calls` lets you specify any "setting" parameter except `prefix` or `max_history`
with one level of indirection, by using *indirect values*:


    indirect value of a setting parameter
        A string that names a keyword parameter of a decorated callable.
        When the callable is called, the value of that keyword argument
        is used for the setting.

To specify an indirect value for a parameter whose normal values are (or can be) ``str``s
(this applies only to ``args_sep`` and ``logger``, at present), append an ``'='`` to the
value. For consistency, any indirect value can end in a trailing ``'='``, which is stripped.
Thus, ``enabled='enable_='`` indicates an indirect value *to be supplied* with the keyword
``enable_``.

Explicit indirect values
============================

An indirect value can be an explicit keyword argument present in the signature of the callable:

    >>> @log_calls(enabled='enable_')
    ... def f(x, y, enable_=False): pass

Thus, calling ``f`` above without passing a value for ``enable_`` uses the default value
``False`` of ``enable_``, and the call gives no output::

    >>> f(1, 2)

Supplying a value ``True`` for ``enable_`` does give `log_calls` output:

    >>> f(3, 4, enable_=True)    # output:
    f <== called by <module>
        arguments: x=3, y=4, enable_=True
    f ==> returning to <module>

Implicit indirect values
============================

An indirect value doesn't have to be present in the signature of a decorated callable.
It can be an implicit keyword argument that ends up in ``**kwargs``:

    >>> @log_calls(args_sep_=', ')      # same as log_calls default
    ... def g(x, y, **kwargs): pass

When the decorated callable is called, the arguments passed by keyword, and the decorated
callable's explicit keyword parameters with default values, are both searched for the
named parameter; if it is found and of the correct type, *its* value is used;
otherwise a default value is used.

Here, the value of the ``args_sep`` setting will be the default value given for ``args_sep_``:

    >>> g(1, 2)
    g <== called by <module>
        arguments: x=1, y=2
    g ==> returning to <module>

whereas here, the ``args_sep`` value used will be ``' $ '``:

    >>> g(3, 4, args_sep_=' $ ')
    g <== called by <module>
        arguments: x=3 $ y=4 $ **kwargs={'args_sep_': ' $ '}
    g ==> returning to <module>

Indirect values are valid values of settings
====================================================

In a settings file, the value of a keyword is treated as an indirect value
if it's enclosed in (single or double) quotes and its last non-quote character
is `'='`. For example::

    ``file='file_='``

Indirect values can be used in settings dicts as well, and there, only indirect
values of ``args_sep`` and ``logger`` require a trailing ``=``.

It's also perfectly legitimate to assign an indirect value to a setting
via ``log_calls_settings``.


--------------------------------------------------------------------

.. _final-example:

Example — A Decorated Class
################################################

In this final section we'll exercise many of the features described above,
taking the opportunity to illustrate their use in a class.

    >>> @log_calls(omit='no_deco ?[1-3] prop.deleter', mute=log_calls.MUTE.CALLS)
    ... class A():
    ...     def __init__(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     @log_calls(mute=log_calls.MUTE.NOTHING)
    ...     def __repr__(self):
    ...         return 'instance of A'
    ...
    ...     @log_calls(log_args=False, mute=log_calls.MUTE.NOTHING)
    ...     def method(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...
    ...     def f1(self): pass
    ...     def g2(self): pass
    ...     def h3(self): pass
    ...     def no_deco(self):
    ...         wrapper = self.get_own_log_calls_wrapper()      # raises ValueError
    ...         wrapper.log_message('Hi')
    ...
    ...     @classmethod
    ...     def clsmethod(cls):
    ...         wrapper = cls.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...
    ...     @property
    ...     def prop(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     @prop.setter
    ...     @log_calls(name='B.%s.setter')
    ...     def prop(self, val):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     @prop.deleter
    ...     def prop(self, val):
    ...         pass
    ...
    ...     def setx(self, val):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi from setx alias x.setter')
    ...     def delx(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi from delx alias x.deleter')
    ...     propx = property(None, setx, delx)
    ...
    ...     @log_calls(record_history=True)
    ...     def busy(self, n):
    ...         for i in range(n):  pass

To reduce clutter in this example, we mute `log_calls` call output for all but two methods.
For all decorated methods other than ``method``, ``log_message`` automatically prefixes
its output with the name of the caller, and doesn't indent by an extra 4 spaces.

Construct an ``A`` instance to call methods and properties on:

    >>> a = A()
    A.__init__: Hi

We explicitly decorated ``method`` so that its `log_calls` output would *not* be muted:

    >>> a.method()  # log_calls call output
    A.method <== called by <module>
        Hi
    A.method ==> returning to <module>

The ``__repr__`` method is not `log_calls`-decorated, despite the explicit decorator:
`log_calls` doesn't itself decorate ``__repr__`` methods.

    >>> print(a)    # no log_calls call output
    instance of A

Because of the ``omit`` parameter, the methods ``no_deco``, ``f1``, ``g2``, ``h3``
and ``prop.deleter`` are not decorated:

    >>> a.get_log_calls_wrapper('no_deco') is None
    True
    >>> a.get_log_calls_wrapper('f1') is None
    True
    >>> a.get_log_calls_wrapper('g2') is None
    True
    >>> a.get_log_calls_wrapper('h3') is None
    True
    >>> a.get_log_calls_wrapper('prop.deleter') is None
    True

Because ``no_deco`` is not decorated, ``self.get_own_log_calls_wrapper()``
in the body of that method raises ``ValueError``, as ``self`` has no such attribute:

    >>> a.no_deco()     # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: ...

``get_own_log_calls_wrapper()`` works within classmethods and staticmethods as well,
though of course it must be called on the class (using ``A.`` in staticmethods).

    >>> a.clsmethod()
    A.clsmethod: Hi

We explicitly decorated the *setter* of the ``prop`` property to disambiguate
its display name. Had we not done so, its display name would also be ``A.prop``,
and the output of ``a.prop = 17`` would be the same as that of the *getter*.

    >>> a.prop
    A.prop: Hi
    >>> a.prop = 17
    A.prop.setter: Hi

For properties defined with the ``property`` function, the display names of its
constituents are their method names:

    >>> a.propx = 13
    A.setx: Hi from setx alias x.setter
    >>> del a.propx
    A.delx: Hi from delx alias x.deleter

Finally, let's accumulate a call history for `a.busy`, then retrieve and display it:

    >>> a.busy(5); a.busy(50); a.busy(500)
    >>> busy_history_csv = a.get_log_calls_wrapper('busy').stats.history_as_csv
    >>> print(busy_history_csv)     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    call_num|self|n|retval|elapsed_secs|process_secs|timestamp|prefixed_fname|caller_chain
    1|instance of A|5|None|...|...|...|'A.busy'|['<module>']
    2|instance of A|50|None|...|...|...|'A.busy'|['<module>']
    3|instance of A|500|None|...|...|...|'A.busy'|['<module>']
