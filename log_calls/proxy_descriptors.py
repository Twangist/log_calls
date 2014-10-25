__author__ = 'brianoneill'
__version__ = 'v0.1b6.7'
__doc__ = """
    <<<<<< TODO >>>>>>
    See docstrings for install_proxy_descriptor and KlassInstanceAttrProxy.
"""
from itertools import product, chain

__all__ = ['install_proxy_descriptor', 'KlassInstanceAttrProxy']


def install_proxy_descriptor(proxy_obj, attr_name_proxied_instance, descr_name, data=True, readonly=False):
    """
    Create and install (setattr) on proxy_obj a descriptor named descr_name,
    assuming proxy_obj has an attribute named attr_name_proxied_instance
    which 'points' to an object that already has an attr/descr named descr_name;
    the created descriptor will then just defer to that anterior attr/descr.

    Suppose a, b are instances of classes A, B resp.,
    and suppose b has an attr 'my_a' that points to a:
        assert b.my_a is a
    Thus proxy_obj == b,
         attr_name_proxied_instance == 'my_a'.
    Suppose a has an attribute 'x' which b wants to reflect
    aka proxy, so that the value of b.x will be (will invoke) a.x.
    b can set this up as follows:
        install_proxy_descriptor(b, 'my_a', 'x')   # b: b itself would say, self

    data: True iff we should create & install a data descriptor,
                   else create & install a non-data-descriptor.
    readonly: True iff created data descriptor should be readonly
                       (i.e. raise AttributeError on attempted 'set' operations).
    """
    class ProxyDataDescr():
        def __get__(this_descr, proxy, owner):
            "todo"
            ### print("**** descriptor %s __get__ called" % descr_name)
            return getattr(
                        getattr(proxy, attr_name_proxied_instance),
                        descr_name)

        def __set__(this_descr, proxy, value):
            "todo"
            if not readonly:
                setattr(
                    getattr(proxy, attr_name_proxied_instance),
                    descr_name,
                    value)
            else:
                # no can do:
                # TODO test!
                raise AttributeError("%s is read-only on %r" % (descr_name, proxy))

    class ProxyMethodDescr():
        def __get__(this_descr, proxy, owner):
            "todo"
            ### print("**** descriptor %s __get__ called" % descr_name)
            return getattr(
                        getattr(proxy, attr_name_proxied_instance),
                        descr_name)

    proxy_descr = (ProxyDataDescr if data else ProxyMethodDescr)()
    setattr(proxy_obj.__class__, descr_name, proxy_descr)


class KlassInstanceAttrProxy():
    """Attributes on (instances of) some other class Klass ==>
            readonly data descriptors on (instances of) this class.
    This class keeps a record of which other klasses it has already created
    descriptors for (classes_proxied, initially empty set).

    The transform '==>' is accomplished by install_proxy_descriptor.

    Note that the attributes of instances of Klass that are exposed this way
    can themselves be descriptors (e.g. properties).
    """
    # Only create descriptors on the class once:
    # for a given descr_name (attr name) they'd be the same :)
    klasses_proxied = set()
    # but ensure that different classes use disjoint attr/descr names
    descr_name2klass = {}       # map descr_name --> klass

    def __init__(self, *, klass_instance):
        """What makes these work is the klass_instance arg,
        which a descriptor uses to access a klass_instance
        and from that its attr of the same name."""
        self.deco_instance = klass_instance

        klassname = klass_instance.__class__.__name__
        if klassname not in self.klasses_proxied:
            # Create descriptors *** on the class ***, once only per class.
            # Same __get__/__set__ functions, called on different instances.
            # It doesn't work to create them on instances:
            #         setattr(self, ... ) doesn't fly.
            klass_descr_names = chain(product(klass_instance.get_descriptor_names(), {True}),
                                      product(klass_instance.get_method_descriptor_names(), {False}))
            klass_descr_names = list(klass_descr_names)
            # Make sure names in klass_descr_names is disjoint from descr_name2klass keys,
            # else somebody else gets clobbered (say who! which other klass)
            for descr_name, _ in klass_descr_names:
                if descr_name in self.descr_name2klass:
                    # Note: klassname is still not in klasses_proxied
                    raise AttributeError("attribute/descriptor-name %s already registered by class %s"
                                         % (descr_name, self.descr_name2klass[descr_name]))

            for descr_name, is_data in klass_descr_names:
                # Create & add descriptor to this class. readonly only matters if is_data
                install_proxy_descriptor(self, 'deco_instance', descr_name, data=is_data, readonly=is_data)

            # Record this class as 'already (successfully!) handled'
            self.klasses_proxied.add(klassname)
