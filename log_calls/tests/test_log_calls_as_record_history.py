__author__ = 'brianoneill'

from log_calls import log_calls, record_history
import doctest

def test_():
    """
``record_history`` is equivalent to ``log_calls`` with the settings:
    record_history=True
    log_call_numbers=True
    mute=log_calls.MUTE.CALLS

This example, ``f``, doesn't use ``log_message`` or ``log_exprs``
so the absence of ``log_call_numbers`` won't be noticed.
``record_history`` *can* use the ``log_*`` methods.
Test with both ``mute=log_calls.MUTE.CALLS`` and ``mute=log_calls.MUTE.ALL``:
both should record history:

    >>> @log_calls(record_history=True, mute=log_calls.MUTE.CALLS)
    ... def f(n):
    ...     for i in range(n): pass

    >>> f(1); f(2); f(3)
    >>> print(f.stats.history_as_csv)      # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    call_num|n|retval|elapsed_secs|process_secs|timestamp|prefixed_fname|caller_chain
    1|1|None|...|...|...|'f'|['<module>']
    2|2|None|...|...|...|'f'|['<module>']
    3|3|None|...|...|...|'f'|['<module>']

    >>> f.stats.clear_history()
    >>> f.mute = log_calls.MUTE.ALL
    >>> f(1); f(2); f(3)
    >>> print(f.stats.history_as_csv)      # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    call_num|n|retval|elapsed_secs|process_secs|timestamp|prefixed_fname|caller_chain
    1|1|None|...|...|...|'f'|['<module>']
    2|2|None|...|...|...|'f'|['<module>']
    3|3|None|...|...|...|'f'|['<module>']

Without ``log_call_numbers=True``, call numbers won't be included in `log_*` output
using `log_calls`:

    >>> @log_calls(record_history=True, mute=log_calls.MUTE.CALLS)
    ... def g(n):
    ...     g.log_exprs("n")
    ...     for i in range(n): pass

    >>> g(1); g(2)    # No call numbers, by default
    g: n = 1
    g: n = 2

For reference, call numbers *are* included  in `log_*` output
when using `record_history`:

    >>> @record_history()
    ... def h(n):
    ...     h.log_exprs("n")
    ...     for i in range(n): pass

    >>> h(1); h(2)    # call numbers
    h [1]: n = 1
    h [2]: n = 2
    """
    pass

#############################################################################

# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

