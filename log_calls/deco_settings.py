__author__ = "Brian O'Neill"  # BTO
# __version__ = '0.3.0'
__doc__ = """
DecoSettingsMapping -- class that's usable with any class-based decorator
that has several keyword parameters; this class makes it possible for
a user to access the collection of settings as an attribute
(object of type DecoSettingsMapping) of the decorated function.
The attribute/obj of type DecoSettingsMapping provides
    (*) a mapping interface for the decorator's keyword params
    (*) an attribute interface for its keyword params
        i.e. attributes of the same names,
    as well as 'direct' and 'indirect' values for its keyword params
    q.v.
Using this class, any setting under its management can take two kinds of values:
direct and indirect, which you can think of as static and dynamic respectively.
Direct/static values are actual values used when the decorated function is
interpreted, e.g. enabled=True, args_sep=" / ". Indirect/dynamic values are
strings that name keyword arguments of the decorated function; when the
decorated function is called, the arguments passed by keyword and the
parameters of the decorated function are searched for the named parameter,
and if it is found, its value is used. Parameters whose normal type is str
(args_sep) indicate an indirect value by appending an '='.

Thus, in:
    @log_calls(args_sep='sep=', prefix="MyClass.")
    def f(a, b, c, sep='|'): pass
args_sep has an indirect value, and prefix has a direct value. A call can
dynamically override the default value in the signature of f by supplying
a value:
    f(1, 2, 3, sep=' $ ')
or use func's default by omitting the sep argument.
A decorated function doesn't have to explicitly declare the named parameter,
if its signature includes **kwargs. Consider:
    @log_calls(enabled='enable')
    def func1(a, b, c, **kwargs): pass
    @log_calls(enabled='enable')
    def func2(z, **kwargs): func1(z, z+1, z+2, **kwargs)
When the following statement is executed, the calls to both func1 and func2
will be logged:
    func2(17, enable=True)
whereas neither of the following two statements will trigger logging:
    func2(42, enable=False)
    func2(99)

For consistency, any parameter value that names a keyword
parameter of the decorated function can also end in a trailing '=', which
is stripped. Thus, enabled='enable_=' indicates an indirect value supplied
by the keyword 'enable_' of the decorated function.
"""
from collections import OrderedDict, defaultdict
import pprint

import warnings     # v0.3.0b23

from .helpers import is_keyword_param, is_quoted_str


__all__ = ['DecoSetting', 'DecoSettingsMapping']


#----------------------------------------------------------------------------
# DecoSetting & basic subclasses
#----------------------------------------------------------------------------

