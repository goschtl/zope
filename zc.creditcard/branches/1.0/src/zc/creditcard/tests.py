"""Tests for zc.ssl

$Id$
"""
import unittest
import zope.testing.doctest

def test_suite():
    suite = unittest.TestSuite([
        zope.testing.doctest.DocTestSuite('zc.creditcard'),
        ])

    return suite
