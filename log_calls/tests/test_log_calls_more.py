__author__ = "Brian O'Neill"
__version__ = '0.1.14'

from log_calls import log_calls

import doctest
import unittest


#############################################################################
# doctests
#############################################################################

def main__static_dynamic_parameter_values__dynamic_control__more():
    """
###Additional tests and examples
####*log_args*, *log_retval*, *log_exit* with indirect values

    >>> @log_calls(log_args='logargs=', log_retval='logretval=', log_exit='logexit=')
    ... def f(x, **kwargs):
    ...     return x**2
    >>> _ = f(2, logexit=False)   # logargs=True, log_retval=False: defaults
    f <== called by <module>
        arguments: x=2, [**]kwargs={'logexit': False}

    >>> _ = f(5, logargs=False, logretval=True) # log_exit=True, default
    f <== called by <module>
        f return value: 25
    f ==> returning to <module>

###More on dynamically enabling/disabling *log_calls* output

Suppose you use `enabled='debug'` to decorate a function `f`. Then a call to `f`
will be logged if one of the following conditions holds:

1. the keyword is *not* passed, but the function `f` explicitly declares
   the keyword parameter (`debug`) and assigns it a 'truthy' default value
   (e.g. `def f(x, debug=True)`), or
2. the call passes the keyword mentioned with a 'truthy' value,
   e.g.`debug=17`.

**NOTE**: *When referring to values, I'll use* true *with lowercase* t *to mean
"truthy", and* false *with lowercase* f *to mean "falsy" .*

####Examples of condition 1. (explicit parameter)

It's instructive to consider examples where the wrapped function explicitly
provides the keyword named by the `enabled` parameter.

Let the wrapped function provide a default value of `True` for the parameter
named by the `enabled` parameter:

    >>> @log_calls(enabled='debug=')
    ... def do_more_stuff_t(a, debug=True, **kwargs):
    ...     pass

Here we get output by default, without having to pass `debug=True`:

    >>> do_more_stuff_t(9)
    do_more_stuff_t <== called by <module>
        arguments: a=9
        defaults:  debug=True
    do_more_stuff_t ==> returning to <module>

and here we get none:

    >>> do_more_stuff_t(4, debug=False)

Now let the explicit indirect parameter have a 'falsy' value:
    >>> @log_calls(enabled='debug=')
    ... def do_more_stuff_f(a, debug=False, **kwargs):
    ...     pass

Here we get no output, as `debug=False` (wrapped function's default value):

    >>> do_more_stuff_f(3)

but here we do get output:

    >>> do_more_stuff_f(4, debug=True)
    do_more_stuff_f <== called by <module>
        arguments: a=4, debug=True
    do_more_stuff_f ==> returning to <module>

####Examples of condition 2. (implicit parameter)

    >>> @log_calls(enabled='debug=')
    ... def bar(**kwargs):
    ...     pass
    >>> bar(debug=False)  # no output
    >>> bar(debug=True)   # output
    bar <== called by <module>
        arguments: [**]kwargs={'debug': True}
    bar ==> returning to <module>

    >>> bar()         # no output: enabled=<keyword> overrides enabled=True

    """
    pass


def main__more_on_logging__more():
    """
##[More on using loggers](id:More-on-using-loggers)

The basic setup:

    # Doesn't work on 3.4.0 on Linux (Ubuntu 12.04):

    # >>> import logging
    # >>> import sys
    # >>> ch = logging.StreamHandler(stream=sys.stdout)
    # >>> logging.basicConfig(handlers=[ch])
    # >>> logger = logging.getLogger('mylogger')
    # >>> logger.setLevel(logging.DEBUG)

    >>> import logging
    >>> import sys
    >>> ch = logging.StreamHandler(stream=sys.stdout)
    >>> c_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    >>> ch.setFormatter(c_formatter)
    >>> logger = logging.getLogger('mylogger')
    >>> logger.addHandler(ch)
    >>> logger.setLevel(logging.DEBUG)

####Indirect values for the *logger* parameter

You can use an indirect value for the `logger` parameter to make the logging
destination late-bound.

In the following example, although logger='logger_' is supplied to `log_calls`,
no `logger_=foo` is passed to the wrapped function `r` in the actual call, and no
`logger=bar` is supplied, so `log_calls` uses the default writing function, `print`.
(Furthermore, no args separator is passed with the `sep_` keyword, so `log_calls`
uses the default separator ', '.)

    >>> @log_calls(enabled='enable=', args_sep='sep_=', logger='logger_=')
    ... def r(x, y, z, **kwargs):
    ...     print(x * y + z)
    >>> r(1, 2, 3, enable=True)
    r <== called by <module>
        arguments: x=1, y=2, z=3, [**]kwargs={'enable': True}
    5
    r ==> returning to <module>

Define two more functions, with the outermost function `t` also using
`logger ='logger_'`, and pass `logger_=logger` to `t` when calling it.
Now both `t` and `r` use `logger` for output (and both use the supplied
separator '\\n'):

    >>> def s(x, y, z, **kwargs):
    ...     r(x, y, z, **kwargs)
    >>> @log_calls(enabled='enable=', args_sep='sep_=', logger='logger_=')
    ... def t(x, y, z, **kwargs):
    ...     s(x, y, z, **kwargs)

    >>> # kwargs == {'logger_': <logging.Logger object at 0x...>,
    >>> #            'enable': True, 'sep_': '\\n'}
    >>> t(1,2,3, enable=True, sep_='\\n', logger_=logger)       # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    DEBUG:mylogger:t <== called by <module>
    DEBUG:mylogger:    arguments:
            x=1
            y=2
            z=3
            [**]kwargs={...}
    DEBUG:mylogger:r <== called by s <== t
    DEBUG:mylogger:    arguments:
            x=1
            y=2
            z=3
            [**]kwargs={...}
    5
    DEBUG:mylogger:r ==> returning to s ==> t
    DEBUG:mylogger:t ==> returning to <module>

####Test of indirect *loglevel*

    >>> logger.setLevel(logging.INFO)   # raise logger's level to INFO
    >>> @log_calls(logger='logger_=', loglevel='loglevel_')
    ... def indirect_loglevel(a, x, y, **kwargs):
    ...     print(a * x**y)

No log_calls output from indirect_loglevel:
    >>> indirect_loglevel(5, 3, 3,
    ...                   enable=True, sep_='\\n',
    ...                   logger_=logger,
    ...                   loglevel_=logging.DEBUG)   # no log_calls output
    135

but now we do get output:
    >>> indirect_loglevel(5, 3, 3,
    ...                   enable=True, sep_='\\n',
    ...                   logger_=logger,
    ...                   loglevel_=logging.INFO)    # doctest: +ELLIPSIS
    INFO:mylogger:indirect_loglevel <== called by <module>
    INFO:mylogger:    arguments: a=5, x=3, y=3, [**]kwargs={...}
    135
    INFO:mylogger:indirect_loglevel ==> returning to <module>
    """
    pass


