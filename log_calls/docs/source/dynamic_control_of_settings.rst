.. _dynamic_control_of_settings:

Dynamic Control of Settings
#################################################################

Sometimes, you'll need or want to change a `log_calls` setting for a decorated callable
on the fly. The major impediment to doing so is that the values of the `log_calls`
parameters are set once the definition of the decorated callable is interpreted.
Those values are established once and for all when the Python interpreter
processes the definition.

The problem, and *log_calls* solutions
========================================================

Even if a variable is used as a parameter value, its value at the time
Python processes the definition is "frozen" for the created callable object.
What gets stored is not the variable, but its value. Subsequently changing
the value of the variable will *not* affect the behavior of the decorator.

For example, suppose ``DEBUG`` is a module-level variable initialized to ``False``:

    >>> DEBUG = False

and you use this code:

    >>> @log_calls(enabled=DEBUG)
    ... def foo(**kwargs): pass
    >>> foo()       # No log_calls output: DEBUG is False

If later you set ``DEBUG = True`` and call ``foo``, that call still won't be logged,
because the ``enabled`` setting of ``foo`` is bound to the original *value*
of ``DEBUG``, established when the definition was processed:

    >>> DEBUG = True
    >>> foo()       # Still no log_calls output

This is simply how default values of keyword parameters work in Python.

`log_calls` provides *three* ways to overcome this limitation
and dynamically control the settings of a decorated callable:

* the ``decorate_*`` classmethods, described in the previous chapter :ref:`decorating_functions_class_hierarchies_modules`,
* the ``log_calls_settings`` attribute, described in this chapter, which provides a mapping interface
  and an attribute-based interface to settings, and
* *indirect values*, as described in the next chapter :ref:`indirect_values`.


.. index:: log_calls_settings (data attribute of decorated callable's wrapper)

.. _log_calls_settings-obj:

The ``log_calls_settings`` attribute — the *settings* API
===========================================================

`log_calls` adds an attribute ``log_calls_settings`` to the wrapper of a decorated callable,
through which you can access the settings for that callable. This attribute
is an object that lets you read and write the settings of the callable via a mapping
(``dict``-like) interface, and equivalently, via attributes of the object. The mapping keys
and the attribute names are simply the `log_calls` settings keywords. ``log_calls_settings`` also
implements many of the standard ``dict`` methods for interacting with the settings in familiar ways.

.. _mapping-interface:

The mapping interface and the attribute interface to settings
----------------------------------------------------------------

Once you've decorated a callable with `log_calls`,

    >>> @log_calls()
    ... def f(*args, **kwargs):
    ...     return 91

you can access and change its settings via the ``log_calls_settings`` attribute
of the decorated callable, which behaves like a dictionary. You can read and
write settings using the `log_calls` keywords as keys:

    >>> f.log_calls_settings['enabled']
    True
    >>> f.log_calls_settings['enabled'] = False
    >>> _ = f()                   # no output (not even 91, because of "_ = ")
    >>> f.log_calls_settings['enabled']
    False
    >>> f.log_calls_settings['log_retval']
    False
    >>> f.log_calls_settings['log_retval'] = True
    >>> f.log_calls_settings['log_elapsed']
    False
    >>> f.log_calls_settings['log_elapsed'] = True

You can also use the same keywords as attributes of ``log_calls_settings``
instead of as keys to the mapping interface; they're completely equivalent:

    >>> f.log_calls_settings.log_elapsed
    True
    >>> f.log_calls_settings.log_call_numbers
    False
    >>> f.log_calls_settings.log_call_numbers = True
    >>> f.log_calls_settings.enabled = True     # turn it back on!
    >>> _ = f()                                 # doctest: +ELLIPSIS
    f [1] <== called by <module>
        arguments: <none>
        f [1] return value: 91
        elapsed time: ... [secs], process time: ... [secs]
    f [1] ==> returning to <module>

    >>> f.log_calls_settings.log_args = False
    >>> f.log_calls_settings.log_elapsed = False
    >>> f.log_calls_settings.log_retval = False
    >>> _ = f()                                 # doctest: +ELLIPSIS
    f [2] <== called by <module>
    f [2] ==> returning to <module>

``log_calls_settings`` has a length ``len(log_calls_settings)``;
its keys and ``items()`` can be iterated through; you can use ``in`` to test
for key membership; and it has an ``update()`` method. As with an ordinary dictionary,
attempting to access a nonexistent setting raises ``KeyError``. Unlike an ordinary
dictionary, you can't add new keys – the ``log_calls_settings`` dictionary is closed
to new members, and attempts to add one will also raise ``KeyError``.

.. index:: as_dict() (wrapper.log_calls_settings method)
.. index:: as_OD() (wrapper.log_calls_settings method)

.. _update-as_etc:

The ``update()``, ``as_dict()``, and ``as_OD()`` methods
---------------------------------------------------------------------------

The ``update()`` method of the ``log_calls_settings`` object lets you update several settings at once:

    >>> f.log_calls_settings.update(
    ...     log_args=True, log_elapsed=False, log_call_numbers=False,
    ...     log_retval=False)
    >>> _ = f()
    f <== called by <module>
        arguments: <none>
    f ==> returning to <module>

You can retrieve the entire collection of settings as a ``dict`` using ``as_dict()``,
and as an ``OrderedDict`` using ``as_OD()``. Either can serve as a snapshot
of the settings, so that you can change settings temporarily, use the new settings,
and then use ``update()`` to restore settings from the snapshot. in addition to taking
keyword arguments, as shown above, ``update()`` can take one or more dicts – in
particular, a dictionary retrieved from one of the ``as_*`` methods:

.. index:: update() (wrapper.log_calls_settings method)

.. py:method:: wrapper.log_calls_settings.update(*dicts, **d_settings) -> None
   :noindex:

   Update the settings from all dicts in ``dicts``, in order, and then from ``d_settings``.
   Allow but ignore attempts to write to immutable keys (``max_history``).
   This permits the user to retrieve a copy of the settings with ``as_dict()``
   or ``as_OD()``, obtaining a dictionary which will contain items for
   immutable settings too; make changes to settings and use them;
   then restore the original settings by passing the retrieved dictionary to ``update()``.

   :param dicts: a sequence of dicts containing setting keywords and values
   :param d_settings: additional settings and values

Example
+++++++++++
This example illustrates the use-case described above.

First, retrieve settings (here, as an ``OrderedDict`` because those are
more `doctest`-friendly, but in "real life" using ``as_dict()`` suffices):

    >>> od = f.log_calls_settings.as_OD()
    >>> od                      # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True),           ('args_sep', ', '),
                 ('log_args', True),          ('log_retval', False),
                 ('log_elapsed', False),      ('log_exit', True),
                 ('indent', True),            ('log_call_numbers', False),
                 ('prefix', ''),              ('file', None),
                 ('logger', None),            ('loglevel', 10),
                 ('mute', False),
                 ('record_history', False),   ('max_history', 0)])

Change settings temporarily:

    >>> f.log_calls_settings.update(
    ...     log_args=False, log_elapsed=True, log_call_numbers=True,
    ...     log_retval=True)

Use the new settings for ``f``:

    >>> _ = f()                     # doctest: +ELLIPSIS
    f [4] <== called by <module>
        f [4] return value: 91
        elapsed time: ... [secs], process time: ... [secs]
    f [4] ==> returning to <module>

Now restore original settings, this time passing the retrieved settings
dictionary rather than keywords (we *could* pass ``**od``, but that's
unnecessary and a pointless expense):

    >>> f.log_calls_settings.update(od)
    >>> od == f.log_calls_settings.as_OD()
    True
