__author__ = "Brian O'Neill"  # BTO
__version__ = '0.3.0'
__doc__ = """
Configurable decorator for debugging and profiling that writes
caller name(s), args+values, function return values, execution time,
number of call, to stdout or to a logger. log_calls can track
call history and provide it in CSV format and Pandas DataFrame format.
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
import os
import io   # so we can refer to io.TextIOBase
import time
import datetime
from collections import namedtuple, deque

import fnmatch  # 0.3.0 for omit, only

from .deco_settings import (DecoSetting,
                            DecoSetting_bool, DecoSetting_int, DecoSetting_str,
                            DecoSettingsMapping)
from .helpers import (get_args_pos, get_args_kwargs_param_names,
                      difference_update,
                      get_defaulted_kwargs_OD, get_explicit_kwargs_OD,
                      dict_to_sorted_str, prefix_multiline_str,
                      is_quoted_str, any_match)
from .proxy_descriptors import ClassInstanceAttrProxy
from .used_unused_kwds import used_unused_keywords

__all__ = ['log_calls', 'CallRecord', '__version__', '__author__']

#------------------------------------------------------------------------------
##~ PROFILE
#------------------------------------------------------------------------------
# from collections import OrderedDict
#
# class time_block():
#     def __init__(self, label):
#         self.label = label
#         self.elapsed_list1 = [0.0]  # self.elapsed_list1[0] replaced with elapsed time
#
#     def __enter__(self):
#         self.start = time.perf_counter()
#         # self.elapsed_list1 becomes the value of foo in
#         #       with time_block(lbl) as foo: ...
#         # (see __exit__).
#         # Caller/user accesses elapsed time via foo[0]
#         return self.elapsed_list1
#
#     def __exit__(self, exc_ty, exc_val, exc_tb):
#         end = time.perf_counter()
#         self.elapsed_list1[0] = end - self.start
#         # print('{}: {}'.format(self.label, end - self.start))
# END PROFILE

#------------------------------------------------------------------------------
# log_calls
#------------------------------------------------------------------------------
CallRecord = namedtuple(
    "CallRecord",
    (
        'call_num',
        'argnames', 'argvals',
        'varargs',
        'explicit_kwargs', 'defaulted_kwargs', 'implicit_kwargs',
        'retval',
        'elapsed_secs', 'CPU_secs',
        'timestamp',
        'prefixed_func_name',
        # caller_chain: list of fn names, possibly "prefixed".
        # From most-recent (immediate caller) to least-recent if len > 1.
        'caller_chain',
    )
)


#-----------------------------------------------------------------------------
# DecoSetting subclasses with pre-call handlers.
# The `context` arg for pre_call_handler methods has these keys:
#     decorator
#     settings              # self._deco_settings     (of decorator)
#     stats                 # self._stats             ("      "    )
#     indent
#     prefixed_fname
#     output_fname          # prefixed_fname + possibly num_calls_logged (if log_call_numbers true)
#     fparams
#     argcount
#     argnames              # argcount-long
#     argvals               # argcount-long
#     varargs
#     explicit_kwargs
#     defaulted_kwargs
#     implicit_kwargs
#     call_list
#     args
#     kwargs
#-----------------------------------------------------------------------------

# TODO 0.2.6, possible `context` setting:  - - - - - - - - - - - - - - - - - -
# todo  context key/vals that would be of interest to wrapped functions:
#     settings
#     stats
#     explicit_kwargs
#     defaulted_kwargs
#     implicit_kwargs   # ??? maybe
#     call_list
# Note: stats (data) attributes are all r/o (but method clear_history isn't!),
#         so wrapped function can't trash 'em;
#       settings - could pass settings.as_dict();
#       the rest (*_kwargs, call_list) could be mucked with,
#         so we'd have to deepcopy() to prevent that.
#       OR just document that wrapped functions shouldn't write to these values,
#          as they're "live" and altering them could cause confusion/chaos/weirdness/crashes.
#end TODO. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class DecoSettingEnabled(DecoSetting_int):
    def __init__(self, name, **kwargs):
        super().__init__(name, int, False, allow_falsy=True, **kwargs)

    def pre_call_handler(self, context):
        return ("%s <== called by %s"
                % (context['output_fname'],
                   ' <== '.join(context['call_list'])))

    def value_from_str(self, s):
        """Virtual method for use by _deco_base._read_settings_file.
        0.2.4.post1"""
        try:
            return int(s)
        except ValueError:
            try:
                return bool(s)
            except ValueError:
                return self.default


class DecoSettingArgs(DecoSetting_bool):
    def __init__(self, name, **kwargs):
        super().__init__(name, bool, True, allow_falsy=True, **kwargs)

    @staticmethod
    def _get_all_ids_of_instances_in_progress(context, *, skipframes):
        in_progress = set()
        # First, deal with wrapper/the function it wraps
        deco = context['decorator']
        if deco.f.__name__ == '__init__' and deco._classname_of_f:
            argvals = context['argvals']
            if argvals and not inspect.isclass(argvals[0]):  # not interested in metaclass __init__
                in_progress.add(id(argvals[0]))

        frame = sys._getframe(skipframes)
        while 1:
            funcname = frame.f_code.co_name
            if funcname == '<module>':
                break

            if funcname == '__init__':
                # so if it's really an instance __init__,
                #     eval('self.__init__', frame.f_globals, frame.f_locals)
                # is a bound method, so .__func__ will be underlying function
                # and .__self__ is the instance it's bound to :)
                try:
                    init_method = eval('self.__init__', frame.f_globals, frame.f_locals)
                except Exception as e:
                    pass
                else:
                    if inspect.ismethod(init_method):
                        func = init_method.__func__
                        instance = init_method.__self__
                        if not inspect.isclass(instance):     # not interested in metaclass __init__
                            in_progress.add(id(instance))

            frame = frame.f_back
        return in_progress

    def pre_call_handler(self, context: dict):
        """Alert:
        this class's handler knows the keyword of another handler (args_sep),
        # whereas it shouldn't even know its own (it should use self.name)"""
        if not context['fparams']:
            return None

        # Make msg
        args_sep = context['settings'].get_final_value(
                    'args_sep', context['kwargs'], fparams=context['fparams'])
        indent = context['indent']

        # ~Kludge / incomplete treatment of seps that contain \n
        end_args_line = ''
        if args_sep[-1] == '\n':
            args_sep = '\n' + (indent * 2)
            end_args_line = args_sep

        msg = indent + "arguments: " + end_args_line

        # Two convenience functions
        def map_to_arg_eq_val_strs(pairs):
                return map(lambda pair: '%s=%r' % pair, pairs)

        def map_to_arg_eq_val_strs_safe(pairs):
            """
            :param pairs: sequence of (arg, val) pairs
            :return: list of strings `arg=val_str` where val_str is
                        object.__repr__(val) if val is an instance currently being constructed,
                        repr(val) otherwise
            """
            # Get all active instances whose __init__s are on call stack
            # caller-of-caller-of-caller's frame
            # caller is pre_call_handler, called by wrapper;
            # we want to start with caller of wrapper, so skipframes=4
            ids_objs_in_progress = self._get_all_ids_of_instances_in_progress(context, skipframes=4)

            arg_eq_val_strs = []
            for pair in pairs:
                arg, val = pair
                if id(val) in ids_objs_in_progress:
                    arg_eq_val_str = '%s=%s' % (arg, object.__repr__(val))
                else:
                    arg_eq_val_str = '%s=%r' % pair
                arg_eq_val_strs.append(arg_eq_val_str)
            return arg_eq_val_strs

        args_vals = list(zip(context['argnames'], context['argvals']))

        if context['varargs']:
            args_vals.append( ("[*]%s" % context['varargs_name'], context['varargs']) )

        args_vals.extend( context['explicit_kwargs'].items() )

        if context['implicit_kwargs']:
            args_vals.append( ("[**]%s" % context['kwargs_name'], context['implicit_kwargs']) )

        if args_vals:
            msg += args_sep.join(
                        map_to_arg_eq_val_strs_safe(args_vals))
        else:
            msg += "<none>"

        # The defaulted kwargs are kw args in self.f_params which
        # are NOT in implicit_kwargs, and their vals are defaults
        # of those parameters. Write these on a separate line.
        # Don't just print the OrderedDict -- cluttered appearance.
        if context['defaulted_kwargs']:
            msg += ('\n' + indent + "defaults:  " + end_args_line
                    + args_sep.join(
                        map_to_arg_eq_val_strs(context['defaulted_kwargs'].items()))
            )

        return msg


