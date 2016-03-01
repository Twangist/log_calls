.. _keyword_parameters:

Keyword Parameters
####################

`log_calls` has many features, and thus many, mostly independent, keyword parameters (21 in release |release|).
This section covers most of them thoroughly, one at a time (though of course you can use
multiple parameters in any call to the decorator):

* :ref:`enabled <enabled-parameter>`
* :ref:`args_sep <args_sep-parameter>`
* :ref:`log_args <log_args-parameter>`
* :ref:`log_retval <log_retval-parameter>`
* :ref:`log_exit <log_exit-parameter>`
* :ref:`log_call_numbers <log_call_numbers-parameter>`
* :ref:`log_elapsed <log_elapsed-parameter>`
* :ref:`indent <indent-parameter>`
* :ref:`name <name-parameter>`
* :ref:`prefix <prefix-parameter>`
* :ref:`file <file-parameter>`
* :ref:`mute <mute-parameter>` (also discusses the global mute switch ``log_calls.mute``)
* :ref:`settings <settings-parameter>`
* :ref:`NO_DECO <NO_DECO-parameter>`
* :ref:`override <override-parameter>`

The remaining parameters are fully documented in later chapters,
For completeness, they're briefly introduced at the end of this chapter,
together with links to their actual documentation.

* :ref:`omit, only <omit-only-brief>`
* :ref:`logger, loglevel <logger-loglevel-brief>`
* :ref:`record_history, max_history <record_history-max_history-brief>`


.. _what-is-a-setting:

What is a *setting*?
============================

When `log_calls` decorates a callable (a function, method, property, ...), it "wraps" that
callable in a function — the *wrapper* of the callable. Subsequently, calls to the decorated
callable actually call the wrapper, which delegates to the original, in between its own
pre- and post-processing. This is simply what decorators do.

`log_calls` gives the wrapper a few attributes pertaining to the wrapped callable, notably
``log_calls_settings``, a dict-like object that contains the `log_calls` state of the callable.
The keys of ``log_calls_settings`` are `log_calls` keyword parameters, such as ``enabled`` and
``log_retval`` — in fact, most of the keyword parameters, though not all of them.

.. index:: setting

**The** *settings of a decorated callable* **are the key/value pairs of its**
``log_calls_settings`` **object, which is an attribute of the callable's wrapper.**
The settings comprise the `log_calls` state of the callable.

Initially the value of a setting is the value passed to the `log_calls` decorator for
the corresponding keyword parameter, or the default value for that parameter if no
argument was supplied for it. ``log_calls_settings`` can then be used to read *and write*
settings values.

``log_calls_settings`` is documented in :ref:`log_calls_settings-obj`.

.. topic:: Usage of "setting"

    We also use the term "settings" to refer to the keys of ``log_calls_settings``,
    as well as to its key/value pairs. For example,

        "the ``indent`` setting",

    or

        "``enabled`` is a setting, but ``override`` is not".

    This overloading shouldn't cause any confusion.

.. _the-settings:

The "settings"
---------------------
The following keyword parameters are settings:

    ``enabled``
    ``args_sep``
    ``log_args``
    ``log_retval``
    ``log_exit``
    ``log_call_numbers``
    ``log_elapsed``
    ``indent``
    ``prefix``
    ``file``
    ``mute``
    ``logger``
    ``loglevel``
    ``record_history``
    ``max_history``

As described in the chapter :ref:`dynamic_control_of_settings`, all of a decorated callable's
settings can be accessed through ``log_calls_settings``, and almost all can be changed
on the fly.

.. _the-non-settings:

The non-settings
-----------------------

The other keyword parameters are *not* settings:

    ``NO_DECO``
    ``settings``
    ``name``
    ``override``
    ``omit``
    ``only``

These are directives to the decorator telling it how to initialize itself. Their initial values
are not subsequently available via attributes of the wrapper, and cannot subsequently be changed.

.. Slight lie above: extended versions of `omit` and `only` *are* actually available
   as attributes of the  wrapper, but at present (v0.3.0) they are not officially
   part of the API. Those retained attributes are not used by `log_calls` "at runtime";
   presently they're used only in a few tests (≤ a half dozen).

--------------------------------------------------------------------

.. _enabled-parameter:

``enabled`` (default: ``True`` ( ``== 1``) )
=========================================================

