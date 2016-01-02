__author__ = 'brianoneill'

from log_calls import log_calls

##############################################################################

def test_double_func_deco():
    """
Double-decorating a function doesn't raise:

    >>> @log_calls()
    ... @log_calls()
    ... def f(): pass
    >>> f()
    f <== called by <module>
    f ==> returning to <module>

The inner settings take precedence over the outer ones:
the outer explicitly given settings are updated with the inner explicitly given settings,
and the result becomes the settings of the decorated function.
Here, the resulting settings of g are: args_sep='; ', log_retval=True:

    >>> @log_calls(args_sep=' | ', log_retval=True)
    ... @log_calls(args_sep='; ')
    ... def g(x, y): pass
    >>> g('a', 'b')
    g <== called by <module>
        arguments: x='a'; y='b'
        g return value: None
    g ==> returning to <module>

Finally, a function decorated multiple times is wrapped just once, not multiple times;
after the first/innermost decoration, subsequent decorations only affect its settings.

Here's a similar example, this time using `log_calls` as a higher-order
function so we can access both the wrapped function and its wrapper(s).

Recall how the @ syntactic sugar works:
    @log_calls(args_sep='; ')
    def h(x, y): ...
is shorthand for:
    def h(x, y): ...
    h = log_calls(args_sep='; ')(h)

so h is set to log_calls(args_sep='; ')(h), which is a wrapper function that writes
log_calls output before and after calling the inner/original/wrapped h.
The following lines achieve the same effect but allow us to save the original h:
    >>> def h(x, y): return x + y
    >>> orig_h = h
    >>> h_lc1 = log_calls(args_sep='; ')(h)
    >>> h_lc1 is not orig_h
    True

orig_h is the original undecorated function:
    >>> orig_h(3, 4)
    7

and h_lc1 is the wrapper:
    >>> h_lc1(3, 4)
    h <== called by <module>
        arguments: x=3; y=4
    h ==> returning to <module>
    7

Now "decorate h again" -- that is, decorate h_lc1, yielding h_lc2.
Note that h_lc1 IS h_lc2, so there is NO additional wrapper,
and only h_lc1's settings have changed:

    >>> h_lc2 = log_calls(args_sep=' | ', log_retval=True)(h_lc1)
    >>> h_lc1 is h_lc2
    True
    >>> h_lc2(3, 4)
    h <== called by <module>
        arguments: x=3; y=4
        h return value: 7
    h ==> returning to <module>
    7

    """
    pass


##############################################################################
# end of tests.
##############################################################################

import doctest

# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests

if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

    # unittest.main()
