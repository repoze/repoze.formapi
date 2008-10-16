from collections import defaultdict

MISSING = object()

def path_iterator(data):
    """path_iterator(data) -> iterator

    Return a ``iterator`` which iterates over all the paths
    which in the data dict.

        >>> data = dict(foo=dict(bar=42, baz=10), buz="hello")

        >>> from repoze.formapi.marshalling import path_iterator
        >>> sorted(list(path_iterator(data)))
        ['buz', 'foo.bar', 'foo.baz']

    """

    for key, value in data.items():
        if type(value) == dict:
            for p in path_iterator(value):
                yield "%s.%s" % (key, p)
        elif isinstance(value, (tuple, list)):
            if len(value) != 1:
                raise TypeError(
                    "Sequence types must contain exactly one simple type.")
            if value[0] not in (int, str, unicode, float):
                raise TypeError(
                    "Sequence must contain a simple type.")
            yield key
        else:
            yield key
            
def resolve_name(name, data):
    """resolve the name given in the data given

    Resolve a name in a dict::

        >>> from repoze.formapi.marshalling import resolve_name
        >>> data = dict(foo=dict(bar=42, baz=10), buz="hello")
        >>> resolve_name("buz", data)
        'hello'
        >>> resolve_name("foo.bar", data)
        42
        >>> resolve_name("foo.baz", data)
        10
        >>> resolve_name("foo", data)
        {'baz': 10, 'bar': 42}

    A KeyError is raised for nonexisting keys::

        >>> resolve_name("foo.notthere", data)
        Traceback (most recent call last):
        ...
        KeyError: 'notthere'

    """

    path = name.split(".")

    obj = data
    for item in path:
        obj = obj[item]

    return obj

def store_item(name, value, data):
    """Set items in a dict using a ``path``

    Using ``store_item`` we're able to set values using a ``path``::

        >>> from repoze.formapi.marshalling import store_item
        >>> data = dict()
        >>> store_item("user.name", "Fred Kaputnik", data)
        >>> store_item("user.nick", "fred", data)
        >>> store_item("user.age", 42, data)
        >>> data
        {'user': {'nick': 'fred', 'age': 42, 'name': 'Fred Kaputnik'}}

    Note that ``empty`` path elements are created using new ``dict``
    objects.

    If a value exists, it is overwritten::

        >>> store_item("user.name", "Alfred E. Neuman", data)
        >>> data
        {'user': {'nick': 'fred', 'age': 42, 'name': 'Alfred E. Neuman'}}

    """
    path = name.split(".")
    path, key = path[:-1], path[-1]

    obj = data
    if len(path):
        for item in path:
            obj = obj.setdefault(item, defaultdict(lambda: None))

    old_value = obj.get(key)
    if type(old_value) == list:
        obj[key].append(value)
    elif type(old_value) == tuple:
        obj[key] += (value,)
    elif value is not MISSING:
        obj[key] = value
        
def convert_int(name, value):
    try:
        return int(value), None
    except ValueError:
        return None, "Error converting value to integer"

def convert_float(name, value):
    try:
        return int(value), None
    except ValueError:
        return None, "Error converting value to float"

type_converters = {
        unicode:    lambda name, value: (value, None),
        str:        lambda name, value: (value, None),
        int:        convert_int,
        float:      convert_float,
}

def convert(params, fields):
    """convert(params, fields) -> data, errors

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

        >>> from repoze.formapi.marshalling import convert
        >>> data, errors = convert(params, fields)

    Since all the tuples in ``params`` are valid, we expect no
    validation errors::

        >>> errors
        {'user': {'nick': None, 'age': None, 'name': None}}

    We can use the ``resolve_name`` function to traverse into the
    errors dictionary.
    
        >>> from repoze.formapi.marshalling import resolve_name
        >>> resolve_name("user.nick", errors) is None
        True

    To get to the marshalled field data, we use a similar approach.

        >>> resolve_name("user.name", data)
        'Fred Kaputnik'
        >>> resolve_name("user.nick", data)
        'fred'
        >>> resolve_name("user.age", data)
        42

    To illustrate error handling, we can violate the validation
    constraint of the ``age`` field.

        >>> data, errors = convert((("user.age", "ten"),), fields)
        
        >>> resolve_name("user.age", data) is None
        True
        
        >>> resolve_name("user.age", errors)
        'Error converting value to integer'

    Note that the ``data`` and ``errors`` dictionaries provide a
    default value of ``None`` for missing entries.

        >>> data, errors = convert((), fields)

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
        
        >>> data, errors = convert(params, fields)

    As expected, we get a list. Note that this list items appear in
    the order they appear in the reqeuest parameters.
    
        >>> resolve_name("user.friends", data)
        ['stefan', 'malthe']

    Tuples are also supported.

        >>> fields = {"points": (int,)}
        
        >>> params = (("points", 42), ("points", 10))
        >>> data, errors = convert(params, fields)
        
        >>> resolve_name("points", data)
        (42, 10)

    Sequence types may only appear as end-points. The following field
    definition is invalid.

        >>> fields = {
        ...     "users": [{
        ...         "name": str,
        ...         "nick": str}]
        ...     }

        >>> convert((), fields)
        Traceback (most recent call last):
         ...
        TypeError: Sequence must contain a simple type.

    """
        
    data = dict()
    errors = Errors()

    # initialize data and errors dict
    for path in path_iterator(fields):
        data_type = resolve_name(path, fields)
        if type(data_type) == list:
            store_item(path, list(), data)
            store_item(path, list(), errors)
        elif type(data_type) == tuple:
            store_item(path, tuple(), data)
            store_item(path, tuple(), errors)
        else:
            store_item(path, MISSING, data)
            store_item(path, MISSING, errors)

    for param in params:
        name, value = param

        # fetch the data type
        data_type = resolve_name(name, fields)

        if type(data_type) in (list, tuple):
            # these merely specify the container type.  Fetch the data type
            data_type = data_type[0]
            
        # fetch type converter
        converter = type_converters.get(data_type)
        if not callable(converter):
            raise RuntimeError("No converter for type %s found, needed for param named '%s'" % (data_type, name))

        # convert
        value, error = converter(name, value)

        # store value in data dict
        store_item(name, value, data)

        # store error in error dict
        store_item(name, error, errors)

    return data, errors

class Errors(dict):
    """Form error dictionary.

    This is a ``dict``-like object which evaluates to ``True`` if
    a key contains a non-None value.

        >>> from repoze.formapi.marshalling import Errors
        >>> errors = Errors()

        >>> errors["foo"] = dict(bar=42, fuz=12)
        >>> bool(errors)
        True


        >>> errors["foo"] = dict(bar=None, fuz=None)
        >>> bool(errors)
        False
    """
        
    def __nonzero__(self):
        for path in path_iterator(self):
            if resolve_name(path, self) is not None:
                return True
        return False

class defaultdict(defaultdict):
    __doc__ = defaultdict.__doc__
    
    def __repr__(self):
        # change the representation-function; t's an implementation
        # detail that this is a ``defaultdict`` object.
        return dict.__repr__(self)
    
# vim: set ft=python ts=4 sw=4 expandtab : 
