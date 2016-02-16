__author__ = "Brian O'Neill"  # BTO
__version__ = '0.1.14'
__doc__ = """
    100% coverage of deco_settings.py
"""

from unittest import TestCase
from log_calls import DecoSetting, DecoSettingsMapping
from log_calls.log_calls import DecoSettingEnabled, DecoSettingHistory

from collections import OrderedDict
import inspect
import logging  # not to use, just for the logging.Logger type
import sys

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# helper
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import re


def collapse_whitespace(s):
    s = re.sub(r'\n', ' ', s)
    s = re.sub(r'\s\s+', ' ', s)
    return s.strip()


##############################################################################
# DecoSetting tests
##############################################################################
class TestDecoSetting(TestCase):
    info_plain = None
    info_extended = None

    @classmethod
    def setUpClass(cls):
        cls.info_plain = DecoSetting('set_once', int, 15,
                                     allow_falsy=True, mutable=False)

        cls.hidden = DecoSetting('hidden', bool, True,
                                 allow_falsy=True, visible=False)

        cls.twotype = DecoSetting('twotype', (logging.Logger, str), None,
                                 allow_falsy=True)

        # with extra fields
        cls.info_extended = DecoSetting('extended', tuple, ('Joe', "Schmoe"),
                                        allow_falsy=True, allow_indirect=False,
                                        extra1='Tom', extra2='Dick', extra3='Harry')

    def test___init__1(self):
        """without any additional attributes"""
        self.assertEqual(self.info_plain.name, 'set_once')
        self.assertEqual(self.info_plain.final_type, int)
        self.assertEqual(self.info_plain.default, 15)
        self.assertEqual(self.info_plain.allow_falsy, True)
        self.assertEqual(self.info_plain.allow_indirect, True)
        self.assertEqual(self.info_plain.mutable, False)
        self.assertEqual(self.info_plain.visible, True)
        self.assertEqual(self.info_plain._user_attrs, [])

    def test___init__2(self):
        """without any additional attributes"""
        self.assertEqual(self.hidden.name, 'hidden')
        self.assertEqual(self.hidden.final_type, bool)
        self.assertEqual(self.hidden.default, True)
        self.assertEqual(self.hidden.allow_falsy, True)
        self.assertEqual(self.hidden.allow_indirect, False)  # because visible=False
        self.assertEqual(self.hidden.mutable, True)
        self.assertEqual(self.hidden.visible, False)

    def test___init__3(self):
        """without any additional attributes"""
        self.assertEqual(self.twotype.name, 'twotype')
        self.assertEqual(self.twotype.final_type, (logging.Logger, str))
        self.assertEqual(self.twotype.default, None)
        self.assertEqual(self.twotype.allow_falsy, True)
        self.assertEqual(self.twotype.allow_indirect, True)  # because visible=False
        self.assertEqual(self.twotype.mutable, True)
        self.assertEqual(self.twotype.visible, True)

    def test___init__4(self):
        """WITH additional attributes."""
        self.assertEqual(self.info_extended.name, 'extended')
        self.assertEqual(self.info_extended.final_type, tuple)
        self.assertEqual(self.info_extended.default, ('Joe', "Schmoe"))
        self.assertEqual(self.info_extended.allow_falsy, True)
        self.assertEqual(self.info_extended.allow_indirect, False)
        self.assertEqual(self.info_extended.mutable, True)
        self.assertEqual(self.info_extended.visible, True)
        self.assertEqual(self.info_extended._user_attrs, ['extra1', 'extra2', 'extra3'])
        self.assertEqual(self.info_extended.extra1, 'Tom')
        self.assertEqual(self.info_extended.extra2, 'Dick')
        self.assertEqual(self.info_extended.extra3, 'Harry')

    def test___repr__1(self):
        plain_repr = "DecoSetting('set_once', int, 15, allow_falsy=True, " \
                     "allow_indirect=True, mutable=False, visible=True, pseudo_setting=False)"
        self.assertEqual(repr(self.info_plain), plain_repr)

    def test___repr__2(self):
        hidden_repr = "DecoSetting('hidden', bool, True, allow_falsy=True, " \
                      "allow_indirect=False, mutable=True, visible=False, pseudo_setting=False)"
        self.assertEqual(repr(self.hidden), hidden_repr)

    def test___repr__3(self):
        twotype_repr = "DecoSetting('twotype', (Logger, str), None, allow_falsy=True, " \
                      "allow_indirect=True, mutable=True, visible=True, pseudo_setting=False)"
        self.assertEqual(repr(self.twotype), twotype_repr)

    def test___repr__4(self):
        ext_repr = "DecoSetting('extended', tuple, ('Joe', 'Schmoe'), " \
                   "allow_falsy=True, allow_indirect=False, " \
                   "mutable=True, visible=True, pseudo_setting=False, " \
                   "extra1='Tom', extra2='Dick', extra3='Harry')"
        self.assertEqual(repr(self.info_extended), ext_repr)


