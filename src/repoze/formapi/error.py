from collections import defaultdict

class Errors(unicode):
    """Container for errors.

    Each error will be present in it's `messages` list. Dictionary lookup can
    be used to get at errors which are specific to a field. 

    Note that structure will automatically create entries for non-existing
    keys. This is done to make access from templates etc. easier and less
    fragile.

      >>> from repoze.formapi.error import Errors
      >>> errors = Errors()

    The `errors` object is a unicode string that inhibits a dict-like
    behavior, too.
    
      >>> isinstance(errors, unicode)
      True

    Any dict-entry returns a new `errors`-object.
    
      >>> isinstance(errors[None], Errors)
      True

    Errors may be appended to the object using the ``append`` method.
    
      >>> errors.append("Abc.")
      >>> errors.append("Def.")

      >>> errors.messages
      ['Abc.', 'Def.']

    We can iterate through the errors object.

      >>> tuple(errors)
      ('Abc.', 'Def.')

    The string representation of the object is a concatenation of the
    individual error messages.
    
      >>> unicode(errors)
      u'Abc. Def.'

      >>> len(errors)
      9
      
    """

    def __init__(self, *args, **kwargs):
        self.dict = defaultdict(Errors, *args, **kwargs)
        self.messages = []

    def __nonzero__(self):
        return len(self.dict) or len(self.messages)

    def __repr__(self):
        return repr(unicode(self))

    def __getitem__(self, name):
        return self.dict[name]

    def __unicode__(self):
        return u" ".join(self.messages)

    def __str__(self):
        return str(unicode(self))

    def __iter__(self):
        return iter(self.messages)

    def __len__(self):
        return len(unicode(self))
    
    def append(self, error):
        self.messages.append(error)
