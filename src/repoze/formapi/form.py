from collections import defaultdict

def convert(params, fields):
    return dict(params), dict((key, None) for key in params if not key)

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
        self.errors = errors
        
    def validate(self):
        if self.errors:
            return False

        # TODO: Execute custom form validators
        return True