##############################################################################
# DecoSetting tests
##############################################################################

class TestDecoSettingsMapping(TestCase):

    # placeholders:
    _settings_mapping = OrderedDict()

    @classmethod
    def setUpClass(cls):
        cls._settings = (
            DecoSettingEnabled('enabled'),
            DecoSetting('folderol',         str,            '',            allow_falsy=True,  allow_indirect=False),
            DecoSetting('my_setting',       str,            'on',          allow_falsy=False, allow_indirect=True),
            DecoSetting('your_setting',     str,            'off',         allow_falsy=False, allow_indirect=False,
                        mutable=False),
            DecoSettingHistory('history', visible=False),
        )
        DecoSettingsMapping.register_class_settings('TestDecoSettingsMapping',
                                                    cls._settings)

    def setUp(self):
        """__init__(self, *, deco_class, **values_dict)"""
        self._settings_mapping = DecoSettingsMapping(
            deco_class=self.__class__,
            # the rest are what DecoSettingsMapping calls **values_dict
            enabled=True,
            folderol='bar',
            my_setting='eek',       # str but doesn't end in '=' --> not indirect
            your_setting='Howdy',
            history=False
        )

    def test_register_class_settings(self):
        self.assertIn('TestDecoSettingsMapping', DecoSettingsMapping._classname2SettingsData_dict)
        od = DecoSettingsMapping._classname2SettingsData_dict['TestDecoSettingsMapping']
        self.assertIsInstance(od, OrderedDict)  # implies od, od is not None, etc.