Every example of `log_calls` that we've seen so far has produced output,
as they have all used the default value ``True`` of the ``enabled`` parameter.
Passing ``enabled=False`` to the decorator suppresses output:

    >>> @log_calls(enabled=False)
    ... def f(a, b, c):
    ...     pass
    >>> f(1, 2, 3)                # no output

This is not totally pointless!, because, as with almost all `log_calls` settings,
you can dynamically change the "enabled" state for a particular function or method.
(Later chapters :ref:`decorating_functions_class_hierarchies_modules` and
:ref:`dynamic_control_of_settings` show ways to do so that could change this
``enabled`` setting.) The above decorates ``f`` and sets its *initial* "enabled" state
to ``False``.

.. note::
 The ``enabled`` setting is in fact an ``int``. This can be used advantageously.

 See the examples :ref:`enabling-with-ints` and :ref:`A-metaclass-example`,
 which illustrate using different positive values to specify increasing levels
 of verbosity in `log_calls`-related output.

.. _enabled-as-bypass:

Bypass
----------------------------

If you supply a negative integer as the value of ``enabled``, that is interpreted as *bypass*: `log_calls`
immediately calls the decorated callable and returns its value. When the value
of ``enabled`` is false (``False`` or ``0``), the decorator performs a little more processing
than that before it delegates to the decorated callable (it increments the number of the call, for example),
though of course less than when ``enabled`` is positive (e.g. ``True``).

--------------------------------------------------------------------

.. _args_sep-parameter:

``args_sep`` (default: ``', '``)
===================================

The ``args_sep`` parameter specifies the string used to separate arguments. If the string ends in
(or is) ``\n``, additional whitespace is appended so that arguments line up nicely:

    >>> @log_calls(args_sep='\\n')
    ... def f(a, b, c, **kwargs):
    ...     print(a + b + c)
    >>> f(1, 2, 3, u='you')       # doctest: +NORMALIZE_WHITESPACE, +SKIP
    f <== called by <module>
        arguments:
            a=1
            b=2
            c=3
            **kwargs={'u': 'you'}
    6
    f ==> returning to <module>

.. topic:: A `doctest` quirk

    The `doctest` examples in this document use ``'\\n'``
    where in actual code you'd write ``'\n'``. All
    the examples herein work (as tests, they pass), but they would fail if
    ``'\n'`` were used.

--------------------------------------------------------------------

.. _log_args-parameter:

``log_args`` (default: ``True``)
===================================

When true, as seen in all examples so far, arguments passed to the decorated callable
are written together with their values. If the callable's signature contains positional
and/or keyword "varargs", those are included if they're nonempty. (These are conventionally named
``*args`` and ``**kwargs``, but `log_calls` will use the parameter names that actually appear in
the callable's definition.) Any default values of keyword parameters with no corresponding argument
are also logged, on a separate line:

    >>> @log_calls()
    ... def f_a(a, *args, something='that thing', **kwargs): pass
    >>> f_a(1, 2, 3, foo='bar')
    f_a <== called by <module>
        arguments: a=1, *args=(2, 3), **kwargs={'foo': 'bar'}
        defaults:  something='that thing'
    f_a ==> returning to <module>

Here, no argument information is logged at all:

    >>> @log_calls(log_args=False)
    ... def f_b(a, *args, something='that thing', **kwargs): pass
    >>> f_b(1, 2, 3, foo='bar')
    f_b <== called by <module>
    f_b ==> returning to <module>

If a callable has no parameters, `log_calls` won't display any "arguments" section:

    >>> @log_calls()
    ... def f(): pass
    >>> f()
    f <== called by <module>
    f ==> returning to <module>

If a callable has parameters but is passed no arguments, `log_calls`
will display ``arguments: <none>``, plus any default values used:

    >>> @log_calls()
    ... def ff(*args, **kwargs): pass
    >>> ff()
    ff <== called by <module>
        arguments: <none>
    ff ==> returning to <module>

    >>> @log_calls()
    ... def fff(*args, kw='doh', **kwargs): pass
    >>> fff()
    fff <== called by <module>
        arguments: <none>
        defaults:  kw='doh'
    fff ==> returning to <module>

--------------------------------------------------------------------

.. _log_retval-parameter:

