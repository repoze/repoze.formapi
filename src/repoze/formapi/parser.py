from repoze.formapi.py24 import defaultdict
from repoze.formapi.error import Errors


def parse(params, fields):
    """Return ``(data, errors)`` tuple.

    This function parses, converts and validates the parameter
    sequence (name, value) pairs.

    The converted data is returned as the ``data`` value, while errors
    encountered during conversion are set in the ``errors`` dict.

    The ``fields`` parameter is used to describe the data
    structure. It's a nested dictionary that ends in simple types, or
    a list of such, e.g.:

        >>> fields = {
        ...     "user": {
        ...         "name": str,
        ...         "nick": str,
        ...         "age": int,
        ...         "extra": str,
        ...     }
        ... }

    Given a sequence of parameteres, the function returns a data
    structure that matches the fields definition.

        >>> params = (
        ...     ("user.name", "Fred Kaputnik"),
        ...     ("user.nick", "fred"),
        ...     ("user.age", 42),
        ...     ("user.extra", ""))

    Note that the field names appear as 'dotted paths'.

        >>> from repoze.formapi.parser import parse
        >>> data, errors = parse(params, fields)

    Since all the tuples in ``params`` are valid, we expect no
    validation errors::

        >>> len(errors)
        0

    We can turn the returned data into a dict:

        >>> d = dict(data)
        >>> sorted(d.items())
        [('user', {'user': {'nick': 'fred', 'age': 42, \
                            'name': 'Fred Kaputnik', 'extra': ''}})]

    Similarly, we can pass the data as keyword arguments:

        >>> (lambda **kwargs: True)(**data)
        True

    To get to the parsed field data, we use a similar approach.

        >>> data['user']['name']
        'Fred Kaputnik'
        >>> data['user']['nick']
        'fred'
        >>> data['user']['age']
        42
        >>> data['user']['extra']
        ''

    To illustrate error handling, we can violate the validation
    constraint of the ``age`` field.

        >>> data, errors = parse((("user.age", "ten"),), fields)

        >>> data['user']['age']
        'ten'

        >>> 'ten' in errors['user']['age'][0]
        True

    Note that the ``data`` and ``errors`` dictionaries provide a
    default value of ``missing`` for missing entries.

        >>> from repoze.formapi.parser import missing

    It evaluates to false.

        >>> bool(missing)
        False

        >>> data, errors = parse((), fields)

        >>> 'age' in data['user']
        False

        >>> data['user']['age'] is missing
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

        >>> data, errors = parse(params, fields)

    As expected, we get a list. Note that this list items appear in
    the order they appear in the reqeuest parameters.

        >>> data['user']['friends']
        ['stefan', 'malthe']

    Tuples are also supported.

        >>> fields = {
        ...     "points": (int,)
        ...     }

        >>> params = (("points", 42), ("points", 10))

        >>> data, errors = parse(params, fields)

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
        >>> parse(params, fields)
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

        >>> data, errors = parse(params, fields)

    As expected, we get a list. Note that this list items appear in
    the order they appear in the reqeuest parameters.

        >>> data['user']['stefan']['name']
        'Stefan Eletzhofer'

    If a trivial input results in a conversion error, the value is set
    to ``None``.

        >>> fields = {
        ...     'user': str,
        ...     'age': int
        ...     }

        >>> params = (
        ...     ('user', ''),
        ...     ('age', ''))

        >>> data, errors = parse(params, fields)

     Empty strings are valid for string fields.

        >>> data['user']
        ''

     Empty strings are trivial for integer fields; it's regarded as a
     non-input.

        >>> data['age']

     This is not an error:

        >>> str(errors['age'])
        ''

     If the field is required, an empty string is an invalid input for
     a number. Invalid inputs are preserved as-is for required fields.

        >>> from repoze.formapi.parser import required
        >>> fields['age'] = required(int)
        >>> data, errors = parse(params, fields)

        >>> data['age'] is None
        True

        >>> bool(errors['age'])
        True

     The same goes for non-trivial invalid inputs.

        >>> data, errors = parse((('age', 'ten'),), fields)
        >>> data['age']
        'ten'

        >>> bool(errors['age'])
        True

    """

    data = Parser(fields)
    errors = Errors()

    parsed_errors = Parser(fields, coerce=False)

    for name, value in params:
        path = tuple(name.split('.'))
        try:
            data[path] = value
        except KeyError:
            continue
        except ValueError as error:
            e = errors
            for p in path:
                e = e[p]
            e += str(error)

    for path, message in parsed_errors:
        e = errors
        for p in path:
            e = e[path]
        e += message

    return data, errors


