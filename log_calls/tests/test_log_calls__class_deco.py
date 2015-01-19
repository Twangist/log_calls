from log_calls import log_calls

import doctest


##############################################################################
# doctests
##############################################################################

#=============================================================================
# main__lc_class_deco__all_method_types
#=============================================================================

#-----------------------
# data
#-----------------------

@log_calls(indent=True, args_sep='\n', log_call_numbers=True, log_retval=True)
class C():
    clsmember = 17

    @log_calls(log_retval=False)
    def __init__(self, x):
        self.x = x

    def foo(self, y):
        self.x = y
        return self.clsmeth(y * 2) + 17

    @classmethod
    @log_calls(args_sep=' / ')
    def clsmeth_lc(cls, z):
        return cls.clsmeth(z)

    @classmethod
    def clsmeth(cls, z):
        cls.clsmember = z
        return z // 2

    @staticmethod
    @log_calls(log_elapsed=True)
    def statmeth_lc(q):
        for i in range(50000):
            pass
        return 2 * q

    @staticmethod
    def statmeth(q):
        return 4 * q


#-----------------------
# doctest
#-----------------------

def main__lc_class_deco__all_method_types():
    """
    >>> assert C.clsmeth_lc(15) == 7            # doctest: +NORMALIZE_WHITESPACE
    C.clsmeth_lc [1] <== called by <module>
        arguments: cls=<class '__main__.C'> / z=15
        C.clsmeth [1] <== called by C.clsmeth_lc [1]
            arguments:
                cls=<class '__main__.C'>
                z=15
            C.clsmeth [1] return value: 7
        C.clsmeth [1] ==> returning to C.clsmeth_lc [1]
        C.clsmeth_lc [1] return value: 7
    C.clsmeth_lc [1] ==> returning to <module>

    >>> C.clsmember == 15
    True

    >>> assert C.statmeth_lc(100) == 200        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    C.statmeth_lc [1] <== called by <module>
        arguments:
            q=100
        C.statmeth_lc [1] return value: 200
        elapsed time: ... [secs], CPU time: ... [secs]
    C.statmeth_lc [1] ==> returning to <module>

    >>> c = C(1000)                             # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    C.__init__ [1] <== called by <module>
        arguments:
            self=<__main__.C object at 0x...>
            x=1000
    C.__init__ [1] ==> returning to <module>

    >>> c.x == 1000
    True

    >>> assert c.foo(-10) == 7                  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    C.foo [1] <== called by <module>
        arguments:
            self=<__main__.C object at 0x...>
            y=-10
        C.clsmeth [2] <== called by C.foo [1]
            arguments:
                cls=<class '__main__.C'>
                z=-20
            C.clsmeth [2] return value: -10
        C.clsmeth [2] ==> returning to C.foo [1]
        C.foo [1] return value: 7
    C.foo [1] ==> returning to <module>

    >>> c.x == -10
    True

    >>> _ = c.statmeth(125)                     # doctest: +NORMALIZE_WHITESPACE
    C.statmeth [1] <== called by <module>
        arguments:
            q=125
        C.statmeth [1] return value: 500
    C.statmeth [1] ==> returning to <module>
    """
    pass

# SURGERY:
main__lc_class_deco__all_method_types.__doc__ = \
    main__lc_class_deco__all_method_types.__doc__.replace("__main__", __name__)


#=============================================================================
# main__lc_class_deco__all_method_types
#=============================================================================

#-----------------------
# data
#-----------------------
@log_calls(indent=True, args_sep='\n', log_call_numbers=True, log_retval=True)
class D():
    def __init__(self):
        pass

    @staticmethod
    def makeDI_1(x):
        return D.DI_1(x)

    @log_calls(args_sep='; ', log_retval=False)
    class DI_1():
        def __init__(self, x, y=91):
            self._init_aux(x, y)
            self.x = x
            self.y = y

        def _init_aux(self, x, y):
            pass

        @log_calls(log_call_numbers=False, log_retval=True)
        def f(self):
            return self.x * self.x + self.y

    class DI_2():
        def __init__(self):
            pass

        def g(self):
            pass

        @log_calls(log_call_numbers=False, log_retval=False)
        def h(self):
            pass


#-----------------------
# doctest
#-----------------------
def main__lc_class_deco__inner_classes():
    """
    >>> di1 = D().makeDI_1(17)      # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    D.__init__ [1] <== called by <module>
        arguments:
            self=<__main__.D object at 0x...>
    D.__init__ [1] ==> returning to <module>
    D.makeDI_1 [1] <== called by <module>
        arguments:
            x=17
        D.DI_1.__init__ [1] <== called by D.makeDI_1 [1]
            arguments: self=<__main__.D.DI_1 object at 0x...>; x=17
            defaults:  y=91
            D.DI_1._init_aux [1] <== called by D.DI_1.__init__ [1]
                arguments: self=<__main__.D.DI_1 object at 0x...>; x=17; y=91
            D.DI_1._init_aux [1] ==> returning to D.DI_1.__init__ [1]
        D.DI_1.__init__ [1] ==> returning to D.makeDI_1 [1]
        D.makeDI_1 [1] return value: <__main__.D.DI_1 object at 0x...>
    D.makeDI_1 [1] ==> returning to <module>

    >>> _ = di1.f()                 # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    D.DI_1.f <== called by <module>
        arguments: self=<__main__.D.DI_1 object at 0x...>
        D.DI_1.f return value: 380
    D.DI_1.f ==> returning to <module>

    >>> di2 = D.DI_2()              # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    D.DI_2.__init__ [1] <== called by <module>
        arguments:
            self=<__main__.D.DI_2 object at 0x...>
    D.DI_2.__init__ [1] ==> returning to <module>

    >>> di2.g()                     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    D.DI_2.g [1] <== called by <module>
        arguments:
            self=<__main__.D.DI_2 object at 0x...>
        D.DI_2.g [1] return value: None
    D.DI_2.g [1] ==> returning to <module>

    >>> di2.h()                     # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    D.DI_2.h <== called by <module>
        arguments:
            self=<__main__.D.DI_2 object at 0x...>
    D.DI_2.h ==> returning to <module>
    """
    pass


# SURGERY:
main__lc_class_deco__inner_classes.__doc__ = \
    main__lc_class_deco__inner_classes.__doc__.replace("__main__", __name__)


#=============================================================================
# main__lc_class_deco__immutable_setting
#=============================================================================

@log_calls(max_history=10)
class A():
    def f(self, x): pass

    @log_calls(max_history=17)
    def g(self, x): pass

    @log_calls(enabled=False)
    def h(self):    pass


def main__lc_class_deco__immutable_setting():
    """
    >>> a = A()
    >>> a.f.log_calls_settings.max_history
    10
    >>> a.g.log_calls_settings.max_history
    17
    >>> a.h.log_calls_settings.max_history
    10
    """

##############################################################################
# end of tests.
##############################################################################
# import inspect
#
#
# def classinfo(cls):
#     for name in cls.__dict__:
#         item = getattr(cls, name)
#         print(name, ' -- ', item)
#         if inspect.ismethoddescriptor(item): print("\tismethoddescriptor")
#         elif inspect.ismemberdescriptor(item): print("\tismemberdescriptor")
#         elif inspect.ismethod(item): print("\tismethod")
#         raw_item = cls.__getattribute__(cls, name)
#         if type(raw_item) in (staticmethod, classmethod) or inspect.isfunction(raw_item):
#             print("\t%s" % type(raw_item))


##############################################################################
# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":
    # classinfo(C)
    # print('==================================================')

    print('==================================================')
    doctest.testmod()   # (verbose=True)

    # unittest.main()
