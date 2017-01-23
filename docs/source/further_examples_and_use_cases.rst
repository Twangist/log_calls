.. _further_examples_and_use_cases:

Further Examples and Use Cases
##################################

This chapter collects several longer examples that demonstrate techniques
and not just individual features of `log_calls`.


.. _enabling-with-ints:

Using ``enabled`` as a level of verbosity
=================================================

Sometimes it's desirable for a function to print or log debugging messages
as it executes. It's the oldest form of debugging! The ``enabled`` parameter
is in fact an ``int``, not just a ``bool``. Instead of giving it a simple ``bool``
value, you can use a nonnegative ``int`` and treat it as a verbosity level:

    >>> DEBUG_MSG_BASIC = 1
    >>> DEBUG_MSG_VERBOSE = 2
    >>> DEBUG_MSG_MOREVERBOSE = 3  # etc.
    >>> @log_calls(enabled='debuglevel')
    ... def do_stuff_with_commentary(*args, debuglevel=0):
    ...     if debuglevel >= DEBUG_MSG_VERBOSE:
    ...         print("*** extra debugging info ***")

No output:

    >>> do_stuff_with_commentary()

Only `log_calls` output:

    >>> do_stuff_with_commentary(debuglevel=DEBUG_MSG_BASIC)
    do_stuff_with_commentary <== called by <module>
        arguments: debuglevel=1
    do_stuff_with_commentary ==> returning to <module>

`log_calls` output plus the function's debugging reportage:

    >>> do_stuff_with_commentary(debuglevel=DEBUG_MSG_VERBOSE)
    do_stuff_with_commentary <== called by <module>
        arguments: debuglevel=2
    *** extra debugging info ***
    do_stuff_with_commentary ==> returning to <module>

The metaclass example later in this chapter also uses this technique,
and writes its messages with the :ref:`log_calls.print() <log_message_method>` method.

.. _recursion-example:

Indentation and call numbers with recursion
===============================================

Setting ``log_call_numbers`` to true is especially useful in with recursive, mutually recursive
and reentrant callables. In this example, the function ``depth`` computes the *depth* of a dictionary
(a non-dict has depth = 0, and a dict has depth = 1 + the max of the depths of its values):

    >>> from collections import OrderedDict
    >>> @log_calls(log_call_numbers=True, log_retval=True)
    >>> def depth(d, key=None):
    ...     """Middle line (elif) is needed only because
    ...     max(empty_sequence) raises ValueError
    ...     (whereas returning 0 would be sensible and even expected)
    ...     """
    ...     if not isinstance(d, dict): return 0    # base case
    ...     elif not d:                 return 1
    ...     else:                       return max(map(depth, d.values(), d.keys())) + 1

Now we call ``depth`` with a nested ``OrderedDict``:

    >>> depth(
    ...     OrderedDict(
    ...         (('a', 0),
    ...          ('b', OrderedDict( (('c1', 10), ('c2', 11)) )),
    ...          ('c', 'text'))
    ...     )
    ... )
    depth [1] <== called by <module>
        arguments: d=OrderedDict([('a', 0), ('b', OrderedDict([('c1', 10), ('c2', 11)])), ('c', 'text')])
        defaults:  key=None
        depth [2] <== called by depth [1]
            arguments: d=0, key='a'
            depth [2] return value: 0
        depth [2] ==> returning to depth [1]
        depth [3] <== called by depth [1]
            arguments: d=OrderedDict([('c1', 10), ('c2', 11)]), key='b'
            depth [4] <== called by depth [3]
                arguments: d=10, key='c1'
                depth [4] return value: 0
            depth [4] ==> returning to depth [3]
            depth [5] <== called by depth [3]
                arguments: d=11, key='c2'
                depth [5] return value: 0
            depth [5] ==> returning to depth [3]
            depth [3] return value: 1
        depth [3] ==> returning to depth [1]
        depth [6] <== called by depth [1]
            arguments: d='text', key='c'
            depth [6] return value: 0
        depth [6] ==> returning to depth [1]
        depth [1] return value: 2
    depth [1] ==> returning to <module>
    2

The three calls ``depth [2]``, ``depth [3]``, and ``depth [6]`` handle
the three items of the dictionary passed to ``depth [1]``; they return
``0``, ``1``, and ``0`` respectively. Finally ``depth [1]`` returns 1 plus
the ``max`` of those values.

.. note::
 The optional ``key`` parameter is for instructional purposes,
 so you can see the key that's paired with the value of ``d`` in the caller's
 dictionary. Typically the signature of this function would be just ``def depth(d)``,
 and the recursive case would return ``1 + max(map(depth, d.values()))``.

