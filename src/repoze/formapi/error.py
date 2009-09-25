from repoze.formapi.py24 import defaultdict
from repoze.formapi.py24 import any

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
      
    The truth value of the errors object is based on the error messages it or
    it's sub errors contain.

      >>> bool(errors)
      True

    If there are no error messages the truth value will be false regardless
    even when there are error keys.

      >>> errors = Errors()
      >>> name_error = errors['name']
      >>> bool(errors)
      False

    Two errors instances are considered equal when they have the same keys with
    the same messages.

      >>> a = Errors()
      >>> a['foo'].append('Error')
      >>> b = Errors()
      >>> b['foo'].append('Error')
      >>> a  == b
      True

    Adding an error to one makes them unequal.

      >>> a['bar'].append('Error')
      >>> a == b
      False

    We can use the standard dictionary ``get`` method.

      >>> a.get('foo')
      <Errors: ['Error'], defaultdict(<class 'repoze.formapi.error.Errors'>, {})>
      >>> a.get('boo', False)
      False

    """

    _messages = _dict = None

    def __init__(self, *args, **kwargs):
        self._dict = defaultdict(Errors, *args, **kwargs)
        self._messages = []

    def __nonzero__(self):
        return bool(self._messages) or any(self._dict.itervalues())

    def __repr__(self):
         return '<Errors: %r, %r>' % (self._messages, self._dict)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._messages[key]
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict
    has_key = __contains__

    def __unicode__(self):
        return u" ".join(self._messages)

    def __str__(self):
        return str(unicode(self))

    def __iter__(self):
        return iter(self._messages)

    def __len__(self):
        return len(unicode(self))

    def __add__(self, error):
        self.append(error)
        return self

    def __getattr__(self, name):
        if name in type(self).__dict__:
            return object.__getattribute__(self, name)
        raise AttributeError(name)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self._messages == other._messages and self._dict == other._dict

    def append(self, error):
        self._messages.append(error)

    def get(self, key, default=None):
        assert isinstance(key, basestring), "Key must be a string."
        return self._dict.get(key, default)