#        self.assertEqual(len(od), len(self._settings))
        names = tuple(map(lambda s: s.name, self._settings))
        self.assertEqual(tuple(od), names)

    def test___init__(self):
        """setUp does what __init__ ordinarily does:
            __init__(self, *, deco_class, **values_dict)"""
        self.assertEqual(self._settings_mapping.deco_class, self.__class__)

    ## TO DO - howdya test THIS?
    ## Implicitly, it gets tested and the descriptors it creates get tested.
    ## make_setting_descriptor is a classmethod.
    # def test_make_setting_descriptor(self):
    #     descr = DecoSettingsMapping.make_setting_descriptor('key')
    #     self.fail()

    def test__deco_class_settings_dict(self):
        """property. Can't use/call/test _deco_class_settings_dict till __init__"""
        od = self._settings_mapping._deco_class_settings_dict
        self.assertIs(od, self._settings_mapping._classname2SettingsData_dict[
            self._settings_mapping.deco_class.__name__]
        )
        self.assertEqual(list(self._settings_mapping),
                         ['enabled', 'folderol', 'my_setting', 'your_setting']
        )

    def test_registered_class_settings_repr(self):
        settings_repr = """
            DecoSettingsMapping.register_class_settings(
                TestDecoSettingsMapping,
                [DecoSetting('enabled', int, False, allow_falsy=True, allow_indirect=True, mutable=True, visible=True, pseudo_setting=False),
                 DecoSetting('folderol', str, '', allow_falsy=True, allow_indirect=False, mutable=True, visible=True, pseudo_setting=False),
                 DecoSetting('my_setting', str, 'on', allow_falsy=False, allow_indirect=True, mutable=True, visible=True, pseudo_setting=False),
                 DecoSetting('your_setting', str, 'off', allow_falsy=False, allow_indirect=False, mutable=False, visible=True, pseudo_setting=False),
                 DecoSetting('history', bool, False, allow_falsy=True, allow_indirect=False, mutable=True, visible=False, pseudo_setting=False)
            ])
        """
        self.assertEqual(
            collapse_whitespace(self._settings_mapping.registered_class_settings_repr()),
            collapse_whitespace(settings_repr)
        )

    def test__handlers(self):
        self.assertEqual(self._settings_mapping._handlers,
                         (('enabled',), ('history',)))

    def test__pre_call_handlers(self):
        self.assertEqual(self._settings_mapping._pre_call_handlers,
                         ('enabled',))

    def test__post_call_handlers(self):
        self.assertEqual(self._settings_mapping._post_call_handlers,
                         ('history',))

    def test__get_DecoSetting(self):
        for key in self._settings_mapping._deco_class_settings_dict:
            self.assertEqual(self._settings_mapping._get_DecoSetting(key),
                             self._settings_mapping._deco_class_settings_dict[key])
            self.assertEqual(key, self._settings_mapping._get_DecoSetting(key).name)

    def test___getitem__(self):
        """Test descriptors too"""
        mapping = self._settings_mapping
        self.assertEqual(mapping['enabled'], True)
        self.assertEqual(mapping['folderol'], 'bar')
        self.assertEqual(mapping['my_setting'], 'eek')
        self.assertEqual(mapping['your_setting'], "Howdy")

        self.assertEqual(mapping.enabled, True)
        self.assertEqual(mapping.folderol, 'bar')
        self.assertEqual(mapping.my_setting, 'eek')
        self.assertEqual(mapping.your_setting, "Howdy")

        def get_bad_item(bad_key):
            return mapping[bad_key]

        def get_bad_attr(bad_attr):
            return getattr(mapping, bad_attr)

        def get_hidden_item():
            return mapping['history']

        def get_hidden_attr():
            return mapping.history

        self.assertRaises(KeyError, get_bad_item, 'no_such_key')
        self.assertRaises(AttributeError, get_bad_attr, 'no_such_attr')

        self.assertRaises(KeyError, get_hidden_item)
        self.assertRaises(AttributeError, get_hidden_attr)

    def test___setitem__(self):
        """Test descriptors too.
        Test your_setting -- mutable=False"""
        mapping = self._settings_mapping

        mapping['enabled'] = False
        mapping['folderol'] = 'BAR'
        mapping['my_setting'] = 'OUCH'

        def set_item_not_mutable(s):
            mapping['your_setting'] = s

        self.assertRaises(ValueError, set_item_not_mutable, "HARK! Who goes there?")

        self.assertEqual(mapping['enabled'], False)
        self.assertEqual(mapping['folderol'], 'BAR')
        self.assertEqual(mapping['my_setting'], 'OUCH')
        self.assertEqual(mapping['your_setting'], "Howdy")      # not mutable, so not changed!

        # Now set back to mostly 'orig' values using descriptors
        mapping.enabled = True
        mapping.folderol = 'bar'
        mapping.my_setting = 'eek'

        def set_attr_not_mutable(s):
            mapping.your_setting = s

        self.assertRaises(ValueError, set_attr_not_mutable, "This won't work either.")

        self.assertEqual(mapping.enabled, True)
        self.assertEqual(mapping.folderol, 'bar')
        self.assertEqual(mapping.my_setting, 'eek')
        self.assertEqual(mapping.your_setting, "Howdy")

        mapping.__setitem__('your_setting', 'not howdy', _force_mutable=True)
        self.assertEqual(mapping.your_setting, "not howdy")

        # Now test setting a nonexistent key, & a nonexistent attr/descr
        def set_bad_item(bad_key, val):
            mapping[bad_key] = val

        self.assertRaises(KeyError, set_bad_item, 'no_such_key', 413)
        ## BUT The following does NOT raise an AttributeError
        # def set_bad_attr(bad_attr, val):
        #     setattr(mapping, bad_attr, val)
        #
        # self.assertRaises(AttributeError, set_bad_attr, 'no_such_attr', 495)
        mapping.no_such_attr = 495
        self.assertEqual(mapping.no_such_attr, 495)

        # Test setting settings with visible=False
        def set_hidden_item():
            mapping['history'] = False

        def set_hidden_attr():
            mapping.history = False

        self.assertRaises(KeyError, set_hidden_item)

        # Get value of history setting
        history_val = mapping.get_final_value('history', fparams=None)
        # You CAN add an attribute called 'history'
        #  BUT it is *not* the 'history' setting:
        mapping.history = not history_val
        self.assertEqual(mapping.history, not history_val)
        # The setting is unchanged:
        self.assertEqual(history_val, mapping.get_final_value('history', fparams=None))

        # Actually change the value:
        mapping.__setitem__('history', not history_val, _force_visible=True)
        # get new val of history
        new_val = mapping.get_final_value('history', fparams=None)
        self.assertEqual(new_val, not history_val)

    def test___len__(self):
        self.assertEqual(len(self._settings_mapping), 4)

    def test___iter__(self):
        names = [name for name in self._settings_mapping]
        self.assertEqual(names, ['enabled', 'folderol', 'my_setting', 'your_setting'])

    def test_items(self):
        items = [item for item in self._settings_mapping.items()]
        self.assertEqual(items,
                         [('enabled', self._settings_mapping['enabled']),
                          ('folderol', self._settings_mapping['folderol']),
                          ('my_setting', self._settings_mapping['my_setting']),
                          ('your_setting', self._settings_mapping['your_setting'])]
        )

    def test___contains__(self):
        self.assertIn('enabled', self._settings_mapping)
        self.assertIn('folderol', self._settings_mapping)
        self.assertIn('my_setting', self._settings_mapping)
        self.assertIn('your_setting', self._settings_mapping)

        self.assertNotIn('history', self._settings_mapping)
        self.assertNotIn('no_such_key', self._settings_mapping)

    def test___repr__(self):
        """
        Split into cases because this bug got fixed in Python 3.5:

        http://bugs.python.org/issue23775
        "Fix pprint of OrderedDict.
         Currently pprint prints the repr of OrderedDict if it fits in one line,
         and prints the repr of dict if it is wrapped.
         Proposed patch makes pprint always produce an output compatible
         with OrderedDict's repr.
        "
        The bugfix also affected tests in test_log_calls_more.py (see docstring there).
        """
        if (sys.version_info.major == 3 and sys.version_info.minor >= 5
           ) or sys.version_info.major > 3:     # :)
            the_repr = """
                DecoSettingsMapping(
                    deco_class=TestDecoSettingsMapping,
                    ** OrderedDict([
                        ('enabled', True),
                        ('folderol', 'bar'),
                        ('my_setting', 'eek'),
                        ('your_setting', 'Howdy')]) )
            """
        else:   # Py <= 3.4
            the_repr = """
                DecoSettingsMapping(
                    deco_class=TestDecoSettingsMapping,
                    ** {
                        'enabled': True,
                        'folderol': 'bar',
                        'my_setting': 'eek',
                        'your_setting': 'Howdy'} )
            """
        self.assertEqual(
            collapse_whitespace(repr(self._settings_mapping)),
            collapse_whitespace(the_repr),
        )

    def test___str__(self):
        ## print("self._settings_mapping str: %s" % str(self._settings_mapping))
        ##     {'folderol': 'bar', 'my_setting': 'eek', 'your_setting': 'Howdy', 'enabled': True}
        self.assertDictEqual(
            eval(str(self._settings_mapping)),
            {'folderol': 'bar', 'my_setting': 'eek', 'your_setting': 'Howdy', 'enabled': True}
        )

    def test_update(self):
        mapping = self._settings_mapping

        d = {'enabled': False, 'folderol': 'tomfoolery', 'my_setting': 'balderdash=', 'your_setting': "Goodbye."}
        mapping.update(**d)                                 # pass as keywords
        self.assertEqual(mapping.enabled, False)
        self.assertEqual(mapping.folderol, 'tomfoolery')
        self.assertEqual(mapping.my_setting, 'balderdash=')
        self.assertEqual(mapping.your_setting, 'Howdy')     # NOT changed, and no exception
        self.assertEqual(len(mapping), 4)

        mapping.enabled = not mapping.enabled
        mapping.folderol = 'nada'
        mapping.my_setting = "something-new"
        mapping.update(d)                                   # pass as dict
        self.assertEqual(mapping.enabled, False)
        self.assertEqual(mapping.folderol, 'tomfoolery')
        self.assertEqual(mapping.my_setting, 'balderdash=')
        self.assertEqual(mapping.your_setting, 'Howdy')     # NOT changed, and no exception
        self.assertEqual(len(mapping), 4)

        d1 = {'enabled': False, 'folderol': 'gibberish'}
        d2 = {'enabled': True, 'my_setting': 'hokum='}

        mapping.update(d1, d2)
        self.assertEqual(mapping.enabled, True)
        self.assertEqual(mapping.folderol, 'gibberish')
        self.assertEqual(mapping.my_setting, 'hokum=')

        mapping.update(d1, d2, **d)
        self.assertEqual(mapping.enabled, False)
        self.assertEqual(mapping.folderol, 'tomfoolery')
        self.assertEqual(mapping.my_setting, 'balderdash=')

        self.assertRaises(
            KeyError,
            mapping.update,
            no_such_setting=True
        )
        self.assertRaises(
            KeyError,
            mapping.update,
            history=True
        )

    def test_as_OrderedDict(self):
        self.assertDictEqual(
            OrderedDict([('enabled', True), ('folderol', 'bar'), ('my_setting', 'eek'), ('your_setting', 'Howdy')]),
            self._settings_mapping.as_OrderedDict()
        )

    def test_as_dict(self):
        self.assertDictEqual(self._settings_mapping.as_dict(),
                             {'folderol': 'bar', 'my_setting': 'eek', 'your_setting': 'Howdy', 'enabled': True})

    def test__get_tagged_value(self):
        mapping = self._settings_mapping
        mapping['enabled'] = "enabled_kwd"
        mapping['folderol'] = 'my_setting_kwd='
        mapping['my_setting'] = 'OUCH'

        self.assertEqual(mapping._get_tagged_value('enabled'), (True, 'enabled_kwd'))
        self.assertEqual(mapping._get_tagged_value('folderol'), (False, 'my_setting_kwd='))
        self.assertEqual(mapping._get_tagged_value('my_setting'), (False, 'OUCH'))
        self.assertEqual(mapping._get_tagged_value('your_setting'), (False, 'Howdy'))

        def bad_key():
            mapping._get_tagged_value('no_such_key')

        self.assertRaises(KeyError, bad_key)

    def test_get_final_value(self):
        mapping = self._settings_mapping
        v = mapping.get_final_value('enabled', fparams=None)
        self.assertEqual(v, True)

        mapping['enabled'] = 'enabled_kwd='
        d = {'enabled_kwd': 17}
        v = mapping.get_final_value('enabled', d, fparams=None)
        self.assertEqual(v, 17)

        def f(a, enabled_kwd=3):
            pass

        fparams = inspect.signature(f).parameters
        v = mapping.get_final_value('enabled', fparams=fparams)
        self.assertEqual(v, 3)

        def g(a, wrong_kwd='nevermind'):
            pass
        gparams = inspect.signature(g).parameters
        v = mapping.get_final_value('enabled', fparams=gparams)
        self.assertEqual(v, False)

        def h(a, enabled_kwd=[]):
            pass
        hparams = inspect.signature(h).parameters
        v = mapping.get_final_value('enabled', fparams=hparams)
        self.assertEqual(v, False)


