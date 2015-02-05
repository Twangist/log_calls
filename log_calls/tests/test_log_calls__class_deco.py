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
# main__lc_class_deco__inner_classes
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


#=============================================================================
# main__lc_class_deco__omit_only__basic
#=============================================================================
MINIMAL = dict(
    log_args=False, log_exit=False
)


def main__lc_class_deco__omit_only__basic():
    """
    >>> @log_calls(omit='f g', settings=MINIMAL)
    ... class E():
    ...     def f(self): pass
    ...     def g(self): pass
    ...     def h(self): pass
    >>> e = E(); e.f(); e.g(); e.h()
    E.h <== called by <module>

    >>> @log_calls(only='f, h', settings=MINIMAL)
    ... class F():
    ...     def f(self): pass
    ...     def g(self): pass
    ...     def h(self): pass
    >>> eff = F(); eff.f(); eff.g(); eff.h()
    F.f <== called by <module>
    F.h <== called by <module>

    >>> @log_calls(only=['f', 'g'], omit=('g',), settings=MINIMAL)
    ... class G():
    ...     def f(self): pass
    ...     def g(self): pass
    ...     def h(self): pass
    >>> gee = G(); gee.f(); gee.g(); gee.h()
    G.f <== called by <module>
    """
    pass


#=============================================================================
# main__lc_class_deco__omit_only__inner_classes
#=============================================================================
def main__lc_class_deco__omit_only__inner_classes():
    """
Qualified (class-prefixed) names; names that match more than one method

    >>> @log_calls(only=('H.HI.f', 'g'), settings=MINIMAL)
    ... class H():
    ...     def f(self): pass
    ...     def g(self): pass
    ...     def h(self): pass
    ...     class HI():
    ...         def f(self): pass
    ...         def g(self): pass
    ...         def h(self): pass
    >>> aich = H(); aich.f(); aich.g(); aich.h()
    H.g <== called by <module>
    >>> hi = H.HI(); hi.f(); hi.g(); hi.h()
    H.HI.f <== called by <module>
    H.HI.g <== called by <module>

Wildcard '*'
Omitting all/any inner classes with '*.*.*':
# NOTE: qualname will *always* match '*.*' so can't use that to filter for inner classes

    >>> @log_calls(omit='*.*.*', settings=MINIMAL)
    ... class O():
    ...     def f(self): pass
    ...     class I1():
    ...         def g1(self): pass
    ...     class I2():
    ...         def g2(self): pass
    >>> O().f(); O.I1().g1(); O.I2().g2()
    O.f <== called by <module>

Only '*_handler' methods:

    >>> @log_calls(only='*_handler', settings=MINIMAL)
    ... class O():
    ...     def f(self): pass
    ...     def my_handler(self): pass
    ...     def their_handler(self): pass
    ...     class I1():
    ...         def g1(self): pass
    ...         def some_handler(self): pass
    ...     class I2():
    ...         def another_handler(self): pass
    ...         def g2(self): pass
    >>> oh = O(); oh.f(); oh.my_handler(); oh.their_handler()
    O.my_handler <== called by <module>
    O.their_handler <== called by <module>
    >>> ohi1 = O.I1(); ohi1.g1(); ohi1.some_handler()
    O.I1.some_handler <== called by <module>
    >>> ohi2 = O.I2(); ohi2.another_handler(); ohi2.g2()
    O.I2.another_handler <== called by <module>

Wildcard '?':

    >>> @log_calls(only='f_ab?', settings=MINIMAL)
    ... class X():
    ...     def f_ab(self): pass
    ...     def f_abc(self): pass
    ...     def f_abd(self): pass
    >>> x = X(); x.f_ab(); x.f_abc(); x.f_abd()
    X.f_abc <== called by <module>
    X.f_abd <== called by <module>

Character sets and ranges

Match characters in set:

    >>> @log_calls(only='g_ab[cd]*', settings=MINIMAL)
    ... class Y():
    ...     def g_ab7_and_more(self): pass
    ...     def g_abc_or_something(self): pass
    ...     def g_abd_perhaps(self): pass
    >>> y = Y(); y.g_ab7_and_more(); y.g_abc_or_something(); y.g_abd_perhaps()
    Y.g_abc_or_something <== called by <module>
    Y.g_abd_perhaps <== called by <module>

Match characters in range:

    >>> @log_calls(only='g_ab[a-z]*', settings=MINIMAL)
    ... class Y():
    ...     def g_ab7_and_more(self): pass
    ...     def g_abc_or_something(self): pass
    ...     def g_abd_perhaps(self): pass
    >>> y = Y(); y.g_ab7_and_more(); y.g_abc_or_something(); y.g_abd_perhaps()
    Y.g_abc_or_something <== called by <module>
    Y.g_abd_perhaps <== called by <module>

Match characters not in range

    >>> @log_calls(only='g_ab[!a-z]*', settings=MINIMAL)
    ... class Y():
    ...     def g_ab7_and_more(self): pass
    ...     def g_abc_or_something(self): pass
    ...     def g_abd_perhaps(self): pass
    >>> y = Y(); y.g_ab7_and_more(); y.g_abc_or_something(); y.g_abd_perhaps()
    Y.g_ab7_and_more <== called by <module>

When provided and nonempty, inner `only` overrides outer `only`
In I1, only g1 is decorated, despite the outer class's `only` specifier:

    >>> @log_calls(only='*_handler', settings=MINIMAL)
    ... class O():
    ...     def f(self): pass
    ...     def my_handler(self): pass
    ...     def their_handler(self): pass
    ...     @log_calls(only='g1')
    ...     class I1():
    ...         def g1(self): pass
    ...         def some_handler(self): pass
    >>> ohi1 = O.I1(); ohi1.g1(); ohi1.some_handler()
    O.I1.g1 <== called by <module>

If inner class has no `only` [or if it's an empty string or empty tuple or empty list],
`only` from the outer class applies:

    >>> @log_calls(only='*_handler', settings=MINIMAL)
    ... class O():
    ...     def f(self): pass
    ...     def my_handler(self): pass
    ...     def their_handler(self): pass
    ...     @log_calls(log_exit=True)
    ...     class I1():
    ...         def g1(self): pass
    ...         def some_handler(self): pass
    >>> ohi1 = O.I1(); ohi1.g1(); ohi1.some_handler()
    O.I1.some_handler <== called by <module>
    O.I1.some_handler ==> returning to <module>


Inner `omit` is added to outer `omit`

    >>> @log_calls(omit='*_handler', settings=MINIMAL)
    ... class O():
    ...     def f(self): pass
    ...     def my_handler(self): pass
    ...     def their_handler(self): pass
    ...     @log_calls(omit='*_function')
    ...     class I1():
    ...         def g1(self): pass
    ...         def some_handler(self): pass
    ...         def some_function(self): pass
    >>> ohi1 = O.I1(); ohi1.g1(); ohi1.some_handler(); ohi1.some_function()
    O.I1.g1 <== called by <module>
    """
    pass


