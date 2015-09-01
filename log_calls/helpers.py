__author__ = 'brianoneill'

__all__ = [
    'difference_update',
    'is_keyword_param',
    'get_args_pos',
    'get_args_kwargs_param_names',
    'get_defaulted_kwargs_OD',
    'get_explicit_kwargs_OD',
    'dict_to_sorted_str',
    'is_quoted_str',
]

from collections import OrderedDict
import inspect


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# helper function(s)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def no_duplicates(seq):
    """Generator that removes duplicates from seq (preserving order).
    Without order preservation, it would suffice to return list(set(seq)).
    seq is an iterable.
    >>> list(no_duplicates([1, 2, 3, 3, 2, 0, 1]))
    [1, 2, 3, 0]
    >>> tuple(no_duplicates([1, 2, 3, 4]))
    (1, 2, 3, 4)
    >>> ''.join(no_duplicates('ababcabcd...xyz'))
    'abcd.xyz'
    """
    seen = set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            yield(x)
    return

def restrict_keys(d: dict, domain) -> dict:
    """Remove from d all items whose key is not in domain; return d.
    >>> d = {'a': 1, 'b': 2}
    >>> dr = restrict_keys(d, {'a', 'c'})
    >>> dr
    {'a': 1}
    >>> d == dr
    True
    """
    for k in set(d):
        if k not in domain: del d[k]
    return d

def difference_update(d: dict, remove) -> dict:
    """Change and return d.
    d: mutable mapping, remove: iterable.
    There is such a method for sets, but unfortunately not for dicts.

    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> remove = ('b', 'outlier')
    >>> d_altered = difference_update(d, remove)
    >>> d_altered is d
    True
    >>> d == {'a': 1, 'c': 3}
    True
    """
    for k in remove:
        if k in d:
            del(d[k])
    return d    # so that we can pass a call to this fn as an arg, or chain


def prefix_multiline_str(prefix: str, multiline_str: str):
    """
    :param prefix: string with which to prefix each line of multiline_str
    :param multiline_str: a possibly multiline string
    :return: prefix + (multiline_str with each \n replaced by \n + prefix)
    >>> prefix_multiline_str("abc: ", None)     # expect no output
    >>> prefix_multiline_str("abc: ", "")
    'abc: '
    >>> prefix_multiline_str("abc: ", "xyz")
    'abc: xyz'
    >>> print(prefix_multiline_str("abc: ", "x\\ny\\nz"))
    abc: x
    abc: y
    abc: z
    """
    if multiline_str is None:
        return None
    if '\n' not in multiline_str:
        return prefix + multiline_str
    return prefix + multiline_str.replace('\n', '\n' + prefix)


def is_keyword_param(param):
    """param is a parameter (a value) from the ordered dict
        inspect.signature(f).parameters
    for some function f.
    Return bool: True iff
        param is not None
        and
            if it's a keyword-only parameter (possibly with no default value!),
            or
            if it's a positional-or-keyword param with a default value

    Doctests:
    >>> is_keyword_param(None) == False
    True

    >>> import inspect
    >>> get_fparams = lambda f: inspect.signature(f).parameters
    >>> def f(): pass
    >>> is_keyword_param(get_fparams(f).get('anything')) == False
    True
    >>> def f(*args): pass
    >>> is_keyword_param(get_fparams(f)['args']) == False
    True

    >>> def f(a, b, *filters, **kwargs): pass
    >>> is_keyword_param(get_fparams(f)['a']) == is_keyword_param(get_fparams(f)['b']) == False
    True
    >>> is_keyword_param(get_fparams(f)['filters']) == is_keyword_param(get_fparams(f)['kwargs']) == False
    True

    >>> def f(x, y, z, *, mandatory, user='Joe', **other_users): pass
    >>> is_keyword_param(get_fparams(f)['mandatory']) == True
    True
    >>> is_keyword_param(get_fparams(f)['user']) == True
    True
    """
    return not not param and (
        param.kind == param.KEYWORD_ONLY
        or
        ((param.kind == param.POSITIONAL_OR_KEYWORD)
         and param.default is not param.empty)
    )


def get_args_pos(fparams) -> int:
    """Position in params of function of varargs, >= 0 if it's present, else -1.
    fparams is inspect.signature(f).parameters
        for some function f.

    Doctests:
    >>> import inspect
    >>> def f(a, b, c, x=8, **kwargs): pass
    >>> get_args_pos(inspect.signature(f).parameters)
    -1
    >>> def ff(a, b, *other_args, **kwargs): pass
    >>> get_args_pos(inspect.signature(ff).parameters)
    2
    >>> def fff(*args): pass
    >>> get_args_pos(inspect.signature(fff).parameters)
    0
    """
    for i, name in enumerate(fparams):
        param = fparams[name]
        if param.kind == param.VAR_POSITIONAL:
            return i
    return -1


