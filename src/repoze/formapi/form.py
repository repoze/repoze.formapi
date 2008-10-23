from collections import defaultdict

def convert(params, fields):
    return dict(params), dict((key, None) for key in params if not key)

class FieldValidator(object):
    """Wrapper for validators.

    This calls a validator object (usually a method) and collects all it's
    errors. It also sets a flag that the form library can use to know that it
    is a validator."""

    is_validator = True

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

def validator(*args):
    # If the first (and only) argument is a callable process it
    if len(args) == 1 and callable(args[0]):
        return FieldValidator(args[0])
    # Treat the args as field names and prepare a wrapper
    else:
        return lambda func: FieldValidator(func, *args)
            

class Errors(defaultdict):
    '''Container for errors.

    Each error will be present in it's `messages` list. Dictionary lookup can
    be used to get at errors which are specific to a field. 

    Note that structure will automatically create entries for non-existing
    keys. This is done to make access from templates etc. easier and less
    fragile.'''

    def __init__(self, *args, **kwargs):
        super(Errors, self).__init__(Errors, *args, **kwargs)
        self.messages = []

    def append(self, error):
        self.messages.append(error)

    def __nonzero__(self):
        return len(self.messages) or len(self)

class Form(object):
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
        self.errors = Errors(errors)
        
    def validate(self):
        for validator in self.__class__.__dict__.itervalues():
            if not getattr(validator, 'is_validator', False):
                continue

            for field_path, validation_error in validator(self):
                errors = self.errors
                for field in field_path:
                    errors = errors[field]
                errors.messages.append(validation_error)
            
        if bool(self.errors):
            return False
        # TODO: Execute custom form validators
        return True