#=============================================================================
# main__lc_class_deco__undecorate_methods
#=============================================================================
def main__lc_class_deco__undecorate_methods():
    """
Topmost-class level:

    >>> @log_calls(omit='f', settings=MINIMAL)
    ... class O():
    ...     @log_calls()
    ...     def f(self): pass
    >>> O().f()         # (no output)

    >>> @log_calls(only='g', settings=MINIMAL)
    ... class O():
    ...     @log_calls()
    ...     def f(self): pass
    ...     def g(self): pass
    >>> O().f(); O().g()
    O.g <== called by <module>

Inner class:

    >>> @log_calls(omit='f', settings=MINIMAL)
    ... class O():
    ...     @log_calls(omit='g')
    ...     class I():
    ...         def f(self): pass
    ...         def g(self): pass
    >>> O.I().f(); O.I().g()        # (no output)

    >>> @log_calls(only='f', settings=MINIMAL)
    ... class O():
    ...     @log_calls(only='g')
    ...     class I():
    ...         def f(self): pass
    ...         def g(self): pass
    >>> O.I().f(); O.I().g()
    O.I.g <== called by <module>

    """
    pass


#=============================================================================
# main__lc_class_deco__undecorate_properties
#=============================================================================
def main__lc_class_deco__undecorate_entire_property():
    """
Property specified via decorator:
    Top-level:
        - only
    >>> @log_calls(only='f', settings=MINIMAL)
    ... class A():
    ...     def f(self): pass
    ...     @property
    ...     @log_calls()
    ...     def prop(self): pass
    ...     @prop.setter
    ...     @log_calls()
    ...     def prop(self, val): pass
    >>> A().f(); A().prop; A().prop = 17
    A.f <== called by <module>

        - omit
    >>> @log_calls(omit='prop')
    ... class A():
    ...     @property
    ...     @log_calls()
    ...     def prop(self): pass
    ...     @prop.setter
    ...     @log_calls()
    ...     def prop(self, val): pass
    >>> A().prop; A().prop = 17     # (no output)

    Inner class:
        - only
    >>> @log_calls(only='f', settings=MINIMAL)
    ... class A():
    ...     @log_calls()
    ...     class I():
    ...         def f(self): pass
    ...         @property
    ...         def prop(self): pass
    ...         @prop.setter
    ...         def prop(self, val): pass
    >>> A.I().f(); A.I().prop; A.I().prop = 17
    A.I.f <== called by <module>

        - omit
    >>> @log_calls(omit='prop', settings=MINIMAL)
    ... class A():
    ...     @log_calls(omit='f')
    ...     class I():
    ...         def f(self): pass
    ...         @property
    ...         def prop(self): pass
    ...         @prop.setter
    ...         def prop(self, val): pass
    >>> A.I().f(); A.I().prop; A.I().prop = 17  # (no output)

Property specified via property():
    Top-level:
        (FIRST, here's what happens without `only` or `omit`):
    >>> @log_calls(settings=MINIMAL)
    ... class A():
    ...     def f(self): pass
    ...     @log_calls()
    ...     def prop_get(self): pass
    ...     @log_calls()
    ...     def prop_set(self, val): pass
    ...     @log_calls()
    ...     def prop_del(self): pass
    ...     prop = property(prop_get, prop_set, prop_del)
    >>> A().f(); A().prop; A().prop = 17; del A().prop
    A.f <== called by <module>
    A.prop_get <== called by <module>
    A.prop_set <== called by <module>
    A.prop_del <== called by <module>

        - only
    >>> @log_calls(only='f', settings=MINIMAL)
    ... class A():
    ...     def f(self): pass
    ...     @log_calls()
    ...     def prop_get(self): pass
    ...     @log_calls()
    ...     def prop_set(self, val): pass
    ...     prop = property(prop_get, prop_set)
    >>> A().f(); A().prop; A().prop = 17
    A.f <== called by <module>

        - omit
    >>> @log_calls(omit='prop', settings=MINIMAL)
    ... class A():
    ...     def f(self): pass
    ...     @log_calls()
    ...     def prop_get(self): pass
    ...     @log_calls()
    ...     def prop_set(self, val): pass
    ...     prop = property(prop_get, prop_set)
    >>> A().f(); A().prop; A().prop = 17
    A.f <== called by <module>


    Inner class:
        - only
    >>> @log_calls(only='f', settings=MINIMAL)
    ... class A():
    ...     @log_calls()
    ...     class I():
    ...         def f(self): pass
    ...         def prop_get(self): pass
    ...         def prop_set(self, val): pass
    ...         prop = property(prop_get, prop_set)
    >>> A.I().f(); A.I().prop; A.I().prop = 17
    A.I.f <== called by <module>

        - omit
    >>> @log_calls(omit='prop', settings=MINIMAL)
    ... class A():
    ...     @log_calls()
    ...     class I():
    ...         def f(self): pass
    ...         def prop_get(self): pass
    ...         def prop_set(self, val): pass
    ...         prop = property(prop_get, prop_set)
    >>> A.I().f(); A.I().prop; A.I().prop = 17
    A.I.f <== called by <module>

    """
    pass


