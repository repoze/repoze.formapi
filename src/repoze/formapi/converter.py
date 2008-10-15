
def path_iterator(data):
    """path_iterator(data) -> iterator

    Return a ``iterator`` which iterates over all the paths
    which in the data dict.

        >>> data = dict(foo=dict(bar=42, baz=10), buz="hello")

        >>> from repoze.formapi.converter import path_iterator
        >>> sorted(list(path_iterator(data)))
        ['buz', 'foo.bar', 'foo.baz']

    """
    for key, value in data.items():
        if type(value) == dict:
            for p in path_iterator(value):
                yield "%s.%s" % (key, p)
        else:
            yield key


def resolve_name(name, data):
    """resolve the name given in the data given

    Resolve a name in a dict::

        >>> from repoze.formapi.converter import resolve_name
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

        >>> from repoze.formapi.converter import store_item
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
            obj = obj.setdefault(item, dict())

    old_value = obj.get(key)
    if type(old_value) == list:
        obj[key].append(value)
    elif type(old_value) == tuple:
        obj[key] += (value,)
    else:
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

type_converters={
        str:   lambda name, value: (value, None),
        int:   convert_int,
        float: convert_float,
}


def convert(params, fields):
    """convert(params, fields) -> data, errors

    This function converts and validates the ``params`` tuple of (name, value)
    pairs.  The data converted is returned in the ``data`` dict.  Errors
    encountered during conversion are set in the ``errors`` dict.

    The ``fields`` parameter is used to convert/validate the data.  It it's a
    dict with either simple types or dicts as value, e.g::

        >>> fields = {
        ...     "user": {
        ...         "name": str,
        ...         "nick": str,
        ...         "age": int,
        ...     }
        ... }

    Using that ``schema-like`` structure, we're able to validate and convert form request
    data::

        >>> params = (("user.name", "Fred Kaputnik"), ("user.nick", "fred"),
        ...     ("user.age", 42))

    Note, the ``names`` in the name, value tuples of the params are ``path`` names.

        >>> from repoze.formapi.converter import convert
        >>> data, errors = convert(params, fields)

    As all the tuples in ``params`` are valid, we get no error::

        >>> errors
        {'user': {'nick': None, 'age': None, 'name': None}}

    Usually, we would request a error for a ``path``like so::

        >>> from repoze.formapi.converter import resolve_name
        >>> resolve_name("user.nick", errors) is None
        True

    Ok, the data is converted w/o error.  Let's have a look::

        >>> resolve_name("user.name", data)
        'Fred Kaputnik'
        >>> resolve_name("user.nick", data)
        'fred'
        >>> resolve_name("user.age", data)
        42

    Let's provoke a validation error::

        >>> data, errors = convert((("user.age", "ten"),), fields)
        >>> resolve_name("user.age", data) is None
        True
        >>> resolve_name("user.age", errors)
        'Error converting value to integer'

    Note that the ``data` dict is populated with ``None`` values as a missing value::

        >>> data
        {'user': {'nick': None, 'age': None, 'name': None}}

    This was simple.  Now let's consider this field structure::

        >>> fields = {
        ...     "user": {
        ...         "name": str,
        ...         "nick": str,
        ...         "friends": [ str, ],
        ...     }
        ... }

    Obviously, we want to have ``user.friends`` to be a a list of friends::

        >>> params = (("user.friends", "stefan"), ("user.friends", "malthe"))
        >>> data, errors = convert(params, fields)
        >>> resolve_name("user.friends", data)
        ['stefan', 'malthe']

    The same goes for tuples::

        >>> fields = {
        ...     "user": {
        ...         "name": str,
        ...         "nick": str,
        ...         "points": (int, ),
        ...     }
        ... }
        >>> params = (("user.points", 42), ("user.points", 10))
        >>> data, errors = convert(params, fields)
        >>> resolve_name("user.points", data)
        (42, 10)

    Now for something more complex. consider this field structure::

        >>> fields = {
        ...     "user_list": [{
        ...         "name": str,
        ...         "nick": str,
        ...     }, ]
        ... }

    Here we clearly expect a ``list of users``, e.g. a list of dicts.

    Currently, we don't support that.

    """
    data = dict()
    errors = dict()

    # initialize data dict
    for path in path_iterator(fields):
        data_type = resolve_name(path, fields)
        if type(data_type) == list:
            store_item(path, list(), data)
        elif type(data_type) == tuple:
            store_item(path, tuple(), data)
        else:
            store_item(path, None, data)

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


# vim: set ft=python ts=4 sw=4 expandtab : 
