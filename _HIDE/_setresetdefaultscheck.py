__author__ = 'brianoneill'

from log_calls import log_calls

global_settings = dict(
    log_call_numbers=True,
    log_exit=False,
    log_retval=True,
)

@log_calls()
def f(x, y): return x

log_calls.set_defaults(global_settings, args_sep=' $ ')

@log_calls()
def g(x,y): return y

log_calls.reset_defaults()

@log_calls()
def h(u, v): return v

_ = f(0, 1); _ = g(2, 3); _ = h(4, 5)
'''
f <== called by <module>
    arguments: x=0, y=1
f ==> returning to <module>
g [1] <== called by <module>
    arguments: x=2 $ y=3
    g [1] return value: 3
h <== called by <module>
    arguments: u=4, v=5
h ==> returning to <module>
'''