#=============================================================================
# main__lc_class_deco__undecorate_property_attrs
#=============================================================================
def main__lc_class_deco__undecorate_property_attrs():
    """
Property specified via decorator:
    Top-level:
        - only
    >>> @log_calls(only='prop.getter', settings=MINIMAL)
    ... class A():
    ...     @property
    ...     def prop(self): pass
    ...     @prop.setter
    ...     @log_calls()
    ...     def prop(self, val): pass
    >>> A().prop; A().prop = 17
    A.prop <== called by <module>

        - omit
    >>> @log_calls(omit='prop.setter', settings=MINIMAL)
    ... class A():
    ...     def f(self): pass
    ...     @property
    ...     @log_calls(name='A.%s.getter')
    ...     def prop(self): pass
    ...     @prop.setter
    ...     @log_calls()
    ...     def prop(self, val): pass
    >>> A().f(); A().prop; A().prop = 17
    A.f <== called by <module>
    A.prop.getter <== called by <module>

    Inner class:
        - only
    >>> @log_calls(only='prop.deleter', settings=MINIMAL)
    ... class A():
    ...     @log_calls()
    ...     class I():
    ...         def f(self): pass
    ...         @property
    ...         def prop(self): pass
    ...         @prop.setter
    ...         def prop(self, val): pass
    ...         @prop.deleter
    ...         @log_calls(name='A.I.%s.deleter')
    ...         def prop(self): pass
    >>> A.I().f(); A.I().prop; A.I().prop = 17; del A.I().prop
    A.I.prop.deleter <== called by <module>

        - omit
    >>> @log_calls(omit='prop.setter prop.deleter', settings=MINIMAL)
    ... class A():
    ...     @log_calls(omit='f')
    ...     class I():
    ...         def f(self): pass
    ...         @property
    ...         def prop(self): pass
    ...         @prop.setter
    ...         def prop(self, val): pass
    ...         @prop.deleter
    ...         def prop(self): pass
    >>> A.I().f(); A.I().prop; A.I().prop = 17; del A.I().prop
    A.I.prop <== called by <module>

    >>> A.log_calls_omit
    ('prop.setter', 'prop.deleter')
    >>> A.I.log_calls_omit
    ('prop.setter', 'prop.deleter', 'f')

Property specified via property():
    Top-level:
        - only [OBSERVE, uses both ways of referring to the property attrs]
    >>> @log_calls(only='prop_get prop.deleter', settings=MINIMAL)
    ... class A():
    ...     @log_calls()
    ...     def prop_get(self): pass
    ...     @log_calls()
    ...     def prop_set(self, val): pass
    ...     @log_calls()
    ...     def prop_del(self): pass
    ...     prop = property(prop_get, prop_set, prop_del)
    >>> A().prop; A().prop = 17; del A().prop
    A.prop_get <== called by <module>
    A.prop_del <== called by <module>

    >>> A.log_calls_only
    ('prop_get', 'prop.deleter', 'prop_del')

        - omit
        Referring to 'prop_get' rather than 'prop.getter' works reliably because prop_get is already decorated

    >>> @log_calls(omit='prop_get', settings=MINIMAL)
    ... class A():
    ...     def f(self): pass
    ...     @log_calls()
    ...     def prop_get(self): pass
    ...     @log_calls()
    ...     def prop_del(self): pass
    ...     prop = property(prop_get, None, prop_del)
    >>> A().f(); A().prop; del A().prop
    A.f <== called by <module>
    A.prop_del <== called by <module>

    Inner class:
        - only
    >>> @log_calls(only='prop.getter', settings=MINIMAL)
    ... class A():
    ...     @log_calls()
    ...     class I():
    ...         def f(self): pass
    ...         def prop_get(self): pass
    ...         def prop_set(self, val): pass
    ...         prop = property(prop_get, prop_set)
    >>> A.I().f(); A.I().prop; A.I().prop = 17
    A.I.prop_get <== called by <module>

    >>> A.I.log_calls_only
    ('prop.getter', 'prop_get')

        - omit
    >>> @log_calls(omit='prop_get', settings=MINIMAL)
    ... class A():
    ...     @log_calls()
    ...     class I():
    ...         def f(self): pass
    ...         def prop_get(self): pass
    ...         def prop_set(self, val): pass
    ...         prop = property(prop_get, prop_set)
    >>> A.I().f(); A.I().prop; A.I().prop = 17
    A.I.f <== called by <module>
    A.I.prop_set <== called by <module>

    >>> A.I.log_calls_omit
    ('prop_get',)
    """
    pass


