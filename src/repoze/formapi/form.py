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

    def __init__(self, request=None, context=None, prefix=None, action=u""):
        fields = []

        self.action = action
        if prefix is not None:
            self.submit = "%s.submit" % prefix
        else:
            self.submit = "submit"
        
        # merge dicts
        items = type(self).__dict__.items()
        if context is not None:
            items.extend(type(context).__dict__.items())

        # initialize field names
        for name, field in items:
            if name.startswith('_'):
                continue
            
            if schema.interfaces.IField.providedBy(field):
                field.__name__ = name
                fields.append(field)

        # set form field values on form instance copy
        form = copy.copy(self)
        for field in fields:
            name = field.__name__
            if prefix is not None:
                name = ".".join((prefix, name))
            if request is not None:
                value = request.params.get(name)
            elif context is not None:
                value = context.__dict__.get(field.__name__)
            else:
                value = None
            setattr(form, field.__name__, value)
            
        # validate
        errors = []
        for name, validator in type(self).__dict__.items():
            if getattr(validator, '__validator__', False):
                for error in validator(form):
                    errors.append(error)

        errors_by_field = {}
        for error in errors:
            errors_by_field.setdefault(error.field.__name__, []).append(error)

        def iterator():
            for field in fields:
                errors = errors_by_field.get(field.__name__, ())
                yield bind_field(form, field, field.__name__, errors)
            
        self.__iterator__ = iterator
        
    def __iter__(self):
        return self.__iterator__()

    def validate(self):
        return dict((field.__name__, field.errors) for field in self \
                    if field.errors)

    @property
    def fields(self):
        return Fields(self)
    
def bind_field(form, field, name, errors):
    field = copy.copy(field)
    
    field.name = field.__name__ = name
    field.label = field.title
    field.help = field.description
    field.error = u" ".join(
        unicode(error) for error in errors) or None
    field.value = getattr(form, field.__name__)
    field.errors = errors
    
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
        
