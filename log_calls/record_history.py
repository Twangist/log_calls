__author__ = "Brian O'Neill"  # BTO
__version__ = '0.1.14'

from .deco_settings import DecoSetting, DecoSettingsMapping
from .log_calls import _deco_base, DecoSettingHistory


class record_history(_deco_base):
    """
    """
    # allow indirection for all except prefix and max_history, which also isn't mutable
    _setting_info_list = (
        DecoSetting('log_call_numbers', bool, False,  allow_falsy=True, visible=False),
        DecoSetting('indent',           bool, False,  allow_falsy=True, visible=False),
        # visible:
        DecoSettingHistory('enabled'),  # alias "record_history" in log_calls
        DecoSetting('prefix',           str,  '',     allow_falsy=True, allow_indirect=False),
        DecoSetting('max_history',      int,  0,      allow_falsy=True, mutable=False),
    )
    DecoSettingsMapping.register_class_settings('record_history',    # name of this class. DRY - oh well.
                                                _setting_info_list)

    def __init__(self, enabled=True, prefix='', max_history=0):
        super().__init__(enabled=enabled,
                         prefix=prefix,
                         max_history=max_history,
                         indent=False,              # p.i.t.a. that this is here :|
                         log_call_numbers=True,     # for call chain in history record
        )

    @classmethod
    def get_logging_fn(cls, _get_final_value_fn) -> tuple:
        """Return pair: logging_fn or None, paired with can_indent: bool.
        cls: unused. Present so this method can be overridden."""
        return None, False

    def __call__(self, f):
        return super().__call__(f)
