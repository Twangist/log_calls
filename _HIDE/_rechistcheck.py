__author__ = 'brianoneill'

from log_calls import record_history

d = dict(
    enabled=False,
    max_history=15,
    NO_DECO=False
)

# @record_history(enabled=True, NO_DECO=False)
@record_history(settings=d)
def f(x): pass

print( f.record_history_settings.as_dict())