``log_retval`` (default: ``False``)
========================================

When this setting is true, values returned by a decorated callable are reported:

    >>> @log_calls(log_retval=True)
    ... def f(a, b, c):
    ...     return a + b + c
    >>> _ = f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3
        f return value: 6
    f ==> returning to <module>

.. note::
    By default, `log_calls` suppresses the return value of ``__init__`` methods,
    even when ``log_retval=True`` has been passed to a decorator of the method's
    class. To override this, you must decorate ``__init__`` itself and supply
    ``log_retval=True``.

--------------------------------------------------------------------

.. _log_exit-parameter:

``log_exit`` (default: ``True``)
========================================

When false, this parameter suppresses the ``... ==> returning to ...`` line
that indicates the callable's return to its caller:

    >>> @log_calls(log_exit=False)
    ... def f(a, b, c):
    ...     return a + b + c
    >>> _ = f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3

--------------------------------------------------------------------

.. _log_call_numbers-parameter:

``log_call_numbers`` (default: ``False``)
================================================

`log_calls` keeps a running tally of the number of times a decorated callable
has been called. You can display this (1-based) number using the ``log_call_numbers``
parameter:

    >>> @log_calls(log_call_numbers=True)
    ... def f(): pass
    >>> for i in range(2): f()
    f [1] <== called by <module>
    f [1] ==> returning to <module>
    f [2] <== called by <module>
    f [2] ==> returning to <module>

The call number is also displayed with the function name when ``log_retval`` is true:

    >>> @log_calls(log_call_numbers=True, log_retval=True)
    ... def f():
    ...     return 81
    >>> _ = f()
    f [1] <== called by <module>
        f [1] return value: 81
    f [1] ==> returning to <module>


The display of call numbers is particularly valuable in the presence of recursion or reentrance —
see the example :ref:`recursion-example`, where the feature is used to good effect.

.. topic:: Resetting the next call number to 1

    To reset the next call number of a decorated function ``f`` to 1, call the ``f.stats.clear_history()``
    method. To reset it to 1 for a callable in a class, call ``wrapper.stats.clear_history()`` where
    ``wrapper`` is the callable's wrapper, obtained via one of the two methods described in
    the section on :ref:`accessing the wrappers of methods <get_own_log_calls_wrapper-function>`.

    See :ref:`clear_history` in the :ref:`call_history_statistics` chapter for details
    about the ``clear_history()`` method and, more generally, the ``stats`` attribute.

--------------------------------------------------------------------

.. _log_elapsed-parameter:

``log_elapsed`` (default: ``False``)
================================================

For performance profiling, you can measure the time a callable took to execute
by using the ``log_elapsed`` parameter. When this setting is true, `log_calls`
reports how long it took the decorated callable to complete, in seconds.
Two measurements are reported:

* *elapsed time* (system-wide, including time elapsed during sleep),
  given by :func:`time.perf_counter`, and
* *process time* (system + CPU time, i.e. kernel + user time, sleep time excluded),
  given by :func:`time.process_time`.

    >>> @log_calls(log_elapsed=True)
    ... def f(n):
    ...     for i in range(n):
    ...         # do something nontrivial...
    ...         pass
    >>> f(5000)                                 # doctest: +ELLIPSIS
    f <== called by <module>
        arguments: n=5000
        elapsed time: ... [secs], process time: ... [secs]
    f ==> returning to <module>

--------------------------------------------------------------------

.. _indent-parameter:

``indent`` (default: ``True``)
================================================

The ``indent`` parameter, when true, indents each new level of logged messages by 4 spaces,
providing a visualization of the call hierarchy.

A decorated callable's logged output is indented only as much as is necessary.
Here, the even numbered functions don't indent, so the indented functions that
they call are indented just one level more than their "inherited" indentation level:

    >>> @log_calls()
    ... def g1():
    ...     pass
    >>> @log_calls(indent=False)    # no extra indentation for g2
    ... def g2():
    ...     g1()
    >>> @log_calls()
    ... def g3():
    ...     g2()
    >>> @log_calls(indent=False)    # no extra indentation for g4
    ... def g4():
    ...     g3()
    >>> @log_calls()
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
    g4 <== called by g5
        g3 <== called by g4
        g2 <== called by g3
            g1 <== called by g2
            g1 ==> returning to g2
        g2 ==> returning to g3
        g3 ==> returning to g4
    g4 ==> returning to g5
    g5 ==> returning to <module>

