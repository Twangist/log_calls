.. _keyword_parameters_reference:

Appendix I: Keyword Parameters Reference
#########################################

The `log_calls` decorator has several keyword parameters, all with hopefully sensible defaults.

.. _settings-appendix-I:

Keyword parameters for "settings"
============================================

+---------------------+-------------------+-------------------------------------------------------------+
| Keyword parameter   | Default value     || Description                                                |
+=====================+===================+=============================================================+
| ``enabled``         | ``1`` (``True``)  || An ``int``. If positive (or ``True``), then `log_calls`    |
|                     |                   || will output (or "log") messages. If false ("disabled":     |
|                     |                   || ``0``, alias ``False``), `log_calls` won't output messages |
|                     |                   || or record history but will continue to increment the       |
|                     |                   || ``stats.num_calls_total`` call counter. If negative        |
|                     |                   || ("bypassed"), `log_calls` won't do anything.               |
+---------------------+-------------------+-------------------------------------------------------------+
| ``args_sep``        | ``', '``          || ``str`` used to separate arguments. The default lists      |
|                     |                   || all args on the same line. If ``args_sep`` is (or ends     |
|                     |                   || in) ``'\n'``, then additional spaces are appended to       |
|                     |                   || the separator for a neater display. Other separators       |
|                     |                   || in which ``'\n'`` occurs are left unchanged, and are       |
|                     |                   || untested – experiment/use at your own risk.                |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_args``        | ``True``          || If true, arguments passed to the decorated callable,       |
|                     |                   || and default values used, will be logged.                   |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_retval``      | ``False``         || If true, log what the decorated callable returns.          |
|                     |                   || At most 77 chars are printed, with a trailing ellipsis     |
|                     |                   || if the value is truncated.                                 |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_exit``        | ``True``          || If true, the decorator will log an exiting message         |
|                     |                   || after the decorated callable returns, and before           |
|                     |                   || returning what the callable returned. The message          |
|                     |                   || is of the form                                             |
|                     |                   ||         ``f returning to ==> caller``                      |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_call_numbers``| ``False``         || If true, display the (1-based) number of the call,         |
|                     |                   || e.g.                                                       |
|                     |                   ||         ``f [3] called by <== <module>``                   |
|                     |                   || and                                                        |
|                     |                   ||         ``f [3] returning to ==> <module>``                |
|                     |                   || for the 3rd logged call. These would correspond to         |
|                     |                   || the 3rd record in the callable's call history,             |
|                     |                   || if ``record_history`` is true.                             |
+---------------------+-------------------+-------------------------------------------------------------+
| ``log_elapsed``     | ``False``         || If true, display how long the callable took to execute,    |
|                     |                   || in seconds — both elapsed time and process time.           |
+---------------------+-------------------+-------------------------------------------------------------+
| ``indent``          | ``False``         || When true, each new level of logged messages is            |
|                     |                   || indented by 4 spaces, giving a visualization               |
|                     |                   || of the call hierarchy.                                     |
+---------------------+-------------------+-------------------------------------------------------------+
| ``prefix``          | ``''``            || A ``str`` with which to prefix the callable's name         |
|                     |                   || in logged messages: on entry, in reporting return          |
|                     |                   || values (if ``log_retval`` is true) and on exit (if         |
|                     |                   || ``log_exit`` is true).                                     |
+---------------------+-------------------+-------------------------------------------------------------+
| ``file``            | ``sys.stdout``    || If ``logger`` is ``None``, a stream (an instance of type   |
|                     |                   || ``io.TextIOBase``) to which `log_calls` will print its     |
|                     |                   || messages. This value is supplied to the ``file``           |
|                     |                   || keyword parameter of the ``print`` function.               |
+---------------------+-------------------+-------------------------------------------------------------+
| ``mute``            | ``0`` (``False``) || Three-valued ``int`` that controls amount of output:       |
|                     |                   ||   ``log_calls.MUTE.NOTHING`` (0) — mute nothing            |
|                     |                   ||   ``log_calls.MUTE.CALLS``   (1) —                         |
|                     |                   ||          mutes `log_calls` own output, but allows          |
|                     |                   ||          output of ``log_message`` and ``log_exprs``       |
|                     |                   ||   ``log_calls.MUTE.ALL``     (2) — mute all output         |
+---------------------+-------------------+-------------------------------------------------------------+
| ``logger``          | ``None``          || If not ``None``, either a logger (a ``logging.Logger``     |
|                     |                   || instance), or the name of a logger (a ``str`` that will    |
|                     |                   || be passed to ``logging.getLogger()``); that logger         |
|                     |                   || will be used to write messages, provided it has            |
|                     |                   || handlers; otherwise, ``print`` is used.                    |
+---------------------+-------------------+-------------------------------------------------------------+
| ``loglevel``        | ``logging.DEBUG`` || Logging level, ignored unless a logger is specified.       |
|                     |                   || This should be one of the logging levels defined by        |
|                     |                   || the ``logging`` module, or a custom level.                 |
+---------------------+-------------------+-------------------------------------------------------------+
| ``record_history``  | ``False``         || If true, a list of records will be kept, one for each      |
|                     |                   || logged call to the decorated callable. Each record         |
|                     |                   || holds: call number (1-based), arguments, defaulted         |
|                     |                   || keyword arguments, return value, time elapsed,             |
|                     |                   || time of call, prefixed name, caller (call chain).          |
|                     |                   || The value of this attribute is a ``namedtuple``.           |
+---------------------+-------------------+-------------------------------------------------------------+
| ``max_history``     | ``0``             || An ``int``.                                                |
|                     |                   || If *value* > 0, store at most *value*-many records,        |
|                     |                   || records, oldest records overwritten;                       |
|                     |                   || if *value* ≤ 0, store unboundedly many records.            |
|                     |                   || Ignored unless ``record_history`` is true.                 |
|                     |                   || This setting can be changed only by calling                |
|                     |                   ||  `wrapper`\ ``.stats.clear_history(max_history=0)``        |
|                     |                   || (q.v.) on the `wrapper` of a decorated callable.           |
+---------------------+-------------------+-------------------------------------------------------------+

