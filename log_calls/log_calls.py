__author__ = "Brian O'Neill"  # BTO
__version__ = 'v0.1.10-b5'
__doc__ = """
Decorator that eliminates boilerplate code for debugging by writing
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
import time
from collections import namedtuple, OrderedDict     # TODO ordered dict of args & vals useful for history?

from .deco_settings import DecoSetting, DecoSettingsMapping
from .helpers import difference_update, is_keyword_param, get_args_kwargs_param_names

__all__ = ['log_calls', 'difference_update', '__version__', '__author__']


CallHistoryRecord = namedtuple(
    "CallHistoryRecord",
    (
        'argnames', 'argvals',
        'varargs',
        'explicit_kwargs', 'defaulted_kwargs', 'implicit_kwargs',
        'retval',
        'elapsed_ms'
    )
)


#------------------------------------------------------------------------------
# log_calls
#------------------------------------------------------------------------------
class log_calls():
    """
    This decorator logs the caller of a decorated function, and optionally
    the arguments passed to that function, before calling it; after calling
    the function, it optionally writes the return value (default: it doesn't),
    and optionally prints a 'closing bracket' message (default: it does).
    "logs" means: prints to stdout, or, optionally, to a logger.

    The decorator takes various keyword arguments, all with sensible defaults.
    Every parameter except prefix can take two kinds of values, direct and
    indirect. Briefly, if the value of any of these parameters (other than prefix)
    is a string that ends in in '=', then it's treated as the name of a keyword
    arg of the wrapped function, and its value when that function is called is
    the final, indirect value of the decorator's parameter (for that call).
    See deco_settings.py docstring for details.

        log_args:     Arguments passed to the (decorated) function will be logged
                      (Default: True)
        log_retval:   Log what the wrapped function returns IFF True/non-false.
                      At most MAXLEN_RETVALS chars are printed. (Default: False)
        args_sep:     str used to separate args. The default is  ', ', which lists
                      all args on the same line. If args_sep ends in a newline '\n',
                      additional spaces are appended to that to make for a neater
                      display. Other separators in which '\n' occurs are left
                      unchanged, and are untested -- experiment/use at your own risk.
        enabled:      If 'truthy', then logging will occur. (Default: True)
        prefix:       str to prefix the function name with when it is used
                      in logged messages: on entry, in reporting return value
                      (if log_retval) and on exit (if log_exit). (Default: '')
        log_exit:     If True (the default), the decorator will log an exiting
                      message after calling the function, and before returning
                      what the function returned.
        logger:       If not None (the default), a Logger which will be used
                      (instead of the print function) to write all messages.
        loglevel:     logging level, if logger != None. (Default: logging.DEBUG)
    """
    MAXLEN_RETVALS = 60
    LOG_CALLS_SENTINEL_ATTR = '_log_calls_sentinel_'        # name of attr
    LOG_CALLS_SENTINEL_VAR = "_log_calls-deco'd"
    LOG_CALLS_PREFIXED_NAME = 'log_calls-prefixed-name'     # name of attr

    # *** DecoSettingsMapping "API" --
    # (1) initialize: call register_class_settings

    # allow indirection for all except prefix
    _setting_info_list = (
        DecoSetting('enabled',    int,            False,         allow_falsy=True,  allow_indirect=True),
        DecoSetting('log_args',   bool,           True,          allow_falsy=True,  allow_indirect=True),
        DecoSetting('log_retval', bool,           False,         allow_falsy=True,  allow_indirect=True),
        DecoSetting('log_exit',   bool,           True,          allow_falsy=True,  allow_indirect=True),
        DecoSetting('args_sep',   str,            ', ',          allow_falsy=False, allow_indirect=True),
        DecoSetting('prefix',     str,            '',            allow_falsy=True,  allow_indirect=False),
        DecoSetting('logger',     logging.Logger, None,          allow_falsy=True,  allow_indirect=True),
        DecoSetting('loglevel',   int,            logging.DEBUG, allow_falsy=False, allow_indirect=True)
    )
    _descriptor_names = ('num_calls', 'call_history', 'total_elapsed')

    DecoSettingsMapping.register_class_settings('log_calls',
                                                _setting_info_list)
    # pass not jst 'log_calls', but the actual class

    # 'virtual' method, called by __init__
    @classmethod
    def make_deco_descriptor(cls, descr_name):
        """E.g. descr_name will be 'num_calls" or etc."""
        class DecoDescr():
            def __get__(self_, stats_dummyObj, owner):
                "instance: a function returned by __call__"
                ### print("**** descriptor %s __get__ called" % descr_name)
                return getattr(stats_dummyObj.deco_instance, descr_name)    # '_' + descr_name

            def __set__(self_, stats_dummyObj, value):
                # THese properties are r/o so trying to set the vals should raise an exception
                # TODO test!
                #setattr(instance, '_' + descr_name, value)
                raise AttributeError("%s is r/o" % descr_name)

        return DecoDescr()

    # A few generic properties, internal logging, and exposed
    # as descriptors on the __Mapping obj
    @property
    def num_calls(self):
        return len(self._call_history)

    @property
    def call_history(self):
        return self._call_history

    @property
    def total_elapsed(self):
        return sum((histrec.elapsed_ms for histrec in self._call_history))

    def _add_to_history(self, f,
                        argnames, argvals,
                        varargs,
                        explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                        retval=None,
                        elapsed_ms=0):
        # uses self.f_params
        self._call_history.append(
                CallHistoryRecord(
                    argnames, argvals,
                    varargs,
                    explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                    retval,
                    elapsed_ms)
        )

    def __init__(
            self,
            enabled=True,
            log_args=True,
            log_retval=False,
            log_exit=True,
            args_sep=', ',
            prefix='',
            logger=None,
            loglevel=logging.DEBUG,
    ):
        """(See class docstring)"""
        # Set up pseudo-dict
        #
        # *** DecoSettingsMapping "API" --
        # (2) construct DecoSettingsMapping object
        #     that will provide mapping & attribute access to settings, & more
        self._settings_mapping = DecoSettingsMapping(
            deco_class=self.__class__,
            # and the rest are what DecoSettingsMapping calls **values_dict
            enabled=enabled,
            log_args=log_args,
            log_retval=log_retval,
            log_exit=log_exit,
            args_sep=args_sep,
            prefix=prefix,
            logger=logger,
            loglevel=loglevel,
        )
        # and the special case:
        self.prefix = prefix

        # Accessed by descriptors on the __Mapping obj
        self._call_history = []
#        self._num_calls = 0

        self.f_params = None    # set properly by __call__

    def __call__(self, f):
        """Because there are decorator arguments, __call__() is called
        only once, and it can take only a single argument: the function
        to decorate. The return value of __call__ is called subsequently.
        So, this method *returns* the decorator proper."""
        # First, save prefix + function name for function f
        prefixed_fname = self.prefix + f.__name__
        self.f_params = inspect.signature(f).parameters
        (self.args_name,
         self.kwargs_name) = get_args_kwargs_param_names(self.f_params)

        @wraps(f)
        def f_log_calls_wrapper_(*args, **kwargs):
            """Wrapper around the wrapped function f.
            When this runs, f has been called, so we can now resolve
            any indirect values for the settings/keyword-params
            of log_calls, using info in kwargs and self.f_params."""
            # *** Part of the DecoSettingsMapping "API" --
            #     (4) using self._settings_mapping.get_final_value in wrapper
            # [[[ This/these is/are 4th chronologically ]]]

            # save a few cycles - we call this a lot (<= 7x). Method 'pointer'
            _get_final_value = self._settings_mapping.get_final_value

            # if nothing to do, hurry up & don't do it
            # TODO: make a version of _get_final_value (sic?) in THIS class
            # todo  which uses self.f_params (don't pass). Maybe part of it is a gen'l fn needed by _add_to_history
            if not _get_final_value('enabled', self.f_params, kwargs):
                ### # call f after adding to stats, return its retval
                ### self._add_to_history(f, args, kwargs, logged=False)     # uses self.f_params
                return f(*args, **kwargs)

            logger = _get_final_value('logger', self.f_params, kwargs)
            loglevel = _get_final_value('loglevel', self.f_params, kwargs)
            # Establish logging function
            logging_fn = partial(logger.log, loglevel) if logger else print

            # Get list of callers up to & including first log_call's-deco'd fn
            # (or just caller, if no such fn)
            call_list = self.call_chain_to_next_log_calls_fn()

            # Our unit of indentation
            indent = " " * 4

            msg = ("%s <== called by %s"
                   % (prefixed_fname, ' <== '.join(call_list)))

            # Gather all the things we need for _add_history (sic)
            argcount = f.__code__.co_argcount
            argnames = f.__code__.co_varnames[:argcount]
            args_vals = list(zip(argnames, args))
            varargs = args[argcount:]
            explicit_kwargs = {k: v for (k, v) in kwargs.items()
                               if k in self.f_params
                               and is_keyword_param(self.f_params[k])}
            implicit_kwargs = difference_update(
                kwargs.copy(), explicit_kwargs)
            defaulted_kwargs = {
                k: self.f_params[k].default
                for k in self.f_params
                if is_keyword_param(self.f_params[k]) and k not in kwargs
            }

            # Make & append args message
            # If function has no parameters or if not log_args,
            # skip arg reportage, don't even bother writing "args: <none>"
            if self.f_params and _get_final_value('log_args', self.f_params, kwargs):

                args_sep = _get_final_value('args_sep', self.f_params, kwargs)  # != ''

                # ~Kludge / incomplete treatment of seps that contain \n
                end_args_line = ''
                if args_sep[-1] == '\n':
                    args_sep = '\n' + (indent * 2)
                    end_args_line = args_sep

                msg += ('\n' + indent + "args: " + end_args_line)

                if varargs:
                    args_vals.append( ("[*]%s" % self.args_name, varargs) )

                args_vals.extend( explicit_kwargs.items() )

                # TODO NEW -- make this next optional via setting?
                # if implicit_kwargs, then f has a "kwargs"-like parameter;
                # the defaulted kwargs are kw args in self.f_params which
                # are NOT in implicit_kwargs, and their vals are defaults
                # of those parameters
                if defaulted_kwargs:
                    args_vals.append( ("(defaulted kwd args)",  defaulted_kwargs) )

                if implicit_kwargs:
                    args_vals.append( ("[**]%s" % self.kwargs_name,  implicit_kwargs) )

                if args_vals:
                    msg += args_sep.join('%s=%r' % pair for pair in args_vals)
                else:
                    msg += "<none>"

                #### TODO can this all be simplified using
                #### todo inspect.getfullargspec(...)
                #### todo  or inspect... signature... bind ( f, *args, **kwargs) ???

            logging_fn(msg)

            # Call f(*args, **kwargs) and get its retval,
            # then add elapsed time and retval (as str? repr?) etc to stats
            t0 = time.time()
            retval = f(*args, **kwargs)
            self._add_to_history(f, argnames, args[:argcount],
                                 varargs,
                                 explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                                 retval,
                                 elapsed_ms=(time.time() - t0)
            )  # uses self.f_params

            # log_retval
            if _get_final_value('log_retval', self.f_params, kwargs):
                retval_str = str(retval)
                if len(retval_str) > log_calls.MAXLEN_RETVALS:
                    retval_str = retval_str[:log_calls.MAXLEN_RETVALS] + "..."
                logging_fn(indent + "%s return value: %s"
                           % (prefixed_fname, retval_str))

            # log_exit
            if _get_final_value('log_exit', self.f_params, kwargs):
                logging_fn("%s ==> returning to %s"
                           % (prefixed_fname, ' ==> '.join(call_list)))
            return retval

        # Add a sentinel as an attribute to f_log_calls_wrapper_
        # so we can in theory chase back to any previous log_calls-decorated fn
        setattr(
            f_log_calls_wrapper_,
            self.LOG_CALLS_SENTINEL_ATTR,
            self.LOG_CALLS_SENTINEL_VAR
        )
        # Add prefixed name of f as an attribute
        setattr(
            f,      # revert to f, after trying f_log_calls_wrapper_
            self.LOG_CALLS_PREFIXED_NAME,
            prefixed_fname
        )

        class DecoInstanceProxy():
            """attributes on deco_instance ==> descriptors on this obj"""
            first_time = True

            # Note: self = deco class instance from outer scope (__call__)
            def __init__(self_, deco_instance):
                self_.deco_instance = self          # deco_instance == self
                if self_.__class__.first_time:
                    for descr_name in self._descriptor_names:
                        setattr(self_.__class__,
                                descr_name,
                                self.make_deco_descriptor(descr_name))
                self_.__class__.first_time = False
            # TODO : Add methods to THIS class,
            # todo   which maybe we should think of and rename
            # todo   as DecoInstanceStats
            # todo  E.g. call_history_as_csv


        stats = DecoInstanceProxy(self)
        setattr(
            f_log_calls_wrapper_,
            'stats',
            stats
        )

        # *** Part of the DecoSettingsMapping "API" --
        #     (3) exposing the DecoSettingsMapping to 'users'
        #     [[[ 3rd step chronologically ]]]
        #
        # Add an attribute on wrapped function, 'log_call_settings',
        # which provides both mapping and attribute interfaces to settings.
        # Same thing as:
        #     f_log_calls_wrapper_.log_calls_settings = self._settings_mapping
        setattr(
            f_log_calls_wrapper_,
            'log_calls_settings',
            self._settings_mapping
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
                # call_list[-1] = curr_frame.f_locals['prefixed_fname']  # bit of a kludge eh TODO TODO
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
                except AttributeError:  # "never happens"
                    # print("**** %s not found (inner fn?)" % curr_funcname)       # <<<DEBUG>>>
                    pass
                else:
                    if curr_funcname in locls:
                        curr_fn = locls[curr_funcname]
                        #   print("**** %s found in locls = curr_frame.f_back.f_back.f_locals, "
                        #         "curr_frame.f_back.f_back.f_code.co_name = %s"
                        #         % (curr_funcname, curr_frame.f_back.f_back.f_locals)) # <<<DEBUG>>>
                    # # TODO FUCK BUT this doesn't work for methods eh
                    # # No doesn't work for... prefixed fnames!
                    # # todo BECAUSE <<<<< curr_funcname lacks prefix >>>>>
                    # # todo Can we fix?
                    # # WHAT IF WE COULD LOOK UP THE ATTRS OF ANY deco'd fn here,
                    # # we could get its (static) prefix if it has one
                    elif ('prefixed_fname' in locls
                        #  and locls['prefixed_fname'] == curr_funcname   # TODO
                         ):
                        # TODO - why? curr_funcname will 'come around for real' next time through loop,
                        # todo   so remove it from end now
                        call_list = call_list[:-1]
                        # and curr_fn is None, so it won't have attr in next "if"
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
