from log_calls import log_calls

MINIMAL = dict(
    log_args=False, log_exit=False
)

# Check:
# '[f-i]*'
# 'A.I.*'
# 'p*'
# '?[!n]*'        matches 'A.*' so this matches EVERYTHING
# '[!f-ip]*'      matches 'A.*' so this matches EVERYTHING
# 'A.[!f-ip]*'    matches A.I.i1, A.I.i2
# 'A.[!f-hp]*'    matches just i1 i2

@log_calls(only='A.I.*', settings=MINIMAL)
class A():
    def fn(self): pass
    def gn(self): pass
    def hn(self): pass
    @property
    def pr(self): pass
    @pr.setter
    def pr(self, x): pass
    @pr.deleter
    def pr(self): pass

    def pdg(self): pass
    def pds(self,x): pass
    pd = property(pdg, pds, None)

    class I():
        def i1(self): pass
        def i2(self): pass

a = A()
a.fn(); a.gn(); a.hn(); a.pr; a.pr = 5; del a.pr
a.pd; a.pd = 5
A.I().i1(); A.I().i2()