#=============================================================================
# main__lc_class_deco__omitonly_with_property_ctor__use_qualified_names
#=============================================================================
def main__lc_class_deco__omitonly_with_property_ctor__use_qualified_names():
    """
We perform fixups on the 'omit' and 'only' lists so that you can use
propertyname.getter, propertyname.setter, propertyname.deleter
to refer to methods supplied to the 'property' constructor, which are also
in the class dictionary.

Empirically: In Python 3.4.2, 'xx' is enumerated before 'setxx' in class XX.
Without the fixup, these tests would (or, could) fail.

- omit

    >>> @log_calls(omit='xx.setter')
    ... class XX():
    ...     def __init__(self): pass
    ...     def method(self): pass
    ...     @staticmethod
    ...     def statmethod():        pass
    ...     @classmethod
    ...     def clsmethod(cls):      pass
    ...     def setxx(self, val):     pass
    ...     def delxx(self):          pass
    ...     xx = property(None, setxx, delxx)

The method is NOT decorated:

    >>> XX.log_calls_wrapper('xx.setter') is None
    True
    >>> XX.log_calls_wrapper('setxx') is None
    True

    >>> XX.log_calls_omit
    ('xx.setter', 'setxx')

- only

    >>> @log_calls(only='y.setter')
    ... class Y():
    ...     def __init__(self): pass
    ...     def method(self): pass
    ...     @staticmethod
    ...     def statmethod():        pass
    ...     @classmethod
    ...     def clsmethod(cls):      pass
    ...     def sety(self, val):     pass
    ...     def dely(self):          pass
    ...     y = property(None, sety, dely)

Wrappers found for 'sety' and 'y.setter' are identical:

    >>> Y.log_calls_wrapper('sety') is Y.log_calls_wrapper('y.setter')
    True

and the method IS decorated:

    >>> bool( Y.log_calls_wrapper('sety') )
    True

    >>> Y.log_calls_only
    ('y.setter', 'sety')

    """
    pass