#-----------------------------------------------------------------------------
# DecoSetting subclasses with post-call handlers.
# The `context` for post_call_handler methods has these additional keys:
#     elapsed_secs
#     CPU_secs
#     timestamp
#     retval
#-----------------------------------------------------------------------------

class DecoSettingRetval(DecoSetting_bool):
    MAXLEN_RETVALS = 77

    def __init__(self, name, **kwargs):
        super().__init__(name, bool, False, allow_falsy=True, **kwargs)

    def post_call_handler(self, context: dict):
        retval_str = str(context['retval'])
        if len(retval_str) > self.MAXLEN_RETVALS:
            retval_str = retval_str[:self.MAXLEN_RETVALS] + "..."
        return (context['indent'] +
                "%s return value: %s" % (context['output_fname'], retval_str))


class DecoSettingElapsed(DecoSetting_bool):
    def __init__(self, name, **kwargs):
        super().__init__(name, bool, False, allow_falsy=True, **kwargs)

    def post_call_handler(self, context: dict):
        return (context['indent'] +
                "elapsed time: %f [secs], CPU time: %f [secs]"
                % (context['elapsed_secs'], context['CPU_secs']))


class DecoSettingExit(DecoSetting_bool):
    def __init__(self, name, **kwargs):
        super().__init__(name, bool, True, allow_falsy=True, **kwargs)

    def post_call_handler(self, context: dict):
        return ("%s ==> returning to %s"
                   % (context['output_fname'],
                      ' ==> '.join(context['call_list'])))


class DecoSettingHistory(DecoSetting_bool):
    def __init__(self, name, **kwargs):
        super().__init__(name, bool, False, allow_falsy=True, **kwargs)

    def post_call_handler(self, context: dict):
        context['decorator']._add_to_history(
            context['argnames'],
            context['argvals'],
            context['varargs'],
            context['explicit_kwargs'],
            context['defaulted_kwargs'],
            context['implicit_kwargs'],
            context['retval'],
            elapsed_secs=context['elapsed_secs'],
            CPU_secs=context['CPU_secs'],
            timestamp_secs=context['timestamp'],
            prefixed_func_name=context['prefixed_fname'],
            caller_chain=context['call_list']
        )
        return None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DecoSetting subclasses overriding value_from_str and has_acceptable_type
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class DecoSettingFile(DecoSetting):
    def value_from_str(self, s):
        """Virtual method for use by _deco_base._read_settings_file.
        0.2.4.post1"""
        if s == 'sys.stderr':
            ### print("DecoSettingFile.value_from_str, s=%s, returning %r (sys.stderr?)" % (s, sys.stderr))
            return sys.stderr
        # 'sys.stdout' ultimately becomes None via this:
        return super().value_from_str(s)

    def has_acceptable_type(self, value):
        """Accommodate IPython, whose sys.stderr is of type IPython.kernel.zmq.iostream.OutStream.
        """
        if not value:
            return False
        if super().has_acceptable_type(value):
            return True
        # Hmmm ok maybe we're running under IPython:
        try:
            import IPython
            return isinstance(value, IPython.kernel.zmq.iostream.OutStream)
        except ImportError:
            return False


class DecoSettingLogger(DecoSetting):
    def value_from_str(self, s):
        """Virtual method for use by _deco_base._read_settings_file.
        s is the name of a logger, enclosed in quotes, or something bad.
        0.2.4.post1"""
        if is_quoted_str(s):
            return s[1:-1]
        return super().value_from_str(s)


#-----------------------------------------------------------------------------
# Fat base class for log_calls and record_history decorators
#-----------------------------------------------------------------------------

