import unittest, doctest

from zope.interface.adapter import AdapterRegistry
from iface.compatibility import CompatibilityAdapterRegistry

def test_suite():
    suite = unittest.TestSuite()

    optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

    suite.addTests([
            doctest.DocFileSuite(
                'mapping.txt',
                optionflags=optionflags),
            doctest.DocFileSuite(
                'compatibility.txt',
                optionflags=optionflags,
                globs=dict(AdapterRegistry=AdapterRegistry)),
            doctest.DocFileSuite(
                'compatibility.txt',
                optionflags=optionflags,
                globs=dict(AdapterRegistry=CompatibilityAdapterRegistry)),            
            ])
            
    return suite

