############################################################
`log_calls` — A Decorator for Debugging and Profiling
############################################################

`log_calls` is a Python 3.3+ decorator that can print a lot of useful information
about calls to decorated functions, methods and properties. The decorator can
write to ``stdout``, to another stream or file, or to a logger. `log_calls`
provides methods for printing your own debug messages to its output stream,
and for easily "dumping" variables and expressions paired with their values.
It can decorate individual functions, methods and properties; but it can also
programmatically decorate callable members of entire classes and class hierarchies,
even of entire modules, with just a single line — which can greatly expedite learning
a new codebase.

In short, `log_calls` can save you from writing, rewriting, copying, pasting and
tweaking a lot of *ad hoc*, debug-only, boilerplate code — and it can keep *your*
codebase free of that clutter.

For each call to a decorated function or method, `log_calls` can show you:

* the caller (in fact, the complete call chain back to another `log_calls`-decorated caller,
  so there are no gaps in chains displayed)
* the arguments passed to the function or method, and any default values used
* nesting of calls, using indentation
* the number of the call (whether it's the 1\ :superscript:`st` call, the 2\ :superscript:`nd`,
  the 103\ :superscript:`rd`, ...)
* the return value
* the time it took to execute
* and more!

These and other features are optional and configurable settings, which can be specified
for each decorated callable via keyword parameters, as well as *en masse* for a group of
callables all sharing the same settings. You can examine and change these settings
on the fly using attributes with the same names as the keywords, or using a dict-like
interface whose keys are the keywords.

`log_calls` can also collect profiling data and statistics, accessible at runtime, such as:

* the number of calls to a function
* total time taken by the function
* the function's entire call history (arguments, time elapsed, return values, callers,
  and more), available as text in CSV format and, if `Pandas <http://pandas.pydata.org>`_
  is installed, as a `DataFrame <http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe>`_.

The package contains two other decorators:

* `record_history`, a stripped-down version of `log_calls`,
  only collects call history and statistics, and outputs no messages;
* `used_unused_keywords` lets a function or method easily determine, per-call,
  which of its keyword parameters were actually supplied by the caller,
  and which received their default values.

This document describes the decorators' features and their use. Th e``tests/``
subdirectory of the distribution archive contains many test suites. These
contain many additional examples, with commentary. As tests, they provide
96+% coverage.
