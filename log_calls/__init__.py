from .log_calls import log_calls, difference_update, __version__, __author__

# tests
from .deco_settings import DecoSetting, DecoSettingsMapping
from .proxy_descriptors import install_proxy_descriptor, ClassInstanceAttrProxy

__all__ = [
    'log_calls', 'difference_update', '__version__', '__author__',
    'DecoSetting', 'DecoSettingsMapping',
    'install_proxy_descriptor', 'ClassInstanceAttrProxy',
]
