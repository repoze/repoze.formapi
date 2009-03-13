from collections import defaultdict

class Errors(object):
    """Container for errors.

    Each error will be present in it's `messages` list. Dictionary lookup can
    be used to get at errors which are specific to a field. 

    Note that structure will automatically create entries for non-existing
    keys. This is done to make access from templates etc. easier and less
    fragile.

      >>> from repoze.formapi.error import Errors
      >>> errors = Errors()

    The `errors` object is an object which can easily be converted to unicode
    and that inhibits a dict-like behavior, too.
    
      >>> unicode(errors)
      u''

    Any dict-entry returns a new `errors`-object.
    
      >>> isinstance(errors[None], Errors)
      True

    Errors may be appended to the object using the add operator.
    
      >>> errors += "Abc."
      >>> errors += "Def."

      >>> errors[0]
      'Abc.'

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

    _messages = _dict = None

    def __init__(self, *args, **kwargs):
        self._dict = defaultdict(Errors, *args, **kwargs)
        self._messages = []

    def __nonzero__(self):
        return len(self._dict) or len(self._messages)

    def __repr__(self):
        return repr(unicode(self))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._messages[key]
        return self._dict[key]

    def __unicode__(self):
        return u" ".join(self._messages)

    def __str__(self):
        return str(unicode(self))

    def __iter__(self):
        return iter(self._messages)

    def __len__(self):
        return len(unicode(self))

    def __add__(self, error):
        self._messages.append(error)
        return self

    def __getattribute__(self, name):
        if name in type(self).__dict__:
            return object.__getattribute__(self, name)
        raise AttributeError(name)

