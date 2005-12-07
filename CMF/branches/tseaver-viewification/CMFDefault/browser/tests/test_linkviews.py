""" Unit tests for Products.CMFDefault.browser.linkviews

$Id$
"""
import unittest
import Zope2
Zope2.startup()

def test_suite():
    from Testing.ZopeTestCase import ZopeDocFileSuite
    return unittest.TestSuite((
            ZopeDocFileSuite('linkviews.txt',
                             package="Products.CMFDefault.browser.tests"),
                            ))

if __name__ == '__main__':
    framework()