class _deco_base():
    """
    Base class for decorators that records history and optionally write to
    the console or logger by supplying their own settings (DecoSetting subclasses)
    with pre_call_handler and post_call_handler methods.
    The wrapper of the wrapped function collects a lot of information,
    saved in a dict `context`, which is passed to the handlers.
    This and derived decorators take various keyword arguments, same as settings keys.
    Every parameter except prefix and max_history can take two kinds of values,
    direct and indirect. Briefly, if the value of any of those parameters
    is a string that ends in in '=', then it's treated as the name of a keyword
    arg of the wrapped function, and its value when that function is called is
    the final, indirect value of the decorator's parameter (for that call).
    See deco_settings.py docstring for details.

    Settings/keyword params to __init__ that this base class knows about,
    and uses in __call__ (in wrapper for wrapped function):

        enabled:           If true, then logging will occur. (Default: True)
        log_call_numbers: If truthy, display the (1-based) number of the function call,
                          e.g.   f [n] <== <module>   for n-th logged call.
                          This call would correspond to the n-th record
                          in the functions call history, if record_history is true.
                          (Default: False)
        indent:            if true, log messages for each level of log_calls-decorated
                           functions will be indented by 4 spaces, when printing
                           and not using a logger (default: False)
        prefix:            str to prefix the function name with when it is used
                           in logged messages: on entry, in reporting return value
                           (if log_retval) and on exit (if log_exit). (Default: '')
        record_history:    If true, an array of records will be kept, one for each
                           call to the function; each holds call number (1-based),
                           arguments and defaulted keyword arguments, return value,
                           time elapsed, time of call, caller (call chain), prefixed
                           function name.(Default: False)
        max_history:       An int. value >  0 --> store at most value-many records,
                                                  oldest records overwritten;
                                   value <= 0 --> unboundedly many records are stored.
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # constants for the `mute` setting
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    class mute():
        NOTHING = False     # (default -- all output produced)
        CALLS = True        # (mute output from decorated functions & methods & properties,
                            #  but log_message and thus log_exprs produce output;
                            #  call # recording, history recording continue if enabled)
        ALL = -1            # (no output at all; but call # recording, history recording continue if enabled)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # sentinels, for identifying functions on the calls stack
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    _sentinels_proto = {
        'SENTINEL_ATTR': '_$_%s_sentinel_',             # name of attr
        'SENTINEL_VAR': "_$_%s-deco'd",
        'WRAPPER_FN_OBJ': '_$_f_%s_wrapper_-BACKPTR',   # LATE ADDITION
        'DECO_OF': '_$_f_%s_wrapper_-or-cls-DECO'       # value = self (0.3.0)
    }

    @classmethod
    def _set_class_sentinels(cls):
        """ 'virtual', called from __init__
        """
        sentinels = cls._sentinels_proto.copy()
        for sk in sentinels:
            sentinels[sk] = sentinels[sk] % cls.__name__
        return sentinels

    # placeholder! _set_class_sentinels called from __init__
    _sentinels = None

    INDENT = 4      # number of spaces to __ by at a time

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # # *** DecoSettingsMapping "API" --
    # # (1) initialize: Subclasses must call register_class_settings
    # #     with a sequence of DecoSetting objs containing at least these:
    # #     (TODO: yes it's an odd lot of required DecoSetting objs)
    #
    # _setting_info_list = (
    #     DecoSettingEnabled('enabled'),
    #     DecoSetting_bool(  'indent',           bool, False, allow_falsy=True),
    #     DecoSetting_bool(  'log_call_numbers', bool, False, allow_falsy=True),
    #     DecoSetting_str(   'prefix',           str,  '',    allow_falsy=True,  allow_indirect=False)
    # )
    # DecoSettingsMapping.register_class_settings('_deco_base',
    #                                             _setting_info_list)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # call history and stats stuff
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    _descriptor_names = (
        'num_calls_logged',
        'num_calls_total',
        'elapsed_secs_logged',
        'CPU_secs_logged',
        'history',
        'history_as_csv',
        'history_as_DataFrame',
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
        # This value is accumulated for logged calls
        # whether or not history is being recorded.
        return self._elapsed_secs_logged

    @property
    def CPU_secs_logged(self):
        # This value is accumulated for logged calls
        # whether or not history is being recorded.
        return self._CPU_secs_logged

    @property
    def history(self):
        return tuple(self._call_history)

    @property
    def history_as_csv(self):
        """
        Headings (columns) are:
            call_num
            each-arg *
            varargs (str)
            implicit_kwargs (str)
            retval          (repr?)
            elapsed_secs
            CPU_secs
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
        fields.extend(['retval', 'elapsed_secs', 'CPU_secs', 'timestamp', 'prefixed_fname', 'caller_chain'])
        # 0.2.1 - use str not repr, get rid of quotes around column names
        csv = csv_sep.join(map(str, fields))
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
            fields.append(str(rec.CPU_secs))
            fields.append(rec.timestamp)        # it already IS a formatted str
            fields.append(repr(rec.prefixed_func_name))
            fields.append(repr(rec.caller_chain))

            csv += csv_sep.join(fields)
            csv += '\n'

        return csv

    @property
    def history_as_DataFrame(self):
        try:
            import pandas as pd
        except ImportError:
            return None

        import io
        df = pd.DataFrame.from_csv(io.StringIO(self.history_as_csv),
                                   sep='|',
                                   infer_datetime_format=True)
        return df

    def _make_call_history(self):
        return deque(maxlen=(self.max_history if self.max_history > 0 else None))

    def clear_history(self, max_history=0):
        """Using clear_history it's possible to change max_history"""
        self._num_calls_logged = 0
        self._num_calls_total = 0

        self._elapsed_secs_logged = 0.0
        self._CPU_secs_logged = 0.0

        self.max_history = int(max_history)  # set before calling _make_call_history
        self._call_history = self._make_call_history()
        self._settings_mapping.__setitem__('max_history', max_history, _force_mutable=True)

    def _add_call(self, *, logged):
        self._num_calls_total += 1
        if logged:
            self._num_calls_logged += 1

    def _add_to_elapsed(self, elapsed_secs, CPU_secs):
        self._elapsed_secs_logged += elapsed_secs
        self._CPU_secs_logged += CPU_secs

    def _add_to_history(self,
                        argnames, argvals,
                        varargs,
                        explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                        retval,
                        elapsed_secs, CPU_secs,
                        timestamp_secs,
                        prefixed_func_name,
                        caller_chain
    ):
        """Only called for *logged* calls, with record_history true.
        Call counters are already bumped."""
        # Convert timestamp_secs to datetime
        timestamp = datetime.datetime.fromtimestamp(timestamp_secs).\
            strftime('%x %X.%f')    # or '%Y-%m-%d %I:%M:%S.%f %p'

        ## 0.2.3+ len(argnames) == len(argvals)
        ## assert len(argnames) == len(argvals)
        # n = min(len(argnames), len(argvals))
        # argnames = argnames[:n]
        # argvals = argvals[:n]

        self._call_history.append(
                CallRecord(
                    self._num_calls_logged,
                    argnames, argvals,
                    varargs,
                    explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                    retval,
                    elapsed_secs, CPU_secs,
                    timestamp,
                    prefixed_func_name=prefixed_func_name,
                    caller_chain=caller_chain)
        )

    # 0.3.0
    def _enabled_state_push(self, enabled):
        self._enabled_stack.append(enabled)

    # 0.3.0
    def _enabled_state_pop(self):
        self._enabled_stack.pop()

    def _logging_state_push(self, logging_fn, global_indent_len, output_fname):
        self._logging_fn.append(logging_fn)
        self._indent_len.append(global_indent_len)
        self._output_fname.append(output_fname)

    def _logging_state_pop(self, enabled_too=False):
        self._logging_fn.pop()
        self._indent_len.pop()
        self._output_fname.pop()
        if enabled_too:
            self._enabled_state_pop()

    def _log_exprs(self, *exprs, sep=', ',
                     extra_indent_level=1, prefix_with_name=False):
        """Evaluates each expression (str) in exprs in the context of the caller;
        makes string from each, expr = val,
        pass those strs to _log_message.
        :param exprs:
        :param sep: as for _log_message
        :param extra_indent_level: as for _log_message
        :param prefix_with_name: as for _log_message
        """
        if not exprs:
            return
        msgs = []
        caller_frame = sys._getframe(1)
        for expr in exprs:
            try:
                val = eval(expr, caller_frame.f_globals, caller_frame.f_locals)
            except Exception as e:  # (SyntaxError, NameError, IndexError, ...)
                val = '<** ' + str(e) + ' **>'
            msgs.append('%s = %r' % (expr, val))
        self._log_message(*msgs,
                          sep=sep,
                          extra_indent_level=extra_indent_level,
                          prefix_with_name=prefix_with_name)

    def _log_message(self, msg, *msgs, sep=' ',
                     extra_indent_level=1, prefix_with_name=False):
        """Signature much like that of print, such is the intent.
        "log" one or more "messages", which can be anything - a string,
        an int, object with __str__ method... all get str()'d.
        sep: what to separate the messages with
        extra_indent_level: self.INDENT * this number is
            an offset from the (absolute) column in which
            the entry/exit messages for the function are written.
        I.e. an offset from the visual frame of log_calls output,
            in increments of 4 (cols) from its left margin.
        log_calls itself explicitly provides extra_indent_level=0.
        The given default value, extra_indent_level=1, is what users
        *other* than log_calls itself want: this aligns the message(s)
        with the "arguments:" part of log_calls output, rather than
        with the function entry/exit messages.
        Negative values of extra_indent_level have their place:
            me.log_message("*** An important message", extra_indent_level=-1)
            me.log_message("An ordinary message").

        prefix_with_name: bool. If True, prepend
               self._output_fname[-1] + ": "
        to the message ultimately written.
        self._output_fname[-1] is the function's possibly prefixed name,
            + possibly [its call #]
        """
        # do nothing unless enabled! cuz then the other 'stack' accesses will blow up
        if self._enabled_stack[-1] <= 0:    # disabled
            return

        # 0.3.0
        # Write nothing if output is stifled (caller is NOT f_log_calls_wrapper_)
        mute = self._settings_mapping['mute']
        if mute == self.mute.ALL:
            return
        # adjust for calls not being logged -- don't indent an extra level
        #  (no 'log_calls frame', no 'arguments:' to align with),
        #  and prefix with display name cuz there's no log_calls "frame"
        if mute == self.mute.CALLS:
            extra_indent_level -= 1
            prefix_with_name = True

        logging_fn = self._logging_fn[-1]
        indent_len = (self._indent_len[-1] +
                      + (extra_indent_level * self.INDENT)
                     )
        if indent_len < 0:
            indent_len = 0   # clamp
        the_msgs = (msg,) + msgs
        the_msg = sep.join(map(str, the_msgs))
        if prefix_with_name:
            the_msg = self._output_fname[-1] + ': ' + the_msg
        logging_fn(prefix_multiline_str(' ' * indent_len, the_msg))

    def _read_settings_file(self, settings_path=''):
        """If settings_path names a file that exists,
        load settings from that file.
        If settings_path names a directory, load settings from
            settings_path + '.' + self.__class__.__name__
            e.g. the file '.log_calls' in directory specified by settings_path.
        If not settings_path or it doesn't exist, return {}.
        Format of settings file - zero or more lines of the form:
            setting_name=setting_value
        with possible whitespace around *_name.
        Blank lines are ok & ignored; lines whose first non-whitespace char is '#'
        are treated as comments & ignored.

        Note: self._settings_mapping doesn't exist yet!
              so this function can't use it, e.g. to test for valid settings,
                    if setting in self._settings_mapping: ...
              won't work.
        """
        if not settings_path:
            return {}

        if os.path.isdir(settings_path):
            settings_path = os.path.join(settings_path, '.' + self.__class__.__name__)
        if not os.path.isfile(settings_path):
            return {}

        d = {}      # returned
        try:
            with open(settings_path) as f:
                lines = f.readlines()
        except BaseException:   # FileNotFoundError?!
            return d

        settings_dict = DecoSettingsMapping.get_deco_class_settings_dict(self.__class__.__name__)
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue

            try:
                setting, val_txt = line.split('=', 1)   # only split at first '='
            except ValueError:
                # fail silently. (Or, TODO: report error? ill-formed line)
                continue                                # bad line
            setting = setting.strip()
            val_txt = val_txt.strip()

            if setting not in settings_dict or not val_txt:
                # fail silently. (Or, TODO: report error? ill-formed line)
                continue

            # special case: None
            if val_txt == 'None':
                if settings_dict[setting].allow_falsy:
                    d[setting] = None
                continue

            # If val_txt is enclosed in quotes (single or double)
            # and ends in '=' (indirect value) then let val = val_txt;
            # otherwise, defer to settings_dict[setting].value_from_str
            is_indirect = (is_quoted_str(val_txt) and
                           len(val_txt) >= 3 and
                           val_txt[-2] == '=')
            if is_indirect:
                val = val_txt[1:-1]     # remove quotes
            else:
                try:
                    val = settings_dict[setting].value_from_str(val_txt)
                except ValueError as e:
                    # fail silently. (Or, TODO: report error? bad value)
                    continue                            # bad line

            d[setting] = val

        return d

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # __init__, __call__
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self,
                 settings=None,
                 _omit=tuple(),             # 0.3.0 class deco'ing: str or seq - omit these methods/proper; not a setting
                 _only=tuple(),             # 0.3.0 class deco'ing: str or seq - deco only these (sans any in omit); not a setting
                 _name_param=None,          # 0.3.0 name or oldstyle fmt str for f_display_name of fn; not a setting
                 _used_keywords_dict={},    # 0.2.4 new parameter, but NOT a "setting"
                 enabled=True,
                 log_call_numbers=False,
                 indent=False,
                 prefix='',
                 mute=False,
                 ** other_values_dict):
        """(See class docstring)
        _used_keywords_dict: passed by subclass via super().__init__:
            the *explicit* keyword args of subclass that the user actually passed,
            not ones that are implicit keyword args,
            and not ones that the user did not pass and which have default values.
            (It's default value is mutable, but we don't change it.)
        """
        #--------------------------------------------------------------------
        # 0.2.4 `settings` stuff, rejiggered in 0.3.0
        # Set/save self._changed_settings =
        #     `settings` (param -- dict or file)
        #     updated with actual keyword parameters supplied to deco call
        # set/save self._effective_settings -
        #     static defaults (for self.__class__.__name__)
        #     updated with self._changed_settings
        #--------------------------------------------------------------------

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Set up defaults_dict with log_calls's defaults - the static ones:
        #   self.__class__.__name__ is name *of subclass*, clsname,
        #   which we trust has already called
        #     DecoSettingsMapping.register_class_settings(clsname, list-of-deco-setting-objs)
        #   Special-case handling of 'enabled' (ugh, eh), whose DecoSetting obj
        #   has .default = False, for "technical" reasons
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        od = DecoSettingsMapping.get_deco_class_settings_dict(self.__class__.__name__)
        defaults_dict = {k: od[k].default for k in od}
        defaults_dict['enabled'] = True
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # get settings from dict | read settings from file
        # if given, as a dict settings_dict
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        settings_dict = {}
        if isinstance(settings, dict):
            settings_dict = settings
        elif isinstance(settings, str):
            settings_dict = self._read_settings_file(settings_path=settings)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # 0.3.0 Save settings_dict updated with _used_keywords_dict
        # so that these can be reapplied by any outer class deco --
        # (class deco's _effective_settings (copy of) updated with these --
        # in class case of __call__
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        settings_dict.update(_used_keywords_dict)   # settings_dict is now no longer *that*
        self._changed_settings = settings_dict

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # update defaults_dict with settings *explicitly* passed to caller
        # of subclass's __init__, and save *that* (used in __call__)
        # as self._effective_settings, which are the final settings used
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        defaults_dict.update(self._changed_settings)    # defaults_dict is now no longer *that*
        self._effective_settings = defaults_dict

        def _make_sequence(names) -> tuple:
            """names is either a string of space- and/or comma-separated umm tokens,
            or is already a sequence of tokens.
            Return tuple of tokens."""
            if isinstance(names, str):
                names = names.replace(',', ' ').split()
            return tuple(map(str, names))

        self._omit = _make_sequence(_omit)
        self._only = _make_sequence(_only)

        self.prefix = prefix                # special case
        self._name_param = _name_param
        self._other_values_dict = other_values_dict     # 0.3.0
        # 0.3.0 Factored out rest of __init__ to function case of __call__

    # Keys: attributes of properties;
    # Vals: what users can suffix prop names with in omit & only lists
    PROP_SUFFIXES = {'fget': 'getter',
                     'fset': 'setter',
                     'fdel': 'deleter'}

    def class__call__(self, cls):
        """
        :param cls: class to decorate ALL the methods of,
                    including properties and methods of inner classes.
        :return: decorated class (cls - modified/operated on)
        Operate on each function in cls.
        Use __getattribute__ to determine whether a function is (/will be)
        an instance method, staticmethod or classmethod;

        if either of the latter, get wrapped actual function (.__func__);
            if wrapped function is itself decorated by <this decorator>
            that is, self.__class__.__name__
            that is, self.__class__
                (look for 'signature' attribute on function,
                 hasattr 'DECO_OF')
            *** GET THE INSTANCE of this deco class *** for that function,
                using sentinel deco_obj = getattr(func, 'DECO_OF')
            get deco_obj._changed_settings of that instance,

            THEN make its settings = self._effective_settings (for this cls)
                updated with those deco_obj._changed_settings

        otherwise, (a non-wrapped function that will be an instance method)
            we already have the function.

        <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO TODO TODO TODO >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        Properties are different:
            if type(item) == property,
            getattr(item, '__get__').__self__ is a property object,
            with attributes fget, fset, fdel,
            and each of these yields the function to deal with (or None).
        """
        ## Equivalently,
        # for name in cls.__dict__:
        #     item = cls.__getattribute__(cls, name)

        # Convenience function
        _any_match = partial(any_match, fnmatch.fnmatchcase)

        for name, item in vars(cls).items():
            actual_item = getattr(cls, name)
            # If item is a staticmethod or classmethod,
            # actual_item is the underlying function;
            # if item is a function or class, actual_item is item.
            # In all these cases, actual_item is callable.
            # If item is a property, it's not callable, and actual_item is item.
            if not (callable(actual_item) or type(item) == property):
                continue

            #-------------------------------------------------------
            # Handle inner classes
            #-------------------------------------------------------
            if inspect.isclass(item):
                # item is an inner class.
                # decorate it, using self._changed_settings
                # Use sentinel 'DECO_OF' attribute on cls to get those
                deco_obj = getattr(item, self._sentinels['DECO_OF'], None)
                new_settings = self._changed_settings.copy()
                new_only = self._only
                new_omit = self._omit
                if deco_obj:    # cls is already decorated
                    # It IS already deco'd, so we want its settings to be
                    #    (copy of) self._changed_settings updated with its _changed_settings
                    new_settings.update(deco_obj._changed_settings)
                    # TODO / TRY THIS
                    # NOTICE WHAT THIS DOES:
                    # inner "only" is what was originally given IF SOMETHING WAS GIVEN
                    #     -- DON'T add outer ones -- otherwise, use the outer ones;
                    # inner "omit" is cumulative -- DO add outer ones
                    new_only = deco_obj._only or self._only
                    new_omit += deco_obj._omit

                new_class = self.__class__(
                    settings=new_settings,
                    only=new_only,
                    omit=new_omit
                )(item)
                # and replace in class dict
                setattr(cls, name, new_class)
                continue    # for name, item in ...

            #-------------------------------------------------------
            # Handle properties
            # Have to be able to omit or limit to only these.
            # TODO document, write tests for this!
            # Caller can specify, in omit or only parameters,
            #    property_name  (matches all prop fns, get set del)
            #    property_name + '.getter' or '.setter' or '.deleter'
            #    name of function supplied as fget, fset, fdel arg
            #        to property() function/constructor
            # and/or
            #    any of the above three, prefixed with class name
            #    (INCLUDING possibly inner function qualifiers,
            #     thus e.g. X.method.innerfunc.<locals>.Cls.prop.getter
            # If property_name is given, it matches any/all of the
            # property functions (get/set/del).
            #-------------------------------------------------------
            if type(item) == property:
                # item == actual_item is a property object,
                # also == getattr(item, '__get__').__self__ :)
                new_funcs = {}                    # or {'fget': None, 'fset': None, 'fdel': None}
                change = False
                for attr in self.PROP_SUFFIXES:   # ('fget', 'fset', 'fdel')
                    func = getattr(item, attr)
                    # put this func in new_funcs[attr]
                    # in case any change gets made. func == None is ok
                    new_funcs[attr] = func
                    if not func:
                        continue    # for attr in (...)

                    # Filter -- `omit` and `only`
                    # 4 maybe 6 names to check
                    # (4 cuz func.__name__ == name if @property and @propname.xxxer decos used)
                    dont_decorate = False
                    namelist = [pre + fn
                                for pre in ('',
                                            cls.__qualname__ + '.')
                                for fn in {name,                        # varies faster than pre
                                           name + '.' + self.PROP_SUFFIXES[attr],
                                           func.__name__}]
                    if _any_match(namelist, self._omit):
                        dont_decorate = True
                    if self._only and not _any_match(namelist, self._only):
                        dont_decorate = True

                    # get a fresh copy for each attr
                    new_settings = self._changed_settings.copy()    # updated below

                    # either func is deco'd, or it isn't
                    deco_obj = getattr(func, self._sentinels['DECO_OF'], None)

                    if dont_decorate:
                        if deco_obj:
                            new_funcs[attr] = deco_obj.f  # Undecorate
                            change = True
                        continue

                    if deco_obj:                        # it IS decorated
                        # Tweak its deco settings
                        new_settings.update(deco_obj._changed_settings)
                        # update func's settings (_force_mutable=True to handle `max_history` properly)
                        deco_obj._settings_mapping.update(new_settings, _force_mutable=True)
                        # ...
                        # and use same func ( = wrapper)
                        # We already did this above:
                        #   new_funcs[attr] = func
                    else:                              # not deco'd
                        # so decorate it
                        new_funcs[attr] = self.__class__(settings=new_settings)(func)
                        change = True

                # Make new property object if anything changed
                if change:
                    # Replace property object in cls
                    setattr(cls,
                            name,
                            property(new_funcs['fget'], new_funcs['fset'], new_funcs['fdel']))
                continue    # for name, item in ...

            #-------------------------------------------------------
            # Handle instance, static, class methods
            #-------------------------------------------------------
            # Filter with self._only and self._omit.
            dont_decorate = False
            namelist = [name, cls.__qualname__ + '.' + name]
            if _any_match(namelist, self._omit):
                dont_decorate = True
            if self._only and not _any_match(namelist, self._only):
                dont_decorate = True

            func = None
            if type(item) == staticmethod:
                func = actual_item              # == item.__func__
            elif type(item) == classmethod:
                func = actual_item.__func__     # == item.__func__
            elif inspect.isfunction(item):
                func = actual_item              # == item

            if not func:                        # nothing we're interested in (whatever it is)
                continue

            # It IS a method; func is the corresponding function
            deco_obj = getattr(func, self._sentinels['DECO_OF'], None)
            if dont_decorate:
                if deco_obj:
                    setattr(cls, name, deco_obj.f)  # Undecorate
                continue

            new_settings = self._changed_settings.copy()    # updated below

            # __init__ fixup, a nicety:
            # By default, don't log retval for __init__.
            # If user insists on it with 'log_retval=True' in __init__ deco,
            # that will override this.
            if name == '__init__':
                new_settings['log_retval'] = False

            if deco_obj:        # is func deco'd by this decorator?
                # Yes. Figure out settings for func,
                new_settings.update(deco_obj._changed_settings)
                # update func's settings (_force_mutable=True to handle `max_history` properly)
                deco_obj._settings_mapping.update(new_settings, _force_mutable=True)
            else:
                # func is not deco'd.
                # decorate it, using self._changed_settings
                new_func = self.__class__(settings=new_settings)(func)

                # if necessary, rewrap with @classmethod or @staticmethod
                if type(item) == staticmethod:
                    new_func = staticmethod(new_func)
                elif type(item) == classmethod:
                    new_func = classmethod(new_func)
                # and replace in class dict
                setattr(cls, name, new_func)

        return cls

    def __call__(self, f_or_cls):
        """Because there are decorator arguments, __call__() is called
        only once, and it can take only a single argument: the function
        to decorate. The return value of __call__ is called subsequently.
        So, this method *returns* the decorator proper.
        (~ Bruce Eckel in a book, ___) TODO ref.

        # 0.2.4.post5+ profiling (of record_history)

            setup_stackframe_hack         7.5 %
            up_to__not_enabled_call       3.3 %
            setup_context_init            1.2 %
            setup_context_inspect_bind   23.4 %
            setup_context_post_bind       8.8 %
            setup_context_kwargs_dicts   32.2 %
            pre_call_handlers             1.3 %
            post_call_handlers           22.3 %
        """
        #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*****
        # 0.3.0 -- handle decorating both functions and classes
        #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*****
        f = f_or_cls if inspect.isfunction(f_or_cls) else None
        cls = f_or_cls if inspect.isclass(f_or_cls) else None

        self.f = f
        self.cls = cls

        # Whether class or function, initialize sentinels (0.3.0 formerly in __init__)
        if not self.__class__._sentinels:
            self.__class__._sentinels = self._set_class_sentinels()

        if cls:
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*
            # 0.3.0 -- case "f_or_cls is a class" -- namely, cls
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*

            self.class__call__(cls)     # modifies cls
            # add attribute to cls: key is useful as sentinel, value is this deco
            setattr(
                cls,
                self._sentinels['DECO_OF'],
                self
            )
            return cls

        else:   # f
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*
            # 0.3.0 -- case "f_or_cls is a function" -- namely, f
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*

            # 0.3.0
            # Use __qualname__ ALL the time, unless user provides `name=display_name_str`
            # where `display_name_str` is either the name to be used for the fn in logged output,
            # or is an oldstyle format str into which f.__name__ will be substituted
            # to obtain the display name.
            # We require Py3.3+, so __qualname__ is available.

            # setup f_display_name
            if self._name_param:
                try:
                    self.f_display_name = (self._name_param % f.__name__)
                except TypeError:
                    self.f_display_name = self._name_param
            else:
                self.f_display_name = f.__qualname__

            self._classname_of_f = '.'.join( f.__qualname__.split('.')[:-1] )

            # Refuse to decorate '__repr__'s.
            # (Maybe don't need to do this,
            #  but it's a helluva lot easier to do it,
            #  less confusing for users too, and a very small price to pay.)
            if f.__name__ == '__repr__' and self._classname_of_f:
                return f

            #================================================================
            # 0.3.0 -- from else to here, stuff migrated from __init__
            #----------------------------------------------------------------
            #----------------------------------------------------------------
            # set up pseudo-dict (DecoSettingsMapping),
            # using settings given by self._effective_settings.
            #
            # *** DecoSettingsMapping "API" --
            # (2) construct DecoSettingsMapping object
            #     that will provide mapping & attribute access to settings, & more
            #----------------------------------------------------------------
            self._settings_mapping = DecoSettingsMapping(
                deco_class=self.__class__,
                # DecoSettingsMapping calls the rest ** values_dict
                ** self._effective_settings     # 0.3.0 set by __init__
            )

            #----------------------------------------------------------------
            # Init more stuff
            #----------------------------------------------------------------
            self._stats = ClassInstanceAttrProxy(class_instance=self)

            # Accessed by descriptors on the stats obj
            self._num_calls_total = 0
            self._num_calls_logged = 0
            # max_history > 0 --> size of self._call_history; <= 0 --> unbounded
            # Set before calling _make_call_history

            # 0.3.0 self._other_values_dict set by __init__
            self.max_history = self._other_values_dict.get('max_history', 0)  # <-- Nota bene
            self._call_history = self._make_call_history()

            # Accumulate this (for logged calls only)
            # even when record_history is false:
            self._elapsed_secs_logged = 0.0
            self._CPU_secs_logged = 0.0

            # 0.2.2.post1
            # stack(s), pushed & popped wrapper of deco'd function
            # by _logging_state_push, _logging_state_pop
            self._logging_fn = []     # stack
            self._indent_len = []     # stack
            self._output_fname = []   # stack
            self._enabled_stack = []  # # 0.3.0 - um, stack

            #----------------------------------------------------------------
            # 0.3.0 -- from else to here, stuff migrated from __init__
            #================================================================

            # Save signature and parameters of f
            self.f_signature = inspect.signature(f)     # Py >= 3.3
            self.f_params = self.f_signature.parameters

            # 0.3.0 We assume Py3.3 so we use perf_counter, process_time all the time
            wall_time_fn = time.perf_counter
            CPU_time_fn = time.process_time

            ##~ PROFILE
            # self.profile__ = OrderedDict((
            #     ('setup_stackframe_hack', []),
            #     ('up_to__not_enabled_call', []),
            #     ('setup_context_init', []),
            #     ('setup_context_inspect_bind', []),
            #     ('setup_context_post_bind', []),
            #     ('setup_context_kwargs_dicts', []),
            #     ('pre_call_handlers', []),
            #     ('post_call_handlers', []),
            # ))
            # END PROFILE

            @wraps(f)
            def f_log_calls_wrapper_(*args, **kwargs):
                """Wrapper around the wrapped function f.
                When this runs, f has been called, so we can now resolve
                any indirect values for the settings/keyword-params
                of log_calls, using info in kwargs and self.f_params."""
                # *** Part of the DecoSettingsMapping "API" --
                #     (4) using self._settings_mapping.get_final_value in wrapper
                # [[[ This/these is/are 4th chronologically ]]]

                # inner/local fn -- save a few cycles and characters -
                # we call this a lot (<= 9x).
                def _get_final_value(setting_name):
                    "Use outer scope's kwargs and self.f_params"
                    return self._settings_mapping.get_final_value(
                        setting_name, kwargs, fparams=self.f_params)

                ##~ PROFILE
                #~ with time_block('setup_stackframe_hack') as profile__setup_stackframe_hack:
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # if nothing to do, hurry up & don't do it.
                # NOTE: call_chain_to_next_log_calls_fn looks in stack frames
                # to find (0.2.4) _log_calls__active_call_items__ (really!)
                # It and its values (the following _XXX variables)
                # must be set before calling f.
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                _enabled = _get_final_value('enabled')
                # 0.3.0 in case f calls log_message (no output if f disabled)
                self._enabled_state_push(_enabled)

                # 0.2.4.post5 "true bypass": if 'enabled' < 0 then scram
                if _enabled < 0:
                    ret = f(*args, **kwargs)
                    self._enabled_state_pop()
                    return ret

                # Bump call counters, before calling fn.
                # Note: elapsed_secs, CPU_secs not reflected yet of course
                self._add_call(logged=_enabled)

                _log_call_numbers = _get_final_value('log_call_numbers')
                # counters just got bumped
                _active_call_number = (self._stats.num_calls_logged
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
                                       int(not not do_indent and not not _enabled))

                # Needed 3x:
                # 0.3.0
                ########## prefixed_fname = _get_final_value('prefix') + f.__name__
                prefixed_fname = _get_final_value('prefix') + self.f_display_name

                # Stackframe hack:
                _log_calls__active_call_items__ = {
                    '_enabled': _enabled,
                    '_log_call_numbers': _log_call_numbers,
                    '_prefixed_fname': prefixed_fname,          # Hack alert (Pt 1)
                    '_active_call_number': _active_call_number,
                    '_extra_indent_level': _extra_indent_level
                }
                # END profile__setup_stackframe_hack

                ##~ PROFILE
                #~ with time_block('up_to__not_enabled_call') as profile__up_to__not_enabled_call:
                # Get logging function IF ANY.
                # For the benefit of callees further down the call chain,
                # if this f is not enabled (_enabled <= 0).
                # Subclass can return None to suppress printed/logged output.
                logging_fn = self.get_logging_fn(_get_final_value)

                # Only do global indentation for print, not for loggers
                global_indent_len = max(_extra_indent_level, 0) * self.INDENT

                # 0.2.2.post1 - save output_fname for log_message use
                call_number_str = ((' [%d]' % _active_call_number)
                                   if _log_call_numbers else '')
                output_fname = prefixed_fname + call_number_str

                # 0.2.2 -- self._log_message() will use
                # the logging_fn, indent_len and output_fname at top of these stacks;
                # thus, verbose functions should use log_message to write their blather.
                # There are parallel stacks of these,
                # used by self._log_message(), maintained in this wrapper.
                self._logging_state_push(logging_fn, global_indent_len, output_fname)
                # END profile__up_to__not_enabled_call

                # (_xxx variables set, ok to call f)
                if not _enabled:
                    ret = f(*args, **kwargs)
                    self._logging_state_pop(enabled_too=True)
                    return ret

                ##~ PROFILE
                #~ with time_block('setup_context') as profile__setup_context_init:
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Set up context, for pre-call handlers
                # (after calling f, add to it for post-call handlers)
                # THIS is the time sink - 23x slower than other 'blocks'
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Key/values of "context" whose values we know so far:
                context = {
                    'decorator': self,
                    'settings': self._settings_mapping,
                    'stats': self._stats,
                    'prefixed_fname': prefixed_fname,
                    'fparams': self.f_params,
                    'call_list': call_list,
                    'args': args,
                    'kwargs': kwargs,
                    'indent': " " * self.INDENT,              # our unit of indentation
                    'output_fname': output_fname,
                    'stats': self._stats,
                }
                # END profile__setup_context_init

                ##~ PROFILE
                #~ with time_block('setup_context') as profile__setup_context_inspect_bind:
                # Gather all the things we need (for log output, & for history)
                # Use inspect module's Signature.bind method.
                # bound_args.arguments -- contains only explicitly bound arguments
                # 0.2.4.post5 - using
                #     inspect.signature(f).bind(*args, **kwargs)
                # took 45% of execution time of entire wrapper; this takes 23%:
                bound_args = self.f_signature.bind(*args, **kwargs)
                # END profile__setup_context_inspect_bind

                ##~ PROFILE
                #~ with time_block('setup_context') as profile__setup_context_post_bind:
                varargs_pos = get_args_pos(self.f_params)   # -1 if no *args in signature
                argcount = varargs_pos if varargs_pos >= 0 else len(args)
                context['argcount'] = argcount
                # The first argcount-many things in bound_args
                context['argnames'] = list(bound_args.arguments)[:argcount]
                context['argvals'] = args[:argcount]

                context['varargs'] = args[argcount:]
                (context['varargs_name'],
                 context['kwargs_name']) = get_args_kwargs_param_names(self.f_params)
                # END profile__setup_context_post_bind

                ##~ PROFILE
                #~ with time_block('setup_context') as profile__setup_context_kwargs_dicts:
                # These 3 statements = 31% of execution time of wrapper
                context['defaulted_kwargs'] = get_defaulted_kwargs_OD(self.f_params, bound_args)
                context['explicit_kwargs'] = get_explicit_kwargs_OD(self.f_params, bound_args, kwargs)
                # context['implicit_kwargs'] = {
                #     k: kwargs[k] for k in kwargs if k not in context['explicit_kwargs']
                # }
                # At least 2x as fast:
                context['implicit_kwargs'] = \
                    difference_update(kwargs.copy(), context['explicit_kwargs'])
                # END profile__setup_context_kwargs_dicts

                # 0.3.0
                mute = _get_final_value('mute')

                ##~ PROFILE
                #~ with time_block('pre_call_handlers') as profile__pre_call_handlers:
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Call pre-call handlers, collect nonempty return values
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if not mute:        # 0.3.0
                    pre_msgs = []
                    for setting_name in self._settings_mapping._pre_call_handlers:  # keys
                        if _get_final_value(setting_name):
                            info = self._settings_mapping._get_DecoSetting(setting_name)
                            msg = info.pre_call_handler(context)
                            if msg:
                                pre_msgs.append(msg)

                    # Write pre-call messages
                    if logging_fn:
                        for msg in pre_msgs:
                            self._log_message(msg, extra_indent_level=0)
                # END profile__pre_call_handlers

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Call f(*args, **kwargs) and get its retval; time it.
                # Add timestamp, elapsed time(s) and retval to context.
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # No dictionary overhead between timer(s) start & stop.
                t0 = time.time()                # for timestamp
                t0_wall = wall_time_fn()
                t0_CPU = CPU_time_fn()
                retval = f(*args, **kwargs)
                t_end_wall = wall_time_fn()
                t_end_CPU = CPU_time_fn()
                context['elapsed_secs'] = (t_end_wall - t0_wall)
                context['CPU_secs'] = (t_end_CPU - t0_CPU)
                context['timestamp'] = t0
                context['retval'] = retval

                self._add_to_elapsed(context['elapsed_secs'], context['CPU_secs'])

                ##~ PROFILE
                #~ with time_block('post_call_handlers') as profile__post_call_handlers:
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Call post-call handlers, collect nonempty return values
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if not mute:        # 0.3.0
                    post_msgs = []
                    for setting_name in self._settings_mapping._post_call_handlers:  # keys
                        if _get_final_value(setting_name):
                            info = self._settings_mapping._get_DecoSetting(setting_name)
                            msg = info.post_call_handler(context)
                            if msg:
                                post_msgs.append(msg)

                    # Write post-call messages
                    if logging_fn:
                        for msg in post_msgs:
                            self._log_message(msg, extra_indent_level=0)

                self._logging_state_pop(enabled_too=True)
                # END profile__post_call_handlers

                ##~ PROFILE
                # self.profile__['setup_stackframe_hack'].extend(profile__setup_stackframe_hack)
                # self.profile__['up_to__not_enabled_call'].extend(profile__up_to__not_enabled_call)
                # self.profile__['setup_context_init'].extend(profile__setup_context_init)
                # self.profile__['setup_context_inspect_bind'].extend(profile__setup_context_inspect_bind)
                # self.profile__['setup_context_post_bind'].extend(profile__setup_context_post_bind)
                # self.profile__['setup_context_kwargs_dicts'].extend(profile__setup_context_kwargs_dicts)
                # self.profile__['pre_call_handlers'].extend(profile__pre_call_handlers)
                # self.profile__['post_call_handlers'].extend(profile__post_call_handlers)
                #~ END PROFILE

                return retval

            # Add a sentinel as an attribute to f_log_calls_wrapper_
            # so we can in theory chase back to any previous log_calls-decorated fn
            setattr(
                f_log_calls_wrapper_,
                self._sentinels['SENTINEL_ATTR'],
                self._sentinels['SENTINEL_VAR']
            )
            # A back-pointer
            setattr(
                f,
                self._sentinels['WRAPPER_FN_OBJ'],
                f_log_calls_wrapper_
            )
            # 0.3.0 -- pointer to self
            setattr(
                f_log_calls_wrapper_,
                self._sentinels['DECO_OF'],
                self
            )
            # stats objects (attr of wrapper)
            setattr(
                f_log_calls_wrapper_,
                'stats',
                self._stats
            )
            ##~ PROFILE
            # setattr(
            #     f_log_calls_wrapper_,
            #     'profile__',
            #     self.profile__
            # )
            # END PROFILE

            setattr(
                f_log_calls_wrapper_,
                self.__class__.__name__ + '_settings',
                self._settings_mapping
            )
            # 0.2.1a
            setattr(
                f_log_calls_wrapper_,
                'log_message',
                self._log_message,
            )
            # 0.3.0
            setattr(
                f_log_calls_wrapper_,
                'log_exprs',
                self._log_exprs,
            )

            return f_log_calls_wrapper_
            #-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            # end else (case "f_or_cls is a function")
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*

    @classmethod
    def get_logging_fn(cls, _get_final_value_fn):
        return print

    @classmethod
    def call_chain_to_next_log_calls_fn(cls):
        """Return list of callers (names) on the call chain
        from caller of caller to first log_calls-deco'd function inclusive,
        if any. If there's no log_calls-deco'd function on the stack,
        or anyway if none are discernible, return [caller_of_caller]."""
        curr_frame = sys._getframe(2)   # caller-of-caller's frame

        call_list = []
        prev_indent_level = -1

        found = False
        found_enabled = False
        hit_bottom = False      # break both loops: reached <module>
        while not found_enabled and not hit_bottom:
            while 1:    # until found a deco'd fn or <module> reached
                curr_funcname = curr_frame.f_code.co_name
                if curr_funcname == 'f_log_calls_wrapper_':
                    # Previous was decorated inner fn; overwrite 'f_log_calls_wrapper_'
                    # print("**** found f_log_calls_wrapper_, prev fn name =", call_list[-1])     # <<<DEBUG>>>
                    # Fixup: get name of wrapped function
                    inner_fn = curr_frame.f_locals['f']
                    call_list[-1] = inner_fn.__name__       # ~ placeholder

                    wrapper_frame = curr_frame
                    found = True
                    break   # inner loop

                call_list.append(curr_funcname)

                if curr_funcname == '<module>':
                    hit_bottom = True
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
                if hasattr(curr_fn, cls._sentinels['SENTINEL_ATTR']):
                    found = True
                    break   # inner loop

                curr_frame = curr_frame.f_back

            # If found, then call_list[-1] is log_calls-wrapped
            if found:
                # Look in stack frame (!) for (0.2.4) _log_calls__active_call_items__
                # and use its values
                #   _enabled, _log_call_numbers, _active_call_number, _extra_indent_level, _prefixed_fname
                if wrapper_frame.f_locals.get('_log_calls__active_call_items__'):
                    active_call_items = wrapper_frame.f_locals['_log_calls__active_call_items__']
                    enabled = active_call_items['_enabled']     # it's >= 0
                    log_call_numbers = active_call_items['_log_call_numbers']
                    active_call_number = active_call_items['_active_call_number']
                    call_list[-1] = active_call_items['_prefixed_fname']   # Hack alert (Pt 3)

                    # only change prev_indent_level once, for nearest deco'd fn
                    if prev_indent_level < 0:
                        prev_indent_level = active_call_items['_extra_indent_level']

                    if enabled and log_call_numbers:
                        call_list[-1] += " [" + str(active_call_number) + "]"
                    found_enabled = enabled     # done with outer loop too if enabled
                else:   # bypassed
                    enabled = False

                if not enabled:
                    curr_frame = curr_frame.f_back
            else:   # not found
                # if not found, truncate call_list to first element.
                hit_bottom = True

        if hit_bottom:
            call_list = call_list[:1]
        return call_list, prev_indent_level


