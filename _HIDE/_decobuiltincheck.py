__author__ = 'brianoneill'

from log_calls import log_calls


# This works (does nothing)
lc_len = log_calls()(len)
print('len is lc_len:', len is lc_len)

# This works (does nothing)
lc_update = log_calls()(dict.update)
print('dict.update is lc_update:', dict.update is lc_update)

# Does nothing but (0.3.0b19) fails on call to _add_class_attrs
log_calls(only='update')(dict)

log_calls()(dict)

# Does nothing but (0.3.0b19) fails on call to _add_class_attrs
log_calls.decorate_class(dict, only='update')

d = dict(x=1, y=2)
d.update(x=500)
print(d)
