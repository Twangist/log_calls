__author__ = "Brian O'Neill"  # BTO
__version__ = 'v0.1.10-b6'
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
import datetime
from collections import namedtuple, OrderedDict     # TODO ordered dict of args & vals useful for history?

from .deco_settings import DecoSetting, DecoSettingsMapping
from .helpers import difference_update, is_keyword_param, get_args_kwargs_param_names
from .proxy_descriptors import KlassInstanceAttrProxy

__all__ = ['log_calls', 'difference_update', '__version__', '__author__']


#------------------------------------------------------------------------------
# log_calls
#------------------------------------------------------------------------------
# TODO: add field(s):
# todo       timestamp (can just use t0 ?? or convert time.time() [sec] to datetime.datetime (sic))
# todo       function name? probably. In fact, prefixed name

CallHistoryRecord = namedtuple(
    "CallHistoryRecord",
    (
        'argnames', 'argvals',
        'varargs',
        'explicit_kwargs', 'defaulted_kwargs', 'implicit_kwargs',
        'retval',
        'elapsed_sec',
        'timestamp',
        'function_name'
    )
)

class log_calls():
    """
    This decorator logs the caller of a decorated function, and optionally
    the arguments passed to that function, before calling it; after calling
    the function, it optionally writes the return value (default: it doesn't),
    and optionally prints a 'closing bracket' message on return (default:
    it does).
    "logs" means: prints to stdout, or, optionally, to a logger.

    The decorator takes various keyword arguments, all with sensible defaults.
    Every parameter except prefix and max_call_history can take two kinds of values,
    direct and indirect. Briefly, if the value of any of those parameters
    is a string that ends in in '=', then it's treated as the name of a keyword
    arg of the wrapped function, and its value when that function is called is
    the final, indirect value of the decorator's parameter (for that call).
    See deco_settings.py docstring for details.

        log_args:          Arguments passed to the (decorated) function will be logged
                           (Default: True)
        log_retval:        Log what the wrapped function returns IFF True/non-false.
                           At most MAXLEN_RETVALS chars are printed. (Default: False)
        args_sep:          str used to separate args. The default is  ', ', which lists
                           all args on the same line. If args_sep ends in a newline '\n',
                           additional spaces are appended to that to make for a neater
                           display. Other separators in which '\n' occurs are left
                           unchanged, and are untested -- experiment/use at your own risk.
        enabled:           If 'truthy', then logging will occur. (Default: True)
        prefix:            str to prefix the function name with when it is used
                           in logged messages: on entry, in reporting return value
                           (if log_retval) and on exit (if log_exit). (Default: '')
        log_exit:          If True (the default), the decorator will log an exiting
                           message after calling the function, and before returning
                           what the function returned.
        logger:            If not None (the default), a Logger which will be used
                           (instead of the print function) to write all messages.
        loglevel:          logging level, if logger != None. (Default: logging.DEBUG)
        record_history:    If truthy, an array of records will be kept, one for each
                           call to the function recording time of call, arguments
                           and defaulted keyword arguments, return value,
                           time elapsed. (Default: False)
        max_history:       An int. value = 0 (default) => don't record history;
                                   value > 0 => store at most value-many records,
                                                oldest records overwritten;
                                   value <=: unboundedly many records
        log_call_number:  If truthy, display number of function call
                           e.g.  f [n] <== <module>   for n-th call. (Default: False)
        log_elapsed:       If truthy, display how long it took the function
                           to execute, in seconds. (Default: False)

    """
    # TODO: keyword parameters for control over stats
    # todo  -- max_call_history: int (keep only the most recent N)
    # todo     TODO implement upper bound!   circular buffer perhaps

    MAXLEN_RETVALS = 60
    LOG_CALLS_SENTINEL_ATTR = '_log_calls_sentinel_'        # name of attr
    LOG_CALLS_SENTINEL_VAR = "_log_calls-deco'd"
    LOG_CALLS_PREFIXED_NAME = 'log_calls-prefixed-name'     # name of attr

    # *** DecoSettingsMapping "API" --
    # (1) initialize: call register_class_settings

    # allow indirection for all except prefix 10/18/14 and max_call_history
    _setting_info_list = (
        DecoSetting('enabled',          int,            False,         allow_falsy=True,  allow_indirect=True),
        DecoSetting('log_args',         bool,           True,          allow_falsy=True,  allow_indirect=True),
        DecoSetting('log_retval',       bool,           False,         allow_falsy=True,  allow_indirect=True),
        DecoSetting('log_exit',         bool,           True,          allow_falsy=True,  allow_indirect=True),
        DecoSetting('args_sep',         str,            ', ',          allow_falsy=False, allow_indirect=True),
        DecoSetting('prefix',           str,            '',            allow_falsy=True,  allow_indirect=False),
        DecoSetting('logger',           logging.Logger, None,          allow_falsy=True,  allow_indirect=True),
        DecoSetting('loglevel',         int,            logging.DEBUG, allow_falsy=False, allow_indirect=True),
        # disallow indirect values, otherwise we have to make a descriptor etc etc
        # and reset/rejigger many things whenever this changes!!! So let's not.
        # value 0: don't record history; value > 0: store at most value records; value < 0 (-1): unbounded

        DecoSetting('record_history',   bool,           0,             allow_falsy=True, allow_indirect=True),
        DecoSetting('max_history',      int,            0,             allow_falsy=True, allow_indirect=False, mutable=False),
        DecoSetting('log_call_number',  bool,           False,         allow_falsy=True, allow_indirect=True),
        DecoSetting('log_elapsed',      bool,           False,         allow_falsy=True, allow_indirect=True),

        # TODO should we also track total calls not just logged?
        # todo  then what do we display, f [n/m] <== <module>   ????
        # TODO If so, then we need two maybe three properties/descriptors: num_calls, num_logged_calls
    )
    DecoSettingsMapping.register_class_settings('log_calls',
                                                _setting_info_list)

    _descriptor_names = ('num_calls', 'call_history', 'total_elapsed')

    @classmethod
    def get_descriptor_names(cls):
        """Called by KlassInstanceAttrProxy when creating descriptors
        that correspond to the attrs of this class named in the returned list.
        KlassInstanceAttrProxy creates descriptors *once*.
        This enforces the rule that the descriptor names / attrs
        are the same for all (deco) instances, i.e. that they 're class-level."""
        return cls._descriptor_names

    # A few generic properties, internal logging, and exposed
    # as descriptors on the stats (KlassInstanceAttrProxy) obj
    @property
    def num_calls(self):
        return self._num_calls

    @property
    def call_history(self):
        return self._call_history

    @property
    def total_elapsed(self):
        return sum((histrec.elapsed_sec for histrec in self._call_history))

    # TODO : Add more properties in this vein?
    # todo  E.g. call_history_as_csv

    def _add_to_history(self, f,
                        argnames, argvals,
                        varargs,
                        explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                        retval=None,
                        elapsed_sec=0,
                        timestamp_secs=0,
                        function_name=''
    ):
        "Only called for *logged* calls"
        self._num_calls += 1

        record_history = self._settings_mapping.get_final_value(
                                'record_history',
                                explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                                fparams=None
        )
        if record_history:
            # Convert timestamp_secs to datetime
            timestamp = datetime.datetime.fromtimestamp(timestamp_secs).\
                strftime('%Y-%m-%d %I:%M:%S %p')

            # TODO: Use self.max_history if > 0
            # todo  Need some kinda object with an insert method that always succeeds
            # todo  and which can be converted to a list exposed by property call_history
            self._call_history.append(
                    CallHistoryRecord(
                        argnames, argvals,
                        varargs,
                        explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                        retval,
                        elapsed_sec,
                        timestamp,
                        function_name)
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
            record_history=False,
            max_history=0,
            log_call_number=False,
            log_elapsed=False
    ):
        """(See class docstring)"""
        # Set up pseudo-dict
        #
        # *** DecoSettingsMapping "API" --
        # (2) construct DecoSettingsMapping object
        #     that will provide mapping & attribute access to settings, & more
        self._settings_mapping = DecoSettingsMapping(
            deco_class=self.__class__,
            # the rest are what DecoSettingsMapping calls **values_dict
            enabled=enabled,
            log_args=log_args,
            log_retval=log_retval,
            log_exit=log_exit,
            args_sep=args_sep,
            prefix=prefix,
            logger=logger,
            loglevel=loglevel,
            record_history=record_history,
            max_history=max_history,
            log_call_number=log_call_number,
            log_elapsed=log_elapsed
        )
        # and the special cases:
        self.prefix = prefix
        self.max_history = max_history  # > 0 --> size of 'buffer'; <= 0 --> unbounded TODO! implement
        # Accessed by descriptors on the __Mapping obj
        self._num_calls = 0
        self._call_history = []

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

            # inner/local fn -- save a few cycles and character -
            # we call this a lot (<= 9x).
            def _get_final_value(setting_name):
                "Use outer scope's kwargs and self.f_params"
                return self._settings_mapping.get_final_value(
                    setting_name, kwargs, fparams=self.f_params)

            # if nothing to do, hurry up & don't do it
            if not _get_final_value('enabled'):
                ### # call f after adding to stats, return its retval
                ### self._add_to_history(f, args, kwargs, logged=False)
                return f(*args, **kwargs)

            logger = _get_final_value('logger')
            loglevel = _get_final_value('loglevel')
            # Establish logging function
            logging_fn = partial(logger.log, loglevel) if logger else print

            # Get list of callers up to & including first log_call's-deco'd fn
            # (or just caller, if no such fn)
            call_list = self.call_chain_to_next_log_calls_fn()

            # Our unit of indentation
            indent = " " * 4

            log_call_number = _get_final_value('log_call_number')
            call_number_str = ('[%s] ' % (self.num_calls+1)) if log_call_number else ''

            msg = ("%s %s<== called by %s"
                   % (prefixed_fname,
                      call_number_str,
                      ' <== '.join(call_list)))

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
            # skip arg reportage, don't even bother writing "arguments: <none>"
            if self.f_params and _get_final_value('log_args'):

                args_sep = _get_final_value('args_sep')  # != ''

                # ~Kludge / incomplete treatment of seps that contain \n
                end_args_line = ''
                if args_sep[-1] == '\n':
                    args_sep = '\n' + (indent * 2)
                    end_args_line = args_sep

                msg += ('\n' + indent + "arguments: " + end_args_line)

                if varargs:
                    args_vals.append( ("[*]%s" % self.args_name, varargs) )

                args_vals.extend( explicit_kwargs.items() )

                if implicit_kwargs:
                    args_vals.append( ("[**]%s" % self.kwargs_name,  implicit_kwargs) )

                # TODO? -- make this next optional via setting?
                # if implicit_kwargs, then f has a "kwargs"-like parameter;
                # the defaulted kwargs are kw args in self.f_params which
                # are NOT in implicit_kwargs, and their vals are defaults
                # of those parameters. Do implicit first.
                if defaulted_kwargs:
                    args_vals.append( ("(defaults used)",  defaulted_kwargs) )

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
            elapsed_sec = (time.time() - t0)
            self._add_to_history(f, argnames, args[:argcount],
                                 varargs,
                                 explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                                 retval,
                                 elapsed_sec=elapsed_sec,
                                 timestamp_secs=t0,
                                 function_name=prefixed_fname
            )

            # log_retval
            if _get_final_value('log_retval'):
                retval_str = str(retval)
                if len(retval_str) > log_calls.MAXLEN_RETVALS:
                    retval_str = retval_str[:log_calls.MAXLEN_RETVALS] + "..."
                logging_fn(indent + "%s return value: %s"
                           % (prefixed_fname, retval_str))

            # log_elapsed
            if _get_final_value('log_elapsed'):
                logging_fn(indent + "elapsed time: %f [sec]" % elapsed_sec)

            # log_exit
            if _get_final_value('log_exit'):
                logging_fn("%s %s==> returning to %s"
                           % (prefixed_fname,
                              call_number_str,
                              ' ==> '.join(call_list)))
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

        stats = KlassInstanceAttrProxy(klass_instance=self)
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
