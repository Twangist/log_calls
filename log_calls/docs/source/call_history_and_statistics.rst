.. _call_history_statistics:

Call History and Statistics
#################################################

Unless it's :ref:`bypassed <enabled-as-bypass>`, `log_calls` always collects at least
a few basic statistics about each call to a decorated callable.
It can collect the entire history of calls to a function or method if asked
to (using the :ref:`record_history <record_history-parameter>` setting).
The statistics and history are accessible via the ``stats`` attribute
that `log_calls` adds to the wrapper of a decorated callable.

The two settings parameters we haven't yet discussed govern the recording
and retention of a decorated callable's call history.

.. _record_history-parameter:

The ``record_history`` parameter (default: ``False``)
===============================================================

When the ``record_history`` setting is true for a decorated callable,
`log_calls` accumulates a sequence of records holding the details of each
*logged* call to the callable:

    A **logged call** to a decorated callable is one that occurs when
    the callable's ``enabled`` setting is true.

That history is accessible via attributes of the ``stats`` object.

Let's define a function ``f`` with ``record_history`` set to true:

    >>> @log_calls(record_history=True, log_call_numbers=True, log_exit=False)
    ... def f(a, *args, x=1, **kwargs): pass

In the next few sections, we'll call this function, manipulate its settings,
and examine its statistics and history.

.. _max_history-parameter:

The ``max_history`` parameter (default: ``0``)
===============================================================

The ``max_history`` parameter bounds the number of call history records retained
in a decorated callable's recorded call history. If this value is 0 or negative,
unboundedly many records are retained (unless or until you change the ``record_history``
setting to false, or call the ``stats.clear_history()`` method). If the value of
``max_history`` is > 0, call history operates as a least-recently-used cache:
`log_calls` will retain at most that many records, discarding the oldest record
to make room for a new ones if the history is at capacity.

You cannot change ``max_history`` using the mapping interface or the attribute
of the same name; attempts to do so raise ``ValueError``. The only way to change
its value is with the ``stats.clear_history(max_history=0)`` method, discussed
:ref:`below <clear_history>`.

.. index:: !stats (data attribute of decorated callable's wrapper)

.. _stats-attribute:

The ``stats`` attribute and *its* attributes
===============================================================

The ``stats`` attribute of a decorated callable is an object that provides
read-only statistics and data about the calls to a decorated callable:

* :ref:`stats.num_calls_logged <num_calls_logged>`
* :ref:`stats.num_calls_total <num_calls_total>`
* :ref:`stats.elapsed_secs_logged <elapsed_secs_logged>`
* :ref:`stats.process_secs_logged <process_secs_logged>`
* :ref:`stats.history <history>`
* :ref:`stats.history_as_csv <history_as_csv>`
* :ref:`stats.history_as_DataFrame <history_as_DataFrame>`

The first four of these don't depend on the ``record_history`` setting at all.
The last three values, ``stats.history*``, are empty unless ``record_history``
is or has been true.

The ``stats`` attribute also provides one method, :ref:`stats.clear_history() <clear_history>`.

Let's call the above-defined function ``f`` twice:

    >>> f(0)
    f [1] <== called by <module>
        arguments: a=0
        defaults:  x=1
    >>> f(1, 100, 101, x=1000, y=1001)
    f [2] <== called by <module>
        arguments: a=1, *args=(100, 101), x=1000, **kwargs={'y': 1001}

and explore its ``stats``.

.. _num_calls_logged:

The ``stats.num_calls_logged`` attribute
----------------------------------------------

The ``stats.num_calls_logged`` attribute holds the number of the most
recent logged call to a decorated callable. Thus, ``f.stats.num_calls_logged``
will equal 2:

    >>> f.stats.num_calls_logged
    2

This counter is incremented on each logged call to the callable, even if its
``log_call_numbers`` setting is false.

.. _num_calls_total:

The ``stats.num_calls_total`` attribute
-----------------------------------------------

The ``stats.num_calls_total`` attribute holds the *total* number of calls
to a decorated callable. This counter is incremented even when logging
is disabled for a callable (its ``enabled`` setting is ``False``, i.e. ``0``),
but *not* when it's :ref:`bypassed <enabled-as-bypass>`.

To illustrate, let's now *disable* logging for ``f`` and call it 3 more times:

    >>> f.log_calls_settings.enabled = False
    >>> for i in range(3): f(i)

Now ``f.stats.num_calls_total`` will equal 5, but ``f.stats.num_calls_logged``
will still equal 2:

    >>> f.stats.num_calls_total
    5
    >>> f.stats.num_calls_logged
    2

Finally, let's re-enable logging for ``f`` and call it again.
The displayed call number will be the number of the *logged* call, 3, the same
value as ``f.stats.num_calls_logged`` after the call:

    >>> f.log_calls_settings.enabled = True
    >>> f(10, 20, z=5000)
    f [3] <== called by <module>
        arguments: a=10, *args=(20,), **kwargs={'z': 5000}
        defaults:  x=1

    >>> f.stats.num_calls_total
    6
    >>> f.stats.num_calls_logged
    3

.. _elapsed_secs_logged:

The ``stats.elapsed_secs_logged`` attribute
------------------------------------------------

The ``stats.elapsed_secs_logged`` attribute holds the sum of the elapsed times of
all *logged* calls to a decorated callable, in seconds. Here's its value for the three
logged calls to ``f`` above (this doctest is actually ``+SKIP``\ ped):

    >>> f.stats.elapsed_secs_logged   # doctest: +SKIP
    6.67572021484375e-06

.. _process_secs_logged:

The ``stats.process_secs_logged`` attribute
------------------------------------------------

The ``stats.process_secs_logged`` attribute holds the sum of the process times
of all *logged* calls to a decorated callable, in seconds.
Here's its value for the three logged calls to ``f`` above (this doctest is
actually ``+SKIP``\ ped):

    >>> f.stats.process_secs_logged   # doctest: +SKIP
    1.1000000000038757e-05

