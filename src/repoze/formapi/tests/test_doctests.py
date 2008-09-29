import zope.interface
import zope.component
import zope.testing

import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

import zope.component
import zope.component.testing
import repoze.formapi.testing

def setUp(suite):
    zope.component.testing.setUp(suite)
    
def test_suite():
    doctests = 'README.txt',
    
    globs = dict(interface=zope.interface,
                 component=zope.component,
                 testing=repoze.formapi.testing)
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
        filename,
        optionflags=OPTIONFLAGS,
        setUp=setUp,
        globs=globs,
        tearDown=zope.component.testing.tearDown,
        package="repoze.formapi") for filename in doctests])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
