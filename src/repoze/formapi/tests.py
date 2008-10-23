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

def test_suite():
    doctests = 'README.txt',
    
    globs = dict(Request=Request)
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
        filename,
        optionflags=OPTIONFLAGS,
        globs=globs,
        package="repoze.formapi") for filename in doctests])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
