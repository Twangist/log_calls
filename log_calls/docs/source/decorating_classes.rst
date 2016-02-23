.. _decorating_classes:

Decorating Classes
####################################################

In the :ref:`quickstart-methods` and :ref:`quickstart-classes` sections of the
:ref:`quickstart` chapter we already introduced the use of `log_calls` to decorate
methods and properties of classes. As shown in the latter section,
if you want to decorate every callable of a class, you don't have to decorate each one
individually: you can simply decorate the class. As that section also shows, this convenience
isn't an all or nothing affair: you can use the ``omit`` and ``only`` keyword
parameters to a `log_calls` class decorator for more fine-grained control over which
callables get decorated. The first sections of this chapter detail the use of those parameters.
The remaining sections discuss other topics pertinent to class decoration.

.. _omit_only_params:

The ``omit`` and ``only`` keyword parameters (default: ``tuple()``)
=======================================================================

These parameters let you concisely specify which methods and properties of a decorated class
get decorated. `log_calls` ignores ``omit`` and ``only`` when decorating a function. When not ``None``,
the value of each of these parameters specifies one or more methods or properties of a decorated class.
If you provide just ``omit``, all callables of the class will be decorated except for those
specified by ``omit``. If you provide just ``only``, only the callables it specifies will be
decorated. If you provide both, the callables decorated will be those specified by ``only``,
excepting any specified by ``omit``.

`log_calls` allows considerable flexibility in the format of values provided for the ``omit`` and ``only``
parameters. First, we give the general definition of what those values can be, and then several examples
illustrating their use.

.. _callable-designators:

Values of the ``omit`` and ``only`` parameters
------------------------------------------------


.. index:: callable designator

