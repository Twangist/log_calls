.. _Logging:

Using Loggers
###############

`log_calls` works well with loggers obtained from Python's ``logging`` module,
objects of type ``logging.Logger``. If you use the ``logger`` keyword parameter,
`log_calls` will write to the specified logger rather than to a file or stream using
``print``.

We'll need a logger for the examples of this chapter — a simple one
with a single handler that writes to the console. Because `doctest` doesn't capture
output written to ``stderr`` (the default stream to which console handlers write),
we'll send the console handler's output to ``stdout``, using the format
``<loglevel>:<loggername>:<message>``.

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> c_formatter = logging.Formatter('%(levelname)8s:%(name)s:%(message)s')
    >>> ch.setFormatter(c_formatter)
    >>> logger = logging.getLogger('a_logger')
    >>> logger.addHandler(ch)
    >>> logger.setLevel(logging.DEBUG)

.. _logger-parameter:

The ``logger`` keyword parameter (default: ``None``)
========================================================

The ``logger`` keyword parameter tells `log_calls` to write its output using
that logger rather than to the ``file`` setting using the ``print`` function.
If the ``logger`` setting is nonempty, it takes precedence over ``file``.
The value of ``logger`` can be either a logger instance (a ``logging.Logger``)
or a string giving the name of a logger, which will be passed to ``logging.getLogger()``.

    >>> @log_calls(logger=logger)
    ... def somefunc(v1, v2):
    ...     logger.debug(v1 + v2)
    >>> somefunc(5, 16)             # doctest: +NORMALIZE_WHITESPACE
    DEBUG:a_logger:somefunc <== called by <module>
    DEBUG:a_logger:    arguments: v1=5, v2=16
    DEBUG:a_logger:21
    DEBUG:a_logger:somefunc ==> returning to <module>

Instead of passing the logger instance as above, we can simply pass its name, ``'a_logger'``:

    >>> @log_calls(logger='a_logger', indent=False)
    ... def anotherfunc():
    ...     somefunc(17, 19)
    >>> anotherfunc()               # doctest: +NORMALIZE_WHITESPACE
    DEBUG:a_logger:anotherfunc <== called by <module>
    DEBUG:a_logger:somefunc <== called by anotherfunc
    DEBUG:a_logger:    arguments: v1=17, v2=19
    DEBUG:a_logger:36
    DEBUG:a_logger:somefunc ==> returning to anotherfunc
    DEBUG:a_logger:anotherfunc ==> returning to <module>

This works because

    "all calls to ``logging.getLogger(name)`` with a given name
    return the same logger instance", so that "logger instances
    never need to be passed between different parts of an application".

    -- Python documentation for `logging.getLogger() <https://docs.python.org/3/library/logging.html?highlight=logging.getlogger#logging.getLogger>`_.


.. note:: If the value of ``logger`` is a ``Logger`` instance that has no handlers
 (which can happen if you specify a logger name for a (theretofore) nonexistent logger),
 that logger won't be able to write anything, so `log_calls` will fall back to ``print``.

.. _loglevel-parameter:

The ``loglevel`` keyword parameter (default: ``logging.DEBUG``)
=====================================================================

`log_calls` also takes a ``loglevel`` keyword parameter, an ``int`` whose value must be
one of the ``logging`` module's constants - ``logging.DEBUG``, ``logging.INFO``, etc.
– or a custom logging level if you've added any. `log_calls` writes output messages
using ``logger.log(loglevel, …)``. Thus, if the ``logger``'s log level is higher than
``loglevel``, no output will appear:

    >>> logger.setLevel(logging.INFO)   # raise logger's level to INFO
    >>> @log_calls(logger='a_logger', loglevel=logging.DEBUG)
    ... def f(x, y, z):
    ...     return y + z
    >>> # No log_calls output from f
    >>> # because loglevel for f < level of logger
    >>> f(1,2,3)                        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    5


.. _logging-further-examples:

Where to find further examples
================================

A realistic example can be found in :ref:`logging-multiple-handlers-example`.

Yet more examples appear in the docstrings of the function

    ``main_logging()``

in ``test_log_calls.py``, and of the functions

    ``main__more_on_logging__more()``,
    ``main__logging_with_indent__minimal_formatters()``, and
    ``main__log_message__all_possible_output_destinations()``

in ``test_log_calls_more.py``.
