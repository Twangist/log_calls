__author__ = 'brianoneill'

import inspect

###############################################################

from log_calls import log_calls

def func(x):
    return x

log_calls.decorate_module_function(func,
                                   log_exit=True)
print(func(3))

from log_calls.tests import some_other_module

log_calls.decorate_module_function(some_other_module.make_id,
                                   args_sep=' | ')

print(some_other_module.make_id(15, 632))
