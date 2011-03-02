import unittest
import doctest

def test_imports():
    '''
    This tests that old imports still work as the main purpose of this
    package now is to provide backward-compatibility.

    >>> from zc.copy import clone, copy, CopyPersistent
    >>> from zc.copy import location_copyfactory, ObjectCopier

    >>> from zc.copy.interfaces import ICopyHook, ResumeCopy

    No ImportErrors should be raised.
    '''

def test_suite():
    return doctest.DocTestSuite()
