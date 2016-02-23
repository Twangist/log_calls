__author__ = 'brianoneill'

from log_calls import log_calls

@log_calls(enabled='enable_')
def f(x, y, enable_=False): pass

f(1, 2)                  # no output: enabled setting = default value of enable_

f(3, 4, enable_=True)    # output:

@log_calls(args_sep='args_sep_=')
def g(x, y, **kwargs): pass

g(1, 2)                   # output: args_sep setting = default value of args_sep setting

g(3, 4, args_sep_=' $ ')    # args_sep uses indirect value

@log_calls(enabled='enable_')
def h(**kwargs): pass

h()
h(enable_=True)
