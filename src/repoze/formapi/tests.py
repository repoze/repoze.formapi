import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

class Request:
    application_url = 'http://app'
    def __init__(self, environ=None, params=None):
        if environ is None:
            environ = {}
        self.environ = environ
        if params is None:
            params = {}
        self.params = params

from repoze.formapi.converter import convert


class TestDataConverter(unittest.TestCase):
    def setUp(self):
        pass

    def test_store_item(self):
        """test storing items in a dict"""
        from repoze.formapi.converter import store_item

        data = {"foo": None,
                "bar": {
                    "baz": None,
                    }
                }

        store_item("foo", "value1", data)
        store_item("bar.baz", "value2", data)
        store_item("bar.new", "value3", data)

        self.assertEqual(data["foo"], "value1")
        self.assertEqual(data["bar"]["baz"], "value2")
        self.assertEqual(data["bar"]["new"], "value3")

    def test_store_item_raises(self):
        """"""
        from repoze.formapi.converter import store_item
        self.assertRaises(KeyError, store_item, "not.there", "foo", dict())

    def test_resolver_resolves(self):
        """the resolver sould resolve names in a dict"""
        from repoze.formapi.converter import resolve_name

        data = {
                "user": {
                    "name": "Fred Kaputnik",
                    "address": "Foo Street",
                    }
                }

        self.assertEqual(resolve_name("user.name", data), "Fred Kaputnik")
        self.assertEqual(resolve_name("user.address", data), "Foo Street")

    def test_resolver_raises(self):
        """the resolver sould raise KeyError on unknown names"""
        from repoze.formapi.converter import resolve_name
        self.assertRaises(KeyError, resolve_name, "not.there", dict())

    def test_convert_returns_dict(self):
        """converter should return a tuple of data, error (each a dict)"""

        fields = {
                "user": {
                    "name": str,
                    "address": str,
                    }
                }
        params = (("user.name", "Fred Kaputnik"), ("user.address", "Foo Street"))

        data, errors = convert(params, fields)

        self.assertEqual(type(data), dict)
        self.assertEqual(type(errors),dict)

    def test_convert_populates_dicts(self):
        """the converter returns a populates dicts even if no parameters given"""
        raise NotImplementedError("nothin to see here")

    def test_errors_dict_act_as_boolean(self):
        """the error dict sould acct as boolean

        That is, the error dict should be "True" if there are errors, "False"
        otherwise.
        """
        raise NotImplementedError("nothin to see here")

    def test_convert_converts(self):
        """converter converting data"""

        fields = {
                "user": {
                    "name":    str,
                    "address": str,
                    "dates":   [int],
                    "tuple":   (float,),
                    }
                }
        params = (("user.name", "Fred Kaputnik"),
                  ("user.address", "Foo Street"),
                  ("user.dates", "17"),
                  ("user.tuple", "3.14"),
                  ("user.dates", "43"),
                  ("user.tuple", "0.5"),
                  ("user.dates", "21"))

        data, errors = convert(params, fields)

        self.assertEqual(data["user"]["name"], "Fred Kaputnik")
        self.assertEqual(data["user"]["address"], "Foo Street")
        self.assertEqual(data["user"]["dates"], [17, 43, 21])
        self.assertEqual(data["user"]["tuple"], (3.14, 0.5))

    def test_type_converters(self):
        from repoze.formapi.converter import convert_int
        from repoze.formapi.converter import convert_float

        value, error = convert_int("foo", "42")
        self.assertEqual(value, 42)
        self.assertEqual(error, None)

        value, error = convert_int("foo", "abc")
        self.assertEqual(value, None)
        self.assertEqual(error, "Error converting value to integer")



def test_suite():
    globs = dict(Request=Request)

    return unittest.TestSuite((
            doctest.DocFileSuite(
                "README.txt",
                optionflags=OPTIONFLAGS,
                globs=globs,
                package="repoze.formapi"),
            unittest.makeSuite(TestDataConverter))
            )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
