__author__ = 'brianoneill'

from log_calls import log_calls

MINIMAL = dict(
    log_args=False,
    log_exit=False
)

@log_calls(omit='prop.setter', settings=MINIMAL)
class XX():
    def getxx(self):     pass
    def setxx(self, val):     pass
    def delxx(self):          pass
    prop = property(getxx, setxx, delxx)
xx = XX(); xx.prop; xx.prop = 5; del xx.prop
# XX.getxx <== called by <module>
# XX.delxx <== called by <module>
