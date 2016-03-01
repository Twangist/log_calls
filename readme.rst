.. log_calls Readme documentation master file, created by
   sphinx-quickstart on Tue Feb  9 05:14:29 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
    :hidden:
    :maxdepth: 1
    :titlesonly:


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

This document introduces `log_calls` and shows you a few ways to use it. To learn more,
see `the complete documentation  <http://www.pythonhosted.org/log_calls/index.html>`_
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

--------------------------------------------------------------------
.. _quickstart:

Quick Start
############

.. _Basic-usage:

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

See the `Call Chains<http://www.pythonhosted.org/log_calls/call_chains.html>`_
chapter of the documentation for more examples and finer points.


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
==================================================

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
will and won't be decorated. The documentation section on
 `the omit and only keyword parameters <http://www.pythonhosted.org/log_calls/omit_only_params.html>`_
contains the details.

Decorating *most* methods, overriding the settings of one method
----------------------------------------------------------------------

Suppose you have a class ``D`` that's just like ``C`` above, but adds a ``double()`` method.
(For the sake of example, never mind that in practice you might subclass ``C``.)
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

Decorating "external" code
==================================================

Sometimes it's enlightening and instructive to decorate objects in a package or module
that you import. It might be in a new codebase you're getting to know, your own nontrivial
code from a while ago which you now wish you had documented more, or even a function, class
or module in Python's standard library.

We'll illustrate techniques with a simple example: decorating the fractions class
``fractions.Fraction``, to see how it uses its own API. Along the way we'll ilustrate
how to use `log_calls` settings to filter the output.

First, let's import the class, decorate it and create an instance:

    >>> import fractions
    >>> Fr = fractions.Fraction
    >>> log_calls.decorate_class(Fr)
    >>> print(Fr(3,4))
    Fraction.__new__ <== called by <module>
        arguments: cls=<class 'fractions.Fraction'>, numerator=3, denominator=4
        defaults:  _normalize=True
    Fraction.__new__ ==> returning to <module>
    Fraction.__str__ <== called by <module>
        arguments: self=Fraction(3, 4)
    Fraction.__str__ ==> returning to <module>
    3/4

Now create a couple of fractions, using the `log_calls` global mute to do it in silence:

    >>> log_calls.mute = True
    >>> fr56 = fractions.Fraction(5,6)
    >>> fr78 = fractions.Fraction(7,8)
    >>> log_calls.mute = False

Before using these, let's redecorate to improve `log_calls` output.
After trying other examples at the command line it becomes apparent that
``__str__`` gets called a lot, and the calls become just noise, so let's
``omit`` that. To eliminate more clutter, let's suppress the exit lines
("... returning to..."). We'll also display return values. Here's how to
accomplish all of that, with one call to ``decorate_class``:

    >>> log_calls.decorate_class(Fr,
    ...                          omit='__str__', log_exit=False, log_retval=True)

Finally, let's do some arithmetic on fractions:

    >>> print(fr78-fr56)
    Fraction._operator_fallbacks.<locals>.forward <== called by <module>
        arguments: a=Fraction(7, 8), b=Fraction(5, 6)
        Fraction.denominator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward
            arguments: a=Fraction(7, 8)
            Fraction.denominator return value: 8
        Fraction.denominator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward
            arguments: a=Fraction(5, 6)
            Fraction.denominator return value: 6
        Fraction.numerator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward
            arguments: a=Fraction(7, 8)
            Fraction.numerator return value: 7
        Fraction.numerator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward
            arguments: a=Fraction(5, 6)
            Fraction.numerator return value: 5
        Fraction.__new__ <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward
            arguments: cls=<class 'fractions.Fraction'>, numerator=2, denominator=48
            defaults:  _normalize=True
            Fraction.__new__ return value: 1/24
        Fraction._operator_fallbacks.<locals>.forward return value: 1/24
    1/24

So ultimately, subtraction of fractions is performed by ``Fraction._operator_fallbacks.<locals>.forward``,
(an instance of) the ``forward`` inner function of the method ``Fraction._operator_fallbacks``. This
instance of ``forward`` presumably implements the operator ``-``'.

The implementation of ``-`` uses the public properties ``denominator`` and ``numerator``
to retrieve the fields of the fractions, and returns a new fraction with the computed numerator and denominator.
Like all fractions, the one returned by ``new`` displays itself in lowest terms.


Where to go from here
==================================================

These examples have shown just a few of the features that make `log_calls` powerful,
versatile, yet easy to use. They have introduced a few of `log_calls`'s keyword
parameters, the source of much of its versatility, as well as one of the ``decorate_*``
methods.

In fhe documentation, read at least the introduction of the chapter,
 `What log_calls Can Decorate <http://www.pythonhosted.org/log_calls/what_log_calls_can_decorate.html>`_,
then read the essential chapter following it,
 `Keyword Parameters <http://www.pythonhosted.org/log_calls/parameters.html>`_,
which documents the parameters in detail. The parameters chapter is a prerequisite
for those that follow it, most of which can be read immediately afterward.

The chapter
 `Decorating Classes <http://www.pythonhosted.org/log_calls/decorating_classes.html>`_,
covers that subject thoroughly, presenting techniques and fine points. In particular the
parameters ``only`` and ``omit`` are documented there.

The ``decorate_*`` methods are presented in
 `Bulk (Re)Decoration, (Re)Decorating Imports <http://www.pythonhosted.org/log_calls/decorating_functions_class_hierarchies.html>`_,

`log_calls` provides even more functionality which these examples haven't even
hinted at. The remaining chapters document all of it.
