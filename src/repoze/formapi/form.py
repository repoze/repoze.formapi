from collections import defaultdict

import types

def convert(params, fields):
    """XXX: Temporary implementation."""
    
    return dict(params), dict((key, None) for key in params if not key)

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

        data, errors = convert(params, self.fields)
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
                    # XXX: implement traversing of error dictionary
                    # and handling of sequence types
                    self.errors[error.field] = error.msg

        return not self.errors

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