--------------------------------------------------------------------

.. _name-parameter:

``name`` (default: ``''``)
================================================

.. index:: display name

The ``name`` parameter lets you change the "display name" of a decorated callable.
The *display name* is the name by which `log_calls` refers to the callable,
in these contexts:

* when logging a call to, and a return from, the callable
* when reporting its return value
* when it's in a :ref:`call chain <call_chains>`.

A value provided for the ``name`` parameter should be a string, of one of the following forms:

* the preferred name of the callable (a string literal), or
* an old-style format string with just one occurrence of ``%s``,
  which the ``__name__`` of the decorated callable will replace.

For example:

    >>> @log_calls(name='f (STUB)')
    ... def f(): pass
    >>> f()
    f (STUB) <== called by <module>
    f (STUB) ==> returning to <module>

Another simple example:

    >>> @log_calls(name='"%s" (lousy name)', log_exit=False)
    ... def g(): pass
    >>> g()
    "g" (lousy name) <== called by <module>

This parameter is useful mainly to simplify the display names of inner functions,
and to disambiguate the display names of *getter* and *deleter* property methods.

.. topic:: Example — using ``name`` with an inner function

    The qualified names of inner functions are ungainly – in the following example,
    the "qualname" of ``inner`` is ``outer.<locals>.inner``:

        >>> @log_calls()
        ... def outer():
        ...     @log_calls()
        ...     def inner(): pass
        ...     inner()
        >>> outer()
        outer <== called by <module>
            outer.<locals>.inner <== called by outer
            outer.<locals>.inner ==> returning to outer
        outer ==> returning to <module>

    You can use the ``name`` parameter to simplify the displayed name of the inner function:

        >>> @log_calls()
        ... def outer():
        ...     @log_calls(name='%s')
        ...     def inner(): pass
        ...     inner()
        >>> outer()
        outer <== called by <module>
            inner <== called by outer
            inner ==> returning to outer
        outer ==> returning to <module>

See :ref:`this <using-name-with-setter-deleter>` section on using the ``name`` parameter
with *setter* and *deleter* property methods, which demonstrates the use of ``name``
to distinguish the methods of properties defined with ``@property`` decorators.

--------------------------------------------------------------------

.. _prefix-parameter:

``prefix`` (default: ``''``)
================================================

The `prefix` keyword parameter lets you specify a string with which to prefix the name
of a callable, thus giving it a new display name.

Here's a simple example:

    >>> @log_calls(prefix='--- ')
    ... def f(): pass
    >>> f()
    --- f <== called by <module>
    --- f ==> returning to <module>

Because versions 0.3.0+ of `log_calls` use  ``__qualname__`` for the display name of
decorated callables, what had been the main use case for ``prefix`` — prefixing method names
with their class name — has gone away. Furthermore, clearly the ``name`` parameter can produce any
display name that ``prefix`` can. However, ``prefix`` is not deprecated, at least not presently:
for what it's worth, it *is* a setting and can be changed dynamically, neither of which is true of ``name``.

--------------------------------------------------------------------

.. _file-parameter:

``file`` (default: ``sys.stdout``)
================================================

The ``file`` parameter specifies a stream (an instance of :class:`io.TextIOBase`) to which `log_calls`
will print its messages. This value is supplied to the ``file`` keyword parameter of the ``print``
function, which has the same default value. This parameter is ignored if you've supplied a logger
for output using the :ref:`logger <logger-parameter>` parameter.

When the output stream is the default ``sys.stdout``, `log_calls` always uses the current meaning
of that expression to obtain its output stream, not just what "sys.stdout" meant at program
initialization. Your program can capture, change and redirect ``sys.stdout``, and `log_calls` will
write to that stream, whatever it currently is. (`doctest` is a good example of a program which
manipulates ``sys.stdout`` dynamically.)

If your program writes to the console a lot, you may not want `log_calls` messages interspersed
with your real output: your understanding of both logically distinct streams might be hindered,
and it may be better to make them two actually distinct streams. Splitting off the `log_calls`
output can also be useful for understanding or for creating documentation: you can gather all,
and only all, of the `log_calls` messages in one place. The ``indent`` setting will be respected,
whether messages go to the console or to a file.

