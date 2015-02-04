__author__ = "Brian O'Neill"
__version__ = '0.2.1'

import doctest


#-----------------------------------------------------------------------------
# main__record_history_class_deco
#-----------------------------------------------------------------------------
def main__record_history_class_deco():
    """
# [The *record_history* decorator as a class decorator](id:record_history-decorator-class-deco)
The `record_history` decorator

## Basic example
illustrating that `record_history` works as a class decorator too, and,
unlike `log_calls`, can record calls to `__repr__`:

    >>> from log_calls import record_history

A not very interesting class:

    >>> @record_history(omit='h')
    ... class RecordThem():
    ...     def __init__(self, a):
    ...         self._a = a
    ...     def f(self, x):
    ...         return self.a * x
    ...     @record_history(name='RT.gee')
    ...     def g(self, x, y):
    ...         return self.f(x) + y
    ...     def h(self, x, y, z):
    ...         pass
    ...     @property
    ...     def a(self):
    ...         return self._a
    ...     def __repr__(self):
    ...         return '<A(%r) at 0x%x>' % (self._a, id(self))
    >>> rt = RecordThem(10)

`RecordThem.__init__` is decorated:

    >>> rt.__init__.stats.num_calls_logged
    1

Unlike `log_calls`, `record_history` *can* decorate `__repr__`.
This will call `RecordThem.__repr__` once:

    >>> print(rt)                              # doctest: +ELLIPSIS
    <A(10) at 0x...>

`__repr` is decorated in `RecordThem`:

    >>> rt.__repr__.stats.num_calls_logged
    1

`RecordThem.f` and `RecordThem.g` are decorated:

    >>>
    >>> for i in range(5):
    ...     _ = rt.f(i), rt.g(i, 2*i)   # _ = ... : suppress doctest output
    >>> rt.f.stats.num_calls_logged, rt.g.stats.num_calls_logged
    (10, 5)

    >>> print(rt.f.stats.history_as_csv)       # doctest: +ELLIPSIS
    call_num|self|x|retval|elapsed_secs|CPU_secs|timestamp|prefixed_fname|caller_chain
    1|<A(10) at 0x...>|0|0|...|...|...|'RecordThem.f'|['<module>']
    2|<A(10) at 0x...>|0|0|...|...|...|'RecordThem.f'|['RT.gee [1]']
    3|<A(10) at 0x...>|1|10|...|...|...|'RecordThem.f'|['<module>']
    4|<A(10) at 0x...>|1|10|...|...|...|'RecordThem.f'|['RT.gee [2]']
    5|<A(10) at 0x...>|2|20|...|...|...|'RecordThem.f'|['<module>']
    6|<A(10) at 0x...>|2|20|...|...|...|'RecordThem.f'|['RT.gee [3]']
    7|<A(10) at 0x...>|3|30|...|...|...|'RecordThem.f'|['<module>']
    8|<A(10) at 0x...>|3|30|...|...|...|'RecordThem.f'|['RT.gee [4]']
    9|<A(10) at 0x...>|4|40|...|...|...|'RecordThem.f'|['<module>']
    10|<A(10) at 0x...>|4|40|...|...|...|'RecordThem.f'|['RT.gee [5]']
    <BLANKLINE>

`RecordThem.h` is not decorated:

    >>> hasattr(rt.h, 'stats')
    False

---------------------------------------------------------
## `record_history_wrapper` method of a decorated class

Attributes of properties defined by the @property decorator can be accessed
using the `record_history_wrapper` classmethod:

    >>> RecordThem.record_history_wrapper('a.getter').stats.num_calls_logged
    10

We could have also used `rt.record_history_wrapper('a.getter')`. You pass
`record_history_wrapper` the name of a method, or a property suffixed with
`.getter`, '.setter' or '.deleter'. If you pass just the name of a property,
`.getter` is assumed:

    >>> RecordThem.record_history_wrapper('a').stats.num_calls_logged
    10

`record_history_wrapper` returns None if the method exists but isn't decorated:

    >>> print(rt.record_history_wrapper('h'))
    None

and raises an exception for other arguments (see tests and description for `log_calls_wrapper`).

---------------------------------------------------------
## `record_history_omit` `record_history_only`

    >>> rt.record_history_omit
    ('h',)


    """
    pass


# SURGERY:
main__record_history_class_deco.__doc__ = \
    main__record_history_class_deco.__doc__.replace("__main__", __name__)


#-----------------------------------------------------------------------------
# main__record_history_class_deco__
#-----------------------------------------------------------------------------




#-----------------------------------------------------------------------------
# main__record_history_class_deco__
#-----------------------------------------------------------------------------


##############################################################################
# end of tests.
##############################################################################


#-----------------------------------------------------------------------------
# For unittest integration
#-----------------------------------------------------------------------------
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

