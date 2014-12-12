__author__ = "Brian O'Neill"  # BTO
__version__ = '0.2.6'

from .deco_settings import DecoSetting, DecoSettingsMapping
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
        DecoSetting('max_history',      int,  0,      allow_falsy=True, mutable=False),
    )
    DecoSettingsMapping.register_class_settings('record_history',    # name of this class. DRY - oh well.
                                                _setting_info_list)

    # 0.2.6 Fix: use decorator:
    @used_unused_keywords()
    def __init__(self, enabled=True, prefix='', max_history=0):
        # 0.2.6 get used_keywords_dict and pass to super().__init__
        used_keywords_dict = record_history.__dict__['__init__'].get_used_keywords()
        super().__init__(_used_keywords_dict=used_keywords_dict,
                         enabled=enabled,
                         prefix=prefix,
                         max_history=max_history,
                         indent=False,              # p.i.t.a. that this is here :|
                         log_call_numbers=True,     # for call chain in history record
        )

    @classmethod
    def get_logging_fn(cls, _get_final_value_fn):
        """Return None: no output.
        cls: unused.."""
        return None

    def __call__(self, f):
        return super().__call__(f)
