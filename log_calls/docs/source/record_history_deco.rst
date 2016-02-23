.. _record_history_deco:

The `record_history` Decorator
#####################################

The `record_history` decorator is a stripped-down version of `log_calls` which
records calls to a decorated callable but writes no messages.
You can think of it as `log_calls` with the ``record_history`` and ``log_call_numbers``
settings always true, with ``mute`` always true (equal, that is, to ``log_calls.MUTE.CALLS``),
and without any of the automatic message-logging apparatus.

`record_history` shares a great deal of functionality with `log_calls`. This chapter will
note differences where they exist, and point to the corresponding documentation for
`log_calls` features.

Usage
===================

Import `record_history` just as you would `log_calls`:

    >>> from log_calls import record_history

We'll use the following function in our examples throughout this chapter:

    >>> @record_history()
    ... def record_me(a, b, x):
    ...     return a * x + b


Keyword parameters
===========================

`record_history` has only the following keyword parameters:

* ``enabled``
* ``prefix``
* ``max_history``
* ``omit``
* ``only``
* ``NO_DECO``
* ``settings``

Of these, only three are "settings" — data that `record_history` maintains about the state
of a decorated callable:

+-----------------------+----------------+---------------------------------------------+
| Keyword parameter     | Default value  || Description                                |
+=======================+================+=============================================+
| ``enabled``           | ``True``       || When true, call history will be recorded   |
+-----------------------+----------------+---------------------------------------------+
| ``prefix``            | ``''``         || A ``str`` to prefix the function name with |
|                       |                || in call records                            |
+-----------------------+----------------+---------------------------------------------+
| ``max_history``       | ``0``          || An ``int``. If the value is > 0,           |
|                       |                || store at most *value*-many records,        |
|                       |                || with oldest records overwritten;           |
|                       |                || if the value is ≤ 0, store unboundedly     |
|                       |                || many records.                              |
+-----------------------+----------------+---------------------------------------------+

Setting ``enabled`` to true in `record_history` is like setting both `enabled`
and `record_history` to true in `log_calls` (granting the analogy above about ``mute``).
You can supply an :ref:`indirect value <indirect_values>` for the ``enabled`` parameter,
as for `log_calls`.

The ``enabled`` and ``prefix`` settings are mutable; ``max_history`` can only be changed
with the ``stats.clear_history(max_history=0)`` method of a decorated callable.


Use ``NO_DECO`` for production
-------------------------------

Like `log_calls`, the `record_history` decorator imposes some runtime overhead.
As for `log_calls`, you can use the ``NO_DECO`` parameter in a settings file
or settings dict so that you can easily toggle decoration, as explained
in :ref:`NO_DECO-for-production`.

