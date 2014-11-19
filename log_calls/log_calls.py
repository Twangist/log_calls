__author__ = "Brian O'Neill"  # BTO
__version__ = '0.2.4b1'
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
import os  #.path.join(...)
import io   # so we can refer to io.TextIOBase
import time
import datetime
from collections import namedtuple, OrderedDict, deque

from .deco_settings import DecoSetting, DecoSettingsMapping
from .helpers import (get_args_pos, get_args_kwargs_param_names,
                      dict_to_sorted_str, prefix_multiline_str)
from .proxy_descriptors import ClassInstanceAttrProxy

__all__ = ['log_calls', 'record_history', '__version__', '__author__']


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
        'elapsed_secs',
        'timestamp',
        'prefixed_func_name',
        # caller_chain: list of fn names, the last possibly a "prefixed name".
        # From most-recent (immediate caller) to least-recent if len > 1.
        'caller_chain',
    )
)


#-----------------------------------------------------------------------------
# DecoSetting subclasses with pre-call handlers.
# The `context` arg for pre_call_handler methods has these keys:
#     decorator
#     settings      # of decorator
#     indent
#     prefixed_fname
#     output_fname
#     fparams
#     argcount
#     argnames      # argcount-long
#     argvals       # argcount-long
#     varargs
#     explicit_kwargs
#     implicit_kwargs
#     defaulted_kwargs
#     call_list
#     args
#     kwargs
#-----------------------------------------------------------------------------

class DecoSettingEnabled(DecoSetting):
    def __init__(self, name, **kwargs):
        super().__init__(name, int, False, allow_falsy=True, **kwargs)

    def pre_call_handler(self, context):
        return ("%s <== called by %s"
                % (context['output_fname'],
                   ' <== '.join(context['call_list'])))