#----------------------------------------------------------------------------
# log_calls
#----------------------------------------------------------------------------
class log_calls(_deco_base):
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
        file:              If `logger` is `None`, a stream (an instance of type `io.TextIOBase`)
                           to which `log_calls` will print its messages. This value is
                           supplied to the `file` keyword parameter of the `print` function.
                           (Default: sys.stdout)
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
    # *** DecoSettingsMapping "API" --
    # (1) initialize: call register_class_settings

    # allow indirection for all except prefix and max_history, which also isn't mutable
    _setting_info_list = (
        DecoSettingEnabled('enabled'),
        DecoSetting_str('args_sep',          str,            ', ',          allow_falsy=False),
        DecoSettingArgs('log_args'),
        DecoSettingRetval('log_retval'),
        DecoSettingElapsed('log_elapsed'),
        DecoSettingExit('log_exit'),
        DecoSetting_bool('indent',           bool,           False,         allow_falsy=True),
        DecoSetting_bool('log_call_numbers', bool,           False,         allow_falsy=True),
        DecoSetting_str('prefix',            str,            '',            allow_falsy=True,
                        allow_indirect=False, mutable=True),    # 0.3.0; was mutable=False

        DecoSettingFile('file',              io.TextIOBase,  None,          allow_falsy=True),
        DecoSettingLogger('logger',          (logging.Logger,
                                              str),          None,          allow_falsy=True),
        DecoSetting_int('loglevel',          int,            logging.DEBUG, allow_falsy=False),
        DecoSetting_int('mute',              int,            False,         allow_falsy=True,
                        allow_indirect=False, mutable=True),
        DecoSettingHistory('record_history'),
        DecoSetting_int('max_history',       int,            0,             allow_falsy=True,
                        allow_indirect=False, mutable=False),
    )
    DecoSettingsMapping.register_class_settings('log_calls',    # name of this class. DRY - oh well.
                                                _setting_info_list)

    @used_unused_keywords()
    def __init__(self,
                 settings=None,     # 0.2.4.post2. A dict or a pathname
                 omit=tuple(),      # 0.3.0 class deco'ing: omit these methods or properties; not a setting
                 only=tuple(),      # 0.3.0 class deco'ing: deco only these methods or props (sans any in omit); not a setting
                 name=None,         # 0.3.0 name or oldstyle fmt str for f_display_name of fn; not a setting
                 enabled=True,
                 args_sep=', ',
                 log_args=True,
                 log_retval=False,
                 log_elapsed=False,
                 log_exit=True,
                 indent=False,         # probably better than =True
                 log_call_numbers=False,
                 prefix='',
                 file=None,    # detectable value so we late-bind to sys.stdout
                 logger=None,
                 loglevel=logging.DEBUG,
                 mute=False,
                 record_history=False,
                 max_history=0,
    ):
        """(See class docstring)
        0.3.0
        omit=tuple()
            When decorating a class, specifies the methods that will NOT be decorated.
            As for `field_names` parameter of namedtuples:
                a single string with each name separated by whitespace and/or commas,
                    for example 'x y' or 'x, y',
                or a tuple/list/sequence of strings.
            The strings themselves can be globs, i.e. can contain wildcards:
                Pattern Meaning
                * 	    matches everything
                ? 	    matches any single character
                [seq] 	matches any character in seq
                [!seq] 	matches any character not in seq
            * and ? can match dots, seq can be a range e.g. 0-9, a-z
            Matching is case-sensitive, of course.

            See https://docs.python.org/3/library/fnmatch.html

            Can be class-prefixed e.g. C.f, or D.DI.foo,
            or unprefixed (and then any matching method outermost or inner classes
            will be omitted).
            Ignored when decorating a function.

        only=tuple()
            As for `field_names` parameter of namedtuples:
                a single string with each name separated by whitespace and/or commas,
                    for example 'x y' or 'x, y',
                or a tuple/list/sequence of strings.
            When decorating a class, ONLY this/these methods, minus any in omit,
            will be decorated.
            Can be class-prefixed e.g. D.DI.foo,
            or unprefixed (and then any matching method outermost or inner classes
            will be deco'd).
            Ignored when decorating a function.
        name
            We now use __qualname__ ALL the time as the display name of a function or method
            (the name used for the fn in logged output),
            UNLESS the user provides `name=display_name_str`
            where `display_name_str` is either the name to be used for the fn in logged output,
            or is an oldstyle format str into which f.__name__ will be substituted
            to obtain the display name.
            Useful e.g. to suppress the clutter of qualnames of inner functions and methods:
            to use just, say, "inner_fn" instead of "outer_fn.<locals>.inner_fn",
            supply `name='%s'`.
            Ignored when decorating a class.
        """
        # 0.2.4 settings stuff:
        # determine which keyword arguments were actually passed by caller!
        used_keywords_dict = log_calls.__dict__['__init__'].get_used_keywords()
        for kwd in ('settings', 'omit', 'only', 'name'):
            if kwd in used_keywords_dict:
                del used_keywords_dict[kwd]

        super().__init__(
            settings=settings,
            _omit=omit,             # 0.3.0 class deco'ing: tuple - omit these methods/inner classes
            _only=only,             # 0.3.0 class deco'ing: tuple - decorate only these methods/inner classes (sans omit)
            _name_param=name,       # 0.3.0 name or oldstyle fmt str etc.
            _used_keywords_dict=used_keywords_dict,
            enabled=enabled,
            args_sep=args_sep,
            log_args=log_args,
            log_retval=log_retval,
            log_elapsed=log_elapsed,
            log_exit=log_exit,
            indent=indent,
            log_call_numbers=log_call_numbers,
            prefix=prefix,
            file=file,
            logger=logger,
            loglevel=loglevel,
            mute=mute,
            record_history=record_history,
            max_history=max_history,
        )

    @classmethod
    def get_logging_fn(cls, _get_final_value_fn):
        """Return logging_fn or None.
        cls: unused. Present so this method can be overridden."""
        outfile = _get_final_value_fn('file')
        if not outfile:
            outfile = sys.stdout    # possibly rebound by doctest

        logger = _get_final_value_fn('logger')
        # 0.2.4 logger can also be a name of a logger
        if logger and isinstance(logger, str):  # not None, not ''
            # We can't first check f there IS such a logger.
            # This creates one (with no handlers) if it doesn't exist:
            logger = logging.getLogger(logger)
        # If logger has no handlers then it can't write anything,
        # so we'll fall back on print
        if logger and not logger.hasHandlers():
            logger = None
        loglevel = _get_final_value_fn('loglevel')
        # Establish logging function
        logging_fn = (partial(logger.log, loglevel)
                      if logger else
                      lambda msg: print(msg, file=outfile, flush=True))
#                      lambda *pargs, **pkwargs: print(*pargs, file=outfile, flush=True, **pkwargs))
        # 0.2.4 - Everybody can indent.
        # loggers: just use formatters with '%(message)s'.
        return logging_fn
