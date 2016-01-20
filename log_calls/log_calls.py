__author__ = "Brian O'Neill"  # BTO
__version__ = '0.3.0b18'
__doc__ = """
Configurable decorator for debugging and profiling that writes
caller name(s), args+values, function return values, execution time,
number of call, to stdout or to a logger. log_calls can track
call history and provide it in CSV format and Pandas DataFrame format.
NOTE: for CPython only -- this uses internals of stack frames
      which may well differ in other interpreters.
See docs/log_calls.md for details, usage info and examples.

Argument logging is based on the Python 2 decorator:
    https://wiki.python.org/moin/PythonDecoratorLibrary#Easy_Dump_of_Function_Arguments
with changes for Py3 and several enhancements, as described in docs/log_calls.md.
"""
import inspect
import functools
from functools import wraps, partial
import logging
import sys
import os
import io   # so we can refer to io.TextIOBase
import time
import datetime
from collections import namedtuple, deque, OrderedDict

import fnmatch  # 0.3.0 for omit, only

from .deco_settings import (DecoSetting,
                            DecoSetting_bool, DecoSetting_int, DecoSetting_str,
                            DecoSettingsMapping)
from .helpers import (no_duplicates, get_args_pos, get_args_kwargs_param_names,
                      difference_update, restrict_keys,
                      get_defaulted_kwargs_OD, get_explicit_kwargs_OD,
                      dict_to_sorted_str, prefix_multiline_str,
                      is_quoted_str, any_match)
from .proxy_descriptors import ClassInstanceAttrProxy
from .used_unused_kwds import used_unused_keywords

__all__ = ['log_calls', 'CallRecord', '__version__', '__author__']


#-----------------------------------------------------------------------------
# DecoSetting subclasses with pre-call handlers.
# The `context` arg for pre_call_handler methods has these keys:
#     decorator
#     settings              # self._deco_settings     (of decorator)
#     stats                 # self._stats             ("      "    )
#     prefixed_fname
#     fparams
#     call_list
#     args
#     kwargs
#     indent
#     output_fname          # prefixed_fname + possibly num_calls_logged (if log_call_numbers true)
#
#     argcount
#     argnames              # argcount-long
#     argvals               # argcount-long
#     varargs
#     varargs_name
#     kwargs_name
#     defaulted_kwargs
#     explicit_kwargs
#     implicit_kwargs
#-----------------------------------------------------------------------------

# TODO 0.3.x, possible `context` setting:  - - - - - - - - - - - - - - - - - -
# todo  context key/vals that might be of interest to wrapped functions:
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


# #### v0.3.0b18
# def my_recursive_repr(fillvalue='...'):
#     'Decorator to make a repr function return fillvalue for a recursive call'
#
#     def decorating_function(user_function):
#         repr_running = set()
#
#         def wrapper(self):
#             key = id(self), -1          # -1 == get_ident()
#             if key in repr_running:
#                 return fillvalue
#             repr_running.add(key)
#             try:
#                 result = user_function()    # BTO: user_function(self)
#             finally:
#                 repr_running.discard(key)
#             return result
#
#         # Can't use functools.wraps() here because of bootstrap issues
#         wrapper.__module__ = getattr(user_function, '__module__', None)
#         wrapper.__doc__ = getattr(user_function, '__doc__', '')
#         wrapper.__name__ = getattr(user_function, '__name__', '')
#         # BTO: only customization is adding defaults for the above 3 getattr calls
#         #      so they don't blow up if e.g. user_function has no attr '__module__'
#         wrapper.__annotations__ = getattr(user_function, '__annotations__', {})
#         return wrapper
#
#     return decorating_function

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
                    #### Note, formerly:
                    arg_eq_val_str = '%s=%r' % pair

                    #### .  v0.3.0b18 BEGIN Guard against recursive reprs

                    # f = my_recursive_repr()       # f == decorating_function
                    # method_wrapper = getattr(val, '__repr__')
                    # g = f(method_wrapper)   # g == decorating_function(user_function)
                    #                         #   == wrapper(self)
                    # safe_repr_p1 = g(val)
                    #
                    # format_str = '%s=%r' if isinstance(val, str) else '%s=%s'
                    # arg_eq_val_str = format_str % (arg, safe_repr_p1)
                    # #### .  v0.3.0b18 END.

                arg_eq_val_strs.append(arg_eq_val_str)

            return arg_eq_val_strs

        args_vals = list(zip(context['argnames'], context['argvals']))

        if context['varargs']:
            args_vals.append( ("*%s" % context['varargs_name'], context['varargs']) )

        args_vals.extend( context['explicit_kwargs'].items() )

        if context['implicit_kwargs']:
            args_vals.append( ("**%s" % context['kwargs_name'], context['implicit_kwargs']) )

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
#     process_secs
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
                "elapsed time: %f [secs], process time: %f [secs]"
                % (context['elapsed_secs'], context['process_secs']))


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
            process_secs=context['process_secs'],
            timestamp_secs=context['timestamp'],
            prefixed_func_name=context['prefixed_fname'],
            caller_chain=context['call_list']
        )
        return None


#-----------------------------------------------------------------------------
# DecoSetting subclasses overriding value_from_str and has_acceptable_type
#-----------------------------------------------------------------------------

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
# CallRecord namedtuple, for history
#-----------------------------------------------------------------------------

CallRecord = namedtuple(
    "CallRecord",
    (
        'call_num',
        'argnames', 'argvals',
        'varargs',
        'explicit_kwargs', 'defaulted_kwargs', 'implicit_kwargs',
        'retval',
        'elapsed_secs', 'process_secs',
        'timestamp',
        'prefixed_func_name',
        # caller_chain: list of fn names, possibly "prefixed".
        # From most-recent (immediate caller) to least-recent if len > 1.
        'caller_chain',
    )
)


#-----------------------------------------------------------------------------
# useful lil lookup tables
#-----------------------------------------------------------------------------

# OrderedDicts instead of dicts for the sake of
# tests of <cls>.log_calls_omit, <cls>.log_calls_only
PROPERTY_USER_SUFFIXES_to_ATTRS = OrderedDict(
    (('getter', 'fget'),
     ('setter', 'fset'),
     ('deleter', 'fdel')) )

# Keys: attributes of properties;
# Vals: what users can suffix prop names with in omit & only lists
PROPERTY_ATTRS_to_USER_SUFFIXES = OrderedDict(
    (('fget', 'getter'),
     ('fset', 'setter'),
     ('fdel', 'deleter')) )

# Name of *** local variable *** of _deco_base_f_wrapper_,
# accessed by callstack-chaseback routine and (0.3.0) _get_own_deco_wrapper
STACKFRAME_HACK_DICT_NAME = '_deco_base__active_call_items__'

#-----------------------------------------------------------------------------
# _get_underlying_function
#-----------------------------------------------------------------------------
def _get_underlying_function(item, actual_item):
    """Factors out some code used 2x, in _get_deco_wrapper and in _deco_base._class__call__
    For some class cls, and some name,
    :param item:           vars(cls)[name] == cls.__dict__[name]
    :param actual_item:    getattr(cls, name)
    :return: func, as per body
    """
    func = None
    if type(item) == staticmethod:
        func = actual_item              # == item.__func__
    elif type(item) == classmethod:
        func = actual_item.__func__     # == item.__func__
    elif inspect.isfunction(item):
        func = actual_item              # == item
    return func


