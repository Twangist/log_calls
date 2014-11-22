__author__ = "Brian O'Neill"  # BTO
__version__ = '0.2.4'
__doc__ = """
Slightly ad-hoc decorator
    used_unused_keywords
for `__init__` function of `log_calls`. It's not *totally* ad-hoc:
`log_calls.__init__` only uses half the functionality of this decorator ;/

This decorator allows a function to determine which of its keyword arguments
were actually supplied by its caller, and which were not supplied and therefore
receive default values. It makes these two collections available as OrderedDicts.
Given
    @used_unused_keywords()
    def h(a='yes', b='no', c=17, **kwargs):
        print("h, used keywords: ", h.get_used_keywords())
        print("h, unused keywords: ", h.get_unused_keywords())

each time `h` is called, it can can `OrderedDict`s of used and unused
(defaulted) keyword arguments together with their values,
using the methods `get_used_keywords()` and `get_unused_keywords()`
that the decorator adds (to the wrapper of `h`).

Only keyword arguments that appear explicitly in the decorated function's
signature occur in the dictionaries of "used" and "unused" keywords;
"implicit" keywords that show up in a function's **kwargs do not occur
in those dictionaries.

Mandatory keyword-only arguments that have no default value are of course
included in the "used" dictionary.

See the doctests in function main() below for examples/tests.
"""

from functools import wraps
import inspect
from .helpers import (get_explicit_kwargs_OD, get_defaulted_kwargs_OD)


class used_unused_keywords():
    """TODO
    """
    def __init__(self, enabled=True):
        _ = enabled             # enabled is um not used
        self._used_kwds = {}
        self._unused_kwds = {}

    def get_used_keywords(self):
        return self._used_kwds

    def get_unused_keywords(self):
        return self._unused_kwds

    def __call__(self, f):

        # (nada)

        @wraps(f)
        def f_used_unused_keywords_wrapper_(*args, **kwargs):

            # Figure out which parameters were NOT supplied
            # by the actual call - the 'defaulted' arguments
            f_params = inspect.signature(f).parameters
            bound_args = inspect.signature(f).bind(*args, **kwargs)

            # These return OrderedDicts
            self._used_kwds = get_explicit_kwargs_OD(f_params, bound_args, kwargs)
            self._unused_kwds = get_defaulted_kwargs_OD(f_params, bound_args)

            return f(*args, **kwargs)

        setattr(
            f_used_unused_keywords_wrapper_,
            'get_used_keywords',
            self.get_used_keywords,
        )
        setattr(
            f_used_unused_keywords_wrapper_,
            'get_unused_keywords',
            self.get_unused_keywords,
        )

        return f_used_unused_keywords_wrapper_


#----------------------------------------------------------------------------
# doctests
#----------------------------------------------------------------------------
def main():
    """
Here's how a global function can access dictionaries of used and unused
(defaulted) keyword arguments together with their values, per-call.
This function `f` has no **kwargs:

    >>> @used_unused_keywords()
    ... def f(x=1, y=2, z=3):
    ...     print("f, used keywords: ", f.get_used_keywords())
    ...     print("f, unused keywords: ", f.get_unused_keywords())
    >>> f(x=101, z=2003)
    f, used keywords:  OrderedDict([('x', 101), ('z', 2003)])
    f, unused keywords:  OrderedDict([('y', 2)])

    >>> f(z='a string')
    f, used keywords:  OrderedDict([('z', 'a string')])
    f, unused keywords:  OrderedDict([('x', 1), ('y', 2)])

    >>> f()
    f, used keywords:  OrderedDict()
    f, unused keywords:  OrderedDict([('x', 1), ('y', 2), ('z', 3)])

In the next example, `g` does have **kwargs, so it can be passed any
old keyword argument and value; however, only explicit keyword parameters
occur in the used and unused dictionaries. Each call to `g` below
passes `extra_kwd` with a value, but as this parameter isn't an explicit
keyword parameter of `g`, it doesn't show up in either the "used" or the
"unused" dictionary:

    >>> @used_unused_keywords()
    ... def g(x=1, y=2, z=3, **kwargs):
    ...     print("g, used keywords: ", g.get_used_keywords())
    ...     print("g, unused keywords: ", g.get_unused_keywords())
    >>> g(x=101, z=2003, extra_kwd='wtf')
    g, used keywords:  OrderedDict([('x', 101), ('z', 2003)])
    g, unused keywords:  OrderedDict([('y', 2)])

    >>> g(z='a string', extra_kwd='wtf')
    g, used keywords:  OrderedDict([('z', 'a string')])
    g, unused keywords:  OrderedDict([('x', 1), ('y', 2)])

    >>> g(extra_kwd='wtf')
    g, used keywords:  OrderedDict()
    g, unused keywords:  OrderedDict([('x', 1), ('y', 2), ('z', 3)])

Mandatory keyword-only arguments that have no default value are of course
included in the "used" dictionary:

    >>> @used_unused_keywords()
    ... def t(*, u, v, w, x=1, y=2, z=3, **kwargs):
    ...     print("t, used keywords: ", t.get_used_keywords())
    ...     print("t, unused keywords: ", t.get_unused_keywords())
    >>> t(u='a', v='b', w='c', x=101, z=2003, extra_kwd='wtf')
    t, used keywords:  OrderedDict([('u', 'a'), ('v', 'b'), ('w', 'c'), ('x', 101), ('z', 2003)])
    t, unused keywords:  OrderedDict([('y', 2)])

Here's how a decorated `__init__` instance method accesses the dictionaries:

    >>> class C():
    ...     @used_unused_keywords()
    ...     def __init__(self, x=1, y=2, z=3, **kwargs):
    ...         wrapper = C.__dict__['__init__']
    ...         print("__init__, used keywords: ", wrapper.get_used_keywords())
    ...         print("__init__, unused keywords: ", wrapper.get_unused_keywords())
    >>> c1 = C(x=101, z=2003, extra_kwd='wtf')
    __init__, used keywords:  OrderedDict([('x', 101), ('z', 2003)])
    __init__, unused keywords:  OrderedDict([('y', 2)])

    >>> c2 = C(z='a string', extra_kwd='wtf')
    __init__, used keywords:  OrderedDict([('z', 'a string')])
    __init__, unused keywords:  OrderedDict([('x', 1), ('y', 2)])

    >>> c3 = C(extra_kwd='wtf')
    __init__, used keywords:  OrderedDict()
    __init__, unused keywords:  OrderedDict([('x', 1), ('y', 2), ('z', 3)])

    """
    pass

