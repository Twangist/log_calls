__author__ = "Brian O'Neill"
_version__ = '0.3.0'

from log_calls import log_calls
import doctest


#-------------------------------------------------------------------
# test__omit_property_attr__repr_with_init_active
#-------------------------------------------------------------------

def test__omit_property_attr__repr_with_init_active():
    """
    >>> @log_calls(omit='pair.deleter')
    ... class P():
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...     @property
    ...     def pair(self):
    ...         return (self.x, self.y)
    ...     @pair.setter
    ...     def pair(self, pr):
    ...         self.x, self.y = pr
    ...     @pair.deleter
    ...     def pair(self):
    ...         print("pair.deleter called -- wouldn't know what to do.")
    ...     def __repr__(self):
    ...         return '<(%r, %r) at 0x%x>' % (self.x, self.y, id(self))
    >>> p = P(0, 0)                         # doctest: +ELLIPSIS
    P.__init__ <== called by <module>
        arguments: self=<__main__.P object at 0x...>, x=0, y=0
    P.__init__ ==> returning to <module>

    >>> print(p.pair)                       # doctest: +ELLIPSIS
    P.pair <== called by <module>
        arguments: self=<(0, 0) at 0x...>
    P.pair ==> returning to <module>
    (0, 0)

    >>> p.pair = (10, 11)                   # doctest: +ELLIPSIS
    P.pair <== called by <module>
        arguments: self=<(0, 0) at 0x...>, pr=(10, 11)
    P.pair ==> returning to <module>

    >>> print(p)                            # doctest: +ELLIPSIS
    <(10, 11) at 0x...>

    >>> del p.pair
    pair.deleter called -- wouldn't know what to do.
    """
    pass

# SURGERY:
test__omit_property_attr__repr_with_init_active.__doc__ = \
    test__omit_property_attr__repr_with_init_active.__doc__.replace("__main__", __name__)


#-------------------------------------------------------------------
# test__repr_with_init_active_2
# __repr__ handling for objects still in construction;
# class inside a function
#-------------------------------------------------------------------
def test__repr_with_init_active_2():
    """
    >>> @log_calls()
    ... def another_fn(y):
    ...     'called by X.__init__'
    ...     return 2 * y


    >>> def globfn():
    ...     class X():
    ...         def __init__(self):
    ...             self.helper(0)
    ...             another_fn(43)
    ...
    ...         @log_calls()
    ...         def helper(self, z):
    ...             'called by __init__ and by users of X objs'
    ...             return z + 1
    ...
    ...         def __repr__(self):
    ...             return "<X() at 0x%x>" % id(self)
    ...
    ...     return X()

`helper` called with __init__ active, so generic `object.__repr__` is used to display `self`,
 rather than the class's `__repr__`.

    >>> x = globfn()            # doctest: +ELLIPSIS
    globfn.<locals>.X.helper <== called by __init__
        arguments: self=<__main__.globfn.<locals>.X object at 0x...>, z=0
    globfn.<locals>.X.helper ==> returning to __init__
    another_fn <== called by __init__
        arguments: y=43
    another_fn ==> returning to __init__

The class's `__repr__` (address `0x...` is the same as above):
    >>> print(repr(x))          # doctest: +ELLIPSIS
    <X() at 0x...>

The instance's __init__ is not active so the class's `__repr__` is used:
    >>> _ = x.helper(100)       # doctest: +ELLIPSIS
    globfn.<locals>.X.helper <== called by <module>
        arguments: self=<X() at 0x...>, z=100
    globfn.<locals>.X.helper ==> returning to <module>
    """
    pass

# SURGERY:
test__repr_with_init_active_2.__doc__ = \
    test__repr_with_init_active_2.__doc__.replace("__main__", __name__)


#-------------------------------------------------------------------
# MORE __repr__ handling for objects still in construction
#-------------------------------------------------------------------
def test__repr_with_init_active_3():
    """
    >>> @log_calls()
    ... def g(obj):
    ...     pass


    >>> class Y():
    ...     def __init__(self, y):
    ...         g(self)
    ...         self.y = y
    ...
    ...     def method(self):
    ...         g(self)
    ...
    ...     def __repr__(self):
    ...         return "Y(%r)" % self.y
    >>> Y('arg').method()                # doctest: +ELLIPSIS
    g <== called by __init__
        arguments: obj=<__main__.Y object at 0x...>
    g ==> returning to __init__
    g <== called by method
        arguments: obj=Y('arg')
    g ==> returning to method
    """
    pass

# SURGERY:
test__repr_with_init_active_3.__doc__ = \
    test__repr_with_init_active_3.__doc__.replace("__main__", __name__)


