__author__ = 'brianoneill'

from log_calls import record_history

d = dict(
    enabled=True,
    NO_DECO=False
)

@record_history(enabled=True, NO_DECO=False)
def f(x): pass

print( f.record_history_settings.as_dict())

