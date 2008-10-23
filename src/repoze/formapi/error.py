from collections import defaultdict

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

    def __repr__(self):
        return repr(dict(self))