class DecoSetting():
    """a little struct - static info about one setting (keyword parameter),
                         sans any value.

    v0.3.0b25
    indirect_default: a user attribute which this constructor knows about.
    If present in kwargs, use the value there; o/w use .default.
    This is the latest take on how to handle missing indirect value of "enabled".

    Callers can add additional fields by passing additional keyword args.
    The additional fields/keys & values are made attributes of this object,
    and a (sorted) list of the keys is saved (_user_attrs).

    Subclasses can supply a pre_call_handler method
    returning str or empty:
        def pre_call_handler(self, context: dict):
            return ("%s <== called by %s"
                    % (context['output_fname'],
                       ' <== '.join(context['call_list'])))
    context contains these keys:
        decorator
        settings      # of decorator
        indent
        prefixed_fname
        output_fname
        fparams
        argcount
        argnames      # len = argcount
        argvals       # len = argcount
        varargs
        explicit_kwargs
        implicit_kwargs
        defaulted_kwargs
        call_list
        args
        kwargs

    Subclasses can supply a post_call_handler method:
    returning str or empty:
        def post_call_handler(self, context: dict):
            return ("%s ==> returning to %s"
                       % (context['output_fname'],
                          ' ==> '.join(context['call_list'])))

    For a post_call_handler, context adds these keys:
        elapsed_secs
        timestamp
        retval
    """
    def __init__(self, name, final_type, default, *,
                 allow_falsy, allow_indirect=True, mutable=True, visible=True,
                 pseudo_setting=False,  # v0.3.0b24
                 **more_attributes):
        """not visible => not allow_indirect
        """
        assert not default or isinstance(default, final_type)
        self.name = name                # key
        self.final_type = final_type    # bool int str logging.Logger ...
        self.default = default
        self.allow_falsy = allow_falsy  # is a falsy final val of setting allowed
        self.allow_indirect = allow_indirect and visible  # are indirect values allowed
        self.mutable = mutable
        self.visible = visible
        self.pseudo_setting = pseudo_setting    # v0.3.0b24

        # v0.3.0b25
        self.indirect_default = more_attributes.pop('indirect_default', self.default)

        # we need to write fields in repr the same way every time,
        # so even though more_attributes isn't ordered,
        # we need to pick an order & stick to it
        self._user_attrs = sorted(list(more_attributes))
        self.__dict__.update(more_attributes)

    def __repr__(self):
        if isinstance(self.final_type, tuple):      # it's a tuple of types
            final_type = '(' + ', '.join(map(lambda t: t.__name__, self.final_type)) + ')'
        else:                                       # it's a type
            final_type = self.final_type.__name__
        #default = self.default if final_type != 'str' else repr(self.default)
        output = ("DecoSetting(%r, %s, %r, allow_falsy=%s, allow_indirect=%s, "
                  "mutable=%s, visible=%s, pseudo_setting=%r, indirect_default=%r"
                  %
                  (self.name, final_type, self.default, self.allow_falsy, self.allow_indirect,
                   self.mutable, self.visible, self.pseudo_setting, self.indirect_default)
        )
        # append user attrs
        for attr in self._user_attrs:
            output += ", %s=%r" % (attr, self.__dict__[attr])

        output += ")"
        return output

    def value_from_str(self, s):
        """Virtual method for use by _deco_base._read_settings_file.
        0.2.4.post1"""
        raise ValueError()

    def has_acceptable_type(self, value):
        return isinstance(value, self.final_type)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DecoSetting subclasses
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class DecoSetting_bool(DecoSetting):
    def value_from_str(self, s):
        """Virtual method for use by _deco_base._read_settings_file.
        0.2.4.post1"""
        ddict = defaultdict(lambda: self.default)
        ddict['TRUE'] = True
        ddict['FALSE'] = False
        return ddict[s.upper()]


class DecoSetting_int(DecoSetting):
    def value_from_str(self, s):
        """Virtual method for use by _deco_base._read_settings_file.
        0.2.4.post1"""
        try:
            return int(s)
        except ValueError:
            return super().value_from_str(s)


class DecoSetting_str(DecoSetting):
    def value_from_str(self, s):
        """Virtual method for use by _deco_base._read_settings_file.
        s must be enclosed in quotes (the same one on each end!)
        and then we return what's quoted... or raise ValueError
        0.2.4.post1"""
        if is_quoted_str(s):
            return s[1:-1]
        return super().value_from_str(s)