#=============================================================================
# main__lc_class_deco__omitonly_with_property_ctor__property_name_only
#=============================================================================
def main__lc_class_deco__omitonly_with_property_ctor__property_name_only():
    """
Same class we test omit='xx.setter' with,
where `xx` is a property created using `property` constructor,
and `xx` is enumerated by `cls.__dict__` before `setxx` in Py3.4.2.
This failed in  prior to handling entire properties
in `_deco_base._add_property_method_names`

    >>> @log_calls(omit='xx')
    ... class XX():
    ...     def __init__(self): pass
    ...     def method(self): pass
    ...     @staticmethod
    ...     def statmethod():        pass
    ...     @classmethod
    ...     def clsmethod(cls):      pass
    ...     def setxx(self, val):     pass
    ...     def delxx(self):          pass
    ...     xx = property(None, setxx, delxx)

The method is NOT decorated:

    >>> XX.log_calls_wrapper('xx.setter') is None
    True
    >>> XX.log_calls_wrapper('setxx') is None
    True

    >>> XX.log_calls_omit
    ('xx', 'setxx', 'delxx')

    - only

    >>> @log_calls(only='xxx')
    ... class XXX():
    ...     def __init__(self): pass
    ...     def method(self): pass
    ...     @staticmethod
    ...     def statmethod():        pass
    ...     @classmethod
    ...     def clsmethod(cls):      pass
    ...     def setxxx(self, val):     pass
    ...     def delxxx(self):          pass
    ...     xxx = property(None, setxxx, delxxx)

Wrappers found for 'setxxx' and 'xxx.setter' are identical:

    >>> XXX.log_calls_wrapper('setxxx') is XXX.log_calls_wrapper('xxx.setter')
    True

and the method IS decorated:

    >>> bool( XXX.log_calls_wrapper('setxxx') )
    True

    >>> XXX.log_calls_only
    ('xxx', 'setxxx', 'delxxx')

    """
    pass


#-----------------------------------------------------------------------------
# main__lc_class_deco__omitonly_locals_in_qualname
#-----------------------------------------------------------------------------
def main__lc_class_deco__omitonly_locals_in_qualname():
    """
Only A.create_objs.<locals>.I.method and A.create_objs.<locals>.I.delx will be decorated.
We have to test using `.<locals>` in `omit`/`only`. This is an artificial example,
but they all would be -- `.<locals>` only qualifies functions, classes and variables local
to a function, and `log_calls` does NOT recurse into function bodies (the locals of a function)
as it does into class members, so anything decorated inside a function will have to be
decorated explicitly, and then the `... .<locals>.` isn't needed to disambiguate anything.
Nevertheless, :

    >>> @log_calls(omit='create_obj')
    ... class A():
    ...     def create_obj(self):
    ...         @log_calls(omit='A.create_obj.<locals>.I.?etx  prop', settings=MINIMAL)
    ...         class I():
    ...             def method(self): pass
    ...             def getx(self): pass
    ...             def setx(self, v): pass
    ...             def delx(self): pass
    ...             x = property(getx, setx, delx)
    ...             @property
    ...             def prop(self): pass
    ...             @prop.setter
    ...             def prop(self, v): pass
    ...
    ...         return I()

    >>> aye = A().create_obj()
    >>> aye.method(); aye.x; aye.x = 42; del aye.x; aye.prop; aye.prop = 101
    A.create_obj.<locals>.I.method <== called by <module>
    A.create_obj.<locals>.I.delx <== called by <module>
    """
    pass