#-----------------------------------------------------------------------------
# _get_own_deco_wrapper
#-----------------------------------------------------------------------------
def _get_own_deco_wrapper(deco_class, cls) -> "function":
    """Return deco wrapper of  caller of caller of caller,
    IFF
    caller of caller is deco'd   # return *that*
    Note:
    cls is deco'd, otherwise it wouldn't have a <clsname> + '_wrapper' attr
    through which to call _get_deco_wrapper :)

    Raise ValueError on error
    """
    # Error messages. We append a code to better determine cause of error.
    ERR_NOT_DECORATED = "'%s' is not decorated [%d]"
    ERR_BYPASSED_OR_NOT_DECORATED = "'%s' is true-bypassed (enabled < 0) or not decorated [%d]"
    ERR_INCONSISTENT_DECO = "inconsistent %s decorator object for '%s' [%d]"
    # caller is function whose wrapper we want
    # ITs caller should be the wrapper
    func_frame = sys._getframe(1)
    code = func_frame.f_code
    funcname = code.co_name

    wrapper_frame = func_frame.f_back
    wrapper_funcname = wrapper_frame.f_code.co_name

    # wrapper_funcname should be '_deco_base_f_wrapper_'
    if wrapper_funcname != '_deco_base_f_wrapper_':
        raise ValueError(ERR_NOT_DECORATED % (funcname, 1))

    # look in its f_locals :) [stackframe hack] for STACKFRAME_HACK_DICT_NAME
    hack_dict = wrapper_frame.f_locals.get(STACKFRAME_HACK_DICT_NAME, None)
    if not hack_dict:
        raise ValueError(ERR_BYPASSED_OR_NOT_DECORATED % (funcname, 2))
    # value for key '_wrapper_deco' is the deco object
    try:
        deco_obj = hack_dict['_wrapper_deco']
    except (TypeError, KeyError):
        deco_obj = None
    if not (deco_obj and type(deco_obj) == deco_class):
        raise ValueError(ERR_NOT_DECORATED % (funcname, 3))

    # we've almost surely found a true wrapper
    try:
        wrapped_f = deco_obj.f
    except AttributeError:
        raise ValueError(ERR_INCONSISTENT_DECO % (deco_class.__name__, funcname, 4))
    # more consistency checks:
    # wrapped_f nonempty and has same name and identical code to our function
    if not wrapped_f:
        raise ValueError(ERR_INCONSISTENT_DECO % (deco_class.__name__, funcname, 5))
    if not (funcname == wrapped_f.__name__ and
            wrapped_f.__code__ is code):
        raise ValueError(ERR_INCONSISTENT_DECO % (deco_class.__name__, funcname, 6))

    # access its attr deco_obj._sentinels['WRAPPER_FN_OBJ'] --
    # THAT, at long last, is (alllmost surely) the wrapper
    wrapper = getattr(wrapped_f, deco_obj._sentinels['WRAPPER_FN_OBJ'], None)
    # if wrapper is None then getattr returns None, so != deco_obj
    if deco_obj != getattr(wrapper, deco_obj._sentinels['DECO_OF'], None):
        raise ValueError(ERR_INCONSISTENT_DECO % (deco_class.__name__, funcname, 7))

    return wrapper


#-----------------------------------------------------------------------------
# _get_deco_wrapper
# classmethod(partial(_get_deco_wrapper, deco_class))
# added as attribute '<deco_name>_wrapper' to decorated classes,
# so that they can easily access the added attributes
# of methods and properties.
# <deco_name> = 'log_calls', 'record_history', ...
#-----------------------------------------------------------------------------