#----------------------------------------------------------------------------
# DecoSettingsMapping
#----------------------------------------------------------------------------
class DecoSettingsMapping():
    """Usable with any class-based decorator that wants to implement
    a mapping interface and attribute interface for its keyword params,
    as well as 'direct' and 'indirect' values for its keyword params"""
    # Class-level mapping: classname |-> OrderedDict of class's settings (info 'structs')
    _classname2SettingsData_dict = {}
    _classname2SettingsDataOrigDefaults_dict = {}

    # Class-level mapping: classname |-> pair of tuples:
    #                                   (pre-call handler settings names,
    #                                    post-call handler settings names)
    _classname2handlers = {}

    # When this is last char of a parameter value (to decorator),
    # interpret value of parameter to be the name of
    # a keyword parameter ** of the wrapped function f **
    INDIRECT_VALUE_MARKER = '='

    @classmethod
    def register_class_settings(cls, deco_classname, settings_iter):
        """
        Called before __init__, presently - by deco classes.
        Client classes should call this *** from class level ***
        e.g.
            DecoSettingsMapping.register_class_settings('log_calls', _setting_info_list)

        Add item (deco_classname, od) to _classname2SettingsData_dict
        where od is an ordered dict built from items of settings_iter.
        cls: this class
        deco_classname: key for dict produced from settings_iter
        settings_iter: iterable of DecoSetting objs"""
        # Only do once per deco class
        if deco_classname in cls._classname2SettingsData_dict:
            return

        od = OrderedDict()
        pre_handlers = []
        post_handlers = []
        for setting in settings_iter:
            od[setting.name] = setting
            if setting.__class__.__dict__.get('pre_call_handler'):
                pre_handlers.append(setting.name)
            if setting.__class__.__dict__.get('post_call_handler'):
                post_handlers.append(setting.name)

        cls._classname2SettingsData_dict[deco_classname] = od
        # v0.3.0b23 Make this an OD too
        cls._classname2SettingsDataOrigDefaults_dict[deco_classname] = OrderedDict(
            [(name, od[name].default) for name in od]
        )
        cls._classname2handlers[deco_classname] = (
            tuple(pre_handlers), tuple(post_handlers))

        # <<<attributes>>> Set up descriptors -- OMIT .pseudo_setting !
        for name in od:
            if od[name].visible and not od[name].pseudo_setting:
                setattr(cls, name, cls.make_setting_descriptor(name))

    # v0.3.0b24
    @classmethod
    def get_factory_defaults_OD(cls, deco_classname) -> OrderedDict:
        # return cls._classname2SettingsDataOrigDefaults_dict[deco_classname]
        class_settings = cls._classname2SettingsData_dict[deco_classname]
        return OrderedDict(
            [(name, value)
             for name, value in cls._classname2SettingsDataOrigDefaults_dict[deco_classname].items()
             if class_settings[name].visible and not class_settings[name].pseudo_setting
            ]
        )

    # v0.3.0b24
    @classmethod
    def get_defaults_OD(cls, deco_classname) -> OrderedDict:
        # return cls._classname2SettingsData_dict[deco_classname]
        return OrderedDict(
            [(name, setting.default)
             for name, setting in cls._classname2SettingsData_dict[deco_classname].items()
             if setting.visible and not setting.pseudo_setting
            ]
        )

    @classmethod
    def set_defaults(cls, deco_classname, defaults: dict):
        """Change global default values for all (subsequent) uses of decorator
        with name deco_classname.
        Only settings that are *visible* for cls can be changed.

        Raises KeyError if any key in defaults isn't actually "settings" are is not "visible".
        In both cases no changes are made.
        Ignores any items in `defaults` whose values are of incorrect type,
        or whose value is 'falsy' but the setting has .allow_falsy == False.
        These behaviors are what __setitem__ & __getitem__ do.

        :param deco_classname: name of decorator class, subclass of _deco_base
        :param defaults: dict of setting-name keys and new default values
        """
        # Change defaults of items in cls._classname2SettingsData_dict[deco_classname]
        deco_settings = cls._classname2SettingsData_dict[deco_classname]

        # Integrity check:
        # if setting_name is not a "setting" or it's not a "visible" setting for cls,
        # raise KeyError: that's what __getitem__/__setitem__ do
        for setting_name in defaults:
            if setting_name not in deco_settings:
                raise KeyError(
                    "set_defaults: no such setting (key) as '%s'" % setting_name)
            elif not deco_settings[setting_name].visible:
                raise KeyError(
                    "set_defaults: setting (key) '%s' is not visible in class %s."
                    % (setting_name, deco_classname))

        # TODO 'indirect' values -- Disallow? anyway, prevent? Somehow.
        #  |   Perhaps just get rid of any trailing INDIRECT_VALUE_MARKER ('=')

        # Change working default values
        for setting_name in defaults:
            deco_setting = deco_settings[setting_name]
            new_default_val = defaults[setting_name]

            if ((new_default_val or deco_setting.allow_falsy)
                and deco_setting.has_acceptable_type(new_default_val)
               ):
                # set working default value = new_default_val
                deco_setting.default = new_default_val

    @classmethod
    def reset_defaults(cls, deco_classname):
        """Revert to initial defaults as per documentation & static declarations in code
        """
        #  v0.3.0b24 -- use new classmethods
        orig_defaults = cls._classname2SettingsDataOrigDefaults_dict[deco_classname]
        settings_map = cls._classname2SettingsData_dict[deco_classname]
        for name in settings_map:
            settings_map[name].default = orig_defaults[name]

    # <<<attributes>>>
    @classmethod
    def make_setting_descriptor(cls, name):
        class SettingDescr():
            """A little data descriptor which just delegates
            to __getitem__ and __setitem__ of instance"""
            def __get__(self, instance, owner):
                """
                instance: a DecoSettingsMapping
                owner: class DecoSettingsMapping(?)"""
                return instance[name]

            def __set__(self, instance, value):
                """
                instance: a DecoSettingsMapping
                value: what to set"""
                # ONLY do this is name is a legit setting name
                # (for this obj, as per this obj's initialization)
                instance[name] = value

        return SettingDescr()

    @property
    def _handlers(self) -> tuple:
        """Can't use/call till self.deco_class set in __init__
        Return: duple of tuples (pre-call-handler setting keys, post-call-handler setting keys).
        """
        return self._classname2handlers[self.deco_class.__name__]

    @property
    def _pre_call_handlers(self) -> tuple:
        """Can't use/call till self.deco_class set in __init__"""
        return self._handlers[0]

    @property
    def _post_call_handlers(self) -> tuple:
        """Can't use/call till self.deco_class set in __init__"""
        return self._handlers[1]

    @property
    def _deco_class_settings_dict(self) -> OrderedDict:
        """Can't use/call till self.deco_class set in __init__"""
        return self._classname2SettingsData_dict[self.deco_class.__name__]

    @classmethod
    def get_deco_class_settings_dict(cls, clsname) -> OrderedDict:
        """For use when loading settings files -
        decorator's DecoSettingsMapping doesn't exist yet."""
        return cls._classname2SettingsData_dict[clsname]

    def _get_DecoSetting(self, key) -> DecoSetting:
        """
        :param key: a setting key.
        :return: the corresponding DecoSetting.
        """
        return self._deco_class_settings_dict[key]

    def _is_visible(self, key) -> bool:
        """key - a setting name."""
        return self._get_DecoSetting(key).visible

    @property
    def _visible_setting_names_gen(self) -> list:
        return (name for name in self._tagged_values_dict if self._is_visible(name))

    def __init__(self, *, deco_class, **values_dict):
        """classname: name of class that has already stored its settings
        by calling register_class_settings(cls, classname, settings_iter)

        values_iterable: iterable of pairs
                       (name,
                        value such as is passed to log_calls-__init__)
                        values are either 'direct' or 'indirect'

        Assumption: every name in values_iterable is info.name
                    for some info in settings_info.
        Must be called after __init__ sets self.classname."""

        self.deco_class = deco_class
        class_settings_dict = self._deco_class_settings_dict

        # Insert values in the proper order - as given by caller,
        # both visible and not visible ones.
        self._tagged_values_dict = OrderedDict()    # stores pairs inserted by __setitem__
        for k in class_settings_dict:
            if k in values_dict:                    # allow k to be set later
                self.__setitem__(k, values_dict[k],
                                 info=class_settings_dict[k],
                                 _force_mutable=True,
                                 _force_visible=True)

    def registered_class_settings_repr(self) -> str:
        list_of_settingsinfo_reprs = []

        for k, info in self._deco_class_settings_dict.items():
            list_of_settingsinfo_reprs.append(repr(info))


        return ("DecoSettingsMapping.register_class_settings("
                "    " + self.deco_class.__name__ + ",\n"
                "    [%s\n"
                "])") % ',\n    '.join(list_of_settingsinfo_reprs)

    def __setitem__(self, key, value,
                    info=None, _force_mutable=False, _force_visible=False):
        """
        key: name of setting, e.g. 'prefix';
             must be in self._deco_class_settings_dict()
        value: something passed to __init__ (of log_calls),
        info: self.deco_class_settings_dict[key] or None
        _force_mutable: if key is already in self._tagged_values_dict and
                        it's not mutable, attempting to __setitem__ on it
                        raises KeyError, unless force_mutable is True
                        in which case it will be written.
        Store pair (is_indirect, modded_val) at key in self._tagged_values_dict[key]
        where
            is_indirect: bool,
            modded_val = val if kind is direct (not is_indirect),
                       = keyword of wrapped fn if is_indirect
                         (sans any trailing '=')
        THIS method assumes that the values in self._deco_class_settings_dict()
        are DecoSetting objects -- all fields of that class are used

        You can only set visible settings.
        """
        # Blithely assuming that if info is not None then it's DecoSetting for key
        if not info:
            if key not in self._deco_class_settings_dict:
                raise KeyError(
                    "no such setting (key) as '%s'" % key)
            info = self._get_DecoSetting(key)
        if not info.visible and not _force_visible:
            raise KeyError(
                "setting (key) '%s' is not visible in class '%s'."
                % (key, self.deco_class.__name__))

        final_type = info.final_type
        default = info.default
        allow_falsy = info.allow_falsy          # 0.2.4 was info.default :| FIXED.
        allow_indirect = info.allow_indirect

        # if the setting is immutable (/not mutable/set-once-only),
        # raise ValueError unless _force_mutable:
        if not info.mutable and not _force_mutable: # and key in self._tagged_values_dict:
            raise ValueError("%s' is write-once (current value: %r)"
                             % (key, self._tagged_values_dict[key][1]))
        if not allow_indirect:
            self._tagged_values_dict[key] = False, value
            return

        # Detect fixup direct/static values, except for final_type == str
        if not isinstance(value, str) or not value:
            indirect = False
            # value not a str, or == '', so use value as-is if valid, else default
            if (not value and not allow_falsy) or not info.has_acceptable_type(value):  # isinstance(value, final_type)
                value = default
        else:                           # val is a nonempty str
            if final_type != str and \
               (not isinstance(final_type, tuple) or str not in final_type):
                # It IS indirect, and val designates a keyword of f
                indirect = True
                # Remove trailing self.INDIRECT_VALUE_MARKER if any
                if value[-1] == self.INDIRECT_VALUE_MARKER:
                    value = value[:-1]
            else:
                # final_type == str, or
                # isinstance(final_type, tuple) and str in final_type.
                # so val denotes an indirect value, an f-keyword,
                # IFF last char is INDIRECT_VALUE_MARKER
                indirect = (value[-1] == self.INDIRECT_VALUE_MARKER)
                if indirect:
                    value = value[:-1]

        self._tagged_values_dict[key] = indirect, value

    def __getitem__(self, key):
        """You can only get visible settings."""
        if not self._is_visible(key):
            raise KeyError(
                "setting (key) '%s' is not visible in class '%s'."
                % (key, self.deco_class.__name__))
        indirect, value = self._tagged_values_dict[key]
        return value + self.INDIRECT_VALUE_MARKER if indirect else value

    def __len__(self):
        """Return # of visible settings."""
        #return len(self._tagged_values_dict)
        return len(list(self._visible_setting_names_gen))

    def __iter__(self):
        """Return iterable of names of visible settings."""
        return self._visible_setting_names_gen

    def items(self):
        """Return iterable of items of visible settings."""
        return ((name, self.__getitem__(name)) for name in self._visible_setting_names_gen)

    def __contains__(self, key):
        """True iff key is a visible setting."""
        return key in self._tagged_values_dict and self._is_visible(key)

    def __repr__(self):
        return ("DecoSettingsMapping( \n"
                "    deco_class=%s,\n"
                "    ** %s\n"
                ")") % \
               (self.deco_class.__name__,
                pprint.pformat(self.as_OD(), indent=8)
               )

    def __str__(self):
        return str(self.as_dict())

    def as_OD(self) -> OrderedDict:
        """Return OrderedDict of visible settings (only).
        v0.3.0b23
          Renamed ``as_OrderedDict`` ==> ``as_OD`` -- to match new classmethods
          ``log_calls.get_factory_defaults_OD()``, ``log_calls.get_defaults_OD()``.
          ``as_OrderedDict`` deprecated.
        """
        od = OrderedDict()
        for k, v in self._tagged_values_dict.items():
            if self._is_visible(k):
                od[k] = v[1]
        return od

    def as_OrderedDict(self) -> OrderedDict:
        """Deprecated alias for ``as_OD`` -- v0.3.0b23."""
        # Issue a warning. (and don't do it ALL the time.)
        # In Py3.2+ "DeprecationWarning is now ignored by default"
        # (https://docs.python.org/3/library/warnings.html),
        # so to see it, you have to run the Python interpreter
        # with the -W switch, e.g. `python -W default run_tests.py`
        # [equivalently: `python -Wd run_tests.py`]
        warnings.warn("Warning: 'as_OrderedDict()' method is deprecated, use 'as_OD()' instead.",
                      DeprecationWarning,
                      stacklevel=2)         # refer to stackframe of caller
        return self.as_OD()

    def as_dict(self):
        """Return dict of visible settings only."""
        return dict(self.as_OD())

    def update(self, *dicts, _force_mutable=False, **d_settings):
        """Do __setitem__ for every key/value pair in every dictionary
        in dicts + (d_settings,).
        Allow but ignore attempts to write to immutable keys!
        This permits the user to get the settings as_dict() or as_OrderedDict(),
        make changes & use them,
        and then restore the original settings, which will contain items
        for immutable settings too. Otherwise the user would have to
        remove all the immutable keys before doing update - ugh.

        0.3.0 added , _force_mutable keyword param
        """
        for d in dicts + (d_settings,):
            for k, v in d.items():
                info = self._deco_class_settings_dict.get(k)
                # skip immutable settings
                if info and not self._deco_class_settings_dict[k].mutable and not _force_mutable:
                    continue
                # if not info, KeyError from __setitem__
                self.__setitem__(k, v, info=info, _force_mutable=_force_mutable)

    def _get_tagged_value(self, key):
        """Return (indirect, value) for key"""
        return self._tagged_values_dict[key]

    def get_final_value(self, name, *dicts, fparams):
        """
        name:    key into self._tagged_values_dict, self._setting_info_list
        *dicts:  varargs, usually just kwargs of a call to some function f,
                 but it can also be e.g. *(explicit_kwargs, defaulted_kwargs,
                 implicit_kwargs, with fparams=None) of that function f,
        fparams: inspect.signature(f).parameters of that function f
        THIS method assumes that the objs stored in self._deco_class_settings_dict
        are DecoSetting objects -- this method uses every attribute of that class
                                   except allow_indirect.
        A very (deco-)specific method, it seems.
        """
        indirect, di_val = self._tagged_values_dict[name]  # di_ - direct or indirect
        if not indirect:
            return di_val

        # di_val designates a (potential) f-keyword

        setting_info = self._deco_class_settings_dict[name]
        final_type = setting_info.final_type
        ## v0.3.0b25
        # default = setting_info.default
        default = setting_info.indirect_default
        allow_falsy = setting_info.allow_falsy

        # If di_val is in any of the dictionaries, get corresponding value
        found = False
        for d in dicts:
            if di_val in d:            # actually passed to f
                val = d[di_val]
                found = True
                break

        if not found:
            if fparams and is_keyword_param(fparams.get(di_val)): # not passed; explicit f-kwd?
                # yes, explicit param of f, so use f's default value
                val = fparams[di_val].default
            else:
                val = default

        # fixup: "loggers" that aren't loggers (or strs), "strs" that arent strs, etc
#        if (not val and not allow_falsy) or (val and not isinstance(val, final_type)):
        if (not val and not allow_falsy) or \
           (type(final_type) == type and not isinstance(val, final_type)) or \
           (type(final_type) == tuple and all((not isinstance(val, t) for t in final_type))):
            val = default
        return val