#-------------------------------------------------------------------
# Tests/examples of `mute`
#-------------------------------------------------------------------
def test__mute():
    """
When a decorated function not muted (`mute` is `False`, the default),
log_calls produces output as do `log_message` and `log_exprs`, which uses `log_message`:
    >>> @log_calls()
    ... def f():
    ...     f.log_message('Hello, world!')
    >>> f()
    f <== called by <module>
        Hello, world!
    f ==> returning to <module>

When `mute` is `True` ( == `log_calls.MUTE.CALLS`),
no extra indent level, and messages are prefixed with function's display name:
    >>> f.log_calls_settings.mute = True
    >>> f()
    f: Hello, world!

When `mute` is `log_calls.MUTE.ALL`, log_message produces no output:
    >>> f.log_calls_settings.mute = log_calls.MUTE.ALL
    >>> f()     # (no output)
    """
    pass


#-------------------------------------------------------------------
# Tests/examples of log_message writing only if enabled
#-------------------------------------------------------------------
def test__log_message_only_if_enabled():
    """
Basic test
`log_message` writes only if `enabled` is true:

    >>> @log_calls()
    ... def f():
    ...     f.log_message('Hello, cruel world!')
    >>> f()
    f <== called by <module>
        Hello, cruel world!
    f ==> returning to <module>
    >>> f.log_calls_settings.enabled = False
    >>> f()     # (no output)
    >>> f.log_calls_settings.enabled = -1
    >>> f()     # (no output)


Test with recursion and indirect `enabled` values -
each instance of the fn should behave properly,
and should not destroy the behavior of instances further up the call chain.

    >>> @log_calls(enabled='_on=', indent=True)
    ... def rec(level, _on=True):
    ...     if level < 0:
    ...         rec.log_message("Hit bottom")
    ...         return
    ...     rec.log_message("About to call rec(%d, _on=%s)" % (level-1, not _on))
    ...     rec(level-1, _on=(not _on))
    ...     rec.log_message("Returned from rec(%d, _on=%s)" % (level-1, not _on))

    >>> rec(3)
    rec <== called by <module>
        arguments: level=3
        defaults:  _on=True
        About to call rec(2, _on=False)
        rec <== called by rec <== rec
            arguments: level=1, _on=True
            About to call rec(0, _on=False)
            rec <== called by rec <== rec
                arguments: level=-1, _on=True
                Hit bottom
            rec ==> returning to rec ==> rec
            Returned from rec(0, _on=False)
        rec ==> returning to rec ==> rec
        Returned from rec(2, _on=False)
    rec ==> returning to <module>

NOTE: In the call chains `rec <== called by rec <== rec` (and
similarly for `rec ==> returning to rec ==> rec`), the nearest `rec`,
to the left of "<==", is not enabled, and `log_calls` has chased back
further till it found an *enabled* function it decorated (namely, another
invocation of `rec`, with an odd value for `level`).
    """
    pass


#-------------------------------------------------------------------
# Tests/examples of log_message writing only if enabled
#-------------------------------------------------------------------
def test__log_message__indirect_mute():
    """
    settings = {'indent': True, 'mute': 'mute_'}

    @log_calls(settings=settings)
    def f(extra_mute_val=None, **kwargs):
        f.log_message("before g", prefix_with_name=True)
        g(extra_mute_val=extra_mute_val, **kwargs)
        f.log_message("after g", prefix_with_name=True)

    @log_calls(settings=settings)
    def g(extra_mute_val=None, **kwargs):
        g.log_message("before h", prefix_with_name=True)
        if extra_mute_val is not None and 'mute_' in kwargs:
            kwargs['mute_'] = extra_mute_val
        h(**kwargs)
        g.log_message("after h", prefix_with_name=True)

    @log_calls(settings=settings)
    def h(**kwargs):
        h.log_message("greetings", prefix_with_name=True)

    f(mute_=False)
    '''
    f <== called by <module>
        arguments: [**]kwargs={'mute_': False}
        defaults:  extra_mute_val=None
        f: before g
        g <== called by f
            arguments: extra_mute_val=None, [**]kwargs={'mute_': False}
            g: before h
            h <== called by g
                arguments: [**]kwargs={'mute_': False}
                h: greetings
            h ==> returning to g
            g: after h
        g ==> returning to f
        f: after g
    f ==> returning to <module>
    '''
    print('-----------------------')
    f(mute_=True)                   # True == log_calls.MUTE.CALLS
    '''
    f: before g
        g: before h
            h: greetings
        g: after h
    f: after g
    '''
    print('-----------------------')
    f(mute_=True, extra_mute_val=log_calls.MUTE.ALL)    # shut up h
    '''
    f: before g
        g: before h
        g: after h
    f: after g
    '''
    print('-----------------------')
    f(mute_=log_calls.MUTE.ALL)
    # (no output)

    """
    pass


