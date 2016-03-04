.. _indent_aware_writing_methods:

Writing Indent-Aware Debug Messages
################################################################################
.. The Indent-Aware Writing Methods

The two methods described in this chapter provide alternatives to
``print()`` for writing debug messages.

`log_calls` exposes the method it uses to write its messages, and
makes it available to decorated callables as the method ``log_message()``,
which a callable can call *on its own wrapper*. If a decorated callable writes
debugging messages, even multiline messages, it can use ``log_message()``
to write those messages so that they sit nicely within the `log_calls`
visual frame.

A quick clarifying example:

    >>> @log_calls()
    ... def f(x):
    ...     f.log_message('Yo')
    >>> f(2)
    f <== called by <module>
        arguments: x=2
        Yo
    f ==> returning to <module>

Most uses of ``log_message()`` will print variables or expressions together with
their values, so we also provide the :ref:`log_exprs() <log_exprs_method>` method,
which make it very simple to do so.

.. note::
    On the reasonable assumption that you will use `log_calls` only in development,
    and that in production you will eliminate its use, using these functions incurs
    the future cost of having to delete them or comment them out.

    Expressions involving ``log_message()`` and ``log_exprs()``, which work when a callable
    is decorated, will raise exceptions when the callable is not decorated.

    However, if you used ``print()`` to write debugging messages, you'd still have to eliminate
    all of those statements in production — or, at least, ensure that they aren't called.
    Regardless of how you write debugging messages, you can guarantee that they are not executed
    in production by guarding them with a condition, such as::

        @log_calls()
        def f(x):
            c = ...             # Compute local c from x and whatever else
            if DEBUG:           # Some flag that's False in production
                print('In f, DEBUG true')
                f.log_exprs('c')


.. _log_message_method:

`log_calls`' own writing method ``log_message()``
==================================================

.. index:: log_message() (method available on decorated callable's wrapper)

.. py:method:: wrapper.log_message(msg, *msgs, sep=' ', extra_indent_level=1, prefix_with_name=False)
    :noindex:

    (To be called by a decorated callable, on its own wrapper.)
    Join one one or more "messages" (anything you want to see as a string) with ``sep``,
    and write the result to the `log_calls` output destination of the caller.

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

    **Note**: If the `mute` setting of the caller is ``log_calls.MUTE.CALLS``,
    ``log_message()`` forces ``prefix_with_name`` to ``True``, and ``extra_indent_level`` to ``0``.
    A little reflection should reveal that these are sensible adjustments.


Using ``log_message()`` within a decorated function
------------------------------------------------------

Consider the following function:

    >>> @log_calls(indent=True, log_call_numbers=True)
    ... def f(n):
    ...     if n <= 0:
    ...         print("*** Base case n <= 0")
    ...     else:
    ...         print("*** n=%d is %s,\\n    but we knew that."
    ...                       % (n, "odd" if n%2 else "even"))
    ...         print("*** (n=%d) We'll be right back, after this:" % n)
    ...         f(n-1)
    ...         print("*** (n=%d) We're back." % n)
    >>> f(2)                                            # doctest: +SKIP
    f [1] <== called by <module>
        arguments: n=2
    *** n=2 is even,
        but we knew that.
    *** (n=2) We'll be right back, after this:
        f [2] <== called by f [1]
            arguments: n=1
    *** n=1 is odd,
        but we knew that.
    *** (n=1) We'll be right back, after this:
            f [3] <== called by f [2]
                arguments: n=0
    *** Base case n <= 0
            f [3] ==> returning to f [2]
    *** (n=1) We're back.
        f [2] ==> returning to f [1]
    *** (n=2) We're back.
    f [1] ==> returning to <module>

The debugging messages written by ``f`` literally "stick out", and it becomes difficult,
especially in more complex situations with multiple functions and methods,
to figure out who actually wrote which message; hence the "(n=%d)" tag. If instead
``f`` uses ``log_message()``, all of its messages from each invocation align neatly
within the `log_calls` visual frame. We take this opportunity to also
illustrate the keyword parameters of ``log_message()``:

    >>> @log_calls(indent=True, log_call_numbers=True)
    ... def f(n):
    ...     if n <= 0:
    ...         f.log_message("Base case n =", n, prefix_with_name=True)
    ...     else:
    ...         f.log_message("*** n=%d is %s,\\n    but we knew that."
    ...                       % (n, "odd" if n%2 else "even"),
    ...                       extra_indent_level=0)
    ...         f.log_message("We'll be right back", "after this:",
    ...                       sep=", ", prefix_with_name=True)
    ...         f(n-1)
    ...         f.log_message("We're back.", prefix_with_name=True)
    >>> f(2)                                            # doctest: +SKIP
    f [1] <== called by <module>
        arguments: n=2
    *** n=2 is even,
        but we knew that.
        f [1]: We'll be right back, after this:
        f [2] <== called by f [1]
            arguments: n=1
        *** n=1 is odd,
            but we knew that.
            f [2]: We'll be right back, after this:
            f [3] <== called by f [2]
                arguments: n=0
                f [3]: Base case n = 0
            f [3] ==> returning to f [2]
            f [2]: We're back.
        f [2] ==> returning to f [1]
        f [1]: We're back.
    f [1] ==> returning to <module>

The ``log_message()`` method works whether the output destination is ``sys.stdout``,
another stream, a file, or a logger. The test file ``test_log_calls_more.py`` 
contains an example ``main__log_message__all_possible_output_destinations()`` 
which illustrates that.


.. _log_message_in_class:

Using ``log_message()`` in classes, via ``get_own_log_calls_wrapper()``
--------------------------------------------------------------------------------------------------

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


.. index:: log_exprs() (method available on decorated callable's wrapper)

.. _log_exprs_method:

The expression-evaluating method ``log_exprs()``
===============================================================

``log_exprs()`` is a convenience method built upon ``log_message()``
which makes it easy to print variables and expressions together with their values.

.. py:method:: wrapper.log_exprs(*exprs, sep=', ', extra_indent_level=1, prefix_with_name=False, prefix='')
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

Here's a small but realistic example:

    >>> @log_calls()
    ... def gcd(a, b):
    ...     while b:
    ...         a, b = b, (a % b)
    ...         gcd.log_exprs('a', 'b', prefix="At bottom of loop: ")
    ...     return a
    >>> gcd(48, 246)
    gcd <== called by <module>
        arguments: a=48, b=246
        At bottom of loop: a = 246, b = 48
        At bottom of loop: a = 48, b = 6
        At bottom of loop: a = 6, b = 0
    gcd ==> returning to <module>
    6


Further examples can be found in the docstring of the function ``test__log_exprs()``
in ``tests/test_log_calls_v30_minor_features_fixes.py``.


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
    ...     f.log_message('Hello, world!')
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
