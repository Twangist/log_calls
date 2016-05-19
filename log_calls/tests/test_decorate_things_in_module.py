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

    >>> log_calls.decorate_module_function(some_other_module.make_id,
    ...                                    args_sep=' | ', log_retval=True)

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
    >>> log_calls.decorate_module_function(func2, args_sep=' ~ ')

`func2` is NOT decorated:
    >>> func2(99, 100)
    100
    """
    pass

import sys
if sys.version_info.major == 3 and sys.version_info.minor >= 5:

    def test__deco_fractions_dot_Fraction():
        """
    This example shows that you can decorate things in the standard library.

        >>> from fractions import Fraction as Fr
        >>> log_calls.decorate_class(Fr)
        >>> print(Fr(3,4))
        Fraction.__new__ <== called by <module>
            arguments: cls=<class 'fractions.Fraction'>, numerator=3, denominator=4
            defaults:  _normalize=True
        Fraction.__new__ ==> returning to <module>
        Fraction.__str__ <== called by <module>
            arguments: self=Fraction(3, 4)
        Fraction.__str__ ==> returning to <module>
        3/4

    (**Note**: In Python 3.4.y, the output lacks the third line, as in 3.4.x
               ``__new__`` has no ``_normalize`` parameter.)


    Create a couple of fractions, in silence:

        >>> log_calls.mute = True
        >>> fr56 = Fr(5,6)
        >>> fr78 = Fr(7,8)
        >>> log_calls.mute = False

    Let's trim the `log_calls` output. Experience shows that ``__str__`` gets called a lot,
    and it becomes just noise, so let's not decorate that. To eliminate more clutter, let's
    suppress the exit lines ("... returning to..."). We'll also display return values:

        >>> log_calls.decorate_class(Fr, omit='__str__', log_exit=False, log_retval=True)

    Now, let's do some arithmetic on fractions:

        >>> print(fr78 - fr56)
        Fraction._operator_fallbacks.<locals>.forward (__sub__) <== called by <module>
            arguments: a=Fraction(7, 8), b=Fraction(5, 6)
            Fraction.denominator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
                arguments: a=Fraction(7, 8)
                Fraction.denominator return value: 8
            Fraction.denominator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
                arguments: a=Fraction(5, 6)
                Fraction.denominator return value: 6
            Fraction.numerator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
                arguments: a=Fraction(7, 8)
                Fraction.numerator return value: 7
            Fraction.numerator <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
                arguments: a=Fraction(5, 6)
                Fraction.numerator return value: 5
            Fraction.__new__ <== called by _sub <== Fraction._operator_fallbacks.<locals>.forward (__sub__)
                arguments: cls=<class 'fractions.Fraction'>, numerator=2, denominator=48
                defaults:  _normalize=True
                Fraction.__new__ return value: 1/24
            Fraction._operator_fallbacks.<locals>.forward (__sub__) return value: 1/24
        1/24

    (**Note**: The output is different in Python 3.4.y -- it's less efficient,
    and it lacks the third to last line.*)

    Just cuz these are mentioned in Quick Start:
        >>> Fr.__sub__          # doctest: +ELLIPSIS
        <function Fraction._operator_fallbacks.<locals>.forward...>
        >>> Fr.__sub__.__qualname__
        'Fraction._operator_fallbacks.<locals>.forward'
        >>> Fr.__sub__.__name__
        '__sub__'

        """
        pass


###############################################################
import doctest

# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    # print("Adding tests for test_decorate_things_in_module.py")
    return tests

if __name__ == '__main__':
    doctest.testmod()
