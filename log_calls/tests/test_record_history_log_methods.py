__author__ = 'brianoneill'

from log_calls import record_history

#-----------------------------------------------------
# record_history.log_message, record_history.log_exprs
# Test in methods, in functions
#-----------------------------------------------------
def test_rh_log_message__output_expected():
    """
    ------------------------------------------------
     log_message
    ------------------------------------------------

    >>> @record_history(omit='not_decorated')
    ... class B():
    ...     def __init__(self):
    ...         record_history.log_message('Hi')
    ...         # Test that the old version still works! It shares code.
    ...         wrapper = self.get_own_record_history_wrapper()
    ...         wrapper.log_message("Hi from original log_message")
    ...
    ...     def method(self):
    ...         record_history.log_message('Hi')
    ...     def not_decorated(self):
    ...         record_history.log_message('Hi')
    ...     @classmethod
    ...     def clsmethod(cls):
    ...         record_history.log_message('Hi')
    ...     @staticmethod
    ...     def statmethod():
    ...         record_history.log_message('Hi')
    ...
    ...     @property
    ...     def prop(self):
    ...         record_history.log_message('Hi')
    ...     @prop.setter
    ...     @record_history(name='B.%s.setter')
    ...     def prop(self, val):
    ...         record_history.log_message('Hi')
    ...
    ...     def setx(self, val):
    ...         record_history.log_message('Hi from setx alias x.setter')
    ...     def delx(self):
    ...         record_history.log_message('Hi from delx alias x.deleter')
    ...     x = property(None, setx, delx)

    >>> b = B()
    B.__init__ [1]: Hi
    B.__init__ [1]: Hi from original log_message

    >>> b.method()
    B.method [1]: Hi

    >>> # NO OUTPUT from this, nor an exception,
    >>> # because by default
    >>> #   record_history.log_methods_raise_if_no_deco == False
    >>> b.not_decorated()

    >>> b.statmethod()
    B.statmethod [1]: Hi
    >>> b.clsmethod()
    B.clsmethod [1]: Hi
    >>> b.prop
    B.prop [1]: Hi
    >>> b.prop = 17
    B.prop.setter [1]: Hi
    >>> b.x = 13
    B.setx [1]: Hi from setx alias x.setter
    >>> del b.x
    B.delx [1]: Hi from delx alias x.deleter

    ------------------------------------------------
     log_exprs
    ------------------------------------------------

    >>> @record_history(omit='not_decorated')
    ... class D():
    ...     def __init__(self):
    ...         x = 2
    ...         y = 3
    ...         # Original first:
    ...         wrapper = self.get_own_record_history_wrapper()
    ...         wrapper.log_exprs('x', 'y', 'x+y')
    ...
    ...         record_history.log_exprs('x', 'y', 'x+y')
    ...
    ...     def method(self):
    ...         x = 2; y = 3
    ...         record_history.log_exprs('x', 'y', 'x+y')
    ...
    ...     def not_decorated(self):
    ...         x = 2; y = 3
    ...         record_history.log_exprs('x', 'y', 'x+y')
    ...
    ...     @classmethod
    ...     def clsmethod(cls):
    ...         x = 2; y = 3
    ...         record_history.log_exprs('x', 'y', 'cls.__name__')
    ...
    ...     @staticmethod
    ...     def statmethod():
    ...         x = 2; y = 3
    ...         record_history.log_exprs('x', 'y', 'x+y')
    ...
    ...     @property
    ...     def prop(self):
    ...         x = 2; y = 3
    ...         record_history.log_exprs('x', 'y', 'x+y')
    ...
    ...     @prop.setter
    ...     @record_history(name='D.%s.setter')
    ...     def prop(self, val):
    ...         x = 2; y = 3
    ...         record_history.log_exprs('x', 'y', 'x+y')
    ...
    ...     def setx(self, val):
    ...         x = 2; y = 3
    ...         record_history.log_exprs('x', 'y', 'x+y')
    ...
    ...     def delx(self):
    ...         x = 2; y = 3
    ...         record_history.log_exprs('x', 'y', 'x+y')
    ...     x = property(None, setx, delx)

    >>> d = D()
    D.__init__ [1]: x = 2, y = 3, x+y = 5
    D.__init__ [1]: x = 2, y = 3, x+y = 5

    >>> d.method()
    D.method [1]: x = 2, y = 3, x+y = 5

    # NO OUTPUT from this, NOR AN EXCEPTION,
    # because by default
    #   record_history.log_methods_raise_if_no_deco == False
    >>> d.not_decorated()

    >>> d.statmethod()
    D.statmethod [1]: x = 2, y = 3, x+y = 5

    >>> d.clsmethod()
    D.clsmethod [1]: x = 2, y = 3, cls.__name__ = 'D'

    >>> d.prop
    D.prop [1]: x = 2, y = 3, x+y = 5

    >>> d.prop = 17
    D.prop.setter [1]: x = 2, y = 3, x+y = 5

    >>> d.x = 13
    D.setx [1]: x = 2, y = 3, x+y = 5

    >>> del d.x
    D.delx [1]: x = 2, y = 3, x+y = 5

    ------------------------------------------------
     functions
    ------------------------------------------------

    >>> @record_history()
    ... def bar(x, y, z):
    ...     record_history.log_message("Hi", "there")
    ...     pass

    >>> bar(1, 2, 3)
    bar [1]: Hi there

    """
    pass


