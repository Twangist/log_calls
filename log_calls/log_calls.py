__author__ = "Brian O'Neill"  # BTO
__version__ = '0.1.11'
__doc__ = """
Configurable decorator for debugging and profiling that writes
caller name(s), args+values, function return values, execution time,
number of call, to stdout or to a logger. log_calls can track
call history and provide it in CSV format.
NOTE: CPython only -- this uses internals of stack frames
      which may well differ in other interpreters.
See docs/log_calls.md for details, usage info and examples.

Argument logging is based on the Python 2 decorator:
    https://wiki.python.org/moin/PythonDecoratorLibrary#Easy_Dump_of_Function_Arguments
with changes for Py3 and several enhancements, as described in docs/log_calls.md.
"""
import inspect
from functools import wraps, partial
import logging
import sys
import time
import datetime
from collections import namedtuple, OrderedDict, deque

from .deco_settings import DecoSetting, DecoSettingsMapping
from .helpers import (difference_update, is_keyword_param,
                      get_args_pos, get_args_kwargs_param_names,
                      dict_to_sorted_str)
from .proxy_descriptors import ClassInstanceAttrProxy

__all__ = ['log_calls', 'difference_update', '__version__', '__author__']


#------------------------------------------------------------------------------
# log_calls
#------------------------------------------------------------------------------
# Need 'call_num' in case 'max_history' is set to some N > 0,
# so that only the N most recent records are retained:
# it's easier to identify calls if they're tagged with call #.
CallRecord = namedtuple(
    "CallRecord",
    (
        'call_num',
        'argnames', 'argvals',
        'varargs',
        'explicit_kwargs', 'defaulted_kwargs', 'implicit_kwargs',
        'retval',
        'elapsed_secs',
        'timestamp',
        'prefixed_func_name',
        # caller_chain: list of fn names, the last possibly a "prefixed name".
        # From most-recent (immediate caller) to least-recent if len > 1.
        'caller_chain',
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
    Every parameter except prefix and max_history can take two kinds of values,
    direct and indirect. Briefly, if the value of any of those parameters
    is a string that ends in in '=', then it's treated as the name of a keyword
    arg of the wrapped function, and its value when that function is called is
    the final, indirect value of the decorator's parameter (for that call).
    See deco_settings.py docstring for details.

        enabled:           If true, then logging will occur. (Default: True)
        args_sep:          str used to separate args. The default is  ', ', which lists
                           all args on the same line. If args_sep ends in a newline '\n',
                           additional spaces are appended to that to make for a neater
                           display. Other separators in which '\n' occurs are left
                           unchanged, and are untested -- experiment/use at your own risk.
        log_args:          Arguments passed to the (decorated) function will be logged,
                           if true (Default: True)
        log_retval:        Log what the wrapped function returns, if true (truthy).
                           At most MAXLEN_RETVALS chars are printed. (Default: False)
        log_exit:          If true, the decorator will log an exiting message after
                           calling the function, and before returning what the function
                           returned. (Default: True)
        log_call_numbers: If truthy, display the (1-based) number of the function call,
                          e.g.   f [n] <== <module>   for n-th logged call.
                          This call would correspond to the n-th record
                          in the functions call history, if record_history is true.
                          (Default: False)
        log_elapsed:      If true, display how long it took the function to execute,
                          in seconds. (Default: False)
        indent:            if true, log messages for each level of log_calls-decorated
                           functions will be indented by 4 spaces, when printing
                           and not using a logger (default: False)
        prefix:            str to prefix the function name with when it is used
                           in logged messages: on entry, in reporting return value
                           (if log_retval) and on exit (if log_exit). (Default: '')
        logger:            If not None (the default), a Logger which will be used
                           (instead of the print function) to write all messages.
        loglevel:          logging level, if logger != None. (Default: logging.DEBUG)
        record_history:    If true, an array of records will be kept, one for each
                           call to the function; each holds call number (1-based),
                           arguments and defaulted keyword arguments, return value,
                           time elapsed, time of call, caller (call chain), prefixed
                           function name.(Default: False)
        max_history:       An int. value >  0 --> store at most value-many records,
                                                  oldest records overwritten;
                                   value <= 0 --> unboundedly many records are stored.
    """
    MAXLEN_RETVALS = 60
    LOG_CALLS_SENTINEL_ATTR = '$_log_calls_sentinel_'        # name of attr
    LOG_CALLS_SENTINEL_VAR = "$_log_calls-deco'd"
    LOG_CALLS_PREFIXED_NAME = '$log_calls-prefixed-name'     # name of attr
    LOG_CALLS_WRAPPER_FN_OBJ = '$f_log_calls_wrapper_-BACKPTR'  # LATE ADDITION

    # *** DecoSettingsMapping "API" --
    # (1) initialize: call register_class_settings

    # allow indirection for all except prefix and 10/18/14 max_history
    _setting_info_list = (
        DecoSetting('enabled',          int,            False,         allow_falsy=True),
        DecoSetting('args_sep',         str,            ', ',          allow_falsy=False),
        DecoSetting('log_args',         bool,           True,          allow_falsy=True),
        DecoSetting('log_retval',       bool,           False,         allow_falsy=True),
        DecoSetting('log_exit',         bool,           True,          allow_falsy=True),
        DecoSetting('log_call_numbers', bool,           False,         allow_falsy=True),
        DecoSetting('log_elapsed',      bool,           False,         allow_falsy=True),
        DecoSetting('indent',           bool,           False,         allow_falsy=True),
        DecoSetting('prefix',           str,            '',            allow_falsy=True,  allow_indirect=False),
        DecoSetting('logger',           logging.Logger, None,          allow_falsy=True),
        DecoSetting('loglevel',         int,            logging.DEBUG, allow_falsy=False),
        DecoSetting('record_history',   bool,           False,         allow_falsy=True),
        DecoSetting('max_history',      int,            0,             allow_falsy=True, allow_indirect=False, mutable=False),
    )
    DecoSettingsMapping.register_class_settings('log_calls',
                                                _setting_info_list)

    _descriptor_names = (
        'num_calls_logged',
        'num_calls_total',
        'elapsed_secs_logged',
        'call_history',
        'call_history_as_csv',
    )
    _method_descriptor_names = (
        'clear_history',
    )

    @classmethod
    def get_descriptor_names(cls):
        """Called by ClassInstanceAttrProxy when creating descriptors
        that correspond to the attrs of this class named in the returned list.
        ClassInstanceAttrProxy creates descriptors *once*.
        This enforces the rule that the descriptor names / attrs
        are the same for all (deco) instances, i.e. that they 're class-level."""
        return cls._descriptor_names

    @classmethod
    def get_method_descriptor_names(cls):
        """Called by ClassInstanceAttrProxy when creating descriptors
        that correspond to the methods of this class named in the returned list.
        ClassInstanceAttrProxy creates descriptors *once*.
        This enforces the rule that the descriptor names / attrs
        are the same for all (deco) instances, i.e. that they 're class-level."""
        return cls._method_descriptor_names

    # A few generic properties, internal logging, and exposed
    # as descriptors on the stats (ClassInstanceAttrProxy) obj
    @property
    def num_calls_logged(self):
        return self._num_calls_logged

    @property
    def num_calls_total(self):
        """All calls, logged and not logged"""
        return self._num_calls_total

    @property
    def elapsed_secs_logged(self):
        # REDONE: This value is accumulated for logged calls
        # whether or not history is being recorded.
        return self._elapsed_secs_logged

    @property
    def call_history(self):
        return tuple(self._call_history)

    @property
    def call_history_as_csv(self):
        """
        Headings (columns) are:
            call_num
            each-arg *
            varargs (str)
            implicit_kwargs (str)
            retval          (repr?)
            elapsed_secs    (double? float?)
            timestamp       (format somehow? what is it anyway)
            function (it's a name/str)
        """
        csv_sep = '|'
        all_args = list(self.f_params)
        varargs_name, kwargs_name = get_args_kwargs_param_names(self.f_params)

        csv = ''

        # Write column headings line (append to csv str)
        fields = ['call_num']
        fields.extend(all_args)
        fields.extend(['retval', 'elapsed_secs', 'timestamp', 'prefixed_fname', 'caller_chain'])
        csv = csv_sep.join(map(repr,fields))
        csv += '\n'

        # Write data lines
        for rec in self._call_history:
            fields = [str(rec.call_num)]
            # Do arg vals.
            # make dict of ALL args/vals
            all_args_vals_dict = {a: repr(v) for (a, v) in zip(rec.argnames, rec.argvals)}
            all_args_vals_dict.update(
                {a: repr(v) for (a, v) in rec.explicit_kwargs.items()}
            )
            all_args_vals_dict.update(
                {a: repr(v) for (a, v) in rec.defaulted_kwargs.items()}
            )
            for arg in all_args:
                if arg == varargs_name:
                    fields.append(str(rec.varargs))
                elif arg == kwargs_name:
                    fields.append(dict_to_sorted_str(rec.implicit_kwargs))     # str(rec.implicit_kwargs)
                else:
                    fields.append(all_args_vals_dict[arg])
            # and now the remaining fields
            fields.append(repr(rec.retval))
            fields.append(str(rec.elapsed_secs))
            fields.append(rec.timestamp)        # it already IS a formatted str
            fields.append(repr(rec.prefixed_func_name))
            fields.append(repr(rec.caller_chain))

            csv += csv_sep.join(fields)
            csv += '\n'

        return csv

    def _make_call_history(self):
        return deque(maxlen=(self.max_history if self.max_history > 0 else None))

    def clear_history(self, max_history=0):
        """Using clear_history it's possible to change max_history"""
        self._num_calls_logged = 0
        self._num_calls_total = 0

        self._elapsed_secs_logged = 0.0

        self.max_history = int(max_history)  # set before calling _make_call_history
        self._call_history = self._make_call_history()
        self._settings_mapping.__setitem__('max_history', max_history, _force_mutable=True)

    def _add_call(self, *, logged):
        self._num_calls_total += 1
        if logged:
            self._num_calls_logged += 1

    def _add_to_history(self,
                        argnames, argvals,
                        varargs,
                        explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                        retval,
                        elapsed_secs,
                        timestamp_secs,
                        prefixed_func_name,
                        caller_chain
    ):
        """Only called for *logged* calls.
        Call counters are already bumped."""
        record_history = self._settings_mapping.get_final_value(
                                'record_history',
                                explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                                fparams=None
        )
        if record_history:
            # Convert timestamp_secs to datetime
            timestamp = datetime.datetime.fromtimestamp(timestamp_secs).\
                strftime('%x %X.%f')    # or '%Y-%m-%d %I:%M:%S.%f %p'

            # argnames can contain keyword args (e.g. defaulted), so guard against that
            n = min(len(argnames), len(argvals))
            argnames = argnames[:n]
            argvals = argvals[:n]

            self._call_history.append(
                    CallRecord(
                        self._num_calls_logged,
                        argnames, argvals,
                        varargs,
                        explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                        retval,
                        elapsed_secs,
                        timestamp,
                        prefixed_func_name=prefixed_func_name,
                        caller_chain=caller_chain)
            )
        self._elapsed_secs_logged += elapsed_secs

    def __init__(
            self,
            enabled=True,
            args_sep=', ',
            log_args=True,
            log_retval=False,
            log_exit=True,
            log_call_numbers=False,
            log_elapsed=False,
            indent=False,   # probably better than =True
            prefix='',
            logger=None,
            loglevel=logging.DEBUG,
            record_history=False,
            max_history=0,
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
            args_sep=args_sep,
            log_args=log_args,
            log_retval=log_retval,
            log_exit=log_exit,
            log_call_numbers=log_call_numbers,
            log_elapsed=log_elapsed,
            indent=indent,
            prefix=prefix,
            logger=logger,
            loglevel=loglevel,
            record_history=record_history,
            max_history=max_history,
        )
        # and the special cases:
        self.prefix = prefix
        # Accessed by descriptors on the __Mapping obj
        self._num_calls_total = 0
        self._num_calls_logged = 0
        # max_history > 0 --> size of self._call_history; <= 0 --> unbounded
        # Set before calling _make_call_history
        self.max_history = max_history
        self._call_history = self._make_call_history()

        # Accumulate this (for logged calls only)
        # even when record_history is false:
        self._elapsed_secs_logged = 0.0

        self.f_params = None    # set properly by __call__

    def __call__(self, f):
        """Because there are decorator arguments, __call__() is called
        only once, and it can take only a single argument: the function
        to decorate. The return value of __call__ is called subsequently.
        So, this method *returns* the decorator proper."""
        # First, save prefix + function name for function f
        prefixed_fname = self.prefix + f.__name__
        # Might as well save f too !
        self.f = f
        # in addition to its parameters
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

            # if nothing to do, hurry up & don't do it.
            # NOTE: call_chain_to_next_log_calls_fn looks in stack frames
            # to find these next 4 _xxx variables (really!)
            _do_it = _get_final_value('enabled')
            self._add_call(logged=_do_it)    # bump self._num_calls_total

            _log_call_numbers = _get_final_value('log_call_numbers')
            backptr = getattr(f, self.LOG_CALLS_WRAPPER_FN_OBJ)
            # counters just got bumped
            _active_call_number = (backptr.stats.num_calls_logged
                                   if _log_call_numbers else
                                   0)
            # Get list of callers up to & including first log_call's-deco'd fn
            # (or just caller, if no such fn)
            call_list, prev_indent_level = self.call_chain_to_next_log_calls_fn()
            # Bump _extra_indent_level if last fn on call_list is deco'd AND enabled,
            # o/w it's the _extra_indent_level which that fn 'inherited'.
            # _extra_indent_level: prev_indent_level, or prev_indent_level + 1
            do_indent = _get_final_value('indent')
            _extra_indent_level = (prev_indent_level +
                                   int(not not do_indent and not not _do_it))
            if not _do_it:
                ### # call f after adding to stats, return its retval
                ### self._add_to_history(args, kwargs, logged=False)
                return f(*args, **kwargs)

            # Our unit of indentation
            indent = " " * 4

            logger = _get_final_value('logger')
            loglevel = _get_final_value('loglevel')
            # Establish logging function
            logging_fn = partial(logger.log, loglevel) if logger else print

            # Only do global indentation for print, not for loggers
            global_indent = ((_extra_indent_level * indent)
                             * int(not logger)
                            )

            # log_call_numbers
            call_number_str = (('[%d] ' % _active_call_number)
                               if _log_call_numbers else '')
            msg = (global_indent +
                   ("%s %s<== called by %s"
                    % (prefixed_fname,
                       call_number_str,
                       ' <== '.join(call_list))))

            # Gather all the things we need (for log output, & for _add_history)
            # Use inspect module's Signature.bind method.
            # bound_args.arguments -- contains only explicitly bound arguments
            bound_args = inspect.signature(f).bind(*args, **kwargs)
            varargs_pos = get_args_pos(self.f_params)   # -1 if no *args in signature
            argcount = varargs_pos if varargs_pos >= 0 else len(args)
            varargs = args[argcount:]
            # The first argcount-many things in bound_args
            argnames = list(bound_args.arguments)[:argcount]

            defaulted_kwargs = OrderedDict(
                [(param.name, param.default) for param in self.f_params.values()
                 if param.name not in bound_args.arguments
                 and param.default != inspect._empty
                ]
            )
            explicit_kwargs = OrderedDict(
                [(k, kwargs[k]) for k in self.f_params
                 if k in bound_args.arguments and k in kwargs]
            )
            varargs_name, kwargs_name = get_args_kwargs_param_names(self.f_params)
            implicit_kwargs = {
                k: kwargs[k] for k in kwargs if k not in explicit_kwargs
            }
            args_vals = list(zip(argnames, args))

            # Make & append args message
            # If function has no parameters or if not log_args,
            # skip arg reportage, don't even bother writing "arguments: <none>"
            if self.f_params and _get_final_value('log_args'):

                args_sep = _get_final_value('args_sep')  # != ''

                # ~Kludge / incomplete treatment of seps that contain \n
                end_args_line = ''
                if args_sep[-1] == '\n':
                    args_sep = '\n' + global_indent + (indent * 2)
                    end_args_line = args_sep

                msg += ('\n' + global_indent + indent + "arguments: " + end_args_line)

                if varargs:
                    args_vals.append( ("[*]%s" % self.args_name, varargs) )

                args_vals.extend( explicit_kwargs.items() )

                if implicit_kwargs:
                    args_vals.append( ("[**]%s" % self.kwargs_name,  implicit_kwargs) )

                if args_vals:
                    msg += args_sep.join('%s=%r' % pair for pair in args_vals)
                else:
                    msg += "<none>"

                # The defaulted kwargs are kw args in self.f_params which
                # are NOT in implicit_kwargs, and their vals are defaults
                # of those parameters. Write these on a separate line.
                # Don't just print the OrderedDict -- cluttered appearance.
                if defaulted_kwargs:
                    msg += ('\n' + global_indent + indent + "defaults:  " + end_args_line
                            + args_sep.join('%s=%r' % pair for pair in defaulted_kwargs.items())
                    )

            logging_fn(msg)

            # Call f(*args, **kwargs) and get its retval,
            # then add elapsed time and retval (as str? repr?) etc to stats
            t0 = time.time()
            retval = f(*args, **kwargs)
            elapsed_secs = (time.time() - t0)

            self._add_to_history(argnames[:argcount], args[:argcount],
                                 varargs,
                                 explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                                 retval,
                                 elapsed_secs=elapsed_secs,
                                 timestamp_secs=t0,
                                 prefixed_func_name=prefixed_fname,
                                 caller_chain=call_list
            )
            # log_retval
            if _get_final_value('log_retval'):
                retval_str = str(retval)
                if len(retval_str) > log_calls.MAXLEN_RETVALS:
                    retval_str = retval_str[:log_calls.MAXLEN_RETVALS] + "..."
                logging_fn(global_indent + indent + "%s %sreturn value: %s"
                           % (prefixed_fname, call_number_str, retval_str))

            # log_elapsed
            if _get_final_value('log_elapsed'):
                logging_fn(global_indent + indent + "elapsed time: %f [secs]" % elapsed_secs)

            # log_exit
            if _get_final_value('log_exit'):
                exit_msg = (
                    global_indent +
                    ("%s %s==> returning to %s"
                           % (prefixed_fname,
                              call_number_str,
                              ' ==> '.join(call_list)))
                )
                logging_fn(exit_msg)
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
        # LATE ADDITION: A back-pointer
        setattr(
            f,
            self.LOG_CALLS_WRAPPER_FN_OBJ,
            f_log_calls_wrapper_
        )
        stats = ClassInstanceAttrProxy( class_instance=self)
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

        call_list = []
        prev_indent_level = -1

        found = False
        found_enabled = False
        break_both = False      # both loops
        while not found_enabled and not break_both:
            while 1:    # until found a deco'd fn or <module> reached
                curr_funcname = curr_frame.f_code.co_name
                if curr_funcname == 'f_log_calls_wrapper_':
                    # Previous was decorated inner fn; don't add 'f_log_calls_wrapper_'
                    # print("**** found f_log_calls_wrapper_, prev fn name =", call_list[-1])     # <<<DEBUG>>>
                    # Fixup: get prefixed named of wrapped function
                    inner_fn = curr_frame.f_locals['f']
                    call_list[-1] = getattr(inner_fn,
                                            log_calls.LOG_CALLS_PREFIXED_NAME)
                    wrapper_frame = curr_frame
                    # # LATE ADDITION
                    # curr_fn = getattr(inner_fn, log_calls.LOG_CALLS_WRAPPER_FN_OBJ)
                    found = True
                    break   # inner loop

                call_list.append(curr_funcname)

                if curr_funcname == '<module>':
                    break_both = True
                    break   # inner loop

                globs = curr_frame.f_back.f_globals
                curr_fn = None
                if curr_funcname in globs:
                    wrapper_frame = curr_frame.f_back
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
                        wrapper_frame = curr_frame.f_back
                        if curr_funcname in locls:
                            curr_fn = locls[curr_funcname]
                            #   print("**** %s found in locls = curr_frame.f_back.f_back.f_locals, "
                            #         "curr_frame.f_back.f_back.f_code.co_name = %s"
                            #         % (curr_funcname, curr_frame.f_back.f_back.f_locals)) # <<<DEBUG>>>
                        elif 'prefixed_fname' in locls:
                            # curr_funcname will 'come around for real' next time through loop,
                            # so remove it from end now
                            call_list = call_list[:-1]
                            # and curr_fn is None, so it won't have attr in next "if"
                if hasattr(curr_fn, log_calls.LOG_CALLS_SENTINEL_ATTR):
                    found = True
                    break   # inner loop
                curr_frame = curr_frame.f_back

            # If found, then call_list[-1] is log_calls-wrapped
            if found:
                # look in stack frame (!) for
                #   _do_it, _log_call_numbers, _active_call_number
                enabled = wrapper_frame.f_locals['_do_it']
                log_call_numbers = wrapper_frame.f_locals['_log_call_numbers']
                active_call_number = wrapper_frame.f_locals['_active_call_number']
                # only change prev_indent_level once, for nearest deco'd fn
                if prev_indent_level < 0:
                    prev_indent_level = wrapper_frame.f_locals['_extra_indent_level']
                if enabled and log_call_numbers:
                    call_list[-1] += " [" + str(active_call_number) + "]"
                found_enabled = enabled     # done with outer loop too if enabled
                if not enabled:
                    curr_frame = curr_frame.f_back
            else:   # not found
                # if not found, truncate call_list to first element.
                call_list = call_list[:1]

        return call_list, prev_indent_level
