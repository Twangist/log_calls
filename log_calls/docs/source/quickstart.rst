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
see only ``f <== called by g1``, and then ``f ==> returning to g1`` followed by
``h ==> returning to <module>``, which wouldn't tell us the whole story about how
control reached ``g1`` from ``h``.

See the :ref:`call_chains`  chapter for more examples and finer points.

.. _quickstart-lc-aware-debug-messages:

Writing `log_calls`-aware debugging messages
-------------------------------------------------------

.. todo::
    Write this.
    * Use probably old stuff about "print"ed messages "literally sticking out".
    * Also show that you can comment out the deco and, by default, the debug-msg-writing
      calls just shut up and don't give errors.
    * link/ref to chapter on log_* methods


(As we saw above..., ) if you use ``print`` to write debugging messages, those messages
literally “stick out”, and it becomes difficult, especially in more complex situations
with multiple functions and methods, to figure out who actually wrote which message — hence the ``---``
and ``***` prefixes used above. `log_calls` provides alternatives to ``print`` that overcome
this and other problems.

<ONE EXAMPLE with say 2 functions, one using
    log_message() .........
 the other using
    log_exprs() .........
>

comment out decos

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
will and won't be decorated. The section on :ref:`the omit and only keyword parameters <omit_only_params>`
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

For more information
----------------------

The :ref:`decorating_classes` chapter covers that subject thoroughly — basics, details,
subtleties and techniques. In particular, the parameters ``only`` and ``omit``
are documented there, in the
section `the omit and only keyword parameters  <http://www.pythonhosted.org/log_calls/decorating_classes.html#the-omit-and-only-keyword-parameters-default-tuple>`_.

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

(**Note**: *In Python 3.4.y, the output lacks the third line: ``__new__`` had no ``normalize`` parameter.*)

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

    >>> print(fr78 - fr56)      # doctest: +SKIP
    Fraction._operator_fallbacks.<locals>.forward (__sub__) <== called by <module>
        arguments: a=Fraction(7, 8), b=Fraction(5, 6)
        Fraction.denominator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
            arguments: a=Fraction(7, 8)
            Fraction.denominator return value: 8
        Fraction.denominator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
            arguments: a=Fraction(5, 6)
            Fraction.denominator return value: 6
        Fraction.numerator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
            arguments: a=Fraction(7, 8)
            Fraction.numerator return value: 7
        Fraction.numerator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
            arguments: a=Fraction(5, 6)
            Fraction.numerator return value: 5
        Fraction.__new__ <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
            arguments: cls=<class 'fractions.Fraction'>, numerator=2, denominator=48
            defaults:  _normalize=True
            Fraction.__new__ return value: 1/24
        Fraction._operator_fallbacks.<locals>.forward (__sub__) return value: 1/24
    1/24

(**Note**: *This is Python 3.5.x output. In Python 3.4.y, the output shows evidence
of less efficiency, and it lacks the third to last line.*)

The topmost call is to an inner function ``forward`` of the method ``Fraction._operator_fallbacks``,
presumably a closure. The ``__name__`` of the callable is actually ``__sub__``, and we know that
the infix subtraction operator ``-`` is implemented by a "dunder" method ``Fraction.__sub__``,
so it looks like the closure `is` the value of that name.

An undecorated function or method ``_sub`` is called by the closure. Because
``_sub`` isn't decorated we don't know what its arguments are, and the call chains for
the decorated ``numerator``, ``denominator`` and ``__new__`` chase back to ``__sub__``.

Why isn't ``_sub`` decorated? Check that — let's guess that it takes two Fraction arguments:

    >>> print(Fr._sub(fr78, fr56))
    Fraction._sub <== called by <module>
        arguments: a=Fraction(7, 8), b=Fraction(5, 6)
        Fraction.denominator <== called by Fraction._sub
            arguments: a=Fraction(7, 8)
            Fraction.denominator return value: 8
        Fraction.denominator <== called by Fraction._sub
            arguments: a=Fraction(5, 6)
            Fraction.denominator return value: 6
        Fraction.numerator <== called by Fraction._sub
            arguments: a=Fraction(7, 8)
            Fraction.numerator return value: 7
        Fraction.numerator <== called by Fraction._sub
            arguments: a=Fraction(5, 6)
            Fraction.numerator return value: 5
        Fraction.__new__ <== called by Fraction._sub
            arguments: cls=<class 'fractions.Fraction'>, numerator=2, denominator=48
            defaults:  _normalize=True
            Fraction.__new__ return value: 1/24
        Fraction._sub return value: 1/24
    1/24

Aha: it *is* decorated after all, and the `log_calls` output looks familiar.
So, perhaps the closure ``forward``, implementing ``__sub__``, has a nonlocal
variable which was bound to the real ``_sub`` at class initialization, before
the methods of the class were decorated; the closure calls the inner, decorated
``_sub``, not the `log_calls` wrapper around it.

Ultimately, then, subtraction of Fractions is performed by a function ``_sub``,
to which ``__sub__`` i.e. ``Fraction._operator_fallbacks.<locals>.forward`` dispatches.
The latter is an inner function of the method ``Fraction._operator_fallbacks``.
The ``_sub`` function uses the public properties ``denominator`` and ``numerator``
to retrieve the fields of the Fractions, and returns a new Fraction, with a
numerator of 2 (= 7 * 6 - 8 * 5) and denominator of 48 (= 6 * 8). ``__new__`` reduces the returned
Fraction to lowest terms (because its parameter ``_normalize`` is true, its default value).

For more information
----------------------------

The ``decorate_*`` methods are presented in the
chapter `Bulk (Re)Decoration, (Re)Decorating Imports <http://www.pythonhosted.org/log_calls/decorating_functions_class_hierarchies.html>`_.


Where to go from here
==================================================

These examples have shown just a few of the features that make `log_calls` powerful,
versatile, yet easy to use. They introduced a few of `log_calls`'s keyword
parameters, the source of much of its versatility, as well as one of the ``decorate_*``
methods.

The next chapter, :ref:`what-log_calls-can-decorate`, gives general culture but also introduces
terminology and concepts subsequently used throughout.
An essential chapter follows that: :ref:`keyword_parameters` documents the parameters in detail.
That chapter is a reference, to which you can refer back
as needed; it's not necessary to assimilate its details before proceeding on to further topics.
For an even more concise reference, in cheatsheet format,
see `Appendix I: Keyword Parameters Reference <http://www.pythonhosted.org/log_calls/appendix_I_parameters_table.html>`_.

The chapters following the keyword parameters chapter all presume familiarlty
with its basic information, and almost all of them can be read immediately after it.

`log_calls` provides yet more functionality which these examples haven't even
hinted at. The remaining chapters document all of it.
