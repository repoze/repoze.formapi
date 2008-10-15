from collections import defaultdict

import types
import converter


class Form(object):
    """Base form class. Optionally pass a dictionary as ``data`` and a
    WebOb-like request object as ``request``."""

    fields = {}

    def __init__(self, data=None, request=None):
        if data is None:
            data = defaultdict(lambda: None)

        self.request = request
        self.data = data

        if request is not None:
            params = request.params
        else:
            params = ()

        data, errors = converter.convert(params, self.fields)
        self.data.update(data)
        self.errors = errors

    def validate(self):
        """Validates the request against the form fields. Returns
        ``True`` if all fields validate, else ``False``."""

        if self.errors:
            return False

        # execute custom form validators
        for name, validator in type(self).__dict__.items():
            if getattr(validator, '__validator__', False):
                for error in validator(self):
                    converter.store_item(error.field, error.msg, self.errors)

        return not self.errors

class Proxy(object):
    """Proxy object; reads and writes to attributes are forwarded to
    the provided object. Descriptors are supported: they must read and
    write to ``self.context``. Note, that all attribute names are
    supported, including the name 'context'.

    Any object can be the context of a proxy.

    >>> class Content(object):
    ...     pass
    ...         
    
    >>> from repoze.formapi import Proxy
    
    >>> class ContentProxy(Proxy):
    ...     def get_test_descriptor(self):
    ...         return self.context.test_descriptor
    ...
    ...     def set_test_descriptor(self, value):
    ...         self.context.test_descriptor = value + 1
    ...
    ...     def get_get_only(self):
    ...         return self.context.test_get_only
    ...
    ...     test_descriptor = property(get_test_descriptor, set_test_descriptor)
    ...     test_get_only = property(get_get_only)
    
    >>> context = Content()
    >>> proxy = ContentProxy(context)

    We can read and write to the ``context`` attribute.
    
    >>> proxy.context = 42
    >>> proxy.context
    42

    Descriptors have access to the original context.
    
    >>> proxy.test_descriptor = 41
    >>> proxy.test_descriptor
    42

    Descriptors that only define a getter are supported.
    
    >>> proxy.test_get_only = 41
    >>> proxy.test_get_only
    41

    Proxies provide dictionary-access to attributes.

    >>> proxy['context']
    42

    >>> proxy.update({
    ...     'context': 41})

    >>> proxy.context
    41
    
    """

    def __init__(self, context):
        # instantiate a new proxy object from the base class, such
        # that we know that no descriptors are defined; this is required t
        proxy = self.__dict__['proxy'] = object.__new__(Proxy)
        proxy.__dict__['context'] = self.__dict__['_context'] = context

    def __getattr__(self, name):
        prop = type(self).__dict__.get(name)
        if prop is not None:
            # call getter in the context of the proxy object
            proxy = self.__dict__['proxy']
            return prop.fget(proxy)
        else:
            return getattr(self.__dict__['_context'], name)
        
    def __setattr__(self, name, value):
        prop = type(self).__dict__.get(name)
        if prop is not None:
            # property might be read-only (e.g. does not define a
            # setter); in this case we just set attribute on context.
            setter = prop.fset
            if setter is not None:
                # call setter in the context of the proxy object
                proxy = self.__dict__['proxy']
                return prop.fset(proxy, value)
        setattr(self.__dict__['_context'], name, value)

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def update(self, d):
        for name, value in d.items():
            setattr(self, name, value)
               
class ValidationError(Exception):
    """Represents a field validation error."""

    def __init__(self, field, msg):
        if not isinstance(msg, unicode):
            msg = unicode(msg)
        self.field = field
        self.msg = msg

    def __repr__(self):
        return '<%s field="%s" %s>' % (
            type(self).__name__, self.field, repr(self.msg))

    def __str__(self):
        return str(unicode(self))
    
    def __unicode__(self):
        return self.msg
    
def validator(*fields):
    def decorator(validator):
        def func(self):
            result = validator(self)
            if result is not None:
                if not isinstance(result, (
                    types.TupleType, types.ListType, types.GeneratorType)):
                    result = (result,)
                for field in fields:
                    for msg in result:
                        yield ValidationError(field, msg)
        func.__validator__ = True
        func.__name__ = validator.__name__
        return func
    return decorator

