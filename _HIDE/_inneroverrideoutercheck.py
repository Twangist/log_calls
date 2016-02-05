__author__ = 'brianoneill'

from log_calls import log_calls

MINIMAL = dict(
    log_args=False,
    log_exit=False
)

@log_calls(settings=MINIMAL)
class E():
    def f(self): pass
    @log_calls(log_exit=True)
    def g(self): pass
E().f(); E().g()
# E.f <== called by <module>
# E.g <== called by <module>
# E.g ==> returning to <module>

print()

@log_calls(settings=MINIMAL, override=True)
class E():
    def f(self): pass
    @log_calls(log_exit=True)
    def g(self): pass
E().f(); E().g()
# E.f <== called by <module>
# E.g <== called by <module>

print()

@log_calls(settings=MINIMAL)
class O():
    def f(self): pass
    class I():
        @log_calls(log_call_numbers=True)
        def fi(self): pass
        def gi(self): pass
O().f(); O().I().fi(); O().I().gi()
# O.f <== called by <module>
# O.I.fi [1] <== called by <module>
# O.I.gi <== called by <module>