For this section only, it's convenient to define the following term:

    callable designator
        (That's *designator of callables*, not a "designator that can be called", whatever that might be.)

        A string which is one of the following:

        * the name of a method
        * the name of a property, possibly followed by one of the qualifiers
          ``.setter``, ``.getter``, ``.deleter``
        * a `glob` (Unix-style shell pattern) — a string possibly containing

            * wildcard characters ``*``, ``?``
            * character sets ``[`` `s`\ :subscript:`1` `s`\ :subscript:`2` ... `s`\ :subscript:`n` ``]``
              where each `s`\ :subscript:`k` can be either a character or a character range
              `s`\ :subscript:`k,1` ``-`` `s`\ :subscript:`k,2` (e.g. ``[acr-tx]``, which denotes ``acrstx``)
            * complements of character sets ``[!`` `s`\ :subscript:`1` `s`\ :subscript:`2` ... `s`\ :subscript:`n` ``]``
              — all characters *except* those denoted by ``[`` `s`\ :subscript:`1` `s`\ :subscript:`2` ... `s`\ :subscript:`n` ``]``

          Matching of globs against method and property names is case-sensitive.

A value of the ``omit`` or ``only`` parameter can be:

  * A single callable designator,
  * a string consisting of multiple callable designators separated by spaces or by commas and spaces, or
  * a sequence (list, tuple, or other iterable) of callable designators.


.. _callable-designators-examples:

Examples of callable designators
++++++++++++++++++++++++++++++++++++

    Given the following class ``X``:

    >>> class X():
    ...     def fn(self): pass
    ...     def gn(self): pass
    ...     def hn(self): pass
    ...     @property
    ...     def pr(self): pass
    ...     @pr.setter
    ...     def pr(self, val): pass
    ...     @pr.deleter
    ...     def pr(self): pass
    ...
    ...     def pdg(self): pass
    ...     def pds(self, val): pass
    ...     pd = property(pdg, pds, None)
    ...     class I():
    ...         def i1(self): pass
    ...         def i2(self): pass

    the following table shows several callable designators for ``X`` and what they designate.
    To reduce clutter, we've omitted initial ``X.`` from the literals in the righthand column:

        +---------------------------------+---------------------------------------------------+
        || Callable designator            || designates these methods and/or properties       |
        +=================================+===================================================+
        || ``fn``                         || ``fn``                                           |
        +---------------------------------+---------------------------------------------------+
        || ``pr.getter``                  || ``pr`` getter                                    |
        +---------------------------------+---------------------------------------------------+
        || ``pr.setter``                  || ``pr`` setter                                    |
        +---------------------------------+---------------------------------------------------+
        || ``pr.deleter``                 || ``pr`` deleter                                   |
        +---------------------------------+---------------------------------------------------+
        || ``pr``                         || {``pr`` getter, ``pr`` setter, ``pr`` deleter}   |
        +---------------------------------+---------------------------------------------------+
        || ``pr.?etter``                  || {``pr`` getter, ``pr`` setter}                   |
        +---------------------------------+---------------------------------------------------+
        || ``p*``                         || {``pr`` getter, ``pr`` setter, ``pr`` deleter,   |
        ||                                ||  ``pds``, ``pdg``}                               |
        +---------------------------------+---------------------------------------------------+
        || ``?n``                         || {``fn``, ``gn``, ``hn``}                         |
        +---------------------------------+---------------------------------------------------+
        || ``[fg]n``                      || {``fn``, ``gn``}                                 |
        +---------------------------------+---------------------------------------------------+
        || ``[f-h]n``                     || {``fn``, ``gn``, ``hn``}                         |
        +---------------------------------+---------------------------------------------------+
        || ``pd``                         || {``pdg``, ``pds``}                               |
        +---------------------------------+---------------------------------------------------+
        || ``pdg``, ``pd.getter``         || ``pdg``                                          |
        +---------------------------------+---------------------------------------------------+
        || ``pds``, ``pd.setter``         || ``pds``                                          |
        +---------------------------------+---------------------------------------------------+
        || ``pd.deleter``                 || nothing (``pd`` has no deleter)                  |
        +---------------------------------+---------------------------------------------------+
        || ``no_such_*``                  || nothing (there are no matches)                   |
        +---------------------------------+---------------------------------------------------+
        || ``[f-i]*``                     || {``fn``, ``gn``, ``hn``, ``I.i1``, ``I.i2``}     |
        +---------------------------------+---------------------------------------------------+
        || ``X.I.*``, ``X.[!f-hp]*``      || {``I.i1``, ``I.i2``}                             |
        +---------------------------------+---------------------------------------------------+
        || ``X.[!f-ip]*``                 || {``I.i1``, ``I.i2``},                            |
        ||                                ||  because ``[!f-ip]`` matches ``I``               |
        +---------------------------------+---------------------------------------------------+
        || ``[!f-hp]*``, ``?[!n]*``       || *every callable* in classes ``X`` and ``X.I``,   |
        ||                                || because these match ``X.`` + *anything*          |
        +---------------------------------+---------------------------------------------------+
        || ``*``                          || every callable in classes ``X`` and ``X.I``      |
        +---------------------------------+---------------------------------------------------+

    .. warning::
        Be aware that:

        1. wildcards can match the dot ``'.'`` in qualified names;
        2. both qualified and unqualified method and property names are matched —
           e.g. for a method ``mymethod`` in a class ``C``, each callable designator
           is checked for a match against both ``mymethod`` and ``C.mymethod``.

        As the second and third to last examples in the above table illustrate,
        these can lead to surprises, especially when using complements of character sets.

----------------------------------------------------------------------------------------------------------------

.. _omit-only-examples:

``omit`` and ``only`` — Examples
==================================

A useful settings dict for the examples of this chapter::

    >>> MINIMAL = dict(
    ...     log_args=False,
    ...     log_exit=False
    ... )


.. _omit-only-basic-examples:

Basic examples
-------------------

First, simple examples for methods, without wildcards, illustrating possible values
for ``omit`` and ``only`` and the interaction of those parameters.

In class ``A``, only ``f`` is decorated::

    >>> @log_calls(only='f', settings=MINIMAL)
    ... class A():
    ...     def f(self): pass
    ...     def g(self): pass
    >>> a = A(); a.f(); a.g()
    A.f <== called by <module>

In class ``B``, ``f`` and ``g`` are omitted, so only ``h`` is decorated (and so, gives output)::

    >>> @log_calls(omit='f g', settings=MINIMAL)
    ... class B():
    ...     def f(self): pass
    ...     def g(self): pass
    ...     def h(self): pass
    >>> b = B(); b.f(); b.g(); b.h()
    B.h <== called by <module>

In class ``C``, only ``f`` and ``h`` are decorated::

    >>> @log_calls(only='f, h', settings=MINIMAL)
    ... class C():
    ...     def f(self): pass
    ...     def g(self): pass
    ...     def h(self): pass
    >>> c = C(); c.f(); c.g(); c.h()
    C.f <== called by <module>
    C.h <== called by <module>

In class ``D``, only ``f`` is decorated::

    >>> @log_calls(only=['f', 'g'], omit=('g',), settings=MINIMAL)
    ... class D():
    ...     def f(self): pass
    ...     def g(self): pass
    ...     def h(self): pass
    >>> d = D(); d.f(); d.g(); d.h()
    D.f <== called by <module>


.. _precedence-of-decorators:

Precedence of inner decorators over outer decorators
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

By default, the *explicitly given* settings of a callable's decorator
take precedence over those of the decorator of its class:

    >>> @log_calls(settings=MINIMAL)
    ... class E():
    ...     def f(self): pass
    ...     @log_calls(log_exit=True)
    ...     def g(self): pass
    >>> E().f(); E().g()
    E.f <== called by <module>
    E.g <== called by <module>
    E.g ==> returning to <module>

The same holds for inner classes: settings provided explicitly to the decorator
of an inner class take precedence over the corresponding settings of the outer class.
To give the outer settings priority, supply ``override=True`` to the outer decorator:

    >>> @log_calls(settings=MINIMAL, override=True)
    ... class E():
    ...     def f(self): pass
    ...     @log_calls(log_exit=True)
    ...     def g(self): pass
    >>> E().f(); E().g()
    E.f <== called by <module>
    E.g <== called by <module>

.. _decorating_properties:

Decorating properties
-----------------------

There are two ways to specify properties: using ``property`` as a decorator,
and using it as a function, as described in the Python documentation for
`property <https://docs.python.org/3/library/functions.html?highlight=property#property>`_.
`log_calls` handles both approaches. The name of the property alone, with no appended qualifier,
designates *all* of the property's existing callables — the `getter`, `setter`, and `deleter`.


.. _decorating_properties-decorator:

Decorating properties specified with the ``@property`` decorator
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Python lets you define properties using decorators. You decorate the *getter* property *prop*
with ``@property``, and then any corresponding *setter* and *deleter* methods
with ``@``\ *prop*\ ``.setter`` and ``@``\ *prop*\ ``.deleter`` respectively.

Using ``only`` to decorate just the *getter*:

    >>> @log_calls(only='prop.getter', settings=MINIMAL)
    ... class A():
    ...     @property
    ...     def prop(self): pass
    ...     @prop.setter
    ...     def prop(self, val): pass
    >>> A().prop; A().prop = 17
    A.prop <== called by <module>

Using ``only`` with the property name — all property methods are decorated:

    >>> @log_calls(only='prop', settings=MINIMAL)
    ... class A():
    ...     @property
    ...     def prop(self): pass
    ...     @prop.setter
    ...     def prop(self, val): pass
    ...     @prop.deleter
    ...     def prop(self): pass
    >>> A().prop; A().prop = 17; del A().prop
    A.prop <== called by <module>
    A.prop <== called by <module>
    A.prop <== called by <module>


.. _using-name-with-setter-deleter:

.. topic:: Using the ``name`` parameter with *setter* and *deleter* property methods

    As the previous example shows, `log_calls` cannot presently give distinct
    display names to the different callables of a property defined by decorators.
    However, you can use the ``name`` parameter to overcome this limitation,
    as shown in the following example. (The `log_calls` decorators come after
    the property decorators.)

    >>> @log_calls(settings=MINIMAL)
    ... class A():
    ...     @property
    ...     def prop(self): pass
    ...     @prop.setter
    ...     @log_calls(name='A.%s.setter')
    ...     def prop(self, val): pass
    ...     @prop.deleter
    ...     @log_calls(name='A.%s.deleter')
    ...     def prop(self, val): pass
    >>> A().f(); A().prop; A().prop = 17; del A().prop
    A.prop <== called by <module>
    A.prop.getter <== called by <module>
    A.prop.deleter <== called by <module>


.. _decorating_properties-constructor:

Decorating properties specified with the ``property`` function
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Python also lets you define properties using ``property`` as a function.
`log_calls` uses the unique names of the methods that comprise the property.

    >>> @log_calls(omit='prop.setter', settings=MINIMAL)
    ... class XX():
    ...     def getxx(self):        pass
    ...     def setxx(self, val):   pass
    ...     def delxx(self):        pass
    ...     prop = property(getxx, setxx, delxx)
    >>> xx = XX(); xx.prop; xx.prop = 5; del xx.prop
    XX.getxx <== called by <module>
    XX.delxx <== called by <module>


----------------------------------------------------------------------------------------------------------------

.. _inner_classes:

Decorating inner classes
==============================

By default, the explicitly given settings of a decorator of (or within) an inner class
take precedence over those of the decorator of its outer class.

    >>> @log_calls(settings=MINIMAL)
    ... class O():
    ...     def f(self): pass
    ...     class I():
    ...         @log_calls(log_call_numbers=True)
    ...         def fi(self): pass
    ...         def gi(self): pass
    O().f(); O().I().fi(); O().I().gi()
    O.f <== called by <module>
    O.I.fi [1] <== called by <module>
    O.I.gi <== called by <module>

To give the outer settings priority, supply ``override=True`` to the outer decorator,
as illustrated above in :ref:`precedence-of-decorators`.

This default precedence of outer over inner is different for ``omit``,
in a way that attempts to meet expectations:

``only`` on inner and outer class decorators
----------------------------------------------------

When present and nonempty, inner ``only`` overrides outer ``only``.
In ``I1``, only ``g1`` is decorated, despite the outer class's ``only`` specifier:

    >>> @log_calls(only='*_handler', settings=MINIMAL)
    ... class O():
    ...     def f(self): pass
    ...     def my_handler(self): pass
    ...     def their_handler(self): pass
    ...     @log_calls(only='g1')
    ...     class I1():
    ...         def g1(self): pass
    ...         def some_handler(self): pass
    >>> oi1 = O.I1(); oi1.g1(); oi1.some_handler()
    O.I1.g1 <== called by <module>

``omit`` on inner and outer class decorators
----------------------------------------------------

``omit`` is cumulative: inner ``omit`` is added to outer ``omit``:

    >>> @log_calls(omit='*_handler', settings=MINIMAL)
    ... class O():
    ...     def f(self): pass
    ...     def my_handler(self): pass
    ...     def their_handler(self): pass
    ...     @log_calls(omit='*_function')
    ...     class I1():
    ...         def g1(self): pass
    ...         def some_handler(self): pass
    ...         def some_function(self): pass
    >>> oi1 = O.I1(); oi1.g1(); oi1.some_handler(); oi1.some_function()
    O.I1.g1 <== called by <module>

Further examples
++++++++++++++++++

For more examples of inner class decoration, consult the docstrings of the
functions ``main__lc_class_deco__inner_classes()``
and ``main__lc_class_deco__omit_only__inner_classes()`` in ``tests/test_log_calls__class_deco.py``.


----------------------------------------------------------------------------------------------------------------

.. _repr-not-decorated:

`log_calls` does not decorate ``__repr__``
==============================================

To avoid infinite, possibly indirect recursions, `log_calls` does not itself
decorate ``__repr__`` methods, but it will decorate them with :func:`reprlib.recursive_repr`:

>>> @log_calls()
... class A():
...     def __init__(self, x): self.x = x
...     def __repr__(self): return str(self.x)

The ``__init__`` method is decorated:

    >>> a = A(5)    # doctest: +ELLIPSIS
    A.__init__ <== called by <module>
        arguments: self=<__main__.A object at 0x...>, x=5
    A.__init__ ==> returning to <module>

but ``__repr__`` is not:

    >>> print(a)    # no log_calls output
    5

