
def resolve_name(name, data):
    """resolve the name given in the data given"""

    path = name.split(".")

    obj = data
    for item in path:
        obj = obj[item]

    return obj


def store_item(name, value, data, create_empty=False, container=None):
    """store the named item in the data dict"""
    path = name.split(".")
    path, key = path[:-1], path[-1]

    obj = data
    if len(path):
        for item in path:
            if create_empty:
                obj = obj.setdefault(item, dict())
            else:
                obj = obj[item]

    if obj.has_key(key):
        if type(obj[key]) in (list, tuple):
            obj[key] = container(list(obj[key]).append(value))
        else:
            obj[key] = container(list(obj[key]) + [value,])
    else:
        if container is None:
            obj[key] = value
        else:
            obj[key] = container(value)


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
    data = dict()
    errors = dict()

    for param in params:
        name, value = param

        # fetch the data type
        data_type = resolve_name(name, fields)

        container_type = None
        if type(data_type) in (list, tuple):
            # these merely specify the container type.  Fetch the data type
            container_type = type(data_type)
            data_type = data_type[0]

        # fetch type converter
        converter = type_converters.get(data_type)
        if not callable(converter):
            raise RuntimeError("No converter for type %s found, needed for param named '%s'" % (data_type, name))

        # convert
        value, error = converter(name, value)

        # store value in data dict
        store_item(name, value, data, create_empty=True, container=container_type)

        # store error in error dict
        store_item(name, error, errors, create_empty=True, container=container_type)

    return data, errors


# vim: set ft=python ts=4 sw=4 expandtab : 
