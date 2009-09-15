from repoze.formapi import marshalling

import types
import re

def get_instances_of(type, *bases):
    for base in bases:
        for value in base.__dict__.values():
            if isinstance(value, type):
                yield value
        for value in get_instances_of(type, *base.__bases__):
            yield value

class Validator(object):
    """Wrapper for validators.

    This calls a validator object (usually a method) and collects all it's
    errors. It also sets a flag that the form library can use to know that it
    is a validator."""

    def __init__(self, func, *fields):
        self.func = func
        # Fields can be empty, in that case we want to have and empty path
        if not fields:
            self.fieldpaths = ((),)
        else:
            self.fieldpaths = [f.split('.') for f in fields]

    def __call__(self, form):
        for error in self.func(form):
            for fieldpath in self.fieldpaths:
                yield (fieldpath, error)

class Action(object):
    def __init__(self, action, name=None, submitted=False):
        self.action = action
        self.name = name
        self.submitted = submitted

    @property
    def __call__(self):
        return self.action

    def __nonzero__(self):
        return self.submitted

    def __repr__(self):
        return '<%s name="%s" submitted="%s">' % (
            type(self).__name__, self.name or "", str(bool(self.submitted)))

class metaclass(type):
    def __init__(kls, name, bases, dict):
        kls.validators = tuple(get_instances_of(Validator, kls))
        kls.actions = tuple(get_instances_of(Action, kls))

class Form(object):
    """Base form class. Optionally pass a dictionary as ``data`` and a
    WebOb-like request object as ``request``."""

    __metaclass__ = metaclass

    fields = {}
    status = None
    prefix = None
    action = None

    def __init__(self, data=None, context=None, request=None, params=None, prefix=None):
        self.context = context
        self.request = request

        if context is not None:
            if data is not None:
                raise ValueError(
                    "Can't provide both ``data`` and ``context``.")

            # proxy the context object
            data = Proxy(context)

        self.data = Data(data)

        if prefix is None:
            prefix = self.prefix

        if request is not None:
            if params is not None:
                raise ValueError(
                    "Can't provide both ``params`` and ``request``.")
            params = request.params

        # find action parameters
        action_params = {}
        if prefix is not None and params is not None:
            re_prefix = re.compile(r'^%s[._-](?P<name>.*)' % prefix)
            for key, value in params.items():
                if key == prefix:
                    action_params[None] = value
                else:
                    m = re_prefix.search(key)
                    if m is not None:
                        action_params[m.group('name')] = value

        # initialize form actions
        actions = self.actions = []
        for action in type(self).actions:
            name = action.name
            action = Action(action.__call__, name, name in action_params)
            actions.append(action)
            if action:
                self.action = action

        # conditionally apply request parameters if:
        # 1. no prefix has been set
        # 2. there is a submitted action
        # 3. there are no defined actions, but a default action was submitted
        if params is not None and (
            prefix is None or \
            filter(None, actions) or \
            len(actions) == 0 and action_params.get(None) is not None):
            params = params.items()
        else:
            params = ()

        # marshall request parameters
        data, errors = marshalling.marshall(params, self.fields)

        if len(params):
            self.data.update(data)

        self.errors = errors
        self.prefix = prefix

    def __call__(self):
        """Calls the first submitted action and returns the value."""

        if self.action is not None:
            self.status = self.action(self, self.data)
        return self.status

    def validate(self):
        """Validates the request against the form fields. Returns
        ``True`` if all fields validate, else ``False``."""
        for validator in self.validators:
            for field_path, validation_error in validator(self):
                errors = self.errors
                for field in field_path:
                    errors = errors[field]
                errors += validation_error

        return not bool(self.errors)

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

class Data(list):
    """Form data object with dictionary-like interface. If initialized
    with a ``data`` object, this will be used to provide default
    values, if not set in the ``request``. Updates to the object are
    transient until the ``save`` method is invoked."""

    def __init__(self, data):
        if data is not None:
            self.append(data)
        self.append({})

    def __getitem__(self, name):
        for data in reversed(self):
            try:
                value = data[name]
            except KeyError:
                continue

            if value is not marshalling.missing:
                return value

    def __setitem__(self, name, value):
        self.tail[name] = value

    @property
    def tail(self):
        return list.__getitem__(self, -1)

    @property
    def head(self):
        return list.__getitem__(self, 0)

    def update(self, data):
        """Updates the dictionary by appending ``data`` to the list at
        the position just before the current dictionary."""

        self.insert(-1, data)

    def save(self):
        """Flattens the dictionary, saving changes to the data object."""

        while len(self) > 1:
            for name, value in self.pop(1).items():
                self.head[name] = value
        self.append({})

class Proxy(object):
    """Proxy object; reads and writes to attributes are forwarded to
    the provided object. Descriptors are supported: they must read and
    write to ``self.context``. Note, that all attribute names are
    supported, including the name 'context'.

    Any object can be the context of a proxy.

    >>> class Content(object):
    ...     pass
    
    >>> from repoze.formapi import Proxy
    
    >>> class ContentProxy(Proxy):
    ...     def get_test_descriptor(self):
    ...         return self.test_descriptor
    ...
    ...     def set_test_descriptor(self, value):
    ...         self.test_descriptor = value + 1
    ...
    ...     def get_get_only(self):
    ...         return self.test_get_only
    ...
    ...     test_descriptor = property(get_test_descriptor, set_test_descriptor)
    ...     test_get_only = property(get_get_only)
    
    >>> context = Content()
    >>> proxy = ContentProxy(context)

    We can read and write to the ``context`` attribute.
    
    >>> proxy.test = 42
    >>> proxy.test
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

    >>> proxy['test']
    42

    >>> proxy['test'] = 41
    >>> proxy.test
    41
    """

    def __init__(self, context):
        # instantiate a base proxy object with this context
        serf = object.__new__(Proxy)
        object.__setattr__(serf, '_context', context)
        object.__setattr__(self, '_context', context)
        object.__setattr__(self, '_serf', serf)

    def __getattribute__(self, name):
        prop = object.__getattribute__(type(self), '__dict__').get(name)
        if prop is not None:
            # call getter in the context of the proxy object
            serf = object.__getattribute__(self, '_serf')
            return prop.fget(serf)
        else:
            return getattr(
                object.__getattribute__(self, '_context'), name)

    def __setattr__(self, name, value):
        prop = object.__getattribute__(type(self), '__dict__').get(name)
        if prop is not None:
            # property might be read-only (e.g. does not define a
            # setter); in this case we just set attribute on context.
            setter = prop.fset
            if setter is not None:
                # call setter in the context of the proxy object
                serf = object.__getattribute__(self, '_serf')
                return prop.fset(serf, value)
        setattr(
            object.__getattribute__(self, '_context'), name, value)

    __getitem__ = __getattribute__
    __setitem__ = __setattr__
    
def action(name):
    if isinstance(name, types.FunctionType):
        return Action(name)
    else:
        def decorator(action):
            return Action(action, name)
        return decorator

def validator(*args):
    # If the first (and only) argument is a callable process it
    if len(args) == 1 and callable(args[0]):
        return Validator(args[0])
    # Treat the args as field names and prepare a wrapper
    else:
        return lambda func: Validator(func, *args)
