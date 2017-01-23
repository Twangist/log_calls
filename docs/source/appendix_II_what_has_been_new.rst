.. _what_has_been_new:

Appendix II: What Has Been New
####################################################

This document collects the full **What's New** sections of all earlier `log_calls` releases.


* 0.2.5.post3

    * Later binding for ``prefix``, though it's still not dynamically changeable.

* *0.2.5.post1* & *0.2.5.post2*

    * Silly fixups (release-bungling)

* **0.2.5**

  Performance timing/profiling enhancements & additions

    * Both elapsed time and process time are both reported now.
      Python 3.3+ enhances the ``time`` module (see :pep:`418`), and
      we take advantage of the new functions
      `perf_counter <https://docs.python.org/3/library/time.html?highlight=time#time.perf_counter>`_
      and `process_time <https://docs.python.org/3/library/time.html?highlight=time#time.process_time>`_.

        * Use ``time.perf_counter``, ``time.process_time`` (Python 3.3+).

        * Added ``stats.process_secs_logged`` attribute.

        * Added ``process_secs`` column to call history (new field for ``CallRecord``\ s).

        * ``log_elapsed`` reports both elapsed and process times.

    * Optimized the decorator wrapper, ~15% speedup

      (still trivial with ~big data, see the IPython notebook
      `history_to_pandas-and-profiling <http://www.pythonhosted.org/log_calls/history_to_pandas-and-profiling.html>`_).

    * Added a "true bypass" feature: when ``enabled`` < 0, adjourn to the decorated function immedately, 
      with no further processing. Again, not a speed speed demon – see the IPython notebook referenced above.

    * Deprecation warning issued if ``settings_path`` parameter used.

      (You'll see this only if you run the Python interpreter with the ``-W <action>`` option, 
      where ``<action>`` is any `valid action string <https://docs.python.org/3/using/cmdline.html#cmdoption-W>`_
      other than ``ignore``, e.g. ``default``.)

    * Updated tests and docs to reflect these changes.

* *0.2.4.post4*

    * *(docs & description changes only, no code changes)*

* *0.2.4.post3*

    * *(never existed)*

* **0.2.4.post2**

    * The ``settings`` parameter (formerly ``settings_path``) lets you specify
      default values for multiple settings, either as a dictionary or as a file.
      The ``settings_path`` parameter is deprecated, as ``settings`` is a superset.
      See the documentation `<http://www.pythonhosted.org/log_calls#settings-parameter>`_
      for details, discussion and examples.

* **0.2.4.post1**

    * ``settings_path`` feature: allow ``file=sys.stderr`` in settings files, under IPython too; 
      neater internals of settings file parsing.

* **0.2.4**

    * The new ``settings_path`` parameter lets you specify a file containing default values 
      for multiple settings. See the documentation `<http://www.pythonhosted.org/log_calls#settings-parameter>`_
      for details, discussion and examples.

    * You can now use a logger name (something you'd pass to ``logging.getLogger()``) 
      as the value of the ``logger`` setting.

    * The ``indent`` setting now works with loggers too. See examples:

        * using ``log_message`` as a general output method that works as expected,
          whatever the destination – ``stdout``, another stream, a file, or a logger
          [in ``tests/test_log_calls_more.py``, docstring of
          ``main__log_message__all_possible_output_destinations()``];

        * setting up a logger with a minimal formatter that looks just like
          the output of ``print`` [in ``tests/test_log_calls_more.py``,
          docstring of ``main__logging_with_indent__minimal_formatters()``].

    * Added the decorator ``used_unused_keywords`` to support the
      ``settings_path`` feature,
      and made it visible (you can import it from the package) because it's
      more broadly useful. This decorator lets a function obtain, on a per-call
      basis, two dictionaries of its explicit keyword arguments and their values:
      those which were actually passed by the caller, and those which were not
      and received default values. For examples, see the docstring of ``main()``
      in ``used_unused_kwds.py``.

    * When displaying returned values (``log_retval`` setting is true), the maximum
      displayed length of values is now 77, up from 60, not counting trailing ellipsis.

    * The deprecated ``indent_extra`` parameter to ``log_message`` is gone.

    * Little bug fixes, improvements.
    
* **0.2.3** and **0.2.3.post** *N*

    * A better signature for "the indent-aware writing method ``log_message()``",
      and more, better examples of it — full docs `<http://www.pythonhosted.org/log_calls#log_message>`_.

* **0.2.2**

    * "The indent-aware writing method ``log_message()``", which decorated functions
      and methods can use to write extra debugging messages that align nicely with
      `log_calls` messages.

    * Documentation `<http://www.pythonhosted.org/log_calls#log_message>`_
      for ``log_message()``.

    * Documentation `<http://www.pythonhosted.org/log_calls#accessing-own-attrs>`_
      for how functions and methods can access the attributes that `log_calls`
      adds for them, within their own bodies.

* **0.2.1**

    * The `stats.history_as_DataFrame attribute <http://www.pythonhosted.org/log_calls/record_history.html#stats.history_as_DataFrame>`_,
      whose value is the call history of a decorated function as a
      `Pandas <http://pandas.pydata.org>`_
      `DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_
      (if Pandas is installed; else ``None``).

    * An IPython notebook (``log_calls/docs/history_to_pandas.ipynb``,
      which compares the performance of using `record_history` *vs* a vectorized
      approach using `numpy <http://www.numpy.org/>`_ to amass medium to large datasets,
      and which concludes that if you can vectorize, by all means do so.

* **0.2.0**

    * Initial public release.