def main__inner_functions__more():
    """
## log_calls_settings of an inner function

    >>> @log_calls()
    ... def f(): pass

    >>> def g(): f()

    >>> def outer():
    ...     @log_calls(args_sep='sepr8r_=', logger='lgr_=')
    ...     def inner():
    ...         g()
    ...     return inner

    >>> inn = outer()
    >>> inn.log_calls_settings.args_sep == 'sepr8r_='
    True

Call it:

    >>> inn()
    inner <== called by <module>
    f <== called by g <== inner
    f ==> returning to g ==> inner
    inner ==> returning to <module>

    """
    pass


def main__methods__more():
    """
## instance methods, classmethods, staticmethods

    >>> @log_calls(indent=True)
    ... def f(): pass

    >>> def g(): f()

    >>> class Klass():
    ...     def __init__(self):
    ...         pass
    ...
    ...     @log_calls(logger='lager=', prefix='Klass.', indent=True)
    ...     def instance_method(self, **kwargs):
    ...         g()
    ...
    ...     @classmethod
    ...     @log_calls(log_args=False, log_retval=True, prefix='Klass.', indent=True)
    ...     def klassmethod(cls, **kwargs):
    ...         g()
    ...
    ...     @staticmethod
    ...     @log_calls(args_sep=' + ', log_elapsed=True, prefix='Klass.', indent=True)
    ...     def statikmethod(x, y, **kwargs):
    ...         g()


`log_calls_settings` can be accessed via the class, for classmethods and staticmethods:

    >>> (Klass.klassmethod.log_calls_settings.log_args,
    ...  Klass.klassmethod.log_calls_settings.log_retval)
    (False, True)

    >>> Klass.statikmethod.log_calls_settings.args_sep
    ' + '


All methods can be accessed through an instance:
    >>> obj = Klass()
    >>> obj.instance_method.log_calls_settings.logger
    'lager='

    >>> (obj.klassmethod.log_calls_settings.log_args,
    ...  obj.klassmethod.log_calls_settings.log_retval)
    (False, True)

    >>> obj.statikmethod.log_calls_settings.args_sep
    ' + '

Call these methods:

    >>> obj.instance_method()       # doctest: +ELLIPSIS
    Klass.instance_method <== called by <module>
        arguments: self=<__main__.Klass object at ...>
        f <== called by g <== Klass.instance_method
        f ==> returning to g ==> Klass.instance_method
    Klass.instance_method ==> returning to <module>

    >>> obj.klassmethod()   # or Klass.klassmethod()
    Klass.klassmethod <== called by <module>
        f <== called by g <== Klass.klassmethod
        f ==> returning to g ==> Klass.klassmethod
        Klass.klassmethod return value: None
    Klass.klassmethod ==> returning to <module>

    >>> obj.statikmethod(1, 2)      # doctest: +ELLIPSIS
    Klass.statikmethod <== called by <module>
        arguments: x=1 + y=2
        f <== called by g <== Klass.statikmethod
        f ==> returning to g ==> Klass.statikmethod
        elapsed time: ... [secs]
    Klass.statikmethod ==> returning to <module>

Similarly, the stats attribute can be accessed via the class or an instance:
    >>> obj.instance_method.stats.num_calls_logged
    1
    >>> Klass.klassmethod.stats.num_calls_total
    1
    >>> elapsed = Klass.statikmethod.stats.elapsed_secs_logged    # doctest: +ELLIPSIS
    >>> # about 0.0001738
    >>> elapsed > 0.0
    True

    """
    pass


# SURGERY:
main__methods__more.__doc__ = \
    main__methods__more.__doc__.replace("__main__", __name__)


# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

    # unittest.main()

