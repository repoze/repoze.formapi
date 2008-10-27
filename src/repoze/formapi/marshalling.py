from collections import defaultdict

from repoze.formapi.error import Errors

MISSING = object()

def marshall(params, fields):
    """marshall(params, fields) -> data, errors

    This function converts and validates the ``params`` tuple of
    (name, value) pairs.  The data converted is returned in the
    ``data`` dict.  Errors encountered during conversion are set in
    the ``errors`` dict.

    The ``fields`` parameter is used to describe the data
    structure. It's a nested dictionary that ends in simple types, or
    a list of such, e.g.

        >>> fields = {
        ...     "user": {
        ...         "name": str,
        ...         "nick": str,
        ...         "age": int,
        ...     }
        ... }

    Using this ``schema-like`` structure, we can convert a list of
    form request parameters into a data structure (field marshalling).

        >>> params = (
        ...     ("user.name", "Fred Kaputnik"),
        ...     ("user.nick", "fred"),
        ...     ("user.age", 42))

    Note that the keys of the parameter tuples are dotted paths.

        >>> from repoze.formapi.marshalling import marshall
        >>> data, errors = marshall(params, fields)

    Since all the tuples in ``params`` are valid, we expect no
    validation errors::

        >>> len(errors)
        0

    To get to the marshalled field data, we use a similar approach.

        >>> data['user']['name']
        'Fred Kaputnik'
        >>> data['user']['nick']
        'fred'
        >>> data['user']['age']
        42

    To illustrate error handling, we can violate the validation
    constraint of the ``age`` field.

        >>> data, errors = marshall((("user.age", "ten"),), fields)
        
        >>> data['user']['age'] is None
        True
        
        >>> errors['user']['age'].messages[0]
        "invalid literal for int() with base 10: 'ten'"

    Note that the ``data`` and ``errors`` dictionaries provide a
    default value of ``None`` for missing entries.

        >>> data, errors = marshall((), fields)

        >>> 'age' in data['user']
        False
        
        >>> data['user']['age'] is None
        True
        
    The fields structure may end in a list of a simple type.

        >>> fields = {
        ...     "user": {
        ...         "friends": [str],
        ...     }
        ... }

    In this case, we expect the ``friends`` entry to be a list of strings::

        >>> params = (
        ...     ("user.friends", "stefan"),
        ...     ("user.friends", "malthe"))
        
        >>> data, errors = marshall(params, fields)
        
    As expected, we get a list. Note that this list items appear in
    the order they appear in the reqeuest parameters.
    
        >>> data['user']['friends']
        ['stefan', 'malthe']

    Tuples are also supported.

        >>> fields = {
        ...     "points": (int,)
        ...     }
        
        >>> params = (("points", 42), ("points", 10))
        
        >>> data, errors = marshall(params, fields)
        
        >>> data['points']
        (42, 10)

    Sequence types may only appear as end-points. The following field
    definition is invalid.

        >>> fields = {
        ...     "users": [{
        ...         "name": str,
        ...         "nick": str}]
        ...     }

        >>> params = (("users.name", "Foo"),)
        >>> marshall(params, fields)
        Traceback (most recent call last):
         ...
        TypeError: Sequences are only allowed as end-points.

    Dictionary entries may be dynamic.

        >>> fields = {
        ...     "user": {
        ...         str: {
        ...            "name": str,
        ...         }
        ...     }
        ... }

        >>> params = (
        ...     ("user.stefan.name", "Stefan Eletzhofer"),
        ...     ("user.malthe.name", "Malthe Borch"))
        
        >>> data, errors = marshall(params, fields)
        
    As expected, we get a list. Note that this list items appear in
    the order they appear in the reqeuest parameters.
    
        >>> data['user']['stefan']['name']
        'Stefan Eletzhofer'
    
    """

    data = Marshaller(fields)
    errors = Errors()

    marshall_errors = Marshaller(fields, coerce=False)

    for name, value in params:
        path = tuple(name.split('.'))
        try:
            data[path] = value
        except ValueError, error:
            data[path] = None
            e = errors
            for p in path:
                e = e[p]
            e.messages.append(error.message)
        except KeyError:
            # parameter does not match this form field definition; we
            # can safely disregard it.
            continue

    for path, message in marshall_errors:
        e = errors
        for p in path:
            e = e[path]
        e.messages.append(message)

    return data, errors

