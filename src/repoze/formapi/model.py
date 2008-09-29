from zope import interface
from zope import schema

import interfaces

def validator(field):
    def decorator(validator):
        def func(self):
            msg = validator(self)
            if msg is not None:
                raise interfaces.ValidationError(field, msg)
        func.__validator__ = True
        func.__name__ = validator.__name__
        return func
    return decorator

class Model(object):
    interface.implements(interfaces.IModel)

    def __init__(self, request):
        # initialize validator instance attributes
        for name, field in self.get_fields():
            setattr(self, name, request.params.get(name))
            field.__name__ = name

    def get_fields(self):
        for name, field in type(self).__dict__.items():
            if schema.interfaces.IField.providedBy(field):
                yield name, field

    def validate_form(self):
        errors = []
        for name, validator in type(self).__dict__.items():
            if getattr(validator, '__validator__', False):
                try:
                    validator(self)
                except interfaces.ValidationError, error:
                    errors.append(error)
        return tuple(errors)
