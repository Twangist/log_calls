__author__ = 'brianoneill'

from unittest import TestCase
from log_calls import DecoSetting, DecoSettingsMapping

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
        """WITH additional attributes
        (tested in iPython notebook Untitled0, seems to work just fine)"""
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
    def test_register_class_settings(self):
        self.fail()

    def test_make_setting_descriptor(self):
        self.fail()

    def test__deco_class_settings_dict(self):
        self.fail()

    def test___init__(self):
        self.fail()

    def test_registered_class_settings_repr(self):
        self.fail()

    def test_setting_names_list(self):
        self.fail()

    def test_is_setting(self):
        self.fail()

    def test___setitem__(self):
        self.fail()

    def test___getitem__(self):
        self.fail()

    def test___len__(self):
        self.fail()

    def test___iter__(self):
        self.fail()

    def test_items(self):
        self.fail()

    def test___contains__(self):
        self.fail()

    def test___repr__(self):
        self.fail()

    def test___str__(self):
        self.fail()

    def test_update(self):
        self.fail()

    def test_as_OrderedDict(self):
        self.fail()

    def test_as_dict(self):
        self.fail()

    def test__get_tagged_value(self):
        self.fail()

    def test_get_final_value(self):
        self.fail()