class Parser(object):
    """Form input parser.

    Any field name that comforms to the field definition may be
    resolved; if not set, an empty value is returned.

        >>> from repoze.formapi.parser import Parser
        >>> from repoze.formapi.parser import missing

        >>> parser = Parser({
        ...     'name': str,
        ...     'users': {
        ...         str: {
        ...            'username': str,
        ...            'id': int,
        ...            'groups': [str]}
        ...         }
        ...     })

    We'll first demonstrate that valid keys return an empty value.

        >>> parser['name'] is missing
        True

        >>> parser['users', 'foo', 'username'] is missing
        True

        >>> parser['users', 'foo', 'groups']
        []

    An exception is raised if an invalid key is tried.

        >>> parser['users', 'foo', 'bar']
        Traceback (most recent call last):
         ...
        KeyError: 'bar'

    The truth-value of an empty ``Parser`` instance is ``False``.

        >>> bool(parser)
        False

    We may set values for valid keys.

        >>> parser['name'] = 'Foo'
        >>> parser['users', 'foo', 'id'] = 1
        >>> parser['users', 'foo', 'username'] = 'foo'

    Sequences append on assignments.

        >>> parser['users', 'foo', 'groups'] = 'foo'
        >>> parser['users', 'foo', 'groups'] = 'bar'

    As expected, we can retrieve the values in exchange for the keys.

        >>> parser['name']
        'Foo'

        >>> parser['users', 'foo', 'username']
        'foo'

        >>> parser['users', 'foo', 'id']
        1

        >>> parser['users', 'foo', 'groups']
        ['foo', 'bar']

    Sequences are replaced, if assigned a sequence.

        >>> parser['users', 'foo', 'groups'] = ['bar']
        >>> parser['users', 'foo', 'groups']
        ['bar']

    Again, an exception is raised if an invalid key is tried.

        >>> parser['users', 'foo', 'bar'] = 'baz'
        Traceback (most recent call last):
         ...
        KeyError: 'bar'

    Values are attempted coerced to the field type.

        >>> parser['users', 'foo', 'id'] = '1'
        >>> parser['users', 'foo', 'id']
        1

    Coercing must not fail.

        >>> parser['users', 'foo', 'id'] = 'one'
        Traceback (most recent call last):
         ...
        ValueError: ...

    We may always assign ``None``.

        >>> parser['users', 'foo', 'id'] = None

    The truth-value of a non-empty ``Parser`` instance is ``True``.

        >>> bool(parser)
        True

    If the path is not exhausted, a new parser instance is
    returned, which curries the path onto new requests.

        >>> parser['users']['foo']['username']
        'foo'

    Each segment is iterable.

        >>> tuple(parser['users'])
        ('foo',)

        >>> tuple(sorted(parser['users']['foo']))
        ('groups', 'id', 'username')

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
        value = self.data.get(path, missing)
        if value is not missing:
            return value

        # verify path; we want to raise an exception if the path does
        # not comply with the field definition
        data_type = self.traverse(path)

        if isinstance(data_type, list):
            return []

        if isinstance(data_type, tuple):
            return ()

        if isinstance(data_type, dict):
            return Parser(self.fields, self.data, path, self.coerce)

        return missing

    def __setitem__(self, path, value):
        if not isinstance(path, tuple):
            path = (path,)
        key = self.path + tuple(path)

        # verify path; we want to raise an exception if the path does
        # not comply with the field definition
        data_type = self.traverse(path)

        error = False
        if isinstance(data_type, (tuple, list)):
            if isinstance(value, (tuple, list)):
                if key in self.data:
                    del self.data[key]
            else:
                value = (value,)

            for v in value:
                if v is not None and self.coerce:
                    try:
                        v = data_type[0](v)
                    except:
                        error = True

                if isinstance(data_type, list):
                    self.data.setdefault(
                        key, []).append(v)
                else:
                    if key in self.data:
                        self.data[key] += (v,)
                    else:
                        self.data[key] = (v,)
        else:
            if value is not None and self.coerce:
                try:
                    value = data_type(value)
                except MissingError:
                    error = True
                    value = None
                except:
                    if value:
                        error = True
                    else:
                        value = None

            self.data[key] = value

        if value is not None:
            self.data[None] = True

        if error is True:
            raise

    def __nonzero__(self):
        return self.data.get(None, False)

    def __repr__(self):
        data = self.parse()
        return repr(data)

    def __iter__(self):
        items = set()
        for path in self.data:
            if path is None:
                continue

            length = len(self.path)

            if tuple(path[:length]) == self.path:
                item = path[length]
                if item not in items:
                    yield item

                items.add(item)

    def keys(self):
        return list(self)

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        for key in self:
            yield (key, self[key])

    def parse(self):
        _data = {}
        for path, value in self.data.items():
            if path is None:
                continue

            data = _data
            for key in path[:-1]:
                if key in data:
                    data = data[key]
                else:
                    data[key] = defaultdict(lambda: missing)
                    data = data[key]
            data[path[-1]] = value
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
                        raise TypeError(
                            "Must be type '%s' (got '%s')." % (
                            (key.__name__, type(value).__name__)))
                    fields = fields[key]
                    continue
            fields = fields[value]
        return fields


def required(cls, msg="Required field"):
    class required(cls):
        def __new__(base, value):
            if not value:
                raise MissingError(msg)
            return cls(value)
    return required


class defaultdict(defaultdict):
    __doc__ = defaultdict.__doc__

    def __repr__(self):
        # change the representation-function; t's an implementation
        # detail that this is a ``defaultdict`` object.
        return dict.__repr__(self)


class Missing(object):
    def __nonzero__(self):
        return False


class MissingError(ValueError):
    pass


missing = Missing()


# vim: set ft=python ts=4 sw=4 expandtab :
