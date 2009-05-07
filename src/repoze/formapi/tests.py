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
            params = ()
        self.params = Params(params)

class Params:
    def __init__(self, params):
        self.params = params

    def __iter__(self):
        for key, value in self.params:
            yield key

    def get(self, key, default=None):
        return dict(self.params).get(key, default)

    def items(self):
        return self.params
        
def test_suite():
    from repoze import formapi

    globs = dict(
        Request=Request,
        formapi=formapi
        )

    return unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt',
            optionflags=OPTIONFLAGS,
            globs=globs,
            package="repoze.formapi"),
        doctest.DocTestSuite(
            'repoze.formapi.form',
            optionflags=OPTIONFLAGS,
            globs=globs),
        doctest.DocTestSuite(
            'repoze.formapi.error',
            optionflags=OPTIONFLAGS,
            globs=globs),
        doctest.DocTestSuite(
            'repoze.formapi.marshalling',
            optionflags=OPTIONFLAGS,
            globs=globs)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
