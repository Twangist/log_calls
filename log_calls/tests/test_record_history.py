__author__ = "Brian O'Neill"
__version__ = '0.1.14'

import doctest


def main__record_history():
    """
# [The *record_history* decorator](id:record_history-decorator)
The `record_history` decorator is a stripped-down version of `log_calls` which
records calls to a decorated function but writes no messages. You can think
of it as `log_calls` with the `record_history` and `log_call_numbers` settings
always true, and without any of the message-logging apparatus.

Just as the settings of `log_calls` for a decorated function are accessible
dynamically through the `log_calls_settings` attribute, the settings of
`record_history` are exposed via a `record_history_settings` attribute.
`record_history_settings` is an object of the same type as `log_calls_settings`,
so it has the same methods and behaviors described in the [`log_calls_settings`
section](./log_calls.html#Dynamic-control-log_calls_settings) of the `log_calls`
documentation.

Functions decorated by `record_history` have a full-featured `stats` attribute,
as described in the [Call history and statistics](#./log_calls.html#call-history-and-statistics)
section of the `log_calls` documentation.

## [Usage](id:usage)
Import `record_history` just as you would `log_calls`:

    >>> from log_calls import record_history

We'll use the following function in our examples:

    >>> @record_history()
    ... def record_me(a, b, x):
    ...     return a * x + b

## [Keyword Parameters](id:parameters)
`record_history` has only three keyword parameters:

Keyword parameter | Default value | Description
----------------: | :------------ | :------------------
       `enabled`    | `True`          | When true, call history will be recorded
       `prefix`     | ``              | A `str` to prefix the function name with in call records
       `max_history`    | 0           | An `int`. *value* > 0 --> store at most *value*-many records, oldest records overwritten; *value* ≤ 0 --> store unboundedly many records.

Setting `enabled` to true in `record_history` is like setting both `enabled`
and `record_history` to true in `log_calls`.

You can supply an [*indirect value*](./log_calls.html#Indirect-values) for the `enabled` parameter, as described
in the log_calls documentation.

## [The *record_history_settings* attribute](id:record_history_settings-attribute)
These settings are accessible dynamically through the `record_history_settings`
attribute of a decorated function.

    >>> len(record_me.record_history_settings)
    3
    >>> list(record_me.record_history_settings)
    ['enabled', 'prefix', 'max_history']
    >>> list(record_me.record_history_settings.items())
    [('enabled', True), ('prefix', ''), ('max_history', 0)]
    >>> record_me.record_history_settings.as_OrderedDict()  # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True), ('prefix', ''), ('max_history', 0)])

## [Call history and statistics for *record_history*](id:Call-history-and-statistics-record_history)
We'll just give a few examples here to show that the `stats` attribute of `record_history`
works just like that of `log_calls`. For a complete account, see
the [Call history and statistics](#./log_calls.html#call-history-and-statistics)
section of the `log_calls` documentation.

Let's finally call the function defined above:

    >>> for x in range(15):
    ...     _ = record_me(3, 5, x)      # "_ = " for doctest

    >>> import pprint
    >>> len(record_me.stats.call_history)
    15

The tallies:

    >>> record_me.stats.num_calls_logged
    15
    >>> record_me.stats.num_calls_total
    15
    >>> record_me.stats.elapsed_secs_logged          # doctest: +SKIP
    2.2172927856445312e-05

Call history in CSV format, with ellipses for 'elapsed_secs' and 'timestamp' columns:

    >>> print(record_me.stats.call_history_as_csv)         # doctest: +ELLIPSIS
    'call_num'|'a'|'b'|'x'|'retval'|'elapsed_secs'|'timestamp'|'prefixed_fname'|'caller_chain'
    1|3|5|0|5|...|...|'record_me'|['<module>']
    2|3|5|1|8|...|...|'record_me'|['<module>']
    3|3|5|2|11|...|...|'record_me'|['<module>']
    4|3|5|3|14|...|...|'record_me'|['<module>']
    5|3|5|4|17|...|...|'record_me'|['<module>']
    6|3|5|5|20|...|...|'record_me'|['<module>']
    7|3|5|6|23|...|...|'record_me'|['<module>']
    8|3|5|7|26|...|...|'record_me'|['<module>']
    9|3|5|8|29|...|...|'record_me'|['<module>']
    10|3|5|9|32|...|...|'record_me'|['<module>']
    11|3|5|10|35|...|...|'record_me'|['<module>']
    12|3|5|11|38|...|...|'record_me'|['<module>']
    13|3|5|12|41|...|...|'record_me'|['<module>']
    14|3|5|13|44|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|'record_me'|['<module>']
    <BLANKLINE>

Disable recording, call the function again:

    >>> record_me.record_history_settings.enabled = False
    >>> _ = record_me(583, 298, 1000)

Call numbers of last 2 calls to `record_me`:
    >>> list(map(lambda rec: rec.call_num, record_me.stats.call_history[-2:]))
    [14, 15]

and here are the call counters:

    >>> record_me.stats.num_calls_logged
    15
    >>> record_me.stats.num_calls_total
    16

Re-enable recording and call the function again:

    >>> record_me.record_history_settings.enabled = True
    >>> _ = record_me(1900, 2000, 20)

Here are the last 3 lines of the CSV call history:
    >>> for line in record_me.stats.call_history_as_csv.strip().split('\\n')[-3:]:       # doctest: +ELLIPSIS
    ...     print(line)
    14|3|5|13|44|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|'record_me'|['<module>']
    16|1900|2000|20|40000|...|...|'record_me'|['<module>']

and here are the call updated counters:

    >>> record_me.stats.num_calls_logged
    16
    >>> record_me.stats.num_calls_total
    17

Finally, let's call `stats.clear_history`, setting `max_history` to 3,
and examine the call history again:

    >>> record_me.stats.clear_history(max_history=3)
    >>> for x in range(15):
    ...     _ = record_me(3, 5, x)
    >>> print(record_me.stats.call_history_as_csv)      # doctest: +ELLIPSIS
    'call_num'|'a'|'b'|'x'|'retval'|'elapsed_secs'|'timestamp'|'prefixed_fname'|'caller_chain'
    13|3|5|12|41|...|...|'record_me'|['<module>']
    14|3|5|13|44|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|'record_me'|['<module>']
    <BLANKLINE>

## [Call history and call chains](id:Call-history-and-call-chains)
An example showing a longer call chain, and call numbers of a decorated
caller appearing in the call chain:

    >>> record_me.stats.clear_history()

    >>> class Base():
    ...     def call_record_me(self, a, b, n):
    ...         nth = 2**n
    ...         for k in range(nth, 2 * nth):
    ...             record_me(a, b, k)
    >>> class Even(Base):
    ...     @record_history(prefix='Even.')
    ...     def call_it(self, n):
    ...         self.call_record_me(2*n + 1, 3*n + 1, n)
    >>> class Odd(Base):
    ...     @record_history(prefix='Odd.')
    ...     def call_it(self, n):
    ...         self.call_record_me(5*n + 1, 7*n + 1, n)
    >>> even = Even()
    >>> odd = Odd()
    >>> for i in range(3):
    ...     (even, odd)[i%2].call_it(i)

    >>> even.call_it.stats.num_calls_logged, odd.call_it.stats.num_calls_logged
    (2, 1)
    >>> record_me.stats.num_calls_logged
    7

    >>> print(even.call_it.stats.call_history_as_csv)        # doctest: +ELLIPSIS
    'call_num'|'self'|'n'|'retval'|'elapsed_secs'|'timestamp'|'prefixed_fname'|'caller_chain'
    1|<__main__.Even object at ...>|0|None|...|...|'Even.call_it'|['<module>']
    2|<__main__.Even object at ...>|2|None|...|...|'Even.call_it'|['<module>']
    <BLANKLINE>

    >>> print(odd.call_it.stats.call_history_as_csv)        # doctest: +ELLIPSIS
    'call_num'|'self'|'n'|'retval'|'elapsed_secs'|'timestamp'|'prefixed_fname'|'caller_chain'
    1|<__main__.Odd object at ...>|1|None|...|...|'Odd.call_it'|['<module>']
    <BLANKLINE>

    >>> print(record_me.stats.call_history_as_csv)     # doctest: +ELLIPSIS
    'call_num'|'a'|'b'|'x'|'retval'|'elapsed_secs'|'timestamp'|'prefixed_fname'|'caller_chain'
    1|1|1|1|2|...|...|'record_me'|['call_record_me', 'Even.call_it [1]']
    2|6|8|2|20|...|...|'record_me'|['call_record_me', 'Odd.call_it [1]']
    3|6|8|3|26|...|...|'record_me'|['call_record_me', 'Odd.call_it [1]']
    4|5|7|4|27|...|...|'record_me'|['call_record_me', 'Even.call_it [2]']
    5|5|7|5|32|...|...|'record_me'|['call_record_me', 'Even.call_it [2]']
    6|5|7|6|37|...|...|'record_me'|['call_record_me', 'Even.call_it [2]']
    7|5|7|7|42|...|...|'record_me'|['call_record_me', 'Even.call_it [2]']
    <BLANKLINE>

##[*stats.elapsed_secs_logged* == sum of *elapsed_secs* column of call history](id:elapsed_secs_logged-equal-sum-etc)
Equal "to within an epsilon", anyway, allowing for some very small
numerical inaccuracy:

    >>> @record_history()
    ... def slow(n):
    ...     val = []
    ...     for i in range(n):
    ...         val.append("a" * i)
    >>> for i in range(100):
    ...     slow(i)
    >>> elapsed_col = list(map(lambda rec: getattr(rec, 'elapsed_secs'),
    ...                        slow.stats.call_history))
    >>> abs(sum(elapsed_col) - slow.stats.elapsed_secs_logged) < 1.0e-15
    True

    """
    pass


# SURGERY:
main__record_history.__doc__ = \
    main__record_history.__doc__.replace("__main__", __name__)


# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