.. index:: record_history_settings (data attribute of decorated callable's wrapper)

"Settings", and the ``record_history_settings`` attribute
==============================================================

Just as the settings of `log_calls` for a decorated callable are accessible
dynamically through the ``log_calls_settings`` attribute, the settings of
`record_history` are exposed via a ``record_history_settings`` attribute.

``record_history_settings`` is an object of the same type as ``log_calls_settings``,
so it has the same methods and behaviors described in the :ref:`log_calls_settings <log_calls_settings-obj>`
section.

As mentioned above, `record_history` has just a few "settings":

    >>> len(record_me.record_history_settings)
    3
    >>> record_me.record_history_settings.as_OD()   # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True), ('prefix', ''), ('max_history', 0)])

..    .. py:data:: record_history_wrapper.stats
.. index:: stats (for record_history-decorated callables)

The ``stats`` attribute and *its* attributes
==============================================================

Callables decorated by `record_history` have a full-featured ``stats`` attribute,
as described in :ref:`stats-attribute`. In the :ref:`record_history-examples` section
below, we'll illustrate its use with the ``record_me`` function.


The ``log_message()`` and ``log_exprs()`` methods
==============================================================

Callables decorated with `record_history` can use :ref:`indent_aware_writing_methods`
``log_message()`` and ``log_exprs()``. Of course, you won't want to do so in a tight loop
whose performance you're profiling, but the functions are available. Output is always via ``print``.


.. index:: get_record_history_wrapper() (record_history-decorated class method)

.. index:: get_own_record_history_wrapper() (record_history-decorated class method)

..    .. py:classmethod:: record_history_decorated_class.get_record_history_wrapper(), record_history_decorated_class.get_own_record_history_wrapper()

The ``get_record_history_wrapper()`` and ``get_own_record_history_wrapper()`` methods
================================================================================================

These classmethods are completely analogous to the ``get_log_calls_wrapper()`` and
``get_own_log_calls_wrapper()`` classmethods, described in the section on
:ref:`accessing wrappers of methods <get_own_log_calls_wrapper-function>`.
They return the wrapper of a method or property decorated by `record_history`, to allow
access to its attributes.


The ``record_history.decorate_*`` classmethods
=================================================

The ``record_history.decorate_*`` classmethods exist, and behave like their `log_calls`
counterparts documented in :ref:`decorating_functions_class_hierarchies_modules`.

-------------------------------------------------------------


.. _record_history-examples:

`record_history` examples
==========================================

Let's finally call the function defined above:

    >>> for x in range(15):
    ...     _ = record_me(3, 5, x)      # "_ = " for doctest

    >>> len(record_me.stats.history)
    15

Some tallies (your mileage may vary for ``elapsed_secs_logged``):

    >>> record_me.stats.num_calls_logged
    15
    >>> record_me.stats.num_calls_total
    15
    >>> record_me.stats.elapsed_secs_logged          # doctest: +SKIP
    2.2172927856445312e-05

Call history in CSV format, with ellipses for 'elapsed_secs', 'process_secs' and 'timestamp' columns:

    >>> print(record_me.stats.history_as_csv)         # doctest: +ELLIPSIS
    call_num|a|b|x|retval|elapsed_secs|process_secs|timestamp|prefixed_fname|caller_chain
    1|3|5|0|5|...|...|...|'record_me'|['<module>']
    2|3|5|1|8|...|...|...|'record_me'|['<module>']
    3|3|5|2|11|...|...|...|'record_me'|['<module>']
    4|3|5|3|14|...|...|...|'record_me'|['<module>']
    5|3|5|4|17|...|...|...|'record_me'|['<module>']
    6|3|5|5|20|...|...|...|'record_me'|['<module>']
    7|3|5|6|23|...|...|...|'record_me'|['<module>']
    8|3|5|7|26|...|...|...|'record_me'|['<module>']
    9|3|5|8|29|...|...|...|'record_me'|['<module>']
    10|3|5|9|32|...|...|...|'record_me'|['<module>']
    11|3|5|10|35|...|...|...|'record_me'|['<module>']
    12|3|5|11|38|...|...|...|'record_me'|['<module>']
    13|3|5|12|41|...|...|...|'record_me'|['<module>']
    14|3|5|13|44|...|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|...|'record_me'|['<module>']
    <BLANKLINE>

Disable recording, and call the function one more time:

    >>> record_me.record_history_settings.enabled = False
    >>> _ = record_me(583, 298, 1000)

The call numbers of the last 2 calls to `record_me` remain ``14`` and ``15``:

    >>> list(map(lambda rec: rec.call_num, record_me.stats.history[-2:]))
    [14, 15]

Here are the call counters:

    >>> record_me.stats.num_calls_logged
    15
    >>> record_me.stats.num_calls_total
    16

Re-enable recording and call the function again, once:

    >>> record_me.record_history_settings.enabled = True
    >>> _ = record_me(1900, 2000, 20)

Here are the last 3 lines of the CSV call history:

    >>> lines = record_me.stats.history_as_csv.strip().split('\\n')
    >>> # Have to skip next test in .md
    >>> #  because doctest doesn't split it at all: len(lines) == 1
    >>> for line in lines[-3:]:                   # doctest: +ELLIPSIS, +SKIP
    ...     print(line)
    14|3|5|13|44|...|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|...|'record_me'|['<module>']
    16|1900|2000|20|40000|...|...|...|'record_me'|['<module>']

and here are the updated call counters:

    >>> record_me.stats.num_calls_logged
    16
    >>> record_me.stats.num_calls_total
    17

Finally, let's call ``stats.clear_history()``, setting ``max_history`` to 3,
call ``record_me`` 15 times, and examine the call history again:

    >>> record_me.stats.clear_history(max_history=3)
    >>> for x in range(15):
    ...     _ = record_me(3, 5, x)
    >>> print(record_me.stats.history_as_csv)      # doctest: +ELLIPSIS
    call_num|a|b|x|retval|elapsed_secs|process_secs|timestamp|prefixed_fname|caller_chain
    13|3|5|12|41|...|...|...|'record_me'|['<module>']
    14|3|5|13|44|...|...|...|'record_me'|['<module>']
    15|3|5|14|47|...|...|...|'record_me'|['<module>']
    <BLANKLINE>