def get_args_kwargs_param_names(fparams) -> (str, str):
    """fparams is inspect.signature(f).parameters
    for some function f.

    Doctests:
    >>> import inspect
    >>> def f(): pass
    >>> get_args_kwargs_param_names(inspect.signature(f).parameters)
    (None, None)
    >>> def f(*args): pass
    >>> get_args_kwargs_param_names(inspect.signature(f).parameters)
    ('args', None)
    >>> def f(a, b, *filters, **kwargs): pass
    >>> get_args_kwargs_param_names(inspect.signature(f).parameters)
    ('filters', 'kwargs')
    >>> def f(x, y, z, user='Joe', **other_users): pass
    >>> get_args_kwargs_param_names(inspect.signature(f).parameters)
    (None, 'other_users')
    """
    args_name = None
    kwargs_name = None
    for name in fparams:
        param = fparams[name]
        if param.kind == param.VAR_KEYWORD:
            kwargs_name = name
        elif param.kind == param.VAR_POSITIONAL:
            args_name = name
        if args_name and kwargs_name:
            break   # found both: done
    return args_name, kwargs_name


def get_defaulted_kwargs_OD(f_params, bound_args) -> OrderedDict:
    """For some call to a function f, args *arg and **kwargs,
    :param f_params:   inspect.signature(f).parameters
    :param bound_args: inspect.signature(f).bind(*args, **kwargs)

    :return: OrderedDict of the (param.name, param.default)
             for keyword parameters param of f that are NOT explicitly passed.

    An ad-hoc little function, but needed in 2 different places.

    TODO (doc)tests?
    """
    arguments = bound_args.arguments
    empty = inspect._empty
    return OrderedDict(
        # ((param.name, param.default)
        #  for param in f_params.values()
        #  if param.name not in arguments
        #     and param.default != empty)
        ((key, f_params[key].default)
        for key in f_params
        if key not in arguments
            and f_params[key].default != empty)
    )


def get_explicit_kwargs_OD(f_params, bound_args, kwargs) -> OrderedDict:
    """For some call to a function f, args *arg and **kwargs,
    :param f_params:   inspect.signature(f).parameters
    :param bound_args: inspect.signature(f).bind(*args, **kwargs)

    :return: OrderedDict of the (kwd, kwargs[kwd])
             for keyword parameters kwd of f that ARE explicitly passed.

    Another ad-hoc little function, needed in 2 different places.

    TODO (doc)tests?
    """
    arguments = bound_args.arguments
    return OrderedDict(
        ((k, kwargs[k])
         for k in f_params
         if k in arguments and k in kwargs)
    )


def dict_to_sorted_str(d):
    """Return a str representation of dict d where keys are in ascending order.
    >>> d = {'c': 3, 'a': 1, 'b': 2}
    >>> print(dict_to_sorted_str(d))
    {'a': 1, 'b': 2, 'c': 3}
    >>> d2 = {'Z': 'zebulon', 'X': 'alphanumeric', 'Y': 'yomomma'}
    >>> print(dict_to_sorted_str(d2))
    {'X': 'alphanumeric', 'Y': 'yomomma', 'Z': 'zebulon'}
    """
    lst = list(d.items())
    lst.sort(key=lambda p: p[0])
    ret = ('{' +
           ', '.join(["%s: %s" % (repr(k), repr(v)) for (k, v) in lst ]) +
           '}')
    return ret


def is_quoted_str(s):
    """
    >>> is_quoted_str('')
    False
    >>> is_quoted_str('"')
    False
    >>> is_quoted_str('Hi')
    False
    >>> is_quoted_str('"Hi\\'')
    False
    >>> is_quoted_str('"Hi"')
    True
    >>> is_quoted_str("''")
    True
    >>> any( map(is_quoted_str, [0, tuple(), list()]))
    False
    """
    QUOTES = {"'", '"'}
    return isinstance(s, str) and len(s) >= 2 and s[0] == s[-1] and s[0] in QUOTES


# match using match_fn(x, pattern).
def any_match(match_fn, seq, patterns):
    """match_fn(s, pat) -> bool
    seq, patterns: iterables, generators.

    Equality:
    >>> any_match(lambda x, y: x == y, (1, 2, 3), (5, 6, 1))
    True
    >>> any_match(lambda x, y: x == y, (1, 2, 3), (5, 6))
    False

    fnmatch.fnmatchcase (fnmatch.fnmatchcase is case-sensitive)
    >>> import fnmatch
    >>> names = (s for s in ('pair', 'P.pair', 'pair.getter', 'P.pair.getter'))
    >>> patterns = ('pair', )
    >>> any_match(fnmatch.fnmatchcase, names, patterns)
    True
    >>> any_match(fnmatch.fnmatchcase, names, patterns) # names is now 'spent', list(names) is empty
    False

    Regexp
    >>> import re
    >>> patterns = (r'a.*b', r'[0-9]{2,2}[a-z]')
    >>> matcher = lambda s, pat: re.match(pat, s)
    >>> any_match(matcher, ('aaaa', 'bbb', '0q'), patterns)
    False
    >>> any_match(matcher, ('aaaab',), patterns)
    True
    >>> any_match(matcher, ('aa', '23z'), patterns)
    True
    """
    return any(
        match_fn(s, pat)
        for s in seq
        for pat in patterns
    )

#############################################################################

if __name__ == "__main__":


    import doctest
    doctest.testmod()
