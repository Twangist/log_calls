__author__ = "Brian O'Neill"
__version__ = '0.3.0'

from log_calls import log_calls
import doctest


#-----------------------------------------------------------------------------
# main__test__get_own_log_calls_wrapper
# test methods accessing their OWN wrappers via utility function/classmethod
# Aiming for complete coverage of the function
#-----------------------------------------------------------------------------
def main__test__get_own_log_calls_wrapper():
    """
Class we'll use through this entire set of tests:

    >>> @log_calls(omit='no_deco', mute=log_calls.MUTE.CALLS)
    ... class B():
    ...     def __init__(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     def method(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     def no_deco(self):
    ...         wrapper = self.get_own_log_calls_wrapper()         # raises ValueError
    ...         wrapper.log_message('Hi')
    ...     @staticmethod
    ...     def statmethod():
    ...         wrapper = B.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...
    ...     @classmethod
    ...     def clsmethod(cls):
    ...         wrapper = B.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...
    ...     @property
    ...     def prop(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...     @prop.setter
    ...     @log_calls(name='B.%s.setter')
    ...     def prop(self, val):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi')
    ...
    ...     def setx(self, val):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi from setx alias x.setter')
    ...     def delx(self):
    ...         wrapper = self.get_own_log_calls_wrapper()
    ...         wrapper.log_message('Hi from delx alias x.deleter')
    ...     x = property(None, setx, delx)

    >>> b = B()
    B.__init__: Hi
    >>> b.method()
    B.method: Hi
    >>> b.no_deco()     # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    AttributeError: ...
    >>> b.statmethod()
    B.statmethod: Hi
    >>> b.clsmethod()
    B.clsmethod: Hi
    >>> b.prop
    B.prop: Hi
    >>> b.prop = 17
    B.prop.setter: Hi
    >>> b.x = 13
    B.setx: Hi from setx alias x.setter
    >>> del b.x
    B.delx: Hi from delx alias x.deleter

This won't work/is wrong:

    try:
        b.method.get_own_log_calls_wrapper()
    except AttributeError as e:
        # 'function' object has no attribute 'get_own_log_calls_wrapper'
        print(e)

    >>> try:
    ...     b.no_deco()
    ... except AttributeError as e:
    ...     print(e)
    'no_deco' is not decorated [1]

    >>> b.method.log_calls_settings.enabled = 0
    >>> # no log_* output if enabled <= 0, but method can still call get_own_log_calls_wrapper
    >>> b.method()

    >>> b.method.log_calls_settings.enabled = -1
    >>> # "true bypass" -- method can't call get_own_log_calls_wrapper
    >>> try:
    ...     b.method()
    ... except AttributeError as e:
    ...     print(e)
    'method' is true-bypassed (enabled < 0) or not decorated [2]

Induce more errors

    >>> def _deco_base_f_wrapper_():     # note name -- fake out get_own_log_calls_wrapper for a few clauses
    ...     # No local named _deco_base__active_call_items__
    ...     try:
    ...         b.no_deco()
    ...     except AttributeError as e:
    ...         print(e)
    >>> _deco_base_f_wrapper_()
    'no_deco' is true-bypassed (enabled < 0) or not decorated [2]

    >>> def _deco_base_f_wrapper_():         # note name -- fake out get_own_log_calls_wrapper longer
    ...     _deco_base__active_call_items__ = 17    # exists but isn't a dict
    ...     try:
    ...         b.no_deco()
    ...     except AttributeError as e:
    ...         print(e)
    >>> _deco_base_f_wrapper_()
    'no_deco' is not decorated [3]

    >>> def _deco_base_f_wrapper_():         # note name -- fake out get_own_log_calls_wrapper still longer
    ...     _deco_base__active_call_items__ = {    # exists, is a dict, no key '_wrapper_deco'
    ...         'a': 45
    ...     }
    ...     try:
    ...         b.no_deco()
    ...     except AttributeError as e:
    ...         print(e)
    >>> _deco_base_f_wrapper_()
    'no_deco' is not decorated [3]

    >>> def _deco_base_f_wrapper_():         # note name -- fake out get_own_log_calls_wrapper even longer
    ...     _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
    ...         '_wrapper_deco': 45
    ...     }
    ...     try:
    ...         b.no_deco()
    ...     except AttributeError as e:
    ...         print(e)
    >>> _deco_base_f_wrapper_()
    'no_deco' is not decorated [3]

    >>> def _deco_base_f_wrapper_():         # note name -- fake out get_own_log_calls_wrapper even longer
    ...     _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
    ...         '_wrapper_deco': log_calls()    # correct type, but not hooked up properly
    ...     }
    ...     try:
    ...         b.no_deco()
    ...     except AttributeError as e:
    ...         print(e)
    >>> _deco_base_f_wrapper_()
    inconsistent log_calls decorator object for 'no_deco' [4]

    >>> def _deco_base_f_wrapper_():         # note name -- fake out get_own_log_calls_wrapper even longer
    ...     lc = log_calls()    # correct type, but still not hooked up properly
    ...     lc.f = None
    ...     _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
    ...         '_wrapper_deco': lc
    ...     }
    ...
    ...     try:
    ...         b.no_deco()
    ...     except AttributeError as e:
    ...         print(e)
    >>> _deco_base_f_wrapper_()
    inconsistent log_calls decorator object for 'no_deco' [5]

    >>> def _deco_base_f_wrapper_():         # note name -- fake out get_own_log_calls_wrapper even longer
    ...     lc = log_calls()    # correct type, but still not hooked up properly
    ...     lc.f = None
    ...     _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
    ...         '_wrapper_deco': lc
    ...     }
    ...
    ...     try:
    ...         b.no_deco()
    ...     except AttributeError as e:
    ...         print(e)
    >>> _deco_base_f_wrapper_()
    inconsistent log_calls decorator object for 'no_deco' [5]

    >>> def _deco_base_f_wrapper_():         # note name -- fake out get_own_log_calls_wrapper even longer
    ...     lc = log_calls()    # correct type, lc.f correct, but STILL not hooked up properly
    ...     lc.f = B.no_deco
    ...     _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
    ...         '_wrapper_deco': lc
    ...     }
    ...
    ...     try:
    ...         b.no_deco()
    ...     except AttributeError as e:
    ...         print(e)
    >>> _deco_base_f_wrapper_()
    inconsistent log_calls decorator object for 'no_deco' [7]

    """
    pass

##############################################################################
# end of tests.
##############################################################################


#-----------------------------------------------------------------------------
# For unittest integration
#-----------------------------------------------------------------------------
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":

    doctest.testmod()   # (verbose=True)

    # unittest.main()