#-----------------------------------------------------------------------------
# main__test__log_calls_wrapper__from_outside
#-----------------------------------------------------------------------------
def main__test__log_calls_wrapper__from_outside():
    """
    >>> @log_calls(omit='*_nodeco delx')
    ... class A():
    ...     def __init__(self):      pass
    ...     def method(self):        pass
    ...
    ...     def method_nodeco(self): pass
    ...
    ...     @staticmethod
    ...     def statmethod():        pass
    ...     @classmethod
    ...     def clsmethod(cls):      pass
    ...
    ...     @staticmethod
    ...     def statmethod_nodeco():   pass
    ...     @classmethod
    ...     def clsmethod_nodeco(cls): pass
    ...
    ...     @property
    ...     def prop(self):          pass
    ...     @prop.setter
    ...     def prop(self, val):     pass
    ...
    ...     def setx(self, val):     pass
    ...     def delx(self):          pass
    ...
    ...     x = property(None, setx, delx)
    >>> a = A()                             # doctest: +ELLIPSIS
    A.__init__ <== called by <module>
        arguments: self=<__main__.A object at 0x...>
    A.__init__ ==> returning to <module>

First, the method names that work
---------------------------------
    >>> decorated_A = (
    ...     '__init__',
    ...     'method',
    ...     'statmethod',
    ...     'clsmethod',
    ...     'prop',
    ...     'prop.getter',
    ...     'prop.setter',
    ...     'x.setter',
    ...     'setx',
    ... )
    >>> all(a.log_calls_wrapper(name) for name in decorated_A)
    True

    >>> not_decorated_A = (
    ...     'method_nodeco',
    ...     'statmethod_nodeco',
    ...     'clsmethod_nodeco',
    ...     'x.deleter',
    ...     'delx',
    ... )
    >>> all((a.log_calls_wrapper(name) is None) for name in not_decorated_A)
    True
    >>> a.log_calls_wrapper('x.setter') == a.log_calls_wrapper('setx')
    True
    >>> a.log_calls_wrapper('x.deleter') == a.log_calls_wrapper('delx')
    True

Stuff that fails - deco'd class
-------------------------------

    >>> bad_names = (
    ...     'no_such_method',
    ...     'foo.bar.baz',
    ...     'foo.',
    ...     'prop.',
    ...     'prop.foo',
    ...     'prop.deleter',
    ...     'x.getter',
    ...     'x',        # equiv to x.getter
    ...     'method.getter',
    ...     '.uvwxyz',
    ...     'not an identifier',
    ...     '88 < x**2',
    ...
    ...     '__doc__',
    ...     17,
    ...     False,
    ...     tuple(),
    ...     ['83'],
    ...     None
    ... )
    >>> for name in bad_names:
    ...     try:
    ...         wrapper = a.log_calls_wrapper(name)
    ...     except ValueError as e:
    ...         print(e)
    ...     except TypeError as e:
    ...         print(e)
    ValueError: class 'A' has no such attribute as 'no_such_method'
    ValueError: no such method specifier 'foo.bar.baz'
    ValueError: bad method specifier 'foo.'
    ValueError: bad method specifier 'prop.'
    ValueError: prop.foo -- unknown qualifier 'foo'
    ValueError: property 'prop' has no 'deleter' in class 'A'
    ValueError: property 'x' has no 'getter' in class 'A'
    ValueError: property 'x' has no 'getter' in class 'A'
    ValueError: method.getter -- 'method' is not a property of class 'A'
    ValueError: bad method specifier '.uvwxyz'
    ValueError: class 'A' has no such attribute as 'not an identifier'
    ValueError: class 'A' has no such attribute as '88 < x**2'
    TypeError: item '__doc__' of class 'A' is of type 'NoneType' and can't be decorated
    TypeError: expecting str for argument 'fname', got 17 of type int
    TypeError: expecting str for argument 'fname', got False of type bool
    TypeError: expecting str for argument 'fname', got () of type tuple
    TypeError: expecting str for argument 'fname', got ['83'] of type list
    TypeError: expecting str for argument 'fname', got None of type NoneType


Now, stuff that fails - non-deco'd class
----------------------------------------

    >>> class NoDeco():
    ...     pass

    >>> nd = NoDeco()
    >>> # 'NoDeco' object has no attribute 'log_calls_wrapper'
    >>> print(nd.log_calls_wrapper)             # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    AttributeError: ...

    >>> # 'NoDeco' object has no attribute 'log_calls_wrapper'
    >>> print(nd.log_calls_wrapper('__init__'))  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    AttributeError: ...
    """
    pass

