from zope import interface
from zope import component

import unittest
from zope.testing import doctest

def test_suite():
    globs = dict(interface=interface, component=component)
    
    return unittest.TestSuite((
        doctest.DocFileSuite(
        'README.txt',
        globs=globs,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),    
        ))

