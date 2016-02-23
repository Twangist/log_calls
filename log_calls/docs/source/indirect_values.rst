.. _indirect_values:

Indirect Values of Keyword Parameters
#######################################################

.. comment chapter title was: Indirect Values (Dynamic Parameter Values)

Most parameters of `log_calls` (all :ref:`settings <what-is-a-setting>` paramaters
except ``prefix`` and ``max_history``) can take two kinds of values: *direct* and
*indirect*, which you can think of as *static* and *dynamic* respectively.
Direct/static values are actual values, such as those computed when the definition
of a decorated callable is interpreted, e.g. ``enabled=True``, ``args_sep=" / "``.
As discussed in the previous chapter, :ref:`dynamic_control_of_settings`, the values
of parameters are set once and for all when the Python interpreter creates a callable
object from the source code of a decorated function or method. Even if you use
a variable as the value of a setting, subsequently changing the variable's value
has no effect on the decorator's setting.

`log_calls` provides yet another way to overcome this limitation, in addition to
those described in the previous two chapters: *indirect values*.

.. topic:: *Caveat*

    Using this capability is more intrusive than the approaches to dynamically changing
    settings already discussed: it introduces more "debug-only" code which you'll have
    to ensure doesn't run in production. As such, it's less appealing. However, it has
    its place, in demos and producing documentation.

Definition and basic examples
=================================

.. index:: indirect value (of a setting parameter)

`log_calls` lets you specify any "setting" parameter except `prefix` or `max_history`
with one level of indirection, by using *indirect values*:


    indirect value of a :ref:`setting <the-settings>` parameter
        A string that names a keyword parameter of a decorated callable.
        When the callable is called, the value of *that* keyword argument
        is used as the value of the setting.

To specify an indirect value for a parameter whose normal values are (or can be) ``str``s
(this applies only to ``args_sep`` and ``logger``, at present), append an ``'='`` to the
value. For consistency, any indirect value can end in a trailing ``'='``, which is stripped.
Thus, ``enabled='enable_='`` indicates an indirect value *to be supplied* with the keyword
``enable_``.

Explicit indirect values
----------------------------

An indirect value can be an explicit keyword argument present in the signature of the callable:

    >>> @log_calls(enabled='enable_')
    ... def f(x, y, enable_=False): pass

Thus, calling ``f`` above without passing a value for ``enable_`` uses the default value
``False`` of ``enable_``, and the call gives no output::

    >>> f(1, 2)

Supplying a value ``True`` for ``enable_`` does give `log_calls` output:

    >>> f(3, 4, enable_=True)    # output:
    f <== called by <module>
        arguments: x=3, y=4, enable_=True
    f ==> returning to <module>



Implicit indirect values
----------------------------

An indirect value doesn't have to be present in the signature of a decorated callable.
It can be an implicit keyword argument that ends up in ``**kwargs``:

    >>> @log_calls(args_sep_=', ')      # same as log_calls default
    ... def g(x, y, **kwargs): pass

When the decorated callable is called, the arguments passed by keyword, and the decorated
callable's explicit keyword parameters with default values, are both searched for the
named parameter; if it is found and of the correct type, *its* value is used;
otherwise a default value is used.

Here, the value of the ``args_sep`` setting will be the default value given for ``args_sep_``:

    >>> g(1, 2)
    g <== called by <module>
        arguments: x=1, y=2
    g ==> returning to <module>

whereas here, the ``args_sep`` value used will be ``' $ '``:

    >>> g(3, 4, args_sep_=' $ ')
    g <== called by <module>
        arguments: x=3 $ y=4 $ **kwargs={'args_sep_': ' $ '}
    g ==> returning to <module>


.. note:: If an indirect value is specified for ``enabled`` and it is "not found", then
 the default value of ``False`` is used. For example:

    >>> @log_calls(enabled='enable_')
    ... def h(**kwargs): pass

 Here, the indirect value ``enable_`` has no default value — there is no default indirect
 value for ``enabled``. In this special case only, the enabled setting will be ``False``
 if no value is supplied for ``enable_`` in a call to ``h``:

    >>> h()             # no output
    >>> h(enable_=True) # output:
    h <== called by <module>
        arguments: **kwargs={'enable_': True}
    h ==> returning to <module>


