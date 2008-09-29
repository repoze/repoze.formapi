from zope import interface
from zope import component
from zope import schema

import interfaces
import copy

def validator(*fields):
    def decorator(validator):
        def func(self):
            msg = validator(self)
            if msg is not None:
                for field in fields:
                    yield interfaces.ValidationError(field, msg)
        func.__validator__ = True
        func.__name__ = validator.__name__
        return func
    return decorator

class Form(object):
    interface.implements(interfaces.IForm)

    def __init__(self, request, model=None, prefix=None):
        # initialize field names
        for name, field in type(self).__dict__.items():
            if schema.interfaces.IField.providedBy(field):
                field.__name__ = name

        # set form field values
        for field in self:
            name = field.__name__
            if prefix is not None:
                name = ".".join(prefix, name)
            value = request.params.get(name)
            if value is None and model is not None:
                value = getattr(model, field.__name__, None)
            setattr(self, field.__name__, value)

    def __iter__(self):
        errors = self.validate()
        for name, field in type(self).__dict__.items():
            if schema.interfaces.IField.providedBy(field):
                error = u" ".join(
                    unicode(error) for error in errors.get(name, ()))
                yield bind_field(self, field, name, error or None)

    def validate(self):
        errors = []
        for name, validator in type(self).__dict__.items():
            if getattr(validator, '__validator__', False):
                for error in validator(self):
                    errors.append(error)

        by_field = {}
        for error in errors:
            by_field.setdefault(error.field.__name__, []).append(error)
                    
        return by_field

def bind_field(form, field, name, error):
    field = copy.copy(field)
    
    field.name = field.__name__ = name
    field.error = error
    field.value = getattr(form, field.__name__)
        
    def render():
        return component.getMultiAdapter(
            (form, field), interfaces.IWidget)

    field.render = render
        
    return field

class Fields(object):
    """Form fields class which provides attribute access to form field
    objects."""

    def __init__(self, form):
        for field in form:
            setattr(self, field.__name__, field)
        
