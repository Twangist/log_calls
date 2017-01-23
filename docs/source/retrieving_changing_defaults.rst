.. _set_reset_defaults:


Retrieving and Changing the Defaults
#############################################################
.. Retrieving, Changing, and Restoring `log_calls` Defaults

`log_calls` classmethods ``set_defaults()``, ``reset_defaults()``
======================================================================

The :ref:`settings parameter <settings-parameter>` lets you specify an entire collection of
:ref:`settings <what-is-a-setting>` at once. If you find that you're passing the same settings
dict or settings file to most `log_calls` decorators in a program, `log_calls` offers a further economy.
At program startup, you can use the ``log_calls.set_defaults`` classmethod to change the `log_calls`
defaults to the settings you want, and eliminate most of the ``settings`` arguments.

.. py:classmethod:: log_calls.set_defaults(new_default_settings=None, **more_defaults)

   Change the `log_calls` default values for settings, different from the "factory defaults".

   :param new_default_settings:  a settings dict or settings file: any valid value
    for the :ref:`settings parameter <settings-parameter>`.
   :type new_default_settings:   ``dict`` (a settings dict) or ``str`` (pathname for a settings file)
   :param more_defaults: keyword parameters where every key is a :ref:`setting <what-is-a-setting>`.
    These override settings in ``new_default_settings``.

   **The new defaults are not retroactive!** (Settings of already-decorated callables remain unchanged.)
   They apply to every decoration that occurs subsequently.

You can easily undo all changes effected by ``set_defaults()``:

.. py:classmethod:: log_calls.reset_defaults()

        Restore the "factory default" defaults.


Examples
------------------------------------------------------

Although these are "toy" examples, they illustrate how the ``*_defaults()`` methods behave:

Decorate ``f`` with "factory defaults":

    >>> @log_calls()
    ... def f(x, y): return x

Define a settings dict:

    >>> new_settings = dict(
    ...     log_call_numbers=True,
    ...     log_exit=False,
    ...     log_retval=True,
    ... )

Call ``set_defaults()`` with the above settings dict, and in addition change
the default for ``args_sep``:

    >>> log_calls.set_defaults(new_settings, args_sep=' $ ')

Decorate ``g`` while these defaults are in force:

    >>> @log_calls()
    ... def g(x,y): return y

Restore the "factory defaults":

    >>> log_calls.reset_defaults()

and decorate ``h``:

    >>> @log_calls()
    ... def h(u, v): return v

Call ``f``, ``g``, and ``h``: only ``g`` will use the defaults of the ``set_defaults()`` call:

    >>> _ = f(0, 1); _ = g(2, 3); _ = h(4, 5)
    f <== called by <module>
        arguments: x=0, y=1
    f ==> returning to <module>
    g [1] <== called by <module>
        arguments: x=2 $ y=3
        g [1] return value: 3
    h <== called by <module>
        arguments: u=4, v=5
    h ==> returning to <module>


`log_calls` classmethods ``get_defaults_OD()``, ``get_factory_defaults_OD()``
===================================================================================

For convenience, `log_calls` also provides classmethods for retrieving the current defaults
and the "factory defaults", each as an ``OrderedDict``:

.. py:classmethod:: log_calls.get_defaults_OD()

        Return an ``OrderedDict`` of the current `log_calls` defaults.

.. py:classmethod:: log_calls.get_factory_defaults_OD()

        Return an ``OrderedDict`` of the `log_calls` "factory defaults".


Examples
------------------

If ``log_calls.set_default()`` has not been called, then the current defaults *are*
the factory defaults:

    >>> log_calls.get_defaults_OD() == log_calls.get_factory_defaults_OD()
    True

The dictionaries returned by the ``get*_defaults_OD()`` methods can be compared
with those obtained from a callable's ``log_calls_settings.as_OD()``
or ``log_calls_settings.as_dict()`` method to determine whether, and if so how,
the callable's settings differ from the defaults.

    >>> def dict_minus(d1, d2: 'Mapping') -> dict:
    ...     """Return a dict of the "dictionary difference" of d1 and d2:
    ...     all items in d1 such that either the key is not in d2,
    ...     or the key is in both but values differ.
    ...     """
    ...     return {
    ...         key: val for key, val in d1.items()
    ...         if not (key in d2 and val == d2[key])
    ...     }

    >>> @log_calls(log_exit=False)
    >>> def func(): pass
    >>> dict_minus(func.log_calls_settings.as_OD(), log_calls.get_defaults_OD())
    {'log_exit': False}
