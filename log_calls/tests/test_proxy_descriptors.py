__author__ = 'brianoneill'
__version__ = '0.1.11'

from unittest import TestCase
from log_calls import install_proxy_descriptor, ClassInstanceAttrProxy


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Classes A, B used by TestInstall_proxy_descriptor;
# A used by TestClassInstanceAttrProxy
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class A():
    def __init__(self, x):
        self.x = x
        self._counter = 0

    @property
    def counter(self):
        self._counter += 1
        return self._counter

    @counter.setter
    def counter(self, val):
        self._counter = val

    def my_method(self):
        return self.x * self.x


class B():
    def __init__(self, A_instance):
        self.A_instance = A_instance

#----------------------------------------------------------------------------
# Test class for function install_proxy_descriptor
#----------------------------------------------------------------------------


class TestInstall_proxy_descriptor(TestCase):

    # create ProxyDataDescr
    def test_install_proxy_descriptor(self):
        a = A(5)
        b = B(a)

        # create ProxyDataDescr readonly
        install_proxy_descriptor(b, "A_instance", "counter", data=True, readonly=True)
        a_count = a.counter
        self.assertEqual(a_count, 1)
        b_count = b.counter
        self.assertEqual(b_count, 2)

        a.counter = 7
        self.assertEqual(a.counter, 8)

        def set_b_counter():
            b.counter = 17

        self.assertRaises(
            AttributeError,
            set_b_counter)

        # create ProxyDataDescr read/write
        b2 = B(a)
        install_proxy_descriptor(b, "A_instance", "counter", data=True, readonly=False)
        self.assertEqual(b2.counter, 9)
        b2.counter = -1
        self.assertEqual(a.counter, 0)

        # create ProxyMethodDescr
        install_proxy_descriptor(b, "A_instance", "my_method", data=False)
        self.assertEqual(b.my_method(), 25)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# A1 just like A
# but has get_descriptor_names, get_method_descriptor_names classmethods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class A1(A):
    @classmethod
    def get_descriptor_names(cls):
        return ['counter', 'x']

    @classmethod
    def get_method_descriptor_names(cls):
        return ['my_method']


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# A2 extends A1
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class A2(A1):
    @classmethod
    def get_descriptor_names(cls):
        return ['filter', 'inverse_filter'] + super().get_descriptor_names()

    @classmethod
    def get_method_descriptor_names(cls):
        return super().get_method_descriptor_names()

    def __init__(self, x, filter='Leavenworth'):
        self._filter = filter
        super().__init__(x)

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, val):
        self._filter = val

    @property
    def inverse_filter(self):
        return self._filter[::-1]


#----------------------------------------------------------------------------
# Test class for ClassInstanceAttrProxy
#----------------------------------------------------------------------------
class TestClassInstanceAttrProxy(TestCase):
    # def __init__(self, *, klass_instance):

    def test_ClassInstanceAttrProxy_1(self):
        # A1 just like A but has get_descriptor_names, get_method_descriptor_names classmethods
        a1_1 = A1(7)
        a1_2 = A1(1000)
        proxy1 = ClassInstanceAttrProxy(class_instance=a1_1)
        proxy2 = ClassInstanceAttrProxy(class_instance=a1_2)
        # These have descriptors 'counter', 'x', 'my_method'
        self.assertEqual(proxy1.counter, 1)
        self.assertEqual(proxy1.x, 7)
        self.assertEqual(proxy1.my_method(), 49)

        for i in range(4):
            proxy2.counter
        self.assertEqual(proxy2.counter, 5)
        self.assertEqual(proxy2.x, 1000)
        self.assertEqual(proxy2.my_method(), 1000000)

        self.assertEqual(proxy1.counter, 2)

        def try_set_counter(proxy):
            proxy.counter = 5000

        self.assertRaises(AttributeError,
                          try_set_counter,
                          proxy1)
        self.assertRaises(AttributeError,
                          try_set_counter,
                          proxy2)
        # A2 subclasses A1, adds method descriptors 'filter', 'inverse_filter'
        a2 = A2(1729)
        proxy_a2 = ClassInstanceAttrProxy(class_instance=a2)
        a2.counter      # counter now 1
        self.assertEqual(proxy_a2.counter, 2)
        self.assertEqual(proxy_a2.x, 1729)
        self.assertEqual(proxy_a2.my_method(), 1729 * 1729)

        self.assertEqual(proxy_a2.filter, "Leavenworth")
        self.assertEqual(proxy_a2.inverse_filter, "htrownevaeL")
