.. The Indent-Aware Writing Methods
.. _indent_aware_writing_methods:

Writing `log_calls`-Aware Debugging Messages
################################################################################

`log_calls` provides the ``log_calls.print`` method as a better alternative to the global
``print`` function for writing debugging messages. It also provides the ``log_calls.print_exprs``
method as an easy way to "dump" variables and expressions together with their values.

``log_calls.print`` writes to the `log_calls` output stream
— whether that's a console stream, file or logger — where its output is properly
synced and aligned with respect to the decorated callable it was called from. If
later you undecorate the callable (for example, by deleting or commenting out the decorator,
or by passing it ``NO_DECO=True``), you don't *have* to remove the call to
``log_calls.print``, because by default the method writes something only when called
from within a decorated callable, and doesn't raise an exception otherwise.

It's quite typical to use debugging messages to print out (or "dump") the values
of local variables and expressions, together with labels. Accomplishing this with
``print`` or even ``log_calls.print`` usually requires ad-hoc though boilerplate string
formatting. As a convenience, `log_calls` provides the :ref:`log_calls.print_exprs() <log_exprs_method>`
method, which prints variables and expressions together with their values in the
context of the caller.

.. _log_message_method:

The ``log_calls.print()`` method
==============================================

When you call ``log_calls.print('my message')`` from within a decorated callable ``f``,
``my message`` appears in the `log_calls` output stream, between the "entering" and "exiting"
parts of the `log_calls` report for the call to ``f``, aligned with the "arguments" section:

    >>> @log_calls()
    ... def f(x):
    ...     log_calls.print('About to try new approach...')
    ...     return 4 * x
    >>> f(2)
    f <== called by <module>
        arguments: x=2
        About to try new approach...
    f ==> returning to <module>
    8

If you undecorate the callable — say, by deleting or commenting out the decorator, or by
passing it ``NO_DECO=True`` — by default you *don't* have to comment out the call to
``log_calls.print``, as it won't write anything and won't raise an exception:

    >>> # @log_calls()
    >>> def f(x):
    ...     log_calls.print('About to try new approach...')
    ...     return 4 * x
    >>> f(2)
    8

You can change this default by setting the `log_calls` global variable ``log_calls.print_methods_raise_if_no_deco``
to ``True``, as discussed :ref:`below <print_methods_raise_if_no_deco>`.

``log_calls.print()`` details
----------------------------------------------------

.. index:: log_calls.print()

.. py:method:: log_calls.print(*msgs, sep=' ', extra_indent_level=1, prefix_with_name=False)
    :noindex:

    Join one or more messages with ``sep``, and write the result to the `log_calls`
    output destination of the caller, a decorated callable. The "messages" are strings,
    or objects to be displayed as ``str``\ s. The method does nothing if no messages are passed.

    :param msgs: messages to write.
    :param extra_indent_level: a number of 4-column-wide *indent levels* specifying
        where to begin writing that message. This value x 4 is an offset in columns
        from the left margin of the visual frame established by `log_calls` – that is,
        an offset from the column in which the callable's entry and exit messages begin.
        The default of 1 aligns the message with the "arguments: " line of `log_calls`'s output.
    :type extra_indent_level: ``int``
    :param prefix_with_name:  If true, the final message is prefaced with the
        name of the callable, plus its call number in square brackets
        if the ``log_call_numbers`` setting is true.
    :type prefix_with_name:  ``bool``

    :raises: AttributeError if called from within
             an undecorated callable and ``log_calls.print_methods_raise_if_no_deco`` is true.

    **Note**: If the `mute` setting of the caller is ``log_calls.MUTE.CALLS``,
    ``log_calls.print()`` forces ``prefix_with_name`` to ``True``, and ``extra_indent_level`` to ``0``.
    A little reflection should reveal that these are sensible adjustments.
    See the following sections for examples.


.. index:: log_calls.print_exprs()

.. _log_exprs_method:

Writing expressions and their values with ``log_calls.print_exprs()``
========================================================================

``log_calls.print_exprs()`` is a convenience method built upon ``log_calls.print()``
which makes it easy to print variables and expressions together with their values.

The :ref:`quickstart-lc-aware-debug-messages` section of the :ref:`quickstart` chapter
contains a few examples. Others can be found in the docstring of the function ``test__log_exprs()``
in ``tests/test_log_calls_v30_minor_features_fixes.py``, and in the test module
``tests/test_log_calls_log_methods.py``.

