from .log_calls import log_calls, __version__, __author__
from .record_history import record_history

# tests
from .deco_settings import DecoSetting, DecoSettingsMapping
from .proxy_descriptors import install_proxy_descriptor, ClassInstanceAttrProxy

__all__ = [
    'log_calls', 'record_history', '__version__', '__author__',
    'difference_update',
    'DecoSetting', 'DecoSettingsMapping',
    'install_proxy_descriptor', 'ClassInstanceAttrProxy',
]
