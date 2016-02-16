__author__ = 'brianoneill'

from log_calls import log_calls
from log_calls.tests.set_reset_defaults.global_defaults import *
# Importing global_defaults performs ``log_calls.set_defaults(global_settings)``,
# for a settings dict ``global_settings``, so defaults are now changed, to:
#    log_call_numbers=True
#    log_exit=False
#    log_retval=True
#    args_sep=' $ '

##############################################################################
# tests
##############################################################################

def test_global_settings():
    """
    >>> @log_calls()
    ... def f(x, y):    return x*(x+1)//2 + y
    >>> @log_calls()
    ... def g(n):       return f(n, 2*n)
    >>> g(2)
    g [1] <== called by <module>
        arguments: n=2
        f [1] <== called by g [1]
            arguments: x=2 $ y=4
            f [1] return value: 7
        g [1] return value: 7
    7

    >>> f.log_calls_settings.as_OD()    # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True),    ('args_sep', ' $ '),        ('log_args', True),
                 ('log_retval', True), ('log_elapsed', False),     ('log_exit', False),
                 ('indent', True),     ('log_call_numbers', True), ('prefix', ''),
                 ('file', None),       ('logger', None),           ('loglevel', 10),
                 ('mute', False),      ('record_history', False),  ('max_history', 0)])

0.3.0b25 -- Test new log_calls.get_defaults_OD()

    >>> log_calls.get_defaults_OD()         # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True),     ('args_sep', ' $ '),         ('log_args', True),
                 ('log_retval', True),  ('log_elapsed', False),      ('log_exit', False),
                 ('indent', True),      ('log_call_numbers', True),  ('prefix', ''),
                 ('file', None),        ('logger', None),            ('loglevel', 10),
                 ('mute', False),       ('record_history', False),   ('max_history', 0)])

0.3.0b25 -- Test new log_calls.get_factory_defaults_OD()

    >>> log_calls.get_factory_defaults_OD() # doctest: +NORMALIZE_WHITESPACE
    OrderedDict([('enabled', True),     ('args_sep', ', '),          ('log_args', True),
                 ('log_retval', False), ('log_elapsed', False),      ('log_exit', True),
                 ('indent', True),      ('log_call_numbers', False), ('prefix', ''),
                 ('file', None),        ('logger', None),            ('loglevel', 10),
                 ('mute', False),       ('record_history', False),   ('max_history', 0)])

Calling `log_calls.reset_defaults()` won't change the settings of `f` or `g`,
of course -- only of newly decorated functions:

    >>> log_calls.reset_defaults()
    >>> f(1, 2)
    f [2] <== called by <module>
        arguments: x=1 $ y=2
        f [2] return value: 3
    3

    >>> log_calls.get_defaults_OD() == log_calls.get_factory_defaults_OD()
    True

    >>> @log_calls()
    ... def h(x, y, z): return x+y+z
    >>> h(1, 2, 3)
    h <== called by <module>
        arguments: x=1, y=2, z=3
    h ==> returning to <module>
    6
    """
    pass


##############################################################################
# end of tests.
##############################################################################

# def not_test():
#     """
#     Same thing, not as a test
#     """
#     @log_calls()
#     def f(x, y):    return x*(x+1)//2 + y
#     @log_calls()
#     def g(n):       return f(n, 2*n)
#     g(2)
#     # g [1] <== called by not_test
#     #     arguments: n=2
#     #     f [1] <== called by g [1]
#     #         arguments: x=2 $ y=4
#     #         f [1] return value: 7
#     #     g [1] return value: 7
#     # 7
#
#     # check global defaults in force — YEP
#     # ALSO check order of settings -- oughta be same as in .get_defaults_OD, get_factory_defaults_OD
#     # WHY IS ``NO_DECO`` ***NOT*** IN HERE (it's good that it isn't! But what keeps it out.)
#     print(
#         f.log_calls_settings.as_OD()    # doctest: +NORMALIZE_WHITESPACE
#     )
#     """
#     OrderedDict([('enabled', True),    ('args_sep', ' $ '),        ('log_args', True),
#                  ('log_retval', True), ('log_elapsed', False),     ('log_exit', False),
#                  ('indent', True),     ('log_call_numbers', True), ('prefix', ''),
#                  ('file', None),       ('logger', None),           ('loglevel', 10),
#                  ('mute', False),      ('record_history', False),  ('max_history', 0)])
#     """
#
#     # Test new log_calls.get_defaults_OD()
#     print(
#         log_calls.get_defaults_OD()             # doctest: +NORMALIZE_WHITESPACE
#     )
#     '''
#     OrderedDict([('enabled', False),    ('args_sep, ' $ '),          ('log_args', True),
#                  ('log_retval', True),  ('log_elapsed', False),      ('log_exit', False),
#                  ('indent', True),      ('log_call_numbers', True),  ('prefix', ''),
#                  ('file', None),        ('logger', None),            ('loglevel', 10),
#                  ('mute', False),       ('record_history', False),   ('max_history', 0)])
#     '''
#
#     # Test new log_calls.get_factory_defaults_OD()
#     print(
#         log_calls.get_factory_defaults_OD()     # doctest: +NORMALIZE_WHITESPACE
#     )
#     '''
#     OrderedDict([('enabled', False),    ('args_sep', ', '),          ('log_args', True),
#                  ('log_retval', False), ('log_elapsed', False),      ('log_exit', True),
#                  ('indent', True),      ('log_call_numbers', False), ('prefix', ''),
#                  ('file', None),        ('logger', None),            ('loglevel', 10),
#                  ('mute', False),       ('record_history', False),   ('max_history', 0)])
#     '''
#
#     log_calls.reset_defaults()
#     f(1, 2)                     # f settings unchanged
#     # f [2] <== called by <module>
#     #     arguments: x=1 $ y=2
#     #     f [2] return value: 3
#     # 3
#
#     print(
#         log_calls.get_defaults_OD() == log_calls.get_factory_defaults_OD()
#     )
#     # True
#
#     @log_calls()
#     def h(x, y, z): return x+y+z
#     h(1, 2, 3)
#     # h <== called by <module>
#     #     arguments: x=1, y=2, z=3
#     # h ==> returning to <module>
#     # 6

##############################################################################

import doctest

# For unittest integration
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests


if __name__ == "__main__":

    # not_test()

    doctest.testmod()   # (verbose=True)

    log_calls.reset_defaults()