#-------------------------------------------------------------------
# test__global_mute
#-------------------------------------------------------------------
def test__global_mute():
    """
Mute setting applied for a function's log_calls output
and within a function for log_message and log_expr output
is
    `max(`*function's mute setting*`, `*global mute*`)`

### Basic examples/tests

    >>> @log_calls(indent=True)
    ... def f(): f.log_message("Hi"); g()
    >>> @log_calls(indent=True)
    ... def g(): g.log_message("Hi")


    >>> assert log_calls.mute == False  # default
    >>> f()
    f <== called by <module>
        Hi
        g <== called by f
            Hi
        g ==> returning to f
    f ==> returning to <module>

    >>> log_calls.mute = True
    >>> f()
    f: Hi
        g: Hi

    >>> log_calls.mute = log_calls.MUTE.ALL
    >>> f()     # (no output)

    >>> log_calls.mute = False
    >>> g.log_calls_settings.mute = log_calls.MUTE.CALLS
    >>> f()
    f <== called by <module>
        Hi
        g: Hi
    f ==> returning to <module>

    >>> log_calls.mute = log_calls.MUTE.CALLS
    >>> g.log_calls_settings.mute = log_calls.MUTE.ALL
    >>> f()
    f: Hi

### Dynamic examples/tests

Global mute is always checked realtime

    >>> @log_calls(indent=True)
    ... def f(mute=False):
    ...     f.log_message("before g")
    ...     g(mute=mute)
    ...     f.log_message("after g")

    >>> @log_calls(indent=True)
    ... def g(mute=False):
    ...     g.log_message("entering g")
    ...     log_calls.mute = mute
    ...     g.log_message("leaving g")

    >>> log_calls.mute = False

Calls to f(), with default arg False, in effect turn off global mute midway through g:

    >>> f()
    f <== called by <module>
        arguments: <none>
        defaults:  mute=False
        before g
        g <== called by f
            arguments: mute=False
            entering g
            leaving g
        g ==> returning to f
        after g
    f ==> returning to <module>

    >>> log_calls.mute = log_calls.MUTE.CALLS
    >>> f()
    f: before g
        g: entering g
            leaving g
        g ==> returning to f
        after g
    f ==> returning to <module>

    >>> log_calls.mute = log_calls.MUTE.ALL
    >>> f()
            leaving g
        g ==> returning to f
        after g
    f ==> returning to <module>

    >>> log_calls.mute = log_calls.MUTE.CALLS
    >>> g.log_calls_settings.mute = log_calls.MUTE.ALL
    >>> f()
    f: before g
        after g
    f ==> returning to <module>

    >>> log_calls.mute = False

`g` is still completely muted
    >>> f(mute=log_calls.MUTE.CALLS)
    f <== called by <module>
        arguments: mute=True
        before g
    f: after g

`g` is still completely muted, and `log_calls.mute == log_calls.MUTE.CALLS`
    >>> f(mute=log_calls.MUTE.ALL)
    f: before g

    >>> log_calls.mute = False  # restore default!
    """
    pass


#-------------------------------------------------------------------
# Tests/examples of log_exprs
#-------------------------------------------------------------------
def test__log_exprs():
    """
    >>> import os
    >>> import math

    >>> @log_calls(mute=True)
    ... def fn(num_files):
    ...     order_of_magnitude = round(math.log10(num_files), 2)
    ...     fn.log_exprs('num_files', 'order_of_magnitude')
    ...     files_per_CPU = math.ceil(num_files/os.cpu_count())
    ...     username = "Joe Doe"
    ...     fn.log_exprs('files_per_CPU', 'username')
    ...     # ...
    ...     # bad exprs:
    ...     z = []
    ...     fn.log_exprs('16-', 'no_such_variable', '"some bum string', 'z[0]',
    ...                  sep='\\n' + (' ' * len('fn: ')))

    >>> fn(10000)
    fn: num_files = 10000, order_of_magnitude = 4.0
    fn: files_per_CPU = 2500, username = 'Joe Doe'
    fn: 16- = '<** unexpected EOF while parsing (<string>, line 1) **>'
        no_such_variable = "<** name 'no_such_variable' is not defined **>"
        "some bum string = '<** EOL while scanning string literal (<string>, line 1) **>'
        z[0] = '<** list index out of range **>'

Another:

    >>> def f(i):
    ...     return 2.5 * i**3 - 5 * i**2 + 17

    >>> @log_calls()        # mute=True
    ... def g(n):
    ...     for i in range(n):
    ...         g.log_exprs('i', 'f(i)')
    ...
    >>> g(5)
    g <== called by <module>
        arguments: n=5
        i = 0, f(i) = 17.0
        i = 1, f(i) = 14.5
        i = 2, f(i) = 17.0
        i = 3, f(i) = 39.5
        i = 4, f(i) = 97.0
    g ==> returning to <module>
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


if __name__ == '__main__':

    doctest.testmod()


