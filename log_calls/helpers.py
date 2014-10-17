__author__ = 'brianoneill'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# helper function(s)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def difference_update(d, d_remove):
    """Change and return d.
    d: mutable mapping, d_remove: iterable.
    There is such a method for sets, but unfortunately not for dicts."""
    for k in d_remove:
        if k in d:
            del(d[k])
    return d    # so that we can pass a call to this fn as an arg, or chain


def is_keyword_param(param):
    return param and (
        param.kind == param.KEYWORD_ONLY
        or
        ((param.kind == param.POSITIONAL_OR_KEYWORD)
         and param.default is not param.empty)
    )


def get_args_kwargs_param_names(fparams) -> (str, str):
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