``log_calls.print_exprs()`` details
----------------------------------------------------

.. py:method:: log_calls.print_exprs(*exprs, sep=', ', extra_indent_level=1, prefix_with_name=False, prefix='', suffix='')
    :noindex:

    Evaluate each expression in ``exprs`` in the context of the caller, a decorated callable;
    make a string `expr` ``=`` `val` from each, and pass those strings
    to (the internal method called by) ``log_calls.print()`` as messages to write,
    separated by ``sep``.

    :param exprs: expressions to evaluate and log with their values
    :type exprs: sequence of ``str``
    :param sep: separator for `expr` ``=`` `val` substrings
    :param extra_indent_level: as for ``log_calls.print()``
    :param prefix_with_name: as for ``log_calls.print()``
    :param prefix: additional text to prepend to output message.
    :param suffix: additional text to append to output message.

    :raises: AttributeError if called from within
             an undecorated callable and ``log_calls.print_methods_raise_if_no_deco`` is true.


.. index:: print_methods_raise_if_no_deco (flag)

.. _print_methods_raise_if_no_deco:

The global variable ``log_calls.print_methods_raise_if_no_deco`` (default: ``False``)
=======================================================================================

By default (when ``print_methods_raise_if_no_deco == False``), if you call ``log_calls.log_*``
from within a method or function that isn't decorated, it does nothing (except waste a
few cycles). You can comment out or delete the ``@log_calls`` decorator, or use the ``NO_DECO``
parameter to suppress decoration, and the ``.log_*`` method calls will play nicely: they won't
output anything, **and** the calls won't raise an exception. In short, leaving the ``log_calls.log_*``
lines uncommented is as benign as it can be.

But probably at some point you *do* want to know when you have lingering code that's
supposedly development-only. `log_calls` will inform you of that if you set
``log_calls.print_methods_raise_if_no_deco`` to ``True`` (or any truthy value).

When this flag is true, calls to ``log_calls.print`` and ``log_calls.print_exprs``
from within an undecorated function or method will raise ``AttributeError``. This
compels you to comment out or delete any calls to ``log_calls.log_*`` from within undecorated
functions or methods. (A call to ``log_calls.log_*`` from within a callable
that *never* was decorated is just a mistake, and it *should* raise an exception; with this flag
set to true, it will.)


.. _indent_aware_writing_methods-mute:

Indent-aware writing methods and muting — examples
==============================================================

Presently, "muting" has three states, of a possible four:

    * ``log_calls.MUTE.NOTHING`` — mute nothing
    * ``log_calls.MUTE.CALLS`` — mute the output of the ``@log_calls`` decorators while allowing the output of the ``log_calls.log_*`` methods
    * ``log_calls.MUTE.ALL`` — mute all `log_calls` output

There's a global mute, ``log_calls.mute``, and each decorated callable has its own ``mute`` setting.


.. _indent_aware_writing_methods-mute-setting:

Examples using the `mute` setting
-----------------------------------

When a decorated callable is not muted (its ``mute`` setting is ``log_calls.MUTE.NOTHING``,
i.e. ``False``, the default), `log_calls` produces output as do ``log_calls.print()``
and ``log_calls.print_exprs()``:

    >>> @log_calls()
    ... def f():
    ...     log_calls.print('Hello, world!')
    >>> f()
    f <== called by <module>
        Hello, world!
    f ==> returning to <module>

When the callable's ``mute`` setting is ``log_calls.MUTE.CALLS``, no extra indent level is added,
and messages are prefixed with the callable's display name:

    >>> f.log_calls_settings.mute = log_calls.MUTE.CALLS
    >>> f()
    f: Hello, world!

When the callable's ``mute`` setting is ``log_calls.MUTE.ALL``,
``log_calls.print()`` and ``log_calls.print_exprs()`` produce no output:

    >>> f.log_calls_settings.mute = log_calls.MUTE.ALL
    >>> f()     # (no output)

Using global `mute`
--------------------------
Setting ``log_calls.mute = log_calls.MUTE.CALLS`` allows output only from ``log_calls.log_*`` methods,
in all decorated callables.

.. todo::
    Say more; implications; example, 2 fns, including turning decoration off


.. _indent_aware_writing_methods-global-mute:

global mute interactions with the `mute` setting — examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, define a couple of simple functions:

    >>> @log_calls()
    ... def g(): log_calls.print("Hi")
    >>> @log_calls()
    ... def f(): log_calls.print("Hi"); g()

