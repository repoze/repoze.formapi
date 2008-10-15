import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

from repoze.formapi.converter import convert

class Request:
    application_url = 'http://app'
    def __init__(self, environ=None, params=None):
        if environ is None:
            environ = {}
        self.environ = environ
        if params is None:
            params = {}
        self.params = params


def test_suite():
    globs = dict(Request=Request)
    
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
            'repoze.formapi.converter',
            optionflags=OPTIONFLAGS,
            globs=globs)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
