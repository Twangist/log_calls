__author__ = 'brianoneill'
from log_calls import log_calls

# @log_calls()
# def g1():
#     pass
# def g2():
#     g1()
# @log_calls(prefix='mid.')
# def g3():
#     g2()
# def g4():
#     g3()
# @log_calls()
# def g5():
#     g4()
#
# g5()
'''
g5 <== called by <module>
    mid.g3 <== called by g4 <== g5
        g1 <== called by g2 <== mid.g3
        g1 ==> returning to g2 ==> mid.g3
    mid.g3 ==> returning to g4 ==> g5
g5 ==> returning to <module>
'''

# @log_calls()
# def f(): pass
# def not_decorated(): f()
# @log_calls(enabled=False)
# def g(): not_decorated()
#
# g()
'''
f <== called by not_decorated
f ==> returning to not_decorated
'''
# @log_calls()
# def e(): pass
# def not_decorated_call_e(): e()
# @log_calls()
# def f(): not_decorated_call_e()
# def not_decorated_call_f(): f()
# @log_calls(enabled=False)
# def g(): not_decorated_call_f()
# @log_calls()
# def h(): g()
# h()
'''
h <== called by <module>
    f <== called by not_decorated_call_f <== g <== h
        e <== called by not_decorated_call_e <== f
        e ==> returning to not_decorated_call_e ==> f
    f ==> returning to not_decorated_call_f ==> g ==> h
h ==> returning to <module>
'''
# @log_calls()
# def h0(z):
#     pass
# def h1(x):
#     @log_calls(name='h1_inner')
#     def h1_inner(y):
#         h0(x*y)
#     return h1_inner
# def h2():
#     h1(2)(3)
# def h3():
#     h2()
# def h4():
#     @log_calls(name='h4_inner')
#     def h4_inner():
#         h3()
#     return h4_inner
# @log_calls()
# def h5():
#     h4()()
# h5()
'''
h5 <== called by <module>
    h4_inner <== called by h5
        h1_inner <== called by h2 <== h3 <== h4_inner
            arguments: y=3
            h0 <== called by h1_inner
                arguments: z=6
            h0 ==> returning to h1_inner
        h1_inner ==> returning to h2 ==> h3 ==> h4_inner
    h4_inner ==> returning to h5
h5 ==> returning to <module>
'''
# @log_calls()
# def j0():
#     pass
# def j1():
#     j0()
# def j2():
#     @log_calls()
#     def j2_inner():
#         j1()
#     j2_inner()
# @log_calls()
# def j3():
#     j2()
# j3()
'''
j3 <== called by <module>
    j2.<locals>.j2_inner <== called by j2 <== j3
        j0 <== called by j1 <== j2.<locals>.j2_inner
        j0 ==> returning to j1 ==> j2.<locals>.j2_inner
    j2.<locals>.j2_inner ==> returning to j2 ==> j3
j3 ==> returning to <module>
'''
# @log_calls()
# def f(): pass
# def not_decorated(): f()
# @log_calls(log_call_numbers=True)
# def g(): not_decorated()
# g()
'''
g [1] <== called by <module>
    f <== called by not_decorated <== g [1]
    f ==> returning to not_decorated ==> g [1]
g [1] ==> returning to <module>
'''
from collections import OrderedDict
@log_calls(log_call_numbers=True, log_retval=True)
def depth(d, key=None):
    """Middle line (elif) is needed only because
    max(empty_sequence) raises ValueError
    (whereas returning 0 would sensible and expected)
    """
    if not isinstance(d, dict): return 0    # base case
    elif not d:                 return 1
    else:                       return max(map(depth, d.values(), d.keys())) + 1
# y = depth(
#     OrderedDict(
#         (('a', 0),
#          ('b', OrderedDict( (('c1', 10), ('c2', 11)) )),
#          ('c', 'text'))
#     )
# )
# print(y)
'''
depth [1] <== called by <module>
    arguments: d=OrderedDict([('a', 0), ('b', OrderedDict([('c1', 10), ('c2', 11)])), ('c', 'text')])
    defaults:  key=None
    depth [2] <== called by depth [1]
        arguments: d=0, key='a'
        depth [2] return value: 0
    depth [2] ==> returning to depth [1]
    depth [3] <== called by depth [1]
        arguments: d=OrderedDict([('c1', 10), ('c2', 11)]), key='b'
        depth [4] <== called by depth [3]
            arguments: d=10, key='c1'
            depth [4] return value: 0
        depth [4] ==> returning to depth [3]
        depth [5] <== called by depth [3]
            arguments: d=11, key='c2'
            depth [5] return value: 0
        depth [5] ==> returning to depth [3]
        depth [3] return value: 1
    depth [3] ==> returning to depth [1]
    depth [6] <== called by depth [1]
        arguments: d='text', key='c'
        depth [6] return value: 0
    depth [6] ==> returning to depth [1]
    depth [1] return value: 2
depth [1] ==> returning to <module>
2
'''

# z = depth({2: {3:4}})
z = depth({})
print(z)