Assume that ``log_calls.mute == log_calls.MUTE.NOTHING``, which is the default.
Calling ``f()`` gives all possible output:

    >>> f()
    f <== called by <module>
        Hi
        g <== called by f
            Hi
        g ==> returning to f
    f ==> returning to <module>

Now change ``log_calls.mute``, call ``f()``, and observe the effects:

    >>> log_calls.mute = log_calls.MUTE.CALLS
    >>> f()
    f: Hi
        g: Hi

    >>> log_calls.mute = log_calls.MUTE.ALL
    >>> f()     # (no output)

Now alter ``log_calls.mute`` and ``g.log_calls_settings.mute``,
call ``f()``, and observe the effects:

    >>> log_calls.mute = log_calls.MUTE.NOTHING
    >>> g.log_calls_settings.mute = log_calls.MUTE.CALLS
    >>> f()
    f <== called by <module>
        Hi
        g: Hi
    f ==> returning to <module>

    >>> log_calls.mute = log_calls.MUTE.CALLS
    >>> g.log_calls_settings.mute = log_calls.MUTE.ALL
    >>> f()
    f: Hi

Further examples can be found in ``tests/test_log_calls_v30_minor_features_fixes.py``.
``test__global_mute()`` illustrate that global mute is always checked in realtime;
``test__log_message__indirect_mute()`` illustrates using an indirect value for the
``mute`` setting.


.. _log_message_in_class:

Using ``log_calls.print()`` in classes
==========================================

.. todo::
    REWORK

The following class illustrates all possibilities of calling ``log_calls.print()``
from a method. To reduce clutter in this example, `log_calls` call output is muted,
and therefore ``.print()`` automatically prefixes its output with the name
of the caller, and doesn't indent by an extra 4 spaces:

    >>> @log_calls(omit='no_deco', mute=log_calls.MUTE.CALLS)
    ... class B():
    ...     def __init__(self):
    ...         log_calls.print('Hi')
    ...     def method(self):
    ...         log_calls.print('Hi')
    ...     def no_deco(self):
    ...         log_calls.print('Hi')
    ...     @classmethod
    ...     def clsmethod(cls):
    ...         log_calls.print('Hi')
    ...     @staticmethod
    ...     def statmethod():
    ...         log_calls.print('Hi')
    ...
    ...     @property
    ...     def prop(self):
    ...         log_calls.print('Hi')
    ...     @prop.setter
    ...     @log_calls(name='B.%s.setter')  # o/w, display name of setter is also 'B.prop'
    ...     def prop(self, val):
    ...         log_calls.print('Hi')
    ...
    ...     def setx(self, val):
    ...         log_calls.print('Hi from setx alias x.setter')
    ...     def delx(self):
    ...         log_calls.print('Hi from delx alias x.deleter')
    ...     x = property(None, setx, delx)

    >>> b = B()
    B.__init__: Hi
    >>> b.method()
    B.method: Hi
    >>> b.no_deco()     # outputs nothing
    >>> b.statmethod()
    B.statmethod: Hi
    >>> b.clsmethod()
    B.clsmethod: Hi
    >>> b.prop
    B.prop: Hi
    >>> b.prop = 17
    B.prop.setter: Hi
    >>> b.x = 13
    B.setx: Hi from setx alias x.setter
    >>> del b.x
    B.delx: Hi from delx alias x.deleter

Observe that the call to ``b.no_deco()`` does nothing, even though the method isn't decorated.
If ``log_calls.print_methods_raise_if_no_deco`` were true, the call from ``b.no_deco()``
to ``log_calls.print`` would raise ``AttributeError``.


`wrapper`\ ``.log_message()``, `wrapper`\ ``.log_exprs()`` [deprecated]
===========================================================================

.. todo::
    0.3.1 (reference the chapter ``accessing_method_wrappers`` when discussing
    (briefly?) the deprecated *wrapper*.log_*() methods -- more difficult to
    use in classes, "plumbing" exposed.)

FORMERLY : A method or property must first access its own wrapper order to use ``log_message()``,
one of the wrapper's attributes. This is straightforward, as explained in the section
on :ref:`accessing wrappers of methods <get_own_log_calls_wrapper-function>`.

... raise ``AttributeError`` (as they would formerly if you called the methods on a wrapper that ``is None``).
