.. _what-log_calls-can-decorate:

What *log_calls* Can Decorate
####################################

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

|    Anything that `log_calls` can decorate is a callable,
|    but not every callable can be decorated by `log_calls`.
|

Whatever `log_calls` **cannot** decorate, it simply returns unchanged.

.. index:: callable

.. _what-is-a-callable:

What is a "callable"?
==========================

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

A few negative examples
==============================================

`log_calls` can't decorate callable builtins, such as ``len`` — it just returns the builtin unchanged:

    >>> len is log_calls()(len)    # No "wrapper" around len -- not deco'd
    True
    >>> dict.update is log_calls()(dict.update)
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

