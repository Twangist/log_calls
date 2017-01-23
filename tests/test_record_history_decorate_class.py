__author__ = 'brianoneill'

import doctest

def test__record_history_decorate_class():
    """
    >>> from log_calls import record_history

    >>> class A():
    ...     def __init__(self, x):  self.x = x
    ...     def twice(self):        return self.x + self.x

    >>> record_history.decorate_class(A, omit='__init__')
    >>> a = A('Abc')
    >>> _ = a.twice(); _ = a.twice(); _ = a.twice()

    >>> hasattr(a.__init__, 'stats')        # __init__ not deco'd
    False

    >>> import pprint
    >>> pprint.pprint(a.twice.stats.history)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    (CallRecord(call_num=1, argnames=['self'], argvals=(<__main__.A object at 0x...>,),
                            varargs=(), explicit_kwargs=OrderedDict(), defaulted_kwargs=OrderedDict(),
                            implicit_kwargs={}, retval='AbcAbc',
                            elapsed_secs=..., process_secs=..., timestamp=...,
                            prefixed_func_name='A.twice', caller_chain=['<module>']),
     CallRecord(call_num=2, argnames=['self'], argvals=(<__main__.A object at 0x...>,),
                            varargs=(), explicit_kwargs=OrderedDict(), defaulted_kwargs=OrderedDict(),
                            implicit_kwargs={}, retval='AbcAbc',
                            elapsed_secs=..., process_secs=..., timestamp=...,
                            prefixed_func_name='A.twice', caller_chain=['<module>']),
     CallRecord(call_num=3, argnames=['self'], argvals=(<__main__.A object at 0x...>,),
                            varargs=(), explicit_kwargs=OrderedDict(), defaulted_kwargs=OrderedDict(),
                            implicit_kwargs={}, retval='AbcAbc',
                            elapsed_secs=..., process_secs=..., timestamp=...,
                            prefixed_func_name='A.twice', caller_chain=['<module>']))

    """
    pass

# SURGERY:
test__record_history_decorate_class.__doc__ = \
    test__record_history_decorate_class.__doc__.replace("__main__", __name__)


# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests

if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

    # unittest.main()