class DecoSettingArgs(DecoSetting):
    def __init__(self, name, **kwargs):
        super().__init__(name, bool, True, allow_falsy=True, **kwargs)

    def pre_call_handler(self, context: dict):
        """Alert:
        this class's handler knows the keyword of another handler,
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

        # A convenience function
        def map_to_arg_eq_val_strs(pairs):
            return map(lambda pair: '%s=%r' % pair, pairs)

        args_vals = list(zip(context['argnames'], context['argvals']))

        if context['varargs']:
            args_vals.append( ("[*]%s" % context['varargs_name'], context['varargs']) )

        args_vals.extend( context['explicit_kwargs'].items() )

        if context['implicit_kwargs']:
            args_vals.append( ("[**]%s" % context['kwargs_name'],  context['implicit_kwargs']) )

        if args_vals:
            #msg += args_sep.join('%s=%r' % pair for pair in args_vals)
            msg += args_sep.join(
                        map_to_arg_eq_val_strs(args_vals))
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
#     timestamp
#     retval
#-----------------------------------------------------------------------------

class DecoSettingRetval(DecoSetting):
    MAXLEN_RETVALS = 77

    def __init__(self, name, **kwargs):
        super().__init__(name, bool, False, allow_falsy=True, **kwargs)

    def post_call_handler(self, context: dict):
        retval_str = str(context['retval'])
        if len(retval_str) > self.MAXLEN_RETVALS:
            retval_str = retval_str[:self.MAXLEN_RETVALS] + "..."
        return (context['indent'] +
                "%s return value: %s" % (context['output_fname'], retval_str))


class DecoSettingElapsed(DecoSetting):
    def __init__(self, name, **kwargs):
        super().__init__(name, bool, False, allow_falsy=True, **kwargs)

    def post_call_handler(self, context: dict):
        return (context['indent'] +
                "elapsed time: %f [secs]" % context['elapsed_secs'])


class DecoSettingExit(DecoSetting):
    def __init__(self, name, **kwargs):
        super().__init__(name, bool, True, allow_falsy=True, **kwargs)

    def post_call_handler(self, context: dict):
        return ("%s ==> returning to %s"
                   % (context['output_fname'],
                      ' ==> '.join(context['call_list'])))


class DecoSettingHistory(DecoSetting):
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
            timestamp_secs=context['timestamp'],
            prefixed_func_name=context['prefixed_fname'],
            caller_chain=context['call_list']
        )
        return None


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
    # sentinels, for identifying functions on the calls stack
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    _sentinels_proto = {
        'SENTINEL_ATTR': '$_%s_sentinel_',        # name of attr
        'SENTINEL_VAR': "$_%s-deco'd",
        'PREFIXED_NAME': '$f_%s-prefixed-name',     # name of attr
        'WRAPPER_FN_OBJ': '$f_%s_wrapper_-BACKPTR'  # LATE ADDITION
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
    #     DecoSetting('indent',           bool,           False,         allow_falsy=True),
    #     DecoSetting('log_call_numbers', bool,           False,         allow_falsy=True),
    #     DecoSetting('prefix',           str,            '',            allow_falsy=True,  allow_indirect=False),
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
        # REDONE: This value is accumulated for logged calls
        # whether or not history is being recorded.
        return self._elapsed_secs_logged

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

        self.max_history = int(max_history)  # set before calling _make_call_history
        self._call_history = self._make_call_history()
        self._settings_mapping.__setitem__('max_history', max_history, _force_mutable=True)

    def _add_call(self, *, logged):
        self._num_calls_total += 1
        if logged:
            self._num_calls_logged += 1

    def _add_to_elapsed(self, elapsed_secs):
        self._elapsed_secs_logged += elapsed_secs

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
        """Only called for *logged* calls, with record_history true.
        Call counters are already bumped."""
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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # __init__, __call__
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self,
                 settings_loc='',      # 0.2.4 new parameter, but NOT a "setting"
                 enabled=True,
                 log_call_numbers=False,
                 indent=False,
                 prefix='',
                 ** other_values_dict):
        """(See class docstring)"""
        # 0.2.4 TODO - settings from file would get totally blown away by update
        if settings_loc:
            d = self._read_settings_file(settings_loc=settings_loc)
        else:
            d = {}
            d.update(
                enabled=enabled,
                log_call_numbers=log_call_numbers,
                indent=indent,
                prefix=prefix,
                ** other_values_dict
            )
        # Set up pseudo-dict
        #
        # *** DecoSettingsMapping "API" --
        # (2) construct DecoSettingsMapping object
        #     that will provide mapping & attribute access to settings, & more
        self._settings_mapping = DecoSettingsMapping(
            deco_class=self.__class__,
            # DecoSettingsMapping calls the rest ** values_dict
            ** d
        )

        if not self.__class__._sentinels:
            self.__class__._sentinels = self._set_class_sentinels()

        self._stats = ClassInstanceAttrProxy(class_instance=self)

        # Accessed by descriptors on the stats obj
        self._num_calls_total = 0
        self._num_calls_logged = 0
        # max_history > 0 --> size of self._call_history; <= 0 --> unbounded
        # Set before calling _make_call_history
        self.max_history = other_values_dict.get('max_history', 0)  # <-- Nota bene
        self._call_history = self._make_call_history()

        # Accumulate this (for logged calls only)
        # even when record_history is false:
        self._elapsed_secs_logged = 0.0

        self.f_params = None    # set properly by __call__
        self.f = None           # set properly by __call__
        self.prefix = prefix    # special case

        # 0.2.2.post1
        # stack(s), pushed & popped by decorator (in wrapper of deco'd function)
        self._logging_fn = []     # stack
        self._indent_len = []     # stack
        self._output_fname = []     # stack

    def _logging_state_push(self, logging_fn, global_indent_len, output_fname):
        # self._logging_fn "stack" will have at one element
        if not self._logging_fn:
            self._logging_fn.append(logging_fn)
        self._indent_len.append(global_indent_len)
        self._output_fname.append(output_fname)

    def _logging_state_pop(self):
        # self._logging_fn "stack" will have at one element
        # Pop _indent_len or _output_fname first, test for emptiness
        self._indent_len.pop()
        if not self._indent_len:      # stack is becoming empty
            self._logging_fn.pop()
        self._output_fname.pop()

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

    def _read_settings_file(self, settings_loc=''):
        """If settings_loc names a file that exists,
        load settings from that file.
        If settings_loc names a directory, load settings from
            settings_loc + '.' + self.__class__.__name__
            e.g. the file '.log_calls' in directory specified by settings_loc.
        If not settings_loc or it doesn't exist, return {}.
        Format of file - zero or more lines of the form:
            setting_name=setting_value.

        Note: self._settings_mapping doesn't exist yet!
              so this function can't use it, e.g. to test for valid settings
                    if setting in self._settings_mapping: ...
        """
        if not settings_loc:
            return {}

        if os.path.isdir(settings_loc):
            settings_loc = os.path.join(settings_loc, '.' + self.__class__.__name__)
        if not os.path.isfile(settings_loc):
            return {}

        d = {}      # returned
        try:
            with open(settings_loc) as f:
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
                # TODO: report error?
                continue                                # bad line
            setting = setting.strip()
            val_txt = val_txt.strip()

            if setting not in settings_dict:
                continue

            # special case: None
            if val_txt == 'None':
                if settings_dict[setting].allow_falsy:
                    d[setting] = None
                continue

            # If val_txt ends in '=' (indirect value) then let val = val_txt;
            # otherwise, figure out *the* final type, favoring str if val_txt is enclosed in quotes;
            # apply the final type to val_txt to get val
            QUOTES = {"'", '"'}
            val_is_str = len(val_txt) >= 2 and val_txt[0] == val_txt[-1] and val_txt[0] in QUOTES
            if val_is_str:
                val_txt = val_txt[1:-1]

            if val_txt and val_txt[-1] == '=':          # indirect value
                val = val_txt
            else:
                final_type = settings_dict[setting].final_type
                # Set one_final_type
                if isinstance(final_type, tuple):
                    one_final_type = str if (str in final_type and val_is_str) else final_type[0]
                else:
                    one_final_type = final_type

                try:
                    val = one_final_type(val_txt)
                except BaseException:                   # SyntaxError - what else?
                    # TODO: report error?
                    continue                            # bad line

            d[setting] = val

        return d

    def __call__(self, f):
        """Because there are decorator arguments, __call__() is called
        only once, and it can take only a single argument: the function
        to decorate. The return value of __call__ is called subsequently.
        So, this method *returns* the decorator proper.
        (~ Bruce Eckel in a book, ___) TODO ref"""
        # First, save prefix + function name for function f
        prefixed_fname = self.prefix + f.__name__
        # Might as well save f too
        self.f = f
        # in addition to its parameters
        self.f_params = inspect.signature(f).parameters

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

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # if nothing to do, hurry up & don't do it.
            # NOTE: call_chain_to_next_log_calls_fn looks in stack frames
            # to find these next 4 _xxx variables (really!)
            # They must be set before calling f.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            _do_it = _get_final_value('enabled')
            # Bump call counters, before calling fn.
            # Note: elapsed_secs not reflected yet of course
            self._add_call(logged=_do_it)

            _log_call_numbers = _get_final_value('log_call_numbers')
            # counters just got bumped
            _active_call_number = (self._stats.num_calls_logged
                                   if _log_call_numbers else
                                   0)
            _prefixed_fname = prefixed_fname        # TODO Hack alert (Pt 1)

            # Get list of callers up to & including first log_call's-deco'd fn
            # (or just caller, if no such fn)
            call_list, prev_indent_level = self.call_chain_to_next_log_calls_fn()

            # Bump _extra_indent_level if last fn on call_list is deco'd AND enabled,
            # o/w it's the _extra_indent_level which that fn 'inherited'.
            # _extra_indent_level: prev_indent_level, or prev_indent_level + 1
            do_indent = _get_final_value('indent')
            _extra_indent_level = (prev_indent_level +
                                   int(not not do_indent and not not _do_it))

            # Get logging function IF ANY.
            # For the benefit of callees further down the call chain,
            # if this f is not enabled (not _do_it).
            # Subclass can return None to suppress printed/logged output.
            # "can_indent" - in log_calls, True iff logging_fn does NOT use a Logger.
            logging_fn = self.get_logging_fn(_get_final_value)

            # Only do global indentation for print, not for loggers
            global_indent_len = max(_extra_indent_level, 0) * self.INDENT

            # 0.2.2.post1 - save output_fname for log_message use
            call_number_str = ((' [%d]' % _active_call_number)
                               if _log_call_numbers else '')
            output_fname = prefixed_fname + call_number_str

            # 0.2.2 -- self._log_message() will use
            # the _logging_fn and _indent_len on top of these stacks:
            # So verbose functions should use THIS to write their blather.
            # There's stack of these, or parallel stacks of these,
            # used by self._log_message(), maintained in this wrapper.
            self._logging_state_push(logging_fn, global_indent_len, output_fname)

            # (_xxx variables set, ok to call f)
            if not _do_it:
                ret = f(*args, **kwargs)
                self._logging_state_pop()
                return ret

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Set up context, for pre-call handlers
            # (after calling f, add to it for post-call handlers)
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
            }

            # Gather all the things we need (for log output, & for history)
            # Use inspect module's Signature.bind method.
            # bound_args.arguments -- contains only explicitly bound arguments
            bound_args = inspect.signature(f).bind(*args, **kwargs)
            varargs_pos = get_args_pos(self.f_params)   # -1 if no *args in signature
            argcount = varargs_pos if varargs_pos >= 0 else len(args)
            context['argcount'] = argcount
            # The first argcount-many things in bound_args
            context['argnames'] = list(bound_args.arguments)[:argcount]
            context['argvals'] = args[:argcount]

            context['varargs'] = args[argcount:]
            (context['varargs_name'],
             context['kwargs_name']) = get_args_kwargs_param_names(self.f_params)

            context['defaulted_kwargs'] = OrderedDict(
                [(param.name, param.default)
                 for param in self.f_params.values()
                 if param.name not in bound_args.arguments
                 and param.default != inspect._empty
                ]
            )
            context['explicit_kwargs'] = OrderedDict(
                [(k, kwargs[k])
                 for k in self.f_params
                 if k in bound_args.arguments and k in kwargs]
            )
            context['implicit_kwargs'] = {
                k: kwargs[k] for k in kwargs if k not in context['explicit_kwargs']
            }
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Call pre-call handlers, collect nonempty return values
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Call f(*args, **kwargs) and get its retval; time it.
            # Add timestamp, elapsed time and retval to context.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # No dictionary overhead between timer start & stop.
            t0 = time.time()
            retval = f(*args, **kwargs)
            context['elapsed_secs'] = (time.time() - t0)
            context['retval'] = retval
            context['timestamp'] = t0

            self._add_to_elapsed(context['elapsed_secs'])

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Call post-call handlers, collect nonempty return values
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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

            self._logging_state_pop()

            return retval

        # Add a sentinel as an attribute to f_log_calls_wrapper_
        # so we can in theory chase back to any previous log_calls-decorated fn
        setattr(
            f_log_calls_wrapper_,
            self._sentinels['SENTINEL_ATTR'],
            self._sentinels['SENTINEL_VAR']
        )
        # Add prefixed name of f as an attribute
        setattr(
            f,      # revert to f, after trying f_log_calls_wrapper_
            self._sentinels['PREFIXED_NAME'],
            prefixed_fname
        )
        # LATE ADDITION: A back-pointer
        setattr(
            f,
            self._sentinels['WRAPPER_FN_OBJ'],
            f_log_calls_wrapper_
        )
        setattr(
            f_log_calls_wrapper_,
            'stats',
            self._stats
        )

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
        return f_log_calls_wrapper_

    @classmethod
    def get_logging_fn(cls, _get_final_value_fn) -> tuple:
        return print

    @classmethod
    def call_chain_to_next_log_calls_fn(cls):
        """Return list of callers (names) on the call chain
        from caller of caller to first log_calls-deco'd function inclusive,
        if any.  If there's no log_calls-deco'd function on the stack,
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
                    # Previous was decorated inner fn; don't add 'f_log_calls_wrapper_'
                    # print("**** found f_log_calls_wrapper_, prev fn name =", call_list[-1])     # <<<DEBUG>>>
                    # Fixup: get prefixed named of wrapped function
                    inner_fn = curr_frame.f_locals['f']
                    # TODO: (Hack alert (Pt 2)) This doesn't always work --
                    # todo      B_meta.__prepare__ <== called by A_meta.__prepare__
                    # todo  but
                    # todo      B_meta.__new__ <== called by __new__
                    # todo  __prepare__, classmethod; __new__, staticmethod.
                    # todo Hence the workaround (_prefixed_fname variable in stackframe;
                    # todo see above & below)
                    call_list[-1] = getattr(inner_fn,
                                            cls._sentinels['PREFIXED_NAME'])
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
                # look in stack frame (!) for
                #   _do_it, _log_call_numbers, _active_call_number, _extra_indent_level, _prefixed
                enabled = wrapper_frame.f_locals['_do_it']
                log_call_numbers = wrapper_frame.f_locals['_log_call_numbers']
                active_call_number = wrapper_frame.f_locals['_active_call_number']
                prefixed_fname_from_stack = wrapper_frame.f_locals['_prefixed_fname']   # TODO Hack alert (Pt 3)
                if prefixed_fname_from_stack:                                           # TODO: DOH? this should always be non-false
                    call_list[-1] = prefixed_fname_from_stack

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
                hit_bottom = True

        if hit_bottom:
            call_list = call_list[:1]
        return call_list, prev_indent_level


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
        DecoSetting('args_sep',         str,            ', ',          allow_falsy=False),
        DecoSettingArgs('log_args'),
        DecoSettingRetval('log_retval'),
        DecoSettingElapsed('log_elapsed'),
        DecoSettingExit('log_exit'),
        DecoSetting('indent',           bool,           False,         allow_falsy=True),
        DecoSetting('log_call_numbers', bool,           False,         allow_falsy=True),
        DecoSetting('prefix',           str,            '',            allow_falsy=True,  allow_indirect=False),
        DecoSetting('file',             io.TextIOBase,  None,          allow_falsy=True),
        DecoSetting('logger',           (logging.Logger,
                                         str),          None,          allow_falsy=True),
        DecoSetting('loglevel',         int,            logging.DEBUG, allow_falsy=False),
        DecoSettingHistory('record_history'),
        DecoSetting('max_history',      int,            0,             allow_falsy=True, allow_indirect=False, mutable=False),
    )
    DecoSettingsMapping.register_class_settings('log_calls',    # name of this class. DRY - oh well.
                                                _setting_info_list)

    def __init__(self,
                 settings_loc='',      # 0.2.4. TODO: document (new parameter, but NOT a "setting")
                 enabled=True,
                 args_sep=', ',
                 log_args=True,
                 log_retval=False,
                 log_elapsed=False,
                 log_exit=True,
                 indent=False,   # probably better than =True
                 log_call_numbers=False,
                 prefix='',
                 file=None,      # detectable value so we late-bind to sys.stdout
                 logger=None,
                 loglevel=logging.DEBUG,
                 record_history=False,
                 max_history=0,
    ):
        """(See class docstring)"""
        # # TODO: First, figure out which of our billion parameters were NOT supplied
        # # by the actual call - the 'defaulted' arguments
        # init_params = inspect.signature(f).parameters
        # bound_args = inspect.signature(f).bind(*args, **kwargs)
        #
        # defaulted_kwargs = [
        #     param.name
        #     for param in f_params.values()
        #      if param.name not in bound_args.arguments
        #      and param.default != inspect._empty
        # ]

        super().__init__(
                         settings_loc=settings_loc,
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
                         record_history=record_history,
                         max_history=max_history,
        )

    @classmethod
    def get_logging_fn(cls, _get_final_value_fn) -> tuple:
        """Return logging_fn or None.
        cls: unused. Present so this method can be overridden."""
        outfile = _get_final_value_fn('file')
        if not outfile:
            outfile = sys.stdout    # possibly rebound by doctest

        logger = _get_final_value_fn('logger')
        # 0.2.4 logger can also be a name of a logger
        if logger and isinstance(logger, str):  # not None, not ''
            logger = logging.getLogger(logger)
        loglevel = _get_final_value_fn('loglevel')
        # Establish logging function
        logging_fn = (partial(logger.log, loglevel)
                      if logger else
                      lambda msg: print(msg, file=outfile, flush=True))
#                      lambda *pargs, **pkwargs: print(*pargs, file=outfile, flush=True, **pkwargs))
        # 0.2.4 - Everybody can indent.
        # loggers - just use formatters with '%(message)s'.
        return logging_fn
