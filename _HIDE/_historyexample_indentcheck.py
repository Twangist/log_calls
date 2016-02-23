__author__ = 'brianoneill'

from log_calls import log_calls

@log_calls(record_history=True, log_call_numbers=True,
           log_exit=False, log_args=False)
def f(a, *extra_args, x=1, **kw_args): pass

def g(a, *args, **kwargs): f(a, *args, **kwargs)

@log_calls(log_exit=False, log_args=False)
def h(a, *args, **kwargs): g(a, *args, **kwargs)

h(0)
'''
h <== called by <module>
    f [1] <== called by g <== h
'''
h(10, 17, 19, z=100)
'''
h <== called by <module>
    f [2] <== called by g <== h
'''
h(20, 3, 4, 6, x=5, y='Yarborough', z=100)
'''
h <== called by <module>
    f [3] <== called by g <== h
'''
