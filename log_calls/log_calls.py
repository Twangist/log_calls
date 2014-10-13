__author__ = 'brianoneill'  # BTO
__version__ = 'v0.1.10-b1'

"""Decorator that eliminates boilerplate code for debugging by writing
caller name(s) and args+values to stdout or, optionally, to a logger.
NOTE: CPython only -- this uses internals of stack frames
      which may well differ in other interpreters.

Argument logging is based on the Python 2 decorator:
    https://wiki.python.org/moin/PythonDecoratorLibrary#Easy_Dump_of_Function_Arguments
with changes for Py3 and several enhancements, as described in doc/log_calls.md.
"""

import inspect
from functools import wraps, partial
import logging
import sys

#__all__ = ['log_calls', 'difference_update']


class log_calls():
    """
    This decorator logs the caller of a decorated function,
    and optionally the arguments passed to that function,
    before calling it; after calling the function, it optionally
    writes the return value (default: it doesn't), and optionally
    prints a 'closing bracket' message (default: it does).
    "logs" means: prints to stdout, or, optionally, to a logger.

    The decorator takes various keyword arguments, all with sensible defaults:
        log_args:     arguments passed to the (decorated) function will be logged
                      (Default: True)
        log_retval:   log what the wrapped function returns IFF True/non-false
                      At most MAXLEN_RETVALS chars are printed. (Default: False)
        args_sep:     str used to separate args. The default is  ', ', which lists
                      all args on the same line. If args_sep='\n' is used, then
                      additional spaces are appended to that to make for a neater
                      display. Other separators in which '\n' occurs are left
                      unchanged, and are untested -- experiment/use at your own risk.
        args_sep_kwd: a str giving the name of a keyword arg of the wrapped
                      function, whose value determines the args_sep to use.
                      Takes precedence over args_sep if given. (Default: '')
        enabled:      if 'truthy', then logging will occur. (Default: True)
        enabled_kwd:  a str giving the name of a keyword arg of the wrapped
                      function, whose value determines whether messages are
                      written (truthy <==> they are written). Takes precedence
                      over 'enabled' if given. (Default: '')
                      See the examples/doctests for the precise rules.
        prefix:       str to prefix the function name with when it is used
                      in logged messages: on entry, in reporting return value
                      (if log_retval) and on exit (if log_exit). (Default: '')
        log_exit:     If True (the default), the decorator will log an exiting
                      message after calling the function, and before returning
                      what the function returned.
        logger:       If not None (the default), a Logger which will be used
                      to write all messages. Otherwise, print is used.
        logger_kwd:   a str giving the name of a keyword arg of the wrapped
                      function, and then logger is the value of that arg passed
                      to the function, IF that is a Logger.
                      Takes precedence over logger if given. (Default: '')
        loglevel:     logging level, if logger != None. (Default: logging.DEBUG)
    """
    MAXLEN_RETVALS = 60
    LOG_CALLS_SENTINEL_ATTR = '_log_calls_sentinel_'        # name of attr
    LOG_CALLS_SENTINEL_VAR = "_log_calls-deco'd"
    LOG_CALLS_PREFIXED_NAME = 'log_calls-prefixed-name'     # name of attr

    def __init__(
            self,
            log_args=True,
            log_retval=False,
            args_sep=', ', args_sep_kwd='',
            enabled=True, enabled_kwd='',
            prefix='',
            log_exit=True,
            logger=None, logger_kwd='',
            loglevel=logging.DEBUG,
    ):
        """(See class docstring)"""
        self.log_args = log_args
        self.log_retval = not not log_retval
        self.args_sep = args_sep
        self.args_sep_kwd = args_sep_kwd
        self.enabled = not enabled_kwd and enabled  # == enabled, if not enabled_kwd
        self.enabled_kwd = enabled_kwd
        self.prefix = prefix
        self.log_exit = log_exit
        self.logger = logger
        self.logger_kwd = logger_kwd
        self.loglevel = loglevel


    def __call__(self, f):
        """Because there are decorator arguments, __call__() is called
        only once, and it can take only a single argument: the function
        to decorate. The return value of __call__ is called subsequently.
        So, this method *returns* the decorator proper."""
        # First, save prefix + function name for function f
        prefixed_fname = self.prefix + f.__name__

        @wraps(f)
        def f_log_calls_wrapper_(*args, **kwargs):

            fparams = inspect.signature(f).parameters

            # Establish "do_it" - 'enabled'
            do_it = self.enabled
            if self.enabled_kwd:
                if self.enabled_kwd in kwargs:  # passed to f
                    do_it = kwargs[self.enabled_kwd]
                else:   # not passed; is it an explicit kwd of f?
                    if is_keyword_param(fparams.get(self.enabled_kwd)):
                        # yes, explicit param of wrapped f; use f's default value
                        do_it = fparams[self.enabled_kwd].default
                    else:
                        do_it = False

            # if nothing to do, hurry up & don't do it
            if not do_it:
                return f(*args, **kwargs)

            # Establish logging function
            logging_fn = print       # partial(print, end='')
            logger = None
            if (self.logger_kwd
                and self.logger_kwd in kwargs
                and isinstance(kwargs[self.logger_kwd], logging.Logger)):
                logger = kwargs[self.logger_kwd]
            elif self.logger and isinstance(self.logger, logging.Logger):
                logger = self.logger
            if logger:
                logging_fn = partial(logger.log, self.loglevel)

            # Get list of callers up to & including first log_call's-deco'd fn
            # (or just caller, if no such fn)
            call_list = self.call_chain_to_next_log_calls_fn()

            msg = ("%s <== called by %s"
                   % (prefixed_fname, ' <== '.join(call_list)))
            # Make & append args message
            indent = " " * 4

            # If function has no parameters, skip arg reportage,
            # don't even bother writing "args: <none>"
            if self.log_args and fparams:
                argcount = f.__code__.co_argcount
                argnames = f.__code__.co_varnames[:argcount]

                # Establish sep, arguments separator
                if (self.args_sep_kwd
                    and self.args_sep_kwd in kwargs
                    and isinstance(kwargs[self.args_sep_kwd], str)
                    and kwargs[self.args_sep_kwd]):
                    sep = kwargs[self.args_sep_kwd]
                else:
                    sep = self.args_sep

                # ~Kludge / incomplete treatment of seps that contain \n
                end_args_line = ''
                if sep == '\n':
                    sep = '\n' + (indent * 2)
                    end_args_line = sep

                msg += ('\n' + indent + "args: " + end_args_line)

                args_vals = list(zip(argnames, args))
                if args[argcount:]:
                    args_vals.append( ("[*]args", args[argcount:]) )

                explicit_kwargs = {k: v for (k, v) in kwargs.items()
                                   if k in fparams
                                   and is_keyword_param(fparams[k])}
                args_vals.extend( explicit_kwargs.items() )

                implicit_kwargs = difference_update(
                    kwargs.copy(), explicit_kwargs)
                if implicit_kwargs:
                    args_vals.append( ("[**]kwargs",  implicit_kwargs) )

                if args_vals:
                    msg += sep.join('%s=%r' % pair for pair in args_vals)
                else:
                    msg += "<none>"

            logging_fn(msg)

            retval = f(*args, **kwargs)

            if self.log_retval:
                retval_str = str(retval)
                if len(retval_str) > log_calls.MAXLEN_RETVALS:
                    retval_str = retval_str[:log_calls.MAXLEN_RETVALS] + "..."
                logging_fn(indent + "%s return value: %s"
                           % (prefixed_fname, retval_str))

            if self.log_exit:
                logging_fn("%s ==> returning to %s"
                           % (prefixed_fname, ' ==> '.join(call_list)))
            return retval

        # Add a sentinel as a property to f_log_calls_wrapper_
        # so we can in theory chase back to any previous log_calls-decorated fn
        setattr(
            f_log_calls_wrapper_,
            self.LOG_CALLS_SENTINEL_ATTR,
            self.LOG_CALLS_SENTINEL_VAR
        )
        setattr(
            f,
            self.LOG_CALLS_PREFIXED_NAME,
            prefixed_fname
        )

        return f_log_calls_wrapper_

    @staticmethod
    def call_chain_to_next_log_calls_fn():
        """Return list of callers (names) on the call chain
        from caller of caller to first log_calls-deco'd function inclusive,
        if any.  If there's no log_calls-deco'd function on the stack,
        or anyway if none are discernible, return [caller_of_caller]."""
        curr_frame = sys._getframe(2)   # caller-of-caller's frame
        found = False
        call_list = []
        while curr_frame:
            curr_funcname = curr_frame.f_code.co_name
            if curr_funcname == 'f_log_calls_wrapper_':
                # Previous was decorated inner fn; don't add 'f_log_calls_wrapper_'
                # print("**** found f_log_calls_wrapper_, prev fn name =", call_list[-1])     # <<<DEBUG>>>
                # Fixup: get prefixed named of wrapped function
                call_list[-1] = getattr(curr_frame.f_locals['f'],
                                        log_calls.LOG_CALLS_PREFIXED_NAME)
                found = True
                break
            call_list.append(curr_funcname)
            if curr_funcname == '<module>':
                break

            globs = curr_frame.f_back.f_globals
            curr_fn = None
            if curr_funcname in globs:
                curr_fn = globs[curr_funcname]
            # If curr_funcname is a decorated inner function,
            # then it's not in globs. If it's called from outside
            # it's enclosing function, it's caller is 'f_log_calls_wrapper_'
            # so we'll see that on next iteration.
            else:
                try:
                    # if it's a decorated inner function that's called
                    # by its enclosing function, detect that:
                    locls = curr_frame.f_back.f_back.f_locals
                    if curr_funcname in locls:
                        curr_fn = locls[curr_funcname]
                        #   print("**** %s found in locls = curr_frame.f_back.f_back.f_locals, "
                        #         "curr_frame.f_back.f_back.f_code.co_name = %s"
                        #         % (curr_funcname, curr_frame.f_back.f_back.f_locals)) # <<<DEBUG>>>
                except AttributeError:
                    # print("**** %s not found (inner fn?)" % curr_funcname)       # <<<DEBUG>>>
                    pass

            if hasattr(curr_fn, log_calls.LOG_CALLS_SENTINEL_ATTR):
                found = True
                break
            curr_frame = curr_frame.f_back

        # So:
        # If found, then call_list[-1] is log_calls-wrapped;
        # if not found, truncate call_list to first element.
        if not found:
            call_list = call_list[:1]

        return call_list


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# helpers
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_keyword_param(param):
    return param and (
        param.kind == param.KEYWORD_ONLY
        or
        ((param.kind == param.POSITIONAL_OR_KEYWORD)
         and param.default is not param.empty)
    )


def difference_update(d, d_remove):
    """Change and return d.
    d: mutable mapping, d_remove: iterable.
    There is such a method for sets, but unfortunately not for dicts."""
    for k in d_remove:
        if k in d:
            del(d[k])
    return d    # so that we can pass a call to this fn as an arg, or chain
