__author__ = "Brian O'Neill"  # BTO
__version__ = '0.3.0v19'

from .deco_settings import DecoSetting, DecoSettingsMapping, DecoSetting_bool
from .log_calls import _deco_base, DecoSettingHistory
from .used_unused_kwds import used_unused_keywords


class record_history(_deco_base):
    """
    """
    # allow indirection for all except prefix and max_history, which also isn't mutable
    _setting_info_list = (
        DecoSetting('log_call_numbers', bool, True,   allow_falsy=True, visible=False),
        DecoSetting('indent',           bool, False,  allow_falsy=True, visible=False),
        # visible:
        DecoSettingHistory('enabled'),  # alias "record_history" in log_calls
        DecoSetting('prefix',           str,  '',     allow_falsy=True, allow_indirect=False),
        DecoSetting('mute',             int,  False,  allow_falsy=True, visible=False),  # 0.3.0
        DecoSetting('max_history',      int,  0,      allow_falsy=True, mutable=False),
        DecoSetting_bool('NO_DECO',  bool,  False,   allow_falsy=True, mutable=False),
    )
    DecoSettingsMapping.register_class_settings('record_history',    # name of this class. DRY - oh well.
                                                _setting_info_list)

    # 0.2.6 Fix: use decorator:
    @used_unused_keywords()
    def __init__(self,
                 settings=None,     # 0.3.0b18 added:  A dict or a pathname
                 omit=tuple(),      # 0.3.0 class deco'ing: omit these methods/inner classes
                 only=tuple(),      # 0.3.0 class deco'ing: decorate only these methods/inner classes (minus any in omit)
                 name=None,         # 0.3.0 name or oldstyle fmt str for f_display_name of fn; not a setting
                 enabled=True,
                 prefix='',
                 max_history=0,
                 NO_DECO=False,
                ):
        # 0.2.6 get used_keywords_dict and pass to super().__init__
        used_keywords_dict = record_history.__dict__['__init__'].get_used_keywords()
        # 0.3.0 but first, ditch parameters that aren't settings
        for kwd in ('omit', 'only', 'name'):
            if kwd in used_keywords_dict:
                del used_keywords_dict[kwd]

        super().__init__(
            settings=settings, # 0.3.0b18 added:  A dict or a pathname
            _omit=omit,        # 0.3.0 class deco'ing: tuple - omit these methods/inner classes
            _only=only,        # 0.3.0 class deco'ing: tuple - decorate only these methods/inner classes (minus omit)
            _name_param=name,  # 0.3.0 name or oldstyle fmt str etc.
            _used_keywords_dict=used_keywords_dict,
            enabled=enabled,
            prefix=prefix,
            mute=False,
            max_history=max_history,
            indent=False,              # p.i.t.a. that this is here :|
            log_call_numbers=True,     # for call chain in history record
            NO_DECO=NO_DECO,
        )

    # 0.3.0
    @classmethod
    def allow_repr(cls) -> bool:
        return True

    # 0.3.0
    @classmethod
    def log_message_auto_prefix_threshold(cls) -> int:
        """:return: one of the "constants" of _deco_base.MUTE
        The log_* functions will automatically prefix their output
        with the function's display name if max of
            the function's mute setting, global_mute()
        is this mute level or higher.
        Returning _deco_base.MUTE.NOTHING means, always prefix.
        """
        return cls.MUTE.NOTHING


    #### 0.3.0.beta12+ try letting record_history use log_* functions
    # @classmethod
    # def get_logging_fn(cls, _get_final_value_fn):
    #     """Return None: no output.
    #     cls: unused.."""
    #     return None

    # def __call__(self, f):
    #     return super().__call__(f)