.. _logging-multiple-handlers-example:

Using a logger with multiple handlers that have different loglevels
================================================================================

First let's set up a logger with a console handler that writes to ``stdout``:

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> c_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    >>> ch.setFormatter(c_formatter)
    >>> logger = logging.getLogger('mylogger')
    >>> logger.addHandler(ch)
    >>> logger.setLevel(logging.DEBUG)

Now let's add another handler, also sent to ``stdout`` for the sake of the example
but best thought of as writing to a log file. We'll set up the existing console handler
with level ``INFO``, and the "file" handler with level ``DEBUG`` – a typical setup: you want
to log all details to the file, but you only want to write more important messages to
the console.

    >>> fh = logging.StreamHandler(stream=sys.stdout)
    >>> f_formatter = logging.Formatter('[FILE] %(levelname)8s:%(name)s: %(message)s')
    >>> fh.setFormatter(f_formatter)
    >>> fh.setLevel(logging.DEBUG)
    >>> logger.addHandler(fh)
    >>> ch.setLevel(logging.INFO)

Suppose we have two functions: one that's lower-level/often-called,
and another that's higher-level/infrequently called. It's appropriate
to give the infrequently called function a higher ``loglevel``:

    >>> @log_calls(logger=logger, loglevel=logging.DEBUG)
    ... def popular(): pass
    >>> @log_calls(logger=logger, loglevel=logging.INFO)
    ... def infrequent(): popular()

Set the log level to ``logging.DEBUG`` – the console handler logs calls
only for ``infrequent``, but the "file" handler logs calls for both functions:

    >>> logger.setLevel(logging.DEBUG)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    INFO:mylogger:infrequent <== called by <module>
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    [FILE]    DEBUG:mylogger: popular <== called by infrequent
    [FILE]    DEBUG:mylogger: popular ==> returning to infrequent
    INFO:mylogger:infrequent ==> returning to <module>
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>

Now set log level to ``logging.INFO`` – both handlers logs calls only for ``infrequent``:

    >>> logger.setLevel(logging.INFO)
    >>> infrequent()       # doctest: +NORMALIZE_WHITESPACE
    INFO:mylogger:infrequent <== called by <module>
    [FILE]     INFO:mylogger: infrequent <== called by <module>
    INFO:mylogger:infrequent ==> returning to <module>
    [FILE]     INFO:mylogger: infrequent ==> returning to <module>


.. _A-metaclass-example:

A metaclass example
==================================

This example demonstrates a few techniques:

* writing debug messages with ``log_calls.print()``, which handles global indentation for you;
* use of ``enabled`` as an integer level of verbosity.

The following class ``A_meta`` will serve as the metaclass for classes defined subsequently:

    >>> # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    >>> # A_meta, a metaclass
    >>> # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    >>> from collections import OrderedDict
    >>> separator = '\n'    # default ', ' gives rather long lines

    >>> A_DBG_NONE = 0
    >>> A_DBG_BASIC = 1
    >>> A_DBG_INTERNAL = 2

    >>> @log_calls(args_sep=separator, enabled='A_debug=')
    ... class A_meta(type):
    ...     @classmethod
    ...     @log_calls(log_retval=True)
    ...     def __prepare__(mcs, cls_name, bases, **kwargs):
    ...         super_dict = super().__prepare__(cls_name, bases, **kwargs)
    ...         A_debug = kwargs.pop('A_debug', A_DBG_NONE)
    ...         if A_debug >= A_DBG_INTERNAL:
    ...             log_calls.print("    mro =", mcs.__mro__)
    ...             log_calls.print("    dict from super() = %r" % super_dict)
    ...         super_dict = OrderedDict(super_dict)
    ...         super_dict['key-from-__prepare__'] = 1729
    ...         return super_dict
    ...
    ...     def __new__(mcs, cls_name, bases, cls_members: dict, **kwargs):
    ...         cls_members['key-from-__new__'] = "No, Hardy!"
    ...         A_debug = kwargs.pop('A_debug', A_DBG_NONE)
    ...         if A_debug >= A_DBG_INTERNAL:
    ...             log_calls.print("    calling super() with cls_members =", cls_members)
    ...         return super().__new__(mcs, cls_name, bases, cls_members, **kwargs)
    ...
    ...     def __init__(cls, cls_name, bases, cls_members: dict, **kwargs):
    ...         A_debug = kwargs.pop('A_debug', A_DBG_NONE)
    ...         if A_debug >= A_DBG_INTERNAL:
    ...             log_calls.print("    cls.__mro__:", cls.__mro__)
    ...             log_calls.print("    type(cls).__mro__[1] =", type(cls).__mro__[1])
    ...         try:
    ...             super().__init__(cls_name, bases, cls_members, **kwargs)
    ...         except TypeError as e:
    ...             # call type.__init__
    ...             if A_debug >= A_DBG_INTERNAL:
    ...                 log_calls.print("    calling type.__init__ with no kwargs")
    ...             type.__init__(cls, cls_name, bases, cls_members)

