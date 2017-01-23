.. _call_chains:

Call Chains
################################


`log_calls` does its best to chase back along the call chain to find
the first *enabled* `log_calls`-decorated callable on the stack.
If there's no such function, it just displays the immediate caller.
If there is such a function, however, it displays the entire list of
functions on the stack up to and including that function when reporting
calls and returns. Without this, you'd have to guess at what was called
in between calls to functions decorated by `log_calls`. If you specified
a ``prefix`` or ``name`` for the decorated caller on the end of a call chain, 
`log_calls` will use the requested display name:

.. _basic-examples:

Basic examples
====================

    >>> @log_calls()
    ... def g1():
    ...     pass
    >>> def g2():
    ...     g1()
    >>> @log_calls(prefix='mid.')
    ... def g3():
    ...     g2()
    >>> def g4():
    ...     g3()
    >>> @log_calls()
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
        mid.g3 <== called by g4 <== g5
            g1 <== called by g2 <== mid.g3
            g1 ==> returning to g2 ==> mid.g3
        mid.g3 ==> returning to g4 ==> g5
    g5 ==> returning to <module>

In the next example, ``g`` is `log_calls`-decorated but logging is disabled,
so the reported call chain for ``f`` stops at its immediate caller:

    >>> @log_calls()
    ... def f(): pass
    >>> def not_decorated(): f()
    >>> @log_calls(enabled=False)
    ... def g(): not_decorated()
    >>> g()
    f <== called by not_decorated
    f ==> returning to not_decorated

Elaborating on the previous example, here are longer call chains with an
intermediate decorated function that has logging disabled:

    >>> @log_calls()
    ... def e(): pass
    >>> def not_decorated_call_e(): e()
    >>> @log_calls()
    ... def f(): not_decorated_call_e()
    >>> def not_decorated_call_f(): f()
    >>> @log_calls(enabled=False)
    ... def g(): not_decorated_call_f()
    >>> @log_calls()
    ... def h(): g()
    >>> h()
    h <== called by <module>
        f <== called by not_decorated_call_f <== g <== h
            e <== called by not_decorated_call_e <== f
            e ==> returning to not_decorated_call_e ==> f
        f ==> returning to not_decorated_call_f ==> g ==> h
    h ==> returning to <module>

`log_calls` chases back to the nearest *enabled* decorated callable,
so that there aren't gaps between call chains.

.. _Call-chains-inner-functions:

Call chains and inner functions
====================================

When chasing back along the stack, `log_calls` also detects inner functions that it has decorated:

    >>> @log_calls()
    ... def h0(z):
    ...     pass
    >>> def h1(x):
    ...     @log_calls(name='h1_inner')
    ...     def h1_inner(y):
    ...         h0(x*y)
    ...     return h1_inner
    >>> def h2():
    ...     h1(2)(3)
    >>> def h3():
    ...     h2()
    >>> def h4():
    ...     @log_calls(name='h4_inner')
    ...     def h4_inner():
    ...         h3()
    ...     return h4_inner
    >>> @log_calls()
    ... def h5():
    ...     h4()()
    >>> h5()
    h5 <== called by <module>
        h4_inner <== called by h5
            h1_inner <== called by h2 <== h3 <== h4_inner
                arguments: y=3
                h0 <== called by h1_inner
                    arguments: z=6
                h0 ==> returning to h1_inner
            h1_inner ==> returning to h2 ==> h3 ==> h4_inner
        h4_inner ==> returning to h5
    h5 ==> returning to <module>


... even when the inner function is called from within the outer function it's defined in:

    >>> @log_calls()
    ... def j0():
    ...     pass
    >>> def j1():
    ...     j0()
    >>> def j2():
    ...     @log_calls()
    ...     def j2_inner():
    ...         j1()
    ...     j2_inner()
    >>> @log_calls()
    ... def j3():
    ...     j2()
    >>> j3()
    j3 <== called by <module>
        j2.<locals>.j2_inner <== called by j2 <== j3
            j0 <== called by j1 <== j2.<locals>.j2_inner
            j0 ==> returning to j1 ==> j2.<locals>.j2_inner
        j2.<locals>.j2_inner ==> returning to j2 ==> j3
    j3 ==> returning to <module>

.. _Call-chains-log_call_numbers:

Call chains and *log_call_numbers*
====================================

If a decorated callable is enabled and has ``log_call_numbers`` set to true,
then its call numbers will be displayed in call chains:

    >>> @log_calls()
    ... def f(): pass
    >>> def not_decorated(): f()
    >>> @log_calls(log_call_numbers=True)
    ... def g(): not_decorated()
    >>> g()
    g [1] <== called by <module>
        f <== called by not_decorated <== g [1]
        f ==> returning to not_decorated ==> g [1]
    g [1] ==> returning to <module>

Also apropos is the example :ref:`recursion-example`.
