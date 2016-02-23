.. include:: _global.rst

.. _whats_new:

What's New in |release|
########################

This chapter catalogs additions and changes in the current release.
:ref:`Appendix II <what_has_been_new>` contains the complete list of
what has been new in earlier versions.


What's New
==========

* `log_calls` and `record_history` can decorate classes	– all, or some, of the
  methods and properties within a class – and their inner classes.

    * The decorators properly decorate instance methods, classmethods, staticmethods and properties
      (whether defined with the ``@property`` decorator or the ``property`` function).

    * Settings provided in the class-level decorator apply to all decorated members
      and inner classes. Members and inner classes can also be individually decorated,
      and (by default) their explicitly given settings supplement and override those given
      at outer levels.

    * ``omit`` and ``only`` keyword parameters to a class decorator let you concisely
      specify which callables to decorate. Each is a sequence of strings specifying methods
      and/or properties — by name, with optional class prefixes, with optional suffixes for
      selecting specific property methods, as well as with wildcards and character-range
      inclusion and exclusion using "glob" syntax.

    * A decorated class has methods ``get_log_calls_wrapper(methodname)``
      and ``get_own_log_calls_wrapper()``, the latter for use by methods and
      properties of the decorated class. These provide easy and uniform ways
      to obtain the wrapper of a decorated method, without the special-case
      handling otherwise (and formerly) required for classmethods and properties.

      `record_history` provides the analogous methods ``get_record_history_wrapper(methodname)``
      and ``get_own_record_history_wrapper()``.

|
    These capabilities are documented in :ref:`decorating_classes`.
|

* `log_calls` and `record_history` have classmethods to programmatically decorate functions,
  classes and class hierarchies, even modules, for situations where altering source code is
  impractical (too many things to decorate) or inadvisable (third-party packages and modules).
  These methods can expedite learning a new codebase:

    * ``decorate_class(baseclass, decorate_subclasses=False, **setting_kwds)``
      decorates a class and optionally all of its subclasses

    * ``decorate_hierarchy(baseclass, **setting_kwds)``
      decorates a class and all of its subclasses

    * ``decorate_function(f, **setting_kwds)``
      decorates a function defined in or imported into the module from which you call this method

    * ``decorate_package_function(f, **setting_kwds)``
      decorates a function in an imported package

    * ``decorate_module_function(f, **setting_kwds)``
      decorates a function in an imported package or module

    * ``decorate_module(mod: 'module', functions=True, classes=True, **setting_kwds)``
      decorates all functions and classes in a module.

|
    These are documented in :ref:`decorating_functions_class_hierarchies_modules`.
|

* `log_calls` has classmethods to globally set and reset default values for settings, program-wide:

    * ``set_defaults(new_default_settings=None, **more_defaults)``

    * ``reset_defaults()``

  as well as classmethods to retrieve the current defaults and the "factory defaults",
  each as an ``OrderedDict``:

    * ``get_defaults_OD()``

    * ``get_factory_defaults_OD()``

|
    These are documented in :ref:`set_reset_defaults`.
|

* The ``log_exprs()`` method, added as an attribute to decorated callables, allows a wrapped callable
  to easily "dump" values of variables and expressions. Simply pass it one or more expressions,
  as strings; it prints the expressions together with their current values. See :ref:`log_exprs_method`.

* New keyword parameters:

    * ``NO_DECO``, a "kill switch". When true,
      the decorator does nothing, returning the decorated callable or class itself, unwrapped
      and unaltered. Using this parameter in a settings file or dictionary lets you toggle
      "true bypass" with a single switch, e.g. for production, without having to comment
      out every decoration.

    * ``name``, a literal string or a format string, lets you specify a custom name
      for a decorated callable.

    * ``override``, a boolean, intended mainly for use with `log_calls` as a functional
      and with the ``decorate_*`` methods, allows updating the explicit settings of
      already decorated classes and callables.

    * ``mute``, a three-valued setting:

        - mute nothing (default)
        - mute output about calls but allow ``log_message()`` and ``log_exprs()`` output
        - mute everything.

* Global mute, ``log_calls.mute``, which can assume the same values as the new ``mute`` setting.

* Classmethods ``log_calls.version()`` and ``record_history.version()`` return the version string.


What's Changed
==============

* The ``indent`` setting is now by default ``True``.

* By default, the display name for a function or method is now its ``__qualname__``,
  which in the case of methods includes class name. This makes unnecessary
  what was probably the main use case of ``prefix``.

* `record_history` can now use ``log_message()`` and ``log_exprs()``. Output is always
  via ``print``.

* Fixed: ``log_message()`` formerly would blow up if called on a function or method
  for which logging was disabled. It now produces no output in that situation.

* ``prefix`` is mutable in `log_calls` and `record_history`.

* Fixed, addressed: double-decoration no longer raises an exception.
  Doing so doesn't wrap another decorator around an already wrapped function or method,
  but merely adjusts the settings of the decorated callable.

* Change to ``__repr__`` handling in the ``arguments`` section of output:
  use ``object.__repr__`` for objects still in construction
  (i.e. whose ``__init__`` methods are still active),
  otherwise use ``repr``.

* `log_calls` won't itself decorate ``__repr__`` methods (it will decorate them instead
  with :func:`reprlib.recursive_repr`); `record_history` can decorate ``__repr__``.

* Removed the deprecated ``settings_path`` keyword parameter.

* Officially, explicitly requires Python 3.3+. The package won't install on earlier versions.

* For consistency with the ``get*_defaults_OD()`` methods, the ``as_OrderedDict()`` method
  of the "settings" objects (e.g. ``log_calls_settings``) has been renamed ``as_OD()``.
  Note, ``as_OrderedDict()`` is still supported but is now deprecated. You'll have to run
  the Python interpreter with the ``-Wd`` flag to see the deprecation warning(s),
  which include the file names and line numbers where ``as_OrderedDict()`` occurs.
  (Since Python 3.2, DeprecationWarnings are by default not displayed.)
