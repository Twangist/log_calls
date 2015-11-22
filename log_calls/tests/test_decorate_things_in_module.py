__author__ = 'brianoneill'

from log_calls import log_calls

###############################################################

def decorate_class_use_then_import_use():
    """
    >>> from log_calls.tests import some_module

    >>> log_calls.decorate_class(some_module.C,
    ...                          decorate_subclasses=True,
    ...                          args_sep='; ', indent=True, omit='__init__')

    >>> d = some_module.D("Hello,")
    >>> d.concat("world!")                  # doctest: +ELLIPSIS
    C.concat <== called by <module>
        arguments: self=<log_calls.tests.some_module.D object at 0x...>; s='world!'
    C.concat ==> returning to <module>
    'Hello, world!'

    >>> d.tacnoc("world!")                  # doctest: +ELLIPSIS
    D.tacnoc <== called by <module>
        arguments: self=<log_calls.tests.some_module.D object at 0x...>; s='world!'
        C.concat <== called by D.tacnoc
            arguments: self=<log_calls.tests.some_module.D object at 0x...>; s='world!'
        C.concat ==> returning to D.tacnoc
    D.tacnoc ==> returning to <module>
    '!dlrow ,olleH'


    >>> from log_calls.tests.some_module import C, D
    >>> c = C("Yo,")
    >>> c.concat("Sammy?")                  # doctest: +ELLIPSIS
    C.concat <== called by <module>
        arguments: self=<log_calls.tests.some_module.C object at 0x...>; s='Sammy?'
    C.concat ==> returning to <module>
    'Yo, Sammy?'

    >>> d = D("Hey,")
    >>> d.concat("Leroy!")                  # doctest: +ELLIPSIS
    C.concat <== called by <module>
        arguments: self=<log_calls.tests.some_module.D object at 0x...>; s='Leroy!'
    C.concat ==> returning to <module>
    'Hey, Leroy!'
    """
    pass

def decorate_external_function__use_then_import_use():
    """
    >>> from log_calls.tests import some_other_module

    >>> log_calls.decorate_external_function(some_other_module.make_id,
    ...                                      args_sep=' | ', log_retval=True)

    >>> print(some_other_module.make_id(15, 632))
    make_id <== called by <module>
        arguments: a=15 | b=632
        make_id return value: 0015-0632-A
    make_id ==> returning to <module>
    0015-0632-A

    >>> from log_calls.tests.some_other_module import make_id

    >>> print(make_id(15, 632))
    make_id <== called by <module>
        arguments: a=15 | b=632
        make_id return value: 0015-0632-A
    make_id ==> returning to <module>
    0015-0632-A
    """
    pass

def decorate_function__imported_function():
    """
    >>> from log_calls.tests.some_other_module import make_id2

    >>> log_calls.decorate_function(make_id2,
    ...                             args_sep=' || ')

`make_id2` is decorated:

    >>> print(make_id2(48, 123))
    make_id2 <== called by <module>
        arguments: a=48 || b=123
    make_id2 ==> returning to <module>
    J_0048_0123_XYZ
    """
    pass

def decorate_function__function_in_same_module():
    """
    >>> def func1(x, y):    return x
    >>> log_calls.decorate_function(func1, args_sep='; ')
    >>> func1(5, 10)
    func1 <== called by <module>
        arguments: x=5; y=10
    func1 ==> returning to <module>
    5
    """
    pass

def decorate_external_function__function_in_same_module__doesnt_work():
    """
    >>> def func2(x, y):    return y
    >>> log_calls.decorate_external_function(func2, args_sep=' ~ ')

`func2` is NOT decorated:
    >>> func2(99, 100)
    100
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
