__author__ = 'brianoneill'

from log_calls import log_calls

global_settings = dict(
    enabled=True,
    log_call_numbers=True,
    log_exit=False,
    log_retval=True,
)
log_calls.set_defaults(global_settings, args_sep=' $ ')