# @used_unused_keywords()
def _get_deco_wrapper(deco_class, cls, fname: str) -> "function":
    """
    deco_class: log_calls, record_history, ...
    cls is (supposed to be) a decorated class.
    fname is name of a method (instance, static or class),
    or name of a property (and then, we return the getter),
    or name of a property + '.getter' or + '.setter' or + '.deleter'
    Note: if a property is defined using the `property` constructor
    as in
        x = property(getx, setx, delx)
    where getx, setx, delx are methods of a class (or None),
    then e.g. setx can be accessed via either e.g.
        x.log_calls_wrapper('setx')
    or
        x.log_calls_wrapper('x.setter')
    where x is a decorated class or an instance thereof.

    No need for qualnames. If A is decorated and has an inner class I,
    then I is decorated too, so use A.I.log_calls_wrapper(fname)

    Return wrapper if fname is decorated, None if it isn't;
    raise exception if fname is crazy or doesn't exist in cls or etc.

    Raise ValueError or TypeError on error:
    ValueError
    Raised when a built-in operation or function receives an argument
    that has the right type but an inappropriate value, and the situation
    is not described by a more precise exception such as IndexError.
    """
    sentinel = deco_class._sentinels['DECO_OF']

    if not isinstance(fname, str):
        raise TypeError("expecting str for argument 'fname', got %r of type %s"
                        % (fname, type(fname).__name__))

    parts = fname.split('.')
    if len(parts) > 2:
        raise ValueError("no such method specifier '%s'" % fname)
    prop_suffix = None
    if len(parts) == 2:
        fname, prop_suffix = parts
        if not (fname and prop_suffix):
            raise ValueError("bad method specifier '%s.%s'"
                             % (fname, prop_suffix))

    cls_dict = cls.__dict__     # = vars(cls) but faster
    if fname not in cls_dict:
        raise ValueError("class '%s' has no such attribute as '%s'"
                         % (cls.__name__, fname))
    item = cls_dict[fname]
    # Guard against '.getter' etc appended to non-properties,
    # unknown things appended to property names
    # surely these deserves complaints (exceptions)
    if prop_suffix:
        if type(item) != property:
            raise ValueError("%s.%s -- '%s' is not a property of class '%s'"
                             % (fname, prop_suffix, fname, cls.__name__))
        if prop_suffix not in PROPERTY_USER_SUFFIXES_to_ATTRS:
            raise ValueError("%s.%s -- unknown qualifier '%s'"
                             % (fname, prop_suffix, prop_suffix))
    actual_item = getattr(cls, fname)
    func = _get_underlying_function(item, actual_item)
    if func:
        # func is an instance-, class- or static-method
        # Return func if it's a deco wrapper, else return None
        return func if getattr(func, sentinel, None) else None

    # not func: item isn't any kind of method.
    # If it's not a property either, raise error
    if type(item) != property:
        raise TypeError("item '%s' of class '%s' is of type '%s' and can't be decorated"
                        % (fname, cls.__name__, type(item).__name__))

    # item is a property
    if not prop_suffix:
        # unqualified property name ==> we assume the user means the 'getter'
        prop_suffix = 'getter'
    func = getattr(item, PROPERTY_USER_SUFFIXES_to_ATTRS[prop_suffix])
    if func:
        return func if getattr(func, sentinel, None) else None
    else:
        # property has no such attribute (no 'setter', for example)
        raise ValueError("property '%s' has no '%s' in class '%s'"
                         % (fname, prop_suffix, cls.__name__))


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
# _deco_base
# Fat base class for log_calls and record_history decorators
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

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
                           and not using a logger (default: True (0.3.0))
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
                                   value <= 0 --> unboundedly many records are stored

        <<<<<<< TODO -- more............. >>>>>>>
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # constants for the `mute` setting
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    class MUTE():
        NOTHING = False     # (default -- all output produced)
        CALLS = True        # (mute output from decorated functions & methods & properties,
                            #  but log_message and thus log_exprs produce output;
                            #  call # recording, history recording continue if enabled)
        ALL = 2             # (no output at all; but call # recording, history recording continue if enabled)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # sentinels, for identifying functions on the calls stack
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    _sentinels_proto = {
        'SENTINEL_ATTR': '_$_%s_sentinel_',             # name of attr
        'SENTINEL_VAR': "_$_%s-deco'd",
        'WRAPPER_FN_OBJ': '_$_f_%s_wrapper_-BACKPTR',   # LATE ADDITION
        'DECO_OF': '_$_f_%s_wrapper_-or-cls-DECO'       # value = self (0.3.0)
    }

    _version = __version__

    @classmethod
    def version(cls):
        return cls._version

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
    #     # and (example args; record_history adds visible=False):
    #     DecoSetting(       'mute',             int,  False, allow_falsy=True,  allow_indirect=False)
    # )
    # DecoSettingsMapping.register_class_settings('_deco_base',
    #                                             _setting_info_list)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # call history and stats stuff
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    _data_descriptor_names = (
        'num_calls_logged',
        'num_calls_total',
        'elapsed_secs_logged',
        'process_secs_logged',
        'history',
        'history_as_csv',
        'history_as_DataFrame',
    )
    _method_descriptor_names = (
        'clear_history',
    )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # virtual classmethods
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def get_logging_fn(cls, _get_final_value_fn):
        return print

    # 0.3.0
    @classmethod
    def allow_repr(cls) -> bool:
        """Subclass must say yay or nay"""
        raise NotImplementedError

    # 0.3.0
    @classmethod
    def fixup_for_init(cls, some_settings: dict):
        """Default: do nothing"""
        return

    # 0.3.0
    @classmethod
    def global_mute(cls) -> bool:
        """Default: False (never globally muted)"""
        return False

    #----------------------------------------------------------------
    # history stuff
    #----------------------------------------------------------------
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
    def process_secs_logged(self):
        # This value is accumulated for logged calls
        # whether or not history is being recorded.
        return self._process_secs_logged

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
            process_secs
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
        fields.extend(['retval', 'elapsed_secs', 'process_secs', 'timestamp', 'prefixed_fname', 'caller_chain'])
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
            fields.append(str(rec.process_secs))
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
        self._process_secs_logged = 0.0

        self.max_history = int(max_history)  # set before calling _make_call_history
        self._call_history = self._make_call_history()
        self._settings_mapping.__setitem__('max_history', max_history, _force_mutable=True)

    def _add_call(self, *, logged):
        self._num_calls_total += 1
        if logged:
            self._num_calls_logged += 1

    def _add_to_elapsed(self, elapsed_secs, process_secs):
        self._elapsed_secs_logged += elapsed_secs
        self._process_secs_logged += process_secs

    def _add_to_history(self,
                        argnames, argvals,
                        varargs,
                        explicit_kwargs, defaulted_kwargs, implicit_kwargs,
                        retval,
                        elapsed_secs, process_secs,
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
                    elapsed_secs, process_secs,
                    timestamp,
                    prefixed_func_name=prefixed_func_name,
                    caller_chain=caller_chain)
        )

    #----------------------------------------------------------------
    # log_* output methods
    #----------------------------------------------------------------
    # 0.3.0
    LoggingState = namedtuple("LoggingState",
                              ('logging_fn',
                               'indent_len',
                               'output_fname',
                               'mute'))

    # 0.3.0
    def _enabled_state_push(self, enabled):
        self._enabled_stack.append(enabled)

    # 0.3.0
    def _enabled_state_pop(self):
        self._enabled_stack.pop()

    def _logging_state_push(self, logging_fn, global_indent_len, output_fname, mute):
        self.logging_state_stack.append(
            self.LoggingState(logging_fn, global_indent_len, output_fname, mute)
        )

    def _logging_state_pop(self, enabled_too=False):
        self.logging_state_stack.pop()
        if enabled_too:
            self._enabled_state_pop()

    def _log_exprs(self, *exprs,
                   sep=', ',
                   extra_indent_level=1,
                   prefix_with_name=False,
                   prefix=''):
        """Evaluates each expression (str) in exprs in the context of the caller;
        makes string from each, expr = val,
        pass those strs to _log_message.
        :param exprs: exprs to evaluate and log with value
        :param sep: default ', '
        :param extra_indent_level: as for _log_message
        :param prefix_with_name: as for _log_message
        :param prefix: additional text to prepend to output message
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
                          prefix_with_name=prefix_with_name,
                          _prefix=prefix)

    def _log_message(self, msg, *msgs,
                     sep=' ',
                     extra_indent_level=1,
                     prefix_with_name=False,
                     _prefix=''):
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

        _prefix: for log_exprs, callers of log_message won't need to use it
                 additional text to prepend to output message
        """
        # do nothing unless enabled! if disabled, the other 'stack' accesses will blow up
        if self._enabled_stack[-1] <= 0:    # disabled
            return

        # 0.3.0
        logging_state = self.logging_state_stack[-1]
        # Write nothing if output is stifled (caller is NOT _deco_base_f_wrapper_)
        # NOTE: only check global_mute() IN REALTIME, like so:
        mute = max(logging_state.mute, self.global_mute())
        if mute == self.MUTE.ALL:
            return
        # adjust for calls not being logged -- don't indent an extra level
        #  (no 'log_calls frame', no 'arguments:' to align with),
        #  and prefix with display name cuz there's no log_calls "frame"
        # NOTE, In this case we force "prefix_with_name = True" <<<
        ####if mute == self.MUTE.CALLS:
        if mute >= self.log_message_auto_prefix_threshold():
            extra_indent_level -= 1
            prefix_with_name = True

        indent_len = (logging_state.indent_len +
                      + (extra_indent_level * self.INDENT)
                     )
        if indent_len < 0:
            indent_len = 0   # clamp
        the_msgs = (msg,) + msgs
        the_msg = sep.join(map(str, the_msgs))
        if prefix_with_name:
            the_msg = logging_state.output_fname + ': ' + the_msg
        if _prefix:
            the_msg = _prefix + the_msg
        logging_state.logging_fn(prefix_multiline_str(' ' * indent_len, the_msg))

    #----------------------------------------------------------------
    # settings
    #----------------------------------------------------------------

    @classmethod
    def reset_defaults(cls):
        DecoSettingsMapping.reset_defaults(cls.__name__)

    @classmethod
    def _get_settings_dict(cls, *,
                           settings=None,
                           deco_settings_keys=None,
                           extra_settings_dict=None
                          ) -> dict:
        """Get settings from dict or read settings from file, if given, as a dict;
        update that dict with any settings from extra_settings_dict, and return the result.
        :param settings: dict, or str as for _read_settings_file (or None)
        :param deco_settings_keys: seq or set of keys naming settings for this deco class `cls`
        :param extra_settings_dict: more settings, restricted to deco_settings_keys (any others ignored)
        :return:
        """
        if not deco_settings_keys:
            deco_settings_keys = set(DecoSettingsMapping.get_deco_class_settings_dict(cls.__name__))

        settings_dict = {}
        if isinstance(settings, dict):
            settings_dict = restrict_keys(settings, deco_settings_keys)
        elif isinstance(settings, str):
            settings_dict = cls._read_settings_file(settings_path=settings)

        if extra_settings_dict:
            settings_dict.update(extra_settings_dict)

        return settings_dict

    @classmethod
    def set_defaults(cls, settings=None, ** more_defaults):
        """
        :param settings: a dict,
                         or a str specifying a "settings file"
                            such as _read_settings_file accepts (its `settings_path` parameter):
                                *  a directory name (dir containing settings file '.' + self.__class__.__name__),
                                *  or a path to a (text) settings file
        :param more_defaults: keyword params where every key is a "setting".
                              These override any default settings provided by `settings` if it's nonempty
        :return:
        """
        d = cls._get_settings_dict(settings=settings,
                                   extra_settings_dict=more_defaults)
        DecoSettingsMapping.set_defaults(cls.__name__, d)

    @classmethod
    def _read_settings_file(cls, settings_path=''):
        """If settings_path names a file that exists,
        load settings from that file.
        If settings_path names a directory, load settings from
            settings_path + '.' + cls.__name__
            e.g. the file '.log_calls' in directory specified by settings_path.
        If not settings_path or it doesn't exist, return {}.
        Format of settings file - zero or more lines of the form:
            setting_name=setting_value
        with possible whitespace around *_name.
        Blank lines are ok & ignored; lines whose first non-whitespace char is '#'
        are treated as comments & ignored.

        v0.3.0 -- special-case handling for pseudo-setting `NO_DECO`
        """
        if not settings_path:
            return {}

        if os.path.isdir(settings_path):
            settings_path = os.path.join(settings_path, '.' + cls.__name__)
        if not os.path.isfile(settings_path):
            return {}

        d = {}      # returned
        try:
            with open(settings_path) as f:
                lines = f.readlines()
        except BaseException:   # FileNotFoundError?!
            return d

        settings_dict = DecoSettingsMapping.get_deco_class_settings_dict(cls.__name__)
        for line in lines:
            line = line.strip()
            # Allow blank lines & comments
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
    # & helpers
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self,
                 settings=None,
                 _omit=tuple(),             # 0.3.0 class deco'ing: str or seq - omit these methods/proper; not a setting
                 _only=tuple(),             # 0.3.0 class deco'ing: str or seq - deco only these (sans any in omit); not a setting
                 _name_param=None,          # 0.3.0 name or oldstyle fmt str for f_display_name of fn; not a setting
                 _override=False,           # 0.3.0b18: new settings override existing ones. NOT a "setting"
                 _used_keywords_dict={},    # 0.2.4 new parameter, but NOT a "setting"
                 enabled=True,
                 log_call_numbers=False,
                 indent=True,               # 0.3.0 changed default
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
        # Initialize effective_settings_dict with log_calls's defaults - the static ones:
        #   self.__class__.__name__ is name *of subclass*, clsname,
        #   which we trust has already called
        #     DecoSettingsMapping.register_class_settings(clsname, list-of-deco-setting-objs)
        #   Special-case handling of 'enabled' (ugh, eh), whose DecoSetting obj
        #   has .default = False, for "technical" reasons
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        deco_settings_map = DecoSettingsMapping.get_deco_class_settings_dict(self.__class__.__name__)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get settings from dict | read settings from file, if given, as a dict
        # Update with _used_keywords_dict, save as self._changed_settings,
        # so that these can be reapplied by any outer class deco --
        # (a copy of a class deco's _effective_settings is updated with these
        #  in class case of __call__)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self._changed_settings = self._get_settings_dict(
            settings=settings,
            deco_settings_keys=set(deco_settings_map),
            extra_settings_dict=_used_keywords_dict
        )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Initialize effective_settings_dict with log_calls's defaults - the static ones.
        #
        # update effective_settings_dict with settings *explicitly* passed to caller
        # of subclass's __init__, and save *that* (used in __call__)
        # as self._effective_settings, which are the final settings used
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        effective_settings_dict = {k: deco_settings_map[k].default for k in deco_settings_map}
        effective_settings_dict['enabled'] = True
        effective_settings_dict.update(self._changed_settings)
        self._effective_settings = effective_settings_dict

        def _make_token_sequence(names) -> tuple:
            """names is either a string of space- and/or comma-separated umm tokens,
            or is already a sequence of tokens.
            Return tuple of tokens."""
            if isinstance(names, str):
                names = names.replace(',', ' ').split()
            return tuple(map(str, names))

        self._omit_ex = self._omit = _make_token_sequence(_omit)
        self._only_ex = self._only = _make_token_sequence(_only)

        self.prefix = prefix                # special case
        self._name_param = _name_param
        self._other_values_dict = other_values_dict     # 0.3.0

        self._override = _override                      # 0.3.0b18

        # initialize sentinel strings
        if not self.__class__._sentinels:
            self.__class__._sentinels = self._set_class_sentinels()

        # 0.3.0 Factored out rest of __init__ to function case of __call__

    @property
    def omit(self): return self._omit_ex

    @property
    def only(self): return self._only_ex

    @staticmethod
    def _is_a_function_in_class(xname, cls) -> bool:
        if xname in cls.__dict__:
            # Get 'raw' item for xname from cls;
            # if it's a function, return True
            xitem = cls.__getattribute__(cls, xname)
            if inspect.isfunction(xitem):
                return True
        return False

    def _add_property_method_names(self, cls, method_specs: tuple) -> tuple:
        """For each name in method_specs (a tuple),
        if name is of the form propertyname.suffix
        where suffix is in ('getter', 'setter', 'deleter'),
        add to method_specs the name of the corresponding function
        (.fget, .fset, .fdel) of attribute with name propertyname,
        provided that function is in the class dict and is a function.

        More generally, a name in method_specs is of the form
            expr [. suffix]
        where expr is a method or property name, possibly prefixed
        by classname + '.', AND WHICH MAY CONTAIN WILDCARDS AND
        CHARACTER RANGES (to match or reject). Classname can name
        inner classes & so can contain dots; Wildcards can match dot.
        Wildcards/chart classes are as in "globs" --
        matching is done with fnmatch.fnmatchcase.

        :param cls: class being deco'd, some of whose methods/fns
                    are in method_specs
        :param method_specs: self._omit or self._only
                             members are names of methods/fns,
                             or propertyname.suffix as described above
        :return: tuple - method_specs_ex, consisting of the method specs
                 in method_specs, each followed by any & all added
                 property functions, with no duplicates
        """
        cls_prefix = cls.__qualname__ + '.'

        # Make list/collection of properties in cls,
        #   plus their names
        # Note that item.__qualname__ == cls_prefix + item.__name__
        cls_properties = []
        for name, item in cls.__dict__.items():
            if type(item) == property:
                # properties don't HAVE __name__s or __qualname__s
                cls_properties.append((name, item))

        # return value; method_specs_ex will contain method_specs
        method_specs_ex = []

        for method_spec in method_specs:
            method_specs_ex.append(method_spec)     # method_specs_ex contains method_specs
            dot_pos = method_spec.rfind('.')

            suffix = ''
            if dot_pos != -1:
                suffix = method_spec[dot_pos+1:]

            if suffix in PROPERTY_USER_SUFFIXES_to_ATTRS:
                pattern = method_spec[:dot_pos]
                suffixes = (suffix,)
            else:
                pattern = method_spec
                suffixes = tuple(PROPERTY_USER_SUFFIXES_to_ATTRS.keys())

            matching_props_suffixes_and_flags = []
            for name, prop in cls_properties:
                for sfx in suffixes:
                    if fnmatch.fnmatchcase(name, pattern):
                        matching_props_suffixes_and_flags.append((prop, sfx, False))
                    elif fnmatch.fnmatchcase(cls_prefix + name, pattern):
                        matching_props_suffixes_and_flags.append((prop, sfx, True))

            if not matching_props_suffixes_and_flags:
                continue

            # For each (prop, sfx, matches_qualname) in matching_props_suffixes_and_flags,
            # get attribute (function) of prop corresponds to sfx;
            # if it exists & is a function in cls, add its matching name
            # (its .__name__ if not matches_qualname, else cls_prefix + its .__name__)
            for prop, sfx, matches_qualname in matching_props_suffixes_and_flags:
                func = getattr(prop, PROPERTY_USER_SUFFIXES_to_ATTRS[sfx], None)
                if not func:
                    continue
                # Is func, by name, actually a function of class cls?
                # (This is false if @property etc decos were used to create prop,
                #  true if property ctor was used.)
                # If so, add its (possibly cls-prefix'd) name to list
                func_name = func.__name__
                if self._is_a_function_in_class(func_name, cls):
                    if matches_qualname:
                        func_name = cls_prefix + func_name
                    method_specs_ex.append(func_name)

        return tuple(no_duplicates(method_specs_ex))

    ### 0.3.0b18
    def _update_settings(self, new: dict, old: dict, override_existing: bool):
        new.update({k: v
                   for (k,v) in old.items()
                   if (not override_existing or k not in old)
                  })

    def _class__call__(self, klass):
        """
        :param klass: class to decorate ALL the methods of,
                    including properties and methods of inner classes.
        :return: decorated class (klass - modified/operated on)
        Operate on each function in klass.
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

            THEN make its settings = self._effective_settings (for this klass)
                updated with those deco_obj._changed_settings

        otherwise, (a non-wrapped function that will be an instance method)
            we already have the function.

        Properties are different:
            if type(item) == property,
            getattr(item, '__get__').__self__ is a property object,
            with attributes fget, fset, fdel,
            and each of these yields the function to deal with (or None).
        """

        # Convenience function
        _any_match = partial(any_match, fnmatch.fnmatchcase)

        # Fixup self._only, self._omit,
        # so that if a named method (function) of the class is specified
        # via propertyname.getter or .setter or .deleter
        # and then the method's name is added to the list too.
        # Otherwise, if the function gets enumerated after the property
        # in loop through klass.__dict__ below, it won't be recognized
        # by name as something to omit or decorate-only.
        self._omit_ex = self._add_property_method_names(klass, self._omit)
        self._only_ex = self._add_property_method_names(klass, self._only)

        ## Equivalently,
        # for name in klass.__dict__:
        #     item = klass.__getattribute__(klass, name)

        for name, item in klass.__dict__.items():
            actual_item = getattr(klass, name)
            # If item is a staticmethod or classmethod,
            # actual_item is the underlying function;
            # if item is a function (instance method) or class, actual_item is item.
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
                # Use sentinel 'DECO_OF' attribute on klass to get those
                new_settings = self._changed_settings.copy()
                new_only = self._only
                new_omit = self._omit
                deco_obj = getattr(item, self._sentinels['DECO_OF'], None)

                if deco_obj:    # klass is already decorated

                    # It IS already deco'd, so we want its settings to be
                    #    (copy of) self._changed_settings updated with its _changed_settings
                    ### 0.3.0b18 -- Use self._override
                    self._update_settings(new=new_settings,
                                          old=deco_obj._changed_settings,
                                          override_existing=self._override)
                    # NOTICE WHAT THIS DOES (if override == False):
                    # inner "only" is what was originally given IF SOMETHING WAS GIVEN
                    #     -- DON'T add outer ones -- otherwise, use the outer ones;
                    # inner "omit" is cumulative, union -- DO add outer ones
                    new_only = deco_obj._only or self._only
                    new_omit += deco_obj._omit

                new_class = self.__class__(
                    settings=new_settings,
                    only=new_only,
                    omit=new_omit
                )(item)
                # and replace in class dict
                setattr(klass, name, new_class)
                continue    # for name, item in ...

            #-------------------------------------------------------
            # Handle properties
            #
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
                for attr in PROPERTY_ATTRS_to_USER_SUFFIXES:   # ('fget', 'fset', 'fdel')
                    func = getattr(item, attr)
                    # put this func in new_funcs[attr]
                    # in case any change gets made. func == None is ok
                    new_funcs[attr] = func
                    if not func:
                        continue    # for attr in (...)

                    func_name = func.__name__

                    # Filter -- `omit` and `only`
                    # 4 maybe 6 names to check
                    # (4 cuz func.__name__ == name if @property and @propname.xxxer decos used)
                    dont_decorate = False
                    namelist = [pre + fn
                                for pre in ('',
                                            klass.__qualname__ + '.')
                                for fn in {name,                        # varies faster than pre
                                           name + '.' + PROPERTY_ATTRS_to_USER_SUFFIXES[attr],
                                           func_name}]
                    if _any_match(namelist, self._omit_ex):
                        dont_decorate = True
                    if self._only and not _any_match(namelist, self._only_ex):
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
                        ### 0.3.0b18 -- Use self._override
                        self._update_settings(new=new_settings,
                                              old=deco_obj._changed_settings,
                                              override_existing=self._override)
                        # update func's settings (_force_mutable=True to handle `max_history` properly)
                        deco_obj._settings_mapping.update(new_settings, _force_mutable=True)
                        # ...
                        # and use same func ( = wrapper)
                        # We already did this above:
                        #   new_funcs[attr] = func
                    else:                              # not deco'd
                        # so decorate it
                        new_func = self.__class__(** new_settings)(func)
                        # update property
                        new_funcs[attr] = new_func
                        # Possibly update klass definition of func with new_func
                        # NOTE: if `property` ctor used to create property (item),
                        # then func (its name) is in class dict, ** as a function **,
                        # BUT IT MAY NOT BE DECO'd YET: despite the order of declarations
                        # in the class body, we get them ~randomly via klass.__dict__.
                        # SO in that case we ALSO have to update klass with new decorated func,
                        # otherwise we'll create a another, new wrapper for it,
                        # and THAT will be found by log_calls_wrapper(func.__name__)
                        # but log_calls_wrapper(property_name + '.___ter') will find this wrapper,
                        # and bad things can happen (log_message can use "the other" wrapper).
                        # So: Is func also in class klass dict *** as a function ***?
                        # NOT the case if @property decorator used to create property (item),
                        # but it IS the case if some random methods (including func)
                        # have been fed to 'property' ctor to create the property.
                        if self._is_a_function_in_class(func_name, klass):
                            setattr(klass, func_name, new_func)
                        change = True

                # Make new property object if anything changed
                if change:
                    # Replace property object in klass
                    setattr(klass,
                            name,
                            property(new_funcs['fget'], new_funcs['fset'], new_funcs['fdel']))
                continue    # for name, item in ...

            #-------------------------------------------------------
            # Handle instance, static, class methods.
            # All we know is, actual_item is callable
            #-------------------------------------------------------
            # Filter with self._only and self._omit.
            dont_decorate = False
            namelist = [name, klass.__qualname__ + '.' + name]
            if _any_match(namelist, self._omit_ex):
                dont_decorate = True
            if self._only and not _any_match(namelist, self._only_ex):
                dont_decorate = True

            func = _get_underlying_function(item, actual_item)
            # not hasattr(func, '__name') and etc: assume it's <deco_name>_wrapper
            # SO if user creates a classmethod that's a partial,
            # it can't & won't be deco'd. No tragedy.
            if not func or (not hasattr(func, '__name__')
                            and type(func) == functools.partial
                            and type(item) == classmethod):  # nothing we're interested in (whatever it is)
                continue

            # It IS a method; func is the corresponding function
            deco_obj = getattr(func, self._sentinels['DECO_OF'], None)
            if dont_decorate:
                if deco_obj:
                    setattr(klass, name, deco_obj.f)  # Undecorate
                continue

            new_settings = self._changed_settings.copy()    # updated below

            # __init__ fixup, a nicety:
            # By default, don't log retval for __init__.
            # If user insists on it with 'log_retval=True' in __init__ deco,
            # that will override this.
            if name == '__init__':
                self.fixup_for_init(new_settings)

            if deco_obj:        # is func deco'd by this decorator?
                # Yes. Figure out settings for func,
                ### 0.3.0b18 -- Use self._override
                self._update_settings(new=new_settings,
                                      old=deco_obj._changed_settings,
                                      override_existing=self._override)
                # update func's settings (_force_mutable=True to handle `max_history` properly)
                deco_obj._settings_mapping.update(new_settings, _force_mutable=True)