.. _indirect-values-in-settings-dicts-ands-files:

Indirect values in settings dicts and files
========================================================

In a settings file, the value of a keyword is treated as an indirect value
if it's enclosed in (single or double) quotes and its last non-quote character
is `'='`. For example::

    ``file='file_='``

Of course, indirect values can be used in settings dicts as well, and there, only indirect
values of ``args_sep`` and ``logger`` require a trailing ``=``.

.. _log_call_settings-indirect:

Using ``log_calls_settings`` to set indirect values
=========================================================

Similarly, it's perfectly legitimate to assign an indirect value to a setting
via ``log_calls_settings``:

    >>> @log_calls(enabled=False)
    ... def g(*args, **kwargs):
    ...     return sum(args)
    >>> g(0, 1, 2)              # no log_calls output
    3
    >>> g.log_calls_settings.enabled = 'enable_log_calls='
    >>> g(1, 2, 3, enable_log_calls=True)
    g <== called by <module>
        arguments: *args=(1, 2, 3), **kwargs={'enable_log_calls': True}
    g ==> returning to <module>
    6


.. _format-from-above:

Controlling format 'from above'
========================================================

This indirection mechanism allows a caller to control the appearance
of logged calls lower in the call chain, provided all decorated callables
use the same indirect parameter keywords.

In the next example, the separator value supplied to ``g`` by keyword argument
propagates to ``f``. Note that the arguments ``42`` and ``99`` end up in ``g``'s
positional *varargs* tuple.

    >>> @log_calls(args_sep='sep=')
    ... def f(a, b, c, **kwargs): pass
    >>> @log_calls(args_sep='sep=')
    ... def g(a, b, c, *g_args, **g_kwargs):
    ...     f(a, b, c, **g_kwargs)
    >>> g(1,2,3, 42, 99, sep='\\n')       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS, +SKIP
    g <== called by <module>
        arguments:
            a=1
            b=2
            c=3
            *g_args=(42, 99)
            **g_kwargs={'sep': '\\n'}
        f <== called by g
            arguments:
                a=1
                b=2
                c=3
                **kwargs={'sep': '\\n'}
        f ==> returning to g
    g ==> returning to <module>


.. _kwargs-paradigms:

Paradigms for handling keyword parameters
==============================================

Several uses of "indirect values" described in this section rely on multiple functions and methods
treating ``**kwargs`` as a kind of "common area" or "bulletin board" – a central store for data
of common interest. This paradigm for ``**kwargs`` handling, which we might call *promiscuous cooperation*,
conflicts with the one usually espoused, for example in discussions about the design of composable classes
which cooperatively call ``super()``. In his article `Python's super() considered super! <http://rhettinger.wordpress.com/2011/05/26/super-considered-super/>`_,
Raymond Hettinger clearly describes that approach as one in which:

|    every method [``f``, say, is] cooperatively designed to accept keyword arguments
|    and a keyword-arguments dictionary, to remove any arguments that it needs,
|    and to forward the remaining arguments using ``**kwds`` [via ``super().f(..., **kwds)``,
|    where ``...`` are positional arguments], eventually leaving the dictionary empty
|    for the final call in the chain.
|

Certainly, this condition implies that a subclass's implementation of a method
should never share keywords with a parent class's implementation.
But it's more stringent than that. It requires that a class's implementation
of a method *never* share keywords with any implementation of that method
in *any* class that might *ever* be on its `mro <https://docs.python.org/3/glossary.html#term-method-resolution-order>`_
list. Indeed, following this prescription, an implementation simply *can't* share keyword parameters:
each method will "remove any [parameters] that it needs" before passing
the baton via ``super()`` to its kinfolk further on down the mro list.
In the presence of multiple inheritance, which alters a class's static mro,
this might be difficult to guarantee.

This is a clear if stern approach to cooperation, one consistent
with the behavior of certain "final calls in the chain" that land in core Python.
For example, ``object.__init__`` and ``type.__init__`` raise an exception
if they receive any ``**kwargs``. (Would that they didn't: this is often a nuisance.)
But the "promiscuous" paradigm of cooperation is also valid and useful,
and causes no harm as long as it's clear what all cooperating parties are agreeing *to*.