import logging

class TestDecoSettingsMapping_set_reset_defaults(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._settings = (
            DecoSettingEnabled('enabled'),
            DecoSetting('number',          (str, int),     '12',          allow_falsy=True,  allow_indirect=False),
            DecoSetting('my_logger',       (str, logging.Logger), 'nix',  allow_falsy=False, allow_indirect=True),
            DecoSetting('your_setting',    str,            'off',         allow_falsy=False, allow_indirect=False,
                        mutable=False),
            DecoSettingHistory('history', visible=False),
        )
        DecoSettingsMapping.register_class_settings('TestDecoSettingsMapping_set_reset_defaults',
                                                    cls._settings)
        # # "'enabled' setting default value = False"
        # print("'enabled' setting default value =",
        #       cls._settings[0].default)

    def setUp(self):
        """
        """
        pass

    def test_set_reset_defaults(self):
        clsname = self.__class__.__name__

        settings_map = DecoSettingsMapping.get_deco_class_settings_dict(clsname)

        # try set 'my_logger' = '' ==> no effect (setting doesn't .allow_falsy)
        DecoSettingsMapping.set_defaults(clsname, {'my_logger': ''})
        self.assertEqual(settings_map['my_logger'].default, 'nix')

        # try setting 'your_setting' = 500 ==> no effect (not acceptable type)
        DecoSettingsMapping.set_defaults(clsname, {'your_setting': 500})
        self.assertEqual(settings_map['your_setting'].default, 'off')

        # try setting 'no_such_setting' = 0 ==> KeyError
        def set_no_such_setting():
            DecoSettingsMapping.set_defaults(clsname, {'no_such_setting': 0})
        self.assertRaises(KeyError, set_no_such_setting)

        # try setting 'history' = False ==> KeyError (setting not visible)
        def set_history():
            DecoSettingsMapping.set_defaults(clsname, {'history': False})
        self.assertRaises(KeyError, set_history)

        # set enabled=False, number=17 (int);
        #    check that .default of things in settings_map reflect this
        DecoSettingsMapping.set_defaults(clsname, dict(enabled=False, number=17))
        self.assertEqual(settings_map['enabled'].default, False)
        self.assertEqual(settings_map['number'].default, 17)
        self.assertEqual(settings_map['my_logger'].default, 'nix')
        self.assertEqual(settings_map['your_setting'].default, 'off')
        # self.assertEqual(settings_map['history'].default, 'True')

        # set enabled=True, number='100', your_setting='Howdy';
        #    check that .default of things in settings_map reflect this
        DecoSettingsMapping.set_defaults(clsname, dict(enabled=True, number='100', your_setting='Howdy'))
        self.assertEqual(settings_map['enabled'].default, True)
        self.assertEqual(settings_map['number'].default, '100')
        self.assertEqual(settings_map['my_logger'].default, 'nix')
        self.assertEqual(settings_map['your_setting'].default, 'Howdy')

        # reset, see that defaults are correct
        DecoSettingsMapping.reset_defaults(clsname)
        self.assertEqual(settings_map['enabled'].default, False)      # the default for DecoSettingEnabled
        self.assertEqual(settings_map['number'].default, '12')
        self.assertEqual(settings_map['my_logger'].default, 'nix')
        self.assertEqual(settings_map['your_setting'].default, 'off')