.. _history:

The ``stats.history`` attribute
--------------------------------------------

The ``stats.history`` attribute of a decorated callable provides the call history
of logged calls as a tuple of records. Each record is a ``namedtuple``
of type ``CallRecord``, whose fields are those shown in the following example.
Here's ``f``'s call history, output reformatted for readability:

    >>> print('\\n'.join(map(str, f.stats.history)))   # doctest: +SKIP
    CallRecord(call_num=1, argnames=['a'], argvals=(0,), varargs=(),
                           explicit_kwargs=OrderedDict(),
                           defaulted_kwargs=OrderedDict([('x', 1)]), implicit_kwargs={},
                           retval=None,
                           elapsed_secs=3.0049995984882116e-06,
                           process_secs=2.9999999999752447e-06,
                           timestamp='10/28/14 15:56:13.733763',
                           prefixed_func_name='f', caller_chain=['<module>'])
    CallRecord(call_num=2, argnames=['a'], argvals=(1,), varargs=(100, 101),
                           explicit_kwargs=OrderedDict([('x', 1000)]),
                           defaulted_kwargs=OrderedDict(), implicit_kwargs={'y': 1001},
                           retval=None,
                           elapsed_secs=3.274002665420994e-06,
                           process_secs=3.0000000000030003e-06,
                           timestamp='10/28/14 15:56:13.734102',
                           prefixed_func_name='f', caller_chain=['<module>'])
    CallRecord(call_num=3, argnames=['a'], argvals=(10,), varargs=(20,),
                           explicit_kwargs=OrderedDict(),
                           defaulted_kwargs=OrderedDict([('x', 1)]), implicit_kwargs={'z': 5000},
                           retval=None,
                           elapsed_secs=2.8769973141606897e-06,
                           process_secs=2.9999999999752447e-06,
                           timestamp='10/28/14 15:56:13.734412',
                           prefixed_func_name='f', caller_chain=['<module>'])

The CSV representation, discussed next, pairs the ``argnames`` with their values
in ``argvals`` (each parameter name in ``argnames`` become a column heading),
making it more human-readable, especially when viewed in a program that presents
CSVs nicely.

.. _history_as_csv:

The ``stats.history_as_csv`` attribute
-------------------------------------------------

The value ``stats.history_as_csv`` attribute is a text representation in CSV format
of a decorated callable's call history. You can save this string
and import it into the program or tool of your choice for further analysis.
(If your tool of choice is `Pandas <http://pandas.pydata.org>`_, you can use
:ref:`history_as_DataFrame`, discussed next, to obtain history directly in
the representation you really want.)

The CSV representation breaks out each argument into its own column, throwing away
information about whether an argument's value was explicitly passed or is a default.