The class ``A_meta`` is a metaclass: it derives from ``type``,
and defines (overrides) methods ``__prepare__``, ``__new__`` and ``__init__``.
All of these `log_calls`-decorated methods awrite their messages using the indent-aware
method :ref:`log_calls.print() <log_message_method>`.

All of ``A_meta``'s methods look for an implicit keyword parameter ``A_debug``,
used as the indirect value of the `log_calls` parameter ``enabled``.
The methods treat its value as an integer verbosity level: they write extra messages
when the value of ``A_debug`` is at least ``A_DBG_INTERNAL``.

Rather than make ``A_debug`` an explicit keyword parameter of the metaclass methods,
as in::

    def __prepare__(mcs, cls_name, bases, *, A_debug=0, **kwargs):

instead we have left their signatures agnostic. If ``A_debug`` is passed
by a class definition (as below), the methods use the passed value, and remove
``A_debug`` from ``kwargs``; otherwise they use a default value ``A_DBG_NONE``,
which is less than their threshold value for writing debug messages.

When we include ``A_debug=A_DBG_INTERNAL`` as a keyword argument to a class that
uses ``A_meta`` as its metaclass, that argument gets passed to all of
``A_meta``'s methods, so not only will calls to the metaclass methods be logged,
but those methods will also print extra debugging information:

    >>> class A(metaclass=A_meta, A_debug=A_DBG_INTERNAL):    # doctest: +NORMALIZE_WHITESPACE
    ...     pass
    A_meta.__prepare__ <== called by <module>
        arguments:
            mcs=<class '__main__.A_meta'>
            cls_name='A'
            bases=()
            **kwargs={'A_debug': 2}
            mro = (<class '__main__.A_meta'>, <class 'type'>, <class 'object'>)
            dict from super() = {}
        A_meta.__prepare__ return value: OrderedDict([('key-from-__prepare__', 1729)])
    A_meta.__prepare__ ==> returning to <module>
    A_meta.__new__ <== called by <module>
        arguments:
            mcs=<class '__main__.A_meta'>
            cls_name='A'
            bases=()
            cls_members=OrderedDict([('key-from-__prepare__', 1729),
                                     ('__module__', '__main__'),
                                     ('__qualname__', 'A')])
            **kwargs={'A_debug': 2}
            calling super() with cls_members = OrderedDict([('key-from-__prepare__', 1729),
                                                            ('__module__', '__main__'),
                                                            ('__qualname__', 'A'),
                                                            ('key-from-__new__', 'No, Hardy!')])
    A_meta.__new__ ==> returning to <module>
    A_meta.__init__ <== called by <module>
        arguments:
            cls=<class '__main__.A'>
            cls_name='A'
            bases=()
            cls_members=OrderedDict([('key-from-__prepare__', 1729),
                                     ('__module__', '__main__'),
                                     ('__qualname__', 'A'),
                                     ('key-from-__new__', 'No, Hardy!')])
            **kwargs={'A_debug': 2}
            cls.__mro__: (<class '__main__.A'>, <class 'object'>)
            type(cls).__mro__[1] = <class 'type'>
    A_meta.__init__ ==> returning to <module>

If we had passed ``A_debug=A_DBG_BASIC``, then only `log_calls` output would have
been printed: the metaclass methods would not have printed their extra debugging
statements.

If we pass ``A_debug=0`` (or omit the parameter), we get no printed output at all,
either from `log_calls` or from ``A_meta``'s methods:

    >>> class AA(metaclass=A_meta, A_debug=False):  # no output
    ...     pass

    >>> class AAA(metaclass=A_meta):                # no output
    ...     pass

**Note**: This example is from the docstring of the function ``main__metaclass_example()`` in ``tests/test_log_calls.py``.
In that module, we perform a fixup to the docstring which changes ``'__main__'`` to ``__name__``,
so that the test works no matter how it's invoked.
