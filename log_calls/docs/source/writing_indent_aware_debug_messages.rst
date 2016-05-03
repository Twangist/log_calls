.. The Indent-Aware Writing Methods
.. _indent_aware_writing_methods:

Writing `log_calls`-Aware Debug Messages
################################################################################

`log_calls` provides the ``log_message`` method as a better alternative to ``print``
for writing debugging messages.

``log_message`` writes to the `log_calls` output stream
— whether that's a console stream, file or logger — where its output is properly
synced and aligned (with respect to the decorated callable it was called from). If
later you undecorate the callable (by deleting or commenting out the decorator,
or by passing it ``NO_DECO=True``), you don't *have* to remove the call to
``log_message``, because by default the method writes something only when called
from within a decorated callable, and doesn't raise an exception otherwise.

It's quite typical to use debugging messages to print out (or "dump") the values
of local variables and expressions, together with labels. Accomplishing this with
``print`` or even ``log_message`` usually requires ad-hoc though boilerplate string
formatting. As a convenience, `log_calls` provides the :ref:`log_exprs() <log_exprs_method>`
method, which prints variables and expressions together with their values in the
context of the caller.

.. todo::
    0.3.1 (reference the chapter ``accessing_method_wrappers`` when discussing
    (briefly?) the deprecated *wrapper*.log_*() methods -- more difficult to
    use in classes, "plumbing" exposed.)

.. index:: log_methods_raise_if_no_deco (flag)

.. _log_message_method:

The ``log_calls.log_message()`` method
==============================================

When you call ``log_calls.log_message('my message')`` from within a decorated callable ``f``,
``my message`` appears in the `log_calls` output stream, between the "entering" and "exiting"
parts of the `log_calls` report for the call to ``f``, aligned with the "arguments" section:

    >>> @log_calls()
    ... def f(x):
    ...     log_calls.log_message('About to try new approach...')
    ...     return 4 * x
    >>> f(2)
    f <== called by <module>
        arguments: x=2
        About to try new approach...
    f ==> returning to <module>
    8

If you undecorate the callable — say, by deleting or commenting out the decorator, or by
passing it ``NO_DECO=True`` — by default you *don't* have to comment out the call to
``log_message``, as it won't write anything and won't raise an exception:

    >>> # @log_calls()
    >>> def f(x):
    ...     log_calls.log_message('About to try new approach...')
    ...     return 4 * x
    >>> f(2)
    8

You can change this default by setting the `log_calls` global variable ``log_calls.log_methods_raise_if_no_deco``
to ``True``, as discussed :ref:`below <log_methods_raise_if_no_deco>`.

``log_message()`` details
----------------------------------------------------

.. index:: log_message()

.. py:method:: log_calls.log_message(msg, *msgs, sep=' ', extra_indent_level=1, prefix_with_name=False)
    :noindex:

    Join one one or more messages with ``sep``, and write the result to the `log_calls`
    output destination of the caller, a decorated callable. The "messages" are strings,
    or objects whose *repr*s will be displayed.

    :param msg: the first or only message
    :param msgs: optional additional messages
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

    :raises: TypeError, ValueError, AttributeError if called from within
             an undecorated callable and ``log_calls.log_methods_raise_if_no_deco`` is true.

    **Note**: If the `mute` setting of the caller is ``log_calls.MUTE.CALLS``,
    ``log_message()`` forces ``prefix_with_name`` to ``True``, and ``extra_indent_level`` to ``0``.
    A little reflection should reveal that these are sensible adjustments.
    See the following sections for examples.


.. index:: log_exprs()

.. _log_exprs_method:

Writing expressions and their values with ``log_exprs()``
===============================================================

``log_exprs()`` is a convenience method built upon ``log_message()``
which makes it easy to print variables and expressions together with their values.

Here's a small but realistic example:

    >>> @log_calls()
    ... def gcd(a, b):
    ...     while b:
    ...         a, b = b, (a % b)
    ...         log_calls.log_exprs('a', 'b', prefix="At bottom of loop: ")
    ...     return a
    >>> gcd(48, 246)
    gcd <== called by <module>
        arguments: a=48, b=246
        At bottom of loop: a = 246, b = 48
        At bottom of loop: a = 48, b = 6
        At bottom of loop: a = 6, b = 0
    gcd ==> returning to <module>
    6

You can also pass expressions to ``log_exprs``:
    >>> @log_calls()
    ... def f():
    ...     x = 42
    ...     log_calls.log_exprs('x', 'x//6')
    >>> f()
    f <== called by <module>
        x = 42, x//6 = 7
    f ==> returning to <module>


Further examples can be found in the docstring of the function ``test__log_exprs()``
in ``tests/test_log_calls_v30_minor_features_fixes.py``.

``log_exprs()`` details
----------------------------------------------------

.. py:method:: log_calls.log_exprs(*exprs, sep=', ', extra_indent_level=1, prefix_with_name=False, prefix='')
    :noindex:

    Evaluate each expression in ``exprs`` in the context of the caller, a decorated callable;
    make a string `expr` ``=`` `val` from each, and pass those strings
    to ``log_message()`` as messages to write, separated by ``sep``.

    :param exprs: expressions to evaluate and log with their values
    :type exprs: sequence of ``str``
    :param sep: separator for `expr` ``=`` `val` substrings
    :param extra_indent_level: as for ``log_message()``
    :param prefix_with_name: as for ``log_message()``
    :param prefix: additional text to prepend to output message.

    :raises: TypeError, ValueError, AttributeError if called from within
             an undecorated callable and ``log_calls.log_methods_raise_if_no_deco`` is true.


