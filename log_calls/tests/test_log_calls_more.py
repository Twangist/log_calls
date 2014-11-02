__author__ = "Brian O'Neill"
__version__ = '0.1.13'

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
        arguments:
            x=1
            y=2
            z=3
            [**]kwargs={...}
    DEBUG:mylogger:r <== called by s <== t
        arguments:
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
        arguments: a=5, x=3, y=3, [**]kwargs={...}
    135
    INFO:mylogger:indirect_loglevel ==> returning to <module>
    """
    pass


# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":
    # # Try it with an inner function
    # @log_calls()
    # def f(): pass
    #
    # def g(): f()
    #
    # def outer():
    #     @log_calls(enabled='doit=', args_sep='sepr8r_=', logger='lgr_=')
    #     def inner():
    #         g()
    #     return inner
    #
    # inn = outer()
    # print("inner function's log_calls_settings: \n%s"
    #       % inn.log_calls_settings)
    #
    # inn()

    # print("==================================")
    #
    # # instance methods, classmethods, staticmethods
    # class Klass():
    #     def __init__(self):
    #         pass
    #     @log_calls(enabled=False, args_sep=' + ', logger='lager=', prefix='Klass.instance.')
    #     def instance_method(self, **kwargs):
    #         pass
    #
    #     @classmethod
    #     @log_calls(enabled=True, log_retval=True, log_args=False, prefix='Klass.klass.')
    #     def klassmethod(cls, **kwargs):
    #         return 78
    #
    #     @staticmethod
    #     @log_calls(enabled=True, prefix='Klass.statik.')
    #     def statikmethod(x, y, **kwargs):
    #         return -1
    #
    # obj = Klass()
    # print("via instance of Klass:")
    # print("instance method log_calls_settings:", obj.instance_method.log_calls_settings)
    # print("classmethod log_calls_settings:", obj.klassmethod.log_calls_settings)
    # print("staticmethod log_calls_settings:", obj.statikmethod.log_calls_settings)
    # print("via Klass:")
    # print("classmethod log_calls_settings:", Klass.klassmethod.log_calls_settings)
    # print("staticmethod log_calls_settings:", Klass.statikmethod.log_calls_settings)
    #
    # print("\nRunning doctest...")

    doctest.testmod()   # (verbose=True)

    # unittest.main()