class Marshaller(object):
    """Form fields marshaller.

    Any field name that comforms to the field definition may be
    resolved; if not set, an empty value is returned.

        >>> from repoze.formapi.marshalling import Marshaller
        
        >>> marshaller = Marshaller({
        ...     'name': str,
        ...     'users': {
        ...         str: {
        ...            'username': str,
        ...            'id': int,
        ...            'groups': [str]}
        ...         }
        ...     })

    We'll first demonstrate that valid keys return an empty value.
    
        >>> marshaller['name'] is None
        True
        
        >>> marshaller['users', 'foo', 'username'] is None
        True
        
        >>> marshaller['users', 'foo', 'groups']
        []

    An exception is raised if an invalid key is tried.
    
        >>> marshaller['users', 'foo', 'bar']
        Traceback (most recent call last):
         ...
        KeyError: 'bar'

    The truth-value of an empty ``Marshaller`` instance is ``False``.

        >>> bool(marshaller)
        False

    We may set values for valid keys.

        >>> marshaller['name'] = 'Foo'
        >>> marshaller['users', 'foo', 'id'] = 1
        >>> marshaller['users', 'foo', 'username'] = 'foo'

    Sequences append on assignments.
        
        >>> marshaller['users', 'foo', 'groups'] = 'foo'
        >>> marshaller['users', 'foo', 'groups'] = 'bar'

    As expected, we can retrieve the values in exchange for the keys.
        
        >>> marshaller['name']
        'Foo'
        
        >>> marshaller['users', 'foo', 'username']
        'foo'

        >>> marshaller['users', 'foo', 'id']
        1

        >>> marshaller['users', 'foo', 'groups']
        ['foo', 'bar']

    Sequences are replaced, if assigned a sequence.

        >>> marshaller['users', 'foo', 'groups'] = ['bar']
        >>> marshaller['users', 'foo', 'groups']
        ['bar']    

    Again, an exception is raised if an invalid key is tried.
    
        >>> marshaller['users', 'foo', 'bar'] = 'baz'
        Traceback (most recent call last):
         ...
        KeyError: 'bar'

    Values are attempted coerced to the field type.
    
        >>> marshaller['users', 'foo', 'id'] = '1'
        >>> marshaller['users', 'foo', 'id']
        1

    Coercing must not fail.

        >>> marshaller['users', 'foo', 'id'] = 'one'
        Traceback (most recent call last):
         ...
        ValueError: ...

    We may always assign ``None``.

        >>> marshaller['users', 'foo', 'id'] = None
        
    The truth-value of a non-empty ``Marshaller`` instance is ``True``.

        >>> bool(marshaller)
        True

    If the path is not exhausted, a new marshaller instance is
    returned, which curries the path onto new requests.

        >>> marshaller['users']['foo']['username']
        'foo'
        
    """

    def __init__(self, fields, data=None, path=(), coerce=True):
        self.fields = fields

        if data is None:
            data = {}

        self.data = data
        self.path = path
        self.coerce = coerce

    def __getitem__(self, path):
        if not isinstance(path, tuple):
            path = (path,)
        path = self.path + tuple(path)
        value = self.data.get(path, MISSING)
        if value is not MISSING:
            return value

        # verify path; we want to raise an exception if the path does
        # not comply with the field definition
        data_type = self.traverse(path)

        if isinstance(data_type, list):
            return []

        if isinstance(data_type, tuple):
            return ()

        if isinstance(data_type, dict):
            return Marshaller(self.fields, self.data, path, self.coerce)

    def __setitem__(self, path, value):
        if not isinstance(path, tuple):
            path = (path,)
        key = self.path + tuple(path)

        # verify path; we want to raise an exception if the path does
        # not comply with the field definition
        data_type = self.traverse(path)

        if isinstance(data_type, (tuple, list)):
            if isinstance(value, (tuple, list)):
                if key in self.data:
                    del self.data[key]
            else:
                value = (value,)

            for v in value:
                if v is not None and self.coerce and not isinstance(v, data_type[0]):
                    v = data_type[0](v)

                if isinstance(data_type, list):
                    self.data.setdefault(
                        key, []).append(v)
                else:
                    if key in self.data:
                        self.data[key] += (v,)
                    else:
                        self.data[key] = (v,)
        else:
            if value is not None and self.coerce and not isinstance(value, data_type):
                value = data_type(value)
            self.data[key] = value

        if value is not None:
            self.data[None] = True

    def __nonzero__(self):
        return self.data.get(None, False)

    def __repr__(self):
        data = self.marshall()
        return repr(data)

    def __iter__(self):
        for path in self.data:
            if path is not None and tuple(
                path[:len(self.path)]) == self.path:
                yield path[len(self.path)]

    def items(self):
        items = []
        for key in self:
            items.append((key, self[key]))
        return items

    def marshall(self):
        _data = {}
        for path, value in self.data.items():
            if path is None:
                continue

            data = _data
            for key in path[:1]:
                if key in data:
                    data = data[key]
                else:
                    data = data[key] = defaultdict(lambda: None)
            data[key] = value
        return _data

    def traverse(self, path):
        path = list(path)
        fields = self.fields
        while path:
            if not isinstance(fields, dict):
                raise TypeError(
                    "Sequences are only allowed as end-points.")

            value = path.pop(0)
            if len(fields) == 1:
                key = fields.keys()[0]
                if key in (str, unicode, int):
                    # make sure value conforms to data type
                    if not isinstance(value, key):
                        raise ValueError(
                            "Must be type '%s' (got '%s')." % (
                            (key.__name__, type(value).__name__)))
                fields = fields[key]
                continue
            fields = fields[value]
        return fields

class defaultdict(defaultdict):
    __doc__ = defaultdict.__doc__

    def __repr__(self):
        # change the representation-function; t's an implementation
        # detail that this is a ``defaultdict`` object.
        return dict.__repr__(self)

# vim: set ft=python ts=4 sw=4 expandtab : 
