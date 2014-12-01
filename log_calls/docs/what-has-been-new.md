# *log_calls* — What Has Been New

This document collects the full **What's New** sections of all `log_calls` releases.

---

* **0.2.5**</br>
Performance timing/profiling enhancements & additions.</br>
    * Both elapsed (wall) and CPU (process) time are now both reported.</br>
    Python 3.3+ enhances the `time` module (*see [PEP 418](https://www.python.org/dev/peps/pep-0418/); also see the Python 3 docs for the new functions [`perf_counter`](https://docs.python.org/3/library/time.html?highlight=time#time.perf_counter) and [`process_time`](https://docs.python.org/3/library/time.html?highlight=time#time.process_time)*), and we take advantage of the new functionaility when it's available.</br> (*Under Py < 3.3 `log_calls` reports elapsed and CPU times as the same number, so as not to further complicate user experience, docs and tests with special appearance and behavior for older Python versions.*)</br>
        * Use `time.perf_counter`, `time.process_time` if available (Python 3.3+), otherwise use `time.time` as in earlier versions.</br>
        * Added `stats.CPU_secs_logged` attribute.
        * Added `CPU_secs` column to call history (new field for `CallRecord`s).
        * `log_elapsed` reports both elapsed and CPU times.
    * Optimized the decorator wrapper, ~15% speedup</br> (still trivial with ~big data, see the IPython notebook [history_to_pandas-and-profiling](http://www.pythonhosted.org/log_calls/history_to_pandas-and-profiling.html)).
    * Added a "true bypass" feature: when `enabled` < 0, adjourn to the decorated function immedately, with no further processing. Again, not a speed speed demon – see the IPython notebook referenced above.
    * Deprecation warning issued if `settings_path` parameter used.</br> (You'll see this only if you run the Python interpreter with the `-W <action>` option, where `<action>` is any [valid action string](https://docs.python.org/3/using/cmdline.html#cmdoption-W) other than `ignore`, e.g. `default`.)
    * Updated tests and docs to reflect these changes.
</br></br>
* *0.2.4.post4*
    * *(docs & description changes only, no code changes)*    
* *0.2.4.post3*
    * *(never existed)*    
* **0.2.4.post2**
    * The `settings` parameter (formerly `settings_path`) lets you specify default values for multiple settings either as a dictionary, or as a file. The `settings_path` parameter is deprecated, as `settings` is a superset. See the documentation [here](http://www.pythonhosted.org/log_calls#settings-parameter) for details, discussion and examples.

* **0.2.4.post1**
    * `settings_path` feature: allow `file=sys.stderr` in settings files, under IPython too; neater internals of settings file parsing.
* **0.2.4**
    * The new `settings_path` parameter lets you specify a file containing default values for multiple settings. See the documentation [here](http://www.pythonhosted.org/log_calls#settings-parameter) for details, discussion and examples.
    * You can now use a logger name (something you'd pass to `logging.getLogger()`) as the value of the `logger` setting.
    * The `indent` setting now works with loggers too. See examples:
        * using `log_message` as a general output function that works as expected, whatever the destination – `stdout`, another stream, a file, or a logger [in `tests/test_log_calls_more.py`, docstring of `main__log_message__all_possible_output_destinations()`];
        * setting up a logger with a minimal formatter that looks just like the output of `print` [in `tests/test_log_calls_more.py`, docstring of  `main__logging_with_indent__minimal_formatters()`].
    * Added the decorator `used_unused_keywords` to support the `settings_path` feature, and made it visible (you can import it from the package) because it's more broadly useful. This decorator lets a function obtain, on a per-call basis, two dictionaries of its explicit keyword arguments and their values: those which were actually passed by the caller, and those which were not and received default values. For examples, see the docstring of `main()` in `used_unused_kwds.py`.
    * When displaying returned values (`log_retval` setting is true), the maximum displayed length of values is now 77, up from 60, not counting trailing ellipsis.
    * The deprecated `indent_extra` parameter to `log_message` is gone.
    * Little bug fixes, improvements.
    
* **0.2.3** and **0.2.3.post** *N*
    * A better signature for [the indent-aware writing method `log_message()`](#log_message), and more, better examples of it — full docs [here](http://www.pythonhosted.org/log_calls#log_message).

* **0.2.2** 
    * [The indent-aware writing method `log_message()`](#log_message), which decorated functions and methods can use to write extra debugging messages that align nicely with `log_calls` messages.
    * [Documentation](http://www.pythonhosted.org/log_calls#log_message) for `log_message()`.
    * [Documentation](http://www.pythonhosted.org/log_calls#accessing-own-attrs) for how functions and methods can access the attributes that `log_calls` adds for them, within their own bodies.
* **0.2.1**
    * The [`stats.history_as_DataFrame` attribute](http://www.pythonhosted.org/log_calls/record_history.html#stats.history_as_DataFrame), whose value is the call history of a decorated function as a [Pandas](http://pandas.pydata.org) [DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe) (if Pandas is installed; else `None`).
    * An IPython notebook (`log_calls/docs/history_to_pandas.ipynb`, browsable as HTML [here](http://www.pythonhosted.org/log_calls/history_to_pandas.html)) which compares the performance of using `record_history` *vs* a vectorized approach using [numpy](http://www.numpy.org/) to amass medium to large datasets, and which concludes that if you can vectorize, by all means do so.
* **0.2.0**
    * Initial public release.
    