# NOTE, 0.3.0b18 EXPERIMENT
# INSTEAD, :
#                 changed_settings = deco_obj._changed_settings.copy()
#                 changed_settings.update(new_settings)
#                 # update func's settings (_force_mutable=True to handle `max_history` properly)
#                 deco_obj._settings_mapping.update(changed_settings, _force_mutable=True)
# end NOTE, 0.3.0b18 EXPERIMENT

            else:
                # func is not deco'd.
                # decorate it, using self._changed_settings
                # record_history doesn't know from 'settings' param,
                # cuz it really doesn't need one, so instead we do:
                new_func = self.__class__(** new_settings)(func)

                # if necessary, rewrap with @classmethod or @staticmethod
                if type(item) == staticmethod:
                    new_func = staticmethod(new_func)
                elif type(item) == classmethod:
                    new_func = classmethod(new_func)
                # and replace in class dict
                setattr(klass, name, new_func)

        return klass

    def __call__(self, f_or_klass):
        """Because there are decorator arguments, __call__() is called
        only once, and it can take only a single argument: the function
        or class to decorate. The return value of __call__ is called
        subsequently. So, this method *returns* the decorator proper.
        (~ Bruce Eckel in a book, ___) TODO ref.
        """

        #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*****
        # 0.3.0
        # -- implement "kill switch", NO_DECO
        # -- handle decorating both functions and classes
        #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*****

        # 0.3.0b16: if it isn't callable, scram'
        if not callable(f_or_klass):
            return f_or_klass

        if self._effective_settings.get('NO_DECO'):
            return f_or_klass
        # else, delete that item wherever it might be
        if 'NO_DECO' in self._effective_settings:
            del self._effective_settings['NO_DECO']
        if 'NO_DECO' in self._changed_settings:
            del self._changed_settings['NO_DECO']

        f = f_or_klass if inspect.isfunction(f_or_klass) else None
        klass = f_or_klass if inspect.isclass(f_or_klass) else None

        self.f = f
        self.cls = klass

        if klass:
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*
            # 0.3.0 -- case "f_or_klass is a class" -- namely, klass
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*

            self._class__call__(klass)     # modifies klass (methods & inner classes)
            self._add_class_attrs(klass)
            return klass

        elif not f:
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*
            # 0.3.0 -- case "f_or_klass is a callable but not a function"
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*
            # functools.partial objects are callable, have no __name__ much less __qualname__,
            # and trying to deco __call__ gets messy.
            # Callable builtins e.g. len are not functions in the isfunction sense, can't deco anyway.
            # Just give up (quietly)
            return f_or_klass

        else:           # not a class, f nonempty is a function of f_or_klass callable
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*
            # 0.3.0 -- case "f_or_klass is a function" -- namely, f
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*

            #----------------------------------------------------------------
            # Don't double-decorate -- don't wanna, & it doesn't work anyway!
            #----------------------------------------------------------------
            # Note: As with methods of classes,
            # .    if f is deco'd, its existing EXPLICITLY GIVEN settings take precedence.

            # # From _class__call__, props & methods cases, w/a few name changes
            deco_obj = getattr(f, self._sentinels['DECO_OF'], None)     # type: _deco_base

            # get a fresh copy for each attr
            new_settings = self._changed_settings.copy()    # updated below

            # __init__ fixup, a nicety:
            # By default, don't log retval for __init__.
            # If user insists on it with 'log_retval=True' in __init__ deco,
            # that will override this.
            if f.__name__ == '__init__':
                self.fixup_for_init(new_settings)

            if deco_obj:        # f is deco'd by this decorator
                # Yes. Figure out settings for f,
                ### 0.3.0b18 -- Use self._override
                self._update_settings(new=new_settings,
                                      old=deco_obj._changed_settings,
                                      override_existing=self._override)
                # update func's settings (_force_mutable=True to handle `max_history` properly)
                deco_obj._settings_mapping.update(new_settings, _force_mutable=True)
                return f

            #----------------------------------------------------------------
            # f is a function & is NOT already deco'd
            #----------------------------------------------------------------

            # 0.3.0.x -- f may not have a .__qualname__
            try:
                self._classname_of_f = '.'.join( f.__qualname__.split('.')[:-1] )
            except AttributeError as e:
                # print("%s has no qualname: %s" % (f, str(e)))     # <<<<<<<<< TODO DELETE DEBUG; don't deco???
                self._classname_of_f = ''

            # Refuse to decorate '__repr__' if deco subclass doesn't allow it.
            if f.__name__ == '__repr__' and self._classname_of_f and not self.allow_repr():
                return f

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
            self._stats = ClassInstanceAttrProxy(
                            class_instance=self,
                            data_descriptor_names=self.__class__._data_descriptor_names,
                            method_descriptor_names=self.__class__._method_descriptor_names)
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
            self._process_secs_logged = 0.0

            # 0.2.2.post1
            # stack(s), pushed & popped wrapper of deco'd function
            # by _logging_state_push, _logging_state_pop
            # 0.3.0 convert to pushing/popping single namedtuples
            self.logging_state_stack = []    # 0.3.0 stack of LoggingState namedtuples
            self._enabled_stack = []         # 0.3.0 - um, stack, of 'enabled's

            #----------------------------------------------------------------
            # 0.3.0 -- from else to here, stuff migrated from __init__
            #================================================================

            # Save signature and parameters of f
            self.f_signature = inspect.signature(f)     # Py >= 3.3
            self.f_params = self.f_signature.parameters

            # 0.3.0 We assume Py3.3 so we use perf_counter, process_time all the time
            wall_time_fn = time.perf_counter
            process_time_fn = time.process_time

            @wraps(f)
            def _deco_base_f_wrapper_(*args, **kwargs):
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

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # if nothing to do, hurry up & don't do it.
                # NOTE: call_chain_to_next_log_calls_fn looks in stack frames
                # to find (0.2.4) STACKFRAME_HACK_DICT_NAME (really!)
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
                # Note: elapsed_secs, process_secs not reflected yet of course
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
                # 0.3.0
                ########## prefixed_fname = _get_final_value('prefix') + f.__name__
                prefixed_fname = _get_final_value('prefix') + self.f_display_name

                # Stackframe hack:
                assert '_deco_base__active_call_items__' == STACKFRAME_HACK_DICT_NAME
                _deco_base__active_call_items__ = {
                    '_enabled': _enabled,
                    '_log_call_numbers': _log_call_numbers,
                    '_prefixed_fname': prefixed_fname,          # Hack alert (Pt 1)
                    '_active_call_number': _active_call_number,
                    '_extra_indent_level': _extra_indent_level,
                    # 0.3.0 for _get_own_deco_wrapper
                    '_wrapper_deco': self
                }

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

                # 0.3.0
                # Note: DON'T combine with global_mute(),
                # cuz this value will be pushed,
                # and when popped any realtime changes to global mute
                # made during call to f would be ignored.
                mute = _get_final_value('mute')

                # 0.2.2 -- self._log_message() will use
                # the logging_fn, indent_len and output_fname at top of these stacks;
                # thus, verbose functions should use log_message to write their blather.
                # There's a stack of logging-state ,
                # used by self._log_message(), maintained in this wrapper.
                self._logging_state_push(logging_fn, global_indent_len, output_fname, mute)

                # (_xxx variables set, ok to call f)
                if not _enabled:
                    ret = f(*args, **kwargs)
                    self._logging_state_pop(enabled_too=True)
                    return ret

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
                }

                # Gather all the things we need (for log output, & for history)
                # Use inspect module's Signature.bind method.
                # bound_args.arguments -- contains only explicitly bound arguments
                # 0.2.4.post5 - using
                #     inspect.signature(f).bind(*args, **kwargs)
                # took 45% of execution time of entire wrapper; this takes 23%:
                bound_args = self.f_signature.bind(*args, **kwargs)

                varargs_pos = get_args_pos(self.f_params)   # -1 if no *args in signature
                argcount = varargs_pos if varargs_pos >= 0 else len(args)
                context['argcount'] = argcount
                # The first argcount-many things in bound_args
                context['argnames'] = list(bound_args.arguments)[:argcount]
                context['argvals'] = args[:argcount]

                context['varargs'] = args[argcount:]
                (context['varargs_name'],
                 context['kwargs_name']) = get_args_kwargs_param_names(self.f_params)

                # These 3 statements = 31% of execution time of wrapper
                context['defaulted_kwargs'] = get_defaulted_kwargs_OD(self.f_params, bound_args)
                context['explicit_kwargs'] = get_explicit_kwargs_OD(self.f_params, bound_args, kwargs)
                # context['implicit_kwargs'] = {
                #     k: kwargs[k] for k in kwargs if k not in context['explicit_kwargs']
                # }
                # At least 2x as fast:
                context['implicit_kwargs'] = \
                    difference_update(kwargs.copy(), context['explicit_kwargs'])

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Call pre-call handlers, collect nonempty return values
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # only consult global mute in r/t
                if not (mute or self.global_mute()):        # 0.3.0
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
                # Add timestamp, elapsed time(s) and retval to context.
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # No dictionary overhead between timer(s) start & stop.
                t0 = time.time()                # for timestamp
                t0_wall = wall_time_fn()
                t0_process = process_time_fn()
                retval = f(*args, **kwargs)
                t_end_wall = wall_time_fn()
                t_end_process = process_time_fn()
                context['elapsed_secs'] = (t_end_wall - t0_wall)
                context['process_secs'] = (t_end_process - t0_process)
                context['timestamp'] = t0
                context['retval'] = retval

                self._add_to_elapsed(context['elapsed_secs'], context['process_secs'])

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Call post-call handlers, collect nonempty return values
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # only consult global mute in r/t
                if not (mute or self.global_mute()):        # 0.3.0
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

                return retval

            self._add_function_attrs(f, _deco_base_f_wrapper_)
            return _deco_base_f_wrapper_

            #-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            # end else (case "f_or_klass is a function")
            #+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*

    def _add_function_attrs(self, f, f_wrapper):
            # Add a sentinel as an attribute to f_wrapper
            # so we can in theory chase back to any previous log_calls-decorated fn
            setattr(
                f_wrapper, self._sentinels['SENTINEL_ATTR'], self._sentinels['SENTINEL_VAR']
            )
            # A back-pointer
            setattr(
                f, self._sentinels['WRAPPER_FN_OBJ'], f_wrapper
            )
            # 0.3.0 -- pointer to self
            setattr(
                f_wrapper, self._sentinels['DECO_OF'], self
            )
            # stats objects (attr of wrapper)
            setattr(
                f_wrapper, 'stats', self._stats
            )
            setattr(
                f_wrapper, self.__class__.__name__ + '_settings', self._settings_mapping
            )
            # 0.2.1a
            setattr(
                f_wrapper, 'log_message', self._log_message,
            )
            # 0.3.0
            setattr(
                f_wrapper, 'log_exprs', self._log_exprs,
            )

    def _add_class_attrs(self, klass):
        # add attribute to klass: key is useful as sentinel, value is this deco
        setattr(
            klass,
            self._sentinels['DECO_OF'],
            self
        )
        # Make it easy for user to find the log_calls wrapper of a method,
        # given its name, via `get_log_calls_wrapper(fname)`
        # or `get_record_history_wrapper(fname)`
        # This can be called on a deco'd class or on an instance thereof.
        this_deco_class = self.__class__
        this_deco_class_name = this_deco_class.__name__
        setattr(
            klass,
            'get_' + this_deco_class_name + '_wrapper',
            classmethod(partial(_get_deco_wrapper, this_deco_class))
        )
        # Make it even easier for methods to find their own log_calls wrappers,
        # via `get_own_log_calls_wrapper(fname)`
        # or `get_own_record_history_wrapper(fname)`
        # This can be called on a deco'd class or on an instance thereof.
        this_deco_class = self.__class__
        setattr(
            klass,
            'get_own_' + this_deco_class_name + '_wrapper',
            classmethod(partial(_get_own_deco_wrapper, this_deco_class))
        )

        # largely for testing (by the time anyone gets to see these,
        # they're no longer used... 'cept outer class at class level
        # can manipulate inner classes' omit and only, but so what)
        setattr(klass, this_deco_class_name + '_omit', self.omit)
        setattr(klass, this_deco_class_name + '_only', self.only)

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
                if curr_funcname == '_deco_base_f_wrapper_':
                    # Previous was decorated inner fn; overwrite '_deco_base_f_wrapper_'
                    # print("**** found _deco_base_f_wrapper_, prev fn name =", call_list[-1])     # <<<DEBUG>>>
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
                # its enclosing function, its caller is '_deco_base_f_wrapper_'
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
                # Look in stack frame (!) for (0.2.4) STACKFRAME_HACK_DICT_NAME
                # and use its values
                #   _enabled, _log_call_numbers, _active_call_number, _extra_indent_level, _prefixed_fname
                if wrapper_frame.f_locals.get(STACKFRAME_HACK_DICT_NAME):
                    active_call_items = wrapper_frame.f_locals[STACKFRAME_HACK_DICT_NAME]
                    enabled = active_call_items['_enabled']     # it's >= 0
                    log_call_numbers = active_call_items['_log_call_numbers']
                    active_call_number = active_call_items['_active_call_number']
                    call_list[-1] = active_call_items['_prefixed_fname']   # Hack alert (Pt 3)

                    # only change prev_indent_level once, for nearest deco'd fn
                    if prev_indent_level < 0:
                        prev_indent_level = active_call_items['_extra_indent_level']

                    if enabled and log_call_numbers:
                        call_list[-1] += (' [%d]' % active_call_number)
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

    @classmethod
    def decorate_hierarchy(cls, baseclass: type, **setting_kwds):
        """Decorate baseclass and, recursively, all of its descendants.
        If any subclasses are directly decorated, their explicitly given setting_kwds,
        EXCEPT `omit` and `only`, override those in `setting_kwds` UNLESS 'override=True'
        is in `setting_kwds`.
        """
        cls.decorate_class(baseclass, decorate_subclasses=True, **setting_kwds)

    @classmethod
    def decorate_class(cls, klass: type, decorate_subclasses=False, **setting_kwds):
        """Decorate klass and, optionally, all of its descendants recursively.
       (If decorate_subclasses == True, and if any subclasses are decorated,
       their explicitly given setting_kwds, EXCEPT `omit` and `only`,
       override those in `setting_kwds` UNLESS 'override=True' is in `setting_kwds`.)
        """
        assert isinstance(klass, type)

        def _deco_class(kls: type):
            t = cls(**setting_kwds)
            _ = t(kls)
            # assert _ == kls

        def _deco_class_rec(kls: type):
            _deco_class(kls)
            for subclass in kls.__subclasses__():
                _deco_class_rec(subclass)

        if decorate_subclasses:
            _deco_class_rec(klass)
        else:
            _deco_class(klass)
        # (_deco_class_rec if decorate_subclasses else _deco_class)(klass)

    # TODO docstring, docs

    @classmethod
    def decorate_package_function(cls, f: 'Callable', **setting_kwds):
        """Wrap ``f`` with decorator ``cls`` (e..g ``log_calls``) using settings in ``settings_kwds``;
        replace definition of ``f.__name__`` with that decorated function in the ``__dict__``
        of the module of ``f``.

        :param cls: decorator class e.g. log_calls
        :param f: a function object, qualified with module, e.g. mymodule.myfunc,
                  however it would be referred to in code at the point of a call to `decorate_package_function`.
        :param setting_kwds: settings for decorator

        inspect.getmodule(f).__name__
        'sklearn.cluster.k_means_'

        inspect.getmodulename('sklearn/cluster/k_means_.py')
        'k_means_'

        SO
            * fmodname = inspect.getmodule(f).__name__
                'sklearn.cluster.k_means_'
            * replace '.' with '/' in fmodname
              fmodname = 'sklearn/cluster/k_means_'

            * inspect.getmodulename('sklearn/cluster/k_means_.py')
              'k_means_'
             VS
              inspect.getmodulename('sklearn.cluster')
              None

              So call inspect.getmodulename(fmodname + '.py')
              If it returns None, leave alone, f was called through module.
              If it's NOT None, then trim off last bit from path
              fmodname = '.'.join(fmodname.split('/')[:-1])
              eval(fmodname + '.' + f.__name__


        """
        f_deco = cls(**setting_kwds)(f)

        namespace = vars(inspect.getmodule(f))

        fmodname = inspect.getmodule(f).__name__
        # 'sklearn.cluster.k_means_'
        basic_modname = inspect.getmodulename(fmodname.replace('.', '/') + '.py')
        # 'k_means_' or 'some_module', or None
        if basic_modname and '.' in fmodname:
            fpackagename = namespace['__package__']     # '.'.join(fmodname.split('.')[:-1])
            exec("import " + fpackagename)
            package_dict = eval("vars(%s)" % fpackagename)    # TODO - works?
            package_dict[f.__name__] = f_deco

        namespace[f.__name__] = f_deco

    @classmethod
    def decorate_module_function(cls, f: 'Callable', **setting_kwds):
        """Wrap ``f`` with decorator ``cls`` (e..g ``log_calls``) using settings in ``settings_kwds``;
        replace definition of ``f.__name__`` with that decorated function in the ``__dict__``
        of the module of ``f``.

        :param cls: decorator class e.g. log_calls
        :param f: a function object, qualified with module, e.g. mymodule.myfunc,
                  however it would be referred to in code at the point of a call to `decorate_module_function`.
        :param setting_kwds: settings for decorator
        """
        namespace = vars(inspect.getmodule(f))
        namespace[f.__name__] = cls(**setting_kwds)(f)

    @classmethod
    def decorate_function(cls, f: 'Callable', **setting_kwds):
        """Wrap f with decorator `cls` using settings, replace definition of f.__name__
        with that decorated function in the global namespace OF THE CALLER.

        :param cls: decorator class e.g. log_calls
        :param f: a function object, with no package/module qualifier.
                  However it would be referred to in code at the point of the call
                  to `decorate_function`.
        :param setting_kwds: settings for decorator
        """
        caller_frame = sys._getframe(1)           # caller's frame
        namespace = caller_frame.f_globals
        namespace[f.__name__] = cls(**setting_kwds)(f)

    # v0.3.0b18 -- Not ready for primetime?
    # Hard to get this working on real-world examples, e.g. sklearn.cluster.k_means_
    @classmethod
    def decorate_module(cls, mod: 'module',
                        functions=True, classes=True,
                        **setting_kwds):
        """
        Can't decorate builtins, attempting
            log_calls.decorate_class(dict, only='update')
        gives:
            TypeError: can't set attributes of built-in/extension type 'dict'
        """
        # Functions
        if functions:
            for name, f in inspect.getmembers(mod, inspect.isfunction):
                vars(mod)[name] = cls(**setting_kwds)(f)
                ### todo vars(mod) also has key __package__,
                ###  |   e.g. 'sklearn.cluster' for mod = 'sklearn.cluster.k_means_'
        # Classes
        if classes:
            for name, kls in inspect.getmembers(mod, inspect.isclass):
                _ = cls(**setting_kwds)(kls)
                # assert _ == kls

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
                           and not using a logger (default: True (0.3.0))
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
        mute:              setting. 3-valued:
                            log_calls.MUTE.NOTHING  (default -- all output produced)
                            alias False
                            log_calls.MUTE.CALLS    (mute output from decorated functions
                                                     & methods & properties, but log_message
                                                     and log_exprs produce output;
                                                     call # recording, history recording continue
                                                     if enabled)
                            alias True
                            log_calls.MUTE.ALL      (no output at all; but call # recording,
                                                     history recording continue if enabled)
                            alias -1

                            mutable, but NOT allow_indirect: log_message has to be able
                            to get the value, and then doesn't have access to the args to f
                            (if f is not enabled, and only kludgily, if f is enabled)

                            When `mute` is True (log_calls.MUTE.CALLS,
                            log_expr and log_message adjust for calls not being logged:
                            because there's no log_calls "frame",
                            -- they don't indent an extra level no 'arguments:' to align with), and
                            -- they automatically prefix messages with function's display name

        record_history:    If true, an array of records will be kept, one for each
                           call to the function; each holds call number (1-based),
                           arguments and defaulted keyword arguments, return value,
                           time elapsed, time of call, caller (call chain), prefixed
                           function name.(Default: False)
        max_history:       An int. value >  0 --> store at most value-many records,
                                                  oldest records overwritten;
                                   value <= 0 --> unboundedly many records are stored.
        Parameters that aren't *settings*
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
        DecoSetting_bool('indent',           bool,           True,          allow_falsy=True),
        DecoSetting_bool('log_call_numbers', bool,           False,         allow_falsy=True),
        DecoSetting_str('prefix',            str,            '',            allow_falsy=True,
                        allow_indirect=False, mutable=True),    # 0.3.0; was mutable=False

        DecoSettingFile('file',              io.TextIOBase,  None,          allow_falsy=True),
        DecoSettingLogger('logger',          (logging.Logger,
                                              str),          None,          allow_falsy=True),
        DecoSetting_int('loglevel',          int,            logging.DEBUG, allow_falsy=False),
        DecoSetting_int('mute',              int,            False,         allow_falsy=True,
                        allow_indirect=True, mutable=True),
        DecoSettingHistory('record_history'),
        DecoSetting_int('max_history',       int,            0,             allow_falsy=True,
                        allow_indirect=False, mutable=False),
        DecoSetting_bool('NO_DECO',  bool,           False,         allow_falsy=True, mutable=False),
    )
    DecoSettingsMapping.register_class_settings('log_calls',    # name of this class. DRY - oh well.
                                                _setting_info_list)

    @used_unused_keywords()
    def __init__(self,
                 settings=None,     # 0.2.4.post2. A dict or a pathname
                 omit=tuple(),      # 0.3.0 class deco'ing: omit these methods or properties; not a setting
                 only=tuple(),      # 0.3.0 class deco'ing: deco only these methods or props (sans any in omit); not a setting
                 name=None,         # 0.3.0 name or oldstyle fmt str for f_display_name of fn; not a setting
                 override=False,    # 0.3.0b18: new settings override existing ones. NOT a "setting"
                 enabled=True,
                 args_sep=', ',
                 log_args=True,
                 log_retval=False,
                 log_elapsed=False,
                 log_exit=True,
                 indent=True,            # 0.3.0, this seems the better default
                 log_call_numbers=False,
                 prefix='',
                 file=None,    # detectable value so we late-bind to sys.stdout
                 logger=None,
                 loglevel=logging.DEBUG,
                 mute=False,
                 record_history=False,
                 max_history=0,
                 NO_DECO=False,
    ):
        """(See base class docstring)
        """
        # 0.2.4 settings stuff:
        # determine which keyword arguments were actually passed by caller!
        used_keywords_dict = log_calls.__dict__['__init__'].get_used_keywords()
        # remove non-"settings"
        for kwd in ('settings', 'omit', 'only', 'name', 'override'):
            if kwd in used_keywords_dict:
                del used_keywords_dict[kwd]

        super().__init__(
            settings=settings,
            _omit=omit,             # 0.3.0 class deco'ing: tuple - omit these methods/inner classes
            _only=only,             # 0.3.0 class deco'ing: tuple - decorate only these methods/inner classes (sans omit)
            _name_param=name,       # 0.3.0 name or oldstyle fmt str etc.
            _override=override,     # 0.3.0b18: new settings override existing ones. NOT a "setting"
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
            NO_DECO=NO_DECO,
        )

    # 0.3.0
    @classmethod
    def allow_repr(cls) -> bool:
        return False

    # 0.3.0
    @classmethod
    def fixup_for_init(cls, some_settings: dict):
        some_settings['log_retval'] = False

    mute = False        # CLASS level attribute

    # 0.3.0
    @classmethod
    def global_mute(cls) -> bool:
        return cls.mute

    # 0.3.0
    @classmethod
    def log_message_auto_prefix_threshold(cls) -> int:
        """:return: one of the "constants" of _deco_base.MUTE
        The log_* functions will automatically prefix their output
        with the function's display name if max of
            the function's mute setting, global_mute()
        is this mute level or higher.
        """
        return cls.MUTE.CALLS

    # 0.3.0
    @classmethod
    def log_message_auto_prefix_threshold(cls) -> int:
        """:return: one of the "constants" of _deco_base.MUTE
        The log_* functions will automatically prefix their output
        with the function's display name if max of
            the function's mute setting, global_mute()
        is this mute level or higher.
        """
        return cls.MUTE.CALLS

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