It's not easy to test this feature with `doctest`, so we'll just give an example of writing to
``sys.stderr``, and then reproduce the output::

    import sys
    @log_calls(file=sys.stderr)
    def f(n):
        if n <= 0:
            return 'a'
        return '(%s)' % f(n-1)

Calling ``f(2)`` returns ``'((a))'`` and writes the following to ``sys.stderr``::

    f <== called by <module>
        arguments: n=2
        f <== called by f
            arguments: n=1
            f <== called by f
                arguments: n=0
            f ==> returning to f
        f ==> returning to f
    f ==> returning to <module>


--------------------------------------------------------------------

.. _mute-parameter:

``mute`` (default: ``log_calls.MUTE.NOTHING``)
================================================

The `mute` parameter gives you control over `log_calls` output from a given decorated callable.
It can take any of the following three numeric values, shown here in increasing order:

:``log_calls.MUTE.NOTHING``:   (default) doesn't mute any output
:``log_calls.MUTE.CALLS``:     mutes all logging of function/method call details,
                               but the output of any calls to the methods :ref:`log_message() <log_message_method>`
                               and :ref:`log_exprs() <log_exprs_method>` is allowed through
:``log_calls.MUTE.ALL``:       mutes all output of `log_calls`.

``mute`` is a *setting* — part of the state maintained for a decorated callable —
and can be changed dynamically.

Examples are best deferred until the ``log_message()`` method has been discussed:
see :ref:`indent_aware_writing_methods-mute`.

The ``mute`` parameter lets `log_calls` behave just like the `record_history` decorator,
collecting statistics silently which are accessible via the ``stats`` attribute of
a decorated callable. See :ref:`record_history_deco` for a precise statement of the analogy;
see the tests/examples in ``tests/test_log_calls_as_record_history`` for illustration.


.. index:: log_calls.mute (log_calls class data attribute)

.. _global_mute:

The global mute switch ``log_calls.mute`` (default: ``log_calls.MUTE.NOTHING``)
----------------------------------------------------------------------------------

In addition to the ``mute`` settings maintained for each decorated callable, `log_calls`
also has a single class attribute ``log_calls.mute``. It can assume the same three
values ``log_calls.MUTE.NOTHING``, ``log_calls.MUTE.CALLS``, and ``log_calls.MUTE.ALL``.
Before each write originating from a call to a decorated callable, `log_calls` uses
the max of ``log_calls.mute`` and the callable's ``mute`` setting to determine whether
to output anything. Thus, realtime changes to ``log_calls.mute`` take effect immediately.

To see this in action, refer to :ref:`indent_aware_writing_methods-mute`.

--------------------------------------------------------------------

.. _settings-parameter:

``settings`` (default: ``None``)
================================================

The ``settings`` parameter lets you collect common values for keyword parameters
in one place and pass them to `log_calls` with a single parameter.
``settings`` is a useful shorthand if you have, for example, a module with several
`log_calls`-decorated functions, all with multiple, mostly identical settings
which differ from `log_calls`'s defaults. Instead of repeating multiple identical
settings across several uses of the decorator, a tedious and error-prone practice,
you can gather them all into one ``dict`` or text file, and use the ``settings``
parameter to concisely specify them all *en masse*. You can use different groups
of settings for different sets of functions, or classes, or modules — you're
free to organize them as you please.

When not ``None``, the ``settings`` parameter can be either a ``dict``, or a ``str``
specifying the location of a *settings file* — a text file containing *key=value* pairs and optional comments.
(Details about settings files, their location and their format appear below, in :ref:`settings-as-str`.)
In either case, the valid keys are :ref:`the keyword parameters that are "settings" <the-settings>`
(as defined in :ref:`what-is-a-setting`) plus, as a convenience, ``NO_DECO``.
*Invalid keys are ignored.*

The values of settings specified in the dictionary or settings file override `log_calls`'s
default values for those settings, and any of the resulting settings are in turn overridden
by corresponding keywords passed directly to the decorator. Of course, you *don't* have to provide
a value for every valid key.

.. note::
    The values can also be *indirect values* for parameters that allow indirection
    (almost all do), as described in the chapter :ref:`indirect_values`.

.. index:: settings dict

.. _settings-as-dict:

