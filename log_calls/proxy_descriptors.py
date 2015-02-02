__author__ = 'brianoneill'
__version__ = '0.1.14'
__doc__ = """
    See docstrings for install_proxy_descriptor and ClassInstanceAttrProxy.
"""
from itertools import product, chain

__all__ = ['install_proxy_descriptor', 'ClassInstanceAttrProxy' ]


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


class ClassInstanceAttrProxy():
    """Attributes on (instances of) some other class  ==>
            descriptors on (instances of) this class
            (data descriptors are readonly).
    The transform '==>' is accomplished by install_proxy_descriptor.

    This class keeps a record of which other classes it has already created
    descriptors for (_classes_and_attrs_proxied, initially empty set)
    -- a little naively,
       classname + marker + tuple(data_descriptor_names) + marker + tuple(method_descriptor_names).

    Note that the attributes of instances of other class that are exposed
    in this way can themselves be descriptors (e.g. properties).
    """
    # Only create descriptors on the class once,
    # for class of class_instance + these attributes/descr names:
    # for a given descr_name (attr name) they'd be the same :)
    _classes_and_attrs_proxied = set()

    def __init__(self, *, class_instance, data_descriptor_names, method_descriptor_names):
        """What makes these work is the class_instance arg,
        which a descriptor uses to access a class_instance
        and from that its attr of the same name."""
        self._proxied_instance_ = class_instance

        class_and_descr_names = (
            class_instance.__class__.__name__
            + '|'
            + ','.join(data_descriptor_names)
            + '|'
            + ','.join(method_descriptor_names)
        )
        if class_and_descr_names not in self._classes_and_attrs_proxied:
            # Create descriptors *** on the class ***, once only per class.
            # Same __get__/__set__ functions, called on different instances.
            # It doesn't work to create them on instances:
            #         setattr(self, ... ) doesn't fly.
            class_descr_names = chain(product(data_descriptor_names,   {True}),
                                      product(method_descriptor_names, {False})
            )
            for descr_name, is_data in list(class_descr_names):
                # Create & add descriptor to this class. readonly only matters if is_data
                install_proxy_descriptor(self, '_proxied_instance_', descr_name,
                                         data=is_data, readonly=is_data)

            # Record this class as 'already (successfully!) handled'
            self._classes_and_attrs_proxied.add(class_and_descr_names)
