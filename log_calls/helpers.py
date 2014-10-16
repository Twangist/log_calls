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
