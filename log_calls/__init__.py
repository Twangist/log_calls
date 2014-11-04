from .log_calls import log_calls, record_history_only, __version__, __author__

# tests
from .deco_settings import DecoSetting, DecoSettingsMapping
from .proxy_descriptors import install_proxy_descriptor, ClassInstanceAttrProxy

__all__ = [
    'log_calls', 'record_history_only', '__version__', '__author__',
    'difference_update',
    'DecoSetting', 'DecoSettingsMapping',
    'install_proxy_descriptor', 'ClassInstanceAttrProxy',
]