Of these, only ``prefix`` and ``max_history`` cannot be indirect, and only ``max_history`` is immutable.

.. _non-settings-appendix-I:

Other keyword parameters (non-"settings")
============================================

+---------------------+-------------------+------------------------------------------------------------------+
| Keyword parameter   | Default value     |   Description                                                    |
+=====================+===================+==================================================================+
| ``settings``        | ``None``          || A dict mapping settings keywords and/or ``NO_DECO``             |
|                     |                   || to values — a *settings dict* — or a string giving              |
|                     |                   || the pathname to a *settings file* containing settings           |
|                     |                   || and values. If the pathname is a directory and not a file,      |
|                     |                   || `log_calls` looks for a file ``.log_calls`` in that directory;  |
|                     |                   || otherwise, it looks for the named file.                         |
|                     |                   || The format of a settings file is: zero or more lines of the     |
|                     |                   || form *setting* = *value*; lines whose first non-whitespace      |
|                     |                   || character is ``'#'`` are comments. These settings are           |
|                     |                   || a baseline; other settings passed to `log_calls` can            |
|                     |                   || override their values.                                          |
+---------------------+-------------------+------------------------------------------------------------------+
| ``name``            | ``''``            || Specifies the display name of a decorated callable, if          |
|                     |                   || nonempty, and then, it must be a ``str``, of the form:          |
|                     |                   || * the preferred name of the callable (a string literal), or     |
|                     |                   || * an old-style format string with one occurrence of ``%s``,     |
|                     |                   ||   which the ``__name__`` of the decorated callable replaces.    |
+---------------------+-------------------+------------------------------------------------------------------+
| ``omit``            | ``tuple()``       || A string or sequence of strings designating callables of        |
|                     |                   || a class. Supplied to a class decorator, ignored in function     |
|                     |                   || decorations. The designated callables will *not* be decorated.  |
|                     |                   || Each of these "designators" can be a name of a method           |
|                     |                   || or property, a name of a property with an appended              |
|                     |                   || qualifier ``.getter``, ``.setter``, or ``.deleter``; it can     |
|                     |                   || have prefixed class names (``Outer.Inner.mymethod``).           |
|                     |                   || It can also contain "glob" wildcards ``*?``, character sets     |
|                     |                   || ``[aqrstUWz_]``, character ranges ``[r-t]``, combinations       |
|                     |                   || of these ``[a2-9f-hX]``, and complements ``[!acr-t]``.          |
|                     |                   || Allowed formats:                                                |
|                     |                   || ``'f'``,   ``'f g h'``,   ``'f, g, h'``, ``[f, g, h]``,         |
|                     |                   | ``(f, g, h)``                                                    |
+---------------------+-------------------+------------------------------------------------------------------+
| ``only``            | ``tuple()``       || A string or sequence of strings designating callables of        |
|                     |                   || a class. Supplied to a class decorator, ignored in function     |
|                     |                   || decorations. Only the designated callables will be              |
|                     |                   || decorated, excluding any specified by ``omit``. These           |
|                     |                   || "designators" are as described for ``omit``. Allowed formats    |
|                     |                   || of sequences of designators are also as described for ``omit``. |
+---------------------+-------------------+------------------------------------------------------------------+
| ``override``        | ``False``         || `log_calls` respects explicitly given settings of already-      |
|                     |                   || decorated callables and classes. Classes are decorated          |
|                     |                   || from the inside out, so explicitly given settings of any        |
|                     |                   || inner decorators are unchanged by an outer class decorator.     |
|                     |                   || To give the settings of the outer decorator priority,           |
|                     |                   || supply it with ``override=True``.                               |
|                     |                   || ``override`` can be used with the ``log_calls.decorate_*``      |
|                     |                   || classmethods, in order to change existing settings              |
|                     |                   || of decorated callables or classes.                              |
+---------------------+-------------------+------------------------------------------------------------------+
| ``NO_DECO``         | ``False``         || When true, prevents `log_calls` from decorating a callable      |
|                     |                   || or class. Intended for use at program startup, it provides      |
|                     |                   || a single "true bypass" switch when placed in a global           |
|                     |                   || *settings dict* or *settings file*.                             |
+---------------------+-------------------+------------------------------------------------------------------+
