import unittest
from zope.testing.doctest import DocFileSuite
 
def test_suite():
    return DocFileSuite('vproposal.txt')