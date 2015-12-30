#*log_calls* — A decorator for debugging and profiling
---
`log_calls` is a Python 3.3+ decorator that can print alot of useful information about calls to decorated functions, methods and properties. It can write to `stdout`, to another stream or file, or to a logger. It provides methods for writing your own debug messages and for easily "dumping" variables and expressions paired with their values. It can decorate individual functions, methods and properties; but it can also decorate entire classes and class hierarchies, even entire modules, with a single line. In short, `log_calls` can save you from writing, rewriting, copying, pasting and tweaking a lot of ad hoc, boilerplate code — and it can keep your codebase free of that clutter.

For each call to a decorated function or method, `log_calls` can show you:

* the caller (in fact, the complete call chain back to another `log_calls`-decorated caller, so there are no gaps in chains displayed),
* the arguments passed to the function, and any default values used,
* indentation by call level,
* the number of the call (whether it's the 1<sup>st</sup> call, the 2<sup>nd</sup>, the 103<sup>rd</sup>…),
* the function's return value,
* the time the function took to execute,
* and more!

These and other features are optional and configurable settings, which can be specified for each decorated callable via keyword parameters. You can also examine and change these settings on the fly using attributes with the same names as the keywords, or using a dict-like interface whose keys are the keywords. 

`log_calls` can also collect profiling data and statistics, accessible at runtime:

* the number of calls to a function,
* total time taken by the function,
* the function's entire call history (arguments, time elapsed, return values, callers, and more), available as text in CSV format and, if [Pandas](http://pandas.pydata.org) is installed, as a [DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe).

The package contains two other decorators:

* `record_history`, a stripped-down version of `log_calls`, 
only collects call history and statistics, and outputs no messages;
* `used_unused_keywords` lets a function or method easily determine, per-call,
which of its keyword parameters were actually supplied by the caller,
and which received their default values.

This document gives an overview of the decorator's features and their use. A thorough account, including many useful examples, can be found in the complete documentation for [`log_calls`](http://www.pythonhosted.org/log_calls) and [`record_history`](http://www.pythonhosted.org/log_calls/record_history.html). The test suites in `log_calls/tests/` contain many additional examples, with commentary.

##[Version](id:Version)
This document describes version `0.3.0` of `log_calls`.

## [What's New in 0.3.0](id:What's-new)
* `log_calls` and `record_history` can decorate classes	– all (or some) methods and properties within a class – and their inner classes.</br>
    * Properly decorates instance methods, classmethods, staticmethods and properties (whether defined with the `@property` decorator or with the `property` constructor).
    * Settings provided in the class-level decorator apply to all decorated members (and inner classes). Members and inner classes can be individually decorated, and their settings supplement and override those given at the class level.
    * `omit` and `only` keyword parameters to `log_calls` used as a class decorator let you specify which methods to decorate. Each is a sequence of "method specifiers", which allow class prefixes, wildcards and character-range inclusion and exclusion, using "glob" syntax.</br>
    * Decorated classes have methods `get_log_calls_wrapper(methodname)` and decorated methods have the attribute `get_own_log_calls_wrapper()`, which provide easy and uniform ways to obtain the wrapper of a decorated method, without the special-case handling otherwise (and formerly) required for classmethods and property methods.</br>
`record_history` provides the analogous methods `get_record_history_wrapper(methodname)` and `get_own_record_history_wrapper()`</br>
</br>

* `log_calls` classmethods to programmatically decorate classes and functions, even entire modules, for situations where altering source code is impractical (too many things to decorate) or bad practice (third-party modules and packages):
    * `decorate_module(module, functions=True, classes=True, **setting_kwds)`
     decorates functions and classes in an imported package or module;</br>
    * `decorate_class(baseclass, subclasses_too=False, **setting_kwds)`
     decorates a base class and optionally all of its subclasses;</br>
    * `decorate_function(f, **setting_kwds)`
     decorates a function defined or imported in the module from which you call this method;</br>
    * `decorate_external_function(f, **setting_kwds)`
     decorates a function in an imported package or module.</br>
</br>

* `log_calls` classmethods to globally set and reset default values for settings, program-wide:
    * `set_defaults(settings=None, **more_defaults)`, and
    * `reset_defaults()`</br>
</br>
* New keyword parameter `NO_DECO`, a "kill switch". When true, the decorator returns the decorated function or class itself, unwrapped/unaltered. Using this parameter in a settings file or dictionary lets you control "true bypass"" with a single switch, e.g. for production, without having to comment out every decoration.</br>

* `log_exprs` method of a wrapped decorated function or method allows the wrapped callable to write values of variables and expressions. Simply pass it one or more expressions, as strings; it prints the expressions together with their current values.</br>

* New keyword parameter and setting `mute`, 3-valued: mute nothing (default), mute output about calls but allow `log_message` and `log_exprs` output; mute everything.

* Global mute, `log_calls.mute`, which takes on the same values as  the `mute` setting.</br>

* New keyword parameter `name` – a literal string, or an old-style format string with a single `%s` for the name of a function or method, that lets you specify a custom name for a decorated callable.

### [What's changed](id:Changes-3.0)
* The `indent` setting is now by default `True`.

* By default, the display name for a function or method is now its `__qualname__`, which in the case of methods includes class name. This makes unnecessary what was probably the main use case of `prefix`.

* `record_history` can now use `log_message` and `log_exprs`. Output is always via `print`.

* Fixed: `log_message` would blow up if called on a function or method for which logging is disabled. It now produces no output in that situation.
* `prefix` is mutable in `log_calls` and `record_history`.</br>

* Fixed, addressed: double-decoration no longer raises an exception. It doesn't wrap another decorator around an already wrapped function or method, but merely affects the settings of the decorated callable.

* Change to `__repr__` handling in `arguments` section of output:</br>
use `object.__repr__` for objects still in construction (i.e. whose `__init__` methods are still active), otherwise use straightup `repr`.</br>

* `log_calls` cannot (won't) decorate `__repr__`; `record_history` can.</br>

* Removed deprecated `settings_path` keyword parameter.</br>

* Officially, explicitly requires Python 3.3+ – the package won't install on earlier versions.</br>


## What Has Been New (in earlier versions)
See the complete collection [here](http://www.pythonhosted.org/log_calls/what-has-been-new.html).

 
##[Preliminaries](id:Preliminaries)
###[Dependencies and requirements](id:Dependencies-requirements)

The *log_calls* package has no dependencies - it requires no other packages. All it requires is a standard distribution of Python 3.3 or higher (Python 3.4+ recommended).

NOTE: This package *probably* requires the CPython implementation, as it uses internals of stack frames which may well differ in other interpreters. It's not guaranteed to fail with other interpreters, it's just untested. (*If you're able and willing to willing to run the tests under another interpreter, please tell us what you find*.)</br>
In the future, `log_calls` will *probably* work in PyPy3, once that supports Python 3.3, and provided it supports the `inspect` module. Presently (Sept 2015, after the release of Python 3.5) the PyPy3 project has still only reached Python 3.2.5, with no information available as to their next milestone.

###[Installation](id:Installation)
You have two simple options:

1. Download the compressed repository, uncompress it into a directory, and run:

    `$ python setup.py install`
    
    in that directory, or
  
2. run:

    `$ pip install log_calls`
  
  to install `log_calls` from PyPI (the Python Package Index). Here and elsewhere, `$` at the *beginning* of a line indicates your command prompt, whatever it may be.

Whichever you choose, ideally you'll do it in a virtual environment (a *virtualenv*). In Python 3.3+, virtual environments are easier than ever to set up because the standard distribution includes everything you need to do so. For a good overview of these new capabilities, see [Lightweight Virtual Environments in Python 3.4](http://www.drdobbs.com/architecture-and-design/lightweight-virtual-environments-in-pyth/240167069).

###[Running the tests](id:Testing)
Each `*.py` file in the log_calls directory has at least one corresponding test file `test_*.py` in the `log_calls/tests/` directory. The tests provide 96+% coverage. All tests have passed on every tested platform + Python version (3.3.x through 3.5.0); however, that's a sparse matrix :) If you encounter any turbulence, do let us know.

####[Running the tests after installation](id:tests-after-install)
You can run the tests for `log_calls` after installing it, by running the following command:
 
    $ ./run_tests.py [-q | -v | -h]

which takes switches `-q` for "quiet" (recommended), `-v` for "verbose", and `-h` for "help"; or, from the `log_calls/tests` directory:

    $ python -m unittest discover log_calls.tests

####[What to expect](id:tests-ok)
Both of the above commands run all tests in the `log_calls/tests/` directory. If you run either of them, the output you see should end like so:

    ----------------------------------------------------------------------
    Ran 100 tests in 0.499s
    
    OK

indicating that all went well. If any test fails, it will tell you.

##[Getting started – Quick start – Basic examples](id:Basic-usage)

First, let's import the `log_calls` decorator from the package of the same name:

    >>> from log_calls import log_calls

In code, `log_calls` now refers to the decorator, a class (type), and not the module:

    >>> type(log_calls)
    type

The decorator has many options, and thus can take many parameters, but let's first see the simplest examples possible, using no parameters at all. 

### Decorating functions
If you decorate a function with `log_calls`, the decorator writes messages announcing entry to the function and what arguments it received; the function executes, and when it returns the decorator announces that:

    >>> @log_calls()
    ... def f(a, b, c):
    ...     print("--- Hi from f")
    >>> f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3
    --- Hi from f
    f ==> returning to <module>

Adding another decorated function to the call chain presents useful information too:

    >>> @log_calls()
    ... def g(n):
    ...     print("*** Hi from g")
    ...     f(n, 2*n, 3*n)
    ...     print("*** Bye from g")
    >>> g(3)
    g <== called by <module>
        arguments: n=3
    *** Hi from g
        f <== called by g
            arguments: a=3, b=6, c=9
    --- Hi from f
        f ==> returning to g
    *** Bye from g
    g ==> returning to <module>

`log_calls` gives informative output even when call chains include undecorated functions. In the next example, a decorated function `h` calls an undecorated `g2`, which calls calls an undecorated `g1`, which, finally, calls the decorated `f` above. 

    >>> def g1(n): f(n, 2*n, 3*n)
    >>> def g2(n): g1(n)
    >>> @log_calls()
    ... def h(x, y): g2(x+y)

Now let's call `h`:

    >>> h(2, 3)
    h <== called by <module>
        arguments: x=2, y=3
        f <== called by g1 <== g2 <== h
            arguments: a=5, b=10, c=15
    --- Hi from f
        f ==> returning to g1 ==> g2 ==> h
    h ==> returning to <module>

Notice that when writing entry and exit messages for `f`, `log_calls` displays the entire active call chain back to the nearest decorated function, so that there aren't "gaps" in the chain of functions it reports on. If it didn't do this, we'd see only `f <== called by g1` and then `f ==> returning to g1`, which wouldn't tell us the whole story about how control reached `g1` from `h`.

See the [Call chains](#Call-chains) section below for more examples and finer points.

### Decorating methods

Similarly, you can decorate methods within a class:

    >>> class A():
    ...     def __init__(self, n):
    ...         self.n = n
    ... 
    ...     @log_calls()
    ...     def ntimes(self, m):
    ...         return self.n * m

Only the `ntimes` method is decorated:

    >>> a = A(3)            # __init__ called
    >>> a.ntimes(4)                      # doctest: +ELLIPSIS
    A.ntimes <== called by <module>
        arguments: self=<__main__.A object at 0x...>, m=4
    A.ntimes ==> returning to <module>
    12

### Decorating classes

To decorate all methods of a class, simply decorate the class itself:

    >>> @log_calls()
    ... class C():
    ...     def __init__(self, n):
    ...         self.n = n if n >= 0 else -n
    ... 
    ...     @staticmethod
    ...     def revint(x):
    ...         return int(str(x)[::-1])
    ... 
    ...     @property
    ...     def revn(self):
    ...         return self.revint(self.n)

All methods of `C` are now decorated. Creating an instance logs the call to `__init__`:

    >>> c = C(123)                    # doctest: +ELLIPSIS
    C.__init__ <== called by <module>
        arguments: self=<__main__.C object at 0x...>, n=123
    C.__init__ ==> returning to <module>

Accessing its `revn` property calls the staticmethod `revint`, and both calls are logged:

    >>> c.revn                        # doctest: +ELLIPSIS
    C.revn <== called by <module>
        arguments: self=<__main__.C object at 0x...>
        C.revint <== called by C.revn
            arguments: x=123
        C.revint ==> returning to C.revn
    C.revn ==> returning to <module>
    321

If you want to decorate only some of the methods of a class, you *don't* have to individually decorate all the ones you want: the [`omit`](#omit-parameter) and [`only`](#only-parameter) keyword parameters to the class decorator let you control which methods get decorated. 

See the [Decorating classes](#decorating-classes) section below for further information and techniques.

## What *log_calls* can decorate — terminology
In what follows, the phrase "decorated function" appears frequently. It's shorthand for *function or method decorated by `log_calls`*. Unless otherwise indicated, what's said of "decorated functions" also holds for decorated methods. Note that lambda expressions are functions, and can be decorated by using `log_calls` as a higher-order function, without the `@` syntactic sugar:

    >>> f = log_calls()(lambda x: 2 * x)
    >>> f(3)
    <lambda> <== called by <module>
        arguments: x=3
    <lambda> ==> returning to <module>
    6

Sometimes we say "decorated callable", but only for variety. Anything that `log_calls` can decorate is a callable, but not every callable can be decorated by `log_calls`. Whatever `log_calls` can't decorate, it simply returns unchanged. 

#### What is a "callable"?
Loosely, a "callable" is anything that can be called; in Python, the term has a precise meaning, encompassing not only functions and methods but also instances of classes that implement a `__call__` method. A correct though unsatisfying definition is: an object is *callable* iff the builtin `callable` function returns `True` on that object. [The official doc for `callable`](https://docs.python.org/3/library/functions.html?highlight=callable#callable) is good enough, if a bit breezy; complete detail can be found in the stackoverflow Q&A [What is a “callable” in Python?](http://stackoverflow.com/questions/111234/what-is-a-callable-in-python) and in the articles cited there.

#### Examples of callables that `log_calls` cannot decorate
`log_calls` can't decorate callable builtins, such as `len`, and it won't try to — it just returns the builtin:

    >>> len is log_calls()(len)    # No ""wrapper"" around `len` -- not deco'd
    True

It also doesn't decorate objects which are callables by virtue of having a `__call__` method, such as `functools.partial` objects:

    >>> from functools import partial
    >>> def h(x, y): return x + y
    >>> h2 = partial(h, 2)        # so h2(3) == 5
    >>> h2lc = log_calls()(h2)
    >>> h2lc is h2                # not deco'd
    True

But of course, you can decorate a *class*  whose instances are callables (or, specifically, the `__call__` method itself):

    >>> @log_calls()
    ... class Rev():
    ...     def __call__(self, s):  return s[::-1]
    >>> rev = Rev()
    >>> callable(rev)
    True

With its `__call__` method decorated, the output from calling `rev` now explains what it means for the object to be `callable`:

    >>> rev('ABC')                        # doctest: +ELLIPSIS
    Rev.__call__ <== called by <module>
        arguments: self=<Rev object at 0x...>, s='ABC'
    Rev.__call__ ==> returning to <module>
    'CBA'


##[The main parameters](id:main-parameters)

`log_calls` has many features, and thus many, mostly independent, keyword parameters (20 in all). This section covers most of them, one at a time, though of course you can use multiple parameters in any call to the decorator:

* [`args_sep`](#args_sep-parameter)
* [`log_args`](#log_args-parameter)
* [`log_retval`](#log_retval-parameter)
* [`log_exit`](#log_exit-parameter)
* [`log_call_numbers`](#log_call_numbers-parameter)
* [`log_elapsed`](#log_elapsed-parameter)
* [`indent`](#indent-parameter)
* [`name`](#name-parameter)
* [`prefix`](#prefix-parameter)
* [`file`](#file-parameter)
* [`enabled`](#enabled-parameter)
* [`mute`](#mute-parameter-and-global-mute) (also discusses the global mute switch `log_calls.mute`)
* [`settings`](#settings-parameter)   #### TODO cannibalize [The *settings* parameter](http://www.pythonhosted.org/log_calls/index.html#settings-parameter) of the main documentation
* [`NO_DECO`](#NO_DECO-parameter)   #### TODO

#### Parameters discussed in other sections
[Decorating classes](#decorating-classes) discusses the two parameters that control which methods and properties get decorated:

* [`omit`](#omit-parameter) – don't decorate these methods/properties;
* [`only`](#only-parameter) – decorate only these methods/properties, excluding any specified by `omit`.

[Using loggers](#Logging) presents the two parameters that let you output `log_calls` messages to a `Logger`: 

* [`logger`](#logger-parameter) – a logger name or a `logging.Logger` object;
* [`loglevel`](#loglevel-parameter) – `logging.DEBUG`, `logging.INFO`, … or a custom loglevel.</br>

[Call history and statistics](#call-history-and-statistics) discusses the two parameters governing call history collection:

* [`record_history`](#record_history-parameter) governs whether call history is retained, and then
* [`max_history`](#max_history-parameter) controls how much of it (cache size). </br>

###[The *args_sep* parameter (default: `', '`)](id:args_sep-parameter)

The `args_sep` parameter specifies the string used to separate arguments. If the string ends in  (or is) `\n`, additional whitespace is appended so that arguments line up nicely:

    >>> @log_calls(args_sep='\\n')
    ... def f(a, b, c, **kwargs):
    ...     print(a + b + c)
    >>> f(1, 2, 3, u='you')       # doctest: +NORMALIZE_WHITESPACE, +SKIP
    f <== called by <module>
        arguments:
            a=1
            b=2
            c=3
            **kwargs={'u': 'you'}
    6
    f ==> returning to <module>

**NOTE**: *In all the doctest examples in this document, you'll see* `'\\n'`
*where in actual code you'd write* `'\n'`. *This is a `doctest` quirk: all
the examples herein work (as tests, they pass), and they would fail if*
`'\n'` *were used. The only alternative would be to use raw character strings
and write* `r'\n'`, *which is not obviously better.*

###[The *log_args* parameter (default: *True*)](id:log_args-parameter)
When true, as seen in all examples so far by default, arguments passed to the decorated function are written together with their values. If the function's signature contains positional and/or keyword "varargs", these are included if they're nonempty. (These are conventionally named `*args` and `**kwargs`, but `log_calls` will use the names that appear in the function's definition.) Any default values of keyword parameters with no corresponding argument are also logged, on a separate line.

    >>> @log_calls()
    ... def f_a(a, *args, something='that thing', **kwargs): pass
    >>> f_a(1, 2, 3, foo='bar')
    f_a <== called by <module>
        arguments: a=1, *args=(2, 3), **kwargs={'foo': 'bar'}
        defaults:  something='that thing'
    f_a ==> returning to <module>

Here, no argument information is logged at all:

    >>> @log_calls(log_args=False)
    ... def f_b(a, *args, something='that thing', **kwargs): pass
    >>> f_b(1, 2, 3, foo='bar')
    f_b <== called by <module>
    f_b ==> returning to <module>

If a function has no parameters, `log_calls` won't display any "arguments"
section:

    >>> @log_calls()
    ... def f(): pass
    >>> f()
    f <== called by <module>
    f ==> returning to <module>

If a function has parameters but is passed no arguments, `log_calls`
will display `arguments: <none>`, plus any default values used:

    >>> @log_calls()
    ... def ff(*args, **kwargs): pass
    >>> ff()
    ff <== called by <module>
        arguments: <none>
    ff ==> returning to <module>

    >>> @log_calls()
    ... def fff(*args, kw='doh', **kwargs): pass
    >>> fff()
    fff <== called by <module>
        arguments: <none>
        defaults:  kw='doh'
    fff ==> returning to <module>

###[The *log_retval* parameter (default: *False*)](id:log_retval-parameter)
When true, this parameter displays the value returned by the function:

    >>> @log_calls(log_retval=True)
    ... def f(a, b, c):
    ...     return a + b + c
    >>> _ = f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3
        f return value: 6
    f ==> returning to <module>

###[The *log_exit* parameter (default: *True*)](id:log_exit-parameter)

When false, this parameter suppresses the `... ==> returning to ...` line
that indicates the function's return to its caller.

    >>> @log_calls(log_exit=False)
    ... def f(a, b, c):
    ...     return a + b + c
    >>> _ = f(1, 2, 3)
    f <== called by <module>
        arguments: a=1, b=2, c=3

###[The *log_call_numbers* parameter (default: *False*)](id:log_call_numbers-parameter)
`log_calls` keeps a running tally of the number of times a decorated function
is called. You can display this (1-based) number using the `log_call_numbers` parameter:

    >>> @log_calls(log_call_numbers=True)
    ... def f(): pass
    >>> for i in range(2): f()
    f [1] <== called by <module>
    f [1] ==> returning to <module>
    f [2] <== called by <module>
    f [2] ==> returning to <module>

The call number is also displayed with the function name when `log_retval` is also true:

    >>> @log_calls(log_call_numbers=True, log_retval=True)
    ... def f():
    ...     return 81
    >>> _ = f()
    f [1] <== called by <module>
        f [1] return value: 81
    f [1] ==> returning to <module>

This is particularly valuable in the presence of recursion — see the [recursion example](#recursion-example) later, where the feature is used to good effect.

To reset the next call number of a decorated function `f` to 1, call `f.stats.clear_history()`: see [Call history and statistics](#call-history-and-statistics) for more about the `stats` attribute of a decorated function.

###[The *log_elapsed* parameter (default: *False*)](id:log_elapsed-parameter)

For performance profiling, you can measure the time it took a function to execute
by using the `log_elapsed` parameter. When true, `log_calls` reports the time the
decorated function took to complete, in seconds. Both *elapsed time* (or "wall time") and *CPU time* (process time, i.e. kernel + user time, sleep time excluded) are reported:

    >>> @log_calls(log_elapsed=True)
    ... def f(n):
    ...     for i in range(n):
    ...         # do something time-critical
    ...         pass
    >>> f(5000)                 # doctest: +ELLIPSIS
    f <== called by <module>
        arguments: n=5000
        elapsed time: ... [secs], CPU time: ... [secs]
    f ==> returning to <module>

###[The *indent* parameter (default: *True*)](id:indent-parameter)
The `indent` parameter, when true, indents each new level of logged messages by 4 spaces, providing a visualization of the call hierarchy.

A decorated function's logged output is indented only as much as is necessary. Here, the even numbered functions don't indent, so the indented functions that they call are indented just one level more than their "inherited" indentation level:

    >>> @log_calls()
    ... def g1():
    ...     pass
    >>> @log_calls(indent=False)    # no extra indentation for g2
    ... def g2():
    ...     g1()
    >>> @log_calls()
    ... def g3():
    ...     g2()
    >>> @log_calls(indent=False)    # no extra indentation for g4
    ... def g4():
    ...     g3()
    >>> @log_calls()
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
    g4 <== called by g5
        g3 <== called by g4
        g2 <== called by g3
            g1 <== called by g2
            g1 ==> returning to g2
        g2 ==> returning to g3
        g3 ==> returning to g4
    g4 ==> returning to g5
    g5 ==> returning to <module>

###[The *name* parameter (default: `None`)](id:name-parameter)

The `name` parameter lets you change the "display name"" of a function or method. The *display name* is the name by which `log_calls` refers to a decorated callable  in these contexts: when logging a call to, and a return from, the callable; when reporting the its return value; and it's at the end of a [call or return chain](#Call-chains). 

A value provided for the `name` parameter should be a string:

* the preferred name of a function or method (a string literal), or 
* an old-style format string with just one occurrence of `%s`, which the `__name__` of the decorated callable will replace.

For example:

    >>> @log_calls(name='f (STUB)')
    ... def f(): pass
    f (STUB) <== called by <module>
    f (STUB) ==> returning to <module>

Another simple example:

    >>> @log_calls(name='"%s" (lousy name)', log_exit=False)
    ... def g(): pass
    "g" (lousy name) <== called by <module>

This parameter is useful mainly to simplify the display names of inner functions, and to disambiguate the display names of *getter* and *deleter* properties.

The qualified names of inner functions are ungainly – in the following example, the "qualname" of `inner` is `outer.<locals>.inner`:

    >>> @log_calls()
    ... def outer():
    ...     @log_calls()
    ...     def inner(): pass
    ...     inner()
    outer <== called by <module>
        outer.<locals>.inner <== called by outer
        outer.<locals>.inner ==> returning to outer
    outer ==> returning to <module>

You can use the `name` parameter to simplify the displayed name of the inner function:

    >>> @log_calls()
    ... def outer():
    ...     @log_calls(name='%s')
    ...     def inner(): pass
    ...     inner()
    outer <== called by <module>
        inner <== called by outer
        inner ==> returning to outer
    outer ==> returning to <module>

The [Decorating classes](#decorating-classes) section demonstrates the use of `name` with *getter* and *deleter* properties.


###[The *prefix* parameter (default: `''`)](id:prefix-parameter)

The `prefix` keyword parameter lets you specify a string with which to prefix the name of a function or method, thus creating a new *display name* for the decorated callable.

Here's a simple example:

    >>> @log_calls(prefix='*** ')
    ... def f(): pass
    >>> f()
    *** f <== called by <module>
    *** f ==> returning to <module>

Because versions 0.3.0+ of `log_calls` use  `__qualname__` for the display name of decorated functions, what used to be the main use case for `prefix`, prefixing method names with their class name, has gone away. However, `prefix` is not deprecated, at least not presently: for what it's worth, it *is* a setting and can be changed dynamically, neither of which is true of `name`.


###[The *file* parameter (default: *sys.stdout*)](id:file-parameter)
The `file` parameter specifies a stream (an instance of `io.TextIOBase`) to which `log_calls` will print its messages. This value is supplied to the `file` keyword parameter of the `print` function, and, like that parameter, its default value is `sys.stdout`. This parameter is ignored if you've supplied a logger for output using the [`logger`](#logger-parameter) parameter.

When the output stream is the default `sys.stdout`, `log_calls` always uses the current meaning of that expression to obtain its output stream, not just what "sys.stdout" meant at program initialization. Your program can capture, change and redirect `sys.stdout`, and `log_calls` will write to that stream, whatever it currently is. (`doctest` is a fine example of such a program!)

If your program writes to the console a lot, you may not want `log_calls` messages interspersed with your real output: your understanding of both logically distinct streams might be hindered, and it may be better to make them two actually distinct streams. Splitting off the `log_calls` output also be useful for understanding or documentation: you can gather all, and only all, of the `log_calls` messages in one place. The `indent` setting will be respected whether messages go to the console or to a file.

It's not easy to test this feature with `doctest`, so we'll just give an example of writing to `stderr`, and reproduce the output:

    >>> import sys
    >>> @log_calls(file=sys.stderr)
    ... def f(n):
    ...     if n <= 0:
    ...         return 'a'
    ...     return '(%s)' % f(n-1)

Running `>>> f(2)` will return `'((a))'` and will write the following to `stderr`:

    f <== called by <module>
        arguments: n=2
        f <== called by f
            arguments: n=1
            f <== called by f
                arguments: n=0
            f ==> returning to f
        f ==> returning to f
    f ==> returning to <module>

###[The *enabled* parameter (default: *True*)](id:enabled-parameter)

Every example of `log_calls` that we've seen so far has produced output, as they have all used the default value `True` of the `enabled` parameter. Passing `enabled=False` to the decorator suppresses output:

    >>> @log_calls(enabled=False)
    ... def f(a, b, c):
    ...     pass
    >>> f(1, 2, 3)                # no output

This is not totally pointless!, because, as with almost all `log_calls` settings, you can dynamically change the "enabled" state for a particular function or method. (See the later section [Dynamic control of settings](#dynamic-control-of-settings) for information about how.) The above decorates `f` and sets its *initial* "enabled" state to `False`.

The `enabled` setting is in fact an `int`. This can be used advantageously. 
See the section [Using *enabled* as a level of verbosity](http://www.pythonhosted.org/log_calls/index.html#enabling-with-ints) in the full documentation for examples of using different positive values to specify increasing levels of verbosity in `log_calls`-related output.

#### *[Bypass](id:bypass)*
If you supply a negative integer, that is interpreted as *bypass*: `log_calls` immediately calls the decorated function and returns its value. When the value of `enabled` is false (`False` or `0`), the decorator performs a little more processing before delegating to the decorated function (it tallies the call to the function), though of course less than when `enabled` is positive (e.g. `True`).


###[Muting *log_calls* output](id:mute-parameter-and-global-mute)
#### *The* `mute` *parameter* (*default:* `log_calls.MUTE.NOTHING`)
The `mute` parameter enables `log_calls` to behave like the `record_history` decorator, collecting statistics silently which are accessible via the `stats` attribute of a decorated function. The section [Call history and statistics](#call-history-and-statistics)) describes this use `log_calls`.

The `mute` parameter can be given one of three values:

    log_calls.MUTE.NOTHING
    log_calls.MUTE.CALLS
    log_calls.MUTE.ALL

* The default value `log_calls.MUTE.NOTHING` mutes no output. 
* The value `log_calls.MUTE.CALLS` mtes all logging of function call details, but the output of any calls to the methods [`log_message`](#log_message) and [`log_exprs`](#log_exprs) is not suppressed: that output is logged, to the current logging destination (`sys.stdout`, a file or stream, or a logger.)
* The value `log_calls.MUTE.ALL` mutes all output of `log_calls`.

#### *The global mute switch* `log_calls.mute`
#### <p style="background-color: yellow"> TODO TODO TODO TODO TODO</p>

###[The *settings* parameter (default: *None*)](id:settings-parameter)   
#### <p style="background-color: yellow"> TODO TODO TODO TODO TODO</p>
Further details can be found in [The *settings* parameter](http://www.pythonhosted.org/log_calls/index.html#settings-parameter) section of the main documentation.



###[The *NO_DECO* parameter (default: *None*)](id:NO_DECO-parameter)   
#### <p style="background-color: yellow"> TODO TODO TODO TODO TODO</p>

The `NO_DECO` parameter prevents `log_calls` from decorating a function or class. When true, the decorator returns the decorated thing itself, unwrapped/unaltered. It's intended for use at program startup, providing a single "true bypass" switch. *It can only prohibit decoration, it cannot undo decoration.*

Using this parameter in a settings file or dictionary lets you control "true bypass"" with a single switch, e.g. for production, without having to comment out every decoration.



##[Decorating classes](id:decorating-classes)

#### <span style="background-color: yellow"> TODO TODO TODO TODO TODO</span>

Here's a simple class illustrating basic possibilities. All methods are decorated except `__init__`, which is excluded by use of the `omit` parameter. The `length` *property* is additionally decorated to give it the `log_retval` setting, which is merged into the settings of the class decorator (note that in here, `@property` comes first). 

    >>> @log_calls(omit='__init__')
    ... class Point():
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...     @staticmethod
    ...     def distance(pt1, pt2):
    ...         return math.sqrt((pt1.x - pt2.x)**2 + (pt1.y - pt2.y)**2)
    ...     @property
    ...     @log_calls(log_retval=True)
    ...     def length(self):
    ...         return self.distance(self, Point(0, 0))
    ...     def diag_reflect(self):
    ...         self.x, self.y = self.y, self.x
    ...         return self
    ...     def __repr__(self):
    ...         return "Point" + str((self.x, self.y))

In the examples that follow, note that displayed method names are their qualified names (`__qualname__`s) which include the name of their class.

    >>> print("Point(1, 2).diag_reflect() ==", Point(1, 2).diag_reflect())
    Point.diag_reflect <== called by <module>
        arguments: self=Point(1, 2)
    Point.diag_reflect ==> returning to <module>
    Point(1, 2).diag_reflect() == Point(2, 1)

Another example with the same class:

    >>> print("length of Point(1, 2) ~~", round(Point(1, 2).length, 2))
    Point.length <== called by <module>
        arguments: self=Point(1, 2)
        Point.distance <== called by Point.length
            arguments: pt1=Point(1, 2), pt2=Point(0, 0)
        Point.distance ==> returning to Point.length
        Point.length return value: 2.236...
    Point.length ==> returning to <module>
    length of Point(1, 2) ~~ 2.24

#### TODO - *demonstrates the use of the `name` parameter with *getter* and *deleter* properties* ^^^^^

##[Using loggers](id:Logging)
`log_calls` works well with loggers obtained from Python's `logging` module –
that is, objects of type `logging.Logger`.
First, we'll set up a logger with a single handler that writes to the console.
Because `doctest` doesn't capture output written to `stderr` (the default stream
to which console handlers write), we'll send the console handler's output to
`stdout`, using the format `<loglevel>:<loggername>:<message>`.

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> c_formatter = logging.Formatter('%(levelname)8s:%(name)s:%(message)s')
    >>> ch.setFormatter(c_formatter)
    >>> logger = logging.getLogger('a_logger')
    >>> logger.addHandler(ch)
    >>> logger.setLevel(logging.DEBUG)

###The *logger* parameter (default: *None*)

The `logger` keyword parameter tells `log_calls` to write its output using
that logger rather than the `print` function:

    >>> @log_calls(logger=logger)
    ... def somefunc(v1, v2):
    ...     logger.debug(v1 + v2)
    >>> somefunc(5, 16)             # doctest: +NORMALIZE_WHITESPACE
    DEBUG:a_logger:somefunc <== called by <module>
    DEBUG:a_logger:    arguments: v1=5, v2=16
    DEBUG:a_logger:21
    DEBUG:a_logger:somefunc ==> returning to <module>

    >>> @log_calls(logger=logger)
    ... def anotherfunc():
    ...     somefunc(17, 19)
    >>> anotherfunc()       # doctest: +NORMALIZE_WHITESPACE
    DEBUG:a_logger:anotherfunc <== called by <module>
    DEBUG:a_logger:somefunc <== called by anotherfunc
    DEBUG:a_logger:    arguments: v1=17, v2=19
    DEBUG:a_logger:36
    DEBUG:a_logger:somefunc ==> returning to anotherfunc
    DEBUG:a_logger:anotherfunc ==> returning to <module>

The value of `logger` can be either a logger instance (a `logging.Logger`) or a string
giving the name of a logger. Instead of passing the logger instance
as above, we can simply pass `a_logger`:

    >>> @log_calls(logger='a_logger')
    ... def yetanotherfunc():
    ...     return 42
    >>> _ = yetanotherfunc()       # doctest: +NORMALIZE_WHITESPACE
    DEBUG:a_logger:yetanotherfunc <== called by <module>
    DEBUG:a_logger:yetanotherfunc ==> returning to <module>

This works because "all calls to [`logging.getLogger(name)`] with a given name
return the same logger instance", so that "logger instances never need to be
passed between different parts of an application",
as per the [Python documentation for `logging.getLogger`](https://docs.python.org/3/library/logging.html?highlight=logging.getlogger#logging.getLogger)

###[The *loglevel* parameter (default: *logging.DEBUG*)](id:loglevel-parameter)

`log_calls` also takes a `loglevel` keyword parameter, whose value must be
one of the `logging` module's constants - `logging.DEBUG`, `logging.INFO`, etc.
– or a custom logging level if you've added any. `log_calls` writes output messages
using `logger.log(loglevel, …)`. Thus, if the `logger`'s log level is higher than
`loglevel`, no output will appear:

    >>> logger.setLevel(logging.INFO)   # raise logger's level to INFO
    >>> @log_calls(logger='logger_=', loglevel=logging.DEBUG)
    ... def f(x, y, z, **kwargs):
    ...     return y + z
    >>> # No log_calls output from f
    >>> # because loglevel for f < level of logger
    >>> f(1,2,3, logger_=logger)       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    5

The use of loggers, and of these parameters, is explored further in the main documentation, which contains an example of [using a logger with multiple handlers that have different loglevels](http://www.pythonhosted.org/log_calls#logging-multiple-handlers).

##[Call chains](id:Call-chains)

`log_calls` does its best to chase back along the call chain to find
the first *enabled* `log_calls`-decorated function on the stack. 
If there's no such function, it just displays the immediate caller. 
If there is such a function, however, it displays the entire list of 
functions on the stack up to and including that function when reporting 
calls and returns. Without this, you'd have to guess at what was called 
in between calls to functions decorated by `log_calls`. If you specified 
a `prefix` or `name` for the decorated caller on the end of a call chain, `log_calls` will use the requested display name:

    >>> @log_calls()
    ... def g1():
    ...     pass
    >>> def g2():
    ...     g1()
    >>> @log_calls(prefix='mid.')
    ... def g3():
    ...     g2()
    >>> def g4():
    ...     g3()
    >>> @log_calls()
    ... def g5():
    ...     g4()
    >>> g5()
    g5 <== called by <module>
    mid.g3 <== called by g4 <== g5
    g1 <== called by g2 <== mid.g3
    g1 ==> returning to g2 ==> mid.g3
    mid.g3 ==> returning to g4 ==> g5
    g5 ==> returning to <module>

In the next example, `g` is `log_calls`-decorated but logging is disabled,
so the reported call chain for `f` stops at its immediate caller:

    >>> @log_calls()
    ... def f(): pass
    >>> def not_decorated(): f()
    >>> @log_calls(enabled=False, log_call_numbers=True)
    ... def g(): not_decorated()
    >>> g()
    f <== called by not_decorated
    f ==> returning to not_decorated

Elaborating on the previous example, here are longer call chains with an 
intermediate decorated function that has logging disabled. We've also enabled indentation:

    >>> @log_calls(indent=True)
    ... def e(): pass
    >>> def not_decorated_call_e(): e()
    >>> @log_calls(indent=True)
    ... def f(): not_decorated_call_e()
    >>> def not_decorated_call_f(): f()
    >>> @log_calls(enabled=False, log_call_numbers=True, indent=True)
    ... def g(): not_decorated_call_f()
    >>> @log_calls(indent=True)
    ... def h(): g()
    >>> h()
    h <== called by <module>
        f <== called by not_decorated_call_f <== g <== h
            e <== called by not_decorated_call_e <== f
            e ==> returning to not_decorated_call_e ==> f
        f ==> returning to not_decorated_call_f ==> g ==> h
    h ==> returning to <module>

`log_calls` chases back to the nearest *enabled* decorated function, so that there aren't gaps between call chains. 

###[Indentation and call numbers with recursion](id:recursion-example)
These features are especially useful in recursive and mutually recursive situations. We have to use `OrderedDict`s here because of doctest:

    >>> from collections import OrderedDict
    >>> @log_calls(log_call_numbers=True, log_retval=True, indent=True)
    ... def depth(d, key=None):
    ...     if not isinstance(d, dict):
    ...         return 0    # base case
    ...     elif not d:
    ...         return 1
    ...     else:
    ...         return max(map(depth, d.values(), d.keys())) + 1
    >>> depth(
    ...     OrderedDict(
    ...         (('a', 0),
    ...          ('b', OrderedDict( (('c1', 10), ('c2', 11)) )),
    ...          ('c', 'text'))
    ...     )
    ... )
    depth [1] <== called by <module>
        arguments: d=OrderedDict([('a', 0), ('b', OrderedDict([('c1', 10), ('c2', 11)])), ('c', 'text')])
        defaults:  key=None
        depth [2] <== called by depth [1]
            arguments: d=0, key='a'
            depth [2] return value: 0
        depth [2] ==> returning to depth [1]
        depth [3] <== called by depth [1]
            arguments: d=OrderedDict([('c1', 10), ('c2', 11)]), key='b'
            depth [4] <== called by depth [3]
                arguments: d=10, key='c1'
                depth [4] return value: 0
            depth [4] ==> returning to depth [3]
            depth [5] <== called by depth [3]
                arguments: d=11, key='c2'
                depth [5] return value: 0
            depth [5] ==> returning to depth [3]
            depth [3] return value: 1
        depth [3] ==> returning to depth [1]
        depth [6] <== called by depth [1]
            arguments: d='text', key='c'
            depth [6] return value: 0
        depth [6] ==> returning to depth [1]
        depth [1] return value: 2
    depth [1] ==> returning to <module>
    2

**NOTE**: *The optional* `key` *parameter is for instructional purposes, so you can see the key that's paired with the value of* `d` *in the caller's dictionary. Typically the signature of this function would be just* `def depth(d)`, *and the recursive case would return* `max(map(depth, d.values())) + 1`.

## [The indent-aware writing method *log_message()*](id:log_message)
#### <p style="background-color: yellow"> TODO TODO TODO TODO TODO</p>
`log_calls` exposes the method it uses to write its messages, `log_message`,
whose full signature is:

    `log_message(msg, *msgs, sep=' ', 
                 extra_indent_level=1, prefix_with_name=False)`

This method takes one or more "messages" (anything you want to see as a string),
and writes one final output message formed by joining those messages separated by `sep`.

`extra_indent_level` is a number of 4-column-wide *indent levels* specifying
where to begin writing that message. This value x 4 is an offset in columns
from the left margin of the visual frame established by log_calls – that is,
an offset from the column in which the function entry/exit messages begin. The default
of 1 aligns the message with the "arguments: " line of `log_calls`'s output.

`prefix_with_name` is a `bool`. If true, the final message is prefaced with the
 possibly prefixed name of the function (using the `prefix` setting), 
 plus possibly its call number in  square brackets (if the `log_call_numbers` setting
 is true).
 
If a decorated function or method writes debugging messages, even multiline
messages, it can use this method to write them so that they sit nicely within
the `log_calls` visual frame.

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

The debugging messages written by `f` literally "stick out", and it becomes difficult,
especially in more complex situations with multiple functions and methods,
to figure out who actually wrote which message; hence the "(n=%d)" tag. If instead
`f` uses `log_message`, all of its messages from each invocation align neatly
within the `log_calls` visual frame. We take this opportunity to also
illustrate the keyword parameters of `log_message`:

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

The `log_message()` method works whether the output destination is `stdout`,
another stream, a file, or a logger. The test file `test_log_calls_more.py`
contains an example `main__log_message__all_possible_output_destinations()`
which illustrates that.

See the full documentation for [the `log_message` method](http://www.pythonhosted.org/log_calls#log_message) for notes 
and internal links to further examples. 

## [The indent-aware expression-evaluating method *log_exprs()*](id:log_exprs)
#### <p style="background-color: yellow"> TODO TODO TODO TODO TODO (*section heading is bad, too*)</p>

## [Advanced Features](id:Advanced-features)
`log_calls` provides a number of features beyond those already described. We'll only give an overview of them here. For a full account, see [the complete documentation](http://www.pythonhosted.org/log_calls).

### [Dynamic control of settings](id:dynamic-control-of-settings)
Sometimes, you'll need or want to change a `log_calls` setting for a decorated function on the fly. The major impediment to doing so is that the values  of the `log_calls` parameters are set once the decorated function is interpreted. 
Those values are established once and for all when the Python interpreter 
parses the definition of a decorated function and creates a function object.

#### [The problem, and two *log_calls* solutions](id:log_call_settings)
Even if a variable is used as a parameter value, its value at the time
Python processes the definition is "frozen" for the created function object.
Subsequently changing the value of the variable will *not* affect the behavior
of the decorator.

For example, suppose `DEBUG` is a module-level variable initialized to `False`:

    >>> DEBUG = False

and you use this code:

    >>> @log_calls(enabled=DEBUG)
    ... def foo(**kwargs):
    ...     pass
    >>> foo()       # No log_calls output: DEBUG is False

If later you set `Debug = True` and call `foo`, that call won't be logged,
because the decorated `foo`'s *enabled* setting is bound to the original value
of `DEBUG`, established when the definition was processed:

    >>> DEBUG = True
    >>> foo()       # Still no log_calls output

`log_calls` provides *two* ways to overcome this limitation and dynamically control the settings of a decorated function:

* [the `log_calls_settings` attribute](#log_call_settings), which provides a mapping interface and an attribute-based interface to settings, and 
* [indirect values](#Indirect-values). 

The following two subsections give a brief introduction to these features, which [the main documentation]((http://www.pythonhosted.org/log_calls) presents in depth.

#### [The *log_calls_settings* attribute](id:log_call_settings)
`log_calls` adds an attribute `log_calls_settings`
to a decorated function, through which you can access the decorator settings for that function. This attribute is an object which lets you control the settings for a decorated function via a mapping (`dict`-like) interface, and equivalently, via attributes of the object. The mapping keys and the attribute names are simply the `log_calls` keywords. `log_calls_settings` also implements many of the standard `dict` methods for interacting with the settings in familiar ways.

#####[The mapping interface and the attribute interface to settings](id:mapping-interface)

Once you've decorated a function with `log_calls`,

    >>> @log_calls()
    ... def f(*args, **kwargs):
    ...     return 91

you can access and change its settings via the `log_calls_settings` attribute
of the decorated function, which behaves like a dictionary. You can read and
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

You can also use the same keywords as attributes of `log_calls_settings`
instead of as keywords to the mapping interface; they're completely
equivalent:

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
        elapsed time: ... [secs], CPU time: ... [secs]
    f [1] ==> returning to <module>

    >>> f.log_calls_settings.log_args = False
    >>> f.log_calls_settings.log_elapsed = False
    >>> f.log_calls_settings.log_retval = False
    >>> _ = f()                                 # doctest: +ELLIPSIS
    f [2] <== called by <module>
    f [2] ==> returning to <module>

The `log_calls_settings` attribute has a length (14), its keys and `items()` can be iterated through, you can use `in` to test for key membership, and it has an `update()` method. As with an ordinary dictionary, attempting to access a nonexistent setting 
raises `KeyError`. Unlike an ordinary dictionary, you can't add new keys – the `log_calls_settings` dictionary is closed to new members, and attempts to add one will also raise `KeyError`.

###### [The *update()*, *as_OrderedDict()* and *as_dict()* methods – and a typical use-case](id:update-as_etc)
The `update()` method of the `log_calls_settings` object lets you update several settings at once:

    >>> f.log_calls_settings.update(
    ...     log_args=True, log_elapsed=False, log_call_numbers=False,
    ...     log_retval=False)
    >>> _ = f()
    f <== called by <module>
        arguments: <none>
    f ==> returning to <module>

You can retrieve the entire collection of settings as either an `OrderedDict` using the `as_OrderedDict()` method, or as a `dict` using `as_dict()`.
Either can serve as a snapshot of the settings, so that you can change settings temporarily, use the new settings, and then use `update()` to restore settings from the snapshot.
in addition to taking keyword arguments, as shown above, `update()` can take one or more dicts – in particular, a dictionary retrieved from one of the `as_*` methods. For example:

Retrieve settings (here, as an `OrderedDict` because those are more doctest-friendly, but using `as_dict()` suffices):

    >>> od = f.log_calls_settings.as_OrderedDict()
    >>> od                      # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True),           ('args_sep', ', '),
                 ('log_args', True),          ('log_retval', False),
                 ('log_elapsed', False),      ('log_exit', True),
                 ('indent', False),           ('log_call_numbers', False),
                 ('prefix', ''),              ('file', None),
                 ('logger', None),            ('loglevel', 10),
                 ('record_history', False),   ('max_history', 0)])

change settings temporarily:

    >>> f.log_calls_settings.update(
    ...     log_args=False, log_elapsed=True, log_call_numbers=True,
    ...     log_retval=True)

use the new settings for `f`:

    >>> _ = f()                     # doctest: +ELLIPSIS
    f [4] <== called by <module>
        f [4] return value: 91
        elapsed time: ... [secs], CPU time: ... [secs]
    f [4] ==> returning to <module>

and restore original settings, this time passing the retrieved settings
dictionary rather than keywords (we *could* pass `**od`, but that's unnecessary and a pointless expense):

    >>> f.log_calls_settings.update(od)
    >>> od == f.log_calls_settings.as_OrderedDict()
    True

**NOTE**: *The [`prefix`](#prefix-parameter) and [`max_history`](#max_history-parameter)
settings are "immutable" (no other settings are), and attempts to change them
directly (e.g.* `f.log_calls_settings.max_history = anything`) *raise* `ValueError`.
*Nevertheless, they* are *items in the retrieved settings dictionaries. To allow for
the use-case just illustrated, `update()` is considerate enough to skip over
immutable settings.*

#### [Indirect values](id:Indirect-values)
`log_calls` provides a second way to access and change settings on the fly. The decorator lets you specify any parameter 
except `prefix` or `max_history` with one level of indirection, by using 
*indirect values*: an indirect value is a string that names a keyword argument 
*of the decorated function*. It can be an explicit keyword argument present 
in the signature of the function, or an implicit keyword argument that ends up 
in `**kwargs` (if that's present in the function's signature). When the decorated 
function is called, the arguments passed by keyword, and the decorated function's 
explicit keyword parameters with default values, are both searched for the named 
parameter; if it is found and of the correct type, *its* value is used; otherwise 
the default value for the `log_calls` parameter is used.

To specify an indirect value for a parameter whose normal values are or can be `str`s (only `args_sep` and `logger`, at present), append an `'='` to the value.  For consistency, 
any indirect value can end in a trailing `'='`, which is stripped. Thus, 
`enabled='enable_='` indicates an indirect value *to be supplied* by the keyword (argument or parameter) `enable_` of the decorated function.

For example, in:

    >>> @log_calls(args_sep='sep=', prefix="*** ")
    ... def f(a, b, c, sep='|'): pass

`args_sep` has an indirect value which names `f`'s explicit keyword parameter `sep`,
and `prefix` has a direct value as it always does. A call can dynamically override the default
value '|' in the signature of `f` by supplying a value:

    >>> f(1, 2, 3, sep=' / ')
    *** f <== called by <module>
        arguments: a=1 / b=2 / c=3 / sep=' / '
    *** f ==> returning to <module>

or it can use `f`'s default value by not supplying a `sep` argument:

    >>> f(1, 2, 3)
    *** f <== called by <module>
        arguments: a=1|b=2|c=3
        defaults:  sep='|'
    *** f ==> returning to <module>

*A decorated function doesn't have to explicitly declare the parameter 
named as an indirect value*, if its signature includes `**kwargs`: 
the intermediate parameter can be an implicit keyword parameter, 
passed by a caller but not present in the function's signature.
Consider:

    >>> @log_calls(enabled='enable')
    ... def func1(a, b, c, **kwargs): pass
    >>> @log_calls(enabled='enable')
    ... def func2(z, **kwargs): func1(z, z+1, z+2, **kwargs)

When the following statement is executed, the calls to both `func1` and `func2` will be logged:

    >>> func2(17, enable=True)
    func2 <== called by <module>
        arguments: z=17, [**]kwargs={'enable': True}
    func1 <== called by func2
        arguments: a=17, b=18, c=19, [**]kwargs={'enable': True}
    func1 ==> returning to func2
    func2 ==> returning to <module>

whereas neither of the following two statements will trigger logging:

    >>> func2(42, enable=False)     # no log_calls output
    >>> func2(99)                   # no log_calls output

See the section in the full documentation on [indirect values](http://www.pythonhosted.org/log_calls#Indirect-values) for several more examples and useful techniques involving indirect values. The test suite `log_calls/tests/test_log_calls_more.py` also contains further doctests/examples. 

### [Call history and statistics](id:call-history-and-statistics)
Unless it's [bypassed](#bypass),`log_calls` always collects at least
a few basic statistics about calls to a decorated function.
It can collect the entire history of calls to a function if asked
to (using the [`record_history` parameter](#record_history-parameter)).
The statistics and history are accessible via the `stats` attribute
which `log_calls` adds to a decorated function.

#### [The *record_history* and *max_history* parameters](id:_history-parameters)
The two settings parameters we haven't yet discussed govern the recording of a decorated function's call history.

#####[The *record_history* parameter (default: *False*)](id:record_history-parameter)
When the `record_history` setting is true for a decorated function `f`, `log_calls` will retain a sequence of records holding the details of each logged call to that function. That history is accessible via attributes of the `stats` object. 

Let's define a function `f` with `record_history` set to true:

    >>> @log_calls(record_history=True, log_call_numbers=True, log_exit=False)
    ... def f(a, *args, x=1, **kwargs): pass

In the following subsections, we'll call this function, manipulate its settings, and examine its statistics.

#####[The *max_history* parameter (default: 0)](id:max_history-parameter)
The `max_history` parameter determines how many call history records are retained for a decorated function whose call history is recorded. If this value is 0 or negative, unboundedly many records are retained (unless or until
you set the `record_history` setting to false, or call the
[`stats.clear_history()`](#stats.clear_history) method). If the value of `max_history` is > 0, `log_calls` will retain at most that many records, discarding the oldest records to make room for newer ones if the history reaches capacity.

You cannot change `max_history` using the mapping interface or the attribute
of the same name; attempts to do so raise `ValueError`. The only way to change its value is with the [`stats.clear_history()`](#stats.clear_history) method, discussed below.

####[The *stats* attribute and *its* attributes](id:stats-attribute)
The `stats` attribute of a decorated function is an object that provides read-only statistics and data about calls to a decorated function:

* [`stats.num_calls_logged`](#stats.num_calls_logged)
* [`stats.num_calls_total`](#stats.num_calls_total)
* [`stats.elapsed_secs_logged`](#elapsed_secs_logged)
* [`stats.CPU_secs_logged`](#CPU_secs_logged)
* [`stats.history`](#stats.history)
* [`stats.history_as_csv`](#stats.history_as_csv)
* [`stats.history_as_DataFrame`](#stats.history_as_DataFrame)

The first three don't depend on the `record_history` setting at all.The last three yield empty results unless `record_history` is true. 

The `stats` attribute also provides one method, [`stats.clear_history()`](#stats.clear_history).

Let's call the function `f` twice:

    >>> f(0)
    f [1] <== called by <module>
        arguments: a=0
        defaults:  x=1
    >>> f(1, 100, 101, x=1000, y=1001)
    f [2] <== called by <module>
        arguments: a=1, [*]args=(100, 101), x=1000, [**]kwargs={'y': 1001}

and explore its `stats`.

#####[The *num_calls_logged* attribute](id:stats.num_calls_logged)
The `stats.num_calls_logged` attribute contains the number of the most
recent logged call to a decorated function. Thus, `f.stats.num_calls_logged`
will equal 2:

    >>> f.stats.num_calls_logged
    2

This counter gets incremented when a decorated function is called that has logging enabled, even if its `log_call_numbers` setting is false.

#####[The *num_calls_total* attribute](id:stats.num_calls_total)
The `stats.num_calls_total` attribute holds the *total* number of calls
to a decorated function. This counter gets incremented even when logging
is disabled for a function.

For example, let's now *disable* logging for `f` and call it 3 more times:

    >>> f.log_calls_settings.enabled = False
    >>> for i in range(3): f(i)

Now `stats.num_calls_total` will equal 5, but `f.stats.num_calls_logged`
will still equal 2:

    >>> f.stats.num_calls_total
    5
    >>> f.stats.num_calls_logged
    2

Finally, let's re-enable logging for `f` and call it again.
The displayed call number will be the number of the *logged* call, 3, the same
value as `f.stats.num_calls_logged` after the call:

    >>> f.log_calls_settings.enabled = True
    >>> f(10, 20, z=5000)
    f [3] <== called by <module>
        arguments: a=10, [*]args=(20,), [**]kwargs={'z': 5000}
        defaults:  x=1

    >>> f.stats.num_calls_total
    6
    >>> f.stats.num_calls_logged
    3

**ATTENTION**: *Thus,* `log_calls` *has some overhead even when it's disabled, and somewhat more when it's enabled. So,* **comment it out in production code!** 

#####[The *elapsed_secs_logged* attribute](id:elapsed_secs_logged)
The `stats.elapsed_secs_logged` attribute holds the sum of the elapsed times ("wall time") of
all logged calls to a decorated function, in seconds. Here's its value for the 3 logged calls to `f` above:

    >>> f.stats.elapsed_secs_logged   # doctest: +SKIP
    6.67572021484375e-06

#####[The *stats.CPU_secs_logged* attribute](id:CPU_secs_logged)
The `stats.CPU_secs_logged` attribute holds the sum of the CPU times
("process time") of all logged calls to a decorated function, in seconds.
Similarly, we'll just exhibit its value for the 3 logged calls to `f` above:

    >>> f.stats.CPU_secs_logged   # doctest: +SKIP
    1.1000000000038757e-05

**NOTE**: *Under Python < 3.3, `stats.elapsed_secs_logged` and `stats.CPU_secs_logged` 
will be the same number.*

#####[The *history* attribute](id:stats.history)
The `stats.history` attribute of a decorated function provides the call history
of logged calls to the function as a tuple of records. Each record is a `namedtuple`of type `CallRecord`. Here's `f`'s call history,
in (almost) human-readable form:

    >>> print('\\n'.join(map(str, f.stats.history)))   # doctest: +SKIP
    CallRecord(call_num=1, argnames=['a'], argvals=(0,), varargs=(),
                           explicit_kwargs=OrderedDict(),
                           defaulted_kwargs=OrderedDict([('x', 1)]), implicit_kwargs={},
                           retval=None, 
                           elapsed_secs=3.0049995984882116e-06, 
                           CPU_secs=2.9999999999752447e-06,
                           timestamp='10/28/14 15:56:13.733763',
                           prefixed_func_name='f', caller_chain=['<module>'])
    CallRecord(call_num=2, argnames=['a'], argvals=(1,), varargs=(100, 101),
                           explicit_kwargs=OrderedDict([('x', 1000)]),
                           defaulted_kwargs=OrderedDict(), implicit_kwargs={'y': 1001},
                           retval=None, 
                           elapsed_secs=3.274002665420994e-06, 
                           CPU_secs=3.0000000000030003e-06,
                           timestamp='10/28/14 15:56:13.734102',
                           prefixed_func_name='f', caller_chain=['<module>'])
    CallRecord(call_num=3, argnames=['a'], argvals=(10,), varargs=(20,),
                           explicit_kwargs=OrderedDict(),
                           defaulted_kwargs=OrderedDict([('x', 1)]), implicit_kwargs={'z': 5000},
                           retval=None, 
                           elapsed_secs=2.8769973141606897e-06, 
                           CPU_secs=2.9999999999752447e-06,
                           timestamp='10/28/14 15:56:13.734412',
                           prefixed_func_name='f', caller_chain=['<module>'])

The CSV representation pairs
the `argnames` with their values in `argvals` (the `argnames` become column headings), 
making it even more human-readable, especially when viewed in a program that 
presents CSVs nicely.

#####[The *history_as_csv* attribute](id:stats.history_as_csv)
The value `stats.history_as_csv` attribute is a text representation in CSV format
of a decorated function's call history. You can save this string
and import it into the program or tool of your choice for further analysis.
(*Note: if your tool of choice is [Pandas](http://pandas.pydata.org), you can use 
the `stats` attribute [`stats.history_as_DataFrame`](#stats.history_as_DataFrame) to obtain history 
directly in the representation you really want.*)
The CSV representation
breaks out each argument into its own column, throwing away 
information about whether an argument's value was passed or is a default.

The CSV separator is '|' rather than ',' because some of the fields – `args`,  `kwargs`
and `caller_chain` – use commas intrinsically. Let's examine one more 
`history_as_csv` for a function that has all of those fields:

    >>> @log_calls(record_history=True, log_call_numbers=True,
    ...            log_exit=False, log_args=False)
    ... def f(a, *extra_args, x=1, **kw_args): pass
    >>> def g(a, *args, **kwargs): f(a, *args, **kwargs)
    >>> @log_calls(log_exit=False, log_args=False)
    ... def h(a, *args, **kwargs): g(a, *args, **kwargs)
    >>> h(0)
    h <== called by <module>
    f [1] <== called by g <== h
    >>> h(10, 17, 19, z=100)
    h <== called by <module>
    f [2] <== called by g <== h
    >>> h(20, 3, 4, 6, x=5, y='Yarborough', z=100)
    h <== called by <module>
    f [3] <== called by g <== h
    
Here's the call history in CSV format:

    >>> print(f.stats.history_as_csv)        # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    call_num|a|extra_args|x|kw_args|retval|elapsed_secs|CPU_secs|timestamp|prefixed_fname|caller_chain
    1|0|()|1|{}|None|...|...|...|'f'|['g', 'h']
    2|10|(17, 19)|1|{'z': 100}|None|...|...|...|'f'|['g', 'h']
    3|20|(3, 4, 6)|5|{'y': 'Yarborough', 'z': 100}|None|...|...|...|'f'|['g', 'h']
    <BLANKLINE>

Ellipses are for the `elapsed_secs`, `CPU_secs` and `timestamp` fields. As usual, `log_calls` will use whatever names you use for *varargs* parameters
(here, `extra_args` and `kw_args`). Whatever the name of the `kwargs` parameter,
items within that field are guaranteed to be in sorted order.

#####[The *history_as_DataFrame* attribute](id:stats.history_as_DataFrame)
The `stats.history_as_DataFrame` attribute returns the history of a decorated
function as a [Pandas](http://pandas.pydata.org) [DataFrame](http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe), 
if the Pandas library is installed. This saves you the intermediate step of 
calling `DataFrame.from_csv` with the proper arguments (and also saves you from 
having to know or care what those are).

If Pandas is not installed, the value of this attribute is `None`.

The documentation for the `record_history` decorator contains an [example of the `history_as_DataFrame` attribute](http://www.pythonhosted.org/log_calls/record_history.html#stats.history_as_DataFrame) 
which also illustrates its use in an IPython notebook.

#####[The *clear_history(max_history=0)* method](id:stats.clear_history)
As you might expect, the `stats.clear_history(max_history=0)` method clears 
the call history of a decorated function. In addition, it resets all running sums:
`num_calls_total` and `num_calls_logged` are reset to 0, and 
`elapsed_secs_logged` is reset to 0.0.

**It is the only way to change the value of the `max_history` setting**, via
the optional keyword parameter for which you can supply any (integer) value,
by default 0.

The function `f` has a nonempty history, as we just saw. Let's clear `f`'s history, setting `max_history` to 33, and check that settings
and `stats` tallies are reset:

    >>> f.stats.clear_history(max_history=33)
    >>> f.log_calls_settings.max_history
    33
    >>> f.stats.num_calls_logged
    0
    >>> f.stats.num_calls_total
    0
    >>> f.stats.elapsed_secs_logged
    0.0
    >>> f.stats.CPU_secs_logged
    0.0

##[The *record_history* decorator](id:record_history-decorator)
The `record_history` decorator is a stripped-down version of `log_calls` which
records calls to a decorated function but writes no messages. You can think
of it as `log_calls` with the `record_history` and `log_call_numbers` settings
always true, and without any of the message-logging apparatus.

`record_history` has only three keyword parameters:

* `enabled`
* `prefix`
* `max_history`

Just as the settings of `log_calls` for a decorated function are accessible
dynamically through the `log_calls_settings` attribute, these settings of
`record_history` are exposed via a `record_history_settings` attribute.
`record_history_settings` is an object of the same type as `log_calls_settings`,
so it has the same methods and behaviors described in the [`log_calls_settings`](#log_call_settings) section.

Functions decorated by `record_history` have a full-featured `stats` attribute,
as described in the [Call history and statistics](#call-history-and-statistics) section above.

See the documentation for [`record_history`](http://www.pythonhosted.org/log_calls/record_history.html) for examples and tests.

**ATTENTION**: *Like* `log_calls`, `record_history` *has some overhead. So,* **comment it out in production code!** 

##[Appendix – Keyword Parameters Reference](id:KeywordParametersReference)

The `log_calls` decorator takes various keyword arguments, all with hopefully sensible defaults:

Keyword parameter | Default value | Description
----------------: | :------------ | :------------------
       `enabled`    | `True`          | An `int`. If positive (or `True`), then `log_calls` will output (or "log") messages. If false ("disabled" – `0` or `False`), `log_calls` won't output messages or record history but will continue to increment the `stats.num_calls_total` call counter. If negative ("bypassed"), `log_calls` won't do anything.
       `args_sep`   | `', '`          | `str` used to separate arguments. The default is  `', '`, which lists all args on the same line. If `args_sep='\n'` is used, or more generally if the `args_sep` string ends in `\n`, then additional spaces are appended to the separator for a neater display. Other separators in which `'\n'` occurs are left unchanged, and are untested – experiment/use at your own risk.
       `log_args`   | `True`          | If true, arguments passed to the decorated function, and default values used by the function, will be logged.
       `log_retval` | `False`         | If true, log what the decorated function returns. At most 77 chars are printed, with a trailing ellipsis if the value is truncated.
       `log_exit`   | `True`          | If true, the decorator will log an exiting message after calling the function of the form `f returning to ==> caller`, and before returning what the function returned.
       `log_call_number` | `False`    | If true, display the (1-based) number of the function call, e.g. `f [3] called by <== <module>` and `f [3] returning to ==> <module>` for the 3rd logged call. This would correspond to the 3rd record in the function's call history, if `record_history` is true.
       `log_elapsed` | `False`        | If true, display how long it took the function to execute, in seconds. Both wall time ("elapsed") and process time ("CPU") are reported (but under Python < 3.3, they're the same number: wall time).
       `indent`     | `False`         | The `indent` parameter indents each new level  of logged messages by 4 spaces, giving a visualization of the call hierarchy.
       `prefix`     | `''`            | A `str` to prefix the function name with in logged messages: on entry, in reporting return value (if `log_retval` is true) and on exit (if `log_exit` is true).
       `file`     | `sys.stdout`      | If `logger` is `None`, a stream (an instance of type `io.TextIOBase`) to which `log_calls` will print its messages. This value is supplied to the `file` keyword parameter of the `print` function.
       `logger`     | `None`          | If not `None`, either a logger (a `logging.Logger` instance), or the name of a logger (a `str` that will be passed to `logging.getLogger()`); that logger will be used to write messages, provided it exists/has handlers. Otherwise, `print` is used.
       `loglevel`   | `logging.DEBUG` | Logging level, ignored unless a logger is specified. This should be one of the logging levels recognized by the `logging` module – one of the constants defined by that module, or a custom level you've added.
       `record_history` | `False`     | If true, a list of records will be kept, one for each logged call to the function. Each record holds: call number (1-based), arguments and defaulted keyword arguments, return value, time elapsed, time of call, prefixed function name, caller (call chain). The value of this attribute is a `tuple`.
       `max_history` | `0`            | An `int`. *value* > 0 --> store at most *value*-many records, oldest records overwritten; *value* ≤ 0 --> store unboundedly many records. Ignored unless `record_history` is true.
       `settings` | `None`            | A dictionary containing settings and values, or a string giving the pathname to a *settings file* containing settings and values. If the pathname is a directory and not a file, `log_calls` looks for a file `.log_calls` in that directory; otherwise, it looks for the named file. The format of a settings file is: zero or more lines of the form *setting* = *value*; lines whose first non-whitespace character is '#' are comments. These settings are defaults: other settings passed to `log_calls` override their values.


####— Brian O'Neill, 2014-2015, NYC
