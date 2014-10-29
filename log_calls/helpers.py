__author__ = 'brianoneill'

__all__ = [
    'difference_update',
    'is_keyword_param',
    'get_args_pos',
    'get_args_kwargs_param_names',
    'dict_to_sorted_str'
]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# helper function(s)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def difference_update(d, d_remove):
    """Change and return d.
    d: mutable mapping, d_remove: iterable.
    There is such a method for sets, but unfortunately not for dicts.

    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> remove = ('b', 'outlier')
    >>> d_altered = difference_update(d, remove)
    >>> d_altered is d
    True
    >>> d == {'a': 1, 'c': 3}
    True
    """
    for k in d_remove:
        if k in d:
            del(d[k])
    return d    # so that we can pass a call to this fn as an arg, or chain


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


def dict_to_sorted_str(d):
    """Return a str representation of dict d where keys are in ascending order.
    >>> d = {'c': 3, 'a': 1, 'b': 2}
    >>> print(dict_to_sorted_str(d))
    {'a': 1, 'b': 2, 'c': 3}
    >>> d2 = {'Z': 'zebulon', 'X': 'alphanumeric', 'Y': 'yomomma'}
    >>> print(dict_to_sorted_str(d2))
    {'X': 'alphanumeric', 'Y': 'yomomma', 'Z': 'zebulon'}
    """
    lst = [(k, v) for (k, v) in d.items()]
    lst.sort(key=lambda p: p[0])
    ret = ('{' +
           ', '.join(["%s: %s" % (repr(k), repr(v)) for (k, v) in lst ]) +
           '}')
    return ret


if __name__ == "__main__":
    import doctest
    doctest.testmod()