``settings`` as a ``dict``
----------------------------

The value of ``settings`` can be a ``dict``, or more generally any object ``d`` for which
it's true that ``isinstance(d, dict)``. A simple example should suffice. Here is a
settings ``dict`` and two `log_calls`-decorated functions using it:

    >>> d = dict(
    ...     args_sep=' | ',
    ...     log_args=False,
    ...     log_call_numbers=True,
    ... )
    >>> @log_calls(settings=d)
    ... def f(n):
    ...     if n <= 0: return
    ...     f(n-1)

    >>> @log_calls(settings=d, log_args=True)
    ... def g(s, t): print(s + t)

    >>> f(2)
    f [1] <== called by <module>
        f [2] <== called by f [1]
            f [3] <== called by f [2]
            f [3] ==> returning to f [2]
        f [2] ==> returning to f [1]
    f [1] ==> returning to <module>

    >>> g('aaa', 'bbb')
    g [1] <== called by <module>
        arguments: s='aaa' | t='bbb'
    aaabbb
    g [1] ==> returning to <module>



.. index:: settings file

.. _settings-as-str:

``settings`` as a pathname (``str``)
------------------------------------------

When the value of the ``settings`` parameter is a ``str``, it must be a path to a
*settings file* — a text file containing *key=value* pairs and optional comments.
If the pathname is just a directory, `log_calls` looks there for a file
named ``.log_calls`` and uses that as a settings file; if the pathname is a file,
`log_calls` uses that file. In either case, if the file doesn't exist then no error
results *nor is any warning issued*, and the ``settings`` parameter is ignored.

.. _format-of-a-settings-file:

.. topic:: Format of a settings file

    A *settings file* is a text file containing zero or more lines of the form

        *setting_name*\ ``=``\ *value*

    Whitespace is permitted around *setting_name* and *value*, and is stripped.
    Blank lines are ignored, as are lines whose first non-whitespace character is ``#``,
    which therefore you can use as comments.

    Here are the allowed "direct" values for settings:

    +-----------------------+------------------------------------------------------+
    || Setting              || Allowed "direct" value                              |
    +=======================+======================================================+
    || ``log_args``         || boolean                                             |
    || ``log_retval``       || (case-insensitive –                                 |
    || ``log_elapsed``      || ``True``, ``False``, ``tRuE``, ``FALSE``, etc.)     |
    || ``log_exit``         ||                                                     |
    || ``indent``           ||                                                     |
    || ``log_call_numbers`` ||                                                     |
    || ``record_history``   ||                                                     |
    || ``NO_DECO``          ||                                                     |
    +-----------------------+------------------------------------------------------+
    || ``enabled``          || int, or case-insensitive boolean as above           |
    +-----------------------+------------------------------------------------------+
    || ``args_sep``         || string, enclosed in quotes                          |
    || ``prefix``           ||                                                     |
    +-----------------------+------------------------------------------------------+
    || ``loglevel``         || int                                                 |
    || ``max_history``      ||                                                     |
    +-----------------------+------------------------------------------------------+
    || ``file``             || ``sys.stdout`` or ``sys.stderr``,                   |
    ||                      || **not** enclosed in quotes (or ``None``)            |
    +-----------------------+------------------------------------------------------+
    || ``logger``           || name of a logger, enclosed in quotes (or ``None``)  |
    +-----------------------+------------------------------------------------------+

    .. warning::
        Ill-formed lines, bad values, and nonexistent settings are all ignored, **silently**.


.. topic:: Settings file example

    Here's an example of what a settings file might contain::

        args_sep   = ' | '
        log_args   = False
        log_retval = TRUE
        logger     = 'star3_logger'
        # file: this is just for illustration, as logger takes precedence.
        #       file can only be sys.stderr or sys.stdout [*** NOT IN QUOTES! ***] (or None)
        file=sys.stderr
        # ``log_elapsed`` has an indirect value:
        log_elapsed='elapsed_='
        # The following lines are bad in one way or another, and are ignored:
        prefix=1492
        loglevel=
        no_such_setting=True
        indent


.. note::
 You can use the ``log_calls.set_defaults()`` classmethod to change the `log_calls` default settings,
 instead of passing the same ``settings`` argument to every ``@log_calls(...)`` decoration.
 See :ref:`set_reset_defaults`.

