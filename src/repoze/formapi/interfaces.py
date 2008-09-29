from zope import interface

class ValidationError(Exception):
    """Validation error. Represents one or more validation errors,
    formatted as ``(field, error_msg)``."""

    def __init__(self, field, error_msg):
        self.field = field
        self.error_msg = error_msg

    def __repr__(self):
        return '<%s field="%s" %s>' % (
            type(self).__name__, self.field.__name__, repr(self.error_msg))

class IField(interface.Interface):
    """Form field."""
    
    label = interface.Attribute(
        """Field label.""")

    description = interface.Attribute(
        """Field description.""")

    value = interface.Attribute(
        """Field value.""")

    def render():
        """Renders a form field widget for this field."""
        
class IModel(interface.Interface):
    """Form model."""

    def __init__(request):
        """Initialize model."""

    def validate_form():
        """Validate all form fields."""

class IForm(interface.Interface):
    """Form."""

    def __init__(model, context=None, prefix=None):
        """Creates new form object with fields based on the provided
        ``model`` (see ``IModel``). If ``context`` is non-trivial,
        it's expected to provide form field values using attribute,
        then dictionary lookup."""
    
    def validate(request):
        """Validate form with values from the passed
        request-object. Raises a validation error if there were errors
        (exception instance provides a list-like interface to
        validation errors."""

