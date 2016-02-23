.. _quickstart:

Quick Start
###########

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

See the :ref:`call_chains`  chapter for more examples and finer points.


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
will and won't be decorated. The section on :ref:`the omit and only keyword parameters <omit_only_params>`
contains the details.

Decorating *most* methods, overriding the settings of one method
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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

These examples have shown just a few of the features that make `log_calls` powerful,
versatile, yet easy to use. They have also introduced a couple of `log_calls`'s keyword
parameters, the source of much of that versatility. The :ref:`keyword_parameters` chapter
documents them in detail. The chapter :ref:`decorating_classes` covers that subject
thoroughly, presenting many techniques and explaining fine points.