Where to find more examples
------------------------------

The test file ``tests/test_log_call_more.py``, in the docstring of the function
``main__settings()``, contains several examples (doctests) of the ``settings`` parameter.
Two of the tests there use "good" settings files in the ``tests/`` directory: ``.log_calls``
and ``log_calls-settings.txt``. Two more test what happens (nothing) when specifying
a nonexistent file or a file with "bad" settings (``tests/bad-settings.txt``).
Another tests the ``settings`` parameter as a ``dict``.

--------------------------------------------------------------------

.. _NO_DECO-parameter:

``NO_DECO`` (default: ``None``)
================================================

The ``NO_DECO`` parameter prevents `log_calls` from decorating a callable or class:
when true, the decorator returns the decorated thing itself, unwrapped and unaltered.
Intended for use at program startup, it provides a single "true bypass" switch.

Using this parameter in a settings dict or settings file lets you control "true bypass"
with a single switch, e.g. for production, without having to comment out every decoration.

.. topic:: ``NO_DECO`` can only prevent decoration, it cannot undo decoration.

    For example, if ``f`` is already decorated, then::

        f = log_calls(NO_DECO=True)(f)

    has no effect: ``f`` remains decorated.

.. _NO_DECO-for-production:

Use ``NO_DECO=True`` for production
-------------------------------------------

Even even when it's disabled or bypassed, `log_calls` imposes some overhead.
For production, therefore, it's best to not use it at all. One tedious way to guarantee
that would be to comment out every ``@log_calls()`` decoration in every source file.
``NO_DECO`` allows a more humane approach: Use a settings file or settings dict
containing project-wide settings, including an entry for ``NO_DECO``. For development, use::

    NO_DECO=False

and for production, change that to::

    NO_DECO=True

Even though it isn't actually a "setting", ``NO_DECO`` is permitted in settings files and dicts
in order to allow this.

Examples
-------------

The tests in ``tests/test_no_deco__via_file.py`` demonstrate using ``NO_DECO``
in an imported ``dict`` and in a settings file.

--------------------------------------------------------------------

.. _override-parameter:

``override`` (default: ``False``)
================================================

The ``override`` parameter is mainly intended for use when redecorating functions and classes
with the ``log_calls.decorate_*`` classmethods, as discussed in the chapter
:ref:`decorating_functions_class_hierarchies_modules`.
``override`` can also be used with class decorators to give its settings precedence over
any explicitly given for callables or inner classes. See :ref:`precedence-of-decorators` for
a simple example, and :ref:`decorate-methods-sklearn-example` for a larger one.

--------------------------------------------------------------------

.. _parameters-docd-elsewhere:

Parameters Documented In Other Chapters
===========================================

The remaining parameters are more specialized and require discussion of the contexts
in which they are used. For completeness, we catalog them here, together with links to
their documentation.


.. _omit-only-brief:

``omit``, ``only`` (defaults: ``tuple()``)
----------------------------------------------------------------

In the chapter :ref:`decorating_classes`, the section
:ref:`omit_only_params` documents the two parameters that control
which callables of a class get decorated.
The value of each is a string or a sequence of strings;
each string is either the name of a callable,
or a "glob" pattern matching names of callables.

* ``omit`` — `log_calls` will *not* decorate these callables;
* ``only`` — `log_calls` decorates only these callables, excluding any specified by ``omit``

.. _logger-loglevel-brief:

``logger`` (default: ``None``), ``loglevel`` (default: ``logging.DEBUG``)
-----------------------------------------------------------------------------

:ref:`Logging` presents the two parameters that let you output `log_calls` messages to a ``Logger``:

* :ref:`logger <logger-parameter>` – a logger name (a ``str``) or a ``logging.Logger`` object;
* :ref:`loglevel <loglevel-parameter>` (an ``int``) – ``logging.DEBUG``, ``logging.INFO``, ...,  or a custom loglevel.

.. _record_history-max_history-brief:

``record_history`` (default: ``False``), ``max_history`` (default: ``0``)
---------------------------------------------------------------------------------

:ref:`call_history_statistics` discusses the two parameters governing call history collection:

* :ref:`record_history <record_history-parameter>` governs whether call history is retained, and then
* :ref:`max_history <max_history-parameter>` controls how much (cache size).

