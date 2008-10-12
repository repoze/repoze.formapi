import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

import repoze.formapi.testing

def test_suite():
    doctests = 'README.txt',
    
    globs = dict(testing=repoze.formapi.testing)
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
        filename,
        optionflags=OPTIONFLAGS,
        globs=globs,
        package="repoze.formapi") for filename in doctests])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
