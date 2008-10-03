from zope import interface
from zope import schema

class ValidationError(Exception):
    """Represents a field validation error."""

    def __init__(self, field, error_msg):
        if not isinstance(error_msg, unicode):
            error_msg = unicode(error_msg)
        self.field = field
        self.error_msg = error_msg

    def __repr__(self):
        return '<%s field="%s" %s>' % (
            type(self).__name__, self.field.__name__, repr(self.error_msg))

    def __str__(self):
        return str(self.error_msg)
    
    def __unicode__(self):
        return self.error_msg
    
class IField(schema.interfaces.IField):
    """Bound form field."""

    name = interface.Attribute(
        """Field name.""")

    value = interface.Attribute(
        """Field value.""")

    error = interface.Attribute(
        """Error message, or ``None`` if no error.""")
    
    def render():
        """Renders a form field widget for this field."""
        
class IForm(interface.Interface):
    """Form class."""

    def __init__(request=None, model=None, prefix=None, action=u""):
        """Creates new form instance. If ``model`` is non-trivial,
        it's expected to provide default form field values using
        attribute, then dictionary lookup."""

    def __iter__():
        """Yields bound form fields (see ``IField``)."""
        
    def validate():
        """Validate form. Returns a dictionary that maps field name to
        validation errors."""

    fields = interface.Attribute(
        """Returns an ``IFields`` instance for this form.""")
        
    action = interface.Attribute(
        """Form action string.""")

    submit = interface.Attribute(
        """Form submit name; if `prefix` is set, this will be
        '%s(prefix)s.submit', else 'submit'.""")
    
class IWidget(interface.Interface):
    """Callable which returns HTML for a form field. Should be
    registered as a component that adapts (form, field)."""