The CSV separator is ``'|'`` rather than ``','`` because some of the fields – ``args``,  ``kwargs``
and ``caller_chain`` – use commas intrinsically. Let's examine ``history_as_csv``
for a function that has all of those fields nontrivially:

    >>> @log_calls(record_history=True, log_call_numbers=True,
    ...            log_exit=False, log_args=False)
    ... def f(a, *extra_args, x=1, **kw_args): pass
    >>> def g(a, *args, **kwargs):
    ...     f(a, *args, **kwargs)
    >>> @log_calls(log_exit=False, log_args=False)
    ... def h(a, *args, **kwargs):
    ...     g(a, *args, **kwargs)
    >>> h(0)
    h <== called by <module>
        f [1] <== called by g <== h
    >>> h(10, 17, 19, z=100)
    h <== called by <module>
        f [2] <== called by g <== h
    >>> h(20, 3, 4, 6, x=5, y='Yarborough', z=100)
    h <== called by <module>
        f [3] <== called by g <== h

Here's the call history of ``f`` in CSV format (ellipses added for the ``elapsed_secs``,
``process_secs`` and ``timestamp`` fields):

    >>> print(f.stats.history_as_csv)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    call_num|a|extra_args|x|kw_args|retval|elapsed_secs|process_secs|timestamp|prefixed_fname|caller_chain
    1|0|()|1|{}|None|...|...|...|'f'|['g', 'h']
    2|10|(17, 19)|1|{'z': 100}|None|...|...|...|'f'|['g', 'h']
    3|20|(3, 4, 6)|5|{'y': 'Yarborough', 'z': 100}|None|...|...|...|'f'|['g', 'h']
    <BLANKLINE>

In tabular form,

+----------+----+------------+---+----------------------+--------+--------------+--------------+-----------+----------------+--------------+
| call_num | a  | extra_args | x | kw_args              | retval | elapsed_secs | process_secs | timestamp | prefixed_fname | caller_chain |
+==========+====+============+===+======================+========+==============+==============+===========+================+==============+
| 1        | 0  | ()         | 1 || {}                  | None   |     ...      |     ...      |    ...    | 'f'            | ['g', 'h']   |
+----------+----+------------+---+----------------------+--------+--------------+--------------+-----------+----------------+--------------+
| 2        | 10 | (17, 19)   | 1 || {'z': 100}          | None   |     ...      |     ...      |    ...    | 'f'            | ['g', 'h']   |
+----------+----+------------+---+----------------------+--------+--------------+--------------+-----------+----------------+--------------+
| 3        | 20 | (3, 4, 6)  | 5 || {'y': 'Yarborough', | None   |     ...      |     ...      |    ...    | 'f'            | ['g', 'h']   |
|          |    |            |   ||  'z': 100}          |        |              |              |           |                |              |
+----------+----+------------+---+----------------------+--------+--------------+--------------+-----------+----------------+--------------+

As usual, `log_calls` will use whatever names you use for *varargs* parameters
(here, ``extra_args`` and ``kw_args``). Whatever the name of the ``kwargs`` parameter,
items within that field are guaranteed to be in sorted order.

.. _history_as_DataFrame:

The ``stats.history_as_DataFrame`` attribute
--------------------------------------------------------

The ``stats.history_as_DataFrame`` attribute returns the history of a decorated
callable as a `Pandas <http://pandas.pydata.org>`_
`DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_,
if the Pandas library is installed. This saves you the intermediate step of
calling ``DataFrame.from_csv`` with the proper arguments (and also saves you from
having to know or care what those are).

If Pandas is not installed, the value of this attribute is ``None``.


..           .. py:method:: wrapper.stats.clear_history()
.. index:: stats.clear_history() (method of decorated callable's wrapper)

.. _clear_history:

The ``stats.clear_history(max_history=0)`` method
------------------------------------------------------------

As you might expect, the ``stats.clear_history(max_history=0)`` method clears
the call history of a decorated callable. In addition, it resets all running sums:

* ``num_calls_total`` and ``num_calls_logged`` are reset to ``0``,
* ``elapsed_secs_logged`` and ``process_secs_logged`` are reset to ``0.0``.

**This method is the only way to change the value of the ``max_history`` setting**,
via the optional keyword parameter for which you can supply any (integer) value,
by default ``0``.

The function ``f`` has a nonempty history, as we just saw. Let's clear ``f``'s history,
setting ``max_history`` to ``33``:

    >>> f.stats.clear_history(max_history=33)

and check that settings and ```stats``` tallies are reset:

    >>> f.log_calls_settings.max_history
    33
    >>> f.stats.num_calls_logged
    0
    >>> f.stats.num_calls_total
    0
    >>> f.stats.elapsed_secs_logged
    0.0
    >>> f.stats.process_secs_logged
    0.0
