__author__ = "Brian O'Neill"  # BTO
__version__ = 'v0.1.10-b8'
__doc__ = """
    v0.1.10-b7 -- 100% coverage of deco_settings.py
"""

from unittest import TestCase
from log_calls import DecoSetting, DecoSettingsMapping
from collections import OrderedDict
import inspect

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
        self.assertEqual(self.info_plain._user_attrs, [])

    def test___init__2(self):
        """WITH additional attributes."""
        self.assertEqual(self.info_extended.name, 'extended')
        self.assertEqual(self.info_extended.final_type, tuple)
        self.assertEqual(self.info_extended.default, ('Joe', "Schmoe"))
        self.assertEqual(self.info_extended.allow_falsy, True)
        self.assertEqual(self.info_extended.allow_indirect, False)
        self.assertEqual(self.info_extended.mutable, True)
        self.assertEqual(self.info_extended._user_attrs, ['extra1', 'extra2', 'extra3'])
        self.assertEqual(self.info_extended.extra1, 'Tom')
        self.assertEqual(self.info_extended.extra2, 'Dick')
        self.assertEqual(self.info_extended.extra3, 'Harry')

    def test___repr__1(self):
        plain_repr = "DecoSetting('set_once', int, 15, allow_falsy=True, allow_indirect=True, mutable=False)"
        self.assertEqual(repr(self.info_plain), plain_repr)

    def test___repr__2(self):
        ext_repr = "DecoSetting('extended', tuple, ('Joe', 'Schmoe'), allow_falsy=True, allow_indirect=False, " \
                   "mutable=True, extra1='Tom', extra2='Dick', extra3='Harry')"
        self.assertEqual(repr(self.info_extended), ext_repr)


##############################################################################
# DecoSetting tests
##############################################################################

class TestDecoSettingsMapping(TestCase):

    # _settings = (
    #     DecoSetting('enabled',          int,            False,         allow_falsy=True,  allow_indirect=True),
    #     DecoSetting('folderol',         str,            '',            allow_falsy=True,  allow_indirect=False),
    #     DecoSetting('my_setting',       str,            'on',          allow_falsy=False, allow_indirect=True),
    #     DecoSetting('your_setting',     str,            'off',         allow_falsy=False, allow_indirect=False,
    #                 mutable=False),
    # )
    # DecoSettingsMapping.register_class_settings('TestDecoSettingsMapping',
    #                                             _settings)

    # placeholder:
    _settings_mapping = OrderedDict()

    @classmethod
    def setUpClass(cls):
        cls._settings = (
            DecoSetting('enabled',          int,            False,         allow_falsy=True,  allow_indirect=True),
            DecoSetting('folderol',         str,            '',            allow_falsy=True,  allow_indirect=False),
            DecoSetting('my_setting',       str,            'on',          allow_falsy=False, allow_indirect=True),
            DecoSetting('your_setting',     str,            'off',         allow_falsy=False, allow_indirect=False,
                        mutable=False),
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
            your_setting='Howdy'
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

    ## TODO howdya test THIS?
    ## Implicitly, it gets tested and the descriptors it creates get tested.
    ##classmethod.
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
            DecoSettingsMapping.register_class_settings([
                DecoSetting('enabled', int, False, allow_falsy=True, allow_indirect=True, mutable=True),
                DecoSetting('folderol', str, '', allow_falsy=True, allow_indirect=False, mutable=True),
                DecoSetting('my_setting', str, 'on', allow_falsy=False, allow_indirect=True, mutable=True),
                DecoSetting('your_setting', str, 'off', allow_falsy=False, allow_indirect=False, mutable=False)
            ])
        """
        self.assertEqual(
            collapse_whitespace(self._settings_mapping.registered_class_settings_repr()),
            collapse_whitespace(settings_repr)
        )

    def test_setting_names_list(self):
        self.assertEqual(list(self._settings_mapping.setting_names_list()),
                         ['enabled', 'folderol', 'my_setting', 'your_setting']
        )

    def test_is_setting(self):
        self.assertTrue(self._settings_mapping.is_setting('enabled'))
        self.assertTrue(self._settings_mapping.is_setting('folderol'))
        self.assertTrue(self._settings_mapping.is_setting('my_setting'))
        self.assertTrue(self._settings_mapping.is_setting('your_setting'))
        self.assertFalse(self._settings_mapping.is_setting('no_such_setting'))

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

        self.assertRaises(KeyError, get_bad_item, 'no_such_key')
        self.assertRaises(AttributeError, get_bad_attr, 'no_such_attr')

    def test___setitem__(self):
        """Test descriptors too.
        Test your_setting -- mutable=False"""
        mapping = self._settings_mapping

        mapping['enabled'] = False
        mapping['folderol'] = 'BAR'
        mapping['my_setting'] = 'OUCH'

        def set_item_not_mutable(s):
            mapping['your_setting'] = s

        self.assertRaises(AttributeError, set_item_not_mutable, "HARK! Who goes there?")

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

        self.assertRaises(AttributeError, set_attr_not_mutable, "This won't work either.")

        self.assertEqual(mapping.enabled, True)
        self.assertEqual(mapping.folderol, 'bar')
        self.assertEqual(mapping.my_setting, 'eek')
        self.assertEqual(mapping.your_setting, "Howdy")

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
        self.assertNotIn('no_such_key', self._settings_mapping)

    def test___repr__(self):
        the_repr = """
            DecoSettingsMapping(
                deco_class=TestDecoSettingsMapping,
                ** {       'enabled': True,
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
        d = {'enabled': False, 'folderol': 'tomfoolery', 'my_setting': 'balderdash='}
        mapping.update(**d)
        self.assertEqual(mapping.enabled, False)
        self.assertEqual(mapping.folderol, 'tomfoolery')
        self.assertEqual(mapping.my_setting, 'balderdash=')

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