.. index:: log_methods_raise_if_no_deco (flag)

.. _log_methods_raise_if_no_deco:

The global variable ``log_calls.log_methods_raise_if_no_deco`` (default: ``False``)
=====================================================================================

.. todo::
    blah blah

By default (when ``log_methods_raise_if_no_deco == False``), if you call ``log_calls.log_*``
from within a method or function that isn't decorated, it does nothing (except waste a
few cycles). You can comment out or delete the ``@log_calls`` decorator, or use the ``NO_DECO``
parameter to suppress decoration, and the ``.log_*`` method calls will play nicely: they won't
output anything, **and** the calls won't raise ``AttributeError`` (as they would formerly
if you called the methods on a wrapper that ``is None``). In short, leaving the ``log_calls.log_*``
lines uncommented is as benign as it can be.

But probably at some point you *do* want to know when you have lingering code that's
supposedly development-only. `log_calls` will inform you of that if you set
``log_calls.log_methods_raise_if_no_deco`` to ``True`` (or any truthy value).

When this flag is true, calls to ``log_calls.log_message`` and ``log_calls.log_exprs``
from within an undecorated function or method will raise an appropriate exception. This
compels you to comment out or delete any calls to ``log_calls.log_*`` from within undecorated
functions or methods. (A call to ``log_calls.log_*`` from within a callable
that *never* was decorated is just a mistake, and it *should* raise an exception; with this flag
set to true, it will.)


.. _indent_aware_writing_methods-mute:

Indent-aware writing methods and muting — examples
==============================================================

.. _indent_aware_writing_methods-mute-setting:

Examples using the `mute` setting
-----------------------------------

When a decorated callable is not muted (its ``mute`` setting is ``log_calls.MUTE.NOTHING``,
i.e. ``False``, the default), `log_calls` produces output as do ``log_message()`` and ``log_exprs()``:

    >>> @log_calls()
    ... def f():
    ...     log_calls.log_message('Hello, world!')
    >>> f()
    f <== called by <module>
        Hello, world!
    f ==> returning to <module>

When the callable's ``mute`` setting is ``log_calls.MUTE.CALLS``, no extra indent level is added,
and messages are prefixed with the callable's display name:

    >>> f.log_calls_settings.mute = log_calls.MUTE.CALLS
    >>> f()
    f: Hello, world!

When the callable's ``mute`` setting is ``log_calls.MUTE.ALL``, ``log_message()`` produces no output:

    >>> f.log_calls_settings.mute = log_calls.MUTE.ALL
    >>> f()     # (no output)

Using global `mute`
--------------------------
Setting ``log_calls.mute = log_calls.MUTE.CALLS`` allows output only from ``log_calls.log_*`` methods,
in all decorated callables.

.. todo::
    Say more; implications; example, 2 fns, including turning decoration off


.. _indent_aware_writing_methods-global-mute:

Examples using the `mute` setting and global mute — corner cases
------------------------------------------------------------------

First, define a couple of simple functions:

    >>> @log_calls()
    ... def g(): g.log_message("Hi")
    >>> @log_calls()
    ... def f(): f.log_message("Hi"); g()

Assume that ``log_calls.mute == False``, which is the default. Calling ``f()`` gives all possible output:

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
``test__log_message__indirect_mute()`` illustrates ``log_message()`` together with
an indirect value for the ``mute`` setting.


.. _log_message_in_class:

Using ``log_message()`` in classes
==========================================

.. todo::
    REWORK

A method or property must first access its own wrapper order to use ``log_message()``,
one of the wrapper's attributes. This is straightforward, as explained in the section
on :ref:`accessing wrappers of methods <get_own_log_calls_wrapper-function>`.

The following class illustrates all possibilities. Note that `log_calls` call output is muted
(to reduce clutter for this example), and therefore ``log_message()`` automatically prefixes
its output with the name of the caller, and doesn't indent by an extra 4 spaces:

    >>> @log_calls(omit='no_deco', mute=log_calls.MUTE.CALLS)
    ... class B():
    ...     def __init__(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     def method(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     def no_deco(self):
    ...         wrapper = self.get_own_log_calls_wrapper()      # raises ValueError
    ...         wrapper.log_message('Hi')
    ...     @classmethod
    ...     def clsmethod(cls):
    ...         wrapper = cls.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     @staticmethod
    ...     def statmethod():
    ...         wrapper = B.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...
    ...     @property
    ...     def prop(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     @prop.setter
    ...     @log_calls(name='B.%s.setter')
    ...     def prop(self, val):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...
    ...     def setx(self, val):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi from setx alias x.setter')
    ...     def delx(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi from delx alias x.deleter')
    ...     x = property(None, setx, delx)

    >>> b = B()
    B.__init__: Hi
    >>> b.method()
    B.method: Hi
    >>> b.no_deco()     # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: ...
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