# SURGERY:
main__test__log_calls_wrapper__from_outside.__doc__ = \
    main__test__log_calls_wrapper__from_outside.__doc__.replace("__main__", __name__)

#-----------------------------------------------------------------------------
# main__test__log_calls_wrapper__from_inside
# test methods accessing their OWN wrappers
#-----------------------------------------------------------------------------
def main__test__log_calls_wrapper__from_inside():
    """
    >>> @log_calls(omit='no_deco', mute=True)
    ... class B():
    ...     def __init__(self):
    ...         wrapper = self.log_calls_wrapper('__init__')
    ...         wrapper.log_message('Hi')
    ...     def method(self):
    ...         wrapper = self.log_calls_wrapper('method')
    ...         wrapper.log_message('Hi')
    ...     def no_deco(self):
    ...         wrapper = self.log_calls_wrapper('no_deco')
    ...         wrapper.log_message('Hi')
    ...     @staticmethod
    ...     def statmethod():
    ...         wrapper = B.log_calls_wrapper('statmethod')
    ...         wrapper.log_message('Hi')
    ...
    ...     @classmethod
    ...     def clsmethod(cls):
    ...         wrapper = B.log_calls_wrapper('clsmethod')
    ...         wrapper.log_message('Hi')
    ...
    ...     @property
    ...     def prop(self):
    ...         wrapper = self.log_calls_wrapper('prop.getter')
    ...         wrapper.log_message('Hi')
    ...     @prop.setter
    ...     def prop(self, val):
    ...         wrapper = self.log_calls_wrapper('prop.setter')
    ...         wrapper.log_message('Hi from prop.setter')
    ...
    ...     def setx(self, val):
    ...         wrapper = self.log_calls_wrapper('setx')
    ...         wrapper.log_message('Hi from setx alias x.setter')
    ...     def delx(self):
    ...         wrapper = self.log_calls_wrapper('x.deleter')
    ...         wrapper.log_message('Hi from delx alias x.deleter')
    ...
    ...     x = property(None, setx, delx)
    >>> b = B()
    B.__init__: Hi
    >>> b.method()
    B.method: Hi
    >>> b.statmethod()
    B.statmethod: Hi
    >>> b.clsmethod()
    B.clsmethod: Hi
    >>> b.prop
    B.prop: Hi
    >>> b.prop = 17
    B.prop: Hi from prop.setter
    >>> b.x = 13
    B.setx: Hi from setx alias x.setter
    >>> del b.x
    B.delx: Hi from delx alias x.deleter

`no_deco` is not decorated, so `log_calls_wrapper` returns None,
but the method tries to access its `log_message` attribute --
hence this error message:

    >>> b.no_deco()         # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    AttributeError: 'NoneType' object has no attribute 'log_message'

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

    @log_calls(omit='no_deco', mute=True)
    class B():
        def __init__(self):
            wrapper = self.log_calls_wrapper()
            wrapper.log_message('Hi')
        def method(self):
            wrapper = self.log_calls_wrapper()
            wrapper.log_message('Hi')
        def no_deco(self):
            wrapper = self.log_calls_wrapper()
            wrapper.log_message('Hi')
        @staticmethod
        def statmethod():
            wrapper = B.log_calls_wrapper()
            wrapper.log_message('Hi')

        @classmethod
        def clsmethod(cls):
            wrapper = B.log_calls_wrapper()
            wrapper.log_message('Hi')

        @property
        def prop(self):
            wrapper = self.log_calls_wrapper()
            wrapper.log_message('Hi')
        @prop.setter
        def prop(self, val):
            wrapper = self.log_calls_wrapper()
            wrapper.log_message('Hi from prop.setter')

        def setx(self, val):
            wrapper = self.log_calls_wrapper()
            wrapper.log_message('Hi from setx alias x.setter')
        def delx(self):
            wrapper = self.log_calls_wrapper()
            wrapper.log_message('Hi from delx alias x.deleter')

        x = property(None, setx, delx)
    b = B()
    # B.__init__: Hi
    b.method()
    # B.method: Hi
    b.statmethod()
    # B.statmethod: Hi
    b.clsmethod()
    #B.clsmethod: Hi
    b.prop
    #B.prop: Hi
    b.prop = 17
    #B.prop: Hi from prop.setter
    b.x = 13
    #B.setx: Hi from setx alias x.setter
    del b.x
    #B.delx: Hi from delx alias x.deleter

# `no_deco` is not decorated, so `log_calls_wrapper` returns None,
# but the method tries to access its `log_message` attribute --
# hence this error message:
#
#    >>> b.no_deco()         # doctest: +IGNORE_EXCEPTION_DETAIL
#    Traceback (most recent call last):
#        ...
#    AttributeError: 'NoneType' object has no attribute 'log_message'

# This won't work/is wrong:
    try:
        b.method.log_calls_wrapper()
    except AttributeError as e:
        # 'function' object has no attribute 'log_calls_wrapper'
        print(e)

    try:
        b.no_deco()
    except ValueError as e:
        print(e)
        # ''no_deco' is not decorated [1]

    b.method.log_calls_settings.enabled = 0
    b.method()  # no log_* output if enabled <= 0, but method can still call log_calls_wrapper

    b.method.log_calls_settings.enabled = -1     # "true bypass" -- method can't call log_calls_wrapper
    try:
        b.method()
    except ValueError as e:
        print(e)
        # ValueError: 'method' appears to be true-bypassed (enabled < 0) or undecorated

# TODO induce more errors

    def f_log_calls_wrapper_():     # note name -- fake out log_calls_wrapper for a few clauses
        # No local named _deco_base__active_call_items__
        try:
            b.no_deco()
        except ValueError as e:
            print(e)
    f_log_calls_wrapper_()  # 'no_deco' appears to be true-bypassed (enabled < 0) or undecorated

    def f_log_calls_wrapper_():         # note name -- fake out log_calls_wrapper longer
        _deco_base__active_call_items__ = 17    # exists but isn't a dict
        try:
            b.no_deco()
        except ValueError as e:
            print(e)
    f_log_calls_wrapper_()  # 'no_deco' appears to not be decorated

    def f_log_calls_wrapper_():         # note name -- fake out log_calls_wrapper still longer
        _deco_base__active_call_items__ = {    # exists, is a dict, no key '_wrapper_deco'
            'a': 45
        }
        try:
            b.no_deco()
        except ValueError as e:
            print(e)
    f_log_calls_wrapper_()  # 'no_deco' appears to not be decorated

    def f_log_calls_wrapper_():         # note name -- fake out log_calls_wrapper even longer
        _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
            '_wrapper_deco': 45
        }
        try:
            b.no_deco()
        except ValueError as e:
            print(e)
    f_log_calls_wrapper_()  # 'no_deco' is not decorated

    def f_log_calls_wrapper_():         # note name -- fake out log_calls_wrapper even longer
        _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
            '_wrapper_deco': log_calls()    # correct type, but not hooked up properly
        }
        try:
            b.no_deco()
        except ValueError as e:
            print(e)
    f_log_calls_wrapper_()  # log_calls decorator object for 'no_deco' missing an attribute (internal error or external damage)

    def f_log_calls_wrapper_():         # note name -- fake out log_calls_wrapper even longer
        lc = log_calls()    # correct type, but still not hooked up properly
        lc.f = None
        _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
            '_wrapper_deco': lc
        }

        try:
            b.no_deco()
        except ValueError as e:
            print(e)
    f_log_calls_wrapper_()  # inconsistent log_calls decorator object for 'no_deco'

    def f_log_calls_wrapper_():         # note name -- fake out log_calls_wrapper even longer
        lc = log_calls()    # correct type, but still not hooked up properly
        lc.f = None
        _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
            '_wrapper_deco': lc
        }

        try:
            b.no_deco()
        except ValueError as e:
            print(e)
    f_log_calls_wrapper_()  # inconsistent log_calls decorator object for 'no_deco'

    def f_log_calls_wrapper_():         # note name -- fake out log_calls_wrapper even longer
        lc = log_calls()    # correct type, lc.f correct, but STILL not hooked up properly
        lc.f = B.no_deco
        _deco_base__active_call_items__ = {    # exists, is a dict, has key '_wrapper_deco', but type != log_calls
            '_wrapper_deco': lc
        }

        try:
            b.no_deco()
        except ValueError as e:
            print(e)
    f_log_calls_wrapper_()  # couldn't find log_calls wrapper of 'no_deco'


#    exit(89)

    doctest.testmod()   # (verbose=True)

    # unittest.main()
