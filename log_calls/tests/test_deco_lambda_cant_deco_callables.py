__author__ = 'brianoneill'

import doctest
from log_calls import log_calls

##############################################################################

def test_deco_lambda():
    """
    >>> f = log_calls()(lambda x: 2 * x)
    >>> f(3)
    <lambda> <== called by <module>
        arguments: x=3
    <lambda> ==> returning to <module>
    6
    """
    pass

def test_cant_deco_callables():
    """
Builtins aren't / can't be decorated:

    >>> len is log_calls()(len)    # No ""wrapper"" around `len` -- not deco'd
    True
    >>> len('abc')  # Redundant check that `len` isn't deco'd
    3

Similarly,

    >>> dict.update is log_calls()(dict.update)
    True

Builtin classes aren't deco'd (v0.3.0b20 fix to _add_class_attrs() makes it harmless)
(Best to have a test for this: fix in `_add_class_attrs` looks for a substring
in TypeError error message, so be able to detect if that changes.)

None of these three lines raise raise TypeError:

    >>> dict is log_calls(only='update')(dict)
    True
    >>> dict is log_calls()(dict)
    True
    >>> log_calls.decorate_class(dict, only='update')

    >>> d = dict(x=1, y=2)      # no output, dict.__init__ not deco'd
    >>> d.update(x=500)         # no output, dict.update not deco'd


Objects that are callable by virtue of implementing the `__call__` method
can't themselves be decorated -- anyway, `log_calls` declines to do so:

    >>> from functools import partial
    >>> def h(x, y): return x + y
    >>> h2 = partial(h, 2)        # so
    >>> callable(h2)
    True
    >>> h2 is log_calls()(h2)     # not deco'd
    True
    >>> h2(3)
    5

Another example of that:

    >>> class Rev():
    ...     def __call__(self, s):  return s[::-1]
    >>> rev = Rev()
    >>> callable(rev)
    True
    >>> rev is log_calls()(rev)  # not deco'd
    True
    >>> rev('ABC')
    'CBA'

However, the class whose instances are callables can be decorated, and then,
`log_calls` produces output when instances are called.

Let's use log_calls() as a function, applying it to the `Rev` class already
defined, instead of using @log_calls() and redefining the class.
All we have to do is call `log_calls()(Rev)`. But that returns a value,
and since this is a doctest, that would be a failed test. We'd have to say
`_ = log_calls()(Rev)` to suppress the value. So, better to show and test
what the returned value really is.

When called on a class, `log_calls` alters the class and some of its members
but returns the same class object:

    >>> # Save Rev, just in case you suspect log_calls might change
    >>> #   the binding of 'Rev' (! -- it doesn't)
    >>> T = Rev
    >>> # All three of these things are identical (`is`-chaining):
    >>> T is Rev is log_calls()(Rev)
    True

Now, instances of Rev have a decorated `__call__` method:
    >>> rev2 = Rev()
    >>> rev2('XYZ')                         # doctest: +ELLIPSIS
    Rev.__call__ <== called by <module>
        arguments: self=<__main__.Rev object at 0x...>, s='XYZ'
    Rev.__call__ ==> returning to <module>
    'ZYX'

    """
    pass

# SURGERY:
test_cant_deco_callables.__doc__ = \
    test_cant_deco_callables.__doc__.replace('__main__', __name__)

##############################################################################
# end of tests.
##############################################################################


# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

    # unittest.main()