#-----------------------------------------------------
# Test record_history.log_methods_raise_if_no_deco (bool)
# On undecorated functions/methods,
# and deco'd but with NO_DECO=True parameter
#-----------------------------------------------------

def test_rh_log_message__no_output_no_exceptions_expected():
    """
    >>> record_history.log_methods_raise_if_no_deco = False  # the default

    >>> def nodeco(x, y, z):
    ...     record_history.log_message("Hi", "from", "function nodeco")
    ...     pass
    >>> nodeco(11, 12, 13)            # no output, NO EXCEPTION

    >>> @record_history(omit='not_decorated')
    ... class A():
    ...     def __init__(self):
    ...         record_history.log_message('Hi')
    ...     def not_decorated(self):
    ...         record_history.log_message('Hi')

    >>> a = A()
    A.__init__ [1]: Hi

    >>> a.not_decorated()   # no output, NO EXCEPTION


    >>> @record_history(NO_DECO=True)
    ... class C():
    ...     def __init__(self):
    ...         record_history.log_message('Hi')
    ...     def cmethod(self, x):
    ...         record_history.log_message('Hi')
    ...         record_history.log_exprs('x + 10')

    >>> c = C()         # no output, no exception

    >>> c.cmethod(5)    # no output, no exception

    >>> def schmoe(x):
    ...     record_history.log_message("Yo, schmoe")
    ...     pass

    >>> schmoe(170)     # no output, no exception
    """
    pass


def test_rh_log_message__exceptions_expected():
    """
    >>> record_history.log_methods_raise_if_no_deco = True   # not the default

    >>> @record_history(omit='not_decorated')
    ... class A():
    ...     def __init__(self):
    ...         record_history.log_message('Hi')
    ...     def not_decorated(self):
    ...         record_history.log_message('Hi')

    >>> a = A()
    A.__init__ [1]: Hi
    >>> a.not_decorated()       # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
    Traceback (most recent call last):
        ...
    AttributeError: ... is not decorated...

    >>> @record_history(NO_DECO=True)
    ... class B():
    ...     def __init__(self):
    ...         # Comment out so we can create a B object!
    ...         # record_history.log_message('Hi')
    ...         pass
    ...     def bmethod1(self):
    ...         record_history.log_message('Hi')
    ...     def bmethod2(self, z):
    ...         record_history.log_exprs('z * 3')

    >>> b = B()     # no harm, noop

    >>> b.bmethod1()  # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
    Traceback (most recent call last):
        ...
    AttributeError: ... is not decorated...

    >>> b.bmethod2(1)  # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
    Traceback (most recent call last):
        ...
    AttributeError: ... is not decorated...


    >>> @record_history(NO_DECO=True)
    ... def foo(x, y, z):
    ...     record_history.log_message("Hi", "from", "function foo")
    ...     pass

    >>> foo(1, 2, 3)  # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
    Traceback (most recent call last):
        ...
    AttributeError: ... is not decorated...

    Undecorated, ever

    >>> def schmoe(x):
    ...     record_history.log_message("Yo, schmoe")
    ...     pass

    >>> schmoe(100)  # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
    Traceback (most recent call last):
        ...
    AttributeError: ... is not decorated...

    """
    pass


###############################################################
import doctest

# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests

if __name__ == '__main__':

    doctest.testmod()
