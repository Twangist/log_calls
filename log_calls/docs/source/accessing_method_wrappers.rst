.. _get_own_log_calls_wrapper-function:

Accessing Method Wrappers
#################################

The ``get_log_calls_wrapper()`` and ``get_own_log_calls_wrapper()`` classmethods
=============================================================================================================================

`log_calls` decorates a callable by "wrapping" it in a function (the *wrapper*) which has
various attributes — not only data containing settings, but also methods. Access to these attributes
requires access to the callable's wrapper. In particular, a decorated callable
must access its *own* wrapper in order to use the :ref:`log_message() <log_message_method>` and
:ref:`log_exprs() <log_exprs_method>` methods.

It's straightforward to access the wrapper of a decorated global function ``f``: after decoration,
``f`` refers to the wrapper. For methods and properties, however, the various kinds of methods
and the two ways of defining properties require different navigation paths to the wrapper.
`log_calls` hides this complexity, providing uniform access to the wrappers of methods and properties.

.. index:: get_log_calls_wrapper() (log_calls-decorated class method)

.. py:classmethod:: decorated_class.get_log_calls_wrapper(fname: str)
    :noindex:

    Classmethod of a decorated class.
    Call this on a decorated class or an instance thereof to access the wrapper
    of the callable named ``fname``, in order to access the
    `log_calls`-added attributes for ``fname``.

    :param fname: name of a method (instance method, staticmethod or classmethod),
        or the name of a property (treated as denoting the getter),
        or the name of a property concatenated with '`.getter`', '`.setter`' or '`.deleter`'.

        .. note::
             If a property is defined using the ``property`` function,
             as in

                ``propx = property(getx, setx, delx)``,

             where ``getx``, ``setx``, ``delx`` are methods of a class (or ``None``),
             then each individual property can be referred to in two ways:

             * via the name of the method, eg. ``setx``, or
             * via ``propx.``\ `qualifier`, where `qualifier` is one of
               ``setter``, ``getter``, ``deleter``, as appropriate
               (so ``propx.setter`` also refers to ``setx``)

             Thus you can use either ``dc.log_calls_wrapper('setx')``
             or ``dc.log_calls_wrapper('propx.setter')`` where ``dc``
             is a decorated class or an instance thereof.

    :raises: ``TypeError`` if ``fname`` is not a ``str``; ValueError if ``fname``
            isn't as described above or isn't in the ``__dict__`` of *decorated_class*.

    :return: wrapper of ``fname`` if ``fname`` is decorated, ``None`` otherwise.


.. index:: get_own_log_calls_wrapper() (log_calls-decorated class method)

.. py:classmethod:: decorated_class.get_own_log_calls_wrapper()
    :noindex:

    Classmethod of a decorated class. Call from *within* a method or property
    of a decorated class. Typically called on ``self`` from within instance methods,
    on ``cls`` from within classmethods, and on the explicitly named enclosing,
    decorated class ``decorated_class`` from within staticmethods.

    :raises: ``ValueError`` if caller is not decorated.

    :return: the wrapper of the caller (a function), so that the caller
             can access its own `log_calls` attributes.

    See the section :ref:`log_message_in_class`, which illustrates the use
    of ``get_own_log_calls_wrapper`` from within every kind of callable in a class.


